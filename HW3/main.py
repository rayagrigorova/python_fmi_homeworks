import math


class Candy:

    def __init__(self, mass, uranium):
        self.mass = mass
        self.uranium = uranium

    def get_uranium_quantity(self):
        """Return the quantity of uranium in grams."""
        return self.mass * self.uranium

    def get_mass(self):
        return self.mass


class Person:

    def __init__(self, position):
        self.position = position

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    @staticmethod
    def get_distance(person_1, person_2):
        """Calculate the distance between two people."""
        dx = person_1.position[0] - person_2.position[0]
        dy = person_1.position[1] - person_2.position[1]
        return math.sqrt(dx ** 2 + dy ** 2)


class Kid(Person):

    CRITICAL_MASS = 20

    def __init__(self, position, initiative):
        super().__init__(position)
        self.initiative = initiative
        self.basket = list()

    def get_initiative(self):
        return self.initiative

    def add_candy(self, candy_to_add):
        self.basket.append(candy_to_add)

    def is_critical(self):
        """Sum the uranium contents of all candies and returns true if sum > 20."""
        uranium_sum = sum(candy.get_uranium_quantity() for candy in self.basket)
        return uranium_sum > Kid.CRITICAL_MASS


class Host(Person):

    def __init__(self, position, candies):
        super().__init__(position)
        self.candies = [Candy(x, y) for x, y in candies]
        self.visited_from = []  # add children that already visited a given host here
        self.current_visitors = []  # add children that are visiting the host at the moment

    def remove_candy(self, func_remove_candy):
        # if the host doesn't have candy, do nothing
        if not self.candies:
            return None
        # save the candy to delete from the list
        candy_to_remove = func_remove_candy(self.candies)
        self.candies.remove(candy_to_remove)
        return candy_to_remove


class FluxCapacitor:

    def __init__(self, participants):
        self.kids = [person for person in participants if type(person) == Kid]
        self.hosts = [person for person in participants if type(person) == Host]

    @staticmethod
    def find_candy_with_biggest_mass(candies):
        return max(candies, key=lambda some_candy: some_candy.mass)

    def get_victim(self):
        while True:
            all_kids_visited_all_hosts = all(len(host.visited_from) == len(self.kids) for host in self.hosts)
            if all_kids_visited_all_hosts:
                break

            # first, determine for each kid which house it's going to visit
            for kid in self.kids:
                try:
                    closest_unvisited_house = min([host for host in self.hosts if kid not in host.visited_from],
                                                  key=lambda host: (
                                                      Person.get_distance(kid, host), host.position[0],
                                                      host.position[1]))
                # ValueError will be thrown if the iterable is empty (there are no unvisited hosts for the current kid)
                except ValueError:
                    continue

                # mark closest_unvisited_house as being actively visited by the respective kid
                closest_unvisited_house.current_visitors.append(kid)
                # the kid moves to the closest house, so change its coordinates
                kid.set_position(closest_unvisited_house.position)

            # secondly, make the hosts distribute the candy
            for host in self.hosts:
                while host.current_visitors:  # aim to empty the active visitors list
                    # if the host doesn't have candy, remove all current visitors
                    # and add them to the list of past visitors
                    if not host.candies:
                        host.visited_from += host.current_visitors
                        host.current_visitors = []
                        break

                    # determine the next kid by comparing initiatives
                    next_kid = max(host.current_visitors, key=lambda some_kid: some_kid.initiative)
                    # find candy for the next kid
                    next_candy = host.remove_candy(FluxCapacitor.find_candy_with_biggest_mass)
                    # add candy to kid's basket
                    next_kid.add_candy(next_candy)
                    # save the kid in the list of past visitors and remove it from active visitors
                    host.visited_from.append(next_kid)
                    host.current_visitors.remove(next_kid)

            # the last step is to add all children that have received critical mass to a set
            irridated_kids = set()
            for kid in self.kids:
                if kid.is_critical():
                    irridated_kids.add(kid)
            if irridated_kids:
                return irridated_kids

        return None
