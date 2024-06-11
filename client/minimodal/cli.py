import subprocess

import click

from . import client


@click.group()
def cli():
    click.echo("🚀 launching minimodal CLI")


@click.argument("file")
@cli.command()
def run(file):
    """Runs the provided file, coordinating remote calls to minimodal."""
    click.echo("🐴 mounting file on minimodal")
    app = client.App()
    try:
        app.mount(file)
    except Exception as e:
        click.echo(f"❌ failed to mount file: {e}")
        return
    click.echo("👟 running app locally")
    subprocess.run(["python", file])
