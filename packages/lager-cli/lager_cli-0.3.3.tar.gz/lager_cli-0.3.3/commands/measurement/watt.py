"""
Watt meter commands for power measurement.
"""
from __future__ import annotations

import json
import os

import click
from ...context import get_default_net, get_impl_path
from ..development.python import run_python_internal
from ...core.net_helpers import (
    resolve_box,
    display_nets,
)

WATT_ROLE = "watt-meter"


@click.command(name="watt", help="Read power from watt meter net (returns watts)")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.argument("netname", required=False)
def watt(ctx, box, netname):
    """
    Read power consumption from a watt meter net.
    Returns power measurement in watts (W).

    Example:
        lager watt my_power_net
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'watt')

    box_ip = resolve_box(ctx, box)

    # If still no netname, list available watt meter nets
    if netname is None:
        display_nets(ctx, box_ip, None, WATT_ROLE, "watt meter")
        return

    # Strip whitespace from netname for better UX
    netname = netname.strip()

    box_image = os.environ.get("LAGER_GATEWAY_IMAGE", "python")

    payload = json.dumps({"netname": netname})

    run_python_internal(
        ctx=ctx,
        runnable=get_impl_path("watt.py"),
        box=box_ip,
        image=box_image,
        env=(),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum="SIGTERM",
        timeout=None,
        detach=False,
        port=(),
        org=None,
        args=[payload],
    )
