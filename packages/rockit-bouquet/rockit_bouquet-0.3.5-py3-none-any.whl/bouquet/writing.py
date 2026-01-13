from .models import ComposeConfig


from pydantic import BaseModel
import yaml


from typing import Any, List


class QuotedString(str):
    pass


def quoted_presenter(dumper, data):
    if any(
        char in data
        for char in [
            ":",
            "{",
            "}",
            "[",
            "]",
            ",",
            "&",
            "*",
            "#",
            "?",
            "|",
            "<",
            ">",
            "=",
            "!",
            "%",
            "@",
            "\\",
        ]
    ):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


class ComposeDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(ComposeDumper, self).increase_indent(flow, False)


yaml.add_representer(QuotedString, quoted_presenter)
yaml.add_representer(str, quoted_presenter)


def write_compose_file(
    compose_config: ComposeConfig,
    filename: str = "podman-compose.yml",
    header: List[str] | None = None,
) -> None:
    """
    Generate a podman-compose.yml file from the ComposeConfig object.

    Parameters
    ----------
    compose_config : ComposeConfig
        The ComposeConfig object containing the configuration.
    filename : str, optional
        The name of the file to write the compose configuration to (default is "podman-compose.yml").
    header : list, optional
        A list of strings representing the header lines to be written at the top of the file.
    """
    with open(filename, "w") as f:
        if header:
            for line in header:
                f.write(f"{line}\n")
            f.write("\n")  # Add a blank line after the header

        yaml_str = yaml.dump(
            compose_config.model_dump(exclude_unset=True),
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            Dumper=ComposeDumper,
        )
        f.write(yaml_str)


def print_to_yaml(dat: Any) -> None:
    """
    Print an object to a YAML string.

    Parameters
    ----------
    dat : Any
        The object to print to YAML.

    """
    yaml_str = yaml.dump(
        dat.model_dump(exclude_unset=True) if issubclass(type(dat), BaseModel) else dat,
        default_flow_style=False,
        sort_keys=False,
        indent=2,
        Dumper=ComposeDumper,
    )
    print(yaml_str)
