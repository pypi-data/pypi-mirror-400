"""
    lager.commands.utility.update

    Update box code from GitHub repository

    Migrated from cli/update/commands.py to cli/commands/utility/update.py
    as part of Session 6, Part 6.5 restructuring.
"""
import click
import subprocess
import time
import sys
import threading
from ...box_storage import resolve_and_validate_box, get_box_user
from ...context import get_default_box


class ProgressBar:
    """Simple progress bar for tracking update steps."""

    def __init__(self, total_steps, width=40):
        self.total_steps = total_steps
        self.current_step = 0
        self.width = width
        self.current_task = ""
        self.start_time = time.time()
        self._stop_event = threading.Event()
        self._render_thread = None
        self._thread_started = False

    def _periodic_render(self):
        """Background thread that renders progress bar every second."""
        while not self._stop_event.is_set():
            self._render()
            time.sleep(1)

    def update(self, task_name):
        """Update progress bar with new task."""
        # Start background thread on first update to avoid showing empty 0/13 bar
        if not self._thread_started:
            self._render_thread = threading.Thread(target=self._periodic_render, daemon=True)
            self._render_thread.start()
            self._thread_started = True

        self.current_step += 1
        self.current_task = task_name
        self._render()

    def _format_elapsed_time(self):
        """Format elapsed time as human-readable string."""
        elapsed = int(time.time() - self.start_time)
        if elapsed < 60:
            return f"{elapsed}s"
        elif elapsed < 3600:
            minutes = elapsed // 60
            seconds = elapsed % 60
            return f"{minutes}m {seconds:02d}s"
        else:
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            return f"{hours}h {minutes:02d}m {seconds:02d}s"

    def _render(self):
        """Render the progress bar."""
        percent = self.current_step / self.total_steps
        filled = int(self.width * percent)
        bar = '█' * filled + '░' * (self.width - filled)
        elapsed = self._format_elapsed_time()
        # Clear line and print progress with extra padding to clear previous text
        task_text = self.current_task[:40]  # Reduced to 40 to make room for time
        sys.stdout.write(f'\r[{bar}] {self.current_step}/{self.total_steps} {task_text:<40} ⏱ {elapsed}')
        sys.stdout.flush()

    def finish(self, success=True):
        """Complete the progress bar."""
        # Stop the background rendering thread if it was started
        if self._thread_started:
            self._stop_event.set()
            self._render_thread.join(timeout=2)

        elapsed = self._format_elapsed_time()
        if success:
            bar = '█' * self.width
            # Add extra padding to clear any remaining text from previous renders
            sys.stdout.write(f'\r[{bar}] Complete! ⏱ {elapsed}{" " * 50}\n')
        else:
            filled = int(self.width * self.current_step / self.total_steps)
            bar = '█' * filled + '░' * (self.width - filled)
            sys.stdout.write(f'\r[{bar}] Failed ⏱ {elapsed}{" " * 50}\n')
        sys.stdout.flush()


@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
@click.option('--skip-restart', is_flag=True, help='Skip container restart after update')
@click.option('--version', required=False, help='Box version/branch to update to (e.g., staging, main)')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output (default shows progress bar only)')
@click.option('--force', is_flag=True, help='Force fresh Docker build by removing cached image (use for major code changes)')
def update(ctx, box, yes, skip_restart, version, verbose, force):
    """
    Update box code from GitHub repository

    This command will:
    1. Connect to the box via SSH
    2. Pull the latest code from GitHub
    3. Install udev rules for USB instrument access
    4. Rebuild and restart Docker containers
    5. Install J-Link if not already present (automatic)
    6. Verify services are running correctly

    Example:
        lager update --box JUL-3
        lager update --box HYP-3 --yes
        lager update --box JUL-3 --verbose
        lager update --box JUL-3 --version staging
        lager update --box JUL-3 --force  # Force fresh build (for major changes)

    The --force flag removes the Docker image before rebuilding, bypassing Docker's
    layer cache. Use this when deleting modules or making structural changes that
    Docker's cache might not detect.
    """
    from ...box_storage import update_box_version
    from ... import __version__ as cli_version

    # Helper for conditional output
    def log(message, nl=True, **kwargs):
        """Print message only in verbose mode."""
        if verbose:
            click.echo(message, nl=nl, **kwargs)

    def log_status(message, status, color, print_message=False):
        """Print status in verbose mode.

        If print_message=True, prints the full message + status.
        If print_message=False (default), only prints the status (assumes message already printed by log()).
        """
        if verbose:
            if print_message:
                click.echo(message, nl=False)
            click.secho(f' {status}', fg=color)

    def log_error(message):
        """Always print errors."""
        click.secho(message, fg='red', err=True)

    # Default to 'main' version if not specified
    target_version = version or 'main'

    # Use default box if none specified
    if not box:
        box = get_default_box(ctx)

    box_name = box

    # Resolve box name to IP address
    resolved_box = resolve_and_validate_box(ctx, box)

    # Get username (defaults to 'lagerdata' if not specified)
    username = get_box_user(box) or 'lagerdata'

    ssh_host = f'{username}@{resolved_box}'

    # Display update information (always show this)
    click.echo()
    click.secho('Box Update', fg='blue', bold=True)
    click.echo(f'Target:  {box_name} ({resolved_box})')
    click.echo(f'Version: {target_version}')
    if verbose:
        click.echo(f'CLI:     {cli_version}')
    click.echo()

    # Confirm before proceeding
    if not yes:
        if not click.confirm('This will update the box code and restart services. Continue?'):
            click.secho('Update cancelled.', fg='yellow')
            ctx.exit(0)

    # Initialize progress bar (only in non-verbose mode)
    # Total steps: connectivity, repo check, git state check, fetch, checkout/pull, flatten, udev, docker stop, [force image removal], docker build, cleanup, /etc/lager, docker start, binaries, jlink, verify, version
    total_steps = 17 if force else 16
    progress = None if verbose else ProgressBar(total_steps=total_steps)

    if not verbose:
        click.echo()  # Blank line before progress bar

    # Step 1: Check SSH connectivity
    if progress:
        progress.update("Checking SSH...")
    log('Checking connectivity...', nl=False)

    use_interactive_ssh = False
    try:
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', '-o', 'BatchMode=yes',
             ssh_host, 'echo test'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            if progress:
                progress.finish(success=False)
            click.echo()  # New line after progress bar
            click.secho('SSH keys not configured', fg='yellow')
            click.echo()
            click.echo('SSH key authentication is not set up for this box.')
            click.echo('You can either:')
            click.echo('  1. Enter your password now (will be prompted for each SSH command)')
            click.echo('  2. Set up SSH keys first with: ssh-copy-id ' + ssh_host)
            click.echo()

            if yes or click.confirm('Would you like to continue with password authentication?'):
                click.echo()
                click.echo('Please enter your password to verify connectivity:')
                test_result = subprocess.run(
                    ['ssh', '-o', 'ConnectTimeout=10', '-o', 'NumberOfPasswordPrompts=1',
                     ssh_host, 'echo test'],
                    timeout=30
                )
                if test_result.returncode != 0:
                    log_error('Error: Password authentication failed')
                    click.echo('Please verify your password and try again.', err=True)
                    ctx.exit(1)
                click.secho('Password authentication successful!', fg='green')
                use_interactive_ssh = True
                # Reinitialize progress bar after password prompt
                if not verbose:
                    progress = ProgressBar(total_steps=total_steps)
                    progress.current_step = 1  # We completed step 1
            else:
                click.secho('Update cancelled.', fg='yellow')
                ctx.exit(0)
        else:
            log_status('Checking connectivity...', 'OK', 'green')
    except subprocess.TimeoutExpired:
        if progress:
            progress.finish(success=False)
        log_error(f'Error: Connection to {ssh_host} timed out')
        ctx.exit(1)
    except Exception as e:
        if progress:
            progress.finish(success=False)
        log_error(f'Error: {str(e)}')
        ctx.exit(1)

    # Helper function to run SSH commands
    def run_ssh_command_with_output(cmd, timeout_secs=120):
        """Run an SSH command and capture output."""
        ssh_cmd = ['ssh']
        if not use_interactive_ssh:
            ssh_cmd.extend(['-o', 'BatchMode=yes'])
        ssh_cmd.append(ssh_host)
        ssh_cmd.append(cmd)
        return subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout_secs)

    def run_ssh_command_interactive(cmd, timeout_secs=120):
        """Run an SSH command that may require sudo password input.

        This function allocates a pseudo-terminal (-t) to allow interactive
        password prompts when using password authentication mode.
        """
        ssh_cmd = ['ssh', '-t']  # Always use -t for interactive commands
        if not use_interactive_ssh:
            ssh_cmd.extend(['-o', 'BatchMode=yes'])
        ssh_cmd.append(ssh_host)
        ssh_cmd.append(cmd)
        # Don't capture output - let it stream to terminal for interactive prompts
        return subprocess.run(ssh_cmd, timeout=timeout_secs)

    # Step 2: Check if box directory exists and is a git repo
    if progress:
        progress.update("Checking repository...")
    log('Checking box repository...', nl=False)

    result = run_ssh_command_with_output('test -d ~/box/.git')
    if result.returncode != 0:
        if progress:
            progress.finish(success=False)
        log_error('Error: Box directory is not a git repository')
        click.echo('The box may have been deployed with rsync instead of git clone.')
        click.echo('Please re-deploy the box using the latest deployment script.')
        ctx.exit(1)
    log_status('Checking box repository...', 'OK', 'green')

    # Step 2.5: Check for and fix flattened sparse checkout state
    # After install with --sparse, files are moved from box/ to root, which breaks git tracking
    # Detect this by checking if lager/ exists at root but git expects it in box/
    if progress:
        progress.update("Checking git state...")
    log('Checking for flattened sparse checkout...', nl=False)

    # Check if we have files at root level that git thinks should be in box/
    flattened_check = run_ssh_command_with_output(
        'cd ~/box && '
        'test -d lager && '  # Files exist at root
        'test ! -d box && '  # No box/ subdirectory
        'git ls-tree HEAD box/ 2>/dev/null | grep -q .'  # Git expects files in box/
    )

    # Track if we need to re-flatten after update
    needs_flatten = False

    if flattened_check.returncode == 0:
        log_status('Checking for flattened sparse checkout...', 'DETECTED', 'yellow')
        log('Fixing flattened sparse checkout state...', nl=False)

        # Clean up untracked files (the flattened files) and reset to proper git state
        # This removes root-level files and restores box/ directory structure
        fix_result = run_ssh_command_with_output(
            'cd ~/box && '
            # Remove the flattened files at root (they're untracked)
            'rm -rf lager oscilloscope-daemon start_box.sh third_party udev_rules verify_restart_policy.sh README.md 2>/dev/null; '
            # Reset git to restore box/ directory
            f'git fetch origin {target_version} && '
            f'git reset --hard origin/{target_version}'
        )

        if fix_result.returncode != 0:
            log_status('Fixing flattened sparse checkout state...', 'FAILED', 'red')
            if verbose and fix_result.stderr:
                click.echo(f'  Error: {fix_result.stderr.strip()}', err=True)
            # Continue anyway - the regular flow might still work
        else:
            log_status('Fixing flattened sparse checkout state...', 'OK', 'green')
            needs_flatten = True  # We restored box/, need to flatten it
    else:
        # Check if box/ directory exists (needs flattening) or lager/ at root (already flat)
        box_dir_check = run_ssh_command_with_output('cd ~/box && test -d box')
        if box_dir_check.returncode == 0:
            # box/ exists, needs flattening
            needs_flatten = True
            log_status('Checking for flattened sparse checkout...', 'NEEDS FLATTEN', 'yellow')
        else:
            log_status('Checking for flattened sparse checkout...', 'OK', 'green')

    # Step 3: Show current version (verbose only)
    if verbose:
        click.echo('Current version:', nl=False)
        result = run_ssh_command_with_output('cd ~/box && git log -1 --format="%h - %s (%cr)"')
        if result.returncode == 0 and result.stdout.strip():
            click.echo(f' {result.stdout.strip()}')
        else:
            click.echo(' (unknown)')

    # Step 4: Fetch and check for updates
    if progress:
        progress.update("Fetching updates...")
    log(f'Fetching updates from origin/{target_version}...', nl=False)

    result = run_ssh_command_with_output(f'cd ~/box && git fetch origin {target_version}')
    if result.returncode != 0:
        if progress:
            progress.finish(success=False)
        log_error('Error: Failed to fetch updates from GitHub')
        if verbose and result.stderr:
            click.echo(result.stderr, err=True)
        ctx.exit(1)
    log_status(f'Fetching updates from origin/{target_version}...', 'OK', 'green')

    # Check if there are updates available
    result = run_ssh_command_with_output(f'cd ~/box && git rev-list HEAD..origin/{target_version} --count')

    needs_pull = False
    if result.returncode == 0:
        commits_behind = int(result.stdout.strip())
        if commits_behind == 0:
            if verbose:
                click.secho('Box code is already up to date!', fg='green')
            needs_pull = False
        else:
            log(f'Updates available: {commits_behind} new commit(s)')
            needs_pull = True

    if needs_pull:
        # Step 5: Update git repo
        if progress:
            progress.update("Pulling updates...")
        log('Ensuring required files are tracked...', nl=False)

        run_ssh_command_with_output(
            'cd ~/box && '
            'git sparse-checkout list | grep -q "^udev_rules$" || git sparse-checkout add udev_rules && '
            'git sparse-checkout list | grep -q "^cli/__init__.py$" || git sparse-checkout add cli/__init__.py'
        )
        log_status('Ensuring required files are tracked...', 'OK', 'green')

        log(f'Checking out version {target_version}...', nl=False)
        result = run_ssh_command_with_output(f'cd ~/box && git checkout {target_version}')
        if result.returncode != 0:
            if progress:
                progress.finish(success=False)
            log_error(f'Error: Failed to checkout version {target_version}')
            ctx.exit(1)
        log_status(f'Checking out version {target_version}...', 'OK', 'green')

        log(f'Updating to match origin/{target_version}...', nl=False)
        result = run_ssh_command_with_output(f'cd ~/box && git reset --hard origin/{target_version}')
        if result.returncode != 0:
            if progress:
                progress.finish(success=False)
            log_error('Error: Failed to update branch')
            ctx.exit(1)
        log_status(f'Updating to match origin/{target_version}...', 'OK', 'green')

        if verbose:
            click.echo('New version:', nl=False)
            result = run_ssh_command_with_output('cd ~/box && git log -1 --format="%h - %s (%cr)"')
            if result.returncode == 0 and result.stdout.strip():
                click.echo(f' {result.stdout.strip()}')
        needs_flatten = True  # After pull, always flatten
    else:
        if progress:
            progress.update("Already up to date")

    # Flatten the directory structure if needed (box/ -> root)
    # This handles sparse checkout where files are in ~/box/box/ but need to be in ~/box/
    if needs_flatten:
        if progress:
            progress.update("Flattening structure...")
        log('Updating file structure...', nl=False)
        result = run_ssh_command_with_output(
            'cd ~/box && '
            'if [ -d box ]; then '
            'shopt -s dotglob && '
            'cp -rf box/* . && '
            'rm -rf box; '
            'fi'
        )
        if result.returncode == 0:
            log_status('Updating file structure...', 'OK', 'green')
        else:
            # Non-fatal - box might already be flattened
            log_status('Updating file structure...', 'SKIPPED', 'yellow')

    # Step 6: Check and update udev rules if needed
    if progress:
        progress.update("Checking udev rules...")
    log('Checking udev rules...', nl=False)

    # Check for udev_rules in the flattened structure first, then fall back to box/udev_rules
    result = run_ssh_command_with_output('test -d ~/box/udev_rules')
    udev_path = '~/box/udev_rules' if result.returncode == 0 else '~/box/box/udev_rules'

    result = run_ssh_command_with_output(f'test -d {udev_path}')
    if result.returncode == 0:
        # Check if rules file exists in source
        rules_check = run_ssh_command_with_output(f'test -f {udev_path}/99-instrument.rules')
        if rules_check.returncode != 0:
            log_status('Checking udev rules...', 'FAILED (file not found)', 'red')
            if verbose:
                click.echo(f'  Error: {udev_path}/99-instrument.rules not found', err=True)
        else:
            # Check if already installed and matches source
            diff_check = run_ssh_command_with_output(
                f'diff -q {udev_path}/99-instrument.rules /etc/udev/rules.d/99-instrument.rules >/dev/null 2>&1'
            )

            if diff_check.returncode == 0:
                # Files match - skip installation
                log_status('Checking udev rules...', 'OK (already up-to-date)', 'green')
            else:
                # Need to install/update
                log_status('Checking udev rules...', 'UPDATE NEEDED', 'yellow')
                log('Installing udev rules...', nl=False)

                install_cmd = (
                    f'cp {udev_path}/99-instrument.rules /tmp/ && '
                    'sudo cp /tmp/99-instrument.rules /etc/udev/rules.d/ && '
                    'sudo chmod 644 /etc/udev/rules.d/99-instrument.rules && '
                    'sudo udevadm control --reload-rules && '
                    'sudo udevadm trigger && '
                    'rm -f /tmp/99-instrument.rules'
                )

                # Use interactive mode for sudo commands - allows password prompts
                if not verbose and progress:
                    # Pause progress bar and inform user
                    sys.stdout.write('\n')
                    click.echo('Installing udev rules (may require sudo password)...')
                elif verbose:
                    click.echo()  # Add newline before potential sudo prompt

                result = run_ssh_command_interactive(install_cmd)

                if not verbose and progress:
                    # Resume progress tracking after interactive command
                    pass  # Progress bar continues automatically
                elif verbose:
                    click.echo()  # Add newline after sudo command

                if result.returncode == 0:
                    # Verify installation succeeded
                    verify_result = run_ssh_command_with_output('test -f /etc/udev/rules.d/99-instrument.rules')
                    if verify_result.returncode == 0:
                        log_status('Installing udev rules...', 'OK', 'green')
                    else:
                        log_status('Installing udev rules...', 'FAILED (verification failed)', 'red')
                        if verbose:
                            click.echo('  Error: udev rules file not found after installation', err=True)
                            click.echo('  This may indicate a sudo permission issue', err=True)
                else:
                    log_status('Installing udev rules...', 'FAILED', 'red')
                    if verbose:
                        click.echo('  Error: Failed to install udev rules', err=True)
                        click.echo('  This may be a sudo permission issue. The sudoers file may need updating.', err=True)
                        click.echo(f'  You can manually install with: ssh {ssh_host}', err=True)
                        click.echo(f'    sudo cp ~/box/udev_rules/99-instrument.rules /etc/udev/rules.d/', err=True)
                        click.echo(f'    sudo udevadm control --reload-rules && sudo udevadm trigger', err=True)
    else:
        log_status('Checking udev rules...', 'FAILED (directory not found)', 'red')
        if verbose:
            click.echo(f'  Error: {udev_path} directory not found', err=True)
            click.echo('  The udev_rules directory should be included in the sparse checkout', err=True)

    # Skip container restart if requested
    if skip_restart:
        if progress:
            progress.finish(success=True)
        click.echo()
        click.secho('Skipping container restart (--skip-restart flag set)', fg='yellow')
        click.echo(f'Run manually: ssh {ssh_host} "cd ~/box && ./start_box.sh"')
        ctx.exit(0)

    # Step 7: Stop containers
    if progress:
        progress.update("Stopping containers...")
    log('Stopping containers...', nl=False)

    run_ssh_command_with_output(
        'docker stop $(docker ps -aq) 2>/dev/null || true && '
        'docker rm $(docker ps -aq) 2>/dev/null || true',
        timeout_secs=30
    )
    log_status('Stopping containers...', 'OK', 'green')

    # Step 7.5: Remove Docker image if --force flag is set
    if force:
        if progress:
            progress.update("Removing cached image...")
        log('Removing cached Docker image (--force)...', nl=False)

        run_ssh_command_with_output(
            'docker rmi lager 2>/dev/null || true',
            timeout_secs=30
        )
        log_status('Removing cached Docker image (--force)...', 'OK', 'green')

    # Step 8: Rebuild Docker container (the slow part)
    if progress:
        progress.update("Building container...")
    log('Rebuilding Docker container (this may take several minutes)...')

    ssh_cmd = ['ssh']
    if not use_interactive_ssh:
        ssh_cmd.extend(['-o', 'BatchMode=yes'])
    ssh_cmd.extend([ssh_host,
         'cd ~/box/lager && '
         'docker build -f docker/box.Dockerfile -t lager .'])

    if verbose:
        # Stream output in verbose mode
        process = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        if process.stdout:
            for line in process.stdout:
                click.echo(f'    {line}', nl=False)
        return_code = process.wait(timeout=600)
    else:
        # Silent mode - just run and wait
        process = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        # Read output to consume Docker build logs
        # The background thread will update the progress bar every second automatically
        if process.stdout:
            for line in process.stdout:
                pass  # Just consume the output
        return_code = process.wait(timeout=600)

    if return_code != 0:
        if progress:
            progress.finish(success=False)
        log_error('Error: Failed to rebuild Docker container')
        ctx.exit(1)
    log_status('Building container...', 'OK', 'green')

    # Step 8.5: Clean up old images to save disk space (after successful build)
    if progress:
        progress.update("Cleaning up images...")
    log('Cleaning up old Docker images...', nl=False)
    run_ssh_command_with_output(
        'docker image prune -af --filter "until=24h"',
        timeout_secs=30
    )
    log_status('Cleaning up old Docker images...', 'OK', 'green')

    # Step 9: Ensure /etc/lager directory exists (required by start_box.sh)
    if progress:
        progress.update("Setting up /etc/lager...")
    log('Ensuring /etc/lager directory exists...', nl=False)

    # Use full paths to match sudoers whitelist in deployment script
    # The sudoers file allows: /bin/mkdir -p /etc/lager, /bin/chmod 777 /etc/lager
    # Only run sudo commands if directory doesn't exist or isn't writable
    check_result = run_ssh_command_with_output('[ -d /etc/lager ] && [ -w /etc/lager ]')
    if check_result.returncode == 0:
        # Directory exists and is writable, no sudo needed
        log_status('Ensuring /etc/lager directory exists...', 'OK', 'green')
    else:
        # Need to create/fix directory with sudo - use interactive mode
        if not verbose and progress:
            # Pause progress bar and inform user
            sys.stdout.write('\n')
            click.echo('Setting up /etc/lager directory (may require sudo password)...')
        elif verbose:
            click.echo()  # Add newline before potential sudo prompt

        etc_lager_result = run_ssh_command_interactive(
            'sudo /bin/mkdir -p /etc/lager && sudo /bin/chmod 777 /etc/lager'
        )

        if not verbose and progress:
            # Resume progress tracking after interactive command
            pass  # Progress bar continues automatically
        elif verbose:
            click.echo()  # Add newline after sudo command

        if etc_lager_result.returncode != 0:
            if progress:
                progress.finish(success=False)
            log_error('Error: Failed to create /etc/lager directory')
            click.echo('This may be a sudo permission issue. SSH into the box and run:', err=True)
            click.echo(f'  ssh {ssh_host}', err=True)
            click.echo(f'  sudo mkdir -p /etc/lager && sudo chmod 777 /etc/lager', err=True)
            click.echo('Then run lager update again.', err=True)
            ctx.exit(1)
        log_status('Ensuring /etc/lager directory exists...', 'OK', 'green')

    # Step 10: Start container
    if progress:
        progress.update("Starting container...")
    log('Starting lager container...', nl=False)

    result = run_ssh_command_with_output(
        'cd ~/box && chmod +x start_box.sh && ./start_box.sh',
        timeout_secs=180
    )

    if result.returncode != 0:
        if progress:
            progress.finish(success=False)
        log_error('Error: Failed to start lager container')
        # Show error output even in non-verbose mode so users can see what went wrong
        if result.stdout:
            click.echo('Container output:', err=True)
            click.echo(result.stdout, err=True)
        if result.stderr:
            click.echo(result.stderr, err=True)
        ctx.exit(1)
    log_status('Starting lager container...', 'OK', 'green')

    # Wait for services
    time.sleep(5)

    # Step 11: Setup customer binaries directory
    if progress:
        progress.update("Setting up binaries...")
    log('Setting up customer binaries directory...', nl=False)

    # Create the customer-binaries directory with proper permissions
    # This allows the container (running as www-data) to write uploaded binaries
    binaries_setup = run_ssh_command_with_output(
        'mkdir -p ~/third_party/customer-binaries && '
        'chmod 777 ~/third_party/customer-binaries'
    )
    if binaries_setup.returncode == 0:
        log_status('Setting up customer binaries directory...', 'OK', 'green')
    else:
        log_status('Setting up customer binaries directory...', 'SKIPPED', 'yellow')

    # Step 12: Install J-Link if not present
    if progress:
        progress.update("Checking J-Link...")
    log('Checking J-Link installation...', nl=False)

    # Check if J-Link is already installed
    jlink_check = run_ssh_command_with_output(
        'find ~/third_party -name JLinkGDBServerCLExe 2>/dev/null | head -n 1'
    )

    if jlink_check.returncode == 0 and jlink_check.stdout.strip():
        log_status('Checking J-Link installation...', 'OK (already installed)', 'green')
    else:
        log_status('Checking J-Link installation...', 'NOT FOUND', 'yellow')
        log('  Installing J-Link...')

        # Create installation script on box
        install_script = """#!/bin/bash
set -e

USERNAME="${USER}"
THIRD_PARTY_DIR="/home/${USERNAME}/third_party"

# Check if already installed
if find "$THIRD_PARTY_DIR" -name JLinkGDBServerCLExe 2>/dev/null | grep -q .; then
    echo "J-Link already installed"
    exit 0
fi

mkdir -p "$THIRD_PARTY_DIR"
cd /tmp

echo "Downloading J-Link debian package..."
DEB_URL="https://www.segger.com/downloads/jlink/JLink_Linux_x86_64.deb"

if command -v wget &> /dev/null; then
    wget --post-data="accept_license_agreement=accepted" -q --show-progress -O JLink.deb "$DEB_URL" 2>&1 || \\
        wget -q --show-progress -O JLink.deb "$DEB_URL" 2>&1
elif command -v curl &> /dev/null; then
    curl -L -d "accept_license_agreement=accepted" -# -o JLink.deb "$DEB_URL" 2>&1 || \\
        curl -L -# -o JLink.deb "$DEB_URL" 2>&1
else
    echo "Error: Neither wget nor curl available"
    exit 1
fi

if [ ! -f JLink.deb ] || [ ! -s JLink.deb ]; then
    echo "Download failed"
    exit 1
fi

echo "Extracting J-Link..."

# Use dpkg-deb if available (most reliable), otherwise use ar
if command -v dpkg-deb &> /dev/null; then
    dpkg-deb -x JLink.deb extracted
    if [ -d extracted/opt/SEGGER ]; then
        JLINK_DIR=$(find extracted/opt/SEGGER -maxdepth 1 -type d -name "JLink*" | head -n 1)
        if [ -n "$JLINK_DIR" ]; then
            mv "$JLINK_DIR" "$THIRD_PARTY_DIR/"
            echo "J-Link installed to $THIRD_PARTY_DIR/$(basename $JLINK_DIR)"
            rm -rf extracted JLink.deb
            echo "Installation complete"
            exit 0
        fi
    fi
    echo "Error: Could not find J-Link in package"
    rm -rf extracted JLink.deb
    exit 1
elif command -v ar &> /dev/null; then
    ar x JLink.deb

    if [ -f data.tar.xz ]; then
        tar xJf data.tar.xz ./opt/SEGGER 2>&1 | grep -v "Cannot utime|Cannot change mode" || true
    elif [ -f data.tar.gz ]; then
        tar xzf data.tar.gz ./opt/SEGGER 2>&1 | grep -v "Cannot utime|Cannot change mode" || true
    else
        echo "Error: Package format not recognized"
        exit 1
    fi

    if [ -d opt/SEGGER ]; then
        JLINK_DIR=$(find opt/SEGGER -maxdepth 1 -type d -name "JLink*" | head -n 1)
        if [ -n "$JLINK_DIR" ]; then
            mv "$JLINK_DIR" "$THIRD_PARTY_DIR/"
            echo "J-Link installed to $THIRD_PARTY_DIR/$(basename $JLINK_DIR)"
        else
            echo "Error: J-Link directory not found in package"
            exit 1
        fi
    else
        echo "Error: Package extraction failed"
        exit 1
    fi

    cd /tmp
    rm -f JLink.deb control.tar.* data.tar.* debian-binary
    rm -rf opt etc usr var

    echo "Installation complete"
    exit 0
else
    echo "Error: Neither dpkg-deb nor ar available for extracting .deb package"
    echo "Please install dpkg or binutils package"
    exit 1
fi
"""

        # Copy install script to box and execute
        install_result = run_ssh_command_with_output(
            f'cat > /tmp/install_jlink.sh << \'EOF\'\n{install_script}\nEOF\n'
            'chmod +x /tmp/install_jlink.sh && '
            '/tmp/install_jlink.sh && '
            'rm /tmp/install_jlink.sh',
            timeout_secs=180
        )

        if install_result.returncode == 0:
            log_status('  Installing J-Link...', 'OK', 'green')
            if verbose and install_result.stdout:
                for line in install_result.stdout.strip().split('\n'):
                    click.echo(f'    {line}')
        else:
            log_status('  Installing J-Link...', 'FAILED (will use pyOCD)', 'yellow')
            if verbose:
                if install_result.stderr:
                    click.echo(f'    Error: {install_result.stderr.strip()}', err=True)
                click.echo()
                click.echo('    J-Link download failed. You can either:')
                click.echo(f'      1. Copy from another box: deployment/copy_jlink_from_box.sh <source-box> {box_name}')
                click.echo('      2. Manually download from https://www.segger.com/downloads/jlink/')
                click.echo('      3. Use pyOCD (already installed, works with most debug probes)')
                click.echo()

    # Step 13: Verify and store version
    if progress:
        progress.update("Verifying...")
    log('Verifying container status...', nl=False)

    result = run_ssh_command_with_output("docker ps --filter 'name=lager' --format '{{.Names}}' | wc -l")
    if result.returncode == 0:
        running_count = int(result.stdout.strip())
        if running_count >= 1:
            log_status('Verifying container status...', 'OK', 'green')
        else:
            log_status('Verifying container status...', 'WARNING', 'yellow')
    else:
        log_status('Verifying container status...', 'FAILED', 'red')

    # Show container status (verbose only)
    if verbose:
        click.echo()
        click.secho('Container Status:', fg='blue', bold=True)
        result = run_ssh_command_with_output(
            "docker ps --filter 'name=lager' "
            "--format 'table {{.Names}}\t{{.Status}}'"
        )
        if result.returncode == 0:
            click.echo(result.stdout.strip())

    # Read and store version
    log('Storing version information...', nl=False)

    read_version_cmd = (
        'cd ~/box && '
        'grep -E "^__version__\\s*=\\s*" cli/__init__.py | '
        'sed -E "s/__version__\\s*=\\s*[\\x27\\x22]([^\\x27\\x22]+)[\\x27\\x22]/\\1/"'
    )
    result = run_ssh_command_with_output(read_version_cmd)

    if result.returncode == 0 and result.stdout.strip():
        box_cli_version = result.stdout.strip()
    else:
        box_cli_version = target_version

    version_content = f'{box_cli_version}|{cli_version}'

    # /etc/lager was already created in Step 9, just write the version file
    run_ssh_command_with_output(f'echo "{version_content}" > /etc/lager/version')

    if box:
        update_box_version(box, box_cli_version)

    log_status('Storing version information...', 'OK', 'green')

    # Finish progress bar
    if progress:
        progress.finish(success=True)

    # Final success message
    click.echo()
    click.secho('Box update completed successfully!', fg='green', bold=True)
    click.echo(f'Verify with: lager hello --box {box_name}')
    click.echo()
