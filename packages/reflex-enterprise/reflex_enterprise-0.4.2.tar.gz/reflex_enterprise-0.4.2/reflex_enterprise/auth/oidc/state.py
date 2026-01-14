"""Reflex state for OIDC authentication."""

import base64
import datetime
import hashlib
import logging
import secrets
import uuid
from typing import ClassVar
from urllib.parse import urlencode, urlparse

import httpx
import reflex as rx
from httpx._client import USE_CLIENT_DEFAULT
from joserfc.jwt import Token

from reflex_enterprise.app import AppEnterprise
from reflex_enterprise.auth.oidc.config import ConfigMixin
from reflex_enterprise.auth.oidc.types import OIDCUserInfo
from reflex_enterprise.auth.oidc.utils import compute_at_hash, verify_jwt
from reflex_enterprise.components.message_listener import (
    POST_MESSAGE_AND_CLOSE_POPUP,
    WINDOW_OPEN,
    WindowMessage,
    message_listener,
)
from reflex_enterprise.utils import call_event_from_computed_var

logger = logging.getLogger("reflex_enterprise.auth.oidc")
COOKIE_MAX_AGE = 604800


class OIDCAuthState(ConfigMixin, rx.State, mixin=True):
    """Reflex base state class for managing OIDC authentication flows.

    This state class handles the OAuth 2.0 Authorization Code flow with PKCE
    for OIDC authentication, including token storage, validation, and user
    information retrieval.

    Users should subclass this state and set the `__provider__` attribute
    to specify the OIDC provider (e.g., "okta", "databricks"), and supply
    appropriate environment variables for client ID, secret, and issuer URI.

    For example:
    ```python
    class OktaAuthState(OIDCAuthState, rx.State):
        __provider__ = "okta"
    ```

    Then use the `OktaAuthState.get_login_button()` method to render a login
    button in your app.

    Attributes:
        access_token: The OAuth 2.0 access token stored in cookie.
        id_token: The OpenID Connect ID token stored in cookie.
        granted_scopes: The scopes granted for the access_token stored in cookie.
        is_iframed: Whether the app is running inside an iframe.
        from_popup: Whether the current page was opened as a popup.

        _redirect_to_url: URL to redirect to after successful authentication.
        _app_state: Random state parameter for CSRF protection.
        _code_verifier: PKCE code verifier for secure authorization.
        _requested_scopes: Scopes requested during authentication.
        _last_error_message: Error message for authentication failures.
    """

    __provider__: ClassVar[str] = "generic"
    _has_registered_endpoints: ClassVar[bool] = False

    access_token: str = rx.Cookie(
        max_age=COOKIE_MAX_AGE,
        secure=True,
        same_site="strict",
    )
    id_token: str = rx.Cookie(
        max_age=COOKIE_MAX_AGE,
        secure=True,
        same_site="strict",
    )
    granted_scopes: str = rx.Cookie(
        max_age=COOKIE_MAX_AGE,
        secure=True,
        same_site="strict",
    )
    is_iframed: bool = False
    from_popup: bool = False

    _redirect_to_url: str
    _app_state: str
    _code_verifier: str
    _requested_scopes: str = "openid email profile"
    _nonce: str | None = None
    _expected_at_hash: str | None = None
    _last_error_message: str
    _last_error_txid: str

    @rx.event
    async def reset_auth(self):
        """Reset authentication state and clear tokens."""
        self.access_token = ""
        self.id_token = ""
        self.granted_scopes = ""

    async def _verify_jwt(self, token_json: str) -> Token:
        return await verify_jwt(
            token_json,
            issuer=await self._issuer_uri(),
            audience=await self._client_id(),
            nonce=self._nonce,
            at_hash=self._expected_at_hash,
        )

    async def _validate_tokens(self) -> bool:
        self._clear_last_error()

        if not self.access_token or not self.id_token:
            return False

        try:
            await self._verify_jwt(self.id_token)
        except Exception as e:
            self._set_last_error_message(f"ID token verification failed: {e}")
            return False

        return True

    def _clear_last_error(self):
        self._last_error_message = ""
        self._last_error_txid = ""

    def _set_last_error_message(self, msg: str):
        self._last_error_txid = uuid.uuid4().hex
        self._last_error_message = msg
        logger.info(
            f"{self.router.session.client_token} [txid={self._last_error_txid}] {self._last_error_message}"
        )

    @rx.var
    def has_error(self) -> bool:
        """Whether there was an authentication error."""
        return bool(self._last_error_message)

    @rx.var
    def last_error_txid(self) -> str:
        """Get the last error transaction ID for logging correlation."""
        return self._last_error_txid

    @rx.var(interval=datetime.timedelta(minutes=30))
    async def userinfo(self) -> OIDCUserInfo | None:
        """Get the authenticated user's information from OIDC token.

        This property retrieves the user's profile information from the OIDC
        userinfo endpoint using the stored access token. The result is cached
        for 30 minutes and automatically revalidated.

        Returns:
            OIDCUserInfo or subclass containing user profile data if authentication is valid,
            None if tokens are invalid or the request fails.
        """
        if not self.id_token:
            return None
        if not await self._validate_tokens():
            await call_event_from_computed_var(self, type(self).reset_auth)
            return None

        # Get the latest userinfo
        try:
            if userinfo_endpoint := await self._issuer_endpoint("userinfo_endpoint"):
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        userinfo_endpoint,
                        headers={"Authorization": f"Bearer {self.access_token}"},
                    )
                    resp.raise_for_status()
                    return resp.json()  # pyright: ignore[reportReturnType]
        except Exception as e:
            self._set_last_error_message(f"Failed to fetch userinfo: {e}")
            return None
        # Have to just trust the ID token claims.
        return (await self._verify_jwt(self.id_token)).claims  # pyright: ignore[reportReturnType]

    def _redirect_uri(self) -> str:
        current_url = urlparse(self.router.url)
        return current_url._replace(
            path=self._authorization_code_endpoint(),
            query=None,
            fragment=None,
        ).geturl()

    def _index_uri(self) -> str:
        current_url = urlparse(self.router.url)
        return current_url._replace(path="/", query=None, fragment=None).geturl()

    @rx.event
    async def redirect_to_login_popup(self):
        """Open a small popup window to initiate the login flow.

        This is used when the app detects it's embedded and needs to open a
        dedicated popup for the authorization flow.
        """
        return rx.call_script(
            WINDOW_OPEN(
                self._popup_login_endpoint(),
                f"{self.__provider__}_popup_login",
                "width=600,height=600",
            )
        )

    @rx.event
    async def redirect_to_logout_popup(self):
        """Open a small popup window to initiate the logout flow."""
        self.access_token = self.id_token = self.granted_scopes = ""
        return rx.call_script(
            WINDOW_OPEN(
                self._popup_logout_endpoint(),
                f"{self.__provider__}_popup_login",
                "width=600,height=600",
            )
        )

    @rx.event
    def set_from_popup(self, from_popup: bool):
        """Set whether the current page was opened as a popup."""
        self.from_popup = from_popup

    @rx.event
    async def redirect_to_login(self):
        """Initiate the OAuth 2.0 authorization code flow with PKCE.

        This method generates the necessary state and code verifier for PKCE,
        constructs the authorization URL, and redirects the user to Okta's
        authorization endpoint.

        Returns:
            A redirect response to the Okta authorization endpoint.
        """
        if self.is_iframed:
            return type(self).redirect_to_login_popup()
        if await self._validate_tokens():
            return [
                self.post_auth_message(),
                rx.toast("You are logged in."),
            ]

        # store app state and code verifier in session
        self._app_state = secrets.token_urlsafe(64)
        self._code_verifier = secrets.token_urlsafe(64)
        self._redirect_to_url = self.router.url

        # calculate code challenge
        hashed = hashlib.sha256(self._code_verifier.encode("ascii")).digest()
        encoded = base64.urlsafe_b64encode(hashed)
        code_challenge = encoded.decode("ascii").strip("=")

        # get request params
        query_params = {
            "client_id": await self._client_id(),
            "redirect_uri": self._redirect_uri(),
            "scope": self._requested_scopes,
            "state": self._app_state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "response_type": "code",
            "response_mode": "query",
        }

        # build request_uri
        self._clear_last_error()
        try:
            request_uri = f"{await self._issuer_endpoint('authorization_endpoint')}?{urlencode(query_params)}"
        except Exception as e:
            self._set_last_error_message(f"Failed to build authorization URL: {e}")
            return rx.toast.error("Authentication error")
        return rx.redirect(request_uri)

    @rx.event
    async def redirect_to_logout(self):
        """Initiate the OAuth 2.0 logout flow.

        This method generates a new state parameter, constructs the logout URL
        with the ID token hint, and redirects the user to Okta's logout endpoint.
        The user's tokens are cleared from local storage after the redirect.

        Returns:
            A redirect response to the Okta logout endpoint.
        """
        if self.is_iframed:
            return type(self).redirect_to_logout_popup()

        # store app state and code verifier in session
        self._app_state = secrets.token_urlsafe(64)

        # get request params
        query_params = {
            "id_token_hint": self.id_token,
            "state": self._app_state,
        }
        if not self.from_popup:
            query_params["post_logout_redirect_uri"] = self._index_uri()

        self._clear_last_error()
        try:
            if end_session_endpoint := await self._issuer_endpoint(
                "end_session_endpoint"
            ):
                request_uri = f"{end_session_endpoint}?{urlencode(query_params)}"
                return rx.redirect(request_uri)
        except Exception as e:
            self._set_last_error_message(f"Failed to build logout URL: {e}")
            return rx.toast.error("Logout error")
        finally:
            await self.reset_auth()

    @rx.event
    async def auth_callback(self):
        """Handle the OAuth 2.0 authorization-code callback.

        This method is called when the user is redirected back from OIDC
        authorization endpoint. It validates the state parameter to prevent CSRF
        attacks, exchanges the authorization code for tokens using PKCE, and
        stores the tokens for future use.

        Returns:
            A redirect response to the original requested URL, or an error toast
            if authentication fails.
        """
        self._clear_last_error()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        code = self.router.url.query_parameters.get("code")
        app_state = self.router.url.query_parameters.get("state")
        if app_state != self._app_state:
            self._set_last_error_message("App state mismatch. Possible CSRF attack.")
            return rx.toast.error("Authentication error")
        if not code:
            self._set_last_error_message("No code provided in the callback.")
            return rx.toast.error("Authentication error")
        query_params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri(),
            "code_verifier": self._code_verifier,
            "scope": self._requested_scopes,
        }
        if client_secret := await self._client_secret():
            auth = (await self._client_id(), client_secret)
        else:
            query_params["client_id"] = await self._client_id()
            auth = USE_CLIENT_DEFAULT
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    await self._issuer_endpoint("token_endpoint"),
                    headers=headers,
                    data=query_params,
                    auth=auth,
                )
                resp.raise_for_status()
                exchange = resp.json()
        except Exception as e:
            self._set_last_error_message(f"Token exchange failed: {e}")
            return rx.toast.error("Authentication error")

        # Get tokens and validate
        if exchange.get("token_type") != "Bearer":
            self._set_last_error_message("Unsupported token type. Should be 'Bearer'.")
            return rx.toast.error("Authentication error")
        await self._set_tokens(
            access_token=exchange["access_token"],
            id_token=exchange["id_token"],
            granted_scopes=exchange.get("scope", ""),
        )

        return rx.redirect(self._redirect_to_url)

    async def _set_tokens(
        self, access_token: str, id_token: str, granted_scopes: str = ""
    ):
        self._nonce = None
        self._expected_at_hash = None
        self.access_token = access_token
        self.id_token = id_token
        self.granted_scopes = granted_scopes

        # compute at_hash and store for additional validation
        try:
            token = await self._verify_jwt(id_token)
            alg = token.header.get("alg")
            at_hash = compute_at_hash(self.access_token, alg)
            # store expected at_hash in a transient property (not persisted)
            self._expected_at_hash = at_hash
        except Exception:
            self._expected_at_hash = None

        # Validate again after setting expected_at_hash
        if not await self._validate_tokens():
            self.access_token = self.id_token = self.granted_scopes = ""

    @rx.var
    def origin(self) -> str:
        """Return the app origin URL (used as postMessage target origin)."""
        return self._index_uri().rstrip("/")

    @rx.event
    def check_if_iframed(self):
        """Run a short client-side check to determine whether the page is iframed.

        The result is reported to `check_if_iframed_cb`.
        """
        return rx.call_function(
            """() => {
    try {
        return window.self !== window.top;
    } catch (e) {
        // This catch block handles potential security errors (Same-Origin Policy)
        // if the iframe content and the parent are from different origins.
        // In such cases, access to window.top might be restricted, implying it's in an iframe.
        return true;
    }
}""",
            callback=type(self).check_if_iframed_cb,
        )

    @rx.event
    def check_if_iframed_cb(self, is_iframed: bool):
        """Callback invoked with the iframe detection result.

        Args:
            is_iframed: True if the page is inside an iframe or cross-origin
                access prevented detection.
        """
        self.is_iframed = is_iframed

    @rx.event
    async def on_iframe_auth_success(self, event: WindowMessage):
        """Handle an authentication success message posted from a child window.

        The message payload is expected to include `access_token`, `id_token`,
        and an optional `nonce`. Tokens are stored via `_set_tokens`.
        """
        if event["data"].get("type") != "auth":
            return
        await self._set_tokens(
            access_token=event["data"].get("access_token"),
            id_token=event["data"].get("id_token"),
            granted_scopes=event["data"].get("scope", ""),
        )

    @rx.event
    def post_auth_message(self):
        """Post tokens back to the opening window and close the popup.

        This is called on the popup page when authentication has completed and
        the tokens are available in `self.access_token` / `self.id_token`.
        """
        payload = {
            "type": "auth",
            "access_token": self.access_token,
            "id_token": self.id_token,
            "scope": self.granted_scopes,
        }
        return rx.call_script(POST_MESSAGE_AND_CLOSE_POPUP(payload, self.origin, 500))

    @classmethod
    def get_login_button(cls, *children) -> rx.Component:
        """Return a login button component that initiates OIDC auth.

        If `children` are provided they will be placed inside the clickable
        element; otherwise a default button label is used. The component wires up
        the message listener (for iframe flows), the click handler, and a mount
        handler that checks whether the page is embedded in an iframe.
        """
        cls.register_auth_endpoints()
        if not children:
            children = [rx.button(f"Login with {cls.__provider__.title()}")]
        return rx.el.div(
            *children,
            rx.cond(
                cls.is_iframed,
                message_listener(
                    allowed_origin=cls.origin,
                    on_message=cls.on_iframe_auth_success,
                ),
            ),
            on_click=cls.redirect_to_login,
            on_mount=cls.check_if_iframed,
            width="fit-content",
        )

    @classmethod
    def get_state_hydrating_component(cls) -> rx.Component:
        """Loading spinner shown before state is hydrated."""
        return rx.vstack(
            rx.spinner(),
            align="center",
            justify="center",
            height="50vh",
            width="100%",
        )

    @classmethod
    def _with_hydrated(cls, *components: rx.Component) -> rx.Component:
        """Wrap components to wait for state hydration before rendering.

        Args:
            components: The components to render after hydration.

        Returns:
            A component that shows a loading spinner until state is hydrated,
            then renders the provided components.
        """
        return rx.cond(
            rx.State.is_hydrated,
            rx.fragment(*components),
            cls.get_state_hydrating_component(),
        )

    @classmethod
    def get_authentication_loading_page(cls) -> rx.Component:
        """Small loading page shown while authentication is validated.

        This page is registered by the package as the callback target when the
        authorization response is being processed.
        """
        return rx.container(
            cls._with_hydrated(
                rx.cond(
                    cls.has_error,
                    rx.vstack(
                        rx.heading("An error occurred during authentication."),
                        rx.text(
                            "Please close this window and try again.",
                        ),
                        rx.text(
                            "An administrator may provide more information about error ID: ",
                            rx.badge(cls.last_error_txid),
                        ),
                    ),
                    rx.cond(
                        ~cls.userinfo,
                        rx.hstack(
                            rx.heading("Validating Authentication..."),
                            rx.spinner(),
                            width="50%",
                            justify="between",
                        ),
                        rx.heading("Redirecting to app..."),
                    ),
                ),
            ),
        )

    @classmethod
    def get_authentication_popup_logout(cls) -> rx.Component:
        """Simple page shown during the logout flow.

        Registered at `/_reflex_oidc_{provider}/popup-logout` to complete the sign-out handshake.
        """
        return rx.container(
            cls._with_hydrated(
                rx.cond(
                    cls.has_error,
                    rx.vstack(
                        rx.heading("An error occurred during logout."),
                        rx.text(
                            "You close this window and clear browser cookies to manually log out.",
                        ),
                        rx.text(
                            "An administrator may provide more information about error ID: ",
                            rx.badge(cls.last_error_txid),
                        ),
                    ),
                    rx.cond(
                        cls.id_token,
                        rx.hstack(
                            rx.heading("Complete logout process."),
                            rx.spinner(),
                            width="50%",
                            justify="between",
                        ),
                        rx.heading("You are logged out. You may close this window."),
                    ),
                ),
            ),
        )

    @classmethod
    def register_auth_endpoints(cls, app: AppEnterprise | None = None):
        """Register the Okta authentication endpoints with the Reflex app.

        This function sets up the necessary OAuth callback endpoint for handling
        authentication responses from OIDC providers. The callback endpoint
        handles the authorization code exchange and redirects users.
        """
        if app is None and cls._has_registered_endpoints:
            return
        if app is None:
            cls._has_registered_endpoints = True

            from reflex.utils.prerequisites import get_app

            app = get_app().app
        if not isinstance(app, AppEnterprise):
            raise TypeError("The app must be an instance of reflex_enterprise.App.")
        app.add_page(
            cls.get_authentication_loading_page(),
            route=cls._authorization_code_endpoint(),
            on_load=cls.auth_callback,
            title=f"{cls.__provider__.title()} Auth Callback",
        )
        app.add_page(
            cls.get_authentication_loading_page(),
            route=cls._popup_login_endpoint(),
            on_load=[
                cls.set_from_popup(True),
                cls.redirect_to_login,
            ],
            title=f"{cls.__provider__.title()} Auth Initiator",
        )
        app.add_page(
            cls.get_authentication_popup_logout(),
            route=cls._popup_logout_endpoint(),
            on_load=[
                cls.set_from_popup(True),
                cls.redirect_to_logout,
            ],
            title=f"{cls.__provider__.title()} Auth Logout",
        )
