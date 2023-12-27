import math
import copy


def custom_round(result):
    fractional_part = result % 1

    if fractional_part == 0:
        rounded_result = result
    elif fractional_part <= 0.5:
        rounded_result = math.floor(result)
    else:
        rounded_result = math.ceil(result)

    return int(rounded_result)


class FunctionWrapper:
    """A class used to implement function intensities"""

    def __init__(self, func, number_of_calls):
        self.func = func
        self.number_of_calls = number_of_calls

    def __call__(self, *args, **kwargs):
        for _ in range(self.number_of_calls):
            self.func(*args, **kwargs)

    def __mul__(self, number):
        """Multiply a function with a given number"""
        result_function = FunctionWrapper(self.func, self.number_of_calls)
        result_function.number_of_calls = custom_round(self.number_of_calls * number)
        return result_function

    def __add__(self, other):
        """Combine effects of functions"""
        result_function = FunctionWrapper(self.func, self.number_of_calls)

        # if the other function hasn't been wrapped yet
        if not isinstance(other, FunctionWrapper):
            result_function.number_of_calls += 1
        else:
            result_function.number_of_calls += other.number_of_calls
        return result_function

    def __truediv__(self, number):
        """Divide effects of a function"""
        result_function = FunctionWrapper(self.func, self.number_of_calls)
        result_function.number_of_calls = custom_round(result_function.number_of_calls / number)
        return result_function


class Potion:
    def __init__(self, effects, duration):
        # since the functions in the dictionary will be changed (wrapped), deep copy it
        self.effects = copy.deepcopy(effects)
        self.duration = duration

        self.usable = True
        self.is_depleted = False
        # Store keys of depleted effects here
        self.depleted_effects = set()

        # Wrap all functions that are still not wrapped to make operations on them easier
        for key in self.effects:
            if not isinstance(self.effects[key], FunctionWrapper):
                wrapped_function = FunctionWrapper(self.effects[key], 1)
                self.effects[key] = wrapped_function

    def perform_checks(self):
        if self.is_depleted:
            raise TypeError("Potion is depleted.")
        if not self.usable:
            raise TypeError("Potion is now part of something bigger than itself.")

    def __getattribute__(self, item):
        if item in object.__getattribute__(self, 'effects'):
            self.perform_checks()
            if item not in self.depleted_effects:
                self.depleted_effects.add(item)
                if len(self.effects) == len(self.depleted_effects):
                    self.is_depleted = True
                return object.__getattribute__(self, 'effects')[item]
            else:
                raise TypeError("Effect is depleted.")
        return object.__getattribute__(self, item)

    def __add__(self, other):
        self.perform_checks()
        other.perform_checks()

        max_duration = max(self.duration, other.duration)

        # merge the two dictionaries of effects together
        effects_merged = other.effects.copy()
        # if there are common keys, their values will be overwritten
        effects_merged.update(self.effects.copy())

        result_potion = Potion(effects_merged, max_duration)

        # get the common functions for the potions
        common_names = set(self.effects.keys()) & set(other.effects.keys())
        for name in common_names:
            result_potion.effects[name].number_of_calls += other.effects[name].number_of_calls

        self.usable = False
        other.usable = False
        return result_potion

    def __mul__(self, number):
        self.perform_checks()

        multiplied_effects = dict(self.effects)

        for key in multiplied_effects:
            multiplied_effects[key] = multiplied_effects[key] * number

        multiplied_potion = Potion(multiplied_effects, self.duration)

        self.usable = False
        return multiplied_potion

    def __sub__(self, other):
        self.perform_checks()
        other.perform_checks()

        # Compare the keys of the two potions using set operations
        if not set(other.effects.keys()).issubset(set(self.effects.keys())):
            raise TypeError("Different effects in right potion")

        purified = Potion(self.effects, self.duration)
        common_names = set(self.effects.keys()) & set(other.effects.keys())

        for name in common_names:
            left_intensity = self.effects[name].number_of_calls
            right_intensity = other.effects[name].number_of_calls

            if right_intensity >= left_intensity:
                purified.effects.pop(name)
            else:
                purified.effects[name].number_of_calls = left_intensity - right_intensity

        self.usable = False
        other.usable = False
        return purified

    def __truediv__(self, number):
        self.perform_checks()

        divided_effects = {key: value / number for key, value in self.effects.items()}
        self.usable = False
        return tuple(Potion(divided_effects, self.duration) for _ in range(number))

    def __eq__(self, other):
        self.perform_checks()
        other.perform_checks()

        for key in self.effects:
            if key not in other.effects:
                return False
            if other.effects[key].number_of_calls != self.effects[key].number_of_calls:
                return False
        return True

    @staticmethod
    def calculate_sums(left_potion, right_potion):
        """Calculate sums of effect intensities for two potions"""
        sum_left = 0
        sum_right = 0

        for key in left_potion.effects:
            sum_left += left_potion.effects[key].number_of_calls

        for key in right_potion.effects:
            sum_right += right_potion.effects[key].number_of_calls

        return sum_left, sum_right

    def __lt__(self, other):
        self.perform_checks()
        other.perform_checks()

        sum_self, sum_other = Potion.calculate_sums(self, other)
        return sum_self < sum_other

    def __gt__(self, other):
        self.perform_checks()
        other.perform_checks()

        sum_self, sum_other = Potion.calculate_sums(self, other)
        return sum_self > sum_other

    def __ge__(self, other):
        return NotImplemented

    def __le__(self, other):
        return NotImplemented


class ГоспожатаПоХимия:
    def __init__(self):
        # for each target, store its original attributes
        self.initial_states = dict()
        # original effects of each potion
        self.effects = dict()
        # remaining times for all active potions
        self.times = dict()
        # associate each potion with a target
        self.targets = dict()

    def restore_target_initial_state(self, target):
        for attribute, value in self.initial_states[id(target)].items():
            setattr(target, attribute, value)

    def apply(self, target, potion):
        if potion.is_depleted:
            raise TypeError("Potion is depleted.")

        if id(target) not in self.initial_states.keys():
            attributes_before_change = copy.deepcopy(target.__dict__)
            self.initial_states[id(target)] = attributes_before_change

        self.effects[id(potion)] = []
        self.times[id(potion)] = potion.duration
        self.targets[id(potion)] = target

        unused_effects = sorted(set(potion.effects.keys()) - potion.depleted_effects,
                                key=lambda x: sum(ord(c) for c in x),
                                reverse=True)

        for unused_effect in unused_effects:
            effect = potion.__getattribute__(unused_effect)
            self.effects[id(potion)].append(copy.deepcopy(effect))
            effect(target)

        potion.is_depleted = True

    def reapply_active_potions(self, target):
        for key in self.effects:
            if self.times[key] == 0:
                continue
            for effect in self.effects[key]:
                number_of_calls = effect.number_of_calls
                effect(target)
                effect.number_of_calls = number_of_calls

    def tick(self):
        to_remove = []

        for key in self.times:
            self.times[key] -= 1

        for key in self.times:
            # restore the old state of 'target' and remove the potion
            if self.times[key] <= 0:
                target = self.targets[key]
                self.restore_target_initial_state(target)
                to_remove.append(key)
                self.reapply_active_potions(target)

        for key in to_remove:
            self.times.pop(key)
            self.effects.pop(key)
            self.targets.pop(key)
