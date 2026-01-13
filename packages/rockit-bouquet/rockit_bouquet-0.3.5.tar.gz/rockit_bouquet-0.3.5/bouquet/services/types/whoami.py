from typing import Any
from pydantic import Field
import re
from ...models import ServiceConfig
from ...defaults import get_default


class WhoamiServiceConfig(ServiceConfig):
    """
    Configuration for Whoami service.

    This class defines the configuration for the Whoami service, which is a simple HTTP server that returns information
    about the incoming request. It initializes the service with default values for container name, image, restart
    policy, networks, and ports.

    Attributes:
        container_name (str): The name of the container. Default is "whoami".
        image (str): The Docker image to use for the service. Default is the image defined in ALLOWED_SERVICE_TYPES.
        restart (str): The restart policy for the container. Default is "always".
        networks (list): The networks the container is connected to. Default is ["internal"].
        ports (list): The ports to expose. Default is ["80:80"].
        host_ip (str): The host IP address where services can be accessed. Default is the value of
            DEFAULT_HOST_IP_ADDRESS.
        allow_traefik (bool): Whether to allow Traefik to manage the service. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to the service. Default is False.

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the configuration with the provided settings and default
            values.
    """

    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    allow_traefik: bool = Field(default=True)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.host_ip = get_default("DEFAULT_HOST_IP_ADDRESS")
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "whoami"
        if not self.container_name:
            self.container_name = "whoami"
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["whoami"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if not self.ports:
            self.ports = [f"{self.host_ip}:1081:80"]

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
                f"traefik.http.services.{safe_container_name}.loadbalancer.server.port": "80",
            }
            if self.apply_traefik_labels
            else {}
        )

        for key, value in new_labels.items():
            if key not in self.labels:
                self.labels[key] = value

    class Config:
        extra = "forbid"
