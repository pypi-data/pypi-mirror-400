def _list(a):
    """Convert element to list of not already"""
    if isinstance(a, (tuple, set)):
        return list(a)
    if not isinstance(a, list):
        return [a]
    return a


def _concat(a, b):
    """Concatenate elements to list"""
    return _list(a) + _list(b)
