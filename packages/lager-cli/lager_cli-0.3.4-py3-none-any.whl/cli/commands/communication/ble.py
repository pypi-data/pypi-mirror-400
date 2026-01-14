"""
    lager.ble.commands

    Commands for BLE - Updated for direct SSH execution

    Migrated to cli/commands/communication/ and refactored to use
    consolidated helpers from cli.core.net_helpers.
"""
from __future__ import annotations

import re
import json

import click
from texttable import Texttable

# Import consolidated helpers from cli.core.net_helpers
from ...core.net_helpers import resolve_box, run_impl_script
from ...context import get_impl_path


@click.group(name='ble')
def ble():
    """
        Scan and connect to Bluetooth Low Energy devices
    """
    pass


ADDRESS_NAME_RE = re.compile(r'\A([0-9A-F]{2}-){5}[0-9A-F]{2}\Z')


def check_name(device):
    return 0 if ADDRESS_NAME_RE.search(device['name']) else 1


def normalize_device(device):
    (address, data) = device
    item = {'address': address}
    manufacturer_data = data.get('manufacturer_data', {})
    for (k, v) in manufacturer_data.items():
        manufacturer_data[k] = bytes(v) if isinstance(v, list) else v
    item.update(data)
    return item


def _run_ble_command(ctx: click.Context, box_ip: str, args_dict: dict) -> None:
    """Run BLE impl script with JSON arguments."""
    run_impl_script(
        ctx,
        box_ip,
        "ble.py",
        args=(json.dumps(args_dict),),
    )


@ble.command('scan')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--timeout', required=False, help='Total time box will spend scanning for devices', default=5.0, type=click.FLOAT, show_default=True)
@click.option('--name-contains', required=False, help='Filter devices to those whose name contains this string')
@click.option('--name-exact', required=False, help='Filter devices to those whose name matches this string')
@click.option('--verbose', required=False, is_flag=True, default=False, help='Verbose output (includes UUIDs)')
def scan(ctx, box, timeout, name_contains, name_exact, verbose):
    """
        Scan for BLE devices
    """
    box_ip = resolve_box(ctx, box)

    scan_args = {
        'action': 'scan',
        'timeout': timeout,
        'name_contains': name_contains,
        'name_exact': name_exact,
        'verbose': verbose
    }

    _run_ble_command(ctx, box_ip, scan_args)


@ble.command('info')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.argument('address', required=True)
def info(ctx, box, address):
    """
        Get BLE device information
    """
    box_ip = resolve_box(ctx, box)

    info_args = {
        'action': 'info',
        'address': address
    }

    _run_ble_command(ctx, box_ip, info_args)


@ble.command('connect')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.argument('address', required=True)
def connect(ctx, box, address):
    """
        Connect to a BLE device
    """
    box_ip = resolve_box(ctx, box)

    connect_args = {
        'action': 'connect',
        'address': address
    }

    _run_ble_command(ctx, box_ip, connect_args)


@ble.command('disconnect')
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.argument('address', required=True)
def disconnect(ctx, box, address):
    """
        Disconnect from a BLE device
    """
    box_ip = resolve_box(ctx, box)

    disconnect_args = {
        'action': 'disconnect',
        'address': address
    }

    _run_ble_command(ctx, box_ip, disconnect_args)
