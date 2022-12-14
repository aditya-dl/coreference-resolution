### Rule-based coreference resolution  ###########
# Lightly inspired by Stanford's "Multi-pass sieve"
# http://www.surdeanu.info/mihai/papers/emnlp10.pdf
# http://nlp.stanford.edu/pubs/conllst2011-coref.pdf

import nltk

pronouns = ['i', 'me', 'mine', 'you', 'your', 'yours', 'she', 'her', 'hers'] + \
           ['he', 'him', 'his', 'it', 'its', 'they', 'them', 'their', 'theirs'] + \
           ['this', 'those', 'these', 'that', 'we', 'our', 'us', 'ours']
downcase_list = lambda toks: [tok.lower() for tok in toks]

############## Pairwise matchers #######################


def exact_match(m_a, m_i):
    """
    return True if the strings are identical

    :param m_a: antecedent markable
    :param m_i: referent markable
    :returns: True if the strings are identical
    :rtype: boolean
    """
    return downcase_list(m_a.string) == downcase_list(m_i.string)


def singleton_matcher(m_a, m_i):
    """
    return value such that a document consists of only singleton entities

    :param m_a: antecedent markable
    :param m_i: referent markable
    :returns: 
    :rtype: boolean
    """
    return m_a.start_token == m_i.start_token and m_a.end_token == m_i.end_token


def full_cluster_matcher(m_a, m_i):
    """
    return value such that a document consists of a single entity

    :param m_a: antecedent markable
    :param m_i: referent markable
    :returns: 
    :rtype: boolean
    """
    return True


def exact_match_no_pronouns(m_a, m_i):
    """
    return True if strings are identical and are not pronouns

    :param m_a: antecedent markable
    :param m_i: referent markable
    :returns: True if the strings are identical and are not pronouns
    :rtype: boolean
    """

    # c1 = not((" ".join(m_a.string).lower() in pronouns) and (" ".join(m_a.string).lower() in pronouns))
    # c2 = m_a.string == m_i.string
    # if c2:
    #     print("m_a:{}, m_i:{}, c1:{}, c2:{}".format(m_a, m_i, c1, c2))
    # print("m_a:{}, m_i:{}, c1:{}, c2:{}".format(m_a.string, m_i.string, c1, c2))

    return downcase_list(m_a.string) == downcase_list(
        m_i.string) and not ("".join(m_a.string).lower() in pronouns)


def match_last_token(m_a, m_i):
    """
    return True if final token of each markable is identical

    :param m_a: antecedent markable
    :param m_i: referent markable
    :rtype: boolean
    """
    return m_a.string[-1].lower() == m_i.string[-1].lower()


def match_no_overlap(m_a, m_i):
    return not (m_i.start_token <= m_a.start_token <= m_i.end_token) and \
           not (m_a.start_token <= m_i.start_token <= m_a.end_token)


def match_last_token_no_overlap(m_a, m_i):
    """
    return True if last tokens are identical and there's no overlap

    :param m_a: antecedent markable
    :param m_i: referent markable
    :returns: True if final tokens match and strings do not overlap
    :rtype: boolean
    """

    return match_last_token(m_a, m_i) and match_no_overlap(m_a, m_i)


def match_on_content(m_a, m_i):
    """
    return True if all content words are identical and there's no overlap

    :param m_a: antecedent markable
    :param m_i: referent markable
    :returns: True if all match on all "content words" (defined by POS tag) and markables do not overlap
    :rtype: boolean
    """
    ALLOWED_TAGS = [
        'CD', 'NN', 'NNS', 'NNP', 'NNPS', 'PRP', 'PRP$', 'JJ', 'JJR', 'JJS'
    ]

    filtered_ma_s = [
        token for i, token in enumerate(m_a.string)
        if m_a.tags[i] in ALLOWED_TAGS
    ]
    filtered_mi_s = [
        token for i, token in enumerate(m_i.string)
        if m_i.tags[i] in ALLOWED_TAGS
    ]

    return not (m_i.start_token <= m_a.start_token <= m_i.end_token) and \
           not (m_a.start_token <= m_i.start_token <= m_a.end_token) and \
           downcase_list(filtered_ma_s) == downcase_list(filtered_mi_s)


########## helper code


def most_recent_match(markables, matcher):
    """
    given a list of markables and a pairwise matcher, return an antecedent list
    assumes markables are sorted

    :param markables: list of markables
    :param matcher: function that takes two markables, returns boolean if they are compatible
    :returns: list of antecedent indices
    :rtype: list
    """
    antecedents = list(range(len(markables)))
    for i, m_i in enumerate(markables):
        for a, m_a in enumerate(markables[:i]):
            if matcher(m_a, m_i):
                antecedents[i] = a
    return antecedents


def make_resolver(pairwise_matcher):
    """
    convert a pairwise markable matching function into a coreference resolution system, which generates antecedent lists

    :param pairwise_matcher: function from markable pairs to boolean
    :returns: function from markable list and word list to antecedent list
    :rtype: function

    The returned lambda expression takes a list of words and a list of markables.
    The words are ignored here. However, this function signature is needed because
    in other cases, we want to do some NLP on the words.
    """
    return lambda markables: most_recent_match(markables, pairwise_matcher)