import pytest
from icat_plus_client.models.investigation import Investigation

from stats.volume.volume import get_volumes_by_investigation


@pytest.fixture
def make_investigations():
    def _make(*investigation_volume_parameters):
        return [
            Investigation(
                id=i,
                name=f"dataset-{i}",
                start_date="",
                end_date="",
                location="/tmp",
                sample_name="",
                parameters={
                    "__acquisitionVolume": acquisition_volume,
                    "__processedVolume": processed_volume,
                    "__volume": volume,
                },
            )
            for i, (volume, acquisition_volume, processed_volume) in enumerate(
                investigation_volume_parameters, start=1
            )
        ]

    return _make


KB = 1024
MB = 1024 * 1024


@pytest.mark.parametrize(
    "investigation_volume_parameters, unit, expected",
    [
        pytest.param(
            [(0, 0, 0)],
            ("bytes"),
            (0, 0, 0),
            id="Investigation with no data in bytes",
        ),
        pytest.param(
            [(0, 0, 0)],
            ("MB"),
            (0, 0, 0),
            id="Investigation with no data in MB",
        ),
        pytest.param(
            [(KB, KB, KB), (KB, KB, KB)],
            ("bytes"),
            (2 * KB, 2 * KB, 2 * KB),
            id="Two investigations in bytes",
        ),
        pytest.param(
            [(KB, KB, KB), (KB, KB, KB)],
            ("MB"),
            (0, 0, 0),
            id="Two investigations in MB",
        ),
        pytest.param(
            [(3 * MB, MB, 2 * MB), (3 * MB, MB, 2 * MB)],
            ("MB"),
            (6, 2, 4),
            id="Two investigations in MB",
        ),
    ],
)
def test_calculate_investigation_volume(investigation_volume_parameters, unit, expected, make_investigations):
    """
    Runs the merge-gap test with multiple dataset inputs.
    """
    investigations = make_investigations(*investigation_volume_parameters)
    result = get_volumes_by_investigation(investigations, unit)
    assert result == expected
