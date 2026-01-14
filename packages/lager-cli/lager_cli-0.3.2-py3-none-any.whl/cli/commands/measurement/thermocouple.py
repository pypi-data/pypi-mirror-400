"""
Thermocouple commands for temperature measurement.
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

THERMOCOUPLE_ROLE = "thermocouple"


@click.command(name="thermocouple", help="Read thermocouple temperature in degrees Celsius (°C)")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.argument("netname", required=False)
def thermocouple(ctx, box, netname):
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'thermocouple')

    box_ip = resolve_box(ctx, box)

    # If still no netname, list available thermocouple nets
    if netname is None:
        display_nets(ctx, box_ip, None, THERMOCOUPLE_ROLE, "thermocouple")
        return

    # Strip whitespace from netname for better UX
    netname = netname.strip()

    box_image = os.environ.get("LAGER_GATEWAY_IMAGE", "python")

    payload = json.dumps({"netname": netname})

    run_python_internal(
        ctx=ctx,
        runnable=get_impl_path("thermocouple.py"),
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
