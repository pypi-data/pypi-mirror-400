"""
Bouquet is intended to make it simpler to define and run a set of services for a beamline. This software defines and
maintains a set of service classes with predefined behaviors and configurations. This allows a user to define the
desired set of services at a high architectural level, and Bouquet will generate the necessary compose file to run the
services.

It is designed to be used with a beamline directory that contains a `beamline_config.yml` file.
This file contains the configuration for the services that will be run in the Compose configuration.

Bouquet recognizes the following service types:
- 'queueserver': A service running a Bluesky kernel and queueserver.
- 'queueserver_http_api': A service running a Bluesky queueserver HTTP API.
- 'queueserver_qtgui': A service running a QT GUI for the Bluesky queueserver.
- 'bluesky_blissdata': A service which translates the Bluesky event model to the Blissdata model.
- 'daiquiri_bluesky': A service running the Daiquiri graphical user interface.
- 'flint': A service running the Flint graphical interface to Blissdata.
- 'redis': A service running a Redis server.
- 'mariadb': A service running a MariaDB server.
- 'mongodb': A service running a MongoDB server.
- 'jupyterhub': A service running a JupyterHub server.
- 'traefik': A service running a Traefik reverse proxy.
- 'whoami': A service running a simple HTTP server that returns information about the incoming request.

Running Bouquet performs the following tasks:
1. Parses environment variables and command-line arguments to configure the script's behavior.
2. Generates a Podman or Docker Compose file based on the provided or default beamline configuration.
3. Optionally starts the services defined in the generated Compose file.

Environment Variables:
- BEAMLINE_DIR: Path to the host Bluesky directory.
- BEAMLINE_CONFIG: Path to the beamline configuration file.
- COMPOSE_NAME: Name of the compose file to generate (default: 'podman-compose.yml').
- COMPOSE_PATH: Path to the directory where the compose file will be generated.
- HOST_IP_ADDRESS: IP address to expose the services (default: '127.0.0.1').
- USE_DOCKER: Flag to use Docker instead of Podman (default: False).
- GENERATE_COMPOSE_ONLY: Flag to only generate the compose file without starting the services (default: False).
- DEMO: Flag to run the demo configuration (default: False).

Command-Line arguments passed to Bouquet will override environment variables.

Author: Devin Burke
Contact: devin.burke@desy.de
"""

import os
import sys
import subprocess

import yaml
import argparse
import re

from .writing import write_compose_file

from . import BeamlineConfig, get_compose_config
from .compose import run_compose, get_compose_header
from .defaults import change_default, get_default

# Get the environment variables
BEAMLINE_DIR = os.environ.get("BEAMLINE_DIR", None)
BEAMLINE_CONFIG = os.environ.get("BEAMLINE_CONFIG", None)
COMPOSE_NAME = os.environ.get("COMPOSE_NAME", get_default("DEFAULT_COMPOSE_NAME"))
COMPOSE_PATH = os.environ.get("COMPOSE_PATH", None)
HOST_IP_ADDRESS = os.environ.get("HOST_IP_ADDRESS", get_default("DEFAULT_HOST_IP_ADDRESS"))
USE_DOCKER = os.environ.get("USE_DOCKER", get_default("DEFAULT_USE_DOCKER"))
GENERATE_COMPOSE_ONLY = os.environ.get("GENERATE_COMPOSE_ONLY", get_default("DEFAULT_GENERATE_COMPOSE_ONLY"))
DEMO = os.environ.get("DEMO", False)
APPLY_TRAEFIK_LABELS = os.environ.get("APPLY_TRAEFIK_LABELS", get_default("DEFAULT_APPLY_TRAEFIK_LABELS"))

# Parse the command line arguments. These will override the environment variables.
parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    "positional_beamline_dir", nargs="?", help="Path to the host beamline directory (positional argument)."
)
parser.add_argument("-b", "--beamline-dir", "--beamline_dir", help="Path to the host beamline directory.")
parser.add_argument("-c", "--beamline-config", "--beamline_config", help="Path to the beamline configuration file.")
parser.add_argument(
    "-n",
    "--compose-name",
    "--compose_name",
    help='Path to the compose file. Defaults to "./podman-compose.yml"',
)
parser.add_argument(
    "-p",
    "--compose-path",
    "--compose_path",
    help="Path to the directory where the compose file will be generated.",
)
parser.add_argument("-d", "--demo", action="store_true", help="Run the demo configuration.")
parser.add_argument("-i", "--host-ip-address", "--host_ip_address", help="IP Address to expose the services.")
parser.add_argument(
    "-u",
    "--use-docker",
    "--use_docker",
    action="store_true",
    help="When true, uses docker instead of podman.",
)
parser.add_argument(
    "-g",
    "--generate-compose-only",
    "--generate_compose_only",
    action="store_true",
    help="Only generate the compose file and do not start the services.",
)
parser.add_argument(
    "-t",
    "--apply-traefik-labels",
    "--apply_traefik_labels",
    action="store_true",
    help="Apply Traefik labels to all services.",
)
args = parser.parse_args()

# Override the environment variables with the command line arguments
if args.beamline_dir is not None:
    BEAMLINE_DIR = args.beamline_dir
elif args.positional_beamline_dir is not None:
    if os.path.isdir(args.positional_beamline_dir):
        BEAMLINE_DIR = args.positional_beamline_dir
    elif os.path.isfile(args.positional_beamline_dir):
        BEAMLINE_CONFIG = args.positional_beamline_dir
if args.beamline_config is not None:
    BEAMLINE_CONFIG = args.beamline_config
if args.compose_name is not None:
    COMPOSE_NAME = args.compose_name
if args.compose_path is not None:
    COMPOSE_PATH = args.compose_path
if args.demo:
    DEMO = args.demo
if args.host_ip_address is not None:
    HOST_IP_ADDRESS = args.host_ip_address
if args.use_docker:
    USE_DOCKER = args.use_docker
if args.generate_compose_only:
    GENERATE_COMPOSE_ONLY = args.generate_compose_only
if args.apply_traefik_labels:
    APPLY_TRAEFIK_LABELS = args.apply_traefik_labels

# If not running the demo, BEAMLINE_DIR or BEAMLINE_CONFIG must be set
if not DEMO and not BEAMLINE_DIR and not BEAMLINE_CONFIG:
    parser.print_help()
    sys.exit(0)

# Check if COMPOSE_PATH is a valid directory
if COMPOSE_PATH and not os.path.isdir(COMPOSE_PATH):
    print(f"COMPOSE_PATH {COMPOSE_PATH} is not a valid directory.")
    sys.exit(1)

# Check if BEAMLINE_DIR is a valid directory
if BEAMLINE_DIR and not os.path.isdir(BEAMLINE_DIR):
    print(f"BEAMLINE_DIR {BEAMLINE_DIR} is not a valid directory.")
    sys.exit(1)


def get_ip_address(domain_name):
    passed_ip = domain_name
    # Regular expression to check if HOST_IP_ADDRESS is an IP address
    ip_pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

    if not ip_pattern.match(domain_name):
        try:
            new_address = subprocess.check_output(["dig", "+short", domain_name], encoding="utf-8").strip()
            if not new_address:
                raise ValueError(f"Could not get IP address for {passed_ip}")
            return new_address
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Subprocess failed with return code {e.returncode}") from e
        except FileNotFoundError as e:
            raise RuntimeError("The 'dig' command is not found") from e
    return domain_name


def filter_compose(compose_config, key, exceptions=None):
    """
    Remove the specified key from services in the compose configuration, except for the specified exceptions.

    Parameters
    ----------
    compose_config : ComposeConfig
        The compose configuration object.
    key : str
        The key to remove from each service in the compose configuration.
    exceptions : list, optional
        A list of service names to exclude from the filter.

    Returns
    -------
    ComposeConfig
        The updated compose configuration with the specified key removed from each service, except for the exceptions.
    """
    if exceptions is None:
        exceptions = []
    for service_name, service in compose_config.services.items():
        if service_name.lower() in exceptions:
            continue
        if hasattr(service, key):
            delattr(service, key)
    return compose_config


def remove_traefik_labels(compose_config):
    """
    Remove any keys that start with 'traefik' from the labels of each service in the compose configuration.

    Parameters
    ----------
    compose_config : ComposeConfig
        The compose configuration object.

    Returns
    -------
    ComposeConfig
        The updated compose configuration with 'traefik' labels removed from each service.
    """
    for service_name, service in compose_config.services.items():
        if hasattr(service, "labels") and isinstance(service.labels, dict):
            service.labels = {k: v for k, v in service.labels.items() if not k.startswith("traefik")}
    return compose_config


def main():
    """
    Main function that orchestrates the generation and running of the Podman or Docker Compose configuration.
    """
    beamline_dir = ""
    beamline_config_file = ""
    compose_name = COMPOSE_NAME
    if DEMO:
        config = BeamlineConfig(
            beamline_name="default_beamline",
            description="Default beamline configuration",
            contact_person="John Doe",
            contact_email="myemail@fakeemail.com",
            contact_phone="555-0123",
            host_ip_address=get_default("DEFAULT_HOST_IP_ADDRESS"),
            version=get_default("DEFAULT_VERSION"),
            services=get_default("DEFAULT_SERVICES"),
        )
    else:
        # User sets only BEAMLINE_DIR, in which case we use the default beamline_config.yml in that directory
        if BEAMLINE_DIR and not BEAMLINE_CONFIG:
            beamline_dir = BEAMLINE_DIR
            beamline_config_file = os.path.join(beamline_dir, get_default("DEFAULT_CONFIGURATION_FILE"))
        # User sets only BEAMLINE_CONFIG, in which case we use that file and set its directory as BEAMLINE_DIR
        elif BEAMLINE_CONFIG and not BEAMLINE_DIR:
            beamline_config_file = BEAMLINE_CONFIG
            beamline_dir = os.path.dirname(beamline_config_file)
        # User sets both BEAMLINE_DIR and BEAMLINE_CONFIG
        elif BEAMLINE_DIR and BEAMLINE_CONFIG:
            beamline_dir = BEAMLINE_DIR
            # If BEAMLINE_CONFIG is a file, use it
            if os.path.isfile(BEAMLINE_CONFIG):
                beamline_config_file = BEAMLINE_CONFIG
            else:
                # Look for the beamline configuration file in the beamline directory
                try:
                    beamline_config_file = os.path.join(beamline_dir, BEAMLINE_CONFIG)
                except FileNotFoundError:
                    print(f"Could not find {BEAMLINE_CONFIG} in {BEAMLINE_DIR}")
                    sys.exit(1)

        else:
            print("Please set BEAMLINE_DIR or BEAMLINE_CONFIG.")
            sys.exit(1)

        # Change beamline_dir and beamline_config_file to absolute paths
        beamline_dir = os.path.abspath(beamline_dir)
        beamline_config_file = os.path.abspath(beamline_config_file)

        # Set the path to the beamline configuration file
        compose_name = COMPOSE_NAME

        if COMPOSE_PATH:
            compose_name = os.path.join(COMPOSE_PATH, COMPOSE_NAME)

        print(f"Reading beamline configuration from {os.path.basename(beamline_config_file)}")
        with open(beamline_config_file, "r", encoding="utf-8") as file:
            config_file = yaml.safe_load(file)
            config = BeamlineConfig(**config_file)
            compose_name = config.compose_file or COMPOSE_NAME

        # If the beamline directory was not set and the config has a beamline directory, use that
        if config.beamline_dir and not BEAMLINE_DIR:
            beamline_dir = os.path.abspath(config.beamline_dir)

        # set cwd to the beamline directory
        os.chdir(beamline_dir)

    if HOST_IP_ADDRESS is not get_default("DEFAULT_HOST_IP_ADDRESS"):
        host_ip_address = HOST_IP_ADDRESS
    else:
        host_ip_address = config.host_ip_address

    host_ip_address = get_ip_address(host_ip_address)

    # Set globals
    change_default("DEFAULT_BEAMLINE_NAME", config.beamline_name)
    change_default("DEFAULT_HOST_IP_ADDRESS", host_ip_address)
    change_default("DEFAULT_USE_DOCKER", USE_DOCKER)
    change_default("DEFAULT_APPLY_TRAEFIK_LABELS", config.apply_traefik_labels)

    print("Bouquet is generating a new compose file.\n")

    compose_config = get_compose_config(config, host_ip=get_ip_address(host_ip_address), use_docker=USE_DOCKER)

    header = get_compose_header(
        config,
        compose_config,
        compose_name,
        beamline_dir,
        beamline_config_file,
        host_ip_address,
        is_demo=DEMO,
    )
    default_compose_name = get_default("DEFAULT_COMPOSE_NAME")
    if compose_name == default_compose_name and USE_DOCKER:
        compose_name = "docker-compose.yml"

    if config.rely_on_traefik:
        filtered_compose_config = filter_compose(compose_config, "ports", exceptions=["traefik"])
        write_compose_file(filtered_compose_config, compose_name, header)
    else:
        compose_config_without_traefik_labels = remove_traefik_labels(compose_config)
        write_compose_file(compose_config_without_traefik_labels, compose_name, header)

    if header:
        print("--------------------------------------------------")
        for line in header:
            print(line.lstrip("# "))

    if not GENERATE_COMPOSE_ONLY:
        print("Starting the services...")
        run_compose(use_docker=USE_DOCKER, filename=COMPOSE_NAME)


if __name__ == "__main__":
    main()
