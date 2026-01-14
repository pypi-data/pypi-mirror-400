import csv
import sys
from datetime import datetime

import typer

from data.investigation import get_investigation_by_id
from logger_utils.time_formatter import format_date
from stats.datasets import calculate_acquisition_time
from stats.samples import count_samples_with_datasets
from stats.volume import volume

volume_statistics_app = typer.Typer(help="Volume related commands for statistics")


@volume_statistics_app.command("investigations", help="Generates volume statistics per investigation.")
def get_sample_count_by_investigation_cli(
    token: str = typer.Option(..., "-t", "--token", help="ICAT session id"),
    instrument_name: str | None = typer.Option(None, help="Filter by instrument name"),
    investigation_name: str | None = typer.Option(None, help="Comma-separated list of investigation names"),
    start_date: str = typer.Option(
        None,
        "-s",
        "--start_date",
        help="Start date range. Format is YYYY-MM-DD. Example: 2019-01-01",
    ),
    end_date: str = typer.Option(
        None,
        "-e",
        "--end_date",
        help="End date range. Format is YYYY-MM-DD. Example: 2019-01-01",
    ),
    csv_file: str | None = typer.Option(
        None,
        "--csv",
        help="Optional CSV file to write the output to. Defaults to stdout.",
    ),
):
    investigations = get_investigation_by_id(
        token,
        investigation_name,
        instrument_name,
        start_date,
        end_date,
    )

    fields = [
        "proposal",
        "beamline",
        "start_date",
        "end_date",
        "investigation_id",
        "samples",
        "scheduled_time",
        "file_count",
        "dataset_count",
        "processed_dataset_count",
        "acquisition_dataset_count",
        "effective_acquisition_time",
        "effective_acquisition_time_seconds",
    ]
    output = open(csv_file, "w", newline="", encoding="utf-8") if csv_file else sys.stdout

    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    for inv in investigations:
        duration_time_delta = calculate_acquisition_time(token, inv.id, 20)
        writer.writerow(
            {
                "proposal": inv.name,
                "beamline": inv.instrument.name,
                "start_date": format_date(inv.start_date),
                "end_date": format_date(inv.end_date),
                "investigation_id": inv.id,
                "samples": count_samples_with_datasets(token, inv.id),
                "scheduled_time": (
                    datetime.fromisoformat(inv.end_date) - datetime.fromisoformat(inv.start_date)
                    if inv.end_date is not None
                    else 0
                ),
                "file_count": inv.parameters.get("__fileCount"),
                "dataset_count": inv.parameters.get("__datasetCount"),
                "processed_dataset_count": inv.parameters.get("__procesedDatasetCount"),
                "acquisition_dataset_count": inv.parameters.get("__acquisitionDatasetCount"),
                "effective_acquisition_time": duration_time_delta,
                "effective_acquisition_time_seconds": (
                    duration_time_delta.total_seconds() if duration_time_delta is not None else 0
                ),
            }
        )


@volume_statistics_app.command(
    "beamline",
    help="""
    Generates volume statistics for all instruments over a date range.

    Example usage:

    .. code-block:: bash

       minedrac statistics volume beamline -t <TOKEN> -s 2023-01-01 -e 2023-12-31 --unit GB
                               """,
)
def statistics_volume_beamline(
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
    unit: str = typer.Option(
        None,
        "-u",
        "--unit",
        help="It can be MB, DB or TB (otherwise will return in bytes)",
    ),
    output: str = typer.Option(
        None,
        "-o",
        "--output",
        help="CSV output file path. Example: myfile.csv",
    ),
):
    """
    Example usage:

    .. code-block:: bash

       minedrac statistics volume beamline -t <TOKEN> -s 2023-01-01 -e 2023-12-31 --unit GB
    """
    # Default to bytes if no units provided
    unit = unit if unit is not None else "bytes"
    volume.get_volume_by_beamlines(token, start_date, end_date, unit, output)


@volume_statistics_app.command("heatmap", help="Show volume statistics per beamline and year")
def statistics_volume_heatmap(
    token: str = typer.Option(..., "-t", "--token", help="ICAT token"),
    start_year: int = typer.Option(
        ...,
        "-s",
        "--start_year",
        help="Start year range. Format is YYYY. Example: 2019",
    ),
    end_year: int = typer.Option(
        ...,
        "-e",
        "--end_year",
        help="End date range. Format is YYYY. Example: 2019",
    ),
    unit: str = typer.Option(
        None,
        "-u",
        "--unit",
        help="It can be MB, DB or TB (otherwise will return in bytes)",
    ),
    output: str = typer.Option(
        None,
        "-o",
        "--output",
        help="CSV output file path. Example: myfile.csv",
    ),
):
    # Default to bytes if no units provided
    unit = unit if unit is not None else "bytes"
    volume.get_volume_by_instrument_year(token, start_year, end_year, unit, output)


@volume_statistics_app.command("year", help="Show volume statistics per year")
def statistics_volume_year(
    token: str = typer.Option(..., "-t", "--token", help="ICAT token"),
    start_year: int = typer.Option(
        ...,
        "-s",
        "--start_year",
        help="Start year range. Format is YYYY. Example: 2019",
    ),
    end_year: int = typer.Option(
        ...,
        "-e",
        "--end_year",
        help="End date range. Format is YYYY. Example: 2019",
    ),
    unit: str = typer.Option(
        None,
        "-u",
        "--unit",
        help="It can be MB, DB or TB (otherwise will return in bytes)",
    ),
):
    # Default to bytes if no units provided
    unit = unit if unit is not None else "bytes"
    volume.get_volume_by_year(token, start_year, end_year, unit)


click_volume_statistics_app = typer.main.get_command(volume_statistics_app)
