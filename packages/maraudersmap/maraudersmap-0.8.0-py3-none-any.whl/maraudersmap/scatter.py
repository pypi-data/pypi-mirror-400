from typing import Union, List


def structjson2csv(json_data: dict) -> List[dict]:
    """
    Flattens `struct_repo.json` to a compatible CSV format

    Args:
        json_data (dict): Nested data from a json file.

    Returns:
        List[dict]: Data compatible with csv.
    """
    csv_data = [{k: v for k, v in json_data.items() if k != "children"}]
    for child in json_data["children"]:
        csv_data += structjson2csv(child)
    return csv_data


def standardize_keys(list_dict: List[dict]) -> List[dict]:
    """Standardizes keys across dictionaries. Required to write `list_dict` to CSV.
    Missing keys in a dictionary are set to None.

        Args:
            list_dict (List[dict]): Input data

        Returns:
            List[dict]: List of dicts with the same keys
    """
    keys = set()
    for el in list_dict:
        keys.update(el.keys())
    return [{k: el[k] if k in el.keys() else None for k in keys} for el in list_dict]


def filter_list_dict(
    list_dict: List[dict], key: str, value: Union[str, int, float]
) -> List[dict]:
    """Exclude dictionaries from the list if they match the (key, value) pair.

    Args:
        list_dict (list): Input data.
        key (str): Key.
        value (Union[str, int, float]): Value to exclude.

    Returns:
        List[dict]: Filtered data
    """
    return [{k: v for k, v in el.items()} for el in list_dict if el[key] != value]
