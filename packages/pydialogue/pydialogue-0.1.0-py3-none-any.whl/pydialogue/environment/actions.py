#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module lists all functions the environment uses to provide feedback to the player.
"""
import copy

from ..language import helpers as lhelpers
from ..language import sentences as tsentences
from ..language import components as lc

from . import helpers as em_helpers


def go(player, direction, from_location=None):
    """
    Returns the environment response when a player tries moving in a direction from a certain location.

    Parameters
    ----------
    player : Entity
        The player that tries moving.
    direction : str
        The direction of movement. This can be north, east, northeast, ... and so on.
        If the string is not a direction or the direction is not present in player.properties['location']
        a negative response is returned.
    from_location : Entity
        The location where the player is.
        If the from_location is not the correct one, a negative feedback is provided.


    Returns
    -------
    log : list
        A list of valid responses.

    """
    if from_location is None:
        from_location = player.properties["location"][1]

    can_not_go_res = tsentences.go(player,
                                   'can', 'not', 'go',
                                   direction)

    log = []

    visibility = player.validate_reachability(player, from_location, can_not_go_res)
    log += visibility

    obstacle = player.properties['location'][1].properties.get((direction, 'obstacle'))

    if obstacle is not None:
        obs_loc = tsentences.be([player.properties['location'][1], "'s", direction, 'obstacle'], 'is', None, obstacle)
        meta_dir_exists = tsentences.have(from_location, 'has', None, ['direction', direction])
        player_loc = tsentences.be([player, "'s", "location"], "is", None, player.properties['location'])

        if 'type' in obstacle.properties and obstacle.properties['type'] == 'door' and 'open' not in obstacle.attributes:
            res_not_open = tsentences.be(obstacle, 'is', 'not', 'open')
            if 'locked' in obstacle.attributes:
                res_locked = tsentences.be(obstacle, 'is', None, 'locked')
                cont_res = tsentences.cont([can_not_go_res,  obs_loc, res_locked])
                cont_res.meta_sent.append(meta_dir_exists)
                cont_res.meta_sent.append(player_loc)

                log.append(cont_res)

            elif 'openable' not in obstacle.attributes:
                res_not_openable = tsentences.be(obstacle, 'is', 'not', 'openable')
                cont_res = tsentences.cont([can_not_go_res, obs_loc, res_not_openable])
                cont_res.meta_sent.append(meta_dir_exists)
                cont_res.meta_sent.append(player_loc)

                log.append(cont_res)

            else:
                cont_res = tsentences.cont([can_not_go_res, obs_loc, res_not_open])
                cont_res.meta_sent.append(meta_dir_exists)
                cont_res.meta_sent.append(player_loc)

                log.append(cont_res)
    if player.world.check_val_is_key('direction', direction) is False:
        log.append(tsentences.be(direction, "is", "not", "direction"))
    elif direction not in player.properties['location'][1].properties:
        player_loc = tsentences.be([player, "'s", "location"], "is", None, player.properties['location'])
        dir_not_exists = tsentences.have(player.properties['location'][1], 'has', 'no', ['direction', direction])
        cont_res = tsentences.cont([can_not_go_res, dir_not_exists])
        cont_res.meta_sent.append(player_loc)
        log.append(cont_res)
    else:
        new_location = player.properties['location'][1].properties[direction]

    if len(log) == 0:
        new_location.objects.append(player)
        old_location = player.properties['location'][1]
        old_location_objs = copy.copy(old_location.objects)
        old_location.objects.remove(player)
        player.properties['location'][1] = new_location
        player.properties['location'][0] = new_location.properties["location"][0]

        def undo(pla=player, old_loc=old_location, old_loc_pos=old_location.properties["location"][0], old_loc_objs=old_location_objs):
            pla.properties['location'][1].objects.remove(pla)
            pla.properties['location'][1] = old_loc
            pla.properties['location'][0] = old_loc_pos
            del pla.properties['location'][1].objects[:]
            pla.properties['location'][1].objects.extend(old_loc_objs)

        player.undo_changes.append(undo)
        intro_location_res = look(new_location, player,
                                  new_location.properties["location"][0], player.properties['location'])
        player_moved_res = tsentences.go(player,
                                         None,
                                         None,
                                         'goes',
                                         direction,
                                         ['from', old_location])

        response = [player_moved_res] + [intro_location_res]
        log = [tsentences.cont(response)]
    return log


def get(entity, player, location, location_position):
    """
    Returns the environment response after the player tries getting the entity at the location.

    Parameters
    ----------
    entity : Entity
        The entity that the player tries taking.
    player : Entity
        The player that tries taking the entity.
    location : Entity
        The location where the entity is found.
    location_position : str
        The location position where the entity is found. For example: on, in, under

    Returns
    -------
    list
        The list of valid responses. If the entity is not gettable, a negative response is returned.

    """

    prepos_location = [location_position, location]

    can_not_get_res = tsentences.get(player,  'can', 'not', 'get', entity)

    log = []
    visibility = entity.validate_reachability(player, location, can_not_get_res)
    log += visibility

    if entity.properties['location'] != prepos_location:
        res = tsentences.be([entity, "'s", 'location'], 'is', 'not', prepos_location)
        res = tsentences.cont([can_not_get_res, res])
        log.append(res)

    if 'static' in entity.attributes:
        res = tsentences.be(entity, 'is', None, 'static')
        res = tsentences.cont([can_not_get_res, res])
        log.append(res)

    if 'player' in entity.attributes:
        res = tsentences.be(entity, 'is', None, 'player')
        getting_players = tsentences.get(rel="getting", entity="players")
        del getting_players.parts[-1]
        res1 = tsentences.permit(action_allowed=getting_players, neg="not", rel="permitted")

        res = tsentences.cont([can_not_get_res, res, res1])
        log.append(res)

    if entity.properties['location'] == ['in', player]:
        res = tsentences.be([entity, "'s", 'location'], "is", None, ['in', player])
        res = tsentences.cont([can_not_get_res, res])
        log.append(res)

    if len(log) == 0:
        old_loc_position = entity.properties['location'][0]
        old_loc_objects = copy.copy(location.objects)
        player.objects.append(entity)
        location.objects.remove(entity)
        entity.properties['location'][1] = player
        entity.properties['location'][0] = "in"
        res = tsentences.get(player, None, None, 'gets', entity)

        def undo(ent=entity, old_location=location, old_loc_pos=old_loc_position, old_loc_objs=old_loc_objects):
            ent.properties['location'][1].objects.remove(ent)
            ent.properties['location'][1] = old_location
            ent.properties['location'][0] = old_loc_pos
            del old_location.objects[:]
            old_location.objects.extend(old_loc_objs)

        entity.undo_changes.append(undo)

        log.append(res)

    return log


def drop(entity, player, location, location_position):
    """
    Returns the environment response after the player tries dropping the entity at the location.

    Parameters
    ----------
    entity : Entity
        The entity that the player tries dropping.
    player : Entity
        The player that tries dropping the entity.
    location : Entity
        It represents the location where the entity should be dropped.
    location_position : str
        The preposition refers to the target location. For example: in, on, under.

    Returns
    -------
    list
        The list of valid responses. If the entity can not be dropped, a negative response is returned.

    """

    can_not_drop_res = tsentences.drop(player, 'can', 'not', 'drop', entity)

    log = []

    visibility = location.validate_reachability(player, location, can_not_drop_res)

    log += visibility

    if entity.properties['location'] != ['in', player]:
        item_not_inventory_res = tsentences.be([entity, "'s", 'location'], 'is', 'not', ['in', player])
        log.append(tsentences.cont([can_not_drop_res, item_not_inventory_res]))
    if entity == location:
        entity.random_gen.shuffle(entity.world.location_positions)
        entity_part = lhelpers.convert_obj_to_part(["the", "item"])
        entity_part += lhelpers.convert_obj_to_part(em_helpers.join_el_conn(set(entity.world.location_positions), ",", "or"))
        entity_part += lhelpers.convert_obj_to_part(["itself"])
        dropping_players = tsentences.drop(rel="dropping",
                                           entity=(["the", "item", set(entity.world.location_positions), "itself"],
                                                   entity_part))
        del dropping_players.parts[-1]
        not_permitted = tsentences.permit(action_allowed=dropping_players, neg="not", rel="permitted")
        log.append(tsentences.cont([can_not_drop_res, not_permitted]))

    loc_path = em_helpers.item_path(location)
    if entity in loc_path:
        sub_log = []
        for ent in loc_path:
            if ent == entity:
                break
            sub_log.append(tsentences.be([ent, "'s", "location"], "is", None, ent.properties["location"]))
        if len(sub_log) > 0:
            log.append(tsentences.cont([can_not_drop_res]+sub_log))
    if location_position == 'in':
        if 'container' not in location.attributes and 'enclosed' not in location.attributes and 'player' not in location.attributes:
            list_attr = ['container', 'enclosed', 'player']
            entity.random_gen.shuffle(list_attr)
            item_is_not = tsentences.be(location, 'is', 'not',
                                        (set(list_attr), lhelpers.convert_obj_to_part(em_helpers.join_el_conn(list_attr, ",",
                                                                                              "or"))))

            log.append(tsentences.cont([can_not_drop_res, item_is_not]))
        elif 'container' in location.attributes and entity > location:
            log.append(tsentences.cont([can_not_drop_res,
                                        tsentences.be([entity, "'s", "size"], "is", None, entity.properties['size']),
                                        tsentences.be([location, "'s", "size"], "is", None, location.properties['size']),
                                        ]))

    elif location_position == 'on':
        if 'supporter' not in location.attributes and 'surface' not in location.attributes:
            list_attr = ['supporter', 'surface']
            entity.random_gen.shuffle(list_attr)
            item_is_not = tsentences.be(location, 'is', 'not',
                                        (set(list_attr),
                                         lhelpers.convert_obj_to_part(em_helpers.join_el_conn(list_attr, ",",
                                                                                              "or")))
                                         )
            log.append(tsentences.cont([can_not_drop_res, item_is_not]))
    elif location_position == 'under':
        if ('hollow', 'under') not in location.attributes:
            item_is_not_hollow = tsentences.be(location, 'is', 'not', ['hollow', 'under'])
            log.append(tsentences.cont([can_not_drop_res, item_is_not_hollow]))
    else:
        list_loc_pos = entity.world.location_positions
        entity.random_gen.shuffle(list_loc_pos)
        loc_pos_res = tsentences.be(['The', 'location', 'position'],
                                    'is',
                                    'not',
                                    (set(list_loc_pos), lhelpers.convert_obj_to_part(em_helpers.join_el_conn(list_loc_pos,",",
                                                                                                             "or"))))
        log.append(loc_pos_res)

    if len(log) == 0:
        old_loc_objects = copy.copy(player.objects)
        player.objects.remove(entity)
        location.objects.append(entity)
        entity.properties['location'][1] = location
        old_loc_pos = entity.properties['location'][0]
        entity.properties['location'][0] = location_position
        drop_res = tsentences.drop(player,
                                   None,
                                   None,
                                   'drops',
                                   entity,
                                   [location_position, location])

        def undo(enti=entity, old_location=player, old_location_position=old_loc_pos, old_loc_objs=old_loc_objects):
            enti.properties['location'][1].objects.remove(enti)
            enti.properties['location'][1] = old_location
            enti.properties['location'][0] = old_location_position
            del old_location.objects[:]
            old_location.objects.extend(old_loc_objs)

        entity.undo_changes.append(undo)
        log.append(drop_res)

    return log


def objects_loc_pos(entity, location_preposition):
    """ Returns the entity's objects that have a specific location preposition.

        For example, if the carrot's location is ['on', kitchen_table] then the carrot's location preposition is 'on'.
        If the <entity> is the kitchen_table and the location_preposition is "on", then the carrot will be part of the
        returned objects.
    """
    holder_objects = list()
    for obj in entity.objects:
        if obj.properties['location'][0] == location_preposition:
            holder_objects.append(obj)

    if len(holder_objects) > 1:
        entity.random_gen.shuffle(holder_objects)
        num_items = entity.random_gen.randint(1, len(holder_objects))
        holder_objects = holder_objects[0:num_items]
    set_objects = set(holder_objects)

    if len(holder_objects) == 1:
        holder_objects = holder_objects[0]
        set_objects = list(set_objects)[0]
    elif len(holder_objects) == 0:
        holder_objects = None
        set_objects = None

    return holder_objects, set_objects


def look_place(entity, player, location_preposition):
    """
    Returns the environment response after a player looks in a place.

    Parameters
    ----------
    entity : Entity
        The entity that the player looks in. The entity has to be a place (have attribute 'place').
    player : Entity
        The player that looks.
    location_preposition : str
        The preposition has to be 'in' in order to return a non-empty response.

    Returns
    -------
    list
        A list comprising one sentence indicating the objects that the player sees in the place.
    """

    if 'place' not in entity.attributes:
        return []
    else:
        #if ('surface' in entity.attributes and location_preposition != 'on') or ('enclosed' in entity.attributes and location_preposition != 'in'):
        #    return []
        if not ((location_preposition == 'on' and 'surface' in entity.attributes) or
                (location_preposition == 'in' and 'enclosed' in entity.attributes)):
            return []

    log = []
    objects, set_objects = objects_loc_pos(entity, location_preposition)

    if objects is None:
        place_is_empty_res = tsentences.have(entity,
                                             'has',
                                             'no',
                                             'items',
                                             [location_preposition, entity])
        log.append(place_is_empty_res)
    else:
        log.append(tsentences.see(player,
                                  None,
                                  'sees',
                                  (set_objects,
                                   lhelpers.convert_obj_to_part(em_helpers.join_el_conn(objects, ",")))))

    return log


def look_supporter(entity, location_preposition):
    """
    Returns the environment response after a player looks on top of the entity.

    Parameters
    ----------
    entity : Entity
        The entity that the player looks on. The entity has to have the attribute 'supporter'.
    location_preposition : str
        The preposition has to be 'on' in order to return a non-empty response.

    Returns
    -------
    list
        A list comprising a single sentence outputting what items the entity has on top of it or outputting that the entity
        contains no items.

    """
    if 'supporter' not in entity.attributes or location_preposition != 'on':
        return []
    supporter_objects, set_objects = objects_loc_pos(entity, location_preposition)
    if supporter_objects is not None:

        contains_res = tsentences.have(entity,
                                       'has',
                                       None,
                                       (set_objects,
                                        lhelpers.convert_obj_to_part(em_helpers.join_el_conn(supporter_objects, ","))),
                                       [location_preposition, entity])
        return [contains_res]

    does_not_have = tsentences.have(entity,
                                    'has',
                                    'no',
                                    'items',
                                    [location_preposition, entity])
    return [does_not_have]


def look_container(entity, location_preposition, can_not_look_res):
    """
    Returns the environment response after a player looks in the container entity.

    Parameters
    ----------
    entity : Entity
        The entity that the player looks in. The entity has to be a supporter (have attribute 'container').
    location_preposition : str
        The preposition has to be 'in' in order to return a non-empty response.
    can_not_look_res : Sentence
        The sentence "<player> can not look in <entity>" is used if looking in the container is not possible.
        For example, this can happen if the container is not opened or the container is locked.

    Returns
    -------
    list
        A list comprising a single sentence outputting what items the entity has in it or outputting that the entity
        contains no items.

    """
    if 'container' not in entity.attributes or location_preposition != 'in':
        return []
    if 'locked' in entity.attributes:
        container_is_locked = tsentences.be(entity, 'is', None, 'locked')
        res = [can_not_look_res, container_is_locked]
        return res

    if 'open' in entity.attributes:
        container_objects, set_objects = objects_loc_pos(entity, location_preposition)
        if container_objects is not None:
            contains_res = tsentences.have(entity,
                                           'has',
                                           None,
                                           (set_objects,
                                            lhelpers.convert_obj_to_part(em_helpers.join_el_conn(container_objects, ","))),
                                           [location_preposition, entity])
            return [contains_res]
        container_is_empty_res = tsentences.have(entity,
                                                 'has',
                                                 'no',
                                                 'items',
                                                 [location_preposition, entity])
        return [container_is_empty_res]

    container_is_closed_res = tsentences.be(entity, 'is', 'not', 'open')
    return [can_not_look_res, container_is_closed_res]


def look_hollow(entity, location_preposition):
    """
    Returns the environment response after a player looks under a hollow entity.

    Parameters
    ----------
    entity : Entity
        The entity should have an attribute hollow.
    location_preposition : str
        The location position should be 'under', otherwise empty list is returned.

    Returns
    -------
    list
        A comprising a single sentence outputting what items the entity has under it or outputting that the entity
        has no items under.
    """

    if ('hollow', 'under') not in entity.attributes or location_preposition != 'under':
        return []
    objects_under, set_objects = objects_loc_pos(entity, location_preposition)
    if objects_under is not None:
        contains_res = tsentences.have(entity,
                                       'has',
                                       None,
                                       (set_objects,
                                        lhelpers.convert_obj_to_part(em_helpers.join_el_conn(objects_under, ","))),
                                       [location_preposition, entity])
        return [contains_res]

    does_not_have = tsentences.have(entity,
                                    'has',
                                    'no',
                                    'items',
                                    [location_preposition, entity])
    return [does_not_have]


def look_object_response(entity, player, location_position, can_not_look_res):
    """
    Finds the suitable response when the player looks in/on/under the entity depending on the entity's properties and attributes.
    For example, if the entity is a table (which is a supporter) and the location preposition is 'on',
    then the look_supporter function is called, and the items that are on top of the table are given
    as part of the environmental response.

    If there is no suitable response found, the sentence: There is nothing special about <entity> is returned.

    Parameters
    ----------
    entity : Entity
        The entity that the player looks in/on/under.
    player : Entity
        The player that performs the look action.
    location_position : str
        A location preposition: in, on, or under.
    can_not_look_res : Sentence
        The sentence is used if looking at the entity is not possible. For example,
        "<player> can not look <location_preposition> entity"

    Returns
    -------
    log : list
        A list of one or multiple sentences. These sentences represent a single response (not multiple valid ones).
        Inside the :func:`look() <pydialogue.environment.actions.look>` function, the sentences are merged
        into a single one using the function :func:`cont() <pydialogue.language.sentences.cont>`.
    """
    log = []
    look_res = tsentences.look(player,
                               None,
                               None,
                               'looks',
                               [location_position, entity]
                               )

    if 'type' in entity.properties and entity.properties['type'] == 'door' and location_position == 'at':
        if 'open' not in entity.attributes:
            res = tsentences.be(entity, "is", "not", "open")
        else:
            res = tsentences.be(entity, "is", None, "open")

        log += [res]

    place_res = look_place(entity, player, location_position)
    if len(place_res) > 0:
        return [look_res] + place_res

    log += look_inventory(entity, location_position)
    log += look_supporter(entity, location_position)
    log += look_container(entity, location_position, can_not_look_res)
    log += look_hollow(entity, location_position)

    if len(log) == 0:
        if location_position == 'in':
            list_attr = ['container', 'enclosed', 'player']
            if all(attr not in entity.attributes for attr in list_attr):
                entity.random_gen.shuffle(list_attr)
                res = tsentences.be(entity, 'is', 'not',
                                        (set(list_attr), lhelpers.convert_obj_to_part(em_helpers.join_el_conn(list_attr, ",",
                                                                                              "or"))))
                log.append(res)
            """
            for attr in ['container', 'enclosed', 'player']:
                if attr not in entity.attributes:
                    res = tsentences.be(entity, 'is', 'not', attr)
                    log += [res]
            """
        elif location_position == 'on':
            list_attr = ['supporter', 'surface']
            if all(attr not in entity.attributes for attr in list_attr):
                entity.random_gen.shuffle(list_attr)
                res = tsentences.be(entity, 'is', 'not',
                                    (set(list_attr), lhelpers.convert_obj_to_part(em_helpers.join_el_conn(list_attr, ",",
                                                                                                         "or"))))
                log.append(res)
        elif location_position == 'under':
            if ('hollow', 'under') not in entity.attributes:
                item_is_not_hollow = tsentences.be(entity, 'is', 'not', ['hollow', 'under'])
                log += [item_is_not_hollow]
        if len(log) != 0:
            log.insert(0, can_not_look_res)
        else:
            nothing_special_res = tsentences.be((None, lc.Word('There')),
                                                'is',
                                                None,
                                                ['nothing', 'special', 'about', entity]
                                                )

            log = [nothing_special_res]

    if not em_helpers.check_can_not(log, "look"):
        log.insert(0, look_res)
    return log


def look_inventory(entity, location_preposition):
    """
    Returns the environment response after a player looks in another player's inventory or in its own inventory.

    Parameters
    ----------
    entity : Entity
        The entity should have an attribute player.
    location_preposition : str
        The location position should be 'in', and it refers to looks in <entity>.

    Returns
    -------
    response : list
        A list of single sentence outputting what items the player contains or outputting that the player
        has no items.  If the location position is not 'in', an empty response is returned.
    """
    if "player" not in entity.attributes or location_preposition != 'in':
        return []

    visible_objects, set_objects = objects_loc_pos(entity, location_preposition)
    if visible_objects is not None:
        inventory_contains_res = tsentences.have(entity,
                                                 'has',
                                                 None,
                                                 (set_objects,
                                                  lhelpers.convert_obj_to_part(em_helpers.join_el_conn(visible_objects, ","))),
                                                 [location_preposition, entity]
                                                 )
        response = [inventory_contains_res]
    else:
        inventory_is_empty_res = tsentences.have(entity,
                                                 'has',
                                                 'no',
                                                 'items',
                                                 [location_preposition, entity])
        response = [inventory_is_empty_res]
    return response


def look(entity, player, position, location):
    """
    Returns the environment response after the player looks (in/on/under) the entity at the specified location.

    Please refer to look_object_response for more information.

    Parameters
    ----------
    entity : Entity
        The entity that the player looks in/on/under.
    player : Entity
        The player looking in/on/under the entity.
    position : str
        The location preposition ('in', 'on', 'under').
    location : list
        The location is a list of two values: a location preposition (string) and a location (Entity).
        The location refers to where the entity is located.

    Returns
    -------
    log : list
        A list of valid responses

    """
    can_not_look = tsentences.look(player,
                                   'can',
                                   'not',
                                   'look',
                                   [position, entity]
                                   )

    visibility = entity.validate_reachability(player, location[1], can_not_look)
    log = []
    log += visibility

    if entity.properties['location'] != location:
        item_not_loc_position = tsentences.be([entity, "'s", 'location'], 'is', 'not', location)
        log.append(tsentences.cont([can_not_look, item_not_loc_position]))

    partial_log = look_object_response(entity, player, position, can_not_look)
    if can_not_look in partial_log:
        for sent in partial_log[1:]:
            log.append(tsentences.cont([can_not_look, sent]))
        #log.append(tsentences.cont(partial_log))

    else:
        if len(log) == 0:
            log = [tsentences.cont(partial_log)]
    return log
