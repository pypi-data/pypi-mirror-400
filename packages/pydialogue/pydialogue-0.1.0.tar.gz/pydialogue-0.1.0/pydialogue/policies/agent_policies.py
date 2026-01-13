#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module lists the policies that the agent uses respond to the dialogue.
"""

import copy

from . import policies_helpers as phelpers
from ..language import helpers as lhelpers
from ..environment import helpers as em_helpers

from . import base_policies as bpolicies
from . import goals as tgoals
from ..state import kn_checkers

from ..language import queries
from ..language import sentences as tsentences

from ..language import components as lc
from ..environment import entities as em
from ..environment import actions


class GoLocationPolicy(bpolicies.ActionPolicy):
    """
    This class represents the agent's self when the user asks the agent to go to an object's location.

    Attributes
    ----------
    go_dir_policy : GoDirectionPolicy
        This self is used to compute the directions to the object's location.

    """
    def __init__(self, go_dir_policy, player=None, dialogue=None):
        super().__init__(player, None, dialogue=dialogue)
        self.go_dir_policy = go_dir_policy

    def parse(self, last_user_command):
        """ Parses the user request that comes from the self user_policies.GoLocPolicy
            in order to extract the necessary parameters to call self.task.
            Later it calls self.task with the extracted parameters to compute the agent's valid utterances and the goal.

            Parameters
            ----------
            last_user_command : Sentence
                One of the following requests (queries.go):

                    - <agent>, go to (a) <object>
                    - then <agent>, go to (a) <object>

                The second sentence is used in the AndPolicy.

            Returns
            -------
            steps : list
                The valid utterances.
            goal : Goal
                The goal of the agent self.player.
        """
        describer = last_user_command.describers[0]
        if describer.get_arg("Rel", _type=0).infinitive != "go":
            return None, None

        end_point_arg = describer.get_arg('Arg-GOL', _type=0)
        end_point = end_point_arg.value if end_point_arg else None
        go_to_location_query = queries.go(describer.get_arg("AM-TMP"),
                                          self.player,
                                          None, 'go', None, None, end_point)

        steps, goal = None, None
        if last_user_command == go_to_location_query:

            if (len(end_point) == 2
                    and isinstance(end_point[-1], em.BaseEntity)
                    and "abstract" in end_point[-1].attributes
                    and end_point[-2] == 'to'):
                can_not_go_res = tsentences.go(self.player, 'can', 'not', 'go',
                                               None, None, ['to', end_point[-1]], self.player)
                neg_res_func = lambda item, player=self.player: tsentences.go(player, 'can', 'not', 'go',
                                                                              None, None, ['to', item], player)
                steps, goal = self.one_task(end_point[-1],
                                            can_not_go_res,
                                            neg_res_func,
                                            last_user_command)
            elif len(end_point) == 2 and isinstance(end_point[1], em.Entity) and end_point[0] == 'to':
                steps, goal = self.task(getattr(self.dialogue.dia_generator.world,
                                                end_point[-1].get_property('var_name'),
                                                None))

        return steps, goal

    def task(self, item, prepos_location=None, preconditions=True):
        """
        Computes the steps that are necessary for self.player to
        successfully go to the location of the item. Furthermore, it
        computes the goal of self.player.


        Parameters
        ----------
        item : Entity
            The item's top location is used as the target location for the agent.
        prepos_location : list, optional
            If the prepos location is not None it is used as the target location for the agent.
            This is done in requests like get the apple in the kitchen and even though the location
            of the apple is not revealed, the kitchen's location is known.
        preconditions : bool, optional
            If True it checks whether all necessary entities for accomplishing the task have
            their location revealed.

        Returns
        -------
        steps : list
            The list of possible utterances for the agent self.player.
        goal : Goal
            The goal of the agent self.player.

        """
        can_not_go_res = tsentences.go(self.player, 'can', 'not', 'go',
                                       None, None, ['to',  item], self.player)

        prec_steps, prec_goal = None, None
        if preconditions:
            prec_items = [self.player, item]
            if prepos_location is not None:
                prec_items.append(prepos_location[1])

            prec_steps, prec_goal = phelpers.prec_action_item(self.dialogue, self.player,
                                                              prec_items, can_not_go_res)

        if prepos_location is None:
            target_loc = item.top_location()
        else:
            target_loc = prepos_location[1].top_location()

        source_loc = self.player.properties['location'][1]
        if (source_loc, target_loc) in self.dialogue.dia_generator.world.all_paths:
            dirs = self.dialogue.dia_generator.world.all_paths[(source_loc, target_loc)]
        else:
            dirs = None
        if dirs is not None and len(dirs) == 0:
            step = tsentences.be([self.player, "'s", 'location'], 'is', None, [target_loc.properties["location"][0], target_loc])
            say_step = tsentences.cont([can_not_go_res, step])
            say_step = tsentences.say(self.player, None, "says", say_step, speaker=self.player)

            if prec_steps is not None and self.dialogue.dia_generator.knowledge_base.check(step) is not True:
                steps = prec_steps
            else:
                steps = [say_step]
            goal = tgoals.Goal(tgoals.multiple_correct,
                               self.dialogue,
                               self.player,
                               steps,
                               len(self.dialogue.get_utterances()) - 1
                               )
        else:
            pr_steps = phelpers.path_revealed(self.dialogue, self.player,
                                              source_loc, target_loc, can_not_go_res)

            neg_responses = []
            steps_checked, steps_unchecked = [], []

            if dirs is not None and len(dirs) > 0:
                state = self.dialogue.dia_generator.world.save_state()
                for direction in dirs:
                    player_loc = self.player.properties['location'][1]
                    obs = None
                    list_undos = []
                    if (direction, 'obstacle') in player_loc.properties:
                        obs = player_loc.properties[(direction, 'obstacle')]
                        check_obstacle = kn_checkers.property_alt_checker(self.dialogue.dia_generator.knowledge_base,
                                                                          player_loc,
                                                                          (direction, "obstacle"),
                                                                          obs,
                                                                          None
                                                                          )
                        x_is_door = kn_checkers.property_alt_checker(self.dialogue.dia_generator.knowledge_base,
                                                                     obs,
                                                                   "type",
                                                                   "door",
                                                                     None)

                        if 'type' in obs.properties and obs.properties['type'] == 'door' and 'locked' in obs.attributes:
                            res = actions.go(self.player, direction)
                            neg_responses += res
                            del obs.attributes['locked']

                            def undo(obstacle=obs):
                                obstacle.attributes['locked'] = None

                            list_undos.append(undo)

                        if 'type' in obs.properties and obs.properties['type'] == 'door' and 'open' not in obs.attributes:
                            # this is only for doors
                            # if there is a door (indicated with the if above) and the agent does not know
                            # if its open, it should just go through.
                            if check_obstacle and x_is_door is not True:
                                res = actions.go(self.player, direction)
                                neg_responses += res
                            obs.attributes["open"] = None

                            def undo(obstacle=obs):
                                del obstacle.attributes['open']

                            list_undos.append(undo)

                    # here it might be the case that player is not at from_loc
                    # in case you use the optional arg from_loc in actions.go.
                    res = actions.go(self.player, direction)
                    # in case it does not progress further.
                    reduced_res = lhelpers.reduce_sentences([res[0]])

                    for und in reversed(list_undos):
                        und()

                    if em_helpers.check_can_not(reduced_res, "go"):
                        break

                if len(neg_responses) > 0:
                    reasons = phelpers.extract_reasons(neg_responses)

                    steps_checked, steps_unchecked = phelpers.compute_say_steps(reasons,
                                                                                neg_responses,
                                                                                self.player,
                                                                                self.dialogue.dia_generator.knowledge_base)
                if em_helpers.check_can_not(res, "go"):
                    reasons = phelpers.extract_reasons(res)

                    sc, su = phelpers.compute_say_steps(reasons,
                                                        res,
                                                        self.player,
                                                        self.dialogue.dia_generator.knowledge_base)
                    steps_checked += sc
                    steps_unchecked += su
                self.dialogue.dia_generator.world.recover_state(state)

            if prec_steps is None and pr_steps is None:
                if len(steps_checked) > 0:
                    steps = []
                    steps += steps_checked
                    phelpers.add_can_not(can_not_go_res, steps)

                    goal = tgoals.Goal(tgoals.multiple_correct,
                                       self.dialogue,
                                       self.player,
                                       steps_checked+steps_unchecked,
                                       len(self.dialogue.get_utterances()) - 1)

                else:
                    steps, _ = self.go_dir_policy.task(dirs[0])
                    if len(steps_unchecked) == 0:
                        goal = tgoals.Goal(tgoals.go_to_loc_goal, self.dialogue, self.player,
                                           target_loc, len(self.dialogue.get_utterances()) - 1)
                    else:
                        goal = tgoals.Goal(tgoals.multiple_correct,
                                           self.dialogue,
                                           self.player,
                                           steps_unchecked,
                                           len(self.dialogue.get_utterances()) - 1
                                           )
            else:
                if prec_steps is not None:
                    steps = prec_steps
                else:
                    steps = pr_steps
                goal = tgoals.Goal(tgoals.multiple_correct,
                                   self.dialogue,
                                   self.player,
                                   steps,
                                   len(self.dialogue.get_utterances()) - 1
                                   )
        return steps, goal

    def replace_dialogue(self, new_dialogue):
        """ Replaces the dialogue with a new dialogue. """
        super().replace_dialogue(new_dialogue)
        self.go_dir_policy.replace_dialogue(new_dialogue)

    def save_state(self):
        """ Saves the self state that changes with time. """
        parent_state = super().save_state()
        go_dir_state = self.go_dir_policy.save_state()

        return parent_state, go_dir_state

    def recover_state(self, state):
        """ Recovers the self state that changes with time. """
        parent_state, go_dir_state = state
        super().recover_state(parent_state)
        self.go_dir_policy.recover_state(go_dir_state)


class GoDirectionPolicy(bpolicies.BasePolicy):
    """ The agent's self when the user asks the agent to go in a direction.

        Attributes
        ----------
        initial_loc : Entity
            This is the location where the agent should try going in a specific direction.
    """
    def __init__(self, player=None, dialogue=None):
        super().__init__(player, dialogue)
        self.prev_user_command = None
        self.initial_loc = None
        self.obstacle_steps_func = phelpers.go_dir_obstacle_steps

    def parse(self, last_user_command):
        """
        Parses the user request outputted from the self user_policies.GoDirectionPolicy.
        Then it returns the list of possible utterances and the goal of the agent self.player.

        Parameters
        ----------
        last_user_command : Sentence
            One of the following requests (queries.go):

                - <agent>, go <direction>
                - then <agent>, go <direction>

            The second sentence is encountered in the user_policies.AndPolicy, and it is parsed in the agent_policies.AndPolicy

        Returns
        -------
        steps : list
            The valid utterances.
        goal : Goal
            The goal of the agent self.player.

        """
        describer = last_user_command.describers[0]
        direction = describer.get_arg('AM-DIR')
        if describer.get_arg("Rel", _type=0).infinitive != "go":
            return None, None

        go_to_direction_query = queries.go(describer.get_arg("AM-TMP"),
                                           self.player,  None, 'go', direction)
        steps, goal = None, None

        if last_user_command == go_to_direction_query:
            steps, goal = self.task(direction, last_user_command)

        return steps, goal

    def task(self, direction, last_user_command=None):
        """
        Computes the steps and the goal necessary for self.player
        successfully going in a specific direction.

        Parameters
        ----------
        direction : str
            The direction in which self.player is headed.
        last_user_command : Sentence
            The user's request is asking self.player to go <direction>.
            Refer to self.parse for the format of the sentence.
            If there is a new request, the initial location of the self.player is changed.

        """
        if last_user_command is not None:
            if self.prev_user_command is None or id(self.prev_user_command) != id(last_user_command):
                self.prev_user_command = last_user_command
                self.initial_loc = self.player.properties['location'][1]
            initial_loc = self.initial_loc
        else:
            initial_loc = self.player.properties['location'][1]

        tries_go_step = tsentences.tries(self.player, None, None, "tries",
                                         tsentences.go(rel='going',
                                                       direction=direction,
                                                       speaker=self.player),
                                         self.player)

        if direction in initial_loc.properties and initial_loc.properties[direction] == self.player.properties['location'][1]:
            player_moved_res = tsentences.go(self.player,
                                             None,
                                             None,
                                             'went',
                                             direction,
                                             ['from', initial_loc])

            steps = [tsentences.say(self.player, None, "says",
                                    player_moved_res, speaker=self.player)]
            goal_multiple = tgoals.Goal(tgoals.multiple_correct,
                                        self.dialogue,
                                        self.player,
                                        steps,
                                        len(self.dialogue.get_utterances()) - 1
                                        )
            return steps, goal_multiple

        state = self.dialogue.dia_generator.world.save_state()
        player_w = getattr(self.dialogue.dia_generator.world, self.player.properties['var_name'], None)
        orig_res = actions.go(player_w, direction, initial_loc)
        self.dialogue.dia_generator.world.recover_state(state)

        go_step = tsentences.go(self.player,
                                None,
                                None,
                                'goes',
                                direction,
                                ['from', initial_loc])

        steps = None
        goal = None

        if go_step != lhelpers.reduce_sentences([orig_res[0]])[0]:
            flattened_res = phelpers.extract_reasons(orig_res)
            obs_steps, obs_goal = self.obstacle_steps_func(self, direction, initial_loc)

            if len(obs_steps) > 0:
                steps, goal = obs_steps, obs_goal
            else:
                steps_checked, steps_not_checked = phelpers.compute_say_steps(flattened_res,
                                                                              orig_res,
                                                                              self.player,
                                                                              self.dialogue.dia_generator.knowledge_base)

                goal_multiple = tgoals.Goal(tgoals.multiple_correct,
                                            self.dialogue,
                                            self.player,
                                            steps_checked+steps_not_checked,
                                            len(self.dialogue.get_utterances()) - 1
                                            )

                if len(steps_checked) > 0:
                    player_loc = tsentences.be(([self.player, "'s", "location"], None),
                                               ("is", None),
                                               (None, None),
                                               ([initial_loc.properties["location"][0], initial_loc], None))
                    player_loc_checked = self.dialogue.dia_generator.knowledge_base.check(player_loc)
                    steps = []
                    # If the sentence contains the player's location, but the location is not revealed.
                    # this is just for the steps, the goal stays the same.
                    for step in steps_checked:
                        inner_step = step.describers[0].get_arg("Arg-PPT")
                        if player_loc in inner_step.meta_sent:
                            if player_loc_checked:
                                steps.append(step)
                        else:
                            steps.append(step)
                    if len(steps) > 0:
                        steps = steps_checked
                        goal = goal_multiple
                    else:
                        steps = None
                if steps is None:
                    steps = [tries_go_step]
                    goal = goal_multiple

        if steps is None:
            steps = [tries_go_step]
        if goal is None:
            goal = tgoals.Goal(tgoals.sent_in_reduced, self.dialogue, go_step, None, len(self.dialogue.get_utterances())-1)

        return steps, goal


class GoDirectionPolicyOld(bpolicies.ActionPolicy):
    """ The agent's self when the user asks the agent to go in a direction.

        Attributes
        ----------
        initial_loc : Entity
            This is the location where the agent should try going in a specific direction.
    """
    def __init__(self, player=None, dialogue=None):
        super().__init__(player, None, dialogue=dialogue)
        self.initial_loc = None

    def parse(self, last_user_command):
        """
        Parses the user request outputted from the self user_policies.GoDirectionPolicy.
        Then it returns the list of possible utterances and the goal of the agent self.player.

        Parameters
        ----------
        last_user_command : Sentence
            One of the following requests (queries.go):

                - <agent>, go <direction>
                - then <agent>, go <direction>

            The second sentence is encountered in the user_policies.AndPolicy, and it is parsed in the agent_policies.AndPolicy

        Returns
        -------
        steps : list
            The valid utterances.
        goal : Goal
            The goal of the agent self.player.

        """
        describer = last_user_command.describers[0]
        direction = describer.get_arg('AM-DIR')
        if describer.get_arg("Rel", _type=0).infinitive != "go":
            return None, None

        go_to_direction_query = queries.go(describer.get_arg("AM-TMP"),
                                           self.player,  None, 'go', direction)
        steps, goal = None, None

        if last_user_command == go_to_direction_query:
            steps, goal = self.task(direction, last_user_command)

        return steps, goal

    def task(self, direction, last_user_command=None):
        """
        Computes the steps and the goal necessary for self.player
        successfully going in a specific direction.

        Parameters
        ----------
        direction : str
            The direction in which self.player is headed.
        last_user_command : Sentence
            The user's request is asking self.player to go <direction>.
            Refer to self.parse for the format of the sentence.
            If there is a new request, the initial location of the self.player is changed.

        """

        if last_user_command is not None:
            if self.prev_user_command is None or id(self.prev_user_command) != id(last_user_command):
                self.prev_user_command = last_user_command
                self.initial_loc = self.player.properties['location'][1]
            initial_loc = self.initial_loc
        else:
            initial_loc = self.player.properties['location'][1]

        tries_go_step = tsentences.tries(self.player, None, None, "tries",
                                         tsentences.go(rel='going',
                                                       direction=direction,
                                                       speaker=self.player),
                                         self.player)

        if direction in initial_loc.properties and initial_loc.properties[direction] == self.player.properties['location'][1]:
            player_moved_res = tsentences.go(self.player,
                                             None,
                                             None,
                                             'went',
                                             direction,
                                             ['from', initial_loc])

            steps = [tsentences.say(self.player, None, "says",
                                    player_moved_res, speaker=self.player)]
            goal_multiple = tgoals.Goal(tgoals.multiple_correct,
                                        self.dialogue,
                                        self.player,
                                        steps,
                                        len(self.dialogue.get_utterances()) - 1
                                        )
            return steps, goal_multiple

        state = self.dialogue.dia_generator.world.save_state()
        player_w = getattr(self.dialogue.dia_generator.world, self.player.properties['var_name'], None)
        orig_res = actions.go(player_w, direction, initial_loc)
        self.dialogue.dia_generator.world.recover_state(state)

        go_step = tsentences.go(self.player,
                                None,
                                None,
                                'goes',
                                direction,
                                ['from', initial_loc])

        steps = None
        goal = None

        if go_step != lhelpers.reduce_sentences([orig_res[0]])[0]:
            flattened_res = phelpers.extract_reasons(orig_res)

            steps_checked, steps_not_checked = phelpers.compute_say_steps(flattened_res,
                                                                          orig_res,
                                                                          self.player,
                                                                          self.dialogue.dia_generator.knowledge_base)

            goal_multiple = tgoals.Goal(tgoals.multiple_correct,
                                        self.dialogue,
                                        self.player,
                                        steps_checked+steps_not_checked,
                                        len(self.dialogue.get_utterances()) - 1
                                        )

            if len(steps_checked) > 0:
                player_loc = tsentences.be(([self.player, "'s", "location"], None),
                                           ("is", None),
                                           (None, None),
                                           ([initial_loc.properties["location"][0], initial_loc], None))
                player_loc_checked = self.dialogue.dia_generator.knowledge_base.check(player_loc)
                steps = []
                # If the sentence contains the player's location, but the location is not revealed.
                # this is just for the steps, the goal stays the same.
                for step in steps_checked:
                    inner_step = step.describers[0].get_arg("Arg-PPT")
                    if player_loc in inner_step.meta_sent:
                        if player_loc_checked:
                            steps.append(step)
                    else:
                        steps.append(step)
                if len(steps) > 0:
                    steps = steps_checked
                    goal = goal_multiple
                else:
                    steps = None
            if steps is None:
                steps = [tries_go_step]
                goal = goal_multiple

        if steps is None:
            steps = [tries_go_step]
        if goal is None:
            goal = tgoals.Goal(tgoals.sent_in_reduced, self.dialogue, go_step, None, len(self.dialogue.get_utterances())-1)

        return steps, goal


class LookItemPolicy(bpolicies.ActionPolicy):
    """ The agent's self when the user requests the agent to look at an item. """

    def parse(self, last_user_command):
        """
        Parses the sentence last_user_command and checks if it matches the user
        request outputted from the self user_policies.LookItemPolicy.
        Then it returns the list of possible utterances and the goal of the agent self.player.

        Parameters
        ----------
        last_user_command : Sentence
            One of the following requests (queries.look):

                - <agent>, look <preposition> (a) <entity> <entity_location>
                - then <agent>, look <preposition> (a) <entity> <entity_location>

            where <preposition> is world.location_positions and <entity_location> is the location of the <entity>.
            The <entity_location> is the entity's location, and it is a list of two values:
            the first is a preposition in/on/under and the second value is an Entity.
            The second type of user request is encountered in the user_policies.AndPolicy and
            it is parsed in the agent_policies.AndPolicy


        """

        describer = last_user_command.describers[0]
        if describer.get_arg("Rel", _type=0).infinitive != "look":
            return None, None

        thing_looked_arg = describer.get_arg('Arg-PPT', _type=0)
        thing_looked = thing_looked_arg.value if thing_looked_arg else None

        look_query = queries.look(describer.get_arg("AM-TMP"),
                                  self.player, None, 'look', thing_looked)

        steps, goal = None, None
        if last_user_command == look_query:
            prepos = None
            if isinstance(thing_looked, list) and isinstance(thing_looked[-1], em.BaseEntity):
                if len(thing_looked) == 4:
                    location = thing_looked[2:4]
                    thing_looked = thing_looked[0:2]
                else:
                    location = None
                thing_looked_entity = thing_looked[-1]
                if location is not None:
                    location = [location[0], getattr(self.dialogue.dia_generator.world, location[1].get_property("var_name"))]
                if (len(thing_looked) == 2
                        and isinstance(thing_looked[-1], em.BaseEntity)
                        and "abstract" in thing_looked[-1].attributes
                        and thing_looked[-2] in self.dialogue.dia_generator.world.location_positions):
                    prepos = thing_looked[-2]
                    neg_res = tsentences.look(self.player,
                                              'can',
                                              'not',
                                              'look',
                                              [prepos, thing_looked_entity],
                                              self.player)

                    def neg_res_func(item, prepos=prepos, player=self.player):
                        res = tsentences.look(player,
                                              'can',
                                              'not',
                                              'look',
                                              [prepos, item],
                                              player)
                        return res

                    steps, goal = self.one_task(thing_looked_entity, neg_res, neg_res_func, last_user_command,
                                                thing_looked_prepos=prepos,
                                                prepos_location=location)
                elif (len(thing_looked) == 2
                      and isinstance(thing_looked[-1], em.Entity)
                      and thing_looked[-2] in self.dialogue.dia_generator.world.location_positions):
                    thing_looked_entity = getattr(self.dialogue.dia_generator.world, thing_looked_entity.get_property("var_name"))
                    prepos = thing_looked[-2]
                    steps, goal = self.task(thing_looked_entity, prepos, location)

        return steps, goal

    def task(self, item, thing_looked_prepos, prepos_location=None):
        """
        Computes the steps and the goal necessary for self.player
        successfully looking in/on/under an item.

        Parameters
        ----------
        item : Entity
            The entity that player looks at.
        thing_looked_prepos : str
            The preposition where the player looks. For example, this can be
            in/on/under. See world.location_positions
        prepos_location : list, optional
            The location of the item. The location does not necessarily have to be the top location.
            (read more env_main.top_loc)

        """
        can_not_look_res = tsentences.look(self.player,
                                           'can',
                                           'not',
                                           'look',
                                           [thing_looked_prepos, item],
                                           speaker=self.player)

        if prepos_location is not None:
            target_location = prepos_location
        else:
            target_location = copy.copy(item.properties['location'])

        action_params = (item, self.player, thing_looked_prepos, target_location)
        look_res = tsentences.look(self.player,
                                   None,
                                   None,
                                   'looks',
                                   [thing_looked_prepos, item]
                                   )

        look_step = tsentences.tries(self.player, None, None, "tries",
                                     tsentences.look(rel='looking',
                                                     thing_looked=[thing_looked_prepos,
                                                                   item]+target_location,

                                                     speaker=self.player),
                                     self.player)
        steps, goal = self.compute_policy_steps(item, can_not_look_res, target_location[1], prepos_location, actions.look, action_params, look_res, look_step)

        return steps, goal


class DropItemPolicy(bpolicies.ActionPolicy):
    """ The agent's self when the user asks the agent to drop an entity at a specific location. """

    def parse(self, last_user_command):
        """
        Parses the sentence last_user_command and checks if it matches the user
        request outputted from the self user_policies.DropPolicy.
        Then it returns the list of possible utterances and the goal of the agent self.player.

        Parameters
        ----------
        last_user_command : Sentence
            One of the following requests (queries.drop):

                - <agent>, drop (a) <entity> <target_location>
                - then <agent>, drop (a) <entity> <target_location>

            where the <target_location> is a list of two values: the first is a preposition in/on/under and
            the second value is an Entity.
            The second sentence form is used in the user_policies.AndPolicy.

        """
        dropper = self.player
        describer = last_user_command.describers[0]
        if describer.get_arg("Rel", _type=0).infinitive != "drop":
            return None, None

        thing_dropped_arg = describer.get_arg('Arg-PPT', _type=0)
        thing_dropped = thing_dropped_arg.value if thing_dropped_arg else None
        location_arg = describer.get_arg('Arg-GOL', _type=0)
        location = location_arg.value if location_arg else None
        drop_query = queries.drop(describer.get_arg("AM-TMP"), dropper, None, 'drop', thing_dropped, location)
        steps, goal = None, None
        if last_user_command == drop_query:
            if location is not None:
                location = [location[0],
                            getattr(self.dialogue.dia_generator.world, location[1].get_property("var_name"))]
            if isinstance(thing_dropped, em.BaseEntity) and "abstract" in thing_dropped.attributes:
                neg_res = tsentences.drop(self.player, 'can', 'not', 'drop',
                                          thing_dropped,
                                          location, self.player)

                def neg_res_func(item, player=self.player):
                    res = tsentences.drop(player, 'can', 'not', 'drop',
                                          item,
                                          speaker=self.player)
                    return res

                steps, goal = self.one_task(thing_dropped,
                                            neg_res,
                                            neg_res_func,
                                            last_user_command,
                                            prepos_location=location)
            elif isinstance(thing_dropped, em.Entity):
                thing_dropped_entity = getattr(self.dialogue.dia_generator.world, thing_dropped.get_property("var_name"))
                steps, goal = self.task(thing_dropped_entity, location)
        return steps, goal

    def task(self, item, prepos_location=None):
        """
        Computes the steps and the goal necessary for self.player
        successfully dropping the item at the target location.

        Parameters
        ----------
        item : Entity
            The entity to be dropped by self.player at the location.
        prepos_location : list, optional
            If provided, prepos_location is the target location where the item should be dropped.
            Otherwise, the target location will be the player's location.
            The prepos_location is a list of two values: the first is a preposition in/on/under, and the
            second value is an Entity.

        """
        can_not_drop_res = tsentences.drop(self.player,
                                           'can', 'not', 'drop',
                                           item, speaker=self.player)

        if prepos_location is None:
            target_location = copy.copy(self.player.properties["location"])
        else:
            target_location = prepos_location

        action_params = (item, self.player, target_location[1], target_location[0])

        drop_step = tsentences.tries(self.player, None, None, "tries",
                                     tsentences.drop(rel='dropping',
                                                     entity=item,
                                                     prepos_location=target_location,
                                                     speaker=self.player),
                                     speaker=self.player)
        drop_res = tsentences.drop(self.player, None, None, 'drops', item, target_location)
        steps, goal = self.compute_policy_steps(item, can_not_drop_res, target_location[1], prepos_location,
                                               actions.drop, action_params, drop_res, drop_step)

        return steps, goal


class GetItemPolicy(bpolicies.ActionPolicy):
    """ The agent's self when the user asks the agent to get an entity """

    def parse(self, last_user_command):
        """
        Parses the sentence last_user_command and checks if it matches the user
        request outputted from the self user_policies.GetItemPolicy.
        Then it returns the list of possible utterances and the goal of the agent self.player.

        Parameters
        ----------
        last_user_command : Sentence
            One of the following requests (queries.open or queries.close):

                - <agent>, get (a) <entity> <entity_location>
                - then <agent>, get (a) <entity> <entity_location>

            where the <entity_location> is the entity's location, and it is a list of two values:
            the first is a preposition in/on/under, and the second value is an Entity.
            The second sentence is encountered in the user_policies.AndPolicy.

        """
        describer = last_user_command.describers[0]
        if describer.get_arg("Rel", _type=0).infinitive != "get":
            return None, None
        getter = self.player
        thing_got_arg = describer.get_arg('Arg-PPT', _type=0)
        thing_got = thing_got_arg.value if thing_got_arg else None
        location_arg = describer.get_arg('Arg-DIR', _type=0)
        location = location_arg.value if location_arg else None
        get_query = queries.get(describer.get_arg("AM-TMP"), getter,  None, 'get', thing_got, location)
        steps, goal = None, None
        if last_user_command == get_query:

            if location is not None:
                location = [location[0], getattr(self.dialogue.dia_generator.world, location[1].get_property("var_name"))]

            if isinstance(thing_got, em.BaseEntity) and "abstract" in thing_got.attributes:
                can_not_get_res = tsentences.get(self.player,
                                                 'can',
                                                 'not',
                                                 'get',
                                                 thing_got,
                                                 location,
                                                 self.player)

                def neg_res_func(item, player=self.player):
                    res = tsentences.get(player,
                                         'can',
                                         'not',
                                         'get',
                                         item,
                                         speaker=player)
                    return res

                steps, goal = self.one_task(thing_got,
                                            can_not_get_res,
                                            neg_res_func,
                                            last_user_command,
                                            prepos_location=location)
            elif isinstance(thing_got, em.Entity):
                thing_got_entity = getattr(self.dialogue.dia_generator.world, thing_got.get_property('var_name'))
                steps, goal = self.task(thing_got_entity, location)
        return steps, goal

    def task(self, item, prepos_location=None):
        """

        Computes the steps and the goal necessary for self.player
        successfully getting the item at the target location.

        Parameters
        ----------
        item : Entity
            The entity to be taken by the agent.
        prepos_location : list
            The location of the item. The location does not necessarily have to be the top location. (read more entity.top loc)
            The entity's location is a list of two values:
            the first is a preposition in/on/under, and the second value is an Entity.

        """
        can_not_get_res = tsentences.get(self.player,
                                         'can',
                                         'not',
                                         'get',
                                         item,
                                         speaker=self.player)

        if prepos_location is None:
            target_location = copy.copy(item.properties["location"])
        else:
            target_location = prepos_location

        get_step = tsentences.tries(self.player,
                                    None,
                                    None,
                                    "tries",
                                    tsentences.get(rel='getting',
                                                   entity=item,
                                                   prepos_location=target_location,
                                                   speaker=self.player),
                                    self.player)
        get_res = tsentences.get(self.player, None, None, 'gets', item)
        action_params = (item, self.player, target_location[1], target_location[0])

        steps, goal = self.compute_policy_steps(item, can_not_get_res, target_location[1],
                                               prepos_location, actions.get, action_params, get_res, get_step)

        return steps, goal

