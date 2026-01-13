from typing import Any
from pydantic import Field
from ...models import ServiceConfig
from ...defaults import get_default
import os


class TraefikServiceConfig(ServiceConfig):
    """
    Configuration for Traefik service.

    This class defines the configuration for the Traefik service, which acts as a reverse proxy and load balancer. It
    initializes the service with default values for container name, image, restart policy, networks, ports, and
    environment variables.

    Attributes:
        container_name (str): The name of the container. Default is "traefik".
        image (str): The Docker image to use for the service. Default is the image defined in ALLOWED_SERVICE_TYPES.
        restart (str): The restart policy for the container. Default is "always".
        networks (list): The networks the container is connected to. Default is ["internal"].
        ports (list): The ports to expose. Default is ["80:80", "443:443", "8080:8080"].
        environment (dict): The environment variables for the container. Default includes "TRAEFIK_API_INSECURE",
            "TRAEFIK_PROVIDERS_DOCKER", etc.
        host_ip (str): The host IP address where services can be accessed. Default is the value of
            DEFAULT_HOST_IP_ADDRESS.
        use_docker (bool): Whether to use Docker. Default is False.
        enable_dashboard (bool): Whether to enable the Traefik dashboard. Default is True.
        apply_traefik_labels (bool): Whether to apply Traefik labels to services. Default is False.
        config_dir (str): The directory on the host to mount as /etc/traefik/ in the container. Default is "".

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the configuration with the provided settings and default
        values.
    """

    host_ip: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    use_docker: bool = Field(default=False)
    enable_dashboard: bool = Field(default=True)
    apply_traefik_labels: bool = Field(default=get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))
    config_dir: str = Field(default="")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.host_ip = get_default("DEFAULT_HOST_IP_ADDRESS")
        self.apply_traefik_labels = get_default("DEFAULT_APPLY_TRAEFIK_LABELS")
        self._service_type = "traefik"
        user_id = os.getuid()
        if not self.container_name:
            self.container_name = "traefik"
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["traefik"]
        if not self.restart:
            self.restart = "always"
        if not self.networks:
            self.networks = ["internal"]
        if not self.ports:
            self.ports = ["80:80", "443:443", "8080:8080"]
        if not self.volumes:
            self.volumes = []

        if self.config_dir:
            self.volumes.append(f"{self.config_dir}:/etc/traefik/")

        default_environment = {}
        if self.apply_traefik_labels:
            default_environment = {
                "TRAEFIK_API_INSECURE": "false",  # Secure the dashboard
                "TRAEFIK_PROVIDERS_DOCKER": "true",
                "TRAEFIK_ENTRYPOINTS_WEB_ADDRESS": ":80",
                "TRAEFIK_ENTRYPOINTS_WEBSECURE_ADDRESS": ":443",
                "TRAEFIK_EXPOSED_BY_DEFAULT": "false",
            }
            if self.enable_dashboard:
                default_environment["TRAEFIK_API_INSECURE"] = "true"
            if not self.use_docker:
                default_environment["TRAEFIK_PROVIDERS_DOCKER_ENDPOINT"] = "unix:///var/run/podman/podman.sock"

        if isinstance(self.volumes, list):
            self.volumes.append(f"/run/user/{user_id}/podman/podman.sock:/var/run/podman/podman.sock")
        else:
            self.volumes = [f"/run/user/{user_id}/podman/podman.sock:/var/run/podman/podman.sock"]

        if isinstance(self.environment, dict):
            default_environment.update(self.environment)
        self.environment = default_environment

    class Config:
        extra = "forbid"
