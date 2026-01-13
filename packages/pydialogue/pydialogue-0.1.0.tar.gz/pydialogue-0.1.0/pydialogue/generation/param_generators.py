#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains functions that generate random parameters for the template functions.
"""

from . import helpers


def random_world_list(curr_params, member_name):
    """
        Fetches an iterable member of the class World
        and generates a random value from it.

        For example, the member can be players, so a random value will be selected from the
        world.players list.

        Parameters
        ----------
        curr_params : dict
            A dictionary that contains the parameters. It is a mapping parameter_name: parameter_value.
        member_name : str
            The name of the member that will be fetched from the class World.

        Returns
        -------
        any
            A random value selected from the world's member.


    """
    world = curr_params['world']
    dia_generator = curr_params['dia_generator']
    member_list = getattr(world, member_name, None)
    if isinstance(member_list, (list, tuple, str)):
        return dia_generator.random_gen.choice(member_list)


def random_location(curr_params):
    """ Generates a random location. The location can be an object. Some templates allow None to be the location,
        meaning the location is not provided.
    """
    dia_generator = curr_params['dia_generator']
    world = curr_params.get('world')
    item = curr_params.get('item')
    item_loc = item.properties.get('location', None)
    template = curr_params.get('primitive_template')
    template_name = getattr(template, "__name__", None)

    if item_loc is not None:
        if item_loc[1] == item:
            return None
    elif "abstract" in item.attributes:
        world_entities = world.query_entity_from_db(item)
        if any(entity == entity.properties['location'][1] for entity in world_entities):
            return None

    if world is not None:
        all_locations = []
        revealed_items = [obj for obj in world.obj_list if "location" in obj.prop_seen and obj != item]
        if len(revealed_items) > 0:
            if template_name not in ['drop_item', 'look_item']:
                all_locations.append(dia_generator.random_gen.choice(revealed_items))
            else:
                # check if loc position is supporter look for revealed supp and if all empty add random
                # similarly for container
                loc_pos = curr_params.get('location_position', None)
                if loc_pos == 'in':
                    attr = 'container'
                elif loc_pos == 'on':
                    attr = 'supporter'
                else:
                    attr = ('hollow', 'under')
                cand_loc = [obj for obj in revealed_items if attr in obj.attributes]
                if loc_pos is not None and len(cand_loc) > 0:
                    all_locations.append(dia_generator.random_gen.choice(cand_loc))
                else:
                    all_locations.append(dia_generator.random_gen.choice(revealed_items))
        all_locations.append(dia_generator.random_gen.choice([obj for obj in world.obj_list if obj != item]))
        if item_loc is not None and item_loc[1] not in all_locations and template_name != 'drop_item':
            del all_locations[-1]
            all_locations.append(item_loc[1])
        if template_name != 'drop_item':
            all_locations += [None]*len(all_locations)
        else:
            all_locations.append(None)
        return dia_generator.random_gen.choice(all_locations)


def random_item(curr_params):
    """ Generates a random item from the list of objects in the world. If the determiner_a is True, the world's object
        should be converted to an abstract object. The abstract object can not be uniquely determined. For example,
        the flour container will be converted to a flour container.
    """
    dia_generator = curr_params.get('dia_generator')
    world = curr_params.get('world')
    agent = curr_params.get('agent')
    seen = [obj for obj in world.obj_list if "location" in obj.prop_seen and obj != agent]
    cand_items = []
    if len(seen) > 0:
        cand_items.append(dia_generator.random_gen.choice(seen))
    unseen = [obj for obj in world.obj_list if "location" not in obj.prop_seen and obj != agent]
    if len(unseen) > 0:
        cand_items.append(dia_generator.random_gen.choice(unseen))
    template = curr_params.get('primitive_template')
    template_name = getattr(template, "__name__", None)

    if template_name == 'drop_item':
        if agent is not None and len(agent.objects) > 0:
            cand_items.append(dia_generator.random_gen.choice(agent.objects))
    elif template_name == "get_item":
        gettable_items = [obj for obj in seen if "static" not in obj.attributes and "player" not in obj.attributes]
        if len(gettable_items) > 0:
            cand_items.append(dia_generator.random_gen.choice(gettable_items))

    elif template_name in ["open_item", "close_item"]:
        cand_items.append(dia_generator.random_gen.choice(world.openables))

    item = dia_generator.random_gen.choice(cand_items)

    if curr_params.get("determiner_a", None) is True:
        item = helpers.unk_from_desc(dia_generator.random_gen, item)
    return item


def random_user(curr_params):
    """ Generates a random player from the list of players except the main player.
        Therefore, the main player can not issue requests.
    """
    dia_generator = curr_params.get('dia_generator')
    world = curr_params.get('world')
    list_candidates = [player for player in world.players if ('main', 'player') not in player.attributes]
    return dia_generator.random_gen.choice(list_candidates)


def random_agent(curr_params):
    dia_generator = curr_params.get('dia_generator')
    world = curr_params.get('world')
    seen = [obj for obj in world.players if "location" in obj.prop_seen]
    if dia_generator.random_gen.choice([0, 1]) == 1 and len(seen) > 0:
        player = dia_generator.random_gen.choice(seen)
    else:
        player = dia_generator.random_gen.choice(world.players)
    return player


def random_dir(curr_params):
    dia_generator = curr_params.get('dia_generator')
    world = curr_params.get('world')
    agent = curr_params.get('agent')
    if agent is not None:
        loc = agent.properties['location'][1]
        loc_directions = []
        for direction in world.directions:
            if direction in loc.properties:
                loc_directions.append(direction)
        rand = dia_generator.random_gen.choice(world.directions)
        candidate_directions = [rand]
        if len(loc_directions) > 0:
            candidate_directions.append(dia_generator.random_gen.choice(loc_directions))
        return dia_generator.random_gen.choice(candidate_directions)
    else:
        direction = dia_generator.random_gen.choice(world.directions)
    return direction


def candidate_prop_keys(curr_params):
    """ Fetches all property keys from the world except var_name and door_to """
    world = curr_params.get('world')
    item = curr_params.get('item')

    cand_keys = []
    if world is not None:
        cand_keys = ['size', 'color', 'material', 'type', 'name', 'nickname', 'surname']
        if 'abstract' not in item.attributes:
            new_cand_keys = [key for key in cand_keys if (key in item.properties and key not in item.prop_seen) or (
                        key not in item.properties and key not in item.elem_not_exists)]
            cand_keys = new_cand_keys

    return cand_keys


def random_param_value(curr_params, param_name):
    """
        Fetches a parameter from the dictionary of parameters and generates a random value from it.
        The parameter should be an iterable.

        Parameters
        ----------
        curr_params : dict
            A dictionary that contains the parameters. It is a mapping parameter_name: parameter_value.
        param_name : str
            The name of the parameter.

        Returns
        -------
        any
            A random value selected from the iterable.

    """
    dia_generator = curr_params.get('dia_generator')
    parameter = curr_params.get(param_name)
    if isinstance(parameter, (list, tuple)) and len(parameter) > 0:
        return dia_generator.random_gen.choice(parameter)

    return None


def random_property_val(curr_params):
    """ Generates random property value for a given property key. It takes one value from the
        list of property values that are suitable for the property key. For example, for the property key color,
        it takes one of the following 'red', 'blue', 'green', etc. Later, it takes ten values
        that are not suitable for the property key. For the given example, this can be 'size' like 'small' or 'big'.
        Finally, it returns a single random value from the list of 11 values.

        The selection is done this way, so that the agent can see a variety of property values, not only the ones
        that are suitable.
    """
    dia_generator = curr_params.get('dia_generator')
    candidate_key = curr_params.get('property_key')

    all_vals = []
    if candidate_key is not None:
        property_values = dia_generator.world.get_property_values([candidate_key])
        dia_generator.random_gen.shuffle(property_values)
        if len(property_values) >= 2:
            all_vals.extend(property_values[0:2])
        else:
            all_vals.extend(property_values)
        candidate_property_keys = curr_params.get('candidate_property_keys')
        if candidate_property_keys is not None:
            item = curr_params.get('item')
            if candidate_key in item.properties:
                item_value = item.properties[candidate_key]
                if item_value not in all_vals:
                    all_vals.append(item_value)
    if len(all_vals) > 0:
        return dia_generator.random_gen.choice(all_vals)
    else:
        return None


def random_determiner_a(curr_params):
    dia_generator = curr_params.get('dia_generator')
    curr_template = curr_params.get('primitive_template')
    curr_template_name = getattr(curr_template, "__name__", None)

    if curr_template_name == 'item_prop_revealed':
        determiner_a = False
    else:
        determiner_a = dia_generator.random_gen.choices([True, False], weights=[0.2, 0.8], k=1)[0]

    return determiner_a
