def flatten_dict(data: dict, separator: str = ".", prefix: str = "") -> dict:
    """
    Flattens a nested dictionary by using composite field names (a.b.c).
    Note, it only works with string keys

    :param data:
    :param separator:
    :param prefix:
    :return:
    """

    ret = {}
    for key, value in data.items():
        if type(value) is dict:
            flattened = flatten_dict(value, separator, key)
            prefix_flattened = {f"{key}{separator}{flattened_key}": flattened_value
                                for flattened_key, flattened_value in flattened.items()}
            ret.update(prefix_flattened)
        else:
            ret[key] = value

    return ret
