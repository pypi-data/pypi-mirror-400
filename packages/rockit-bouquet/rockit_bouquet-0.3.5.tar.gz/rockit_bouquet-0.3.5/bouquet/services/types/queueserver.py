from typing import Any
from pydantic import Field
import re
from ...models import ServiceConfig
from ...defaults import get_default


class QueueserverServiceConfig(ServiceConfig):
    """
    Configuration for Queueserver service.

    This class defines the configuration for the Queueserver service, which runs the Bluesky queueserver. It initializes
    the service with default values for container name, image, restart policy, networks, and environment variables.

    Depends_on: redis

    Attributes:
        container_name (str): The name of the container. Default is "queueserver".
        image (str): The Docker image to use for the service. Default is the image defined in ALLOWED_SERVICE_TYPES.
        restart (str): The restart policy for the container. Default is "always".
        networks (list): The networks the container is connected to. Default is ["internal"].
        depends_on (list): The services this service depends on. Default is ["redis"].
        environment (dict): The environment variables for the container. Default includes "REDIS_HOST" and "REDIS_PORT".
        device_file (str): Name of the device file in config/bluesky/devices. Default is "devices.yml".
        redis (str): The Redis service name. Default is "redis".
        host_ip (str): The host IP address where services can be accessed. Default is the value of
            DEFAULT_HOST_IP_ADDRESS.
        allow_traefik (bool): Whether to allow Traefik to manage the service. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the service. Default is False.
        config_dir (str): The directory on the host to mount as /config in the container. Default is "".

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the configuration with the provided settings and default
            values.
    """

    device_file: str = Field(default="devices.yml")
    redis: str = Field(default="redis")
    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    allow_traefik: bool = Field(default=False)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))
    config_dir: str = Field(default="")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.host_ip = get_default("DEFAULT_HOST_IP_ADDRESS")
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "queueserver"

        if "redis" not in self.model_fields_set:
            self.redis = f"redis_{self.container_name}"

        if not self.container_name:
            self.container_name = "queueserver"
        if not self.depends_on:
            self.depends_on = [self.redis]
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["queueserver"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if not self.volumes:
            self.volumes = []

        if self.config_dir:
            self.volumes.append(f"{self.config_dir}:/config")

        default_environment = {
            "REDIS_HOST": f"{self.redis}",
            "REDIS_PORT": 6379,
            "DEVICE_URI_PATH": f"/config/bluesky/devices/{self.device_file}",
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
                f"traefik.http.routers.{safe_container_name}-info.rule": f'Host("{safe_container_name}-'
                f'info.{beamline_name}")',
                f"traefik.http.routers.{safe_container_name}-info.service": f"{safe_container_name}-info",
                f"traefik.http.services.{safe_container_name}-info.loadbalancer.server.port": "60625",
                f"traefik.http.routers.{safe_container_name}-control.rule": f'Host("{safe_container_name}-'
                f'control.{beamline_name}")',  # noqa: E501
                f"traefik.http.routers.{safe_container_name}-control.service": f"{safe_container_name}-control",
                f"traefik.http.services.{safe_container_name}-control.loadbalancer.server.port": "60615",
            }
            if self.apply_traefik_labels
            else {}
        )

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
