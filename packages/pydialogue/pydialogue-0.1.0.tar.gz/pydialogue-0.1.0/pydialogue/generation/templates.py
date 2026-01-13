#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains functions called templates that generate different dialogue types.
"""
from ..policies import agent_policies
from ..policies import user_policies
from ..policies import other_policies
from . import helpers

from . import dialogue as dia
from . import goal_generators as gen


def init_dialogue(dia_generator, user_policy, agent_policy, entities_descriptions=None):
    """
    Creates and initializes the dialogue.

    Parameters
    ----------
    dia_generator : DialogueGenerator
        The dialogue generator that was used to generate the dialogue.
    user_policy : UserPolicy
        The user self. The user issues the request to the agent.
    agent_policy : AgentPolicy
        The agent's self. The agent should satisfy the user's request.
    entities_descriptions : dict (:class:`~pydialogue.environment.entities.Entity` : :class:`~pydialogue.environment.descriptions.BaseDescription`)
        A description for each of the entities that are part of the dialogue.
        Each entity can have a different description.
        For example, the toy's container can be described as "the static red container" or "the red openable container".
        If left None, entities' descriptions will be automatically generated as the dialogue runs.

    Returns
    -------
    dialogue : Dialogue
        The initialized dialogue.

    """
    dialogue = dia.Dialogue(dia_generator, entities_descriptions=entities_descriptions)

    env_policy = dia_generator.env_auto_policy
    if env_policy is None:
        return None

    env_policy.replace_dialogue(dialogue)

    if agent_policy is None:
        return None

    dialogue.add_policies([user_policy, agent_policy])

    dialogue.goal_generator = gen.GoalGenerator(agent_policy)
    # To speed up things during execution. Check Dialogue.run for more.
    # dialogue.use_generator = False

    return dialogue


def go_direction(dia_generator, user, agent, direction, entities_descriptions=None):
    """ Creates a dialogue between a user, an agent and the environment.
        The user issues a request to the agent in the following manner:

            <user> says: <agent> go <direction>

        The goal of the dialogue is for the agent to fulfill the user's request.

        Parameters
        ----------
        dia_generator : DialogueGenerator
            The class used for generating new dialogues.
        user : Entity
            The user that sends the request.
        agent : Entity
            The agent that needs to fulfill the user's request.
        direction : str
            The direction where the agent should go. For example: north, east, northeast ...
            The list of directions can be found in dia_generator.world.directions.
        entities_descriptions : dict (:class:`~pydialogue.environment.entities.Entity` : :class:`~pydialogue.environment.descriptions.BaseDescription`)
            A description for each of the entities that are part of the dialogue.
            Each entity can have a different description.
            For example, the toys container can be described as the static container or the red container.
            If left None, entities' descriptions will be automatically generated as the dialogue runs.

        Returns
        -------
        dialogue : Dialogue
            Returns the dialogue that is ready to be run.

    """
    user_policy = helpers.find_policy(dia_generator.user_policy_database[user],
                                      user_policies.GoDirectionPolicy
                                      )
    user_policy.agent = agent
    user_policy.direction = direction

    agent_policy = helpers.find_policy(dia_generator.agent_policy_database[agent],
                                       agent_policies.GoDirectionPolicy
                                       )

    dialogue = init_dialogue(dia_generator, user_policy, agent_policy,
                             entities_descriptions)

    return dialogue


def action_item(dia_generator, user, agent, user_pol_class, agent_pol_class,
                item, location=None, location_position=None,  entities_descriptions=None):
    """ Creates a dialogue between a user, an agent and the environment.
        The user issues a request using the user's self to the agent in the following manner:

            <user> says: <agent> <action> (preposition) <item> <preposition> <location>

        For example:

            Jim says: John look in the toys container in the bedroom.

        In this case, the user_pol_class is user_policies.LookItemPolicy
        The goal of the dialogue is for the agent to fulfill the user's request by making several utterances.

        Parameters
        ----------
        dia_generator : DialogueGenerator
            The class used for generating new dialogues.
        user : Entity
            The user that issues the request.
        agent : Entity
            The agent that needs to fulfill the user's request.
        user_pol_class : type
            The class type that is used to create an instance of the user self.
            The user policies can be found in the user_policies.py file.
        agent_pol_class : type
            The class type that is used to create an instance of the agent self.
            The agent policies can be found in the agent_policies.py file.
        item : Entity
            The item that the agent acts upon.
        location : Entity, optional
            The supposed location of the item. It does not have to be the correct one.
        location_position : str, optional
            The preposition that refers to the location. For example. in, under or on.
        entities_descriptions : dict (:class:`~pydialogue.environment.entities.Entity` : :class:`~pydialogue.environment.descriptions.BaseDescription`)
            A description for each of the entities that are part of the dialogue.
            Each entity can have different description.
            For example, the toys container can be described as the static container or the red container.
            If left None, entities descriptions will be automatically generated as the dialogue runs.

        Returns
        -------
        dialogue : Dialogue
            Returns the dialogue that is ready to be run.
    """

    user_policy = helpers.find_policy(dia_generator.user_policy_database[user],
                                      user_pol_class
                                      )
    user_policy.item = item
    user_policy.agent = agent
    user_policy.location = location
    user_policy.location_position = location_position
    agent_policy = helpers.find_policy(dia_generator.agent_policy_database[agent],
                                       agent_pol_class
                                       )

    dialogue = init_dialogue(dia_generator, user_policy,
                             agent_policy, entities_descriptions)

    return dialogue


def go_location(dia_generator, user, agent, item, location=None, location_position=None,  entities_descriptions=None):
    return action_item(dia_generator, user, agent, user_policies.GoLocationPolicy, agent_policies.GoLocationPolicy,
                       item, location, location_position, entities_descriptions)


def get_item(dia_generator, user, agent, item, location=None, location_position=None,  entities_descriptions=None):
    return action_item(dia_generator, user, agent, user_policies.GetItemPolicy, agent_policies.GetItemPolicy,
                       item, location, location_position, entities_descriptions)


def drop_item(dia_generator, user, agent, item, location=None, location_position=None,  entities_descriptions=None):
    return action_item(dia_generator, user, agent, user_policies.DropItemPolicy, agent_policies.DropItemPolicy,
                       item, location, location_position, entities_descriptions)


def look_item(dia_generator, user, agent, item, location=None, location_position=None,  entities_descriptions=None):
    return action_item(dia_generator, user, agent, user_policies.LookItemPolicy, agent_policies.LookItemPolicy,
                       item, location, location_position, entities_descriptions)


def item_prop_revealed(dia_generator,
                       item,
                       property_key,
                       property_val,
                       entities_descriptions=None):

    agent_policy = other_policies.ItemPropRevealedPolicy(item, property_key, property_val)

    dialogue = dia.Dialogue(dia_generator, entities_descriptions=entities_descriptions)
    dialogue.feedback = False
    env_policy = dia_generator.env_auto_policy
    if env_policy is None:
        return None

    env_policy.replace_dialogue(dialogue)

    dialogue.add_policies([agent_policy])

    dialogue.goal_generator = gen.GoalGenerator(agent_policy)

    return dialogue