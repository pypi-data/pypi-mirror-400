import typer
import json
from rich.console import Console

from opensearchcli.commands.helpers import body_dict_from_flags, parse_params

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Manage OpenSearch index settings",
)
console = Console()


@app.command()
def get(
    ctx: typer.Context,
    index: str = typer.Argument(help="The name of the index to retrieve settings for"),
    params: list[str] = typer.Option(
        default_factory=list, help="Settings parameters to retrieve"
    ),
):
    """Retrieve settings for a specific index."""
    _params = parse_params(params)
    settings = ctx.obj.opensearch.indices.get_settings(index=index, params=_params)
    typer.echo(json.dumps(settings, indent=2))


@app.command()
def set(
    ctx: typer.Context,
    index: str = typer.Argument(help="The name of the index to update settings for"),
    settings: list[str] = typer.Argument(
        help="Settings to update in the format key=value"
    ),
):
    """Update settings for a specific index."""
    payload = body_dict_from_flags(settings)
    response = ctx.obj.opensearch.indices.put_settings(index=index, body=payload)
    typer.echo(json.dumps(response, indent=2))
