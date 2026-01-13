"""
Default configuration values for the Bouquet application.

This module defines default values for various configuration parameters used throughout the Bouquet application.
It provides constants for default service configurations, network settings, volume configurations, and other
application-wide defaults.

The module also provides functions to get and change default values at runtime.

Available Functions:
    change_default: Change the value of a default configuration variable.
    get_default: Get the value of a default configuration variable.
"""

__all__ = [
    "change_default",
    "get_default",
]


COMPOSE_VERSION = "3"

DEFAULT_BEAMLINE_NAME = "default_beamline"

DEFAULT_VERSION = "0.2.0"

DEFAULT_VOLUMES = {
    "batches": {
        "labels": {
            "description": "bluesky batches",
        },
    },
    "redis_data": {
        "labels": {
            "description": "Persistent storage for Redis",
        },
    },
}

DEFAULT_NETWORKS = {
    "internal": {
        "driver": "bridge",
        "labels": {
            "description": "Internal network mode. Ports must be manually exposed to the host.",
        },
    }
}

DEFAULT_SERVICES = {
    "queueserver": {
        "type": "queueserver",
        "image": "registry.hzdr.de/rock-it/wp2/rock-it-starterpack/rock-it_bluesky:demo",
        "environment": {"ZMQ_HOST": "document-proxy", "ZMQ_PORT": 5577},
    },
    # "queueserver_qtgui": {
    #     "type": "queueserver_qtgui",
    #     "title": "Demo",
    #     "queueserver": "queueserver",
    # },
    "qapi": {
        "type": "queueserver_http_api",
    },
    "bluesky-blissdata": {"type": "bluesky_blissdata", "proxy": "document-proxy"},
    "daiquiri": {
        "type": "daiquiri_bluesky",
        "redis": "redis_bluesky-blissdata",
        "environment": {"QSERVER_API_KEY": "123456"},
        "queueserver_http_api": "qapi",
    },
    "flint": {"type": "flint", "redis": "redis_bluesky-blissdata"},
    "jupyterhub": {"type": "jupyterhub"},
    "document-proxy": {"type": "document_proxy"},
}

DEFAULT_CONFIGURATION_FILE = "beamline_config.yml"
DEFAULT_COMPOSE_NAME = "./podman-compose.yml"
DEFAULT_HOST_IP_ADDRESS = "127.0.0.1"
DEFAULT_USE_DOCKER = False
DEFAULT_GENERATE_COMPOSE_ONLY = False
ALLOWED_SERVICE_TYPES = {
    "queueserver": "registry.hzdr.de/rock-it/wp2/rock-it-starterpack/rock-it_bluesky:latest",
    "queueserver_qtgui": "registry.hzdr.de/hzb/bluesky/qt_gui/images/minimal-qt-gui-image:v1.0.6",
    "bluesky_blissdata": "registry.hzdr.de/rock-it/wp2/rock-it-starterpack/rock-it_bluesky-blissdata:latest",
    "daiquiri_bluesky": "registry.hzdr.de/rock-it/wp2/rock-it-starterpack/rock-it_daiquiri:latest",
    "flint": "registry.hzdr.de/rock-it/wp2/flint_docker:latest",
    "queueserver_http_api": "registry.hzdr.de/rock-it/wp2/rock-it-starterpack/rock-it_qapi:latest",
    "tiled": "ghcr.io/bluesky/tiled:latest",
    "redis": "docker.io/redis/redis-stack:7.2.0-v5",
    "mongodb": "docker.io/mongo:latest",
    "mariadb": "docker.io/esrfbcu/mimosa-database:main",
    "jupyterhub": "registry.hzdr.de/rock-it/wp2/rock-it-starterpack/rock-it_jupyterhub:latest",
    "traefik": "docker.io/traefik:latest",
    "whoami": "docker.io/containous/whoami:latest",
    "document_proxy": "registry.hzdr.de/rock-it/wp2/rock-it-starterpack/rock-it_document-proxy:latest",
    "callback_handler": "registry.hzdr.de/rock-it/wp2/rock-it-starterpack/rock-it_callbacks:latest",
}

DEFAULT_APPLY_TRAEFIK_LABELS = False

ALL_DEFAULTS = {
    "COMPOSE_VERSION": COMPOSE_VERSION,
    "DEFAULT_VERSION": DEFAULT_VERSION,
    "DEFAULT_BEAMLINE_NAME": DEFAULT_BEAMLINE_NAME,
    "DEFAULT_VOLUMES": DEFAULT_VOLUMES,
    "DEFAULT_NETWORKS": DEFAULT_NETWORKS,
    "DEFAULT_SERVICES": DEFAULT_SERVICES,
    "DEFAULT_CONFIGURATION_FILE": DEFAULT_CONFIGURATION_FILE,
    "DEFAULT_COMPOSE_NAME": DEFAULT_COMPOSE_NAME,
    "DEFAULT_HOST_IP_ADDRESS": DEFAULT_HOST_IP_ADDRESS,
    "DEFAULT_USE_DOCKER": DEFAULT_USE_DOCKER,
    "DEFAULT_GENERATE_COMPOSE_ONLY": DEFAULT_GENERATE_COMPOSE_ONLY,
    "ALLOWED_SERVICE_TYPES": ALLOWED_SERVICE_TYPES,
    "DEFAULT_APPLY_TRAEFIK_LABELS": DEFAULT_APPLY_TRAEFIK_LABELS,
}


def change_default(var_name, new_value):
    """
    Change the value of a default configuration variable.
    
    Parameters
    ----------
    var_name : str
        The name of the default variable to change.
    new_value : Any
        The new value to assign to the default variable.
    """
    ALL_DEFAULTS[var_name] = new_value


def get_default(var_name):
    """
    Get the value of a default configuration variable.
    
    Parameters
    ----------
    var_name : str
        The name of the default variable to retrieve.
        
    Returns
    -------
    Any
        The value of the requested default variable.
        
    Raises
    ------
    KeyError
        If the requested variable name does not exist in ALL_DEFAULTS.
    """
    return ALL_DEFAULTS[var_name]
