#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains the functions that check whether the information exists in the KnowledgeBase.
"""
import copy

from . import kn_helpers
from . import kn_parsers
from ..environment import entities as em
from ..language import sentences as tsentences


def basic_checker(kb_state, sent):
    """
    Checks whether a sentence with the same meaning is present in the database.

    Parameters
    ----------
    kb_state : KnowledgeBase
        The knowledge base that contains the set of truthful sentences.
    sent : Sentence
        This sentence is checked against the database.

    Returns
    -------
    is_true : bool
        True is returned if the sentence is present
        False is returned if the sentence with the opposite meaning is present.
        None is returned if the sentence is not present.

    """
    is_true = None

    if sent in kb_state.sent_db:
        is_true = True

    oppos_sent = kn_helpers.create_oppos_sent(sent)
    if oppos_sent in kb_state.sent_db:
        is_true = False

    return is_true


def property_checker(kb_state, sent):
    """
    Checks whether the sentence is in one of the following forms:

        - <entity> 's <property_key> is <property_val>
        - <entity> is <attribute>

    and if so, extracts the arguments and calls
    the :func:`property_check_alt() <pydialogue.state.kn_checkers.property_check_alt>` function.
    The :func:`property_check_alt() <pydialogue.state.kn_checkers.property_check_alt>` checks whether
    the sentence is truthful and whether the information it conveys is visible to the agents.

    Parameters
    ----------
    kb_state : KnowledgeBase
        The knowledge base that is used for testing the truthfulness of the sentence
    sent : Sentence
        The sentence that is checked.

    Returns
    -------
    has_prop : bool or None
        Returns True if the sentence is truthful. Otherwise, False.
        If the information is not visible to the agent, None is returned regardless of the truthfulness of the sentence.

    """
    has_prop = None

    mem = kn_helpers.check_prop(sent)

    if mem is not None:
        ent, pkey, pval, pneg = mem
        has_prop = property_alt_checker(kb_state, ent, pkey, pval, pneg)

    return has_prop


def property_alt_checker(kb_state, ent, pkey, pval, pneg):
    """
    Checks whether the entity's (property_key, property_value) is the correct one and whether the property value
    is seen by the agent.

    Additionally, this function can be used to check whether the entity's attribute
    exists and whether is seen by the agent.

    Parameters
    ----------
    kb_state : KnowledgeBase
        The kb_state.world is used for getting the most recent version of the entity
        (in case there are copies of the entity)
    ent : Entity
        The entity which property is checked.
    pkey : str or tuple or None
        The property key. If pkey is None, then the existence of an attribute is checked.
    pval : any
        The property value or the attribute.
    pneg : str or None
        pneg indicates whether to check for equality or inequality

    Returns
    -------
    result : bool or None
        Returns True if the entity's pkey is pval and pneg is None or entity's pkey is not pval and pneg is not None.
        Otherwise, False is returned.
        If the information is not visible to the agent in the context, None is returned regardless of the truthfulness.

    """
    if ((pkey is not None and not isinstance(pkey, str) and not isinstance(pkey, tuple))
            or (pkey is None and not isinstance(pval, str) and not isinstance(pval, tuple))):
        return None

    world_ent = getattr(kb_state.world, ent.get_property("var_name"), None)
    if world_ent is None:
        return None

    result = None
    if pkey is not None:
        if pkey in world_ent.prop_seen:
            result = world_ent.prop_seen[pkey] == pval
        else:
            if pkey in world_ent.prop_seen_neg and pval in world_ent.prop_seen_neg[pkey]:
                result = False
    else:
        if pval in world_ent.attr_seen:
            result = True
        elif pval in world_ent.attr_seen_neg:
            result = False

    if result is not None:
        if pneg is not None and pneg in ['no', 'not']:
            result = not result
    return result


def multiple_prop_checker(kb_state, sent):
    mem = kn_helpers.check_prop(sent)

    if mem is not None:
        ent, pkey, pval, pneg = mem
        if isinstance(pval, set):
            list_eval = []
            for val in pval:
                has_prop = property_alt_checker(kb_state, ent, pkey, val, pneg)
                list_eval.append(has_prop)

            if all(list_eval):
                return True
            elif False in list_eval:
                return False


def elem_exists_checker(kb_state, sent):
    """
    Checks whether the sentence is in the form described in kn_parsers.elem_exists_parse
    and if so, extracts the arguments and calls the
    :func:`check_elem_exists_alt() <pydialogue.state.kn_checkers.check_elem_exists_alt>` function.
    The :func:`check_elem_exists_alt() <pydialogue.state.kn_checkers.check_elem_exists_alt>`
    checks whether the entity's element (property or attribute) exists and
    whether the existence is visible to the agents.

    Parameters
    ----------
    kb_state : KnowledgeBase
        The knowledge base is used for testing the truthfulness of the sentence.
    sent : Sentence
        The sentence to check for truthfulness.

    Returns
    -------
    elem_exists : bool or None
        Returns True if the sentence is truthful. Otherwise, False.
        If the information that the sentence conveys is not previously seen by the agent, None is returned regardless
        of the truthfulness.

    """
    parsed = kn_parsers.elem_exists_parse(sent)
    elem_exists = None
    if parsed is not None:
        ent, elem, pneg = parsed
        elem_exists = elem_exists_alt_checker(kb_state, ent, elem, pneg)
    return elem_exists


def elem_exists_alt_checker(kb_state, ent, elem, pneg):
    """
    Checks whether the entity's property key or attribute exists and is seen by the agent in the context.

    Parameters
    ----------
    kb_state : KnowledgeBase
        The kb_state.world is used for getting the most recent version of the entity
        (in case a copy of the entity is provided)
    ent : Entity
        The entity whose element existence is checked.
    elem : str or tuple
        The property key or the attribute
    pneg : str or None
        pneg indicates whether to check for equality or inequality

    Returns
    -------
    result : bool
        True if the element exists and pneg is None, or the element does not exist and pneg is not None.
        Otherwise, False is returned.
        If the element's existence is not seen by the agent in the context, None is returned.
    """

    world_ent = getattr(kb_state.world, ent.get_property("var_name"), None)
    if world_ent is None:
        return None

    result = None
    if elem is not None:

        if (elem in world_ent.elem_exists
                or elem in world_ent.prop_seen
                or elem in world_ent.attr_seen):
            result = True
        elif elem in world_ent.elem_not_exists:
            result = False
    if result is not None and pneg is not None and pneg in ['no', 'not']:
        result = not result

    return result


def have_checker(kb_state, sent):
    """
    Checks whether an object has items on/under/in it and whether the agent has seen this information.

    Parameters
    ----------
    kb_state : KnowledgeBase
        The knowledge base is used to check the validity of the sentence.
    sent : Sentence
        The sentence has to be in the form described in kn_parsers.have_parse.

    Returns
    -------
    is_true : bool or None
        True if the sentence is truthful. Otherwise, False.
        If the information that the sentence conveys is not seen by the agent, None is returned, regardless
        of the truthfulness of the sentence.

    """
    is_true = None

    mem = kn_parsers.have_parse(sent)
    if mem is not None:
        owner, possession, neg, loc = mem
        if loc is None:
            loc = ['in', owner]
        results = []
        if isinstance(owner, em.Entity):
            if possession == "items" and neg is not None and neg in ['no', 'not']:
                objs = kb_state.world.obj_list
            else:
                if possession is None:
                    possession = []
                elif isinstance(possession, set):
                    possession = list(possession)
                elif not isinstance(possession, list):
                    possession = [possession]
                objs = possession

            for obj in objs:
                if not isinstance(obj, em.Entity):
                    return None
                res = property_alt_checker(kb_state, obj, "location", loc, neg)
                results.append(res)
            if len(results) > 0 and all(results):
                is_true = True

            elif False in results:
                is_true = False

    return is_true


def val_is_key_checker(kb_state, sent):
    """ Checks whether the agent has seen the following sentences in the meta context:

        ..

            <property_value> is (not) <property_key>

            or

            <str> is (not) direction.

        For example, "medium is not a color".

    """
    if len(sent.describers) > 0:
        describer = sent.describers[0]
        arg_ppt = describer.get_arg("Arg-PPT")
        arg_prd = describer.get_arg("Arg-PRD")
        am_neg = describer.get_arg("AM-NEG")
        if (arg_ppt is None or arg_prd is None or
                sent != tsentences.be((arg_ppt, None), ("is", None), (am_neg, None), (arg_prd, None))):
            return None
        if isinstance(arg_prd, list):
            arg_prd = tuple(arg_prd)

        additional_prds = [('player', prop) for prop in ['name', 'nickname', 'surname']]
        if arg_prd not in kb_state.world.all_properties+['direction']+additional_prds:
            return None

        result = None
        all_keys = []
        for obj in kb_state.world.obj_list:
            for key, val in obj.prop_seen.items():
                if val == arg_ppt:
                    all_keys.append(key)
        if len(all_keys) > 0:
            if am_neg == 'not':
                result = not (arg_prd in all_keys)
            elif am_neg is None:
                result = arg_prd in all_keys
        if result is None:
            result = basic_checker(kb_state, sent)
        return result
