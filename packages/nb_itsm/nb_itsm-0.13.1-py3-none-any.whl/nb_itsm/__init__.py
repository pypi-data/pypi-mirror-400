import importlib.metadata
from netbox.plugins import PluginConfig
from .version import __version__


class NetboxItsmConfig(PluginConfig):
    name = 'nb_itsm'
    base_url = 'nb-itsm'
    verbose_name = 'ITIL Service Management'
    description = importlib.metadata.metadata('nb_itsm').get('summary', 'pyproject.toml error')
    version = __version__
    author = importlib.metadata.metadata('nb_itsm').get('author', 'pyproject.toml error')
    author_email = 'admin@cispa.de'
    min_version = "4.1.0"
    max_version = "4.5.99"
    required_settings = []
    default_settings = {
        "top_level_menu": True
    }

    def ready(self):
        super().ready()

config = NetboxItsmConfig # noqa
