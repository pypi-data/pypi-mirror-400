#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module lists all the classes that generate the goals of the dialogue.
"""
from ..policies import goals as tgoals


class GoalGenerator:
    """ A simple goal generator that generates the agent's goal (class goals.Goal).
        The agent's goal can change during the dialogue, so the goal generator is required.

        Attributes
        ----------
        policy : Policy
            The rule-based self that returns the self's goal.
    """
    def __init__(self, policy):
        self.policy = policy

    def execute(self):
        """ The current rule-based agent policies return the next player's utterance and their goal. We
            use the self's get_goal function to fetch the goal.
        """
        return self.policy.get_goal()

    def replace_dialogue(self, new_dialogue):
        """ In case the self is used in a different dialogue, this
            function allows replacing the dialogue.
        """
        self.policy.replace_dialogue(new_dialogue)

    def save_state(self):
        """ Saves the state of the goal generator by saving the self state. """
        return self.policy.save_state()

    def recover_state(self, state):
        """ Recovers the state of the goal generator by recovering the self state. """
        self.policy.recover_state(state)
