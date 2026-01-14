import csv
import logging
from collections import Counter
from datetime import datetime

from icat_plus_client.models.investigation import Investigation

from data import dataset, instrument, investigation

logger = logging.getLogger(__name__)


def get_techniques_by_investigation_cli(token: str, start_date: str, end_date: str) -> None:
    """
    Generate a report of datasets and techniques per beamline within a date range.

    The report includes:
        - Number of experimental sessions
        - Number of datasets with non default techniques
        - Comma-separated list of unique techniques
        - Counts per technique

    :param token: ICAT session token for authentication.
    :param start_date: Start date for filtering investigations.
    :param end_date: End date for filtering investigations.

    """
    investigations = investigation.get_investigation_by_id(
        token,
        start_date,
        end_date,
    )
    results = []

    nb_datasets, techniques, technique_count = get_techniques_by_investigation(
        token=token, investigations=investigations, start_date=start_date, end_date=end_date
    )
    technique_count_str = "; ".join(f"{k}:{v}" for k, v in technique_count.items())
    results.append(
        {
            "beamline": "",
            "nb_exp_sessions": len(investigations),
            "nb_datasets": nb_datasets,
            "techniques": techniques,
            "technique_count": technique_count_str,
        }
    )
    return results


def get_techniques_by_beamlines(token: str, start_date: str, end_date: str) -> None:
    """
    Generate a report of datasets and techniques per beamline within a date range.

    The report includes:
        - Number of experimental sessions
        - Number of datasets with non default techniques
        - Comma-separated list of unique techniques
        - Counts per technique

    :param token: ICAT session token for authentication.
    :param start_date: Start date for filtering investigations.
    :param end_date: End date for filtering investigations.

    """
    instruments = instrument.get_instruments()
    results = []

    for inst in instruments:
        logger.info(f"Processing beamline {inst.name}...")
        investigations = investigation.get_investigation_by_id(
            session_id=token,
            instrument_name=inst.name,
            start_date=start_date,
            end_date=end_date,
        )
        nb_datasets, techniques, technique_count = get_techniques_by_investigation(
            token=token, investigations=investigations, start_date=start_date, end_date=end_date
        )
        technique_count_str = "; ".join(f"{k}:{v}" for k, v in technique_count.items())
        results.append(
            {
                "beamline": inst.name,
                "nb_exp_sessions": len(investigations),
                "nb_datasets": nb_datasets,
                "techniques": techniques,
                "technique_count": technique_count_str,
            }
        )
    return results


def write_csv(data: list[dict[str, str]], csv_file: str) -> None:
    fields = [
        "beamline",
        "nb_exp_sessions",
        "nb_datasets",
        "techniques",
        "technique_count",
    ]
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=",")
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def get_techniques_by_investigation(
    token: str, investigations: list[Investigation], start_date: str, end_date: str
) -> tuple[int, str, dict[str, int]]:
    """
    Count datasets and techniques for a list of investigations,
    excluding the default XRAYS technique.
    :param token: ICAT session token.
    :param investigations: List of investigations.

    :return: A tuple containing:
             - nb_datasets: Number of datasets with at least one non-XRAYS technique.
             - techniques_str: Comma-separated list of unique technique names.
             - technique_count: Dictionary mapping technique and dataset count.
    """
    if not investigations:
        return 0, "", {}
    default_techniques = {
        "http://purl.org/pan-science/ESRFET#XRAYS",
        "http://purl.org/pan-science/ESRFET#EM",
    }
    nb_datasets = 0
    all_techniques = []
    start_dt = datetime.fromisoformat(start_date).date()
    end_dt = datetime.fromisoformat(end_date).date()

    for inv in investigations:
        datasets = dataset.get_datasets(token, investigation_ids=str(inv.id))
        for ds in datasets:
            ds_date = datetime.fromisoformat(ds.start_date).date()
            if not (start_dt <= ds_date <= end_dt):
                continue
            techniques = ds.techniques
            non_xrays_techniques = []
            for t in techniques:
                if t.pid in default_techniques:
                    continue
                short_name = t.name.split(",")[0].strip()
                non_xrays_techniques.append(short_name)
            if non_xrays_techniques:
                nb_datasets += 1
                all_techniques.extend(non_xrays_techniques)

    technique_count = dict(sorted(Counter(all_techniques).items()))
    techniques_str = "; ".join(technique_count.keys())

    return nb_datasets, techniques_str, technique_count
