from unittest.mock import patch

from icat_plus_client.models.investigation import Investigation

from stats.technique.technique import get_techniques_by_beamlines


class FakeTechnique:
    def __init__(self, pid, name):
        self.pid = pid
        self.name = name


class FakeDataset:
    def __init__(self, techniques, start_date):
        self.techniques = techniques
        self.start_date = start_date


class FakeInstrument:
    def __init__(self, name):
        self.name = name


def test_get_techniques_by_beamlines_return_data(tmp_path):
    fake_instruments = [FakeInstrument("BM01"), FakeInstrument("BM02")]
    fake_investigations = [
        Investigation(
            id=1,
            name="Fake Investigation 1",
            startDate="2024-01-01",
            endDate="2024-01-02",
        )
    ]
    fake_datasets = [
        FakeDataset(
            [
                FakeTechnique(
                    "http://purl.org/pan-science/ESRFET#SAD",
                    "SAD, Single-wavelength Anomalous Diffraction",
                )
            ],
            start_date="2024-01-01",
        ),
        FakeDataset(
            [FakeTechnique("http://purl.org/pan-science/ESRFET#XRAYS", "XRAYS, X-ray")],
            start_date="2024-01-01",
        ),
        FakeDataset(
            [FakeTechnique("http://purl.org/pan-science/ESRFET#PTYCHO", "PTYCHO, Ptychography")],
            start_date="2024-01-02",
        ),
    ]

    with (
        patch("data.instrument.get_instruments", return_value=fake_instruments),
        patch(
            "data.investigation.get_investigation_by_id",
            return_value=fake_investigations,
        ),
        patch("data.dataset.get_datasets", return_value=fake_datasets),
    ):
        data = get_techniques_by_beamlines(
            token="my_dummy_token",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

    # one row per beamline
    assert len(data) == 2

    row1 = data[0]
    assert row1["beamline"] == "BM01"
    assert row1["nb_exp_sessions"] == 1
    assert row1["nb_datasets"] == 2  # XRAYS is excluded
    assert "SAD" in row1["techniques"]
    assert "PTYCHO" in row1["techniques"]
    assert "SAD:1" in row1["technique_count"]
    assert "PTYCHO:1" in row1["technique_count"]

    row2 = data[1]
    assert row2["beamline"] == "BM02"
    assert row2["nb_exp_sessions"] == 1
    assert row2["nb_datasets"] == 2
