import csv
import os

import pytest

from data import session
from stats.technique.technique import get_techniques_by_beamlines, write_csv


def get_test_token():
    username = os.getenv("ICAT_USER")
    password = os.getenv("ICAT_PASSWORD")
    authenticator = "db"
    if not username or not password:
        pytest.skip("ICAT credentials not set, skipping integration test")

    session_response = session.get_session(authenticator, username, password)
    return session_response


@pytest.mark.integration
def test_integration_get_techniques_by_beamlines_csv(tmp_path):
    token = get_test_token()
    start_date = "2025-01-01"
    end_date = "2025-01-02"

    csv_file = tmp_path / "beamline_report.csv"

    data = get_techniques_by_beamlines(token, start_date, end_date)

    write_csv(data, csv_file)

    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) > 0

    for row in rows:
        assert "beamline" in row
        assert "nb_exp_sessions" in row
        assert "nb_datasets" in row
        assert "techniques" in row
        assert "technique_count" in row
