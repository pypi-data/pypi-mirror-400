from typing import Any
from pydantic import Field
import re
from ...models import ServiceConfig
from ...defaults import get_default


class RedisServiceConfig(ServiceConfig):
    """
    Configuration for Redis service.

    This class defines the configuration for the Redis service, which runs the Redis database. It initializes the
        service with default values for container name, image, restart policy, networks, and ports.

    Depends_on: None

    kwargs:
        persist (bool): Whether to persist the data. Default is True.

    Attributes:
        container_name (str): The name of the container. Default is "redis".
        image (str): The Docker image to use for the service. Default is the image defined in ALLOWED_SERVICE_TYPES.
        restart (str): The restart policy for the container. Default is "always".
        networks (list): The networks the container is connected to. Default is ["internal"].
        ports (list): The ports to expose. Default is ["127.0.0.1:6380:6379"].
        allow_traefik (bool): Whether to allow Traefik to manage the service. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the service. Default is False.
        config_file (str): Path to the Redis configuration file. Default is an empty string.

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the configuration with the provided settings and
            default values.
    """

    allow_traefik: bool = Field(default=False)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))
    config_file: str | None = Field(default=None, description="Path to the Redis configuration file")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "redis"
        persist = kwargs.get("persist", True)
        if not self.container_name:
            self.container_name = "redis"
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["redis"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if not self.volumes:
            self.volumes = [f"{self.container_name}_data:/data"] if persist else []

        if self.config_file:
            self.volumes.append(f"{self.config_file}:/usr/local/etc/redis/redis.conf")

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
                f"traefik.http.services.{safe_container_name}.loadbalancer.server.port": "6379",
            }
            if self.apply_traefik_labels
            else {}
        )

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
