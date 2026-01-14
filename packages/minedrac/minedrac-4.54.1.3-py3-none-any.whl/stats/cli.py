import typer

from stats.technique.cli import technique_statistics_app
from stats.volume.cli import volume_statistics_app

statistics_app = typer.Typer(help="Statistics related commands")

# Sub-Typer for commands
statistics_app.add_typer(technique_statistics_app, name="technique")
statistics_app.add_typer(volume_statistics_app, name="volume")


# For click documentation
click_statistics_app = typer.main.get_command(statistics_app)
