<p align="left">
  <img src="assets/bouquet.png" alt="Logo" width="50%">
</p>

# Bouquet

## Overview

Bouquet simplifies the process of defining and running a set of services for a beamline. This software defines and
maintains a set of service classes with predefined behaviors and configurations. This allows a user to define the
desired set of services at a high architectural level, and Bouquet will generate the necessary compose file to run the
services.

It is designed to be used with a beamline directory that contains a `beamline_config.yml` file. This file contains the
configuration for the services that will be run in the Compose configuration.

Each service should only require its name (the corresponding key in services) and its service type. Bouquet will
substitute default values for required composition settings as needed. To overwrite these values you simply enter
key/value pairs into the service just as you would a container composition file (e.g. docker-compose.yml).

Bouquet will automatically generate support services as required (e.g. redis, mariadb, mongodb, etc.)

## Installation

### Prerequisites

- Python 3.11 or higher
- Podman or Docker
- Podman Compose or Docker Compose

### Installing from PyPI

```sh
pip install rockit-bouquet
```

### Installing from Source

1. Clone the repository:
```sh
git clone https://codebase.helmholtz.cloud/rock-it/wp2/rock-it-starterpack/bouquet
cd bouquet
```

2. Install using Poetry:
```sh
poetry install
```

Or using pip:
```sh
pip install .
```

## Project Architecture

Bouquet is organized into several key components:

### Core Components

- **bouquet.py**: The main entry point that handles command-line arguments and environment variables.
- **compose.py**: Handles the generation of the Podman/Docker Compose configuration.
- **models.py**: Defines the data models for beamline configuration, service configuration, and compose configuration.
- **defaults.py**: Provides default values for various configuration parameters.
- **writing.py**: Handles writing the generated compose file to disk.

### Service Types

The `services/types/` directory contains modules for each supported service type. Each service type module defines a class that inherits from `ServiceConfig` and provides default values and configuration for that service type.

### Data Flow

1. The user provides a beamline configuration file or directory.
2. Bouquet parses the configuration and creates a `BeamlineConfig` object.
3. The `get_compose_config` function converts the `BeamlineConfig` to a `ComposeConfig` object.
4. The `write_compose_file` function writes the `ComposeConfig` to a YAML file.
5. If not in generate-only mode, Bouquet runs the compose file using Podman or Docker.

### Extension

To add a new service type:

1. Create a new module in `services/types/` with a class that inherits from `ServiceConfig`.
2. Add the service type to the `ALLOWED_SERVICE_TYPES` dictionary in `defaults.py`.
3. Implement the necessary configuration in the service type class.

## Features

- Parses environment variables and command-line arguments to configure the script's behavior.
- Generates a Podman or Docker Compose file based on the provided beamline configuration file.
- Starts the services defined in the beamline configuration file with Podman or Docker Compose.
- Supports a variety of service types, including Bluesky queueservers, QT GUIs, and HTTP APIs, Daiquiri, Flint, Redis,
MariaDB, and MongoDB.
- A beamline configuration file can be created to fully define the services to be run. Bouquet will handle necessary
substitutions and configurations.
- `rely_on_traefik` and `apply_traefik_labels` are two options that enable
easy implementation of traefik. The former will automatically add the traefik reverse proxy service and disable exposed ports of other services. The latter will automatically apply pre-defined labels to the services to configure traefik without needing to mount a traefik.yml config file.

### Example beamline_config.yml
#### A simple example
```yml
beamline_name: default_beamline
description: Default beamline configuration
contact_person: John Doe
contact_email: "myemail@fakeemail.com"
contact_phone: 555-0123
version: '3'
host_ip_address: 127.0.0.1
services:
  queueserver:
    type: queueserver
  queueserver_qtgui:
    type: queueserver_qtgui
  queueserver_http_api:
    type: queueserver_http_api
  bluesky_blissdata:
    type: bluesky_blissdata
  daiquiri:
    type: daiquiri_bluesky
  flint:
    type: flint
```
#### A more complex example
```yml
beamline_name: p65
description: ROCK-IT catalysis demonstrator at Petra-III P65, DESY
contact_person: Devin Burke
contact_email: email@domain.com
contact_phone: "0000"
host_ip_address: "domainname.desy.de"
compose_file: "./podman-compose.yml"
version: '0.3.0'
rely_on_traefik: true
apply_traefik_labels: true

services:
  bluesky-primary:
    type: queueserver
    image: myregistry/beamlineQueue:latest
    device_file: sim_devices.yml
    image: "beamline_p65:latest"
    volumes:
      - /beamlinestorage:/beamlinestorage

  bluesky-secondary:
    type: queueserver
    device_file: sim_devices.yml
    volumes:
      - ./config/bluesky-secondary:/config
      - ./src/p65:/opt/bluesky/

  bluesky-primary-qtgui:
    type: queueserver_qtgui
    title: "Primary Queue Server"
    queueserver: bluesky-primary

  bluesky-secondary-qtgui:
    type: queueserver_qtgui
    title: "Secondary Queue Server"
    queueserver: bluesky-secondary

  bluesky-blissdata:
    type: bluesky_blissdata
    redis: redis_bluesky_blissdata

  daiquiri:
    type: daiquiri_bluesky
    queueserver_http_api: qapi
    redis: redis_bluesky_blissdata
    env_file:
      - ./daiquiri_keys.env
  
  flint:
    type: flint
    redis: redis_bluesky_blissdata

  qapi:
    type: queueserver_http_api
    env_file:
      - ./qapi_keys.env
    queueserver: bluesky-primary

  tiled:
    type: tiled
    env_file:
      - ./tiled_keys.env
    volumes:
      - ./config/tiled:/deploy/config
```

## Supported Service Types

Bouquet recognizes the following service types:
- `queueserver`: A service running a Bluesky kernel and queueserver.
- `queueserver_http_api`: A service running a Bluesky queueserver HTTP API.
- `queueserver_qtgui`: A service running a QT GUI for the Bluesky queueserver.
- `bluesky_blissdata`: A service which translates the Bluesky event model to the Blissdata model.
- `daiquiri_bluesky`: A service running the Daiquiri graphical user interface.
- `flint`: A service running the Flint graphical interface to Blissdata.
- `redis`: A service running a Redis server.
- `mariadb`: A service running a MariaDB server.
- `mongodb`: A service running a MongoDB server.
- `jupyterhub`: A jupyterhub service which spawns JupyterLab instances.
- `traefik`: A reverse-proxy service to securely manage network traffic to and from the pod.
- `whoami`: A tiny Go webserver that prints OS information and HTTP request to output. Useful for development.
- `document_proxy`: A service that acts as a proxy for the Bluesky publisher and ZMQ subscriber.
- `tiled`: A service that runs a Tiled server for data access.
- `callback_handler`: A service that runs a RemoteDispatcher and callback handler for Bluesky. This offloads the
                      callback handling from the queueserver to a separate service.

### Service Configuration
Services in Bouquet are meant to be extensions of container composition files (e.g. docker-compose.yml).
This means that you can add any key/value pair that you would normally add to a container composition file to the
service configuration in the beamline configuration file. Bouquet will substitute default values for required
composition settings as needed.

All service types inherit from bouquet.models.`ServiceConfig`

#### Service Config Attributes:
- `container_name` (str): The name of the container, aliased as "name".
- `image` (str): The Docker image to use for the service.
- `restart` (str): The restart policy for the container.
- `entrypoint` (List[str] | str): The entrypoint command for the container.
- `environment` (Dict[str, Any]): The environment variables for the container.
- `env_file` (List[str]): List of files containing environment variables.
- `ports` (List[str]): The ports to expose.
- `volumes` (List[str]): The volumes to mount.
- `depends_on` (List[str]): The services this service depends on.
- `networks` (List[str]): The networks the container is connected to.
- `command` (List[str] | str): The command to run in the container.
- `labels` (Dict[str, str]): Labels to apply to the container. Used by some services.

In addition to the standard composition settings, Bouquet recognizes the following service-specific settings:

- `type`: The type of service to run. This is a required field.
- `queueserver`: 
  - device_file (str): Name of the device file in config/bluesky/devices. Default is "devices.yml".
  - redis_host (str): Hostname of the Redis server. Default is "redis".
  - host_ip (str): IP address used to access the service. Default is "127.0.0.1"
  - config_dir (str): The directory on the host to mount as /config in the container. Default is "".
- `queueserver_http_api`:
  - queueserver (str): Name of the queueserver service. Default is "queueserver".
  - host_ip (str): IP address used to access the service. Default is "127.0.0.1".
  - host_port (int): Port to expose the HTTP API. Default is 60610.
  - config_dir (str): The directory on the host to mount as /config in the container. Default is "".
- `queueserver_qtgui`:
  - title (str): Title of the QT GUI window. Default is "".
  - queueserver (str): Name of the queueserver service. Default is "queueserver".
  - host_port (str | int): Port to expose the QT GUI. Default is 60610.
- `bluesky_blissdata`:
  - redis (str): Name of the Redis service. Default is "redis".
  - host_ip (str): IP address used to access the service. Default is "127.0.0.1".
  - proxy (str): Hostname of the ZMQ server. Default is "127.0.0.1".
  - proxy_port (int): Port of the ZMQ server. Default is 5577.
  - redis_config_file (str): If set, the auto-generated redis service will use this file to configure the Redis server.
  - log_level (str): The log level for the service. Default is "". Possible values are "info" and "debug".
- `daiquiri_bluesky`:
  - redis (str): Name of the Redis service. Default is "redis".
  - mariadb (str): Name of the MariaDB service. Default is "mariadb".
  - queueserver_http_api (str): Name of the queueserver HTTP API service. Default is "queueserver_http_api".
  - host_ip (str): IP address used to access the service. Default is "127.0.0.1"
  - host_port (int): Port to expose the daiquiri service. Default is 8080.
  - config_dir (str): The directory on the host to the Daiquiri resources directory in the container.
                      Default is an empty string.
- `flint`:
  - redis (str): Name of the Redis service. Default is "redis".
  - redis_index (int): Index of the Redis database. Default is 0.
  - host_ip (str): IP address used to access the service. Default is "127.0.0.1".
- `redis`:
  - persist (bool): Flag to persist the Redis database. Default is True.
  - config_file (str): Path to the Redis configuration file on the host. Defaults to None.
- `mariadb`:
  - N/A
- `mongodb`:
  - N/A
- `jupyterhub`:
  - host_ip (str): IP address used to access the service. Default is "127.0.0.1"
  - host_port (int): Port to expose the JupyterHub service. Default is 8000.
  - config_dir (str): The directory on the host to mount config directories in the container. Default is "".
- `tiled`:
  - host_ip (str): IP address used to access the service. Default is "127.0.0.1".
  - host_port (int): Port to expose the Tiled service. Default is 8888.
  - config_dir (str): The directory on the host to mount as /config in the container. Default is "".
- `document_proxy`:
  - in_port (int): Input port for the Bluesky publisher.
  - out_port (int): Output port for the ZMQ subscriber.
  - host_ip (str): IP address used to access the service. Default is "127.0.0.1"
  - host_port (int): Port to expose the document proxy. Default is 5578.
- `callback_handler`:
  - host_ip (str): The host IP address where the service can be accessed. Default is the value of 
                   DEFAULT_HOST_IP_ADDRESS.
  - host_port (int): The port on which the service will be exposed. Default is 5579.
  - proxy (str): The proxy address for the service. Default is "localhost".
  - proxy_port (str | int): The proxy port for the service. Default is 5578.
  - service_port (str | int | None): The internal service port. Default is None.
  - debug (int | str): Debug mode setting. Default is "0".
  - config_dir (str): The directory on the host to mount as /config in the container.
  - config_file (str): The path to the configuration file. Default is "config.yml".

Generically, bouquet also supports `allow_traefik` and `apply_traefik_labels` to enable connections via Traefik and to apply labels respectively.

## Environment Variables

- `BEAMLINE_DIR`: Path to the host Bluesky directory.
- `BEAMLINE_CONFIG`: Path to the beamline configuration file.
- `COMPOSE_NAME`: Name of the compose file to generate (default: 'podman-compose.yml').
- `COMPOSE_PATH`: Path to the directory where the compose file will be generated. Defaults to the beamline directory.
- `HOST_IP_ADDRESS`: IP address to expose the services (default: '127.0.0.1').
- `USE_DOCKER`: Flag to use Docker instead of Podman (default: False).
- `GENERATE_COMPOSE_ONLY`: Flag to only generate the compose file without starting the services (default: False).
- `DEMO`: Flag to run the demo configuration (default: False).

## Command-Line Arguments

Command-line arguments passed to Bouquet will override environment variables.

- `-b`, `--beamline-dir`: Path to the host beamline directory.
- `-c`, `--beamline-config`: Path to the beamline configuration file.
- `-n`, `--compose-name`: Path to the compose file. Defaults to "./podman-compose.yml".
- `-p`, `--compose-path`: Path to the directory where the compose file will be generated.
- `-d`, `--demo`: Run the demo configuration.
- `-i`, `--host-ip-address`: IP Address to expose the services.
- `-u`, `--use-docker`: When true, uses Docker instead of Podman.
- `-g`, `--generate-compose-only`: Only generate the compose file and do not start the services.
- `-t`, `--apply-traefik-labels`: Apply predefined service labels to configure traefik.

## Usage

To use Bouquet, run the following command:

```sh
bouquet [options] /path/to/beamline_dir-or-config_file
```

## Documentation

### Building Documentation Locally

To build the documentation locally, follow these steps:

1. Install the required dependencies:
```sh
pip install sphinx sphinx-rtd-theme
```

2. Navigate to the docs directory:
```sh
cd docs
```

3. Build the HTML documentation:
```sh
make html
```

4. The built documentation will be available in the `docs/build/html` directory. You can open `index.html` in your browser to view it.

## Contributing

Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for information on how to contribute to this project.

## Releasing to PyPI

This project is configured to automatically publish to PyPI when a new version tag is pushed to the repository. The release process works as follows:

1. Update the version number in `pyproject.toml`
2. Commit the changes and push to the repository
3. Create and push a new tag with the format `vX.Y.Z` (e.g., `v0.3.1`)
4. The GitLab CI pipeline will automatically build and publish the package to PyPI

For the automatic publishing to work, a PyPI API token must be configured in the GitLab CI/CD settings as a protected variable named `PYPI_TOKEN`.