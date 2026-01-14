import csv
import logging
from collections.abc import Iterable
from datetime import datetime, timedelta

from icat_plus_client.models.dataset import Dataset

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def merge_intervals(
    intervals: Iterable[tuple[datetime, datetime, object]],
    merge_gap: timedelta,
):
    """
    Merge overlapping or near-adjacent intervals.

    Returns a list of:
        (merged_start, merged_end, [datasets])
    """
    merged = []

    for start, end, ds in sorted(intervals, key=lambda x: x[0]):
        if not merged:
            merged.append([start, end, [ds]])
            continue

        last_start, last_end, last_datasets = merged[-1]

        # overlap OR gap within threshold
        if start <= last_end + merge_gap:
            merged[-1][1] = max(last_end, end)
            last_datasets.append(ds)
        else:
            merged.append([start, end, [ds]])

    return merged


def sum_dataset_durations(
    datasets: list[Dataset] | None = None,
    merge_gap_minutes: int = 0,
    outfile: str | None = None,
    ignore_longer_than: int | None = None,
) -> timedelta:
    if datasets is None:
        datasets = []

    merge_gap = timedelta(minutes=merge_gap_minutes)

    fields = [
        "sample_name",
        "dataset_name",
        "start_date",
        "end_date",
        "dataset_duration",
        "gap_with_previous",
        "will_merge",
        "accumulative_time",
    ]

    writer = None
    f = None
    if outfile:
        f = open(outfile, "w", newline="")
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader()

    # -----------------------------
    # Parse + filter intervals
    # -----------------------------
    intervals = []
    for ds in datasets:
        start = datetime.fromisoformat(ds.start_date.replace("Z", "+00:00"))
        end = datetime.fromisoformat(ds.end_date.replace("Z", "+00:00"))

        if ignore_longer_than and end - start > timedelta(hours=ignore_longer_than):
            continue

        intervals.append((start, end, ds))

    if not intervals:
        return timedelta(0)

    # -----------------------------
    # Warn about true overlaps
    # -----------------------------
    intervals.sort(key=lambda x: x[0])
    for i in range(len(intervals) - 1):
        s1, e1, d1 = intervals[i]
        s2, e2, d2 = intervals[i + 1]
        if s2 < e1:
            logger.warning(
                "%s Overlap: %s (%s → %s) overlaps with %s (%s → %s) sample_id:%s investigation_id:%s",
                d1.investigation.name,
                d1.name,
                s1,
                e1,
                d2.name,
                s2,
                e2,
                d1.sample_name,
                d1.investigation.id,
            )

    # -----------------------------
    # Merge intervals correctly
    # -----------------------------
    merged = merge_intervals(intervals, merge_gap)

    # -----------------------------
    # Sum durations + write rows
    # -----------------------------
    total_time = timedelta(0)
    previous_end = None

    for merged_start, merged_end, datasets_in_block in merged:
        block_duration = merged_end - merged_start
        total_time += block_duration

        for ds in datasets_in_block:
            start = datetime.fromisoformat(ds.start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(ds.end_date.replace("Z", "+00:00"))

            gap = ""
            will_merge = False
            if previous_end is not None:
                gap = start - previous_end
                will_merge = gap <= merge_gap

            if writer:
                writer.writerow(
                    {
                        "sample_name": ds.sample_name,
                        "dataset_name": ds.name,
                        "start_date": ds.start_date,
                        "end_date": ds.end_date,
                        "dataset_duration": end - start,
                        "gap_with_previous": gap,
                        "will_merge": will_merge,
                        "accumulative_time": total_time,
                    }
                )

            previous_end = end

    if f:
        f.close()

    return total_time
