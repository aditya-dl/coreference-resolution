from . import coref_rules
from collections import defaultdict


def minimal_features(markables, a, i):
    """
    Compute a minimal set of features for antecedent a and mention i

    :param markables: list of markables for the document
    :param a: index of antecedent
    :param i: index of mention
    :returns: dict of features
    :rtype: defaultdict
    """

    f = defaultdict(float)

    m_a = markables[a]
    m_i = markables[i]

    if a == i:
        f["new-entity"] = 1
    else:
        if coref_rules.exact_match(m_a, m_i):
            f["exact-match"] = 1
        if coref_rules.match_last_token(m_a, m_i):
            f["last-token-match"] = 1
        if coref_rules.match_on_content(m_a, m_i):
            f["content-match"] = 1
        if m_a.start_token <= m_i.start_token <= m_a.end_token or m_i.start_token <= m_a.start_token <= m_i.end_token:
            f["crossover"] = 1

    return f


def distance_features(x, a, i, max_mention_distance=5, max_token_distance=10):
    """
    compute a set of distance features for antecedent a and mention i

    :param x: markable list for document
    :param a: antecedent index
    :param i: mention index
    :param max_mention_distance: upper limit on mention distance
    :param max_token_distance: upper limit on token distance
    :returns: dict of features
    :rtype: defaultdict
    """

    f = defaultdict(float)
    if a == i:
        return f
    else:
        mention_dist = min(abs(i - a), max_mention_distance)
        token_dist = min(abs(x[i].start_token - x[a].end_token),
                         max_token_distance)
        if mention_dist > 0:
            f["mention-distance-{}".format(mention_dist)] = 1

        if token_dist > 0:
            f["token-distance-{}".format(token_dist)] = 1
        return f


def make_feature_union(feat_func_list):
    """
    return a feature function that is the union of the feature functions in the list

    :param feat_func_list: list of feature functions
    :returns: feature function
    :rtype: function
    """

    def union_func(x, a, i):
        f = defaultdict(float)
        for feat_func in feat_func_list:
            f.update(feat_func(x, a, i))
        return f

    return union_func


def make_bakeoff_features():
    raise NotImplementedError