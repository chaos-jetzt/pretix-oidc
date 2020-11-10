import json
import time
from django.conf import settings
from pretix.base.models import User
from pretix.settings import config
from requests_oauthlib import OAuth2Session
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from pretix.control.views.auth import process_login

from . import auth_backend


def return_from_sso(request):
    try:
        token, userinfo = _get_token_and_userinfo_redirect_flow( request)
        _process_token(request, token)
        user =  _process_userinfo(request, userinfo)
    except Exception as e:
        print(e)
        return HttpResponse(_('Login failed'))

    return process_login(request, user, False)


def _get_token_and_userinfo_redirect_flow(request):
    authorization_code_url = request.build_absolute_uri()
    
    client_id = config.get('pretix_oidc', 'oidc_client_id', fallback='pretix')
    client_secret = config.get('pretix_oidc', 'oidc_client_secret', fallback='pretix')
    token_url = config.get('pretix_oidc', 'oidc_token_url', fallback='https://sso.example.com/token')
    userinfo_url = config.get('pretix_oidc', 'oidc_userinfo_url', fallback='https://sso.example.com/user')
    
    state = request.session['OAUTH2_STATE']
    redirect_uri = request.session['OAUTH2_REDIRECT_URI']
    
    oauth2_session = OAuth2Session(client_id,
                                   scope='openid email profile',
                                   redirect_uri=redirect_uri,
                                   state=state)
    token = oauth2_session.fetch_token(
        token_url, client_secret=client_secret,
        authorization_response=authorization_code_url)
    userinfo = oauth2_session.get(userinfo_url).json()
    
    return token, userinfo

def _process_token(request, token):
    # TODO validate the JWS signature
    now = time.time()
    # Put access_token into session to be used for authenticating with API
    # server
    sess = request.session
    sess['ACCESS_TOKEN'] = token['access_token']
    sess['ACCESS_TOKEN_EXPIRES_AT'] = now + token['expires_in']
    sess['REFRESH_TOKEN'] = token['refresh_token']
    sess['REFRESH_TOKEN_EXPIRES_AT'] = now + token['refresh_expires_in']

def _process_userinfo(request, userinfo):
    username = userinfo['preferred_username']
    email = userinfo['email']
    request.session['USERINFO'] = userinfo
        
    try:
        user = User.objects.filter(email=email).get()
    except ObjectDoesNotExist:
        locale = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else settings.LANGUAGE_CODE
        timezone = request.timezone if hasattr(request, 'timezone') else settings.TIME_ZONE

        user = User.objects.create(
            email=email,
            fullname=username,
            locale=locale,
            timezone=timezone,
            auth_backend=auth_backend.OIDCAuthBackend.identifier,
            password='',
        )

    if user.auth_backend != auth_backend.OIDCAuthBackend.identifier:
        return HttpResponseBadRequest(_('Could not create user: Email is already registered.'))

    return user
