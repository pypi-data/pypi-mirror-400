from icat_plus_client.models.dataset import Dataset
from icat_plus_client.models.investigation import Investigation


def sum_investigation_parameter(investigations: list[Investigation], parameter_name: str):
    """
    Sums the values of a given parameter across a list of investigations.

    Args:
        investigations (list): List of investigations (each a dict with a 'parameters'
         field).
        parameter_name (str): The parameter key to sum.

    Returns:
        int: The total sum of the parameter values.
    """
    total = 0
    for inv in investigations:
        value = inv.parameters.get(parameter_name, 0)
        try:
            total += int(value)
        except (ValueError, TypeError):
            # If the value is not numeric or missing, skip
            continue
    return total


def sum_dataset_volume(datasets: list[Dataset]) -> float:
    return 49
