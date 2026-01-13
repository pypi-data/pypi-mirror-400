from typing import Any
from pydantic import Field
import re
from ...models import ServiceConfig
from ...defaults import get_default


class FlintServiceConfig(ServiceConfig):
    """
    Configuration for Flint service.

    This class defines the configuration for the Flint service, which runs the Flint display. It initializes the
    service with default values for container name, image, restart policy, networks, ports, volumes, and environment
    variables.

    Depends_on: redis

    Attributes:
        container_name (str): The name of the container. Default is "flint".
        image (str): The Docker image to use for the service. Default is the image defined in ALLOWED_SERVICE_TYPES.
        restart (str): The restart policy for the container. Default is "always".
        networks (list): The networks the container is connected to. Default is ["internal"].
        ports (list): The ports to expose. Default is ["127.0.0.1:9041:9033"].
        volumes (list): The volumes to mount. Default is ["/tmp/.X11-unix:/tmp/.X11-unix"].
        depends_on (list): The services this service depends on. Default is ["redis"].
        environment (dict): The environment variables for the container. Default includes "REDIS_DATA_HOST" and
            "DISPLAY".
        host_ip (str): The host IP address where services can be accessed. Default is the value of
            DEFAULT_HOST_IP_ADDRESS.
        redis (str): The Redis service name. Default is "redis".
        redis_index (int): Index of the Redis database. Default is 0.
        allow_traefik (bool): Whether to allow Traefik to manage the service. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the service. Default is the value of

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the configuration with the provided settings and default
            values.
    """

    redis: str = Field(default="redis")
    redis_index: int = Field(default=0)
    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    allow_traefik: bool = Field(default=True)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.host_ip = get_default("DEFAULT_HOST_IP_ADDRESS")
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "flint"
        if not self.container_name:
            self.container_name = "flint"
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["flint"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if not self.volumes:
            self.volumes = ["/tmp/.X11-unix:/tmp/.X11-unix"]
        if not self.ports:
            self.ports = [f"{self.host_ip}:9041:9033"]

        if not self.depends_on:
            self.depends_on = [self.redis]

        default_environment = {
            "REDIS_DATA_HOST": f"redis://{self.redis}:6379/{self.redis_index}",
            "DISPLAY": "${DISPLAY}",
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

        new_labels = (
            {
                "traefik.enable": "true" if self.allow_traefik else "false",
                f"traefik.http.routers.{safe_container_name}.rule": f'Host("{safe_container_name}.{beamline_name}")',
                f"traefik.http.services.{safe_container_name}.loadbalancer.server.port": "9033",
            }
            if self.apply_traefik_labels
            else {}
        )

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
