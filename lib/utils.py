"""various utility functions"""
import itertools


def listify(item):
    """casts non list item to single element list"""
    return item if isinstance(
        item, list) else [item]


def flatten_list(l):
    """flattens nested lists"""
    return list(itertools.chain.from_iterable(l))


def unique_list(l):
    """remove duplicate items from a list"""
    return list(set(l))
