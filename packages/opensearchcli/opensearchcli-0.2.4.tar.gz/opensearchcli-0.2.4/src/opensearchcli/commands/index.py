import json
import typer
from rich.console import Console

from opensearchcli.commands import index_settings

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Manage OpenSearch index operations",
)
app.add_typer(index_settings.app, name="settings", help="Manage index settings")
console = Console()


@app.command()
def list(
    ctx: typer.Context,
    index_pattern: str = typer.Argument(
        ..., help="Index name or pattern to list indices"
    ),
):
    """List indices matching the given pattern."""
    indices = ctx.obj.opensearch.indices.get(index=index_pattern)
    typer.echo(json.dumps(list(indices.keys()), indent=2))


@app.command()
def get(
    ctx: typer.Context,
    index: str = typer.Argument(
        help="The name of the index to retrieve information for"
    ),
):
    """Retrieve information for a specific index."""
    index_info = ctx.obj.opensearch.indices.get(index=index)
    typer.echo(json.dumps(index_info, indent=2))


@app.command()
def ism(
    ctx: typer.Context,
    index: str = typer.Argument(
        help="The name of the index to retrieve the ISM policy information for"
    ),
):
    """Retrieve ISM information for a specific index."""
    index_info = ctx.obj.opensearch.plugins.index_management.explain_index(index=index)
    typer.echo(json.dumps(index_info, indent=2))


@app.command()
def ism_reset(
    ctx: typer.Context,
    index: str = typer.Argument(help="The name of the index to reset the policy on"),
    policy: str = typer.Argument(
        help="The name of the policy", default="mdr4all_policy"
    ),
):
    """Reset ism policy on a specific index."""
    res = ctx.obj.opensearch.plugins.index_management.remove_policy_from_index(
        index=index
    )
    console.print("Remove old policies:")
    console.print(res)
    body = {"policy_id": policy}
    res = ctx.obj.opensearch.plugins.index_management.add_policy(index=index, body=body)
    console.print(f"Set new policy '{policy}':")
    console.print(res)


@app.command()
def ism_unmanaged(
    ctx: typer.Context,
    index: str = typer.Argument(help="Search for unmanaged indices", default=".ds-*"),
):
    """List indexes with no ism policy."""
    res = ctx.obj.opensearch.plugins.index_management.explain_index(index=index)

    unmanaged_indexes = [
        index
        for index, details in res.items()
        if index != "total_managed_indices"
        and details.get("index.plugins.index_state_management.policy_id") is None
    ]
    if unmanaged_indexes:
        console.print(f"Found {len(unmanaged_indexes)} unmanaged indexes.")
        for index in unmanaged_indexes:
            console.print(f"Unmanaged index: {index}")
    else:
        console.print("All policies are being managed ok.")


@app.command()
def ism_failed(
    ctx: typer.Context,
    index: str = typer.Argument(
        help="Search for indices with failed ISM status", default=".ds-*"
    ),
):
    """List indexes with failed ism policy status."""
    res = ctx.obj.opensearch.plugins.index_management.explain_index(index=index)
    failed_indexes = [
        index
        for index, details in res.items()
        if index != "total_managed_indices"
        and details.get("enabled") is False
        and details.get("action", {}).get("failed") is True
    ]
    if failed_indexes:
        console.print(
            f"Found {len(failed_indexes)} indexes have failed during policy management."
        )
        for index in failed_indexes:
            console.print(f"Failed index: {index}")
    else:
        console.print("All indices are in a good state for policy management.")
