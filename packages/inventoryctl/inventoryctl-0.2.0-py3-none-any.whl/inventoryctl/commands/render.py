import typer
import sys
import re
import os
from pathlib import Path
from inventoryctl.core.yaml_handler import YamlHandler
from inventoryctl.core.errors import UserError
from ruamel.yaml import YAML

app = typer.Typer(no_args_is_help=True)
yaml_handler = YamlHandler()


@app.command("ansible")
def render_ansible(
    inventory_file: Path,
):
    """
    Render Ansible inventory.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.get("inventory_groups", {})

    # Structure for Ansible:
    # all:
    #   children:
    #     group1: ...
    #     group2: ...

    # The spec's "Inventory YAML Contract" seems to map `inventory_groups` directly to Ansible groups.
    # But usually Ansible YAML inventory has `all` at top or keys are groups.
    # "inventory_groups" key in the source file is a wrapper for this tool.
    # To render ansible, we essentially strip that wrapper and maybe format it.

    output = {}
    for g_name, g_data in inventory_groups.items():
        output[g_name] = g_data
        # Filter out _meta from hosts?
        # Spec: "_meta reserved namespace. Everything else is passed through to Ansible".
        # So we should strip _meta from the rendered output.

        if "hosts" in output[g_name]:
            # Deep copy to avoid modifying original if we were caching,
            # but here we loaded fresh.
            hosts = output[g_name]["hosts"]
            for h_name, h_data in hosts.items():
                if "_meta" in h_data:
                    del h_data["_meta"]

    yaml = YAML()
    yaml.dump(output, sys.stdout)


@app.command("ssh")
def render_ssh(
    inventory_file: Path,
):
    """
    Render SSH config.
    """
    data = yaml_handler.load(inventory_file)
    inventory_groups = data.get("inventory_groups", {})

    for g_name, g_data in inventory_groups.items():
        group_vars = g_data.get("vars", {})
        hosts = g_data.get("hosts", {})

        for h_name, h_data in hosts.items():
            # Merge group vars and host vars (host wins)
            # We are looking for: ansible_host, ansible_user, ansible_ssh_common_args (ProxyJump), ansible_ssh_private_key_file, ssh_local_forwards

            # Effective config
            host_val = h_data.get("ansible_host")
            user_val = h_data.get("ansible_user", group_vars.get("ansible_user"))
            common_args = h_data.get(
                "ansible_ssh_common_args", group_vars.get("ansible_ssh_common_args")
            )
            identity_file = h_data.get(
                "ansible_ssh_private_key_file",
                group_vars.get("ansible_ssh_private_key_file"),
            )
            local_forwards = h_data.get(
                "ssh_local_forwards", group_vars.get("ssh_local_forwards")
            )

            if not host_val:
                continue

            print(f"Host {h_name}")
            print(f"  HostName {host_val}")
            if user_val:
                print(f"  User {user_val}")

            # IdentityFile (do not expand ~, use as-provided)
            if identity_file:
                print(f"  IdentityFile {identity_file}")

            # Parse ProxyJump out of ansible_ssh_common_args robustly (support quoted values)
            if common_args:
                # Look for ProxyJump=("value"|'value'|value)
                m = re.search(
                    r'ProxyJump=(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))', common_args
                )
                if m:
                    jump = m.group(1) or m.group(2) or m.group(3)
                    if jump:
                        print(f"  ProxyJump {jump}")

            # Local forwards
            if local_forwards:
                if isinstance(local_forwards, list):
                    for f in local_forwards:
                        print(f"  LocalForward {f}")
                elif isinstance(local_forwards, str):
                    print(f"  LocalForward {local_forwards}")

            print("")
