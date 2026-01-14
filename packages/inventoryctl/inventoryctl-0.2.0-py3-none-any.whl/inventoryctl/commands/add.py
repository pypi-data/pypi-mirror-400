import typer
from pathlib import Path
from typing import List, Optional
from inventoryctl.core.yaml_handler import YamlHandler
from inventoryctl.core.errors import UserError, ConflictError

app = typer.Typer(no_args_is_help=True)
yaml_handler = YamlHandler()

def parse_vars(vars_list: List[str]) -> dict:
    result = {}
    for v in vars_list:
        if "=" not in v:
            raise UserError(f"Invalid var format: {v}. Expected key=value")
        key, value = v.split("=", 1)
        result[key] = value
    return result

@app.command("host")
def add_host(
    name: str,
    inventory_file: Path,
    group_name: str = typer.Option(..., "--group", help="Group name"),
    ansible_host: str = typer.Option(..., "--ansible-host", help="Ansible host IP/DNS"),
    var: Optional[List[str]] = typer.Option(None, "--var", help="key=value variables"),
    source: Optional[str] = typer.Option(None, "--source", help="Source ID"),
    force: bool = typer.Option(False, "--force", help="Fail if exists unless force is used"), 
    upsert: bool = typer.Option(False, "--upsert", help="Update if exists"),
):
    """
    Add a host to the inventory.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.setdefault("inventory_groups", {})
    
    if group_name not in inventory_groups:
        raise UserError(f"Group '{group_name}' does not exist. Create it first.")
        
    group = inventory_groups[group_name]
    hosts = group.setdefault("hosts", {})
    
    if name in hosts:
        if not upsert and not force:
             raise ConflictError(f"Host '{name}' already exists in group '{group_name}'. Use --upsert to update or --force to overwrite.")
    
    host_data = {"ansible_host": ansible_host}
    if var:
        host_data.update(parse_vars(var))
        
    if source:
        host_data.setdefault("_meta", {})["source"] = source
        
    if name in hosts and upsert:
         existing = hosts[name]
         existing["ansible_host"] = ansible_host
         if var:
             existing.update(parse_vars(var))
         if source:
             if "_meta" not in existing: existing["_meta"] = {}
             existing["_meta"]["source"] = source
    else:
        hosts[name] = host_data

    yaml_handler.save(inventory_file, data)


@app.command("group")
def add_group(
    name: str,
    inventory_file: Path,
    var: Optional[List[str]] = typer.Option(None, "--var", help="key=value variables"),
):
    """
    Add a group to the inventory.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.setdefault("inventory_groups", {})
    
    if name in inventory_groups:
         raise ConflictError(f"Group '{name}' already exists.")
         
    group_data = {"hosts": {}}
    if var:
        group_data["vars"] = parse_vars(var)
        
    inventory_groups[name] = group_data
    yaml_handler.save(inventory_file, data)
