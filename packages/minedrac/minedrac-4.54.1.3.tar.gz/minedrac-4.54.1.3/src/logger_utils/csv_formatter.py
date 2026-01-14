import csv
import logging
from io import StringIO


class CSVFormatter(logging.Formatter):
    def __init__(self, fieldnames, fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s"):
        super().__init__(fmt)
        self.fieldnames = fieldnames

    def format(self, record):
        # Convert the extra fields into a CSV line
        row = {field: getattr(record, field, "") for field in self.fieldnames}
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.fieldnames, extrasaction="ignore", lineterminator="")
        writer.writerow(row)
        # Use CSV line as the actual message
        record.msg = output.getvalue()
        return super().format(record)
