from .queueserver import QueueserverServiceConfig
from .queueserver_qtgui import QueueserverQtGUIServiceConfig
from .queueserver_http_api import QueueserverHTTPAPIConfig
from .bluesky_blissdata import BlueskyBlissdataServiceConfig
from .daiquiri_bluesky import DaiquiriBlueskyServiceConfig
from .tiled import TiledServiceConfig
from .flint import FlintServiceConfig
from .mariadb import MariaDBServiceConfig
from .mongodb import MongoDBServiceConfig
from .redis import RedisServiceConfig
from .jupyterhub import JupyterhubServiceConfig
from .traefik import TraefikServiceConfig
from .whoami import WhoamiServiceConfig
from .document_proxy import DocumentProxyServiceConfig
from .callback_handler import CallbackHandlerServiceConfig
from ...models import ServiceConfig

__all__ = ["get_service_config_class", "get_service_config"]


def get_service_config_class(service_type: str) -> ServiceConfig:
    service_type_to_class = {
        "queueserver": QueueserverServiceConfig,
        "queueserver_qtgui": QueueserverQtGUIServiceConfig,
        "bluesky_blissdata": BlueskyBlissdataServiceConfig,
        "daiquiri_bluesky": DaiquiriBlueskyServiceConfig,
        "flint": FlintServiceConfig,
        "queueserver_http_api": QueueserverHTTPAPIConfig,
        "tiled": TiledServiceConfig,
        "redis": RedisServiceConfig,
        "mongodb": MongoDBServiceConfig,
        "mariadb": MariaDBServiceConfig,
        "jupyterhub": JupyterhubServiceConfig,
        "traefik": TraefikServiceConfig,
        "whoami": WhoamiServiceConfig,
        "document_proxy": DocumentProxyServiceConfig,
        "callback_handler": CallbackHandlerServiceConfig,
    }
    try:
        return service_type_to_class[service_type]
    except KeyError:
        raise ValueError(f"Unknown service type: {service_type}.")


def get_service_config(service_type: str, **kwargs) -> ServiceConfig:
    service_config_class = get_service_config_class(service_type)
    return service_config_class(**kwargs)
