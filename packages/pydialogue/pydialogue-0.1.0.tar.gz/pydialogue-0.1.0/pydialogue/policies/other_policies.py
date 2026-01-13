
from . import base_policies as bpolicies
from . import goals as tgoals
from ..language import sentences as tsentences


class ItemPropRevealedPolicy(bpolicies.Policy):
    """ The agent's policy when the user asks the agent whether an item has
        a specific property pair (key, value).

    """
    def __init__(self, item, prop_key, prop_val, dialogue=None):
        super().__init__(dialogue=dialogue)
        self.item = item
        self.prop_key = prop_key
        self.prop_val = prop_val

    def execute(self, include_goal=False, **params):

        steps = self.get_steps()

        if include_goal:
            goal = self.get_goal()
            return steps, goal

        return steps

    def get_steps(self):
        # pick one prop that's not inside
        # maybe add <x> has not property color

        response = None
        if isinstance(self.prop_key, tuple):
            prop_key = list(self.prop_key)
            prop_key_list = prop_key
        else:
            prop_key = self.prop_key
            prop_key_list = [self.prop_key]

        if self.prop_key is None or self.prop_val is None:
            return None

        if self.prop_key not in self.item.properties:
            response = tsentences.have(self.item,
                                       'has',
                                       'no',
                                       prop_key)
        else:
            if self.item.properties[self.prop_key] == self.prop_val:
                neg = None
            else:
                neg = 'not'

            response = tsentences.be([self.item, "'s"]+ prop_key_list,
                                      "is",
                                      neg,
                                      self.prop_val)

        return response

    def get_goal(self):
        return tgoals.Goal(lambda: 1)
