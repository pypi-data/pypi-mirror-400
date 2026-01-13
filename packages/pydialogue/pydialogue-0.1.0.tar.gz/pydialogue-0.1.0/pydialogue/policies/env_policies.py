#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module lists the policies that the environment uses to provide feedback to the player.
"""
import logging
from abc import abstractmethod

from ..policies import base_policies as bpolicies
from ..language import components as lc
from ..environment import entities as em
from ..environment import actions
from ..environment import helpers as env_helpers
from ..language import sentences as tsentences
from ..language import desc_mappers

logger = logging.getLogger(__name__)


class EnvPolicy(bpolicies.Policy):
    """ The environment self provides a response to every player's action.
        The player is None, since the environment is not governed by any entity.
    """
    def __init__(self, dialogue=None):
        super().__init__(None, dialogue)
        self.dialogue = dialogue

    def execute(self, include_goal=False, last_utter=None):
        """
        Returns the environment response as feedback to the last utterance of the agent.

        Parameters
        ----------
        include_goal : bool, optional
            Whether to include the goal of the environment.
        last_utter : Sentence, optional
            If the last utterance is not provided, the last dialogue utterance is taken.

        Returns
        -------
        list
            Returns multiple valid environmental responses.
        None, optional
            The goal of the environment is None, since the goal is currently generated in the
            agent's self.
        """

        if last_utter is None:
            dia_utterances = self.dialogue.get_utterances()
            if len(dia_utterances) > 0:
                last_utter = dia_utterances[-1]
            else:
                last_utter = None

        if last_utter is None or len(last_utter.describers) == 0 or last_utter.speaker is None:
            responses = None
        else:
            try:
                responses = self.parse(last_utter=last_utter)
            except Exception as err:
                logger.error(err, exc_info=True)
                responses = None
        if include_goal:
            return responses, None
        return responses

    @abstractmethod
    def parse(self, last_utter):
        """
        Parses the utterance into an actions.<action> method call that provides the environment feedback.

        Parameters
        ----------
        last_utter : Sentence
            The utterance to be parsed.

        Returns
        -------
        res : Sentence
            Returns multiple valid environmental responses.
        """

    def get_steps(self, **params):
        """ Returns the valid responses of the environment """
        steps = self.execute(include_goal=False, **params)
        return steps

    def get_goal(self, **params):
        """ Returns the goal of the environment. The environment goal is None since
            the agents have goals.
        """
        return None

    def save_state(self):
        """
        Returns the state from the parent class and additionally the world state.
        The world state is returned since the environment's policies make changes
        in the world.

        """
        if self.dialogue is not None:
            state = self.dialogue.dia_generator.world.save_state()
        else:
            state = None
        return super().save_state(), state

    def recover_state(self, state):
        """ Recovers the parent state and the environment state. """
        super().recover_state(state[0])
        if self.dialogue is not None:
            self.dialogue.dia_generator.world.recover_state(state[1])


class EmptyPolicy(EnvPolicy):
    """ This self is used when a player issues an empty sentence (that does not contain any verbs or
        describers). """
    def parse(self, last_utter):
        """ Returns a sentence: <speaker> issued an empty response if the last speaker's utterance
            has no describers or no verb.
        """
        describers = last_utter.describers
        result = None
        if len(describers) == 0 or describers[0].get_arg('Rel') is None:
            result = tsentences.issue(last_utter.speaker,
                                      None,
                                      None,
                                      "issued",
                                      ["an", "empty", "response"]
                                      )
        return result


class GoPolicy(EnvPolicy):
    """ This self is used for providing feedback when a player tries moving in the world."""

    def parse(self, last_utter):
        """
        Parses the player's utterance into an actions.go method call that provides the environmental feedback.
        The utterance has to be in the form:

            <player> tries going <direction> (from_location)
        """
        world = self.dialogue.dia_generator.world
        inner_utter, player = env_helpers.extract_tries_sent(last_utter, world)

        if inner_utter is None or player is None:
            return None
        describer = inner_utter.describers[0]
        direction = describer.get_arg('AM-DIR')
        from_location = describer.get_arg('Arg-DIR')

        if inner_utter == tsentences.go(rel=('going', None),
                                        direction=(direction, None),
                                        source_location=(from_location, None)):

            if from_location is not None:
                if (isinstance(from_location, list) and len(from_location) == 2
                        and from_location[0] == "from" and isinstance(from_location[1], em.Entity)):
                    from_location = getattr(world, from_location[1].properties.get("var_name"), from_location)
                else:
                    return None

            if direction is not None and isinstance(direction, str):
                res = actions.go(player, direction, from_location)
                return res
        return None


class GetPolicy(EnvPolicy):
    """ This self is used for providing feedback when a player tries getting an entity in the world."""

    def parse(self, last_utter):
        """
        Parses the player's utterance into an actions.get method call that provides the environmental feedback.

        The utterance has to be in the form:

            <player> tries getting <entity> <location_preposition> <location>

        The location refers to the entity's location.
        For example, Hannah tries getting the plastic container under the table.
        Here the plastic container's location is under the table.

        """
        world = self.dialogue.dia_generator.world
        inner_utter, player = env_helpers.extract_tries_sent(last_utter, world)
        if inner_utter is None or player is None:
            return None
        describer = inner_utter.describers[0]
        entity = describer.get_arg('Arg-PPT')
        if not isinstance(entity, em.Entity):
            return None

        prep_location = describer.get_arg('Arg-DIR')
        res = None
        if (inner_utter == tsentences.get(rel=('getting', None),
                                          entity=(entity, None),
                                          prepos_location=(prep_location, None))):

            if (isinstance(prep_location, list) and len(prep_location) == 2
                    and isinstance(prep_location[0], str) and isinstance(prep_location[1], em.Entity)):
                location_position = prep_location[0]
                location = getattr(world, prep_location[1].properties.get("var_name"))

                res = actions.get(entity, player, location, location_position)
            elif prep_location is None:
                res = tsentences.be([entity, "'s", "location"],
                                    "is",
                                    None,
                                    ["absent", "in", "the", "sentence", last_utter])

        return res


class DropPolicy(EnvPolicy):
    """ This self is used for providing a response when a player tries dropping an entity in the world."""

    def parse(self, last_utter):
        """
            Parses the player's utterance into an actions.drop method call that provides the environmental feedback.
            The utterance has to be in the following form:

                <player> tries dropping <entity> <location_position> <location>

            The location refers to the one where the entity should be dropped.
            For example, The big person tries dropping the small ball in the toy's container.

        """
        world = self.dialogue.dia_generator.world
        inner_utter, player = env_helpers.extract_tries_sent(last_utter, world)
        if inner_utter is None or player is None:
            return None
        inner_desc = inner_utter.describers[0]
        entity = inner_desc.get_arg('Arg-PPT')
        if not isinstance(entity, em.Entity):
            return None
        prep_location = inner_desc.get_arg('Arg-GOL')
        res = None
        if (inner_utter == tsentences.drop(rel=('dropping', None),
                                           entity=(entity, None),
                                           prepos_location=(prep_location, None)
                                           )):
            if (isinstance(prep_location, list)
                    and len(prep_location) == 2 and isinstance(prep_location[0], str)
                    and isinstance(prep_location[1], em.Entity)):
                location_position = prep_location[0]
                location = getattr(world, prep_location[1].properties.get("var_name"))
                entity = getattr(world, entity.properties.get("var_name"))
                res = actions.drop(entity, player, location, location_position)
            elif prep_location is None:
                res = tsentences.be([entity, "'s", "location"],
                                    "is",
                                    None,
                                    ["absent", "in", "the", "sentence", last_utter])
        return res


class LookPolicy(EnvPolicy):
    """ This self provides a response when a player tries looking at an entity in the world."""

    def parse(self, last_utter):
        """
            Parses the player's utterance into an actions.look method call that provides the environmental feedback.

            The utterance has to be in the form:

                <player> tries looking <location_preposition1> <entity> <location_preposition2> <location>

            The location refers to the entity's location.
            For example, John tries looking in the toys container in the bedroom.
        """

        world = self.dialogue.dia_generator.world
        inner_utter, player = env_helpers.extract_tries_sent(last_utter, world)
        if inner_utter is None or player is None:
            return None
        inner_desc = inner_utter.describers[0]
        prep_thing_looked = inner_desc.get_arg('Arg-PPT')
        #item_location = inner_desc.get_arg('AM-LOC')

        if (inner_utter == tsentences.look(rel=('looking', None),
                                           thing_looked=(prep_thing_looked, None))):
            if len(prep_thing_looked) == 4:
                item_location = prep_thing_looked[2:4]
                prep_thing_looked = prep_thing_looked[0:2]
            else:
                item_location = None

            if (isinstance(prep_thing_looked, list) and len(prep_thing_looked) == 2
                    and isinstance(prep_thing_looked[0], str) and isinstance(prep_thing_looked[1], em.Entity)):
                look_position = prep_thing_looked[0]
                thing_looked = getattr(world, prep_thing_looked[1].properties.get("var_name"))
                if item_location is None:
                    res = tsentences.be([thing_looked, "'s", "location"],
                                        "is",
                                        None,
                                        ["absent", "in", "the", "sentence", last_utter])
                else:
                    res = actions.look(thing_looked, player, look_position,
                                       [item_location[0], getattr(world, item_location[1].properties.get("var_name"))])
                return res

        return None


class SayPolicy(EnvPolicy):
    """ This self provides a response when a player says a sentence """

    def parse(self, last_utter):
        """ Checks whether a sentence is in the format <user> says to <agent>: <inner_sentence>
            and if so, it returns an empty sentence with speaker=None.
            speaker=None indicates that the sentence is uttered by the environment.
            The empty sentence is returned because there is no need to implement actions.say.
            The agent can say anything, and the agent's utterance is anyway added to the context.
        """

        describer = last_utter.describers[0]
        user = describer.get_arg('Arg-PAG')
        if user != last_utter.speaker:
            return None

        mapped_sent = desc_mappers.say(last_utter.describers)
        if describer.get_arg("AM-NEG") is None and mapped_sent == last_utter:
            empty_sent = lc.Sentence()
            empty_sent.describers.append(lc.Describer())
            empty_sent.speaker = None
            return empty_sent
        return None


class EnvAutoPolicy(bpolicies.AutoPolicy):
    """ A self that automatically selects the right self out of a list of environmental policies. """

    def execute(self, include_goal=False, **params):
        """
            Runs the self and returns a list of valid environment responses.

            Additionally, the goal is returned if include_goal is set to True.
            If all the policies in self.list_policies return None, then the environment returns:

                <player> issued an unrecognizable sentence.

        """
        if "last_utter" in params:
            last_utter = params["last_utter"]
        else:
            dia_utterances = self.dialogue.get_utterances()
            if len(dia_utterances) > 0:
                last_utter = dia_utterances[-1]
            else:
                last_utter = None
            params['last_utter'] = last_utter

        if last_utter is not None and last_utter.speaker is not None:
            result = super().execute(include_goal, **params)

            if result is None:
                if len(last_utter.describers) > 0:
                    """
                    result = tsentences.issue(last_utter.speaker,
                                              None,
                                              None,
                                              "issued",
                                              ["a", "sentence", "with", "unexpected", "describer/s"]
                                              )
                    """
                    result = tsentences.be(None, "was", None, ["an", "error", "in", "the", "serialization"])
                    result.parts.insert(0, lc.Word("There"))
                else:
                    # the sent has no describers
                    """
                    result = tsentences.issue(last_utter.speaker,
                                              None,
                                              None,
                                              "issued",
                                              ["an", "sentence", "without", "describers"])
                    """

                    result = tsentences.be(None, "was", None, ["an", "error", "in", "the", "serialization"])
                    result.parts.insert(0, lc.Word("There"))
                not_inacc = tsentences.be(["The", "sentence"],
                                          "is",
                                          "not",
                                          "inaccurate")
                not_inacc.parts.insert(4, lc.Word("necessarily"))
                not_inacc.describers[0].args["AM-ADV"] = "necessarily"

                result = tsentences.cont([result, not_inacc])
        else:
            result = None

        if result is not None and last_utter.speaker is not None and 'player' not in last_utter.speaker.attr_seen:
            if isinstance(result, list):
                result[0].meta_sent.append(tsentences.be(last_utter.speaker, 'is', None, 'player'))
            else:
                result.meta_sent.append(tsentences.be(last_utter.speaker, 'is', None, 'player'))
        if include_goal is True and not isinstance(result, tuple):
            result = (result, None)

        return result
