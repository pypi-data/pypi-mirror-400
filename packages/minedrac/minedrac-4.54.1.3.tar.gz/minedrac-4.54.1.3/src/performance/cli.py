import csv
import os
import random
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps

import typer
from icat_plus_client.models.session import Session

from data import dataset, investigation, sample, session

performance_app = typer.Typer(help="Performance workbench commands")


def get_role(user: Session):
    if user.is_administrator:
        return "administrator"
    if user.is_instrument_scientist:
        return "instrumentScientist"
    return "user"


# Decorator to measure execution time
def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        return result, round(duration)

    return wrapper


@timed
def get_timed_datasets(**kwargs):
    return dataset.get_datasets(**kwargs)


@timed
def get_timed_samples(**kwargs):
    return sample.get_samples_by(**kwargs)


def get_timed_dataset_by_samples(**kwargs):
    return sample.get_samples_by(**kwargs)


def workbench(
    fetch_fn,
    result_label: str,
    *,
    random_seed: int = 42,
    cooldown_seconds: float = 0,
    skip_range=(0, 100),
    limit_range=(100, 200),
    x: int = 1,
    y: int = 1,
):
    """
    Generic benchmark decorator.

    fetch_fn: timed callable (get_timed_datasets / get_timed_samples)
    result_label: CSV column name ('datasets' / 'samples')
    """

    def decorator(func):
        @wraps(func)
        def wrapper(
            tokens: str | None = typer.Option(
                None, "-t", "--token", help="Comma separated list of ICAT tokens"
            ),
            credentials: str | None = typer.Option(
                ..., "-c", "--credentials", help="Example: user1,password1:user2,password2"
            ),
            investigation_ids: str | None = typer.Option(None, "-i", "--investigation-ids"),
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
            skip_count: int | None = typer.Option(
                3,
                "-k",
                "--skip-count",
                help="Number of skip variations",
            ),
            limit_count: int | None = typer.Option(
                3,
                "-l",
                "--limit-count",
                help="Number of limit variations",
            ),
            output: str | None = typer.Option(None, "-o", "--output"),
        ):
            user_tokens = []
            if tokens is not None:
                user_tokens = tokens.split(",")
            else:
                if credentials is not None:
                    users_credentials = credentials.split(":")
                    for user_credentials in users_credentials:
                        username = user_credentials.split(",")[0]
                        password = user_credentials.split(",")[1]

                        token = session.get_session("db", username, password)
                        user_tokens.append(token)

            investigation_id_list = []

            if investigation_ids is not None:
                investigation_id_list = investigation_ids.split(",")
            else:
                investigations = investigation.get_investigation_by_id(
                    user_tokens[0], start_date=start_date, end_date=end_date
                )
                investigation_id_list = [i.id for i in investigations]

            role_timings = defaultdict(list)

            random.seed(random_seed)

            # --------------------------------------------------------------
            # Build randomized calls
            # --------------------------------------------------------------
            calls = []
            for investigation_id in investigation_id_list:
                for _ in range(skip_count):
                    skip = str(random.randint(*skip_range))
                    for _ in range(limit_count):
                        limit = str(random.randint(*limit_range))
                        for token in user_tokens:
                            calls.append(
                                {
                                    "token": token,
                                    "investigation_id": investigation_id,
                                    "skip": skip,
                                    "limit": limit,
                                }
                            )

            random.shuffle(calls)

            # --------------------------------------------------------------
            # Execute benchmark
            # --------------------------------------------------------------
            for call in calls:
                token = call["token"]
                investigation_id = call["investigation_id"]
                skip = call["skip"]
                limit = call["limit"]

                user_session: Session = session.get_info(token)
                role = get_role(user_session.user)

                result, duration = fetch_fn(
                    token=token,
                    investigation_ids=investigation_id,
                    limit=limit,
                    skip=skip,
                )

                role_timings[role].append(duration)

                print(
                    f"Role: {role} | "
                    f"user={user_session.user.username} | "
                    f"investigation_id={investigation_id} | "
                    f"skip={skip} | "
                    f"limit={limit} | "
                    f"{result_label}={len(result)} | "
                    f"time(ms)={duration} "
                )

                time.sleep(cooldown_seconds)

            # --------------------------------------------------------------
            # Statistics
            # --------------------------------------------------------------
            print("\n=== Benchmark statistics per role ===\n")
            ROLES = ["user", "instrumentScientist", "administrator"]

            fields = ["date"]
            for role in ROLES:
                fields.extend(
                    [
                        f"{role}_count",
                        f"{role}_avg",
                        f"{role}_min",
                        f"{role}_max",
                        f"{role}_std",
                    ]
                )

            stdout_writer = csv.DictWriter(sys.stdout, fieldnames=fields, delimiter="\t")
            stdout_writer.writeheader()

            if output:
                file_exists = os.path.exists(output)

                f = open(output, "a", newline="")
                file_writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")

                if not file_exists:
                    file_writer.writeheader()

            row = {}
            for role in ROLES:
                times = role_timings.get(role, [])

                if len(times) < 2:
                    row.update(
                        {
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            f"{role}_count": "",
                            f"{role}_avg": "",
                            f"{role}_min": "",
                            f"{role}_max": "",
                            f"{role}_std": "",
                        }
                    )
                    continue

                row.update(
                    {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        f"{role}_count": len(times),
                        f"{role}_avg": f"{statistics.mean(times):.2f}",
                        f"{role}_min": f"{min(times):.2f}",
                        f"{role}_max": f"{max(times):.2f}",
                        f"{role}_std": f"{statistics.stdev(times):.2f}",
                    }
                )

            stdout_writer.writerow(row)
            if file_writer:
                file_writer.writerow(row)

        return wrapper

    return decorator


@performance_app.command("dataset")
@workbench(
    fetch_fn=get_timed_datasets,
    result_label="datasets",
)
def dataset_workbench(
    tokens: str | None = typer.Option(None, "-t", "--token", help="Comma separated list of ICAT tokens"),
    credentials: str | None = typer.Option(
        ..., "-c", "--credentials", help="Example: user1,password1:user2,password2"
    ),
    investigation_ids: str | None = typer.Option(
        None,
        "--investigation-ids",
        "-i",
        help="Comma separated list of investigation IDs (optional)",
    ),
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
    skip_count: int | None = typer.Option(
        3,
        "-k",
        "--skip-count",
        help="Number of skip variations",
    ),
    limit_count: int | None = typer.Option(
        3,
        "-l",
        "--limit-count",
        help="Number of limit variations",
    ),
    output: str | None = typer.Option(
        None,
        "-o",
        "--output",
        help="CSV output file path. Example: myfile.csv",
    ),
):
    """Benchmark dataset retrieval."""


@performance_app.command(
    "sample",
    help="""
    Generates statistics about the duration of the calls to the sample endpoint

    Example usage:

    .. code-block:: bash

      minedrac performance sample --token <TOKEN>  --start-date 2019-02-01 --end-date 2019-02-02 \
          --output benchmark.csv

    .. code-block:: bash

      minedrac performance dataset \
        --credentials admin,,*****:principalInvestigator,,*****:instrumentScientist,***** \
        --investigation-ids 2233749723 \
        --output benchmark.csv --skip-count 1 --limit-count 2

    .. code-block:: bash

      === Benchmark statistics per role ===

        Role: instrumentScientist | count=28 | avg=155.68ms | min=62.00ms | max=856.00ms | std=217.77ms
        Role: administrator | count=28 | avg=169.14ms | min=64.00ms | max=583.00ms | std=180.10ms
        Role: user | count=28 | avg=117.39ms | min=66.00ms | max=560.00ms | std=125.73ms
                               """,
)
@workbench(
    fetch_fn=get_timed_samples,
    result_label="samples",
)
def samples_workbench(
    tokens: str | None = typer.Option(None, "-t", "--token", help="Comma separated list of ICAT tokens"),
    credentials: str | None = typer.Option(
        ..., "-c", "--credentials", help="Example: user1,password1:user2,password2"
    ),
    investigation_ids: str | None = typer.Option(
        None,
        "--investigation-ids",
        "-i",
        help="Comma separated list of investigation IDs (optional)",
    ),
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
    skip_count: int | None = typer.Option(
        3,
        "-k",
        "--skip-count",
        help="Number of skip variations",
    ),
    limit_count: int | None = typer.Option(
        3,
        "-l",
        "--limit-count",
        help="Number of limit variations",
    ),
    output: str | None = typer.Option(
        None,
        "-o",
        "--output",
        help="CSV output file path. Example: myfile.csv",
    ),
):
    """Benchmark dataset retrieval."""


# For click documentation
click_performance_app = typer.main.get_command(performance_app)
