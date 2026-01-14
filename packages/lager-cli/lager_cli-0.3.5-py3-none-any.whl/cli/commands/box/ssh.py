"""
    lager.commands.box.ssh

    SSH into boxes
"""
import click
import subprocess
import sys
from ...box_storage import resolve_and_validate_box
from ...context import get_default_box


@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
def ssh(ctx, box):
    """
        SSH into a box
    """
    from ...box_storage import get_box_user

    # Use default box if none specified
    if not box:
        box = get_default_box(ctx)

    # Resolve and validate the box (handles both names and IPs)
    resolved_box = resolve_and_validate_box(ctx, box)

    # Get username from box storage (defaults to 'lagerdata' if not found)
    username = get_box_user(box) or 'lagerdata'

    # Build SSH command
    ssh_host = f'{username}@{resolved_box}'

    try:
        # Use subprocess to execute SSH interactively
        # We use os.execvp to replace the current process with SSH
        # This allows full interactivity (shell, etc.)
        import os
        os.execvp('ssh', ['ssh', ssh_host])
    except FileNotFoundError:
        click.secho('Error: SSH client not found. Please ensure SSH is installed.', fg='red', err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f'Error connecting to {ssh_host}: {str(e)}', fg='red', err=True)
        ctx.exit(1)
