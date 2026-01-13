#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module lists the user policies that the user uses to respond to the dialogue.
"""

import copy
from abc import ABC, abstractmethod

from ..language import sentences as tsentences
from ..language import queries as tqueries

from . import base_policies as bp


class UserPolicy(bp.Policy, ABC):
    """
    The self for the user issuing a request.

    The goal is always None since the goal is defined in the agent self
    (see base_policies.ActionPolicy).

    Attributes
    ----------
    player : Entity
        The user.
    dialogue : Dialogue, optional
        The dialogue where this self is used. The default is None.

    """

    def execute(self, include_goal=False, **params):
        steps = self.get_steps(**params)
        goal = self.get_goal(**params)
        if include_goal:
            return steps, goal
        else:
            return steps

    def get_goal(self, **params):
        return None


class BaseItemPolicy(UserPolicy, ABC):
    """
    Base self that covers the user requests in the following format:

    ..

        <player> says: <agent>, <action> (a) <item>

    For example, Andy says: Hans, get a red ball

    Attributes
    ----------
    player : Entity
        The user that issues the request.
    item : Entity
        The item that the user acts upon.
    agent : Entity
        The agent that has to perform the action.
    dialogue : Dialogue, optional
        The dialogue that the self belongs to. The default is None.

    """
    def __init__(self, player, item=None, agent=None, dialogue=None):
        super().__init__(player, dialogue)
        self.item = item
        self.agent = agent

    @abstractmethod
    def generate_response(self, item, agent_desc_elems, tmp):
        """
        Generate the user request that the agent has to complete.

        Parameters
        ----------
        item : Entity
            The entity that the agent acts upon.
        agent_desc_elems : list
            List of elements, property keys, attributes, or other strings for the agent description.
        tmp : tuple
            The tmp element is used for temporal words/phrases. The first element of the tuple
            can be a string or a list and the second one Word or Phrase.


        Returns
        -------
        Sentence
            The user request.
        """
        pass

    def get_steps(self, **params):
        """
        Get the user request based on the attributes of this class.

        Returns
        -------
        sent : Sentence
            The user request.

        """
        if self.item is None or self.agent is None:
            return None

        sent = None

        if self.dialogue is not None:
            player_prev_utters = self.dialogue.get_player_utters(self.player)
        else:
            player_prev_utters = []
        if len(player_prev_utters) < 1:
            item = self.item
            self.agent.describe()
            agent_desc_elems = copy.copy(self.agent.description.elements)
            if agent_desc_elems[0] == "the":
                del agent_desc_elems[0]
            tmp = params.get("tmp", None)
            sent = self.generate_response(item, agent_desc_elems, tmp)
            if sent is not None:
                sent = tsentences.say(self.player, None, 'says',
                                      sent, speaker=self.player)
            self.reset()
        return sent

    def reset(self):
        self.item = None
        self.agent = None

    def save_state(self):
        return self.item, self.agent

    def recover_state(self, state):
        self.item, self.agent = state[0], state[1]


class ActionItemPolicy(BaseItemPolicy, ABC):
    """ Action self that covers the user requests in the following format:

            <agent>, <action> (a) <item> <location_position> <location>

        For example, Hans, get the red ball in the kitchen.

    """
    def __init__(self, player, item=None, agent=None, location=None, location_position=None,  dialogue=None):
        super().__init__(player, item, agent,  dialogue)
        self.location = location
        self.location_position = location_position

    def reset(self):
        super().reset()
        self.location = None
        self.location_position = None

    def save_state(self):
        return super().save_state(), self.location, self.location_position

    def recover_state(self, state):
        super().recover_state(state[0])
        self.location, self.location_position = state[1], state[2]


class GoDirectionPolicy(UserPolicy):
    """ Action self that covers the user requests in the following format:

            <player> says: <agent>, go <direction>

        For example, the big person says: John, go north
    """
    def __init__(self, player, agent=None, direction=None, dialogue=None):
        super().__init__(player, dialogue)
        self.agent = agent
        self.direction = direction

    def get_steps(self, **params):
        sent = None
        if self.agent is None or self.direction is None:
            return None

        player_prev_utters = self.dialogue.get_player_utters(self.player)

        if len(player_prev_utters) < 1:
            tmp = params.get("tmp", None)
            self.agent.describe()
            agent_desc_elems = copy.copy(self.agent.description.elements)
            if agent_desc_elems[0] == "the":
                del agent_desc_elems[0]

            request_go_to_direction = tqueries.go(tmp=tmp,
                                                  player=(self.agent, self.agent.describe(agent_desc_elems)),
                                                  rel="go",
                                                  direction=self.direction,
                                                  speaker=self.player)

            sent = tsentences.say(self.player, None, 'says',
                                  request_go_to_direction, speaker=self.player)
            self.reset()

        return sent

    def reset(self):
        self.agent = None
        self.direction = None

    def save_state(self):
        return self.agent, self.direction

    def recover_state(self, state):
        self.agent = state[0]
        self.direction = state[1]


class GoLocationPolicy(ActionItemPolicy):
    """ The self for the user request: <agent>, go to (a) item """
    def generate_response(self, item, agent_desc_elems, tmp):

        target_location = ['to', item]

        sent = tqueries.go(tmp,
                           (self.agent, self.agent.describe(agent_desc_elems)),
                           rel='go',
                           target_location=target_location,
                           speaker=self.player)

        return sent


class GetItemPolicy(ActionItemPolicy):
    """ The self for the user request: <agent>, get (a) item <location_position> <location>"""

    def generate_response(self, item, agent_desc_elems, tmp):

        if self.location is not None:
            loc_pos = [self.location_position, self.location]
        else:
            loc_pos = None

        sent = tqueries.get(tmp,
                            (self.agent, self.agent.describe(agent_desc_elems)),
                            rel='get',
                            entity=item,
                            prepos_location=loc_pos,
                            speaker=self.player)

        return sent


class DropItemPolicy(ActionItemPolicy):
    """ The self for the user request: <agent>, drop (a) item <location_position> <location>"""

    def generate_response(self, item, agent_desc_elems, tmp):

        if self.location is not None:
            loc_pos = [self.location_position, self.location]
        else:
            loc_pos = None

        sent = tqueries.drop(tmp,
                             (self.agent, self.agent.describe(agent_desc_elems)),
                             rel='drop',
                             entity=item,
                             prepos_location=loc_pos,
                             speaker=self.player)
        return sent


class LookItemPolicy(ActionItemPolicy):
    """ The self for the user request: <agent>, look <location_position> (a) item in <location> """

    def generate_response(self, item, agent_desc_elems, tmp):

        if self.location is not None:
            loc_pos = [self.location.properties["location"][0], self.location]
        else:
            loc_pos = None

        if isinstance(item, list):
            item = [self.location_position] + item
        else:
            item = [self.location_position, item]

        sent = tqueries.look(tmp,
                             (self.agent, self.agent.describe(agent_desc_elems)),
                             rel='look',
                             thing_looked=item if not loc_pos else item+loc_pos,
                             speaker=self.player)
        return sent
