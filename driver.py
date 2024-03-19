from arcade import clamp
import math

from reloadable import Reloadable


class Driver(Reloadable):
    def __init__(self, state=None, ship=None):

        self.ship = ship
        self.reset = True

        self.last_x = ship.x
        self.i = 0

        super().__init__(state)

    def tick(self, ct):
        inputs = self.get_inputs(ct)

        if inputs:
            inputs["enabled"] = True

        if self.reset:
            inputs["reset"] = True
            self.reset = False

        return inputs

    def get_inputs(self, ct):

        moved = self.ship.x - self.last_x
        self.last_x = self.ship.x
        self.i = self.i + 0.2 * self.ship.x
        self.i = clamp(self.i, -2, 2)

        return {
            "factor": -5,
            "p": 1 * self.ship.x,
            "d": 60 * moved,
            "i": 0.05 * self.i,
        }


class ExampleDriver(Reloadable):

    serialize_vars = ()

    def __init__(self, state=None, ship=None):

        self.ship = ship
        self.reset = True

        self.last_x = self.ship.x
        self.i = 0

        super().__init__(state)
        print(self.ship)

    def tick(self, ct):
        inputs = self.get_inputs(ct)

        if inputs:
            inputs["enabled"] = True

        if self.reset:
            inputs["reset"] = True
            self.reset = False

        return inputs

    def get_inputs(self, ct):

        p = -1 * self.ship.x
        d = 125 * (self.last_x - self.ship.x)
        self.i = self.i + 0.2 * self.ship.x  # clamp(, -2000, 2000)

        self.last_x = self.ship.x

        return {
            "factor": 1,
            "p": p,
            "d": d,
            "i": -0.01 * self.i,
        }
