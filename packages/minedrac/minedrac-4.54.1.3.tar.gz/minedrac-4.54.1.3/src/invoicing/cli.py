import csv
import sys
from datetime import datetime

import typer

from data import dataset, investigation
from data.parcel import get_declared_samples_by, get_parcels_by
from invoicing import duration
from stats.volume.volume import get_volumes_by_investigation

invoicing_app = typer.Typer(help="Create usage statistics for invoicing industrial clients")


@invoicing_app.command("report", help="Generates a invoicing report")
def invoicing_report(
    token: str = typer.Option(..., "-t", "--token", help="ICAT session ID"),
    investigation_ids: str | None = typer.Option(
        None,
        "--investigation-ids",
        "-i",
        help="Comma separated list of investigation IDs (optional)",
    ),
    instrument_name: str | None = typer.Option(None, help="Filter by instrument name"),
    investigation_name: str | None = typer.Option(None, help="Filter by instrument name"),
    start_date: str = typer.Option(
        None,
        "-s",
        "--start-date",
        help="Start date range. Format is YYYY-MM-DD. Example: 2019-01-01",
    ),
    end_date: str = typer.Option(
        None,
        "-e",
        "--end-date",
        help="End date range. Format is YYYY-MM-DD. Example: 2019-01-01",
    ),
    unit: str = typer.Option(
        "GB",
        "-u",
        "--unit",
        help="It can be MB, GB or TB (otherwise will return in GB)",
    ),
    merge_gap_minutes: int = typer.Option(
        20,
        "-g",
        "--gap",
        help="Gap in minutes to merge datasets. Less than 'gap' minutes the datasets time will be merged",
    ),
    output: str = typer.Option(
        None,
        "-o",
        "--output",
        help="CSV output file path. Example: myfile.csv",
    ),
    log: str = typer.Option(
        None,
        "-l",
        "--log",
        help="CSV log output file path. Example: myfile_log.csv",
    ),
    ignore_longer_than: int = typer.Option(
        None,
        "-ig",
        "--ignore",
        help="The time in hours that will be taken into account to omit a dataset as considered an error.",
    ),
):
    investigations = investigation.get_investigation_by_id(
        session_id=token,
        investigation_id=investigation_ids,
        start_date=start_date,
        end_date=end_date,
        instrument_name=instrument_name,
        investigation_name=investigation_name,
    )

    fields = [
        "proposal",
        "investigation_id",
        "beamline",
        "start_date",
        "end_date",
        "booked_time",
        "samples_collected",
        "samples_declared",
        "parcels",
        "volume",
        "raw_volume",
        "processed_volume",
        "effective_time",
        "total_time",
    ]

    writers = [csv.DictWriter(sys.stdout, fieldnames=fields, delimiter="\t")]
    # If file provided, also write to the file
    if output:
        f = open(output, "w", newline="")
        writers.append(csv.DictWriter(f, fieldnames=fields, delimiter="\t"))
    else:
        f = None

    # Write headers on all writers
    for w in writers:
        w.writeheader()

    for inv in investigations:
        (total, raw, processed) = get_volumes_by_investigation([inv], unit)
        samples_declared = get_declared_samples_by(token, str(inv.id))
        parcels = get_parcels_by(token, str(inv.id))
        start = datetime.fromisoformat(inv.start_date)
        end = datetime.fromisoformat(inv.end_date) if inv.end_date is not None else start
        row = {
            "proposal": inv.name,
            "investigation_id": inv.id,
            "beamline": inv.instrument.name,
            "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": end.strftime("%Y-%m-%d %H:%M:%S"),
            "booked_time": end - start,
            "volume": f"{total} {unit}",
            "raw_volume": f"{raw} {unit}",
            "processed_volume": f"{processed} {unit}",
        }

        """Calculate total dataset duration for a session."""
        datasets = dataset.get_datasets(
            token=token,
            investigation_ids=str(inv.id),
            dataset_type="acquisition",
        )

        samples_collected = sorted({d.sample_name for d in datasets if getattr(d, "sample_name", None)})
        row["samples_collected"] = len(samples_collected)
        row["samples_declared"] = len(samples_declared)
        row["parcels"] = len(parcels)
        row["total_time"] = duration.sum_dataset_durations(
            datasets, merge_gap_minutes, log, ignore_longer_than
        )
        row["effective_time"] = duration.sum_dataset_durations(datasets, 0, None, ignore_longer_than)

        for w in writers:
            w.writerow(row)


click_invoicing_app = typer.main.get_command(invoicing_app)
