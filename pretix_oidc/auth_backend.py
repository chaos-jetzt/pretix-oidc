from pretix.base.auth import BaseAuthBackend
from pretix.settings import config
from pretix.helpers.urls import build_absolute_uri
from requests_oauthlib import OAuth2Session


class OIDCAuthBackend(BaseAuthBackend):
    """
    This class implements the interface for pluggable authentication modules used by pretix.
    """

    """
    A short and unique identifier for this authentication backend.
    This should only contain lowercase letters and in most cases will
    be the same as your package name.
    """
    identifier = 'oidc_auth'

    """
    A human-readable name of this authentication backend.
    """
    @property
    def verbose_name(self):
        return config.get('pretix_oidc', 'oidc_server_name', fallback='OpenID Connect')

    def request_authenticate(self, request):
        """
        This method will be called when the user opens the login form. If the user already has a valid session
        according to your login mechanism, for example a cookie set by a different system or HTTP header set by a
        reverse proxy, you can directly return a ``User`` object that will be logged in.
        ``request`` will contain the current request.
        You are expected to either return a ``User`` object (if login was successful) or ``None``.
        """
        return

    def authentication_url(self, request):
        """
        This method will be called to populate the URL for the authentication method's tab on the login page.
        """

        redirect_uri = build_absolute_uri('plugins:pretix_oidc:oidc.response')
        
        client_id = config.get('pretix_oidc', 'oidc_client_id', fallback='pretix')
        base_authorize_url = config.get('pretix_oidc', 'oidc_authorize_url', fallback='https://sso.example.com/auth')

        oauth2_session = OAuth2Session(
            client_id, scope='openid email profile', redirect_uri=redirect_uri)
        authorization_url, state = oauth2_session.authorization_url(
            base_authorize_url)

        # Store state in session for later validation (see auth.py)
        request.session['OAUTH2_STATE'] = state
        request.session['OAUTH2_REDIRECT_URI'] = redirect_uri

        return authorization_url
