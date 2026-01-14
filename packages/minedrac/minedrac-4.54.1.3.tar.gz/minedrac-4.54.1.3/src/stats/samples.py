from data import sample


def count_samples_with_datasets(token: str, investigation_id: float) -> int:
    samples = sample.get_samples_by(token, investigation_id)
    count = 0
    for s in samples:
        for param in s.parameters:
            if param.name == "__datasetCount" and int(param.value) > 0:
                count += 1
                break  # no need to check other params for this sample
    return count
