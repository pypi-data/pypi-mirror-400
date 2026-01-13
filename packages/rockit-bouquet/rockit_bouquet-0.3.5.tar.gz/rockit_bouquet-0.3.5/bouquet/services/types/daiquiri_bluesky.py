from typing import Any
import re
from pydantic import Field
from ...models import ServiceConfig
from ...defaults import get_default


class DaiquiriBlueskyServiceConfig(ServiceConfig):
    """
    Configuration for Daiquiri Bluesky service.

    This class defines the configuration for the Daiquiri Bluesky service, which runs the Daiquiri browser-based GUI.
    It initializes the service with default values for container name, image, restart policy, networks, ports, and
    environment variables.

    Attributes:
        redis (Optional[str]): The Redis service name. Default is "redis".
        mariadb (Optional[str]): The MariaDB service name. Default is "mariadb".
        queueserver_http_api (Optional[str]): The QueueServer HTTP API service name. Default is "queueserver_http_api".
        host_ip (Optional[str]): The host IP address where services can be accessed. Default is the value of
            DEFAULT_HOST_IP_ADDRESS.
        host_port (str | int): The host port for the service. Default is '8080'.
        allow_traefik (bool): Whether to allow Traefik to manage the service. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the service. Default is False.
        config_dir (str): The directory on the host to the Daiquiri resources directory in the container.
                          Default is an empty string.

    Methods:
        __post_init_post_parse__: Method that runs after the model has been initialized and parsed, setting default
        values for various attributes if they are not provided.
    """

    redis: str = Field(default="redis")
    mariadb: str = Field(default="mariadb")
    queueserver_http_api: str = Field(default="queueserver_http_api")
    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    host_port: str | int = Field(default="8080")
    allow_traefik: bool = Field(default=True)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))
    config_dir: str = Field(default="")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.host_ip = get_default("DEFAULT_HOST_IP_ADDRESS")
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "daiquiri_bluesky"

        if "redis" not in self.model_fields_set:
            self.redis = "bluesky-blissdata"

        if not self.container_name:
            self.container_name = "daiquiri_bluesky"
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["daiquiri_bluesky"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if not self.ports:
            self.ports = [
                f"{self.host_ip}:{self.host_port}:8080",
                # f"{self.host_ip}:9010:9010",
                # f"{self.host_ip}:9030:9030",
            ]
        if not self.depends_on:
            self.depends_on = [self.redis, self.mariadb, self.queueserver_http_api]
        if not self.volumes:
            self.volumes = []

        if self.config_dir:
            self.volumes.append(f"{self.config_dir}/implementors:/daiquiri_bluesky/daiquiri_bluesky/implementors/")
            self.volumes.append(f"{self.config_dir}/resources/config:/daiquiri_bluesky/daiquiri_bluesky/resources/config")
            self.volumes.append(f"{self.config_dir}/resources/layout:/daiquiri_bluesky/daiquiri_bluesky/resources/layout")

        default_environment = {
            "REDIS_HOST": f"{self.redis}:6379",
            "QSERVER_API_HOST": f"{self.queueserver_http_api}:60610",
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
                f"traefik.http.routers.{safe_container_name}.service": safe_container_name,
                f"traefik.http.services.{safe_container_name}.loadbalancer.server.port": f"{self.host_port}",
            }
            if self.apply_traefik_labels
            else {}
        )

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
