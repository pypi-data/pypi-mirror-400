"""
    lager.commands.utility.install

    Install lager-mono box code onto a new box
"""
import click
import subprocess
import ipaddress
import tempfile
import shutil
from pathlib import Path
from importlib import resources
from ...box_storage import add_box, get_box_ip, get_box_user


def get_script_path(script_name: str, subdir: str = "scripts") -> Path:
    """Get path to deployment script from package resources.

    This function finds deployment scripts that are packaged with the CLI,
    allowing `lager install` to work from pip-installed versions.

    Args:
        script_name: Name of the script file (e.g., "setup_and_deploy_box.sh")
        subdir: Subdirectory within deployment ("scripts" or "security")

    Returns:
        Path to the script file
    """
    if subdir == "scripts":
        package = "cli.deployment.scripts"
    elif subdir == "security":
        package = "cli.deployment.security"
    else:
        raise ValueError(f"Unknown subdir: {subdir}")

    # Try importlib.resources first (works for pip-installed package)
    try:
        script_files = resources.files(package)
        script_traversable = script_files.joinpath(script_name)

        # For regular directory installs, we can get the path directly
        # by converting the Traversable to a string and checking if it exists
        potential_path = Path(str(script_traversable))
        if potential_path.exists():
            return potential_path

        # For zip/wheel imports, extract to temp directory
        temp_dir = Path(tempfile.gettempdir()) / "lager_deployment" / subdir
        temp_dir.mkdir(parents=True, exist_ok=True)
        dest = temp_dir / script_name

        # Read content and write to temp file
        content = script_traversable.read_bytes()
        dest.write_bytes(content)
        dest.chmod(0o755)  # Make executable
        return dest

    except (ModuleNotFoundError, FileNotFoundError, TypeError, AttributeError):
        pass

    # Fallback: try repo-relative path for development
    repo_root = Path(__file__).parent.parent.parent.parent
    repo_path = repo_root / "deployment" / subdir / script_name
    if repo_path.exists():
        return repo_path

    # Final fallback: check if scripts are in cli/deployment (dev mode)
    cli_root = Path(__file__).parent.parent.parent
    dev_path = cli_root / "deployment" / subdir / script_name
    if dev_path.exists():
        return dev_path

    raise FileNotFoundError(f"Deployment script not found: {script_name}")


@click.command()
@click.pass_context
@click.option("--box", default=None, help="Box name (uses stored IP and username)")
@click.option("--ip", default=None, help="Target box IP address")
@click.option("--user", default=None, help="SSH username (default: lagerdata, or stored username if using --box)")
@click.option("--branch", default="main", help="Git branch to deploy (default: main)")
@click.option("--skip-jlink", is_flag=True, help="Skip J-Link installation")
@click.option("--skip-firewall", is_flag=True, help="Skip UFW firewall configuration")
@click.option("--skip-verify", is_flag=True, help="Skip post-deployment verification")
@click.option("--corporate-vpn", default=None, help="Corporate VPN interface name (e.g., tun0)")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts")
def install(ctx, box, ip, user, branch, skip_jlink, skip_firewall, skip_verify, corporate_vpn, yes):
    """
    Install lager-mono box code onto a new box.

    This command deploys the lager-mono box code to any IP address
    (local network, Tailscale, or other VPN). Uses git sparse checkout
    to minimize disk usage and enable 'lager update' for future updates.

    Examples:
        lager install --ip <BOX_IP>
        lager install --ip 192.168.1.100 --branch staging
        lager install --ip <BOX_IP> --user pi --yes
        lager install --box JUL-10
    """
    # 1. Resolve box name to IP and username if --box is provided
    if box and ip:
        click.secho("Error: Cannot specify both --box and --ip", fg='red', err=True)
        ctx.exit(1)

    if box:
        # Look up IP from box storage
        stored_ip = get_box_ip(box)
        if not stored_ip:
            click.secho(f"Error: Box '{box}' not found in configuration", fg='red', err=True)
            click.secho("Use 'lager boxes' to see available boxes, or use --ip to specify directly.", fg='yellow', err=True)
            ctx.exit(1)
        ip = stored_ip

        # Look up username from box storage (if not explicitly provided)
        if user is None:
            stored_user = get_box_user(box)
            user = stored_user or "lagerdata"
    elif ip is None:
        click.secho("Error: Either --box or --ip is required", fg='red', err=True)
        ctx.exit(1)
    else:
        # Default username if not provided
        if user is None:
            user = "lagerdata"

    # 2. Validate IP address
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        click.secho(f"Error: '{ip}' is not a valid IP address", fg='red', err=True)
        ctx.exit(1)

    ssh_host = f"{user}@{ip}"

    # 3. Check SSH connectivity (with password fallback)
    click.echo(f"Checking SSH connectivity to {ssh_host}...")
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", ssh_host, "echo ok"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            # SSH keys not configured - offer password authentication
            click.secho("SSH keys not configured", fg='yellow')
            click.echo()
            click.echo("SSH key authentication is not set up for this box.")
            click.echo("You can either:")
            click.echo(f"  1. Enter your password now (will be prompted during installation)")
            click.echo(f"  2. Set up SSH keys first with: ssh-copy-id {ssh_host}")
            click.echo()

            if yes or click.confirm("Would you like to continue with password authentication?"):
                click.echo()
                click.echo("Please enter your password to verify connectivity:")
                test_result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=10", "-o", "NumberOfPasswordPrompts=1",
                     ssh_host, "echo ok"],
                    timeout=60
                )
                if test_result.returncode != 0:
                    click.secho("Error: Password authentication failed", fg='red', err=True)
                    click.echo("Please verify your password and try again.", err=True)
                    ctx.exit(1)
                click.secho("Password authentication successful!", fg='green')
                click.echo()
                click.secho("Note: You may be prompted for your password multiple times during installation.", fg='yellow')
            else:
                click.secho("Installation cancelled.", fg='yellow')
                ctx.exit(0)
        else:
            click.secho("SSH connection OK", fg='green')
    except subprocess.TimeoutExpired:
        click.secho(f"Error: SSH connection to {ssh_host} timed out", fg='red', err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        ctx.exit(1)

    click.echo()

    # 4. Verify deploy script exists
    try:
        deploy_script = get_script_path("setup_and_deploy_box.sh")
        if not deploy_script.exists():
            raise FileNotFoundError(f"Script not found at {deploy_script}")
    except FileNotFoundError as e:
        click.secho(f"Error: Deployment script not found", fg='red', err=True)
        click.secho(f"Details: {e}", fg='yellow', err=True)
        click.secho("Try reinstalling lager-cli: pip install --upgrade lager-cli", fg='yellow', err=True)
        ctx.exit(1)

    # 5. Display summary and confirm
    click.echo()
    if box:
        click.secho(f"Installing lager-mono to {box} ({ip})...", fg='cyan', bold=True)
    else:
        click.secho(f"Installing lager-mono to {ip}...", fg='cyan', bold=True)
    click.echo(f"  Branch: {branch}")
    click.echo(f"  User: {user}")
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

    # 6. Run setup_and_deploy_box.sh with --sparse
    click.secho("Running box deployment...", fg='cyan')
    click.echo("This may take several minutes.\n")

    deploy_args = [str(deploy_script), ip, "--user", user, "--sparse", "--branch", branch, "--skip-add-box"]

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
    click.echo()

    # 7. Prompt to add box to .lager config (skip if --box was used since it's already configured)
    if not box and not yes:
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