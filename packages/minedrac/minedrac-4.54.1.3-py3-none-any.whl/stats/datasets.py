from datetime import timedelta

from data import dataset
from invoicing.duration import sum_dataset_durations


def calculate_acquisition_time(
    token: str, investigation_id: float, gap=20, dataset_type="acquisition"
) -> timedelta:
    datasets = dataset.get_datasets(token, investigation_ids=str(investigation_id), dataset_type=dataset_type)
    return sum_dataset_durations(datasets, gap)
