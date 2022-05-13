import math

def manhattan(data1, data2):
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
    if len(data1) != len(data2) or len(data1) < 1:
        return 0.0
    diff = [abs(d1 - d2) for d1, d2 in zip(data1, data2)]
    dist = sum(diff)
    return dist


def euclidean(first_item, second_item):
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
    if len(data1) != len(data2) or len(data1) < 1:
        return 0.0
    diff = [(d1 - d2) ** 2 for d1, d2 in zip(data1, data2)]
    dist = math.sqrt(sum(diff))
    return dist
