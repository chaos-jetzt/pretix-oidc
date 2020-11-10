from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^oidc_login$', views.return_from_sso, name='oidc.response'),
]
