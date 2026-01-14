import typer

from config import ICAT_PLUS_SERVER

config_app = typer.Typer(help="Configuration settings")


@config_app.command("settings", help="Prints the configuration settings")
def settings():
    typer.echo(f"icat_plus_server = {ICAT_PLUS_SERVER}")


click_config_app = typer.main.get_command(config_app)
