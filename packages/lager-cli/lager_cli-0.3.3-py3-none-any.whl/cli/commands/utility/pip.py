"""
    lager.commands.utility.pip

    Commands for managing pip packages in lager python container

    Migrated from cli/pip/commands.py to cli/commands/utility/pip.py
    as part of Session 6, Part 6.6 restructuring.
"""
import sys
import os
import re
import click
from ...context import get_default_box
from ..development.python import run_python_internal_get_output, run_python_internal

def _normalize_package_name(pkg):
    """Normalize package name for comparison (remove version specifiers)"""
    # Extract package name before version specifier
    match = re.match(r'^([a-zA-Z0-9\-_\.]+)', pkg)
    if match:
        return match.group(1).lower().replace('_', '-')
    return pkg.lower()

def _read_remote_requirements(ctx, box):
    """Read user requirements from remote box via HTTP"""
    import json
    import tempfile

    try:
        # Use run_python_internal to read the file via HTTP
        # Create a simple Python script to read the file
        script_content = """
import os
import json

requirements_file = '/etc/lager/user_requirements.txt'

if os.path.exists(requirements_file):
    with open(requirements_file, 'r') as f:
        content = f.read()
    packages = []
    for line in content.splitlines():
        line = line.strip()
        # Skip empty lines and comments
        if line and not line.startswith('#'):
            packages.append(line)
    print(json.dumps({'packages': packages}))
else:
    print(json.dumps({'packages': []}))
"""

        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(script_content)
            temp_script = f.name

        try:
            # Run the script and capture output
            output_bytes = run_python_internal_get_output(
                ctx,
                temp_script,
                box,
                image='',
                env=(),
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum='SIGTERM',
                timeout=0,
                detach=False,
                port=(),
                org=None,
                args=(),
            )

            # Parse the output
            output = output_bytes.decode('utf-8') if output_bytes else ''
            result = json.loads(output.strip())
            return result['packages']

        finally:
            # Clean up temp file
            os.unlink(temp_script)

    except Exception as e:
        click.secho(f'Error: Failed to read requirements from box: {e}', fg='red', err=True)
        sys.exit(1)

def _write_remote_requirements(ctx, box, packages):
    """Write packages to remote box user requirements file via HTTP"""
    import json
    import tempfile

    try:
        # Create the file content
        content = '# User-installed packages via lager pip\n'
        content += '# This file is managed by lager pip install/uninstall commands\n'
        content += '# Add your custom packages below (one per line with optional version specifier)\n'
        content += '#\n'
        content += '# Examples:\n'
        content += '#   pandas==2.0.0\n'
        content += '#   numpy\n'
        content += '#   scipy>=1.10.0\n'
        content += '\n'
        for pkg in sorted(packages):
            content += f'{pkg}\n'

        # Create a Python script to write the file
        script_content = f"""
import os
import json

requirements_file = '/etc/lager/user_requirements.txt'
content = {json.dumps(content)}

# Ensure directory exists
os.makedirs(os.path.dirname(requirements_file), exist_ok=True)

# Write the file
with open(requirements_file, 'w') as f:
    f.write(content)

print(json.dumps({{'status': 'success'}}))
"""

        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(script_content)
            temp_script = f.name

        try:
            # Run the script and capture output
            output_bytes = run_python_internal_get_output(
                ctx,
                temp_script,
                box,
                image='',
                env=(),
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum='SIGTERM',
                timeout=0,
                detach=False,
                port=(),
                org=None,
                args=(),
            )

            # Verify success
            output = output_bytes.decode('utf-8') if output_bytes else ''
            result = json.loads(output.strip())
            if result.get('status') != 'success':
                raise Exception('Failed to write requirements file')

        finally:
            # Clean up temp file
            os.unlink(temp_script)

    except Exception as e:
        click.secho(f'Error: Failed to write requirements to box: {e}', fg='red', err=True)
        sys.exit(1)

def _validate_packages(packages):
    """Validate that packages exist on PyPI before attempting installation"""
    import urllib.request
    import json

    invalid_packages = []

    for pkg in packages:
        # Extract package name (remove version specifiers)
        pkg_name = _normalize_package_name(pkg)

        try:
            # Check if package exists on PyPI
            url = f'https://pypi.org/pypi/{pkg_name}/json'
            req = urllib.request.Request(url, headers={'User-Agent': 'lager-cli'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status != 200:
                    invalid_packages.append(pkg)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                invalid_packages.append(pkg)
        except Exception:
            # Network error or timeout - skip validation for this package
            pass

    return invalid_packages

def _install_packages_in_container(ctx, box):
    """Install packages from user_requirements.txt inside the running container"""
    import json
    import tempfile

    click.secho('\nInstalling packages in container...', fg='blue')

    try:
        # Create a Python script to install packages via pip
        script_content = """
import subprocess
import json
import os

requirements_file = '/etc/lager/user_requirements.txt'

try:
    if not os.path.exists(requirements_file):
        print('No user requirements file found')
        print(json.dumps({'status': 'success', 'installed': 0}))
        exit(0)

    # Read requirements file
    with open(requirements_file, 'r') as f:
        content = f.read()

    # Count non-comment, non-empty lines
    packages = [line.strip() for line in content.splitlines()
                if line.strip() and not line.strip().startswith('#')]

    if not packages:
        print('No packages to install')
        print(json.dumps({'status': 'success', 'installed': 0}))
        exit(0)

    print(f'Installing {len(packages)} package(s)...', flush=True)

    # Run pip install
    result = subprocess.run(
        ['pip3', 'install', '-r', requirements_file],
        capture_output=False,
        timeout=300
    )

    if result.returncode == 0:
        print(json.dumps({'status': 'success', 'installed': len(packages)}))
    else:
        print(json.dumps({'status': 'error', 'message': 'pip install failed'}))
        exit(1)

except subprocess.TimeoutExpired:
    print(json.dumps({'status': 'error', 'message': 'Installation timed out'}))
    exit(1)
except Exception as e:
    print(json.dumps({'status': 'error', 'message': str(e)}))
    exit(1)
"""

        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(script_content)
            temp_script = f.name

        try:
            # Run the script and stream output to user
            run_python_internal(
                ctx,
                temp_script,
                box,
                image='',
                env=(),
                passenv=(),
                kill=False,
                download=(),
                allow_overwrite=False,
                signum='SIGTERM',
                timeout=600,  # 10 minute timeout for package installation
                detach=False,
                port=(),
                org=None,
                args=(),
            )

            click.secho('\nPackages installed successfully!', fg='green')
            click.secho('Note: Packages are installed in the running container.', fg='yellow')
            click.secho('      To persist after container restart, rebuild with: lager update --box ' + box, fg='yellow')
            return True

        finally:
            # Clean up temp file
            os.unlink(temp_script)

    except Exception as e:
        click.secho(f'\nFailed to install packages: {e}', fg='red', err=True)
        return False

@click.group()
def pip():
    """Manage pip packages in the python container"""
    pass

@pip.command()
@click.pass_context
@click.option("--box", 'box', required=False, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt and install immediately')
@click.argument('packages', nargs=-1, required=True)
def install(ctx, box, yes, packages):
    """Install packages into the python container

    This command adds packages to the box's package list and installs them.
    Note: Packages persist in /etc/lager but need reinstall after container restart.

    Examples:
        lager pip install pandas
        lager pip install numpy==1.24.0
        lager pip install scipy matplotlib
    """
    from ...box_storage import resolve_and_validate_box

    # Resolve and validate the box name
    target = resolve_and_validate_box(ctx, box)

    # Read current requirements from box
    current_packages = _read_remote_requirements(ctx, target)
    current_names = {_normalize_package_name(pkg) for pkg in current_packages}

    # Add new packages (avoid duplicates)
    new_packages = []
    for pkg in packages:
        pkg_name = _normalize_package_name(pkg)
        if pkg_name not in current_names:
            new_packages.append(pkg)
            current_packages.append(pkg)
            current_names.add(pkg_name)
            click.secho(f'Adding {pkg} to package list', fg='green')
        else:
            click.secho(f'Package {pkg} already in package list', fg='yellow')

    if not new_packages:
        click.secho('No new packages to install', fg='yellow')
        return

    # Validate packages exist on PyPI before modifying files
    click.secho('\nValidating packages on PyPI...', fg='blue')
    invalid_packages = _validate_packages(new_packages)

    if invalid_packages:
        click.secho('\nError: The following packages do not exist on PyPI:', fg='red', err=True)
        for pkg in invalid_packages:
            click.secho(f'  - {pkg}', fg='red', err=True)
        click.secho('\nNo changes were made. Please check package names and try again.', fg='yellow', err=True)
        sys.exit(1)

    click.secho('All packages validated', fg='green')

    # Write updated requirements to box
    _write_remote_requirements(ctx, target, current_packages)

    click.secho('\nPackages added to list', fg='green')

    # Prompt user to install packages (skip prompt if --yes flag)
    if yes or click.confirm('\nInstall packages in container now?', default=True):
        if _install_packages_in_container(ctx, target):
            click.secho('Packages are now available.', fg='green')
        else:
            click.secho(f'To install later, run:', fg='yellow')
            click.secho(f'  lager pip apply --box {target}', fg='yellow')
    else:
        click.secho('\nTo install later, run:', fg='blue')
        click.secho(f'  lager pip apply --box {target}', fg='blue')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
def list(ctx, box):
    """List user-installed packages

    Shows packages that have been installed via 'lager pip install'.
    These packages persist across container restarts.
    """
    from ...box_storage import resolve_and_validate_box

    # Resolve and validate the box name
    target = resolve_and_validate_box(ctx, box)

    # Read packages from box
    packages = _read_remote_requirements(ctx, target)

    if not packages:
        click.secho('No user-installed packages found', fg='yellow')
        click.secho('\nTo install packages permanently:', fg='blue')
        click.secho('  lager pip install <package-name>', fg='blue')
        return

    click.secho('User-installed packages:', fg='green')
    for pkg in packages:
        click.echo(f'  {pkg}')

    click.secho(f'\nTotal: {len(packages)} package(s)', fg='blue')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
@click.argument('packages', nargs=-1, required=True)
def uninstall(ctx, box, yes, packages):
    """Uninstall packages from the python container

    Removes packages from the package list. Note: To fully remove packages
    from the running container, the container must be restarted.

    Examples:
        lager pip uninstall pandas
        lager pip uninstall numpy scipy
    """
    from ...box_storage import resolve_and_validate_box

    # Resolve and validate the box name
    target = resolve_and_validate_box(ctx, box)

    # Read current requirements from box
    current_packages = _read_remote_requirements(ctx, target)

    if not current_packages:
        click.secho('No user-installed packages found', fg='yellow')
        return

    # Normalize package names for removal
    packages_to_remove = {_normalize_package_name(pkg) for pkg in packages}

    # Filter out packages to remove
    removed = []
    remaining = []
    for pkg in current_packages:
        pkg_name = _normalize_package_name(pkg)
        if pkg_name in packages_to_remove:
            removed.append(pkg)
            click.secho(f'Removing {pkg} from package list', fg='green')
        else:
            remaining.append(pkg)

    if not removed:
        click.secho('No matching packages found in package list', fg='yellow')
        return

    # Write updated requirements to box
    _write_remote_requirements(ctx, target, remaining)

    click.secho(f'\nRemoved {len(removed)} package(s) from package list', fg='green')
    click.secho('Note: Packages are removed from the list. To fully remove from the', fg='yellow')
    click.secho('      running container, restart it with: lager update --box ' + target, fg='yellow')

@pip.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
def apply(ctx, box, yes):
    """Install packages from the package list into the running container

    Use this command to install packages after using 'lager pip install'
    when you chose not to install immediately.

    Examples:
        lager pip apply --box TEST-2
        lager pip apply --box TEST-2 --yes
    """
    from ...box_storage import resolve_and_validate_box

    # Resolve and validate the box name
    target = resolve_and_validate_box(ctx, box)

    # Read current packages to show what will be installed
    packages = _read_remote_requirements(ctx, target)

    if packages:
        click.secho(f'Package list ({len(packages)} package(s)):', fg='blue')
        for pkg in packages:
            click.echo(f'  {pkg}')
    else:
        click.secho('No packages in package list', fg='yellow')
        return

    # Confirm installation unless --yes flag is used
    if not yes:
        if not click.confirm('\nInstall packages now?', default=True):
            click.secho('Installation cancelled', fg='yellow')
            return

    # Install packages
    if _install_packages_in_container(ctx, target):
        click.secho('Packages are now available.', fg='green')
    else:
        click.secho('Package installation failed', fg='red', err=True)
        sys.exit(1)
