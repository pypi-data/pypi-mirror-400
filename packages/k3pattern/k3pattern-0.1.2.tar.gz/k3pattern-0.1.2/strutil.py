def common_prefix(a, *others, **options):
    """
    Find common prefix of several `string`s, tuples of string, or other nested
    structure, recursively by default.
    It returns the shortest prefix: empty string or empty tuple is removed.
    :param a: `a` and element in `others`: are `string`, `tuple` or `list` to find common prefix of them.
    if field `recursive` in `options` is set to `False`, it will run non-recursively.
    :return: a common prefix of the same type of `a`.
    """
    recursive = options.get("recursive", True)
    for b in others:
        if type(a) is not type(b):
            raise TypeError("a and b has different type: " + repr((a, b)))
        a = _common_prefix(a, b, recursive)

    return a


def _common_prefix(a, b, recursive=True):
    rst = []
    for i, elt in enumerate(a):
        if i == len(b):
            break

        if type(elt) is not type(b[i]):
            raise TypeError("a and b has different type: " + repr((elt, b[i])))

        if elt == b[i]:
            rst.append(elt)
        else:
            break

    # Find common prefix of the last different element.
    #
    # string does not support nesting level reduction. It infinitely recurses
    # down.
    # And non-iterable element is skipped, such as int.
    i = len(rst)
    if recursive and i < len(a) and i < len(b) and not isinstance(a, str) and hasattr(a[i], "__len__"):
        last_prefix = _common_prefix(a[i], b[i])

        # discard empty tuple, list or string
        if len(last_prefix) > 0:
            rst.append(last_prefix)

    if isinstance(a, tuple):
        return tuple(rst)
    elif isinstance(a, list):
        return rst
    else:
        return "".join(rst)
