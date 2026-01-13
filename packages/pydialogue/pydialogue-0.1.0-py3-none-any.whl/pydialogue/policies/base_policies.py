#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module lists the self interface and other base policies that are inherited by the agent/user policies.
"""
from abc import ABC, abstractmethod

from . import policies_helpers as phelpers
from ..language import sentences as tsentences
from . import goals as tgoals
from ..state import kn_checkers

from ..environment import helpers as em_helpers
from ..environment import entities as em
from ..language import helpers as shelpers
from ..language import desc_mappers


class Policy(ABC):
    """
    This class sets up an interface that every self should implement.

    Attributes
    ----------
    player : Entity, optional
        The player or agent that acts according to the self. If None
        it is assumed that the environment responds.
    dialogue : Dialogue, optional
        The current dialogue that the self is part of.
    """
    def __init__(self, player=None, dialogue=None):
        self.player = player
        self.dialogue = dialogue

    @abstractmethod
    def execute(self, include_goal=False, **params):
        """
        Runs the self.

        Parameters
        ----------
        include_goal : bool
            If true, returns the goal. Otherwise, return only the steps.
        params : dict
            Additional parameters that might modify the behavior of the self.

        Returns
        -------
        steps : list
            Since there can be more than one valid response in a specific context,
            the list of valid responses is returned.
        goal : Goal, optional
            The goal of the self.
        """
        pass

    @abstractmethod
    def get_steps(self, **params):
        """ Returns the list of steps/valid utterances of the self. This function can be useful if
            the steps are computed separately from the goal. """
        pass

    @abstractmethod
    def get_goal(self, **params):
        """ Returns the goal of the self. This function can be useful if
            the goal is computed separately from the steps.
        """
        pass

    def replace_dialogue(self, new_dialogue):
        """ The dialogue is replaced when the self is part of a new dialogue. """
        self.dialogue = new_dialogue

    def save_state(self):
        """ Since the same self can change dialogues over time, the dialogue is returned. """
        return self.dialogue

    def recover_state(self, state):
        """ Recovers the dialogue in case it was changed over time. """
        self.replace_dialogue(state)


class BasePolicy(Policy, ABC):
    """ The base self is used in cases where the user issues a request to an agent and
        the agent has to return an appropriate response.
    """

    @abstractmethod
    def parse(self, last_user_command):
        """ Extracts the parameters of the user request necessary to compute the agent's self logic
            and implements the logic as well.

            Parameters
            ----------
            last_user_command : Sentence
                A user request sentence (queries.<x>) that does not mention the user. For example,
                     "Max, change the toy's color to red."
            Returns
            -------
            steps : list
                The list of valid responses.
            goal : Goal, optional
                The goal of the self.

        """
        pass

    def execute(self, include_goal=False, say_last_user_command=None, **params):
        """
        Runs the self.

        Parameters
        ----------
        include_goal : bool, optional
            Whether to include the self's goal or not. The default is False.
        say_last_user_command : Sentence, optional
            A say sentence in the following format responses.say(queries.<x>). For example,
            "Jim says: Max, change the toy's color to red!"
            If this sentence is not provided, the first dialogue utterance is expected to be the user's request.

        Returns
        -------
        steps : list
            A list of valid responses.
        goal : Goal, optional
            The goal of the self.
        """
        last_user_command = self.extract_inner_sentence(say_last_user_command)
        if last_user_command is not None:
            steps, goal = self.parse(last_user_command)
        else:
            steps, goal = None, None

        if include_goal:
            return steps, goal

        return steps

    def extract_inner_sentence(self, say_last_user_command=None):
        """
        Extract the inner sentence from the responses.say sentence.

        Parameters
        ----------
        say_last_user_command : Sentence, optional
            A say sentence in the following format responses.say(queries.<x>). For example,
            "Jim says: Max, change the toy's color to red."
            If it's not provided, the first dialogue utterance is expected to be the user's request.

        Returns
        -------
        last_user_command : Sentence
            The extracted inner sentence, if found. Otherwise, None is returned.

        """
        if not say_last_user_command:
            say_last_user_command = self.dialogue.utterances[0] if len(self.dialogue.utterances) > 0 else None

        last_user_command = phelpers.extract_inner_sent(say_last_user_command)
        if last_user_command is None or len(last_user_command.describers) > 1:
            return None
        describer = last_user_command.describers[0]
        player = describer.get_arg('AM-DIS')
        if player != self.player:
            return None
        return last_user_command

    def get_steps(self, **params):
        """ Returns the list of valid responses. """
        steps = self.execute(include_goal=False, **params)
        return steps

    def get_goal(self, **params):
        """ Returns the goal of the self. """
        _, goal = self.execute(include_goal=True, **params)
        return goal


class ActionPolicy(BasePolicy, ABC):

    def __init__(self, player=None, go_location_policy=None, action_item_obstacle_steps=None, dialogue=None):
        super().__init__(player, dialogue)
        self.go_location_policy = go_location_policy
        self.item = None
        self.prev_user_command = None
        if action_item_obstacle_steps is None:
            self.obstacle_steps_func = phelpers.action_item_obstacle_steps
        else:
            self.obstacle_steps_func = action_item_obstacle_steps

    def one_task(self, item, neg_response, neg_res_func, last_user_command,  **task_params):
        """
        Runs the agent's self for the following user request:

            <agent> <action> (preposition) a <item> <location>

        For example, "Max, look in a plastic container"

        The agent should accomplish the user request for one item that exists in the world
        and that fits the item's description provided by the user. This function calls self.task
        for each item that fits the description.

        In case the agent issues several steps but during the process
        it discovers that the action can not be done, then it should switch to another
        similar item. If the action is not possible for all the items that fit the description,
        then the neg_response should be outputted.

        Parameters
        ----------
        item : BaseEntity
            The item that describes the kind of object the agent should act upon. It contains
            the properties and attributes that describe the object. Additionally, it contains an 'abstract' attribute
            to indicate that it does not exist in the material world.
        neg_response : Sentence
            In case the action can not be achieved for all items in the world, a negative response (neg_response) is returned.
            An example is, "Hans can not get a big red item."
        neg_res_func : function
            A function that returns a negative response. For example, for the action get, this would be:
            <agent> can not get <object>. The neg_res_func requires only one argument because the <agent> is embedded
            in the sentence using self.player. This function is used to check if self.task returns a negative response.
        last_user_command : Sentence
            The last user request to the agent.
        **task_params : dict
            Additional self-specific parameters that might be required for execution.

        Returns
        -------
        steps : list
            A list of valid responses.
        goal : Goal
            The goal is to check if the action is successful for at least one of the items in the world.

        """
        if self.prev_user_command is None or id(last_user_command) != id(self.prev_user_command):
            self.reset()
            self.prev_user_command = last_user_command
        similar_items = self.dialogue.dia_generator.world.query_entity_from_db(item)
        counter = 0
        neg_goals_counter = 0
        goals = []
        list_steps = []
        item_list = []
        say_neg_response = tsentences.say(self.player, None, 'says',
                                          neg_response, speaker=self.player)

        """
        know_base = self.dialogue.dia_generator.knowledge_base
        new_similar_items = []
        for sitem in similar_items:
            result = True
            for elem in item.description.elements:
                if elem in sitem.properties and not kn_checkers.property_alt_checker(know_base, sitem, elem, sitem.properties[elem], None):
                    result = False
                if elem != 'abstract' and elem in sitem.attributes and not kn_checkers.property_alt_checker(know_base, sitem, None, elem, None):
                    result = False
            if result is True:
                new_similar_items.append(sitem)
        """
        for sitem in similar_items:
            steps, goal = self.task(item=sitem, **task_params)
            if not isinstance(steps, list):
                steps = [steps]
            neg_sent = neg_res_func(sitem)
            found_flag = phelpers.reduce_and_check_say(steps, neg_sent)
            if found_flag:
                counter += 1
                neg_goals_counter += 1
            else:
                if goal.func == tgoals.multiple_correct:
                    if len(goal.args) > 0:
                        goal_steps = goal.args[2]
                    elif "steps" in goal.kwargs:
                        goal_steps = goal.kwargs["steps"]
                    else:
                        goal_steps = []
                    if phelpers.reduce_and_check_say(goal_steps, neg_sent):
                        neg_goals_counter += 1
                goals.append(goal)
                list_steps.append(steps)
                item_list.append(sitem)

        if counter != len(similar_items):
            if neg_goals_counter == len(similar_items):
                goal = tgoals.Goal(tgoals.correct_steps_sublist, self.dialogue, self.player,
                                   [say_neg_response], len(self.dialogue.get_utterances()) - 1)
            else:
                goal = tgoals.Goal(tgoals.goal_or, goals)
            idx = None
            if self.item is not None:
                for item_idx, item_li in enumerate(item_list):
                    if item_li == self.item:
                        idx = item_idx
                        break
            if idx is None or self.item is None:
                idx = self.dialogue.dia_generator.random_gen.choice(range(len(list_steps)))
                self.item = item_list[idx]

            steps = list_steps[idx]
        else:
            steps = [say_neg_response]
            goal = tgoals.Goal(tgoals.correct_steps_sublist, self.dialogue, self.player,
                               steps, len(self.dialogue.get_utterances()) - 1)

        return steps, goal

    def compute_policy_steps(self, item, can_not_action_res,
                             target_location, prepos_location, action_func,
                             action_params, action_res, action_step):
        """
        Computes the next policy steps and the goal for the agent, given the current context.

        Computes the agent's response to the user request:

            <policy.player> <action> (preposition) <item> <preposition> <location>

        The general algorithm works in such a way that if the player has the knowledge that it can not execute the action,
        then it has to provide a response in the following form:

            <policy.player> says: neg_res

        In case multiple neg_res are possible, they are prioritized in the following way:

            1. The neg_res is because the <action> can not be executed for a specific reason.
            2. The neg_res is because the item's location is not revealed.
            3. The neg_res is because the GoItemPolicy returned negative response
               (due to an obstacle or when the path is not revealed)

        For example, if the request is: Hannah, get the static toys container,
        and it was previously revealed that static items are not gettable,
        it is not important whether the location of the toys container is revealed nor whether
        there is a path to the toys container since the entity is not gettable anyway.

        Note that in each of the 1..3 cases, there might be multiple responses as well. For this reason,
        the goal :func:`goals.multiple_correct() <pydialogue.policies.goals.multiple_correct>` is used.

        If the <action> can be executed by the agent, then it utters the next step
        that leads the agent closer to the goal. During the dialogue turn, just the
        first step is taken, so it suffices to provide a single step.


        Parameters
        ----------

        item : Entity
            The <item> in the user request.
        can_not_action_res : Sentence
            A sentence in the form: <policy.player> can not (preposition) <action> <item> <preposition> <location>
        target_location : Entity
            This is the location where the agent should go to act on the item.
            For example, for the action get, this is the item's location, and for the
            action drop, this is the location where the item should be dropped.
        prepos_location : list
            A list consisting of two elements, namely preposition (in, on, under) and location (Entity)
            This is the location where the item is supposedly at. Note that sometimes, prepos_location
            might not be the same as the target location. For example, the request can be: get the item <from_wrong_location>
            The prepos_location is allowed to be None as well.
        action_func : function
            A function that comes from the module environment.actions and is used to get the environment response.
        action_params : dict or tuple
            A dictionary mapping param_name: param_value, containing the parameters of the action_func or an ordered tuple
            (param_value1, param_value2 ...)
        action_res : Sentence
            A sentence in the form: <policy.player> <action> (preposition) <item> <preposition> <location>.
            It is used for checking whether the environment returns a positive response.
        action_step : Sentence
            The step in the form: <policy.player> tries (preposition) <action> <item> <preposition> <location>

        Returns
        -------
        steps : list
            The agent's next response. The list is in case multiple responses are valid.
        goal : Goal
            The goal of the agent's policy.

        """
        steps, goal = None, None
        import copy
        prec_items = [self.player, item]
        if prepos_location is not None:
            prec_items.append(prepos_location[1])

        prec_steps, prec_goal = phelpers.prec_action_item(self.dialogue, self.player, prec_items, can_not_action_res)

        go_steps, go_goal = self.go_location_policy.task(item, prepos_location, False)
        target_loc = target_location.top_location()
        loc_is_rev = tsentences.be(([self.player, "'s", 'location'], None),
                                   ('is', None),
                                   (None, None),
                                   ([target_loc.properties["location"][0], target_loc], None))

        if self.dialogue.dia_generator.knowledge_base.check(loc_is_rev):
            go_steps = []
            go_goal = tgoals.Goal(lambda: 1)

        sloc = self.player.properties['location'][1].top_location()
        tloc = target_loc

        state = self.dialogue.dia_generator.world.save_state()
        phelpers.make_item_reachable(self.player, sloc, tloc, self.dialogue.dia_generator.world)
        phelpers.open_all_containers(self.player, item, self.dialogue.dia_generator.world)
        orig_res = action_func(*action_params)
        self.dialogue.dia_generator.world.recover_state(state)

        if action_res != shelpers.reduce_sentences([orig_res[0]])[0]:
            flattened_res = phelpers.extract_reasons(orig_res)
            steps_checked, steps_not_checked = phelpers.compute_say_steps(flattened_res,
                                                                 orig_res,
                                                                 self.player,
                                                                 self.dialogue.dia_generator.knowledge_base)

            if len(steps_checked) > 0:
                steps = steps_checked
                goal = tgoals.Goal(tgoals.multiple_correct,
                                   self.dialogue,
                                   self.player,
                                   steps_not_checked + steps_checked,
                                   len(self.dialogue.get_utterances()) - 1)
                return steps, goal

        state = self.dialogue.dia_generator.world.save_state()
        phelpers.make_item_reachable(self.player, sloc, tloc, self.dialogue.dia_generator.world)
        orig_res = action_func(*action_params)
        self.dialogue.dia_generator.world.recover_state(state)

        substeps = []
        if action_res != shelpers.reduce_sentences([orig_res[0]])[0]:
            if prec_steps is None:
                substeps, goal = self.obstacle_steps_func(self, item)
                if len(substeps) == 0:
                    flattened_res = phelpers.extract_reasons(orig_res)
                    steps_checked, steps_not_checked = phelpers.compute_say_steps(flattened_res,
                                                                         orig_res,
                                                                         self.player,
                                                                         self.dialogue.dia_generator.knowledge_base)

                    goal_multiple = tgoals.Goal(tgoals.multiple_correct,
                                                self.dialogue,
                                                self.player,
                                                steps_not_checked + steps_checked,
                                                len(self.dialogue.get_utterances()) - 1
                                                )
                    if len(steps_checked) > 0:
                        steps = steps_checked
                        goal = goal_multiple

                        # The item can be still opened but the real reason is that it is not revealed.
                        # This is part of validate visibility if the item is inside container and the container is
                        # inside another container.

                        if prec_steps is not None:
                            if "container" in item.properties["location"][1].attributes:
                                for step in steps:
                                    inner_sentences = shelpers.reduce_sentences(
                                        [step.describers[0].get_arg('Arg-PPT')])[1:]

                                    for sent in inner_sentences:
                                        if sent == desc_mappers.be(sent.describers) and sent.describers[0].get_arg(
                                                'Arg-PRD') in ['open', 'openable', 'locked']:
                                            subj = sent.describers[0].get_arg("Arg-PPT")
                                            curr_loc = phelpers.check_loc(self.dialogue.dia_generator.knowledge_base,
                                                                 item,
                                                                 item.properties['location'])
                                            if curr_loc is not None:
                                                loc_path = []
                                                while True:
                                                    if curr_loc == curr_loc.properties['location'][1]:
                                                        break
                                                    loc_path.append(curr_loc)
                                                    curr_loc = curr_loc.properties['location'][1]

                                                if isinstance(subj,
                                                              em.Entity) and subj not in prec_items and subj in loc_path:
                                                    steps = prec_steps
                                                    goal = prec_goal
                                                    break
                    else:
                        if prec_steps is not None:
                            steps, goal = prec_steps, prec_goal
                        elif len(go_steps) > 0 and desc_mappers.say([go_steps[0].describers[0]]) == go_steps[
                            0] and em_helpers.check_can_not(
                                shelpers.reduce_sentences([go_steps[0].describers[0].get_arg('Arg-PPT')]), "go"):
                            steps, goal = go_steps, go_goal

                            phelpers.add_can_not(can_not_action_res, goal.args[2])
                        else:
                            steps = go_steps if len(go_steps) > 0 else [action_step]

                            # The steps_not_checked will be checked after the environment provides the negative response
                            # So the agent has to utter the reason why the action can not be completed.

                            goal = goal_multiple
        if steps is None:
            if prec_steps is not None:
                steps, goal = prec_steps, prec_goal
            elif len(go_steps) > 0 and desc_mappers.say([go_steps[0].describers[0]]) == go_steps[
                0] and em_helpers.check_can_not(
                    shelpers.reduce_sentences([go_steps[0].describers[0].get_arg('Arg-PPT')]), "go"):
                steps, goal = go_steps, go_goal

                phelpers.add_can_not(can_not_action_res, goal.args[2])
            else:
                substeps += [action_step]

        if goal is None:
            sub_goal = tgoals.Goal(tgoals.correct_steps_sublist, self.dialogue,
                                   self.player, substeps,
                                   len(self.dialogue.get_utterances()) - 1)
            goal = tgoals.Goal(tgoals.goal_and, [go_goal, sub_goal])
            steps = go_steps if len(go_steps) > 0 else [substeps[0]]

        return steps, goal

    def reset(self):
        """ Reset the state that the self modifies with time """
        if self.go_location_policy is not None:
            self.go_location_policy.reset()

        self.prev_user_command = None
        self.item = None

    def replace_dialogue(self, new_dialogue):
        """ Replace the dialogue with a new one.
            The GoLocation self's dialogue is replaced as well.
        """
        super().replace_dialogue(new_dialogue)
        if self.go_location_policy is not None:
            self.go_location_policy.replace_dialogue(new_dialogue)

    def save_state(self):
        """ Save the state that the self modifies with time """
        go_location_state = None
        if self.dialogue is not None:
            kb_state = self.dialogue.dia_generator.knowledge_base.save_state()
        else:
            kb_state = None
        if self.go_location_policy is not None:
            go_location_state = self.go_location_policy.save_state()

        return super().save_state(), go_location_state, self.item, self.prev_user_command, kb_state

    def recover_state(self, state):
        """ Recover the state that the self modifies with time """
        super().recover_state(state[0])
        if state[1] is not None:
            self.go_location_policy.recover_state(state[1])
        self.item = state[2]
        self.prev_user_command = state[3]
        if self.dialogue is not None:
            self.dialogue.dia_generator.knowledge_base.recover_state(state[4])


class AutoPolicy(Policy):
    """
    This class allows the automatic selection of the right policies (in case there are multiple).
    The criterion for selection is if the policies output
    a response or a goal that is not None when executed.

    Attributes
    ----------
    list_policies : list
        A list of instances that inherit the Policy class.
    dialogue : Dialogue
        An instance of the class Dialogue.

    """

    def __init__(self, list_policies, dialogue):
        player = list_policies[0].player if len(list_policies) > 0 else None
        super().__init__(player, dialogue)
        self.list_policies = list_policies
        self.replace_dialogue(self.dialogue)

    def parse(self, **params):
        """ Iterates through all policies in the list_policies and
            returns the ones that outputs a step or a goal.
            If multiple policies output a valid response, then all the responses
            are returned and their goals are merged into one or_goal. """
        valid_res = []
        valid_goals = []
        for pol in self.list_policies:
            if self != pol:
                steps, goal = pol.execute(include_goal=True, **params)
                if steps is not None:
                    if isinstance(steps, list):
                        valid_res += steps
                    else:
                        valid_res.append(steps)
                if goal is not None:
                    valid_goals.append(goal)

        if len(valid_goals) > 1:
            valid_goal = tgoals.goal_or(valid_goals)
        elif len(valid_goals) == 1:
            valid_goal = valid_goals[0]

        if len(valid_res) == 0:
            valid_res = None
        if len(valid_goals) == 0:
            valid_goal = None

        return valid_res, valid_goal

    def execute(self, include_goal=False, **params):
        """
        Runs the self.

        Parameters
        ----------
        include_goal : bool, optional
            Whether to include the goal of the self. The default is False.
        **params : dict
            Additional parameters that some policies in self.list_policies
            might require.

        Returns
        -------
        steps : list
            The list of valid utterances.
        goal : Goal, optional
            The goal of the self.

        """
        steps, goal = self.parse(**params)
        if include_goal:
            return steps, goal
        return steps

    def get_steps(self, **params):
        """ Returns the valid utterances of the self. """
        steps = self.execute(include_goal=False, **params)
        return steps

    def get_goal(self, **params):
        """ Returns the goal of the self. """
        _, goal = self.execute(include_goal=True, **params)
        return goal

    def reset(self):
        """ Reset all the policies in list_policies. """
        for pol in self.list_policies:
            if self != pol:
                pol.reset()

    def replace_dialogue(self, new_dialogue):
        """ Replaces the dialogue in the class and also the dialogue in all the policies
            that are part of the AutoPolicy. """
        self.dialogue = new_dialogue
        for pol in self.list_policies:
            if pol != self:
                pol.replace_dialogue(new_dialogue)

    def save_state(self):
        """ Save all the policies states in a list. """
        policies_state = []
        for pol in self.list_policies:
            if self != pol:
                policies_state.append(pol.save_state())
            else:
                policies_state.append(None)

        return policies_state

    def recover_state(self, policies_state):
        """ Recover all the policies' states from a list. """
        for idx, pol_state in enumerate(policies_state):
            pol = self.list_policies[idx]
            if self != pol:
                pol.recover_state(pol_state)
