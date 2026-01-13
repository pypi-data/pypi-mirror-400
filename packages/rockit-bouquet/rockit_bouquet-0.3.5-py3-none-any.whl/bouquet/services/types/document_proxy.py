from typing import Any
from pydantic import Field
import re
from ...models import ServiceConfig
from ...defaults import get_default


class DocumentProxyServiceConfig(ServiceConfig):
    """
    Configuration for Document Proxy service.

    This class defines the configuration for the Document Proxy service, which runs the Bluesky document proxy.
    It initializes the service with default values for container name, image, restart policy, networks, and environment
    variables.

    Attributes:
        container_name (str): The name of the container. Default is "document_proxy".
        image (str): The Docker image to use for the service. Default is the image defined in ALLOWED_SERVICE_TYPES.
        restart (str): The restart policy for the container. Default is "always".
        networks (list): The networks the container is connected to. Default is ["internal"].
        depends_on (list): The services this service depends on. Default is an empty list.
        environment (dict): The environment variables for the container. Default includes "IN_PORT", "OUT_PORT", and
        "VERBOSITY".
        in_port (str | int): The port for data from Bluesky Publisher. Default is 5577.
        out_port (str | int): The ZMQ Publishing port for subscribers. Default is 5578.
        host_ip (str): The host IP address where services can be accessed. Default is the value of
        DEFAULT_HOST_IP_ADDRESS.
        host_port (str | int): The host port for the service. Default is 5578.
        allow_traefik (bool): Whether to allow Traefik to manage the service. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the service. Default is the value of

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the configuration with the provided settings and default
            values.
    """

    in_port: str | int = Field(default=5577, description="Port for data from Bluesky Publisher.")
    out_port: str | int = Field(default=5578, description="ZMQ Publishing port for subscribers.")
    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    host_port: str | int = Field(default=5578)
    allow_traefik: bool = Field(default=True)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._service_type = "document_proxy"
        if not self.container_name:
            self.container_name = "document_proxy"
        if not self.depends_on:
            self.depends_on = []
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["document_proxy"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if not self.labels:
            self.labels = {}
        if not self.ports:
            self.ports = [f"{self.host_ip}:{self.host_port}:{self.out_port}"]

        default_environment = {
            "IN_PORT": self.in_port,
            "OUT_PORT": self.out_port,
            "VERBOSITY": "SILENT",
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
                f"traefik.http.services.{safe_container_name}.loadbalancer.server.port": f"{self.out_port}",
            }
            if self.apply_traefik_labels
            else {}
        )

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
