from typing import Any
from pydantic import Field
import re

from ...models import ServiceConfig
from ...defaults import get_default


class CallbackHandlerServiceConfig(ServiceConfig):
    """
    Configuration for the Callback Handler service.

    This class defines the configuration for the Callback Handler service, which is responsible for handling
    callbacks in the Bluesky environment. It initializes the service with default values for container name,
    image, restart policy, networks, environment variables, and other settings.

    Attributes:
        host_ip (str): The host IP address where the service can be accessed. Default is the value of
            DEFAULT_HOST_IP_ADDRESS.
        host_port (str | int): The host port for the service. Default is 5580.
        allow_traefik (bool): Whether to allow Traefik to manage the service. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the service. Default is the value of
            DEFAULT_APPLY_TRAEFIK_LABELS.
        proxy (str): The proxy address for the service. Default is "localhost".
        proxy_port (str | int): The proxy port for the service. Default is 5578.
        service_port (str | int | None): The internal service port. Default is None.
        debug (int | str): Debug mode setting. Default is "0".
        config_dir (str): The directory on the host to mount as /config in the container. Default is an empty string.
        config_file (str): The path to the configuration file. Default is "config.yml".

    Methods:
        __init__(**kwargs): Initializes the configuration with the provided settings and default values.
    """

    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    host_port: str | int = Field(default=5580)
    allow_traefik: bool = Field(default=True)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))
    proxy: str = Field(default="localhost")
    proxy_port: str | int = Field(default=5578)
    service_port: str | int | None = Field(default=None)
    debug: int | str = Field(default="0")
    config_dir: str = Field(default="")
    config_file: str = Field(default="config.yml")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.host_ip = get_default("DEFAULT_HOST_IP_ADDRESS")
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "callback_handler"
        allowed_service_types = get_default("ALLOWED_SERVICE_TYPES")

        if not self.container_name:
            self.container_name = "callback_handler"
        if not self.image:
            self.image = allowed_service_types["callback_handler"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if self.service_port is not None:
            self.ports = [f"{self.host_ip}:{self.host_port}:{self.service_port}"]
        if not self.volumes:
            self.volumes = []

        if self.config_dir:
            self.volumes.append(f"{self.config_dir}:/config")

        default_environment = {
            "ZMQ_HOST": f"{self.proxy}",
            "ZMQ_PORT": f"{self.proxy_port}",
            "DEBUG": f"{self.debug}",
            "LOG_DIR": "/logs",
            "CONFIG_FILE": f"/config/{self.config_file}",
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
        if self.service_port is not None:
            new_labels = (
                {
                    "traefik.enable": "true" if self.allow_traefik else "false",
                    f"traefik.http.routers.{safe_container_name}-supervisor.rule": f'Host("{safe_container_name}-'
                    f'supervisor.{beamline_name}")',
                    # noqa: E501
                    f"traefik.http.routers.{safe_container_name}-supervisor.service": f"{safe_container_name}-"
                    f"supervisor",
                    f"traefik.http.services.{safe_container_name}-supervisor.loadbalancer.server."
                    f"port": f"{self.service_port}",
                }
                if self.apply_traefik_labels
                else {}
            )
        else:
            new_labels = {}

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
