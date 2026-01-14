import typer
import sys
from inventoryctl.commands import (
    add,
    update,
    delete,
    get,
    list_cmd,
    sync,
    validate,
    render,
    format_cmd,
    batch,
)
from inventoryctl.core.errors import InventoryError, ExitCode

app = typer.Typer(no_args_is_help=True)

app.add_typer(add.app, name="add", help="Create resource")
app.add_typer(update.app, name="update", help="Update resource")
app.add_typer(delete.app, name="delete", help="Delete resource")
app.add_typer(get.app, name="get", help="Fetch resource")
app.add_typer(list_cmd.app, name="list", help="List resources")
app.add_typer(sync.app, name="sync", help="Reconcile desired state")
app.add_typer(batch.app, name="batch", help="Batch operations from JSON")
app.command(name="validate")(validate.validate)
app.add_typer(render.app, name="render", help="Generate derived artifacts")
app.command(name="format")(format_cmd.format_inventory)


def main():
    try:
        app()
    except InventoryError as e:
        typer.echo(f"Error: {e.message}", err=True)
        sys.exit(e.exit_code)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        sys.exit(ExitCode.INTERNAL_ERROR)


if __name__ == "__main__":
    main()
