import typer
import json
import sys
from pathlib import Path
from typing import Optional
from inventoryctl.core.yaml_handler import YamlHandler
from inventoryctl.core.errors import InventoryError, UserError

app = typer.Typer(no_args_is_help=True)
yaml_handler = YamlHandler()


def parse_vars(vars_dict: dict) -> dict:
    """Parse variables from a dictionary."""
    return vars_dict if vars_dict else {}


def process_host_operation(
    action: str, host_config: dict, inventory_file: Path
) -> tuple[bool, str]:
    """
    Process a single host operation.

    Returns: (success: bool, message: str)
    """
    try:
        # Extract common fields
        hostname = host_config.get("hostname")
        if not hostname:
            return False, "Missing required field: hostname"

        ansible_host = host_config.get("ansible_host")
        ansible_user = host_config.get("ansible_user")
        ansible_port = host_config.get("ansible_port", 22)
        groups = host_config.get("groups", [])
        variables = host_config.get("vars", {})
        source = host_config.get("source")
        upsert = host_config.get("upsert", False)
        force = host_config.get("force", False)

        # Load inventory
        data = yaml_handler.load(inventory_file)
        inventory_groups = data.setdefault("inventory_groups", {})

        if action == "add":
            # Add operation
            if not groups:
                return False, f"Missing required field 'groups' for host: {hostname}"
            if not ansible_host:
                return (
                    False,
                    f"Missing required field 'ansible_host' for host: {hostname}",
                )

            # Process each group
            for group_name in groups:
                if group_name not in inventory_groups:
                    # Auto-create group if it doesn't exist
                    inventory_groups[group_name] = {"hosts": {}}

                group = inventory_groups[group_name]
                hosts = group.setdefault("hosts", {})

                # Check if host exists
                if hostname in hosts:
                    if not upsert and not force:
                        return (
                            False,
                            f"Host '{hostname}' already exists in group '{group_name}'",
                        )

                # Build host data
                host_data = {"ansible_host": ansible_host}

                # Add optional ansible variables
                if ansible_user:
                    host_data["ansible_user"] = ansible_user
                if ansible_port and ansible_port != 22:
                    host_data["ansible_port"] = ansible_port

                # Add custom variables
                if variables:
                    host_data.update(parse_vars(variables))

                # Add source metadata
                if source:
                    host_data.setdefault("_meta", {})["source"] = source

                # Update or add host
                if hostname in hosts and upsert:
                    existing = hosts[hostname]
                    existing.update(host_data)
                else:
                    hosts[hostname] = host_data

            yaml_handler.save(inventory_file, data)
            return True, f"Added/updated host: {hostname}"

        elif action == "update":
            # Update operation
            if not groups:
                return False, f"Missing required field 'groups' for host: {hostname}"

            updated = False
            for group_name in groups:
                if group_name not in inventory_groups:
                    continue

                group = inventory_groups[group_name]
                hosts = group.get("hosts", {})

                if hostname in hosts:
                    host_data = hosts[hostname]

                    # Update ansible_host if provided
                    if ansible_host:
                        host_data["ansible_host"] = ansible_host

                    # Update optional ansible variables
                    if ansible_user:
                        host_data["ansible_user"] = ansible_user
                    if ansible_port and ansible_port != 22:
                        host_data["ansible_port"] = ansible_port

                    # Update custom variables
                    if variables:
                        host_data.update(parse_vars(variables))

                    # Update source metadata
                    if source:
                        host_data.setdefault("_meta", {})["source"] = source

                    updated = True

            if not updated:
                return False, f"Host '{hostname}' not found in any specified groups"

            yaml_handler.save(inventory_file, data)
            return True, f"Updated host: {hostname}"

        elif action == "delete":
            # Delete operation
            deleted = False

            if groups:
                # Delete from specific groups
                for group_name in groups:
                    if group_name in inventory_groups:
                        group = inventory_groups[group_name]
                        hosts = group.get("hosts", {})
                        if hostname in hosts:
                            del hosts[hostname]
                            deleted = True
            else:
                # Delete from all groups
                for group_name, group in inventory_groups.items():
                    hosts = group.get("hosts", {})
                    if hostname in hosts:
                        del hosts[hostname]
                        deleted = True

            if not deleted:
                return False, f"Host '{hostname}' not found"

            yaml_handler.save(inventory_file, data)
            return True, f"Deleted host: {hostname}"

        else:
            return False, f"Unsupported action: {action}"

    except InventoryError as e:
        return False, f"Inventory error: {e.message}"
    except Exception as e:
        return False, f"Error: {str(e)}"


@app.command("host")
def batch_host(
    action: str,
    inventory_file: Path,
    json_file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="JSON file with batch data"
    ),
    continue_on_error: bool = typer.Option(
        True, "--continue-on-error", help="Continue processing after errors"
    ),
):
    """
    Perform batch operations on hosts using JSON input.

    JSON format (from file or stdin):
    [
      {
        "hostname": "web-01",
        "ansible_host": "10.0.0.1",
        "ansible_user": "ubuntu",
        "ansible_port": 22,
        "groups": ["webservers", "production"],
        "vars": {
          "custom_var": "value"
        },
        "source": "api",
        "upsert": true,
        "force": false
      }
    ]

    Actions:
    - add: Create new hosts (or update if upsert=true)
    - update: Update existing hosts
    - delete: Remove hosts (groups optional for deletion)
    """
    # Read JSON input
    try:
        if json_file:
            with open(json_file, "r") as f:
                batch_data = json.load(f)
        else:
            # Read from stdin
            batch_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        raise UserError(f"Invalid JSON input: {e}")
    except Exception as e:
        raise UserError(f"Error reading input: {e}")

    if not isinstance(batch_data, list):
        raise UserError("JSON input must be an array of host configurations")

    # Process each host
    total = len(batch_data)
    success_count = 0
    failed_items = []

    typer.echo(f"🔄 Processing {total} host operations ({action})...")

    for idx, host_config in enumerate(batch_data, 1):
        if not isinstance(host_config, dict):
            typer.echo(
                f"  [{idx}/{total}] ⚠️  Skipped: Invalid configuration (not a dict)",
                err=True,
            )
            failed_items.append({"index": idx, "reason": "Invalid configuration"})
            continue

        hostname = host_config.get("hostname", f"item-{idx}")
        success, message = process_host_operation(action, host_config, inventory_file)

        if success:
            typer.echo(f"  [{idx}/{total}] ✅ {hostname}: {message}")
            success_count += 1
        else:
            typer.echo(f"  [{idx}/{total}] ❌ {hostname}: {message}", err=True)
            failed_items.append({"hostname": hostname, "index": idx, "reason": message})

            if not continue_on_error:
                typer.echo(
                    f"\n🚨 Aborting due to error (use --continue-on-error to keep processing)",
                    err=True,
                )
                raise typer.Exit(code=1)

    # Summary
    failed_count = len(failed_items)
    typer.echo("")
    typer.echo("📊 Batch Summary:")
    typer.echo(f"   Total: {total}")
    typer.echo(f"   Success: {success_count}")
    typer.echo(f"   Failed: {failed_count}")

    if failed_items:
        typer.echo("")
        typer.echo("Failed items:")
        for item in failed_items:
            hostname = item.get("hostname", f"item-{item['index']}")
            typer.echo(f"  - {hostname}: {item['reason']}")

        if success_count == 0:
            typer.echo("\n❌ All operations failed")
            raise typer.Exit(code=1)
        else:
            typer.echo("\n⚠️  Partial success - some operations failed")
            raise typer.Exit(code=2)
    else:
        typer.echo("\n✅ All operations completed successfully")


@app.command("group")
def batch_group(
    action: str,
    inventory_file: Path,
    json_file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="JSON file with batch data"
    ),
    continue_on_error: bool = typer.Option(
        True, "--continue-on-error", help="Continue processing after errors"
    ),
):
    """
    Perform batch operations on groups using JSON input.

    JSON format (from file or stdin):
    [
      {
        "name": "webservers",
        "vars": {
          "http_port": 80,
          "app_env": "production"
        }
      }
    ]

    Actions:
    - add: Create new groups
    - update: Update existing groups
    - delete: Remove groups
    """
    # Read JSON input
    try:
        if json_file:
            with open(json_file, "r") as f:
                batch_data = json.load(f)
        else:
            # Read from stdin
            batch_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        raise UserError(f"Invalid JSON input: {e}")
    except Exception as e:
        raise UserError(f"Error reading input: {e}")

    if not isinstance(batch_data, list):
        raise UserError("JSON input must be an array of group configurations")

    # Process each group
    total = len(batch_data)
    success_count = 0
    failed_items = []

    typer.echo(f"🔄 Processing {total} group operations ({action})...")

    data = yaml_handler.load(inventory_file)
    inventory_groups = data.setdefault("inventory_groups", {})

    for idx, group_config in enumerate(batch_data, 1):
        if not isinstance(group_config, dict):
            typer.echo(
                f"  [{idx}/{total}] ⚠️  Skipped: Invalid configuration (not a dict)",
                err=True,
            )
            failed_items.append({"index": idx, "reason": "Invalid configuration"})
            continue

        group_name = group_config.get("name", f"item-{idx}")
        variables = group_config.get("vars", {})

        try:
            if action == "add":
                if group_name in inventory_groups:
                    typer.echo(
                        f"  [{idx}/{total}] ⚠️  {group_name}: Already exists", err=True
                    )
                    failed_items.append(
                        {"name": group_name, "index": idx, "reason": "Already exists"}
                    )
                    continue

                group_data = {"hosts": {}}
                if variables:
                    group_data["vars"] = parse_vars(variables)

                inventory_groups[group_name] = group_data
                typer.echo(f"  [{idx}/{total}] ✅ {group_name}: Created")
                success_count += 1

            elif action == "update":
                if group_name not in inventory_groups:
                    typer.echo(
                        f"  [{idx}/{total}] ❌ {group_name}: Not found", err=True
                    )
                    failed_items.append(
                        {"name": group_name, "index": idx, "reason": "Not found"}
                    )
                    continue

                if variables:
                    inventory_groups[group_name]["vars"] = parse_vars(variables)

                typer.echo(f"  [{idx}/{total}] ✅ {group_name}: Updated")
                success_count += 1

            elif action == "delete":
                if group_name not in inventory_groups:
                    typer.echo(
                        f"  [{idx}/{total}] ❌ {group_name}: Not found", err=True
                    )
                    failed_items.append(
                        {"name": group_name, "index": idx, "reason": "Not found"}
                    )
                    continue

                del inventory_groups[group_name]
                typer.echo(f"  [{idx}/{total}] ✅ {group_name}: Deleted")
                success_count += 1

            else:
                typer.echo(
                    f"  [{idx}/{total}] ❌ {group_name}: Unsupported action '{action}'",
                    err=True,
                )
                failed_items.append(
                    {
                        "name": group_name,
                        "index": idx,
                        "reason": f"Unsupported action: {action}",
                    }
                )

        except Exception as e:
            typer.echo(f"  [{idx}/{total}] ❌ {group_name}: {str(e)}", err=True)
            failed_items.append({"name": group_name, "index": idx, "reason": str(e)})

            if not continue_on_error:
                typer.echo(
                    f"\n🚨 Aborting due to error (use --continue-on-error to keep processing)",
                    err=True,
                )
                raise typer.Exit(code=1)

    # Save changes if any succeeded
    if success_count > 0:
        yaml_handler.save(inventory_file, data)

    # Summary
    failed_count = len(failed_items)
    typer.echo("")
    typer.echo("📊 Batch Summary:")
    typer.echo(f"   Total: {total}")
    typer.echo(f"   Success: {success_count}")
    typer.echo(f"   Failed: {failed_count}")

    if failed_items:
        typer.echo("")
        typer.echo("Failed items:")
        for item in failed_items:
            group_name = item.get("name", f"item-{item['index']}")
            typer.echo(f"  - {group_name}: {item['reason']}")

        if success_count == 0:
            typer.echo("\n❌ All operations failed")
            raise typer.Exit(code=1)
        else:
            typer.echo("\n⚠️  Partial success - some operations failed")
            raise typer.Exit(code=2)
    else:
        typer.echo("\n✅ All operations completed successfully")
