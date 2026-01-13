import rich_click as click
from flyte.cli import _common as common
from rich.panel import Panel

from flyteplugins.union.remote import ApiKey


@click.command("api-key")
@click.option("--name", type=str, help="Name for API key", required=True)
@click.pass_obj
def create_api_key(cfg: common.CLIConfig, name: str):
    """
    Create an API key for headless authentication.

    This creates OAuth application credentials that can be used to authenticate
    with Union without interactive login. The generated API key should be set
    as the FLYTE_API_KEY environment variable. Oauth applications should not be
    confused with Union Apps, which are a different construct entirely.

    Examples:

        # Create an API key named "ci-pipeline"
        $ flyte create api-key --name ci-pipeline

        # The output will include an export command like:
        # export FLYTE_API_KEY="<base64-encoded-credentials>"
    """
    # Api keys (aka oauth apps) are not scoped to project/domain.
    cfg.init(project="", domain="")

    try:
        api_key = ApiKey.create(name=name)

        console = common.get_console()

        # Create formatted output with panel
        output = (
            f"[green bold]Client ID:[/green bold] {api_key.client_id}\n\n"
            f"[yellow bold]⚠️  The following API key will only be shown once. Be sure to keep it safe![/yellow bold]\n\n"
            f"Configure your headless CLI by setting the following environment variable:\n\n"
            f'[cyan]export FLYTE_API_KEY="{api_key.encoded_credentials}"[/cyan]'
        )

        console.print(
            Panel.fit(
                output,
                title="[bold]API Key Created Successfully[/bold]",
                border_style="green",
            )
        )

    except Exception as e:
        raise click.ClickException(f"Unable to create api-key with name: {name}\n{e}") from e


@click.command("api-key")
@click.argument("client-id", type=str, required=False)
@click.option("--limit", type=int, default=100, help="Maximum number of keys to list")
@click.pass_obj
def get_api_key(cfg: common.CLIConfig, client_id: str | None, limit: int):
    """
    Get or list API keys.

    If CLIENT-ID is provided, gets a specific API key.
    Otherwise, lists all API keys.

    Examples:

        # List all API keys
        $ flyte get api-key

        # List with a limit
        $ flyte get api-key --limit 10

        # Get a specific API key
        $ flyte get api-key my-client-id
    """
    # Api keys (aka oauth apps) are not scoped to project/domain.
    cfg.init(project="", domain="")

    console = common.get_console()

    try:
        if client_id:
            # Get specific key
            key = ApiKey.get(client_id=client_id)
            console.print(common.format(f"API Key {client_id}", [key], "json"))
        else:
            # List all keys
            keys = list(ApiKey.listall(limit=limit))
            if not keys:
                console.print("[yellow]No API keys found.[/yellow]")
                return

            console.print(common.format("API Keys", keys, cfg.output_format))

    except Exception as e:
        raise click.ClickException(f"Unable to get api-key(s): {e}") from e


@click.command("api-key")
@click.argument("client-id", type=str)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_obj
def delete_api_key(cfg: common.CLIConfig, client_id: str, yes: bool):
    """
    Delete an API key.

    Examples:

        # Delete an API key (with confirmation)
        $ flyte delete api-key my-client-id

        # Delete without confirmation
        $ flyte delete api-key my-client-id --yes
    """
    # Api keys (aka oauth apps) are not scoped to project/domain.
    cfg.init(project="", domain="")

    console = common.get_console()

    if not yes:
        click.confirm(f"Are you sure you want to delete API key '{client_id}'?", abort=True)

    try:
        ApiKey.delete(client_id=client_id)
        console.print(f"[green]✓[/green] Successfully deleted API key: [cyan]{client_id}[/cyan]")

    except Exception as e:
        raise click.ClickException(f"Unable to delete api-key: {e}") from e
