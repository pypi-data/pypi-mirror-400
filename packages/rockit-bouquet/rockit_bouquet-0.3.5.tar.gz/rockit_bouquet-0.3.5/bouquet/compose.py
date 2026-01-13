import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List

from . import get_service_config_class
from .models import BeamlineConfig, ComposeConfig, ServiceConfig
from .services import get_service_config
from .defaults import get_default

__all__ = [
    "get_compose_config",
    "run_compose",
    "get_compose_header",
]


def _get_all_services(services_as_dict: Dict[str, Dict[str, Any]], **kwargs) -> Dict[str, ServiceConfig]:
    """
    Convert a dictionary of service configurations to ServiceConfig objects.
    
    This internal function takes a dictionary of service configurations from the beamline config
    and converts them to ServiceConfig objects. It handles extracting the service type,
    setting default container names, and merging additional keyword arguments.
    
    Parameters
    ----------
    services_as_dict : Dict[str, Dict[str, Any]]
        Dictionary of service configurations where keys are service names and values are
        dictionaries of service attributes.
    **kwargs : Any
        Additional keyword arguments to merge into each service configuration.
        
    Returns
    -------
    Dict[str, ServiceConfig]
        Dictionary of ServiceConfig objects where keys are service names.
        
    Raises
    ------
    ValueError
        If a service is missing a type.
    """
    service_models = {}
    for service_name, _config in services_as_dict.items():
        config = _config.copy()

        if "service_type" in config:
            service_type = config.pop("service_type")
        elif "type" in config:
            service_type = config.pop("type")
        else:
            raise ValueError(f"Service '{service_name}' is missing a type.")

        if "container_name" not in config:
            config["container_name"] = config.get("name", service_name)

        # merge kwargs into config
        config.update(kwargs)

        # Pass only the allowed fields to the service class
        allowed_fields = get_service_config_class(service_type).model_fields.keys()
        service_models[service_name] = get_service_config(
            service_type=service_type, **{k: v for k, v in config.items() if k in allowed_fields}
        )

    return service_models


def get_compose_config(
    beamline_config: BeamlineConfig,
    networks: Dict[str, Any] = get_default("DEFAULT_NETWORKS"),
    volumes: Dict[str, Any] = get_default("DEFAULT_VOLUMES"),
    compose_version: str = get_default("COMPOSE_VERSION"),
    host_ip: str = "127.0.0.1",
    use_docker: bool = False,
) -> ComposeConfig:
    """
    Generate a ComposeConfig object from the given beamline configuration.

    This function takes a BeamlineConfig object and generates a ComposeConfig object
    that includes services, networks, and volumes. It also checks for any undefined
    services that are required by the defined services and adds them to the configuration.

    Parameters
    ----------
    beamline_config : BeamlineConfig
        The configuration object for the beamline, containing service definitions.
    networks : Dict[str, Any], optional
        A dictionary of network configurations to include in the compose file (default is DEFAULT_NETWORKS).
    volumes : Dict[str, Any], optional
        A dictionary of volume configurations to include in the compose file (default is DEFAULT_VOLUMES).
    compose_version : str, optional
        The version of the docker-compose format to use (default is COMPOSE_VERSION).
    host_ip : str, optional
        The IP address of the host machine (default is "127.0.0.1").
    use_docker : bool, optional
        Whether to use Docker instead of Podman (default is False).

    Returns
    -------
    ComposeConfig
        The generated ComposeConfig object containing the complete configuration for services, networks, and volumes.

    Raises
    ------
    ValueError
        If a required service is not defined in the service configuration and is not one of the default services
        (redis, mariadb, mongodb).
    """
    services = _get_all_services(beamline_config.services, host_ip=host_ip, use_docker=use_docker)
    compose = ComposeConfig(
        version=compose_version,
        services=services,
        networks=networks,
        volumes=volumes,
    )

    # Check for undefined services and add them to the configuration
    required_services = _get_required_services(compose.services)
    undefined_services = _which_dependent_services_are_undefined(required_services, compose.services)
    services_depending_on_undefined_services = _map_services_depending_on_undefined(
        undefined_services, compose.services
    )
    new_services = {}
    for undefined_service in undefined_services:
        if "redis" in undefined_service:
            redis_extra_kwargs = {}
            for dependent_service in services_depending_on_undefined_services.get(undefined_service, []):
                if hasattr(dependent_service, "redis_config_file") and dependent_service.redis_config_file:
                    redis_extra_kwargs["config_file"] = dependent_service.redis_config_file
                break
            new_services[undefined_service] = get_service_config(
                service_type="redis", container_name=undefined_service, **redis_extra_kwargs
            )
        elif "mariadb" in undefined_service:
            new_services[undefined_service] = get_service_config(
                service_type="mariadb", container_name=undefined_service
            )
        elif "mongodb" in undefined_service:
            new_services[undefined_service] = get_service_config(
                service_type="mongodb", container_name=undefined_service
            )
        else:
            raise ValueError(f"Service {undefined_service} is not defined in the service configuration.")

    # Add new services to the configuration
    for service in new_services.values():
        compose.services[service.container_name] = service

    # Look for any volumes in the configs that should be added to the compose file list of volumes
    volumes = compose.volumes
    for service in compose.services.values():
        if service.volumes:
            for volume in service.volumes:
                host_volume = volume.split(":")[0]
                if "/" in host_volume:
                    continue
                if host_volume not in volumes:
                    volumes[host_volume] = {}

    # If relying on traefik, add the traefik service to the configuration
    if beamline_config.rely_on_traefik:
        if "traefik" not in compose.services:
            compose.services["traefik"] = get_service_config(service_type="traefik", container_name="traefik")

    return compose


def _get_required_services(services: Dict[str, ServiceConfig]) -> set:
    """
    Extract all services that are required by the defined services.
    
    This internal function examines the depends_on attribute of each service
    and collects all services that are required by any service.
    
    Parameters
    ----------
    services : Dict[str, ServiceConfig]
        Dictionary of ServiceConfig objects where keys are service names.
        
    Returns
    -------
    set
        Set of service names that are required by any service.
    """
    required_services = set()
    for _, service in services.items():
        if hasattr(service, "depends_on"):
            if service.depends_on:
                required_services.update(service.depends_on)
    return required_services


def _which_dependent_services_are_undefined(required_services: set, defined_services: Dict[str, ServiceConfig]) -> set:
    """
    Identify services that are required but not defined.
    
    This internal function compares the set of required services with the set of defined services
    to identify services that are required but not defined.
    
    Parameters
    ----------
    required_services : set
        Set of service names that are required by any service.
    defined_services : Dict[str, ServiceConfig]
        Dictionary of ServiceConfig objects where keys are service names.
        
    Returns
    -------
    set
        Set of service names that are required but not defined.
    """
    undefined_services = set()
    for service in required_services:
        if service not in defined_services:
            undefined_services.add(service)
    return undefined_services


def _map_services_depending_on_undefined(
    undefined_services: set, defined_services: Dict[str, ServiceConfig]
) -> Dict[str, List[ServiceConfig]]:
    """
    Map undefined services to the services that depend on them.
    
    This internal function creates a mapping from undefined services to the list of
    services that depend on them. This is useful for determining which services
    need to be created automatically.
    
    Parameters
    ----------
    undefined_services : set
        Set of service names that are required but not defined.
    defined_services : Dict[str, ServiceConfig]
        Dictionary of ServiceConfig objects where keys are service names.
        
    Returns
    -------
    Dict[str, List[ServiceConfig]]
        Dictionary mapping undefined service names to lists of ServiceConfig objects
        that depend on them.
    """
    services_depending_on_undefined = {}
    for service_name, service in defined_services.items():
        if hasattr(service, "depends_on") and service.depends_on:
            for dep in service.depends_on:
                if dep in undefined_services:
                    if dep not in services_depending_on_undefined:
                        services_depending_on_undefined[dep] = []
                    services_depending_on_undefined[dep].append(service)
    return services_depending_on_undefined


def run_compose(use_docker, filename):
    """
    Starts the services defined in the generated Podman or Docker Compose file.

    Parameters
    ----------
    use_docker : bool
        Whether to use Docker instead of Podman.
    filename : str
        The name of the compose file.
    """
    if use_docker:
        print("Starting docker-compose...")
        try:
            subprocess.run(
                ["docker", "compose", "-f", filename, "up", "-d", "--remove-orphans"],
                check=True,
            )
        except FileNotFoundError:
            try:
                subprocess.run(
                    ["docker-compose", "-f", filename, "up", "-d", "--remove-orphans"],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Subprocess failed with return code {e.returncode}")
                sys.exit(1)
            except FileNotFoundError as e:
                print(e)
                sys.exit(1)
    else:
        print("Starting podman-compose...")
        try:
            subprocess.run(
                ["podman-compose", "-f", filename, "up", "-d", "--remove-orphans"],
                check=True,
            )
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Subprocess failed with return code {e.returncode}")
            sys.exit(1)


def get_compose_header(
    beamline_config: BeamlineConfig,
    compose_config: ComposeConfig,
    filename: str,
    beamline_dir: str,
    config_file: str,
    host_ip_address: str,
    is_demo: bool = False,
) -> List[str]:
    """
    Generate the header for the Podman or Docker Compose file.

    Parameters
    ----------
    beamline_config : BeamlineConfig
        The beamline configuration object.
    compose_config : ComposeConfig
        The compose configuration object.
    filename : str
        The name of the compose file.
    beamline_dir : str
        The path to the beamline directory.
    config_file : str
        The path to the beamline configuration file.
    host_ip_address : str
        The IP address of the host machine.
    is_demo : bool, optional
        Whether the configuration is for a demo (default is False).
    """

    # Create the header
    header = [
        "# Bouquet generated docker-compose file",
        f"# Beamline: {beamline_config.beamline_name}",
        f'# Compose file generated at {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}',
        "# This is a demo." if is_demo else "",
        "\n# Composition information:",
        f"# Beamline directory: {beamline_dir}",
        f"# Beamline configuration file: {config_file}",
        f"# Compose file name: {filename}",
        f"# Host IP address: {host_ip_address}",
        f"# Rely on Traefik: {beamline_config.rely_on_traefik}",
        f"# Apply traefik labels: {beamline_config.apply_traefik_labels}",
        "\n# Services:",
        "# NAME : SERVICE_TYPE : IMAGE",
    ]
    for service in compose_config.services.values():
        header.append(f"# {service.container_name} : {service._service_type} : {service.image}")

    return header
