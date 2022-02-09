#
# The script providing implementation of functions to calculate distance
# used in the Novelry Search method.
#

import math

def novelty_metric_manhattan(first_item, second_item):
    """
    The function to calculate the novelty metric score as a distance between two
    data vectors in provided NoveltyItems
    Arguments:
        first_item:     The first NoveltyItem
        second_item:    The second NoveltyItem
    Returns:
        The novelty metric as a distance between two
        data vectors in provided NoveltyItems
    """
    if not (hasattr(first_item, "data") or hasattr(second_item, "data")):
        return NotImplemented

    if len(first_item.data) != len(second_item.data):
        # can not be compared
        return 0.0

    diff_sum = 0.0
    size = len(first_item.data)
    for i in range(size):
        diff = abs(first_item.data[i] - second_item.data[i])
        diff_sum += diff

    return diff_sum / float(size)

def novelty_metric_euclidean(first_item, second_item):
    """
    The function to calculate the novelty metric score as a distance between two
    data vectors in provided NoveltyItems
    Arguments:
        first_item:     The first NoveltyItem
        second_item:    The second NoveltyItem
    Returns:
        The novelty metric as a distance between two
        data vectors in provided NoveltyItems
    """
    if not (hasattr(first_item, "data") or hasattr(second_item, "data")):
        return NotImplemented

    if len(first_item.data) != len(second_item.data):
        # can not be compared
        return 0.0

    diff_sum = 0.0
    size = len(first_item.data)
    for i in range(size):
        diff = (first_item.data[i] - second_item.data[i])
        diff_sum += (diff * diff)

    return math.sqrt(diff_sum)
