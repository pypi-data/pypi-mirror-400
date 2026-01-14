"""
    lager.commands.utility.uninstall

    Uninstall lager-mono box code from a gateway
"""
import click
import subprocess
import ipaddress
from ...box_storage import get_box_ip, get_box_user


@click.command()
@click.pass_context
@click.option("--ip", help="Target box IP address")
@click.option("--box", help="Target box name from .lager config")
@click.option("--user", default="lagerdata", help="SSH username (default: lagerdata)")
@click.option("--keep-docker-images", is_flag=True, help="Keep Docker images (only remove containers)")
@click.option("--all", "remove_all", is_flag=True, help="Remove everything including /etc/lager, udev rules, sudoers, third_party, and deploy key")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts")
def uninstall(ctx, ip, box, user, keep_docker_images, remove_all, yes):
    """
    Uninstall lager-mono box code from a gateway.

    This command removes the lager-mono box code and related components
    from a gateway. By default it removes:

    \b
    - Docker containers (lager)
    - Docker images (unless --keep-docker-images)
    - ~/box directory (box code)

    By default, /etc/lager (saved nets, user packages) is PRESERVED.

    With --all flag, also removes:

    \b
    - /etc/lager directory (saved nets, user_requirements.txt)
    - Udev rules (/etc/udev/rules.d/lager-*.rules)
    - Sudoers file (/etc/sudoers.d/lagerdata-udev)
    - Third party tools (~/third_party)
    - Deploy key (~/.ssh/lager_deploy_key*)

    Examples:
        lager uninstall --ip <BOX_IP>
        lager uninstall --box my-box
        lager uninstall --ip <BOX_IP> --all
        lager uninstall --box my-box --yes
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

    ssh_host = f"{user}@{ip}"

    # 2. Check SSH connectivity
    click.echo(f"Checking SSH connectivity to {ssh_host}...")
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", ssh_host, "echo ok"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            click.secho(f"Error: Cannot connect to {ssh_host}", fg='red', err=True)
            click.secho("Make sure SSH keys are configured and the box is reachable.", fg='yellow', err=True)
            ctx.exit(1)
    except subprocess.TimeoutExpired:
        click.secho(f"Error: SSH connection to {ssh_host} timed out", fg='red', err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        ctx.exit(1)

    click.secho("SSH connection OK", fg='green')
    click.echo()

    # 3. Display what will be removed and confirm
    click.secho(f"Uninstalling lager-mono from {ip}...", fg='cyan', bold=True)
    click.echo()
    click.secho("The following will be REMOVED:", fg='yellow', bold=True)
    click.echo("  - Docker containers (lager)")
    if not keep_docker_images:
        click.echo("  - Docker images")
    click.echo("  - ~/box directory")

    if remove_all:
        click.echo("  - /etc/lager directory (saved nets, user packages)")
        click.echo("  - Udev rules (/etc/udev/rules.d/lager-*.rules)")
        click.echo("  - Sudoers file (/etc/sudoers.d/lagerdata-udev)")
        click.echo("  - ~/third_party directory")
        click.echo("  - Deploy key (~/.ssh/lager_deploy_key*)")
    else:
        click.echo()
        click.secho("The following will be PRESERVED:", fg='green', bold=True)
        click.echo("  - /etc/lager directory (saved nets, user packages)")

    click.echo()

    if not yes:
        click.secho("WARNING: This action cannot be undone!", fg='red', bold=True)
        if not click.confirm("Are you sure you want to proceed?", default=False):
            click.echo("Uninstall cancelled.")
            ctx.exit(0)

    click.echo()

    # Track sudo password (will be prompted for if needed)
    sudo_password = None

    # Helper function to run SSH commands
    def run_ssh(cmd, description, allow_fail=False, needs_sudo=False):
        """Run an SSH command and handle errors."""
        nonlocal sudo_password

        click.echo(f"  {description}...", nl=False)

        # If command needs sudo and we have a password, use sudo -S
        if needs_sudo and sudo_password:
            cmd = f"echo '{sudo_password}' | sudo -S {cmd}"

        try:
            ssh_cmd = ["ssh", "-o", "BatchMode=yes", ssh_host, cmd]

            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Check if we need to prompt for sudo password
            if result.returncode != 0 and needs_sudo and sudo_password is None:
                if "password is required" in result.stderr or "a terminal is required" in result.stderr:
                    click.secho(" needs password", fg='yellow')
                    click.echo()
                    sudo_password = click.prompt("  Enter sudo password for box", hide_input=True)
                    click.echo(f"  {description}...", nl=False)
                    # Retry with password
                    cmd_with_password = f"echo '{sudo_password}' | sudo -S " + cmd.replace("sudo ", "", 1)
                    ssh_cmd = ["ssh", "-o", "BatchMode=yes", ssh_host, cmd_with_password]
                    result = subprocess.run(
                        ssh_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

            if result.returncode == 0 or allow_fail:
                click.secho(" done", fg='green')
                return True
            else:
                click.secho(" failed", fg='red')
                if result.stderr:
                    # Filter out sudo password prompt messages
                    error_lines = [line for line in result.stderr.strip().split('\n')
                                   if not line.startswith('[sudo]') and line.strip()]
                    if error_lines:
                        click.secho(f"    Error: {error_lines[-1]}", fg='red', err=True)
                return False
        except subprocess.TimeoutExpired:
            click.secho(" timeout", fg='yellow')
            return False
        except Exception as e:
            click.secho(f" error: {e}", fg='red')
            return False

    # 4. Stop and remove Docker containers
    click.secho("[Step 1/5] Stopping Docker containers...", fg='cyan')
    run_ssh("docker stop $(docker ps -q) 2>/dev/null || true", "Stopping all containers", allow_fail=True)
    run_ssh("docker rm -f $(docker ps -aq) 2>/dev/null || true", "Removing all containers", allow_fail=True)
    click.echo()

    # 5. Remove Docker images (unless --keep-docker-images)
    click.secho("[Step 2/5] Cleaning Docker...", fg='cyan')
    if not keep_docker_images:
        run_ssh("docker image prune -af 2>/dev/null || true", "Removing Docker images", allow_fail=True)
        run_ssh("docker builder prune -af 2>/dev/null || true", "Clearing Docker build cache", allow_fail=True)
    else:
        click.echo("  Skipping Docker image removal (--keep-docker-images)")
    click.echo()

    # 6. Remove ~/box directory
    click.secho("[Step 3/5] Removing box code...", fg='cyan')
    run_ssh("rm -rf ~/box", "Removing ~/box directory")
    click.echo()

    # 7. Remove /etc/lager (only with --all)
    click.secho("[Step 4/5] Configuration...", fg='cyan')
    if remove_all:
        run_ssh("sudo rm -rf /etc/lager", "Removing /etc/lager directory", allow_fail=False, needs_sudo=True)
    else:
        click.echo("  Preserving /etc/lager directory (saved nets, user packages)")
    click.echo()

    # 8. Remove additional components if --all
    click.secho("[Step 5/5] Cleaning up additional components...", fg='cyan')
    if remove_all:
        # Remove udev rules
        run_ssh(
            "sudo rm -f /etc/udev/rules.d/lager-*.rules /etc/udev/rules.d/*lager*.rules 2>/dev/null; "
            "sudo udevadm control --reload-rules 2>/dev/null || true",
            "Removing udev rules",
            allow_fail=True,
            needs_sudo=True
        )

        # Remove sudoers file
        run_ssh(
            "sudo rm -f /etc/sudoers.d/lagerdata-udev 2>/dev/null || true",
            "Removing sudoers file",
            allow_fail=True,
            needs_sudo=True
        )

        # Remove third_party directory
        run_ssh("rm -rf ~/third_party", "Removing ~/third_party directory", allow_fail=True)

        # Remove deploy key
        run_ssh(
            "rm -f ~/.ssh/lager_deploy_key ~/.ssh/lager_deploy_key.pub",
            "Removing deploy key",
            allow_fail=True
        )

        # Clean up SSH config (remove GitHub entry for deploy key)
        run_ssh(
            "sed -i '/# Lager deploy key/,/IdentityFile.*lager_deploy_key/d' ~/.ssh/config 2>/dev/null || true",
            "Cleaning SSH config",
            allow_fail=True
        )
    else:
        click.echo("  Skipping additional cleanup (use --all for complete removal)")

    click.echo()
    click.secho("Uninstall complete!", fg='green', bold=True)
    click.echo()
    click.echo(f"The lager-mono box code has been removed from {ip}.")

    if not remove_all:
        click.echo()
        click.secho("Note: /etc/lager directory was preserved (contains saved nets and user packages).", fg='green')
        click.echo()
        click.echo("To completely remove all lager components including configuration, run:")
        click.secho(f"  lager uninstall --ip {ip} --all", fg='cyan')
