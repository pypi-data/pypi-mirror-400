import typer
from pathlib import Path
from typing import List, Optional
from inventoryctl.core.yaml_handler import YamlHandler
from inventoryctl.core.errors import UserError

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
def update_host(
    host_name: str, # Positional argument for host name? Spec: inventoryctl update host <hostname> ... inventory.yaml
    inventory_file: Path,
    group_name: Optional[str] = typer.Option(None, "--group", help="Group name"),
    ansible_host: Optional[str] = typer.Option(None, "--ansible-host", help="Ansible host IP/DNS"),
    var: Optional[List[str]] = typer.Option(None, "--var", help="key=value variables"),
    unset_var: Optional[List[str]] = typer.Option(None, "--unset-var", help="Variables to remove"),
):
    """
    Update a host in the inventory.
    """
    # Spec: inventoryctl update host <hostname> ... inventory.yaml
    # host_name is first positional arg.
    # inventory_file is second positional arg (after options).
    
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.get("inventory_groups", {})
    
    # Find the host. Host names are unique within a group, but globally?
    # Spec "Inventory YAML Contract" shows hosts nested under groups.
    # So a host is identified by Group + Name.
    # But the update command has `--group` as *optional*?
    # "inventoryctl update host <hostname> [--group <group>]"
    # If group is not provided, do we search for it?
    # "Host must exist".
    # If group is provided, we check that group.
    # If not, we scan all groups? 
    # Let's assume we scan if not provided, or fail if ambiguous.
    
    target_group_name = None
    target_host_data = None
    
    if group_name:
        if group_name in inventory_groups:
            if host_name in inventory_groups[group_name].get("hosts", {}):
                target_group_name = group_name
                target_host_data = inventory_groups[group_name]["hosts"][host_name]
    else:
        found = []
        for g_name, g_data in inventory_groups.items():
            if host_name in g_data.get("hosts", {}):
                found.append(g_name)
        
        if len(found) == 1:
            target_group_name = found[0]
            target_host_data = inventory_groups[target_group_name]["hosts"][host_name]
        elif len(found) > 1:
            raise UserError(f"Host '{host_name}' found in multiple groups: {found}. Please specify --group.")
            
    if target_host_data is None:
        raise UserError(f"Host '{host_name}' not found.")
        
    # Apply updates
    if ansible_host:
        target_host_data["ansible_host"] = ansible_host
        
    if var:
        target_host_data.update(parse_vars(var))
        
    if unset_var:
        for k in unset_var:
            target_host_data.pop(k, None)
            
    # If group is specified and different, move the host?
    # Spec says "[--group <group>]". Usually means "in this group".
    # But if I want to *move* a host? 
    # "Only provided fields change".
    # If I say `update host foo --group bar`, does it move foo to bar?
    # Or does it just mean "find foo in group bar and update it"?
    # Given the ambiguity and "No implicit deletes", I'll assume it helps identify the host or modify properties.
    # But a host doesn't have a "group" property in the YAML. The structure *is* the group.
    # So changing group means moving.
    # Let's stick to identifying for now. If moving is needed, usually it's delete + add or a specific move command.
    # Or maybe `update host <hostname> --group <new_group>` moves it?
    # Let's assume for now it's for identification.
    
    yaml_handler.save(inventory_file, data)


@app.command("group")
def update_group(
    group_name: str,
    inventory_file: Path,
    var: Optional[List[str]] = typer.Option(None, "--var", help="key=value variables"),
    unset_var: Optional[List[str]] = typer.Option(None, "--unset-var", help="Variables to remove"),
):
    """
    Update a group in the inventory.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.get("inventory_groups", {})
    
    if group_name not in inventory_groups:
        raise UserError(f"Group '{group_name}' not found.")
        
    group_data = inventory_groups[group_name]
    vars_data = group_data.setdefault("vars", {})
    
    if var:
        vars_data.update(parse_vars(var))
        
    if unset_var:
        for k in unset_var:
            vars_data.pop(k, None)
            
    yaml_handler.save(inventory_file, data)
