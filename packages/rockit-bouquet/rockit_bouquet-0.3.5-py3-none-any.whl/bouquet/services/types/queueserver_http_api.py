from typing import Any
from pydantic import Field
import re
from ...models import ServiceConfig
from ...defaults import get_default


class QueueserverHTTPAPIConfig(ServiceConfig):
    """
    Configuration for Queueserver HTTP API service.

    This class defines the configuration for the Queueserver HTTP API service, which runs the HTTP API for the Bluesky
    queueserver. It initializes the service with default values for container name, image, restart policy, networks,
    ports, and environment variables.

    Depends_on: queueserver

    Attributes:
        container_name (str): The name of the container. Default is "queueserver_http_api".
        image (str): The Docker image to use for the service. Default is the image defined in ALLOWED_SERVICE_TYPES.
        restart (str): The restart policy for the container. Default is "always".
        networks (list): The networks the container is connected to. Default is ["internal"].
        ports (list): The ports to expose. Default is ["127.0.0.1:60610:60610"].
        depends_on (list): The services this service depends on. Default is ["queueserver"].
        environment (dict): The environment variables for the container. Default includes "QSERVER_HOST",
            "QSERVER_PORT", "QSERVER_INFO_PORT", "QSERVER_API_HOST", and "QSERVER_API_PORT".
        queueserver (str): The Queueserver service name. Default is "queueserver".
        host_ip (str): The host IP address where services can be accessed. Default is the value of
            DEFAULT_HOST_IP_ADDRESS.
        host_port (str | int): The host port for the service. Default is 60610.
        allow_traefik (bool): Whether to allow Traefik to manage the service. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the service. Default is False.
        config_dir (str): The directory on the host to mount as /config in the container. Default is "".

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the configuration with the provided settings
            and default values.
    """

    queueserver: str = Field(default="queueserver")
    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    host_port: str | int = Field(default="60610")
    allow_traefik: bool = Field(default=True)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))
    config_dir: str = Field(default="")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.host_ip = get_default("DEFAULT_HOST_IP_ADDRESS")
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "queueserver_http_api"
        if not self.container_name:
            self.container_name = "queueserver_http_api"
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["queueserver_http_api"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if not self.ports:
            self.ports = [f"{self.host_ip}:{self.host_port}:60610"]
        if not self.depends_on:
            self.depends_on = [self.queueserver]
        if not self.volumes:
            self.volumes = []

        if self.config_dir:
            self.volumes.append(f"{self.config_dir}:/config")

        default_environment = {
            "QSERVER_HOST": f"{self.queueserver}",
            "QSERVER_PORT": "60615",
            "QSERVER_INFO_PORT": "60625",
            "QSERVER_API_HOST": f"{self.container_name}",
            "QSERVER_API_PORT": "60610",
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
                f"traefik.http.services.{safe_container_name}.loadbalancer.server.port": "60610",
            }
            if self.apply_traefik_labels
            else {}
        )

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
