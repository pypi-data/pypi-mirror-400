import typer

from authentication.cli import authentication_app
from config.cli import config_app
from invoicing.cli import invoicing_app
from performance.cli import performance_app
from stats.cli import statistics_app

app = typer.Typer(help="ICAT+ CLI")

# Sub-Typer for commands
login_app = typer.Typer(help="Allows users to log in and retrieve token information")

app.add_typer(login_app, name="login")
app.add_typer(invoicing_app, name="invoicing")
app.add_typer(config_app, name="config")
app.add_typer(authentication_app, name="login")
app.add_typer(performance_app, name="performance")
app.add_typer(statistics_app, name="statistics")


def main():
    app()


if __name__ == "__main__":
    main()

click_app = typer.main.get_command(app)
