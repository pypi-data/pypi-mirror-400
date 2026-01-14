def percentage(part_count, whole_count, round_to=False):
    # Fucking deprecate this, this is pointless
    if round_to:
        return round(100 * (part_count / whole_count), round_to)
    return 100 * (part_count / whole_count)


def dict_difference(a, b):
    """
    This can be replaced with set calcaultions
    """
    if not isinstance(a, dict) and not isinstance(b, dict):
        raise TypeError("dict_difference only works on dicts")

    diff_dict = {}
    for k in a.keys():
        if k in b:
            diff_dict[k] = b[k] - a[k]
        else:
            diff_dict[k] = -a[k]

    for k in b.keys():
        if k not in a:
            diff_dict[k] = b[k]

    return diff_dict


def dict_transpose(a):
    if not isinstance(a, dict):
        raise TypeError("dict_transpose only works on dicts")

    transposed_dict = {}
    for b in a:
        for k, v in a.items():
            for i, j in v.items():
                if i not in transposed_dict:
                    transposed_dict[i] = {}
                transposed_dict[i][k] = j

    return transposed_dict
