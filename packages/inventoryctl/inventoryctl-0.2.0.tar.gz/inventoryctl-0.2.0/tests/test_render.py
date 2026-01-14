from pathlib import Path
from inventoryctl.commands.render import render_ssh


def test_render_ssh_parses_identity_and_localforward(tmp_path, capsys):
    yaml_file = tmp_path / "inv.yaml"
    yaml_file.write_text(
        """
inventory_groups:
  mygroup:
    vars:
      ansible_user: u
      ansible_ssh_common_args: "-o ProxyJump=gw.example"
    hosts:
      myhost:
        ansible_host: 1.2.3.4
        ansible_ssh_private_key_file: ~/.ssh/id_rsa
        ssh_local_forwards:
          - "9000 127.0.0.1:9000"
"""
    )

    render_ssh(yaml_file)
    captured = capsys.readouterr()

    assert "Host myhost" in captured.out
    assert "HostName 1.2.3.4" in captured.out
    assert "IdentityFile ~/.ssh/id_rsa" in captured.out
    assert "ProxyJump gw.example" in captured.out
    assert "LocalForward 9000 127.0.0.1:9000" in captured.out


def test_render_ssh_uses_group_common_args_for_proxyjump(tmp_path, capsys):
    yaml_file = tmp_path / "inv2.yaml"
    yaml_file.write_text(
        """
inventory_groups:
  groupa:
    vars:
      ansible_ssh_common_args: "-o ProxyJump=group-gw"
    hosts:
      hosta:
        ansible_host: hosta.example
"""
    )

    render_ssh(yaml_file)
    captured = capsys.readouterr()

    assert "Host hosta" in captured.out
    assert "HostName hosta.example" in captured.out
    assert "ProxyJump group-gw" in captured.out
