import hlt
from hlt import collision, entity
from hlt.entity import Entity
from random import randrange


class Controller:

    def __init__(self):
        """
        Variables:
            game: Game              #holds Game Object
            game_map: MAP           #Holds all data about the current turn
            me: Player              #Player object that refers to the current user

            my_ships: list of ships
            enemy_ships: list of ships
            my_planets: list of planets
            enemy_planets: list of planets
            unclaimed_planets: list of planets
            command_queue: list of commands received from ships

        """
        self.game = None
        self.game_map = None
        self.me = 0

        self.my_ships = []
        self.enemy_ships = []
        self.my_planets = []
        self.my_planets = []
        self.enemy_planets = []
        self.unclaimed_planets = []

        self.command_queue = []
        self.planet_queue = dict()

    def proceed_to_next_turn(self):
        """
        :param:

        What does this do?
            1. Send Command Queue using Game object
            2. Update the game_map
            3. Updates the current game map

        :return:
        """
        self.game.send_command_queue(self.command_queue)
        self.game_map = self.game.update_map()
        self.command_queue = self.command_queue = []
        self.me = self.game_map.get_me()
        self.planet_queue = dict()
    

    def determine_ships(self):
        """ Init all ships to be either an enemy ship or a players ship """
        self.enemy_ships = []
        self.my_ships = []
        for player in self.get_players():
            if player is not self.me:
                self.enemy_ships.extend(player.all_ships())
            else:
                self.my_ships.extend(player.all_ships())

    def determine_planet_ownership(self):
        """
            Init all planets to be either an enemy planet
                or a players planet or an unowned planet
        """
        self.my_planets = []
        self.enemy_planets = []
        self.unclaimed_planets = []
        for planet in self.game_map.all_planets():
            if planet.owner is self.me:
                self.my_ships.append(planet)
            elif planet.owner is None:
                self.unclaimed_planets.append(planet)
            else:
                self.enemy_planets.append(planet)

    def ship_navigate(self, ship, location):
        
        if type(location) is hlt.entity.Planet:
            """ if location is a planet """
            if ship.can_dock(location):
                """ if it can be docked, then dock it """
                self.command_queue.append(ship.dock(location))

            else:
                if location.owner is self.me or location.owner is None:
                    """ if the owner is me or noone, move twards the planet"""
                    navigate_command = ship.navigate(
                        ship.closest_point_to(location),
                        self.game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False
                    )

                    if navigate_command:
                        self.command_queue.append(navigate_command)
                else:
                    """ else move to the enemy ships at the planet"""
                    navigate_command = ship.navigate(
                        ship.closest_point_to(location.all_docked_ships()[0]),
                        self.game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False
                    )

                    """ Add to command que """
                    if navigate_command:
                        self.command_queue.append(navigate_command)

        elif type(location) is hlt.entity.Position:
            """ If location is just a position, then move to it """
            navigate_command = ship.navigate(
                location,
                self.game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False
            )

            """ Add to command que """
            if navigate_command:
                self.command_queue.append(navigate_command)
        else:
            navigate_command = ship.navigate(
                ship.closest_point_to(location),
                self.game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False
            )

            """ Add to command que """
            if navigate_command:
                self.command_queue.append(navigate_command)

    def closest_planet_to(self, obj):
        return self.closest_planets_to(obj)[0]

    def closest_planets_to(self, obj):
        planets = self.unclaimed_planets
        quick_sort(planets, 0, len(planets) - 1, obj)
        return planets

    def closest_all_planets_to(self, obj):
        planets = self.game_map.all_planets()
        quick_sort(planets, 0, len(planets) - 1, obj)
        return planets

    def closest_enemy_ship(self, obj):
        """ Returns the closest Enemy to the target """
        enemy = self.enemy_ships
        quick_sort(enemy, 0, len(self.enemy_ships) - 1, obj)
        return enemy[0]

    def list_closest_enemy_ships(self, obj):
        """ Returns a list of the closest Enemies to the target """
        enemy = self.enemy_ships
        quick_sort(enemy, 0, len(self.enemy_ships) - 1, obj)
        return enemy

    def add_to_planet_queue(self, planet):
        if self.planet_queue.get(planet.id) is None:
            self.planet_queue[planet.id] = 0
        self.planet_queue[planet.id] += 1

    """ GETTERS AND SETTERS AREA """

    def get_players(self):
        return self.game_map.all_players()

    def get_my_ships(self):
        return self.my_ships

    def get_enemy_ships(self):
        return self.enemy_ships

    def get_my_planets(self):
        return self.my_planets

    def get_enemy_planets(self):
        return self.enemy_planets

    def get_unclaimed_planets(self):
        return self.unclaimed_planets

    def get_starting_corner(self):
        
        """ Check if i own ships to prevent crash """
        if len(self.my_ships) < 1:
            return entity.Position(0, 0)

        """ Look to the first planet i own"""
        starting_ship = self.my_ships[0]

        """ Determine its Quadrent """
        corner = entity.Position(0, 0)
        if starting_ship.x > 120:
            corner.x = 240
        else:
            corner.x = 0
        if starting_ship.y > 80:
            corner.y = 160
        else:
            corner.y = 0
        return corner

    def get_planet_queue(self, planet):
        if self.planet_queue.get(planet.id) is None:
            return 0
        return self.planet_queue.get(planet.id)

    def set_game(self, game):
        """
        :param game:  Game

        What does this do?
            1. Takes the game from input and assigns it to self.game
            2. Gets the current map and assigns it to self.game_map
            3. From map we get the users Player object and assigns it to self.me

        :return: None
        """
        self.game = game
        self.game_map = self.game.update_map()
        self.me = self.game_map.get_me()


def does_ship_collide(ship, target_location):
    """
        Determine if any ship will collide when moving to a new location
    """
    start = Entity(ship.x, ship.y, 5, 0, 0, 0)
    collision.intersect_segment_circle(start, target_location, start)


def get_point_away_from(ship, fleeing_from):
    """
        Move in the oposite direction from the fleeing_from target
    """
    flee_x = 0
    flee_y = 0
    for i in fleeing_from:
        flee_x = i.x
        flee_y = i.y
    flee_x = flee_x / 2 - ship.x
    flee_y = flee_y / 2 - ship.y
    return hlt.entity.Position(flee_x, flee_y)



""" Quick Sort Algorithm"""
def partition(lst, start, end, pivot, ship_):
    lst[pivot], lst[end] = lst[end], lst[pivot]
    store_index = start
    for k in range(start, end):
        if lst[k].calculate_distance_between(ship_) < lst[end].calculate_distance_between(ship_):
            lst[k], lst[store_index] = lst[store_index], lst[k]
            store_index += 1
    lst[store_index], lst[end] = lst[end], lst[store_index]
    return store_index


def quick_sort(lst, start, end, ship_):
    if start >= end:
        return lst
    pivot = randrange(start, end + 1)
    new_pivot = partition(lst, start, end, pivot, ship_)
    quick_sort(lst, start, new_pivot - 1, ship_)
    quick_sort(lst, new_pivot + 1, end, ship_)
