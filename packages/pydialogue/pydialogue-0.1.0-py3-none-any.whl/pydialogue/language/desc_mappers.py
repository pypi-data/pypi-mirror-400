#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains all functions that convert a specific Describer into the corresponding Sentence.

We decided to put a list of describers as an argument for each of the functions below, even though some
functions use only one describer. The reason is to be consistent among all functions.
"""
import functools

from . import sentences as tsentences
from . import queries as tqueries
from . import describers as tdescribers

from . import components as lc


def cont_connector(describers, database, connector=None):
    """ Creates multiple sentences from describers and
        joins them using a connector like "and". The end result is a single compound sentence.

    """
    res = None
    if len(describers) >= 2:

        sentences = []
        for desc in describers:
            sent = lc.Sentence()
            sent.describers = [desc]
            sentences.append(database.query_sentence(sent.describers))

        if None not in sentences:
            if connector is None:
                res = tsentences.cont(sentences)
            else:
                res = tsentences.cont_and(sentences, connector)

    return res


def validate_describers(func):
    @functools.wraps(func)
    def wrapper(describers, no_parts=True):
        """
        Wraps the describer mapper functions with preconditions
        that check whether the list of the describers contains at least one describer
        and also if a verb is present as a Describer argument.
        If no_parts is True, then the sentence.phrase_parts are left out.
        """
        if len(describers) == 0:
            return None

        rel = describers[0].get_arg("Rel")
        if rel is None:
            return None

        return func(describers, no_parts)
    return wrapper


@validate_describers
def get(describers, no_parts=True):
    """ Calls the :func:`sentences.get() <pydialogue.language.sentences.get>` with the arguments from the first Describer
        in the list of describers.
        If the argument AM-DIS argument is present, it calls the :func:`queries.get() <pydialogue.language.queries.get>`
        instead.
    """
    rel = describers[0].get_arg("Rel")

    if lc.verb_inf(rel.lower()) != "get":
        return None

    player = describers[0].get_arg("Arg-PAG")
    mod = describers[0].get_arg("AM-MOD")
    neg = describers[0].get_arg("AM-NEG")
    entity = describers[0].get_arg("Arg-PPT")
    giver = describers[0].get_arg("Arg-DIR")
    am_tmp = describers[0].get_arg("AM-TMP", _type=0)

    query_flag = False
    if player is None:
        am_dis = describers[0].get_arg("AM-DIS", _type=0)
        if am_dis is not None:
            query_flag = True

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.get((player, None), (mod, None), (neg, None),
                                    (rel, None), (entity, None), (giver, None))
        res.describers.append(describer)

        if query_flag:
            describer.args["AM-DIS"] = am_dis
            if am_tmp is not None:
                describer.args["AM-TMP"] = am_tmp

    else:
        if not query_flag:
            res = tsentences.get(player,  mod, neg, rel, entity,  giver)
        else:
            res = tqueries.get(am_tmp.value if am_tmp is not None else None,
                               am_dis.value, neg, rel, entity,  giver)
    return res


@validate_describers
def drop(describers, no_parts=True):
    """ Calls the :func:`sentences.drop() <pydialogue.language.sentences.drop>` with the arguments from the first Describer
        in the list of describers.
        If the argument AM-DIS argument is present, it calls the :func:`queries.drop() <pydialogue.language.queries.drop>`
        instead.
    """
    rel = describers[0].get_arg("Rel")
    if lc.verb_inf(rel.lower()) != "drop":
        return None

    player = describers[0].get_arg("Arg-PAG")
    query_flag = False
    if player is None:
        am_dis = describers[0].get_arg("AM-DIS", _type=0)
        if am_dis is not None:
            query_flag = True

    mod = describers[0].get_arg("AM-MOD")
    neg = describers[0].get_arg("AM-NEG")
    entity = describers[0].get_arg("Arg-PPT")
    location = describers[0].get_arg("Arg-GOL")
    am_tmp = describers[0].get_arg("AM-TMP", _type=0)

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.drop((player, None), (mod, None), (neg, None),
                                     (rel, None), (entity, None),
                                     (location, None))
        res.describers.append(describer)

        if query_flag:
            describer.args["AM-DIS"] = am_dis
            if am_tmp is not None:
                describer.args["AM-TMP"] = am_tmp

    else:
        if not query_flag:
            res = tsentences.drop(player,  mod, neg, rel, entity, location)
        else:
            res = tqueries.drop(am_tmp.value if am_tmp is not None else None,
                                am_dis.value, neg, rel, entity, location)
    return res


@validate_describers
def say(describers, no_parts=True):
    """ Creates a func:`sentences.say() <pydialogue.language.sentences.say>` from the first Describer
        of a list of describers """
    rel = describers[0].get_arg("Rel")

    if lc.verb_inf(rel.lower()) != "say":
        return None
    user = describers[0].get_arg("Arg-PAG")
    neg = describers[0].get_arg("AM-NEG")
    statement = describers[0].get_arg("Arg-PPT")
    agent = describers[0].get_arg("Arg-GOL")

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.say((user, None), (neg, None), (rel, None),
                                    (statement, None), (agent, None))
        res.describers.append(describer)
    else:
        res = tsentences.say(user, neg, rel, statement, agent)
    return res


@validate_describers
def see(describers, no_parts=True):
    """ Creates a `sentences.see() <pydialogue.language.sentences.see>` from the first Describer of a list of describers """
    rel = describers[0].get_arg("Rel")

    if lc.verb_inf(rel.lower()) != "see":
        return None

    player = describers[0].get_arg("Arg-PAG")
    neg = describers[0].get_arg("AM-NEG")
    entity = describers[0].get_arg("Arg-PPT")
    location = describers[0].get_arg("AM-LOC")

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.see((player, None), (neg, None),  (rel, None),
                                    (entity, None), (location, None))
        res.describers.append(describer)
    else:
        res = tsentences.see(player, neg, rel, entity, location)

    return res


@validate_describers
def look(describers, no_parts=True):
    """ Calls the :func:`sentences.look() <pydialogue.language.sentences.look>` with the arguments from the first Describer
        in the list of describers.
        If the argument AM-DIS argument is present, it calls the :func:`queries.look() <pydialogue.language.queries.look>`
        instead.
    """
    rel = describers[0].get_arg("Rel")

    if lc.verb_inf(rel.lower()) != "look":
        return None

    looker = describers[0].get_arg("Arg-PAG")
    query_flag = False
    if looker is None:
        am_dis = describers[0].get_arg("AM-DIS", _type=0)
        if am_dis is not None:
            query_flag = True

    mod = describers[0].get_arg("AM-MOD")
    neg = describers[0].get_arg("AM-NEG")
    rel = describers[0].get_arg("Rel")
    #location = describers[0].get_arg("AM-LOC")
    thing_looked = describers[0].get_arg("Arg-PPT")
    am_tmp = describers[0].get_arg("AM-TMP", _type=0)

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.look((looker, None), (mod, None), (neg, None),
                                     (rel, None), (thing_looked, None))
        res.describers.append(describer)

        if query_flag:
            describer.args["AM-DIS"] = am_dis
            if am_tmp is not None:
                describer.args["AM-TMP"] = am_tmp

    else:
        if not query_flag:
            res = tsentences.look(looker, mod, neg, rel, thing_looked)
        else:
            res = tqueries.look(am_tmp.value if am_tmp is not None else None,
                                am_dis.value, neg, rel, thing_looked)
    return res


@validate_describers
def go(describers, no_parts=True):
    """ Calls the :func:`sentences.go() <pydialogue.language.sentences.go>` with the arguments from the first Describer
        in the list of describers.
        If the argument AM-DIS argument is present, it calls the :func:`queries.go() <pydialogue.language.queries.go>`
        instead.
    """
    rel = describers[0].get_arg("Rel")

    if lc.verb_inf(rel.lower()) != "go":
        return None

    goer = describers[0].get_arg("Arg-PPT")

    query_flag = False
    if goer is None:
        am_dis = describers[0].get_arg("AM-DIS", _type=0)
        if am_dis is not None:
            query_flag = True

    mod = describers[0].get_arg("AM-MOD")
    neg = describers[0].get_arg("AM-NEG")

    direction = describers[0].get_arg("AM-DIR")
    start_point = describers[0].get_arg("Arg-DIR")
    end_point = describers[0].get_arg("Arg-GOL")

    am_tmp = describers[0].get_arg("AM-TMP", _type=0)

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.go((goer, None), (mod, None), (neg, None), (rel, None),
                                   (direction, None), (start_point, None),
                                   (end_point, None))
        res.describers.append(describer)

        if query_flag:
            describer.args["AM-DIS"] = am_dis
            if am_tmp is not None:
                describer.args["AM-TMP"] = am_tmp
    else:
        if not query_flag:
            res = tsentences.go(goer, mod, neg, rel, direction, start_point,  end_point)
        else:
            res = tqueries.go(am_tmp.value if am_tmp is not None else None,
                              am_dis.value, neg, rel, direction, start_point,  end_point)

    return res


@validate_describers
def be(describers, no_parts=True):
    """ Calls the :func:`sentences.be() <pydialogue.language.sentences.be>` with the arguments from the first Describer
        in the list of describers.
        If the argument AM-DIS argument is present, it calls the :func:`queries.be() <pydialogue.language.queries.be>`
        instead.
    """
    rel = describers[0].get_arg("Rel")

    if lc.verb_inf(rel.lower()) != "be":
        return None

    topic = describers[0].get_arg("Arg-PPT")
    neg = describers[0].get_arg("AM-NEG")
    comment = describers[0].get_arg("Arg-PRD")
    am_tmp = describers[0].get_arg("AM-TMP", _type=0)

    query_flag = False

    am_dis = describers[0].get_arg("AM-DIS", _type=0)
    if am_dis is not None:
        query_flag = True

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.be((topic, None), (rel, None),
                                   (neg, None), (comment, None))
        res.describers.append(describer)

        if query_flag:
            describer.args["AM-DIS"] = am_dis
            if am_tmp is not None:
                describer.args["AM-TMP"] = am_tmp
    else:
        if not query_flag:
            res = tsentences.be(topic, rel, neg, comment)
        else:
            res = tqueries.be(am_tmp.value if am_tmp is not None else None,
                              am_dis.value, topic, rel, neg, comment)

    return res


@validate_describers
def have(describers, no_parts=True):
    """ Creates a `sentences.have() <pydialogue.language.sentences.have>` from the first Describer of a list of describers.
    """
    rel = describers[0].get_arg("Rel")

    if lc.verb_inf(rel.lower()) != "have":
        return None

    owner = describers[0].get_arg("Arg-PAG")
    neg = describers[0].get_arg("AM-NEG")
    possession = describers[0].get_arg("Arg-PPT")
    location = describers[0].get_arg("AM-LOC")

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.have((owner, None),  (rel, None), (neg, None),
                                     (possession, None), (location, None))
        res.describers.append(describer)
    else:
        res = tsentences.have(owner, rel, neg, possession, location)

    return res


@validate_describers
def tries(describers, no_parts=True):
    """ Creates a `sentences.tries() <pydialogue.language.sentences.tries>`
        from the first Describer of a list of describers.
    """
    rel = describers[0].get_arg("Rel")
    if lc.verb_inf(rel.lower()) != "try":
        return None

    entity_trying = describers[0].get_arg("Arg-PAG")
    mod = describers[0].get_arg("AM-MOD")
    neg = describers[0].get_arg("AM-NEG")
    thing_tried = describers[0].get_arg("Arg-PPT")

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.tries((entity_trying, None), (mod, None), (neg, None),
                                      (rel, None), (thing_tried, None))
        res.describers.append(describer)
    else:
        res = tsentences.tries(entity_trying, mod, neg, rel, thing_tried)

    return res


@validate_describers
def know(describers, no_parts=True):
    """ Creates a `sentences.know() <pydialogue.language.sentences.know>`
        from the first Describer of a list of describers.
    """

    rel = describers[0].get_arg("Rel")
    if lc.verb_inf(rel.lower()) != "know":
        return None

    knower = describers[0].get_arg("Arg-PAG")
    neg = describers[0].get_arg("AM-NEG")
    fact_known = describers[0].get_arg("Arg-PPT")

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.know((knower, None), (neg, None),
                                     (rel, None), (fact_known, None))
        res.describers.append(describer)
    else:
        res = tsentences.know(knower, neg, rel, fact_known)

    return res


@validate_describers
def reveal(describers, no_parts=True):
    """ Creates a `sentences.reveal() <pydialogue.language.sentences.reveal>`
        from the first Describer of a list of describers. """

    rel = describers[0].get_arg("Rel")
    if lc.verb_inf(rel.lower()) != "reveal":
        return None

    revealer = describers[0].get_arg("Arg-PAG")
    neg = describers[0].get_arg("AM-NEG")
    truth_cond = describers[0].get_arg("Arg-PPT")

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.reveal((revealer, None), (neg, None),
                                       (rel, None), (truth_cond, None))
        res.describers.append(describer)
    else:
        res = tsentences.reveal(revealer, neg, rel, truth_cond)

    return res


@validate_describers
def permit(describers, no_parts=True):
    """ Creates a `sentences.permit() <pydialogue.language.sentences.permit>`
        from the first Describer of a list of describers. """

    rel = describers[0].get_arg("Rel")
    if lc.verb_inf(rel.lower()) != "permit":
        return None

    allower = describers[0].get_arg("Arg-PAG")
    neg = describers[0].get_arg("AM-NEG")
    action_allowed = describers[0].get_arg("Arg-PPT")
    allowed_agent = describers[0].get_arg("Arg-GOL")

    am_adv = describers[0].get_arg("AM-ADV", _type=0)

    if no_parts:
        res = lc.Sentence()
        describer = tdescribers.permit((allowed_agent, None), (neg, None),
                                       (rel, None), (action_allowed, None),
                                       (allower, None))
        res.describers.append(describer)

    else:
        res = tsentences.permit(action_allowed,  neg, rel, allower)
        if am_adv is not None:
            res.parts.append(am_adv.part)

    if am_adv is not None:
        res.describers[0].args["AM-ADV"] = am_adv

    return res


def empty(describers, no_parts=True):
    """ Creates an empty sentence that does not have any words.
        An empty sentence is identified by having no verb.
        The no_parts parameter is used to be consistent with the other desc mappers.
    """

    rel = describers[0].get_arg("Rel")
    if rel is None:
        sent = lc.Sentence()
        desc = lc.Describer()
        sent.describers += [desc]
        desc.args['Rel'] = lc.RelArg(None)
        return sent
    return None
