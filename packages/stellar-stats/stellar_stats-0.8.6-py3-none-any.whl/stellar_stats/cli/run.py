import os

import click
import streamlit.web.bootstrap as bootstrap
from streamlit.web.cli import configurator_options


def run_streamlit(file_path, args=None, **kwargs):
    """
    Run a Streamlit app with proper context initialization
    """
    if args is None:
        args = []

    # Initialize bootstrap configuration
    bootstrap.load_config_options(flag_options=kwargs)

    # Run the Streamlit app
    bootstrap.run(file_path, is_hello=False, args=args, flag_options=kwargs)


@click.command()
@click.argument("args", nargs=-1)
@configurator_options
def run(args, **kwargs):
    """Run the Streamlit application"""
    dirname = os.path.dirname(os.path.dirname(__file__))
    filepath = os.path.join(dirname, "app.py")
    run_streamlit(filepath, args=args, **kwargs)