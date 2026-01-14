"""
    lager.commands.box.hello

    Say hello to box
"""
import click
from ...context import get_impl_path
from ..development.python import run_python_internal
from ...box_storage import resolve_and_validate_box_with_name

@click.command()
@click.pass_context
@click.option("--box", required=False, help="Lagerbox name or IP")
def hello(ctx, box):
    """Test box connectivity"""
    # Resolve and validate the box, keeping track of the original name
    original_box_name = box  # Save for username lookup
    resolved_box, box_name = resolve_and_validate_box_with_name(ctx, box)

    run_python_internal(
        ctx,
        get_impl_path('hello.py'),
        resolved_box,
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
        args=(resolved_box,),  # Pass the resolved IP as an argument
        dut_name=box_name,  # Pass box name for username lookup
    )
