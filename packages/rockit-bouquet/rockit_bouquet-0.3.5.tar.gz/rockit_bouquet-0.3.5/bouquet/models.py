from pydantic import BaseModel, Field, PrivateAttr, validator
from typing import Any, Dict, List
from .defaults import get_default


class BeamlineConfig(BaseModel):
    """
    Pydantic model to store the beamline configuration.

    This is an application-specific configuration file that defines a list of services. Each service must have a "type"
    attribute that defines its service type.

    Valid service keys:
        type (str): The type of service.
        container_name (str): The name of the container.
        image (str): The Docker image to use for the service.
        restart (str): The restart policy for the container.
        environment (Dict[str, Any]): A dictionary of environment variables.
        env_file (List[str]): A list of files containing environment variables.
        ports (List[str]): A list of ports to expose.
        volumes (List[str]): A list of volumes to mount.
        networks (List[str]): A list of networks the container is connected to.
        command (List[str] | str): The command to run in the container.
        depends_on (List[str]): A list of services that this service depends on.

    Valid service types:
        - queueserver: A service running Bluesky and the queueserver
        - queueserver_http_api: A service running the queueserver HTTP API
        - queueserver_qtgui: A service running the queueserver Qt GUI
        - bluesky_blissdata: A service which translates the Bluesky event model to the Blissdata model
        - daiquiri_bluesky: A service which runs the Daiquiri browser-based GUI
        - tiled: Runs the Tiled data service
        - flint: A service running the flint display
        - mariadb: A service running the MariaDB database
        - mongodb: A service running the MongoDB database
        - redis: A service running the Redis database
        - jupyterhub: A service running JupyterHub
        - traefik: A service running the Traefik reverse proxy
        - whoami: A service running a simple HTTP server that returns information about the incoming request

    Example Service:
    'service_name': {
        'type': 'service_type',
        'environment': {
            'key': 'value',
        }
        'depends_on': ['service1', 'service2'],
    }

    Attributes:
        beamline_name (str): The name of the beamline.
        description (str): A description of the beamline.
        contact_person (str): The contact person for the beamline.
        contact_email (str): The contact email for the beamline.
        contact_phone (str): The contact phone number for the beamline.
        version (str): The version of the beamline configuration.
        host_ip_address (str): The domain name or IP address used to access the beamline services.
        services (Dict[str, Dict[str, Any]]): A dictionary of services, where the key is the service name and the value
            is a dictionary of service attributes. The only required attribute for each service is "type".
        compose_file (str | None): The name of the compose file to generate.
        beamline_dir (str | None): The path to the beamline directory. Can be overridden by runtime arguments.
        rely_on_traefik (bool): A flag that causes bouquet to ignore all port configurations to rely solely on Traefik.
                                 For this to work properly, the Traefik service must be named "traefik".
        apply_traefik_labels (bool): A flag that causes bouquet to apply Traefik labels to all services.
    """

    beamline_name: str
    description: str
    contact_person: str
    contact_email: str
    contact_phone: str
    version: str
    host_ip_address: str = Field(default=get_default("DEFAULT_HOST_IP_ADDRESS"))
    services: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    compose_file: str | None = None
    beamline_dir: str | None = None
    rely_on_traefik: bool = False
    apply_traefik_labels: bool = False

    @validator("services")
    def validate_services(cls, services):
        for service_name, service_config in services.items():
            if "type" not in service_config and "service_type" not in service_config:
                raise ValueError(f"Service '{service_name}' is missing both 'type' and 'service_type' attributes.")
        return services


class ServiceConfig(BaseModel):
    """
    Pydantic model to store the service configuration compliant with the docker-compose format.

    This class defines the configuration for a service in a docker-compose file. It includes attributes for container
    name, image, restart policy, environment variables, environment files, ports, volumes, dependencies, networks,
    and commands.

    Attributes:
        container_name (str | None): The name of the container, aliased as "name".
        image (str | None): The Docker image to use for the service.
        restart (str | None): The restart policy for the container.
        entrypoint (List[str] | str | None): The entrypoint command for the container.
        environment (Dict[str, Any] | None): The environment variables for the container.
        env_file (List[str] | None): List of files containing environment variables.
        ports (List[str] | None): The ports to expose.
        volumes (List[str] | None): The volumes to mount.
        depends_on (List[str] | None): The services this service depends on.
        networks (List[str] | None): The networks the container is connected to.
        command (List[str] | str | None): The command to run in the container.
        labels (Dict[str, str] | None): The labels to apply to the container.
    """

    _service_type: str = PrivateAttr()
    container_name: str | None = Field(default=None)
    image: str | None = None
    restart: str | None = None
    entrypoint: List[str] | str | None = None
    environment: Dict[str, Any] | None = Field(default_factory=dict)
    env_file: List[str] | None = None
    ports: List[str] | None = None
    volumes: List[str] | None = None
    depends_on: List[str] | None = None
    networks: List[str] | None = None
    command: List[str] | str | None = None
    labels: Dict[str, str] | None = None

    class Config:
        extra = "allow"


class ComposeConfig(BaseModel):
    """
    Pydantic model to store the docker-compose configuration.

    This class defines the structure of a container composition YAML file.
    It includes attributes for the version of the docker-compose format, services, networks, and volumes.

    Attributes:
        version (str): The version of the docker-compose format.
        services (Dict[str, ServiceConfig]): A dictionary of service configurations, where the key is
            the service name and the value is a ServiceConfig object.
        networks (Dict[str, Dict[str, Any]]): A dictionary of network configurations.
        volumes (Dict[str, Dict[str, Any]]): A dictionary of volume configurations.
    """

    version: str = Field(default=get_default("COMPOSE_VERSION"))
    services: Dict[str, ServiceConfig] = Field(default_factory=dict)
    networks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    volumes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
