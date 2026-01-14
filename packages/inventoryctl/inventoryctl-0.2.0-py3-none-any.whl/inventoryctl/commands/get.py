import typer
import json
import sys
from pathlib import Path
from ruamel.yaml import YAML
from inventoryctl.core.yaml_handler import YamlHandler
from inventoryctl.core.errors import UserError

app = typer.Typer(no_args_is_help=True)
yaml_handler = YamlHandler()

@app.command("host")
def get_host(
    host_name: str,
    inventory_file: Path,
):
    """
    Get a host from the inventory.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.get("inventory_groups", {})
    
    found_host = None
    
    for g_name, g_data in inventory_groups.items():
        if host_name in g_data.get("hosts", {}):
            found_host = g_data["hosts"][host_name]
            # We might want to include the group name in the output?
            # Spec says "Outputs YAML or JSON". 
            # If we just output the host data, it's a dict.
            break
            
    if found_host is None:
        raise UserError(f"Host '{host_name}' not found.")
        
    # Default to YAML output as per design goals (YAML in -> YAML out)
    # But strictly, the tool could have an output format option.
    # Spec: "Outputs YAML or JSON".
    # I'll default to YAML.
    
    yaml = YAML()
    yaml.dump(found_host, sys.stdout)
