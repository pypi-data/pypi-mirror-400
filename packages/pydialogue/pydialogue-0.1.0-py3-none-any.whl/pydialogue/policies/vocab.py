from ..environments.world import compute_unique_list


def filter_words(obj):
    """ Creates a flat list of words.
        If the obj is a list, recursively add all elements of the list
        such that the result is a flat list of words.
    """
    words = []
    if isinstance(obj, str):
        words.append(obj)
    elif isinstance(obj, (list, tuple)):
        for elem in obj:
            words += filter_words(elem)
    return words


def compute_world_vocab(world):
    """
    Find all words that are part of the property keys, property values, and
    the attributes as well.
    """

    words = []
    property_keys = [prop for prop in world.all_properties if prop not in ['var_name', 'door_to']]
    attributes = [attr for attr in world.all_attributes if attr != ('main', 'player')]

    for word in property_keys+world.get_property_values(property_keys)+attributes:
        words += filter_words(word)

    return words


def compute_policies_words():
    """ Computes all the words that are used in the rule-based policies. """

    policies_words = [',', '.', '?', ':', 'the', 'entity', "'s",
                      'be', 'is', 'say', 'says', 'try', 'tries', 'go', 'went', 'goes', 'going',
                      'drop', 'drops', 'dropping', 'get', 'gets', 'getting',
                      'look', 'looks', 'looking', 'open',
                      'have', 'has',
                      'revealed', 'issued', 'to', 'a',  'an', 'in', 'on', 'under',
                      'and', 'then', 'can', 'not', 'no',
                      'whether', 'know', 'item',
                      'permitted', 'if', 'has', 'direction', 'players', 'path',
                      'position', 'from', 'items', 'see', 'sees',
                      'there', 'nothing', 'special', 'about', 'an', 'empty',
                      'response', 'unrecognizable', 'command', 'or', 'itself',
                      'successful', 'obstacle', 'absent', 'error', 'serialization',
                      'inaccurate', 'necessarily', 'dialogue']

    return list(set(policies_words))


def compute_input_vocab(world):
    """ Computes all the input vocabulary words by merging the words returned from the user, agent and environment policies.
        Additionally, all property keys and values are added from the world.
    """
    words = compute_policies_words() + compute_world_vocab(world)
    words += ['abstract']
    words = compute_unique_list(words)
    return words