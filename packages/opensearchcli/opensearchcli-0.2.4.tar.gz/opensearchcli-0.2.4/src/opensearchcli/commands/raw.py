import json
import typer
from rich.console import Console

from opensearchcli.commands.helpers import body_dict_from_flags, parse_params

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Make raw API calls to OpenSearch cluster",
)
console = Console()


@app.command()
def do(
    ctx: typer.Context,
    method: str = typer.Argument("GET", help="HTTP method to use"),
    endpoint: str = typer.Argument(help="API endpoint to call"),
    body: list[str] = typer.Option(default_factory=dict, help="Request body for POST/PUT requests"),
    params: list[str] = typer.Option(default_factory=dict, help="Query parameters for the request"),
):
    """Make a raw API call to the OpenSearch cluster."""
    opensearch = ctx.obj.opensearch

    payload = body_dict_from_flags(body)
    query_params = parse_params(params)

    response = opensearch.transport.perform_request(
        method,
        endpoint,
        body=payload if body else None,
        params=query_params if params else None,
    )
    if ctx.meta.get("json_output"):
        typer.echo(json.dumps(response, indent=2))
    else:
        console.print(response)
