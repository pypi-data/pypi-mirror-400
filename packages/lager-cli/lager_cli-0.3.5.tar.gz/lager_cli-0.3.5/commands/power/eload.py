"""
Electronic load CLI commands.

Usage:
    lager eload                     -> lists electronic load nets
    lager eload <NETNAME> cc 0.5    -> set constant current to 0.5A
    lager eload <NETNAME> cv 12.0   -> set constant voltage to 12V
    lager eload <NETNAME> cr 100    -> set constant resistance to 100 ohms
    lager eload <NETNAME> cp 10     -> set constant power to 10W
    lager eload <NETNAME> state     -> display electronic load state
"""
from __future__ import annotations

import click

# Import consolidated helpers from cli.core.net_helpers
from ...core.net_helpers import (
    require_netname,
    resolve_box,
    display_nets,
    run_impl_script,
    NET_ROLES,
)
from ...context import get_default_net


ELOAD_ROLE = NET_ROLES["eload"]  # "eload"


# ---------- CLI ----------

@click.group(invoke_without_command=True)
@click.argument('netname', required=False)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.pass_context
def eload(ctx, netname, box):
    """Control electronic load settings and modes"""
    # Use provided netname, or fall back to default if not provided
    if netname is None:
        netname = get_default_net(ctx, 'eload')

    if netname is not None:
        ctx.obj.netname = netname

    # If no subcommand and no netname, list nets
    if ctx.invoked_subcommand is None:
        resolved_box = resolve_box(ctx, box)
        display_nets(ctx, resolved_box, None, ELOAD_ROLE, "electronic load")


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.pass_context
def cc(ctx, value, box):
    """Set (or read) constant current mode in amps (A)"""
    resolved_box = resolve_box(ctx, box)
    netname = require_netname(ctx, "eload")
    args = ["cc", netname]
    if value is not None:
        args.append(str(value))
    run_impl_script(ctx, resolved_box, 'eload.py', args=tuple(args))


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.pass_context
def cv(ctx, value, box):
    """Set (or read) constant voltage mode in volts (V)"""
    resolved_box = resolve_box(ctx, box)
    netname = require_netname(ctx, "eload")
    args = ["cv", netname]
    if value is not None:
        args.append(str(value))
    run_impl_script(ctx, resolved_box, 'eload.py', args=tuple(args))


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.pass_context
def cr(ctx, value, box):
    """Set (or read) constant resistance mode in ohms"""
    resolved_box = resolve_box(ctx, box)
    netname = require_netname(ctx, "eload")
    args = ["cr", netname]
    if value is not None:
        args.append(str(value))
    run_impl_script(ctx, resolved_box, 'eload.py', args=tuple(args))


@eload.command()
@click.argument('value', required=False, type=float)
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.pass_context
def cp(ctx, value, box):
    """Set (or read) constant power mode in watts (W)"""
    resolved_box = resolve_box(ctx, box)
    netname = require_netname(ctx, "eload")
    args = ["cp", netname]
    if value is not None:
        args.append(str(value))
    run_impl_script(ctx, resolved_box, 'eload.py', args=tuple(args))


@eload.command()
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.pass_context
def state(ctx, box):
    """Display electronic load state"""
    resolved_box = resolve_box(ctx, box)
    netname = require_netname(ctx, "eload")
    args = ["state", netname]
    run_impl_script(ctx, resolved_box, 'eload.py', args=tuple(args))
