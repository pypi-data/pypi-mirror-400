from typing import Annotated

import json
import typer
from opensearchpy import RequestError
from rich.console import Console

from opensearchcli.commands import cluster_settings
from opensearchcli.commands.exceptions import catch_exception

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Manage OpenSearch cluster operations",
)
app.add_typer(cluster_settings.app, name="settings", help="Manage cluster settings")
console = Console()


@app.command()
def info(
    ctx: typer.Context,
):
    """Retrieve cluster information."""
    info = ctx.obj.opensearch.info()
    typer.echo(json.dumps(info, indent=2))


@app.command()
def health(
    ctx: typer.Context,
):
    """Check the health of the OpenSearch cluster."""
    health = ctx.obj.opensearch.cluster.health()
    typer.echo(json.dumps(health, indent=2))


@app.command()
@catch_exception(RequestError, exit_code=1)
def allocation_explain(
    ctx: typer.Context,
    index: Annotated[
        str, typer.Argument(help="The name of the index to explain allocation for")
    ] = None,
):
    """Explain shard allocation for a specific index."""
    if index:
        explanation = ctx.obj.opensearch.cluster.allocation_explain(index=index)
    else:
        explanation = ctx.obj.opensearch.cluster.allocation_explain()

    typer.echo(json.dumps(explanation, indent=2))


@app.command()
def pending_tasks(
    ctx: typer.Context,
):
    """List pending tasks in the OpenSearch cluster."""
    tasks = ctx.obj.opensearch.cluster.pending_tasks()
    typer.echo(json.dumps(tasks, indent=2))


@app.command()
def stats(ctx: typer.Context):
    """Retrieve cluster statistics."""
    stats = ctx.obj.opensearch.cluster.stats()
    typer.echo(json.dumps(stats, indent=2))
