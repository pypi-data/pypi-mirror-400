from datetime import timedelta

import pytest
from icat_plus_client.models.dataset import Dataset
from icat_plus_client.models.dataset_document_investigation import (
    DatasetDocumentInvestigation,
)

from invoicing.duration import sum_dataset_durations


# Fixture for investigation
@pytest.fixture
def investigation():
    return DatasetDocumentInvestigation(
        id=1,
        name="INV",
        startDate="2024-01-30T10:00:00.000Z",
        endDate="2024-01-30T12:00:00.000Z",
        location="/tmp",
        sampleName="",
    )


@pytest.fixture
def make_datasets(investigation):
    def _make(*dataset_times):
        return [
            Dataset(
                id=i,
                name=f"dataset-{i}",
                start_date=start,
                end_date=end,
                location="/tmp",
                sample_name="",
                parameters=[],
                investigation=investigation,  # Pydantic requirement
            )
            for i, (start, end) in enumerate(dataset_times, start=1)
        ]

    return _make


@pytest.mark.parametrize(
    "dataset_times, merge_gap_minutes, expected, ignore_longer_than",
    [
        pytest.param(
            [("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z")],
            20,
            timedelta(hours=1),
            5,
            id="Single dataset duration with 1h dataset",
        ),
        pytest.param(
            [("2024-01-30T10:00:00.000Z", "2024-01-30T10:00:01.000Z")],
            20,
            timedelta(seconds=1),
            5,
            id="Single dataset duration with 1s dataset",
        ),
        pytest.param(
            [("2024-01-30T10:00:00.000Z", "2024-01-30T10:00:00.000Z")],
            20,
            timedelta(seconds=0),
            5,
            id="Single dataset duration with 0s dataset",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
                ("2024-01-30T11:00:00.000Z", "2024-01-30T12:00:00.000Z"),
            ],
            20,
            timedelta(hours=2, minutes=0),
            5,
            id="Two datasets no gap in between",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
                ("2024-01-30T11:30:00.000Z", "2024-01-30T12:00:00.000Z"),
            ],
            20,
            timedelta(hours=1, minutes=30),
            5,
            id="Two datasets with gap in between",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
                ("2024-01-30T11:30:00.000Z", "2024-01-30T12:00:00.000Z"),
            ],
            30,
            timedelta(hours=2, minutes=0),
            5,
            id="Two datasets with gap short enough in between",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
            ],
            30,
            timedelta(hours=1, minutes=0),
            5,
            id="Two fully overlaping datasets with gap short enough in between",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
                ("2024-01-30T10:30:00.000Z", "2024-01-30T11:30:00.000Z"),
            ],
            30,
            timedelta(hours=1, minutes=30),
            5,
            id="Two partial overlaping datasets with gap short enough in between",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
                ("2024-01-29T10:30:00.000Z", "2024-01-29T11:30:00.000Z"),
            ],
            30,
            timedelta(hours=2, minutes=0),
            5,
            id="Two partial overlaping datasets in different days",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
                ("2024-01-30T11:30:00.000Z", "2024-01-30T12:00:00.000Z"),
                ("2024-01-30T12:30:00.000Z", "2024-01-30T13:00:00.000Z"),
            ],
            30,
            timedelta(hours=3, minutes=0),
            5,
            id="Three datasets with no gaps",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T11:00:00.000Z"),
                ("2024-01-30T11:30:00.000Z", "2024-01-30T12:00:00.000Z"),
                ("2024-01-30T12:30:00.000Z", "2024-01-30T13:00:00.000Z"),
                ("2024-01-30T12:30:00.000Z", "2024-01-30T22:00:00.000Z"),
            ],
            30,
            timedelta(hours=3, minutes=0),
            5,
            id="Three datasets with no gaps and one to be ignored",
        ),
        pytest.param(
            [
                ("2024-01-30T10:00:00.000Z", "2024-01-30T12:00:00.000Z"),
                ("2024-01-30T12:30:00.000Z", "2024-01-30T22:00:00.000Z"),
            ],
            30,
            timedelta(hours=0, minutes=0),
            1,
            id="All ignored",
        ),
    ],
)
def test_calculate_dataset_duration(
    dataset_times, merge_gap_minutes, expected, ignore_longer_than, make_datasets
):
    """
    Runs the merge-gap test with multiple dataset inputs.
    """
    datasets = make_datasets(*dataset_times)

    result = sum_dataset_durations(
        datasets, merge_gap_minutes=merge_gap_minutes, outfile=None, ignore_longer_than=ignore_longer_than
    )
    assert result == expected
