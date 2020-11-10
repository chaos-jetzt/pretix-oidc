from django.utils.translation import gettext_lazy

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")

__version__ = '1.0.0'


class PluginApp(PluginConfig):
    name = 'pretix_oidc'
    verbose_name = 'Pretix OIDC'

    class PretixPluginMeta:
        name = gettext_lazy('Pretix OIDC')
        author = 'chaos-jetzt'
        description = gettext_lazy('OpenIDConnect authentication backend for pretix')
        visible = True
        version = __version__
        category = 'INTEGRATION'
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_oidc.PluginApp'
