import typer
from pathlib import Path
from inventoryctl.core.yaml_handler import YamlHandler

def format_inventory(
    inventory_file: Path,
):
    """
    Format the inventory file (canonicalize).
    """
    yaml_handler = YamlHandler()
    data = yaml_handler.load(inventory_file)
    
    # Logic to sort keys?
    # For now, just loading and saving with ruamel might normalize some things,
    # but to enforce sort order (e.g. hosts alphabetically), we'd need to manipulate the data.
    
    inventory_groups = data.get("inventory_groups", {})
    
    # Sort groups
    # ruamel.yaml CommentedMap preserves order. We can reconstruct it.
    # Note: This might lose comments if not careful, but ruamel is good at it 
    # if we just move items in the existing CommentedMap.
    # But creating a new dict sorts it but loses comments attached to keys?
    # Safe way: simple load/save ensures consistent indentation/formatting.
    # To sort:
    
    # Let's just save for now, which ensures the YAML settings from YamlHandler are applied.
    yaml_handler.save(inventory_file, data)
    typer.echo(f"Formatted {inventory_file}")
