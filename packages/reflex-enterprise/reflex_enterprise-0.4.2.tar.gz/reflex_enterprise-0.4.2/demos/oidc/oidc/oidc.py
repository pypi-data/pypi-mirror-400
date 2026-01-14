import logging

import reflex as rx

import reflex_enterprise as rxe
from reflex_enterprise.auth.oidc.state import OIDCAuthState

logging.basicConfig(level=logging.INFO)


class OktaAuthState(OIDCAuthState, rx.State):
    """OIDC Auth State for Okta."""

    __provider__ = "okta"

    @rx.event
    def check_if_iframed_cb(self, is_iframed: bool):
        """Callback invoked with the iframe detection result.

        Args:
            is_iframed: True if the page is inside an iframe or cross-origin
                access prevented detection.
        """
        self.is_iframed = True


class DatabricksAuthState(OIDCAuthState, rx.State):
    """OIDC Auth State for Databricks."""

    __provider__ = "databricks"
    _requested_scopes: str = "all-apis offline_access openid email profile"


def user_info_card(auth_cls: type[OIDCAuthState]) -> rx.Component:
    return rx.card(
        rx.cond(
            auth_cls.userinfo.is_not_none(),
            rx.vstack(
                rx.heading(f"{auth_cls.__provider__.title()} User Info", size="4"),
                rx.foreach(
                    auth_cls.userinfo,
                    lambda kv: rx.text(f"{kv[0]}: {kv[1]} "),
                ),
                rx.button("Logout", on_click=auth_cls.redirect_to_logout),
            ),
            auth_cls.get_login_button(),
        ),
    )


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("OIDC Demo", size="9"),
            rx.hstack(
                user_info_card(OktaAuthState),
                user_info_card(DatabricksAuthState),
                spacing="2",
            ),
        ),
    )


app = rxe.App()
app.add_page(index)

OktaAuthState.register_auth_endpoints()
DatabricksAuthState.register_auth_endpoints()
