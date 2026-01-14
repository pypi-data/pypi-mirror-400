import csv
import sys
from collections.abc import Callable
from functools import wraps

from icat_plus_client.models.investigation import Investigation

from data import instrument, investigation
from stats import investigation_parameters


def get_volumes_by_investigation(
    investigations: list[Investigation], unit: str = "bytes"
) -> tuple[float, float, float]:
    """
    Returns the total volumes (__volume, __acquisitionVolume, __processedVolume)
    converted into the desired unit, truncated to 2 decimal places.

    Args:
        investigations (list): List of investigations.
        unit (str): "bytes", "MB", "GB", or "TB". Default is "bytes".

    Returns:
        tuple(float, float, float): Volumes in the requested unit.
    """
    conversion = {
        "bytes": 1,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
    }

    if unit not in conversion:
        raise ValueError(f"Invalid unit '{unit}'. Use one of {list(conversion.keys())}.")

    def truncate(number: float, digits: int = 2) -> float:
        stepper = 10.0**digits
        return int(number * stepper) / stepper

    if investigations is not None:
        __volume = investigation_parameters.sum_investigation_parameter(investigations, "__volume")
        __acquisitionVolume = investigation_parameters.sum_investigation_parameter(
            investigations, "__acquisitionVolume"
        )
        __processedVolume = investigation_parameters.sum_investigation_parameter(
            investigations, "__processedVolume"
        )

        factor = conversion[unit]
        return (
            int(truncate(__volume / factor, 2)),
            int(truncate(__acquisitionVolume / factor, 2)),
            int(truncate(__processedVolume / factor, 2)),
        )

    return 0.0, 0.0, 0.0


def yearly_csv(fields: list[str] | None = None, delimiter: str = "\t"):
    """
    Decorator to generate CSV per year.
    The decorated function should have signature:
        func(token: str, year: int, unit: str) -> Dict[str, float]
    """

    def decorator(func: Callable[[str, int, str], dict[str, float]]):
        @wraps(func)
        def wrapper(token: str, start_year: int, end_year: int, unit: str = ""):
            writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter=delimiter)
            writer.writeheader()

            for year in range(start_year, end_year + 1):
                row = func(token, year, unit)
                writer.writerow(row)

        return wrapper

    return decorator


def get_datasets_count_by(investigations: list[Investigation]) -> float:
    return investigation_parameters.sum_investigation_parameter(investigations, "__datasetCount")


@yearly_csv(fields=["year", "dataset_count"])
def get_datasets_by_year(token: str, year: int, unit: str) -> dict[str, float]:
    investigations: list[Investigation] = investigation.get_investigation_by_id(
        session_id=token,
        start_date=f"{year}-01-01",
        end_date=f"{year}-12-31",
    )
    dataset_count = get_datasets_count_by(investigations=investigations)
    return {
        "year": year,
        "dataset_count": dataset_count,
    }


@yearly_csv(fields=["year", "total_volume", "raw_volume", "processed_volume"])
def get_volume_by_year(token: str, year: int, unit: str) -> dict[str, float]:
    investigations = investigation.get_investigation_by_id(
        session_id=token,
        start_date=f"{year}-01-01",
        end_date=f"{year}-12-31",
    )
    total_volume, raw_volume, processed_volume = get_volumes_by_investigation(
        investigations=investigations, unit=unit
    )
    return {
        "year": year,
        "total_volume": total_volume,
        "raw_volume": raw_volume,
        "processed_volume": processed_volume,
    }


def get_volume_by_beamlines(token: str, start_date: str, end_date: str, unit: str, output: str):
    instruments = instrument.get_instruments()
    fields = [
        "beamline",
        "total_volume",
        "raw_volume",
        "processed_volume",
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter="\t")
    writer.writeheader()

    file_writer = None
    f = None
    if output:
        f = open(output, "w", newline="")
        file_writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        file_writer.writeheader()

    for ins in instruments:
        investigations = investigation.get_investigation_by_id(
            session_id=token,
            instrument_name=ins.name,
            start_date=start_date,
            end_date=end_date,
        )
        [total_volume, acquisition_volume, processed_volume] = get_volumes_by_investigation(
            investigations=investigations, unit=unit
        )

        row = {
            "beamline": ins.name,
            "total_volume": total_volume,
            "raw_volume": acquisition_volume,
            "processed_volume": processed_volume,
        }

        writer.writerow(
            {
                "beamline": ins.name,
                "total_volume": total_volume,
                "raw_volume": acquisition_volume,
                "processed_volume": processed_volume,
            }
        )
        if file_writer:
            file_writer.writerow(row)


def get_volume_by_instrument_year(token: str, start_year: int, end_year: int, unit: str, output: str):
    instruments = instrument.get_instruments()
    # Build CSV fields: first "year", then each instrument's name
    fields = ["year"] + [ins.name for ins in instruments]

    writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter="\t")
    writer.writeheader()

    for year in range(start_year, end_year + 1):
        row = {"year": year}  # Start with the year
        for ins in instruments:
            # Get all investigations in the date range
            investigations = investigation.get_investigation_by_id(
                session_id=token,
                start_date=f"{year}-01-01",
                end_date=f"{year}-12-31",
                instrument_name=ins.name,
            )
            [total_volume, acquisition_volume, processed_volume] = get_volumes_by_investigation(
                investigations=investigations, unit=unit
            )
            # Add total_volume to the row under the instrument name
            row[ins.name] = total_volume
        writer.writerow(row)
