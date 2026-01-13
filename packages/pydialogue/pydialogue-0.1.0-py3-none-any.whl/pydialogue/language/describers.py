#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module offers a list of functions that create instances of Describer-s.
"""
from . import components as lc


def say(
        user=(None, None),
        neg=(None, None),
        rel=(None, None),
        utterance=(None, None),
        agent=(None, None),
        prune=True
):
    """ Creates a Describer for the :func:`sentences.say() <pydialogue.language.sentences.say>` """

    describer = lc.Describer(
                             {"Arg-PAG": lc.Arg(user[0], user[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "Arg-PPT": lc.Arg(utterance[0], utterance[1]),
                              "Arg-GOL": lc.Arg(agent[0], agent[1])
                              },
                             prune)

    return describer


def know(knower=(None, None),
         neg=(None, None),
         rel=(None, None),
         fact_known=(None, None),
         prune=True):
    """ Creates a Describer for the :func:`sentences.know() <pydialogue.language.sentences.know>` """

    describer = lc.Describer(
                             {"Arg-PAG": lc.Arg(knower[0], knower[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "Arg-PPT": lc.Arg(fact_known[0], fact_known[1])},
                             prune)

    return describer


def go(
       goer=(None, None),
       mod=(None, None),
       neg=(None, None),
       rel=(None, None),
       direction=(None, None),
       start_point=(None, None),
       end_point=(None, None),
       prune=True
):
    """ Creates a Describer for the :func:`sentences.go() <pydialogue.language.sentences.go>` """

    describer = lc.Describer(
                             {"Arg-PPT": lc.Arg(goer[0], goer[1]),
                              "AM-MOD": lc.Arg(mod[0], mod[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "AM-DIR": lc.Arg(direction[0], direction[1]),
                              "Arg-DIR": lc.Arg(start_point[0], start_point[1]),
                              "Arg-GOL": lc.Arg(end_point[0], end_point[1])
                              },
                             prune
                             )

    return describer


def get(
        receiver=(None, None),
        mod=(None, None),
        neg=(None, None),
        rel=(None, None),
        thing_gotten=(None, None),
        giver=(None, None),
        prune=True
):
    """ Creates a Describer for the :func:`sentences.get() <pydialogue.language.sentences.get>` """

    desc = lc.Describer({"Arg-PAG": lc.Arg(receiver[0], receiver[1]),
                         "AM-MOD": lc.Arg(mod[0], mod[1]),
                         "AM-NEG": lc.Arg(neg[0], neg[1]),
                         "Rel": lc.RelArg(rel[0], rel[1]),
                         "Arg-PPT": lc.Arg(thing_gotten[0], thing_gotten[1]),
                         "Arg-DIR": lc.Arg(giver[0], giver[1])},
                        prune)
    return desc


def drop(player=(None, None),
         mod=(None, None),
         neg=(None, None),
         rel=(None, None),
         entity=(None, None),
         location=(None, None),
         prune=True):

    """ Creates a Describer for the :func:`sentences.drop() <pydialogue.language.sentences.drop>` """

    desc = lc.Describer({"Arg-PAG": lc.Arg(player[0], player[1]),
                         "AM-MOD": lc.Arg(mod[0], mod[1]),
                         "AM-NEG": lc.Arg(neg[0], neg[1]),
                         "Rel": lc.RelArg(rel[0], rel[1]),
                         "Arg-PPT": lc.Arg(entity[0], entity[1]),
                         "Arg-GOL": lc.Arg(location[0], location[1])},
                        prune)
    return desc


def look(player=(None, None),
         mod=(None, None),
         neg=(None, None),
         rel=(None, None),
         thing_looked=(None, None),
         prune=True):

    """ Creates a Describer for the :func:`sentences.look() <pydialogue.language.sentences.look>` """

    describer = lc.Describer({"Arg-PAG": lc.Arg(player[0], player[1]),
                              "AM-MOD": lc.Arg(mod[0], mod[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "Arg-PPT": lc.Arg(thing_looked[0], thing_looked[1])},
                              #"AM-LOC": lc.Arg(location[0], location[1])},
                             prune)
    return describer


def be(topic=(None, None),
       rel=(None, None),
       neg=(None, None),
       comment=(None, None),
       prune=True):
    """ Creates a Describer for the :func:`sentences.be() <pydialogue.language.sentences.be>` """

    describer = lc.Describer(
                             {"Arg-PPT": lc.Arg(topic[0], topic[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Arg-PRD": lc.Arg(comment[0], comment[1])
                              },
                             prune
                             )

    return describer


def have(owner=(None, None),
         rel=(None, None),
         neg=(None, None),
         possession=(None, None),
         location=(None, None),
         prune=True):
    """ Creates a Describer for the :func:`sentences.have() <pydialogue.language.sentences.have>` """

    describer = lc.Describer(
                             {"Arg-PAG": lc.Arg(owner[0], owner[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Arg-PPT": lc.Arg(possession[0], possession[1]),
                              "AM-LOC": lc.Arg(location[0], location[1])
                              },
                             prune
                             )

    return describer


def tries(entity_trying=(None, None),
          mod=(None, None),
          neg=(None, None),
          rel=(None, None),
          thing_tried=(None, None),
          prune=True):
    """ Creates a Describer for the :func:`sentences.tries() <pydialogue.language.sentences.tries>` """

    describer = lc.Describer({"Arg-PAG": lc.Arg(entity_trying[0], entity_trying[1]),
                              "AM-MOD": lc.Arg(mod[0], mod[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Arg-PPT": lc.Arg(thing_tried[0], thing_tried[1])},
                             prune
                             )

    return describer


def see(player=None, neg=(None, None), rel=(None, None),
        entity=(None, None), location=(None, None),  prune=True):
    """ Creates a Describer for the :func:`sentences.see() <pydialogue.language.sentences.see>` """

    see_desc = lc.Describer(
                            {"Arg-PAG": lc.Arg(player[0], player[1]),
                             "AM-NEG": lc.Arg(neg[0], neg[1]),
                             "Rel": lc.RelArg(rel[0], rel[1]),
                             "Arg-PPT": lc.Arg(entity[0], entity[1]),
                             "AM-LOC": lc.Arg(location[0], location[1])
                             },
                            prune)
    return see_desc


def permit(allowed_agent=(None, None), neg=(None, None), rel=(None, None),
           action_allowed=(None, None), allower=(None, None), prune=True):
    """ Creates a Describer for the :func:`sentences.permit() <pydialogue.language.sentences.permit>` """
    permit_desc = lc.Describer(
                               {"Arg-GOL": lc.Arg(allowed_agent[0], allowed_agent[1]),
                                "AM-NEG": lc.Arg(neg[0], neg[1]),
                                "Rel": lc.RelArg(rel[0], rel[1]),
                                "Arg-PPT": lc.Arg(action_allowed[0], action_allowed[1]),
                                "Arg-PAG": lc.Arg(allower[0], allower[1])
                                },
                               prune)

    return permit_desc


def reveal(revealer=(None, None), truth_cond=(None, None), neg=(None, None), rel=(None, None),
           prune=True):
    """ Creates a Describer for the :func:`sentences.reveal() <pydialogue.language.sentences.reveal>` """
    describer = lc.Describer({"Arg-PAG": lc.Arg(revealer[0], revealer[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "Arg-PPT": lc.Arg(truth_cond[0], truth_cond[1])},
                             prune)
    return describer


def issue(issuer=(None, None), mod=(None, None), neg=(None, None), rel=(None, None),
          thing_issued=(None, None), prune=True):
    """ Creates a Describer for the :func:`sentences.issue() <pydialogue.language.sentences.issue>` """
    describer = lc.Describer(
                             {"Arg-PAG": lc.Arg(issuer[0], issuer[1]),
                              "AM-MOD": lc.Arg(mod[0], mod[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "Arg-PPT": lc.Arg(thing_issued[0], thing_issued[1])},
                             prune)
    return describer


def want(wanter=(None, None), neg=(None, None), rel=(None, None),
         thing_wanted=(None, None), prune=True):
    """ Creates a Describer for the :func:`sentences.want() <pydialogue.language.sentences.want>` """

    describer = lc.Describer({"Arg-PAG": lc.Arg(wanter[0], wanter[1]),
                              "AM-NEG": lc.Arg(neg[0], neg[1]),
                              "Rel": lc.RelArg(rel[0], rel[1]),
                              "Arg-PPT": lc.Arg(thing_wanted[0], thing_wanted[1])},
                             prune)
    return describer
