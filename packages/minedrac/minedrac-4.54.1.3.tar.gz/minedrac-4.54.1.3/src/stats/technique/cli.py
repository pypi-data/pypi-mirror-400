import json

import pandas as pd
import typer

from data import session
from stats.technique import technique

technique_statistics_app = typer.Typer(help="Technique related commands for statistics")


def validate_token(token: str):
    session_response = session.get_info(token)
    if session_response is None:
        typer.echo(" Invalid or expired token. Exiting.")
        raise typer.Exit(code=1)


@technique_statistics_app.command("investigation", help="Gets technique statistics per investigation")
def statistics_technique_investigation(
    token: str = typer.Option(..., "-t", "--token", help="ICAT token"),
    start_date: str = typer.Option(
        ...,
        "-s",
        "--start_date",
        help="Start date range. Format is YYYY-MM-DD. Example: 2019-01-01",
    ),
    end_date: str = typer.Option(
        ...,
        "-e",
        "--end_date",
        help="End date range. Format is YYYY-MM-DD. Example: 2019-01-01",
    ),
    output_format: str = typer.Option(
        "csv",
        "-f",
        "--format",
        help="Output format: csv | json | stdout",
    ),
    output_file: str = typer.Option(
        None,
        "-o",
        "--output",
        help="Output filepath",
    ),
):
    validate_token(token)
    data = technique.get_techniques_by_investigation_cli(token, start_date, end_date)
    if output_format == "csv":
        if not output_file:
            raise typer.BadParameter("You must provide --output when format=csv")
        technique.write_csv(data, output_file)
    elif output_format == "json":
        if output_file:
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
        else:
            print(json.dumps(data, indent=2))

    elif output_format == "stdout":
        df = pd.DataFrame(data)
        print(df)

    else:
        raise typer.BadParameter("Invalid format. csv | json | stdout")


@technique_statistics_app.command("beamline", help="Gets technique statistics per beamline")
def statistics_technique_beamline(
    token: str = typer.Option(..., "-t", "--token", help="ICAT token"),
    start_date: str = typer.Option(
        ...,
        "-s",
        "--start_date",
        help="Start date range. Format is YYYY-MM-DD. Example: 2019-01-01",
    ),
    end_date: str = typer.Option(
        ...,
        "-e",
        "--end_date",
        help="End date range. Format is YYYY-MM-DD. Example: 2019-01-01",
    ),
    output_format: str = typer.Option(
        "csv",
        "-f",
        "--format",
        help="Output format: csv | json | stdout",
    ),
    output_file: str = typer.Option(
        None,
        "-o",
        "--output",
        help="Output filepath",
    ),
):
    validate_token(token)
    data = technique.get_techniques_by_beamlines(token, start_date, end_date)
    if output_format == "csv":
        if not output_file:
            raise typer.BadParameter("You must provide --output when format=csv")
        technique.write_csv(data, output_file)
    elif output_format == "json":
        if output_file:
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
        else:
            print(json.dumps(data, indent=2))

    elif output_format == "stdout":
        df = pd.DataFrame(data)
        print(df)

    else:
        raise typer.BadParameter("Invalid format. csv | json | stdout")


click_technique_statistics_app = typer.main.get_command(technique_statistics_app)
