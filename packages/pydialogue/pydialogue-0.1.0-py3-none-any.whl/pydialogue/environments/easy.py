#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides the function for creating the simulated training environment.
"""


from ..environment import entities as env
from . import builders
from . import world as tworld


def build_world(random_seed=None):
    """ Build the entities of the easy world.
        In the easy world, only <x> rooms are used, and <y> directions for the rooms.
        There are a total of <z> objects.
    """
    undo_changes = []
    world = tworld.World(random_seed=random_seed, undo_changes=undo_changes, init=False)
    barn = env.Entity(world)
    main_path = env.Entity(world)
    meadow = env.Entity(world)
    living_room = env.Entity(world)
    kitchen = env.Entity(world)
    bedroom = env.Entity(world)
    bathroom = env.Entity(world)
    basement = env.Entity(world)

    ''' DEFINE THE AGENTS '''

    player = builders.build_player(world, 'player', 'medium', 'person', location=['on', main_path],
                                    name='Heidi', surname='Mustermann', nickname='maple')
    player.attributes[('main', 'player')] = None
    player2 = builders.build_player(world, 'player2', 'small', 'person', location=['in', barn],
                                    name='Andy', surname='Mustermann', nickname='peanut',  material='plastic')
    player2.attributes['supporter'] = None
    inv = builders.build_player(world, 'inv', ['very', 'big'], 'person', location=['in', basement],
                                name='Max', nickname='uncle', color='green')
    inv.attributes['supporter'] = None

    dog = builders.build_player(world, 'dog', _type='dog',  location=['in', barn],
                                name='Hannah', surname='Doe', nickname='coco', color='brown', material='cardboard')

    ''' DEFINE THE ENTITIES '''
    cat = builders.build_entity(world, 'cat', _type='cat', color='orange', location=['in', bedroom],
                                name='Andy', surname='Doe', nickname='fluffy', material='cotton')

    toys_container = builders.build_entity(world, 'toys_container', _type="box",
                                           color='red', location=['in', bedroom])
    toys_container.attributes['container'] = None
    toys_container.attributes['supporter'] = None
    toys_container.attributes[('hollow', 'under')] = None
    toys_container.attributes['openable'] = None
    toys_container.attributes['open'] = None

    small_container = builders.build_entity(world, 'small_container', _type="box", color='green',
                                            location=['in', toys_container])
    small_container.attributes['container'] = None
    small_container.attributes[('hollow', 'under')] = None
    small_container.attributes['openable'] = None
    small_container.attributes['open'] = None

    inner_container = builders.build_entity(world, 'inner_container', _type='box', material='cardboard',
                                            location=['in', small_container])
    inner_container.attributes['container'] = None
    inner_container.attributes['locked'] = None
    inner_container.properties['location'] = ['in', small_container]

    toy_drawer = builders.build_entity(world, 'toy_drawer', color="red", size=['very', 'small'],
                                        _type="drawer", location=['in', bedroom])

    small_ball = builders.build_entity(world, 'small_ball', 'small', 'ball', 'red', 'cotton', location=['in', small_container])
    big_ball = builders.build_entity(world, 'big_ball', 'big', 'ball', 'green', 'sugar', location=['in', toys_container])
    small_apple = builders.build_entity(world, 'small_apple', 'small', 'apple', 'red', 'metal', location=['in', player])
    big_apple = builders.build_entity(world, 'big_apple', 'big', 'apple', 'green', 'plastic', location=['on', player2])
    chicken = builders.build_entity(world, 'chicken', _type='chicken', name="Jim", material='cardboard', location=['on', meadow])

    kitchen_table = builders.build_table(world, 'kitchen_table', material='plastic', location=['in', kitchen])
    kitchen_window = builders.build_window(world, "kitchen_window", "small", "green", "wooden", ["in", kitchen])
    kitchen_window.attributes['supporter'] = None

    carrot = builders.build_entity(world, 'carrot', _type='carrot', color='orange', location=['on', kitchen_table])

    food_drawer = builders.build_entity(world, 'food_drawer', color="green",
                                        _type="drawer", location=['in', kitchen])
    food_drawer.attributes['openable'] = None
    food_drawer.attributes['open'] = None
    food_drawer.attributes[('hollow', 'under')] = None
    food_drawer.attributes['container'] = None
    food_drawer.attributes['static'] = None

    shelf1 = builders.build_entity(world, 'shelf1', _type="shelf", color="brown", material="plastic",
                                   location=['in', food_drawer])
    shelf1.attributes['supporter'] = None
    cardboard_container = builders.build_entity(world, 'cardboard_container', size="big",
                                                material="cardboard", location=['on', meadow])
    cardboard_container.attributes['container'] = None
    cardboard_container.attributes['open'] = None
    flour_bag = builders.build_entity(world, 'flour_bag', _type="bag", size="small",
                                      material="cotton", color="white", location=['in', cardboard_container])
    flour_bag.attributes['container'] = None
    flour_bag.attributes['openable'] = None
    flour_bag.attributes['open'] = None

    sugar_bowl = builders.build_entity(world, 'sugar_bowl', _type="bowl", size="small",
                                       material="plastic", color="white", location=['in', cardboard_container])
    sugar_bowl.attributes['container'] = None
    sugar_bowl.attributes['open'] = None

    white_sugar_cube = builders.build_entity(world, 'white_sugar_cube', _type="cube", size=["very", "small"],
                                             material="sugar", color="white", location=['in', sugar_bowl])

    brown_sugar_cube = builders.build_entity(world, 'brown_sugar_cube', _type="cube", size=["very", "small"],
                                             material="sugar", color="brown", location=['in', sugar_bowl])

    main_door = builders.build_door(world, 'main_door', size="medium",
                                    material='plastic', location=['in', kitchen], door_to=living_room)
    main_door.attributes['open'] = None

    liv_room_door = builders.build_door(world, 'liv_room_door', material='metal', location=['in', living_room])
    liv_room_door.attributes['locked'] = None

    bathroom_door = builders.build_door(world, 'bathroom_door', 'big', 'red', 'wooden', ['in', bathroom])
    bathroom_door.attributes['locked'] = None

    barn_door = builders.build_door(world, 'barn_door', 'small', 'brown', location=['in', barn])
    barn_door.attributes['locked'] = None

    bedroom_hall_door = builders.build_door(world, 'bedroom_hall_door', 'big', 'brown', location=['in', bedroom])
    bedroom_hall_door.attributes['locked'] = None

    bedroom_home_door = builders.build_door(world, 'bedroom_home_door', 'big',
                                            material='plastic', location=['in', bedroom])
    bedroom_home_door.attributes['locked'] = None

    ''' DEFINE ROOMS '''

    barn.properties['var_name'] = 'barn'
    barn.properties['location'] = ['in', barn]
    barn.properties['south'] = main_path
    barn.properties[('north', 'obstacle')] = barn_door
    barn.attributes['static'] = None
    barn.attributes['place'] = None
    barn.attributes['enclosed'] = None
    barn.properties['color'] = 'brown'
    barn.properties['name'] = 'barn'

    living_room.properties['type'] = 'room'
    living_room.properties['size'] = 'big'
    living_room.properties['var_name'] = 'living_room'
    living_room.properties['location'] = ['in', living_room]
    living_room.properties['west'] = kitchen
    living_room.properties[('west', 'obstacle')] = main_door
    living_room.properties[('north', 'obstacle')] = liv_room_door
    living_room.properties['east'] = bedroom
    living_room.properties['south'] = main_path
    living_room.properties['name'] = 'lounge'
    living_room.attributes['static'] = None
    living_room.attributes['place'] = None
    living_room.attributes['enclosed'] = None

    main_path.properties['var_name'] = 'main_path'
    main_path.properties['location'] = ['on', main_path]
    main_path.properties['south'] = meadow
    main_path.properties['west'] = barn
    main_path.properties['north'] = living_room
    main_path.attributes['static'] = None
    main_path.attributes['place'] = None
    main_path.attributes['surface'] = None
    main_path.properties['size'] = 'small'

    meadow.properties['var_name'] = 'meadow'
    meadow.properties['location'] = ['on', meadow]
    meadow.properties['north'] = main_path
    meadow.attributes['static'] = None
    meadow.attributes['place'] = None
    meadow.attributes['surface'] = None
    meadow.properties['size'] = 'big'

    kitchen.properties['type'] = 'room'
    kitchen.properties['var_name'] = 'kitchen'
    kitchen.properties['location'] = ['in', kitchen]
    kitchen.properties['west'] = living_room
    kitchen.properties[('west', 'obstacle')] = main_door
    kitchen.properties['south'] = basement
    kitchen.properties['material'] = 'wooden'
    kitchen.attributes['static'] = None
    kitchen.attributes['place'] = None
    kitchen.attributes['enclosed'] = None
    kitchen.properties['color'] = 'orange'
    kitchen.properties['name'] = 'kitchen'

    bedroom.properties['type'] = 'room'
    bedroom.properties['var_name'] = 'bedroom'
    bedroom.properties['material'] = 'plaster'
    bedroom.properties['location'] = ['in', bedroom]
    bedroom.properties['west'] = living_room
    bedroom.properties['south'] = bathroom
    bedroom.properties[('southeast', 'obstacle')] = bedroom_hall_door
    bedroom.properties[('east', 'obstacle')] = bedroom_home_door
    bedroom.attributes['static'] = None
    bedroom.attributes['place'] = None
    bedroom.attributes['enclosed'] = None
    bedroom.properties['size'] = ['very', 'big']
    bedroom.properties['name'] = 'bedroom'

    bathroom.properties['type'] = 'room'
    bathroom.properties['var_name'] = 'bathroom'
    bathroom.properties['location'] = ['in', bathroom]
    bathroom.properties[('east', 'obstacle')] = bathroom_door
    bathroom.properties['north'] = bedroom
    bathroom.attributes['static'] = None
    bathroom.attributes['place'] = None
    bathroom.attributes['enclosed'] = None
    bathroom.properties['material'] = 'plaster'
    bathroom.properties['color'] = 'white'
    bathroom.properties['name'] = 'bathroom'

    basement.properties['type'] = 'room'
    basement.properties['var_name'] = 'basement'
    basement.properties['north'] = kitchen
    basement.properties['location'] = ['in', basement]
    basement.attributes['static'] = None
    basement.attributes['place'] = None
    basement.attributes['enclosed'] = None
    basement.properties['material'] = 'wooden'
    basement.properties['size'] = 'small'
    basement.properties['name'] = 'basement'

    obj_list = [barn, main_path, meadow, living_room, bedroom,
                bathroom, kitchen, basement, small_ball,
                big_ball, small_apple, big_apple, chicken,
                toys_container, toy_drawer, small_container, carrot, player, player2, inv, dog, cat,
                kitchen_table, kitchen_window, main_door, liv_room_door, bathroom_door, barn_door,
                bedroom_hall_door, bedroom_home_door, inner_container, food_drawer, shelf1,
                cardboard_container, flour_bag, sugar_bowl, white_sugar_cube, brown_sugar_cube]

    world.basic_init(obj_list=obj_list)

    return world
