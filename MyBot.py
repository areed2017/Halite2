import logging
from random import randint

import hlt
from hlt.controller import Controller

"""

    @author: Andrew Reed
    Date: January 11th 2018
    
    Education: Rochester institute of tech.
    Reason for joining the contest:
            Test my skills, and hopefully expand my career
 
"""

""" Init game and controller """
game = hlt.Game("ML_V5")
controller = Controller()
controller.set_game(game)

""" determine planet/ships and define the 'origin planet' """
controller.determine_planet_ownership()
controller.determine_ships()
origin_planet = controller.closest_planet_to( controller.get_starting_corner() )
center_planet = controller.closest_planet_to( hlt.entity.Position(120, 80) )

ship_tasks = dict()
planet_queue = dict()
ship_origin = dict()
origin_direction = dict()

""" Define Each Quadrent Of The Map """
Q1_center = hlt.entity.Position(60, 40)
Q2_center = hlt.entity.Position(180, 40)
Q3_center = hlt.entity.Position(60, 120)
Q4_center = hlt.entity.Position(180, 120)

MAX_SHIPS_PER_TURN = 20
turn = 0


while True:
    """     Start Of Turn:              """

    ships_delt_with = 0.0

    controller.determine_planet_ownership()
    controller.determine_ships()
    origin_planet = controller.game_map.get_planet(origin_planet.id)

    """
        Target In Each Quadrent is defined here
            -These are used when processing time is close to being
                used up and decisions have to be made fast
    """
    Q1_enemies = controller.list_closest_enemy_ships(Q1_center)
    Q2_enemies = controller.list_closest_enemy_ships(Q2_center)
    Q3_enemies = controller.list_closest_enemy_ships(Q3_center)
    Q4_enemies = controller.list_closest_enemy_ships(Q4_center)

    """ Define Turn Specific Data """
    num_players = len(controller.get_players())

    my_ships = controller.get_my_ships()
    enemy_ships = controller.get_enemy_ships()

    my_planets = controller.get_my_planets()
    enemy_planets = controller.get_enemy_planets()
    unclaimed_planets = controller.get_unclaimed_planets()
    planet_path = controller.closest_all_planets_to(origin_planet)

    """ Victory Lap For Fun """
    victory_lap = False
    if len(enemy_planets) < 2 and turn > 50:
        victory_lap = True

    """         Cycle Through Ships:    """
    for ship in my_ships:

        ship_has_task = False

        """ Ships are over the amount process can take """
        if ships_delt_with > MAX_SHIPS_PER_TURN:
            """
                Determine Which Quadrent The Ship Is In and
                Send it after the corresponding Quadrent Target
            """
            if ship.x < 120:
                if ship.y < 80:
                    for enemy in Q1_enemies:
                        ship_has_task = True
                        controller.ship_navigate(ship, enemy)
                        Q1_enemies.remove(enemy)
                        break
                    if not ship_has_task:
                        controller.ship_navigate(ship, Q2_center)
                else:
                    for enemy in Q2_enemies:
                        ship_has_task = True
                        controller.ship_navigate(ship, enemy)
                        Q2_enemies.remove(enemy)
                        break
                    if not ship_has_task:
                        controller.ship_navigate(ship, Q4_center)
            else:
                if ship.y < 80:
                    for enemy in Q3_enemies:
                        ship_has_task = True
                        controller.ship_navigate(ship, enemy)
                        Q3_enemies.remove(enemy)
                        break
                    if not ship_has_task:
                        controller.ship_navigate(ship, Q1_center)
                else:
                    for enemy in Q4_enemies:
                        ship_has_task = True
                        controller.ship_navigate(ship, enemy)
                        Q4_enemies.remove(enemy)
                        break
                    if not ship_has_task:
                        controller.ship_navigate(ship, Q3_center)
            continue

        if victory_lap:
            """ Send Ships Off To Do Their Victory Lap """
            if turn < 280:
                ships_delt_with += 0.4
                controller.ship_navigate(ship, hlt.entity.Position(120, 80))
            else:
                controller.ship_navigate(ship, enemy_planets[0])
                ships_delt_with += 0.4
            continue

        """ Set Ship Origin """
        if ship_origin.get(ship.id) is None:
            planet = controller.closest_all_planets_to(ship)[0]
            ship_origin[ship.id] = planet
            if origin_direction.get(planet.id) is None:
                origin_direction[planet.id] = controller.closest_all_planets_to(planet)
        else:
            planet = controller.game_map.get_planet(ship_origin[ship.id].id)
            ship_origin[ship.id] = planet
            origin_direction[planet.id] = controller.closest_all_planets_to(planet)

        """ If Ship Is Docked Ignore It """
        if ship.docking_status is not ship.DockingStatus.UNDOCKED:
            ships_delt_with += .4
            continue

        ships_delt_with += 1.0

        """ If Beginning Ships Head To Origin Planet """
        if ship.id == 2:
            if turn < 2:
                continue
        if ship.id == 1:
            if turn < 3:
                continue

        """ For each Planet in order of closest from starting position """
        for planet in origin_direction[ship_origin[ship.id].id]:
            if planet.owner is None:
                """ If no owner and planet will be dockable then move twards/dock said planet """
                if planet.num_docking_spots >= controller.get_planet_queue(planet) + len(planet.all_docked_ships()):
                    controller.ship_navigate(ship, planet)
                    controller.add_to_planet_queue(planet)
                    break

            elif planet.owner.id is controller.me.id:
                """ If the planet is mine and it is not yet full, navigate to it """
                if planet.num_docking_spots <= controller.get_planet_queue(planet) + len(planet.all_docked_ships()):
                    continue
                controller.ship_navigate(ship, planet)
                controller.add_to_planet_queue(planet)
                break

            elif controller.enemy_planets.__contains__(planet):
                """ If the planet is the enemies planet attack the closest ship """
                controller.ship_navigate(ship, controller.closest_enemy_ship(ship))
                controller.add_to_planet_queue(planet)
                break


    """ End Turn """
    turn += 1
    controller.proceed_to_next_turn()
