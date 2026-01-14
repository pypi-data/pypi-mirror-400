import typer
import json
from pathlib import Path
from typing import List, Dict, Any
from ruamel.yaml import YAML
from inventoryctl.core.yaml_handler import YamlHandler
from inventoryctl.core.errors import UserError

app = typer.Typer(no_args_is_help=True)
yaml_handler = YamlHandler()

def load_input(input_file: Path) -> List[Dict[str, Any]]:
    if not input_file.exists():
        raise UserError(f"Input file '{input_file}' not found.")
        
    with open(input_file, 'r') as f:
        if input_file.suffix == '.json':
            return json.load(f)
        elif input_file.suffix in ['.yaml', '.yml']:
            yaml = YAML(typ='safe')
            return yaml.load(f) or []
        else:
            # Try parsing as JSON first, then YAML
            content = f.read()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                yaml = YAML(typ='safe')
                return yaml.load(content) or []

@app.command("hosts")
def sync_hosts(
    inventory_file: Path,
    group_name: str = typer.Option(..., "--group", help="Target group"),
    source: str = typer.Option(..., "--source", help="Source ID"),
    input_file: Path = typer.Option(..., "--input", help="Input file (JSON/YAML)"),
    prune: bool = typer.Option(False, "--prune", help="Delete hosts not in input"),
):
    """
    Sync hosts from an external source.
    """
    input_hosts = load_input(input_file)
    if not isinstance(input_hosts, list):
         raise UserError("Input must be a list of host objects.")
         
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.setdefault("inventory_groups", {})
    
    # Ensure group exists
    if group_name not in inventory_groups:
        inventory_groups[group_name] = {"hosts": {}}
        
    group_data = inventory_groups[group_name]
    hosts = group_data.setdefault("hosts", {})
    
    # Set of host names in input
    input_host_names = set()
    
    for h in input_hosts:
        name = h.get("name")
        if not name:
            continue # Skip invalid input
        input_host_names.add(name)
        
        # Prepare host data
        # "Create/update hosts in input"
        # Input format example: {"name": "...", "ansible_host": "...", "vars": {...}}
        
        host_payload = {}
        if "ansible_host" in h:
            host_payload["ansible_host"] = h["ansible_host"]
        
        # Merge vars into the host object directly as per YAML structure
        if "vars" in h and isinstance(h["vars"], dict):
            host_payload.update(h["vars"])
            
        # Add source meta
        host_payload.setdefault("_meta", {})["source"] = source
        
        # Update or Create
        if name in hosts:
             # Update existing
             # We should preserve fields NOT in input?
             # Spec says "Create/update hosts in input".
             # Usually sync implies making it match the input for the managed fields.
             # But if we have manual vars?
             # "Delete hosts in group+source not in input" implies we own the "group+source" namespace.
             # So for hosts from this source, we should probably overwrite.
             # But we should respect existing structure if possible (comments etc).
             
             existing = hosts[name]
             existing.update(host_payload) # Shallow merge
             # Ensure _meta source is set (it is in payload)
        else:
             hosts[name] = host_payload
             
    if prune:
        # Delete hosts in group+source not in input
        to_delete = []
        for h_name, h_data in hosts.items():
            h_source = h_data.get("_meta", {}).get("source")
            if h_source == source and h_name not in input_host_names:
                to_delete.append(h_name)
                
        for h_name in to_delete:
            del hosts[h_name]
            
    yaml_handler.save(inventory_file, data)
