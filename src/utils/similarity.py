from typing import List


def num_overlap(l1: List, l2: List) -> float:
    """
    Overlap between two lists.

    Parameters:
    - l1: first list
    - l2: second list

    Return:
    - number of overlapping values
    """
    return len(set(l1) & set(l2))
