import os
from typing import Annotated

import typer
from pathlib import Path
from opensearchpy import OpenSearch
from rich.console import Console
from opensearchcli.commands import cluster, config, snapshot, commands, raw, index
import urllib3

urllib3.disable_warnings()

console = Console()
app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
app.add_typer(typer_instance=commands.app, name="commands")
app.add_typer(
    typer_instance=cluster.app, name="cluster", help="OpenSearch cluster API commands"
)
app.add_typer(
    typer_instance=index.app, name="index", help="OpenSearch index API commands"
)
app.add_typer(
    typer_instance=snapshot.app,
    name="snapshot",
    help="OpenSearch snapshot API commands",
)
app.add_typer(typer_instance=raw.app, name="raw", help="Make raw OpenSearch API calls")
app.add_typer(
    typer_instance=config.app, name="config", help="Manage configuration profiles"
)


@app.command(name="version")
def version():
    """
    Show version info
    """
    import importlib.metadata
    import tomlkit
    from importlib.metadata import PackageNotFoundError

    try:
        # packaged run
        version = importlib.metadata.version("opensearchcli")
        console.print(f"Version: {version}")
    except PackageNotFoundError:
        # local run
        pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
        with pyproject.open() as f:
            toml = tomlkit.load(f)
            version = toml["project"]["version"]
            console.print(f"Version: {version}")


class OpenSearchCli:
    def __init__(
        self,
        config: config.Config,
        profile: config.ConfigProfile,
        config_file_path: str,
        json_output: bool = False,
    ) -> None:
        self._opensearch: OpenSearch | None = None
        self.config = config
        self.profile = profile
        self.config_file_path = config_file_path
        self.json_output = json_output

    @property
    def opensearch(self) -> OpenSearch:
        if self._opensearch is None:
            self._opensearch = OpenSearch(
                hosts=[
                    {
                        "host": self.profile.domain,
                        "port": self.profile.port,
                    }
                ],
                http_auth=(self.profile.username, self.profile.password),
                use_ssl=True,
                verify_certs=False,
                ssl_show_warn=False,
                headers={"Accept": "application/json"} if self.json_output else {},
            )
        return self._opensearch


@app.callback()
def common(
    ctx: typer.Context,
    config_file: Annotated[str, typer.Option()] = os.path.expanduser(
        path=f"{Path.home()}/.config/opensearch-cli/config.toml"
    ),
    profile: Annotated[
        str, typer.Option(help="OpenSearch profile name", envvar="OPENSEARCH_PROFILE")
    ] = "default",
    json_output: Annotated[bool, typer.Option("--json", help="Output results as JSON")]=False,
) -> None:
    """OpenSearch CLI - Manage your OpenSearch clusters."""

    try:
        _config = config.read_config(config_file=config_file)
        _profile = _config.find_profile_by_name(profile_name=profile)
    except Exception as ex:
        console.log(f"Error while reading config {config_file}:", ex, style="red")
        exit(1)

    ctx.obj = OpenSearchCli(
        config=_config,
        profile=_profile,
        config_file_path=config_file,
        json_output=json_output,
    )
    ctx.meta["json_output"] = json_output


if __name__ == "__main__":
    app()
