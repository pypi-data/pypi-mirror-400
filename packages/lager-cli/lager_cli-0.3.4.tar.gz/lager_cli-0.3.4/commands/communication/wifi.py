"""
    lager.wifi.commands

    Commands for controlling WiFi - Updated for direct SSH execution

    Migrated to cli/commands/communication/ and refactored to use
    consolidated helpers from cli.core.net_helpers.
"""
from __future__ import annotations

import json

import click
from texttable import Texttable

# Import consolidated helpers from cli.core.net_helpers
from ...core.net_helpers import resolve_box, run_impl_script


def _run_wifi_command(ctx: click.Context, box_ip: str, args_dict: dict) -> None:
    """Run WiFi impl script with JSON arguments."""
    run_impl_script(
        ctx,
        box_ip,
        "wifi.py",
        args=(json.dumps(args_dict),),
    )


@click.group(name='wifi', hidden=True)
def _wifi():
    """
        Lager wifi commands
    """
    pass


@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
def status(ctx, box):
    """
        Get the current WiFi Status of the box
    """
    box_ip = resolve_box(ctx, box)

    status_args = {
        'action': 'status'
    }

    _run_wifi_command(ctx, box_ip, status_args)


@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--interface', required=False, help='Wireless interface to use', default='wlan0')
def access_points(ctx, box, interface='wlan0'):
    """
        Get WiFi access points visible to the box
    """
    box_ip = resolve_box(ctx, box)

    scan_args = {
        'action': 'scan',
        'interface': interface
    }

    _run_wifi_command(ctx, box_ip, scan_args)


@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--ssid', required=True, help='SSID of the network to connect to')
@click.option('--interface', help='Wireless interface to use', default='wlan0', show_default=True)
@click.option('--password', required=False, help='Password of the network to connect to', default='')
def connect(ctx, box, ssid, interface, password=''):
    """
        Connect the box to a new network
    """
    box_ip = resolve_box(ctx, box)

    connect_args = {
        'action': 'connect',
        'ssid': ssid,
        'password': password,
        'interface': interface
    }

    _run_wifi_command(ctx, box_ip, connect_args)


@_wifi.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Confirm the action without prompting')
@click.argument('SSID', required=True)
def delete_connection(ctx, box, yes, ssid):
    """
        Delete the specified network from the box
    """
    if not yes and not click.confirm('An ethernet connection will be required to bring the box back online. Proceed?', default=False):
        click.echo("Aborting")
        return

    box_ip = resolve_box(ctx, box)

    delete_args = {
        'action': 'delete',
        'ssid': ssid,
        'connection_name': ssid
    }

    _run_wifi_command(ctx, box_ip, delete_args)
