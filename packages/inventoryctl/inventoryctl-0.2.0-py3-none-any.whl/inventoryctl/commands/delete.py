import typer
from pathlib import Path
from typing import Optional
from inventoryctl.core.yaml_handler import YamlHandler
from inventoryctl.core.errors import UserError

app = typer.Typer(no_args_is_help=True)
yaml_handler = YamlHandler()

@app.command("host")
def delete_host(
    host_name: str,
    inventory_file: Path,
    group_name: Optional[str] = typer.Option(None, "--group", help="Group name"),
    source: Optional[str] = typer.Option(None, "--source", help="Source ID"),
):
    """
    Delete a host from the inventory.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.get("inventory_groups", {})
    
    # Logic similar to update: find host, then delete.
    # Idempotent: if not found, succeed.
    
    groups_to_check = []
    if group_name:
        if group_name in inventory_groups:
            groups_to_check.append(group_name)
    else:
        groups_to_check = list(inventory_groups.keys())
        
    deleted = False
    for g_name in groups_to_check:
        g_data = inventory_groups[g_name]
        hosts = g_data.get("hosts", {})
        if host_name in hosts:
            host_data = hosts[host_name]
            # Check source constraint
            if source:
                host_source = host_data.get("_meta", {}).get("source")
                if host_source != source:
                    continue # Skip if source doesn't match
            
            del hosts[host_name]
            deleted = True
            
    # If group was specified and we didn't delete (and didn't find because of source mismatch or just missing), 
    # for idempotency we just return success.
    
    yaml_handler.save(inventory_file, data)

@app.command("group")
def delete_group(
    group_name: str,
    inventory_file: Path,
):
    """
    Delete a group from the inventory.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.get("inventory_groups", {})
    
    if group_name in inventory_groups:
        del inventory_groups[group_name]
        
    yaml_handler.save(inventory_file, data)
