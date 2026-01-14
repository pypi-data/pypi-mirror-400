"""
GPO (GPIO Output) command for setting digital output states.

This module provides the `lager gpo` command for setting GPIO output level
on LabJack devices.
"""
from __future__ import annotations

import json
import os

import click

from ...context import get_default_net
from ...core.net_helpers import (
    resolve_box,
    list_nets_by_role,
    display_nets_table,
    run_impl_script,
)


GPIO_ROLE = "gpio"


@click.command(name="gpo", help="Set GPIO output level (0/1, low/high, off/on, toggle)")
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.argument("netname", required=False)
@click.argument("level", required=False,
                type=click.Choice(["low", "high", "on", "off", "0", "1", "toggle"], case_sensitive=False))
def gpo(ctx, box, netname, level):
    """Set the output level of a GPIO output net.

    Level can be: low, high, on, off, 0, 1, or toggle.
    If no netname is provided, lists available GPIO nets.
    """
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'gpio')

    box_ip = resolve_box(ctx, box)

    # If still no netname, list available GPIO nets
    if netname is None:
        nets = list_nets_by_role(ctx, box_ip, GPIO_ROLE)
        display_nets_table(nets, empty_message="No GPIO nets found on this box.")
        return

    # If we have a net but no level, show error
    if level is None:
        raise click.UsageError(
            "LEVEL required.\n\n"
            "Usage: lager gpo <NET_NAME> <LEVEL>\n"
            "Example: lager gpo gpio1 high --box mybox"
        )

    box_image = os.environ.get("LAGER_GATEWAY_IMAGE", "python")
    payload = json.dumps({"netname": netname, "action": "output", "level": level})

    run_impl_script(
        ctx=ctx,
        box=box_ip,
        impl_script="gpio.py",
        args=(payload,),
        image=box_image,
        timeout=None,
    )
