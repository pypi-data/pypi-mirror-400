"""
    lager.commands.utility.install

    Install lager-mono box code onto a new box
"""
import click
import subprocess
import ipaddress
from pathlib import Path
from ...box_storage import add_box, get_box_ip, get_box_user


def get_script_path(script_name: str) -> tuple[Path, bool]:
    """Get path to deployment script and whether running from repo.

    Returns:
        tuple[Path, bool]: (script_path, is_from_repo)

    Tries two locations:
    1. Packaged deployment scripts (when installed from PyPI)
    2. Repository deployment scripts (when running from cloned repo)
    """
    # Try packaged deployment scripts first (PyPI installation)
    # From cli/commands/utility/install.py:
    # - parent = cli/commands/utility/
    # - parent.parent = cli/commands/
    # - parent.parent.parent = cli/
    cli_root = Path(__file__).parent.parent.parent
    packaged_script = cli_root / "deployment" / "scripts" / script_name

    if packaged_script.exists():
        return packaged_script, False

    # Fall back to repo location (development/repo installation)
    # - parent.parent.parent.parent = <repo root>
    repo_root = cli_root.parent
    repo_script = repo_root / "deployment" / "scripts" / script_name

    if repo_script.exists():
        return repo_script, True

    # Neither location exists
    return packaged_script, False


@click.command()
@click.pass_context
@click.option("--ip", help="Target box IP address")
@click.option("--box", help="Target box name from .lager config")
@click.option("--user", default="lagerdata", help="SSH username (default: lagerdata)")
@click.option("--branch", default="main", help="Git branch to deploy (default: main)")
@click.option("--rsync", is_flag=True, help="Use rsync mode (faster, but disables 'lager update')")
@click.option("--skip-jlink", is_flag=True, help="Skip J-Link installation")
@click.option("--skip-firewall", is_flag=True, help="Skip UFW firewall configuration")
@click.option("--skip-verify", is_flag=True, help="Skip post-deployment verification")
@click.option("--corporate-vpn", default=None, help="Corporate VPN interface name (e.g., tun0)")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts")
def install(ctx, ip, box, user, branch, rsync, skip_jlink, skip_firewall, skip_verify, corporate_vpn, yes):
    """
    Install lager-mono box code onto a new box.

    This command deploys the lager-mono box code to any IP address
    (local network, Tailscale, or other VPN). By default uses git sparse
    checkout to minimize disk usage and enable 'lager update' for future
    updates (requires GitHub deploy key). Use --rsync for simpler deployment
    without git.

    Examples:
        lager install --ip <BOX_IP>
        lager install --box my-box
        lager install --ip <BOX_IP> --rsync  # Use rsync if no deploy key
        lager install --box my-box --branch staging
        lager install --ip <BOX_IP> --user pi --yes
    """
    # 1. Resolve box name to IP if --box provided
    if not ip and not box:
        click.secho("Error: Either --ip or --box must be specified", fg='red', err=True)
        ctx.exit(1)

    if ip and box:
        click.secho("Error: Cannot specify both --ip and --box", fg='red', err=True)
        ctx.exit(1)

    if box:
        # Resolve box name to IP
        resolved_ip = get_box_ip(box)
        if not resolved_ip:
            click.secho(f"Error: Box '{box}' not found in .lager config", fg='red', err=True)
            click.echo("Run 'lager boxes list' to see available boxes")
            ctx.exit(1)

        ip = resolved_ip

        # Use configured user if not explicitly provided
        if user == "lagerdata":  # Default value
            configured_user = get_box_user(box)
            if configured_user:
                user = configured_user

    # 2. Validate IP address
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        click.secho(f"Error: '{ip}' is not a valid IP address", fg='red', err=True)
        ctx.exit(1)

    # 2. Verify deploy script exists and check if running from repo
    deploy_script, is_from_repo = get_script_path("setup_and_deploy_box.sh")

    if not deploy_script.exists():
        click.secho(f"Error: Deployment script not found", fg='red', err=True, bold=True)
        click.echo()
        click.echo("This should not happen. Please report this issue at:")
        click.echo("https://github.com/lagerdata/lager-mono/issues")
        click.echo()
        ctx.exit(1)

    # 3. Check if rsync mode is allowed (only from repo)
    if rsync and not is_from_repo:
        click.secho(f"Error: --rsync mode requires the lager-mono repository", fg='red', err=True, bold=True)
        click.echo()
        click.echo("When installed from PyPI, only sparse checkout mode is supported.")
        click.echo("Sparse checkout clones directly from GitHub to the box.")
        click.echo()
        click.secho("Options:", fg='cyan')
        click.echo("  1. Remove --rsync flag to use sparse checkout (recommended)")
        click.echo("  2. Clone the repository to use rsync mode:")
        click.echo("     git clone https://github.com/lagerdata/lager-mono.git")
        click.echo(f"     cd lager-mono")
        if box:
            click.echo(f"     lager install --box {box} --rsync")
        else:
            click.echo(f"     lager install --ip {ip} --rsync")
        click.echo()
        ctx.exit(1)

    # 4. Display summary and confirm
    click.echo()
    click.secho(f"Installing lager-mono to {ip}...", fg='cyan', bold=True)
    click.echo(f"  Branch: {branch}")
    click.echo(f"  User: {user}")
    if rsync:
        click.echo(f"  Mode: rsync (fast, but 'lager update' disabled)")
    else:
        click.echo(f"  Mode: Git sparse checkout (enables 'lager update')")
    if skip_jlink:
        click.echo(f"  Skip J-Link: Yes")
    if skip_firewall:
        click.echo(f"  Skip Firewall: Yes")
    if corporate_vpn:
        click.echo(f"  Corporate VPN: {corporate_vpn}")
    click.echo()

    if not yes:
        if not click.confirm("Proceed with installation?", default=True):
            click.echo("Installation cancelled.")
            ctx.exit(0)

    click.echo()

    # 5. Run setup_and_deploy_box.sh
    click.secho("Running box deployment...", fg='cyan')
    click.echo("This may take several minutes.\n")

    deploy_args = [str(deploy_script), ip, "--user", user, "--skip-add-box"]

    # Add sparse checkout flag if not using rsync
    if not rsync:
        deploy_args.extend(["--sparse", "--branch", branch])

    if skip_jlink:
        deploy_args.append("--skip-jlink")
    if skip_firewall:
        deploy_args.append("--skip-firewall")
    if skip_verify:
        deploy_args.append("--skip-verify")
    if corporate_vpn:
        deploy_args.extend(["--corporate-vpn", corporate_vpn])

    try:
        # Run the deploy script, streaming output to the terminal
        result = subprocess.run(
            deploy_args,
            check=False,
            timeout=1800,  # 30 minute timeout
        )

        if result.returncode != 0:
            click.echo()
            click.secho("Deployment failed!", fg='red', err=True)
            click.secho("Check the output above for details.", fg='yellow', err=True)
            ctx.exit(1)

    except subprocess.TimeoutExpired:
        click.secho("Error: Deployment timed out after 30 minutes", fg='red', err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"Error running deployment: {e}", fg='red', err=True)
        ctx.exit(1)

    click.echo()
    click.secho("Box deployment complete!", fg='green', bold=True)

    # Display mode-specific next steps
    if rsync:
        click.echo()
        click.secho("Note: 'lager update' is not available in rsync mode.", fg='yellow')
        click.echo("To enable updates, you'll need to:")
        click.echo("  1. Set up a GitHub deploy key (see deployment/README.md)")
        click.echo("  2. Redeploy using: lager install --ip {} (without --rsync)".format(ip))
    click.echo()

    # 6. Prompt to add box to .lager config
    if not yes:
        if click.confirm("Add this box to your configuration?", default=True):
            box_name = click.prompt("Box name", type=str)
            if box_name and box_name.strip():
                add_box(box_name.strip(), ip, user=user, version=branch)
                click.secho(f"Added '{box_name}' -> {ip} to .lager config", fg='green')
                click.echo()
                click.secho(f"You can now use: lager hello --box {box_name}", fg='cyan')
            else:
                click.secho("Skipped adding box to config (empty name)", fg='yellow')

    click.echo()
    click.secho("Installation complete!", fg='green', bold=True)
