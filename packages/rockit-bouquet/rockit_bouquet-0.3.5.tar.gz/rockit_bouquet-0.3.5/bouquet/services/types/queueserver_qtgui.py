from typing import Any
from pydantic import Field
from ...models import ServiceConfig
from ...defaults import get_default


class QueueserverQtGUIServiceConfig(ServiceConfig):
    """
    Configuration for Queueserver Qt GUI service.

    This class defines the configuration for the Queueserver Qt GUI service, which runs the Qt GUI for the Bluesky
    queueserver. It initializes the service with default values for container name, image, networks, volumes, command,
    and environment variables.

    Depends_on: queueserver

    Attributes:
        container_name (str): The name of the container. Default is "queueserver_qtgui".
        image (str): The Docker image to use for the service. Default is the image defined in ALLOWED_SERVICE_TYPES.
        networks (list): The networks the container is connected to. Default is ["internal"].
        volumes (list): The volumes to mount. Default is ["/tmp/.X11-unix:/tmp/.X11-unix", "batches:/opt/batches"].
        command (str): The command to run in the container. Default is "bluesky-qtgui --zmq localhost:5578" or
            "bluesky-qtgui --zmq localhost:5578 --title <title>" if title is provided.
        depends_on (list): The services this service depends on. Default is ["queueserver"].
        environment (dict): The environment variables for the container. Default includes "BATCH_SAVE_DIR" and
            "QSERVER_ZMQ_CONTROL_ADDRESS".
        title (str): The title of the Qt GUI window. Default is "".
        queueserver (str): The Queueserver service name. Default is "queueserver".

    Methods:
        __init__(config: Dict[str, Any], **kwargs): Initializes the configuration with the provided settings and
            default values.
    """

    title: str = Field(default="Title")
    queueserver: str = Field(default="queueserver")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._service_type = "queueserver_qtgui"
        if not self.container_name:
            self.container_name = "queueserver_qtgui"
        if not self.image:
            self.image = get_default("ALLOWED_SERVICE_TYPES")["queueserver_qtgui"]
        if not self.networks:
            self.networks = ["internal"]
        if not self.volumes:
            self.volumes = ["/tmp/.X11-unix:/tmp/.X11-unix", "batches:/opt/batches"]
        if not self.command:
            self.command = f'bluesky-emil-gui --zmq localhost:5578 --title "{self.title}"'

        if not self.depends_on:
            self.depends_on = [self.queueserver]

        default_environment = {
            "BATCH_SAVE_DIR": "/opt/batches",
            "QSERVER_ZMQ_CONTROL_ADDRESS": f"tcp://{self.queueserver}:60615",
            "QSERVER_ZMQ_INFO_ADDRESS": f"tcp://{self.queueserver}:60625",
            "DISPLAY": "${DISPLAY}",
        }

        if isinstance(self.environment, dict):
            default_environment.update(self.environment)
        self.environment = default_environment

    class Config:
        extra = "forbid"
