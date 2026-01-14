import typer
import sys
from pathlib import Path
from typing import Optional
from ruamel.yaml import YAML
from inventoryctl.core.yaml_handler import YamlHandler

app = typer.Typer(no_args_is_help=True)
yaml_handler = YamlHandler()

@app.command("hosts")
def list_hosts(
    inventory_file: Path,
    group_name: Optional[str] = typer.Option(None, "--group", help="Group name"),
    source: Optional[str] = typer.Option(None, "--source", help="Source ID"),
):
    """
    List hosts in the inventory.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.get("inventory_groups", {})
    
    result = []
    
    groups_to_check = []
    if group_name:
        if group_name in inventory_groups:
            groups_to_check.append(group_name)
    else:
        groups_to_check = list(inventory_groups.keys())
        
    for g_name in groups_to_check:
        g_data = inventory_groups[g_name]
        hosts = g_data.get("hosts", {})
        for h_name, h_data in hosts.items():
            if source:
                if h_data.get("_meta", {}).get("source") != source:
                    continue
            
            # What to output? Just names? Or full objects?
            # "List resources". Usually a list of names or summary.
            # Example doesn't specify output format details, but "List Hosts" usually implies names.
            # However, for machine parsing, maybe YAML list of objects?
            # Let's output a YAML list of host names for now, or maybe a simple list.
            # "inventoryctl list hosts ... inventory.yaml"
            # If I look at kubectl get pods, it lists them.
            # But "YAML in -> YAML out".
            # Let's output a list of strings (hostnames) in YAML format.
            result.append(h_name)
            
    yaml = YAML()
    yaml.dump(result, sys.stdout)
