from typing import Any
from pydantic import Field
import re

from ...models import ServiceConfig
from ...defaults import get_default


class BlueskyBlissdataServiceConfig(ServiceConfig):
    """
    Configuration for Bluesky Blissdata service.

    This class defines the configuration for the Bluesky Blissdata service,
    which translates the Bluesky event model to the Blissdata model. It
    initializes the service with default values for container name, image,
    restart policy, networks, ports, and environment variables.

    Depends_on: redis

    Attributes:
        container_name (str): The name of the container. Default is
            "bluesky_blissdata".
        image (str): The Docker image to use for the service. Default is the
            image defined in ALLOWED_SERVICE_TYPES.
        restart (str): The restart policy for the container. Default is
            "always".
        networks (list): The networks the container is connected to. Default
            is ["internal"].
        ports (list): The ports to expose. Default is ["127.0.0.1:9037:9032",
            "127.0.0.1:5579:5578"].
        depends_on (list): The services this service depends on. Default is
            ["redis"].
        environment (dict): The environment variables for the container.
            Default includes "redis_host", "redis_port", "zmq_host", and
            "zmq_port".
        redis (str): The Redis service name. Default is "redis".
        host_ip (str): The host IP address where services can be accessed.
            Default is the value of DEFAULT_HOST_IP_ADDRESS.
        allow_traefik (bool): Whether to allow Traefik to manage the service.
            Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the
            service. Default is the value of DEFAULT_APPLY_TRAEFIK_LABELS.
        proxy (str): The host for the ZeroMQ connection. Default is "127.0.0.1"
        proxy_port (str | int): The port for the ZeroMQ connection. Default is 5578.
        redis_config_file (str | None): Path to the Redis configuration file.
        log_level (str): The log level for the service. Default is "". Possible values are "info" and "debug".

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the
        configuration with the provided settings and default values.
    """

    redis: str = Field(default="redis")
    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    allow_traefik: bool = Field(default=True)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))
    proxy: str = Field(default="localhost")
    proxy_port: str | int = Field(default=5578)
    redis_config_file: str | None = Field(default=None, description="Path to the Redis configuration file")
    log_level: str = Field(default="")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.host_ip = get_default("DEFAULT_HOST_IP_ADDRESS")
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "bluesky_blissdata"

        if "redis" not in self.model_fields_set:
            self.redis = f"redis_{self.container_name}"

        allowed_service_types = get_default("ALLOWED_SERVICE_TYPES")
        if not self.container_name:
            self.container_name = "bluesky_blissdata"
        if not self.image:
            self.image = allowed_service_types["bluesky_blissdata"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]

        if not self.depends_on:
            self.depends_on = [self.redis]

        verbosity_flag = ""
        if self.log_level.lower() == "info":
            verbosity_flag = "-v"
        elif self.log_level.lower() == "debug":
            verbosity_flag = "-vv"
        default_environment = {
            "REDIS_HOST": self.redis,
            "REDIS_PORT": "6379",
            "ZMQ_HOST": f"{self.proxy}",
            "ZMQ_PORT": f"{self.proxy_port}",
            "VERBOSITY_FLAG": verbosity_flag,
        }

        if isinstance(self.environment, dict):
            default_environment.update(self.environment)
        self.environment = default_environment

        # Derive DNS safe names
        safe_container_name = self.container_name
        safe_container_name = safe_container_name.replace("_", "-")
        safe_container_name = re.sub(r"[^a-zA-Z0-9-]", "", safe_container_name)

        beamline_name = get_default("DEFAULT_BEAMLINE_NAME")
        beamline_name = beamline_name.replace("_", "-")
        beamline_name = re.sub(r"[^a-zA-Z0-9-]", "", beamline_name)

        if not self.labels:
            self.labels = {}

        new_labels = {}

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
