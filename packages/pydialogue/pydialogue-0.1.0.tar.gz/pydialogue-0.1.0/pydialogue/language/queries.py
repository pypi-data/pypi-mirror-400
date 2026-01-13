#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides functions that create request sentences from parameters.
"""

from . import components as lc
from . import describers as tdescribers
from . import helpers as he


@he.auto_fill([6], ["speaker"])
def get(tmp=(None, None), player=(None, None), neg=(None, None), rel=(None, None),
        entity=(None, None), prepos_location=(None, None), speaker=None):
    """ Creates a request for the verb get in the following format:

            <tmp> <player> (neg) <get> <entity> <prepos_location>

        For example, "Hannah, get the book on the shelf."
    """
    from . import desc_mappers as dm

    if lc.verb_inf(rel[0]) != "get":
        return None
    get_res = lc.Sentence([tmp[1],
                           player[1],
                           lc.Word(","),
                           neg[1],
                           rel[1],
                           entity[1],
                           prepos_location[1],
                           lc.Word('.')], speaker=speaker)

    get_desc = tdescribers.get((None, None), (None, None), neg, rel,
                               entity, prepos_location)
    get_desc.args["AM-DIS"] = lc.Arg(player[0], player[1])
    if tmp[0] is not None:
        get_desc.args["AM-TMP"] = lc.Arg(tmp[0], tmp[1])
    get_res.describers = [get_desc]
    get_res.customizers["request_mapping"] = lc.Customizer(he.returns_same, {"sentence": get_res})
    get_res.customizers["desc_mapping"] = lc.Customizer(dm.get, {})

    return get_res


@he.auto_fill([6], ["speaker"])
def drop(tmp=(None, None), player=(None, None), neg=(None, None), rel=(None, None),
         entity=(None, None), prepos_location=(None, None), speaker=None):
    """ Creates a request for the verb drop in the following format:

            <tmp> <player> (neg) <drop> <entity> <prepos_location>

        where prepos_location refers to the target location.
        For example, "Max, drop the cup on the table."

    """
    from . import desc_mappers as dm

    if lc.verb_inf(rel[0]) != "drop":
        return None

    drop_res = lc.Sentence([tmp[1],
                            player[1],
                            lc.Word(","),
                            neg[1],
                            rel[1],
                            entity[1],
                            prepos_location[1],
                            lc.Word('.')],
                           speaker=speaker)

    drop_res_desc = tdescribers.drop((None, None), (None, None), neg, rel,
                                     entity, prepos_location)
    drop_res_desc.args["AM-DIS"] = lc.Arg(player[0], player[1])
    if tmp[0] is not None:
        drop_res_desc.args["AM-TMP"] = lc.Arg(tmp[0], tmp[1])

    drop_res.describers = [drop_res_desc]
    drop_res.customizers['request_mapping'] = lc.Customizer(he.returns_same, {"sentence": drop_res})
    drop_res.customizers["desc_mapping"] = lc.Customizer(dm.drop, {})

    return drop_res


@he.auto_fill([6], ["speaker"])
def look(tmp=(None, None), player=(None, None), neg=(None, None), rel=(None, None),
         thing_looked=(None, None), speaker=None):
    """ Creates a request for the verb look in the following format:

             <tmp> <player> (neg) <look> <thing_looked> <item_location>

        For example, "Max, look in the clothing drawer in the bedroom."
    """
    from . import desc_mappers as dm

    if lc.verb_inf(rel[0]) != "look":
        return None

    look_response = lc.Sentence([tmp[1],
                                 player[1],
                                 lc.Word(","),
                                 neg[1],
                                 rel[1],
                                 thing_looked[1],
                                 lc.Word('.')],
                                speaker=speaker)

    describer = tdescribers.look((None, None), (None, None), neg, rel,
                                 thing_looked, look_response)
    describer.args["AM-DIS"] = lc.Arg(player[0], player[1])
    if tmp[0] is not None:
        describer.args["AM-TMP"] = lc.Arg(tmp[0], tmp[1])
    look_response.describers = [describer]
    look_response.customizers["request_mapping"] = lc.Customizer(he.returns_same,
                                                                 {"sentence": look_response})
    look_response.customizers["desc_mapping"] = lc.Customizer(dm.look, {})

    return look_response


@he.auto_fill([7], ["speaker"])
def go(tmp=(None, None), player=(None, None), neg=(None, None), rel=(None, None),
       direction=(None, None), source_location=(None, None), target_location=(None, None), speaker=None):
    """ Creates a request for the verb go in the following format:

             <tmp> <player> (neg) <go> <direction> <source_location> <target_location>

        For example, "Andy, go north from the guest room."
    """

    from . import desc_mappers as dm

    if lc.verb_inf(rel[0]) != "go":
        return None

    go_res = lc.Sentence([tmp[1],
                          player[1],
                          lc.Word(","),
                          neg[1],
                          rel[1],
                          direction[1],
                          source_location[1],
                          target_location[1],
                          lc.Word('.')],
                         speaker=speaker)

    go_desc = tdescribers.go((None, None), (None, None), neg,
                             rel, direction, source_location,
                             target_location, go_res)
    go_desc.args["AM-DIS"] = lc.Arg(player[0], player[1])
    if tmp[0] is not None:
        go_desc.args["AM-TMP"] = lc.Arg(tmp[0], tmp[1])

    go_res.describers = [go_desc]
    go_res.customizers["request_mapping"] = lc.Customizer(he.returns_same, {"sentence": go_res})
    go_res.customizers["desc_mapping"] = lc.Customizer(dm.go, {})

    return go_res


def cont_connector(sentences, speaker=None, connector=None):
    """ Connects multiple requests in a single compound request using a connector. """
    from . import sentences as tsentences

    requests = []
    for sent in sentences:
        req = sent.run_customizer("request_mapping")
        requests.append(req)
    if connector is not None:
        res = tsentences.cont_and(requests, connector, speaker)
    else:
        res = tsentences.cont(requests, speaker)
    return res
