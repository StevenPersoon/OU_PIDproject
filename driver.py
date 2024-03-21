from arcade import clamp
import time
import math

from reloadable import Reloadable


class Driver(Reloadable):
    def __init__(self, state=None, ship=None):

        self.ship = ship
        self.reset = True

        self.last_x = ship.x
        self.i = 0

        self.pos = 'l'
        self.ts = []
        self.printed_time = False
        self.start_time = 0
        super().__init__(state)

    def tick(self, ct):
        inputs = self.get_inputs(ct)

        if inputs:
            inputs["enabled"] = True

        if self.reset:
            inputs["reset"] = True
            self.reset = False

        self.get_settling_time(False)   # Check for settling time every tick

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

    def get_settling_time(self, reset):
        """"
        Calculates the time the to reach the steady state within 5% tolerance
        """
        if reset is True:
            self.start_time = time.monotonic()
            self.pos = 'l'
            self.ts.clear()
            self.printed_time = False

        if (self.pos == 'to_r') and (self.ship.x > 0.05):      # For transitioning from left edge to right edge
            self.pos = 'r'
        elif (self.pos == 'to_l') and (self.ship.x < -0.05):     # For transitioning from right edge to left edge
            self.pos = 'l'
        elif (self.ship.x >= -0.05) and (self.pos == 'l'):
            self.ts.append(time.monotonic() - self.start_time)
            self.pos = 'to_r'
            #print('start time is {}'.format(self.start_time))
            #print('current time is {}'.format(time.monotonic()))
            print('time left bound is {}'.format(self.ts[-1]))
        elif (self.ship.x <= 0.05) and (self.pos == 'r'):
            self.ts.append(time.monotonic() - self.start_time)
            self.pos = 'to_l'
            #print('start time is {}'.format(self.start_time))
            #print('current time is {}'.format(time.monotonic()))
            print('time right bound is {}'.format(self.ts[-1]))

        if len(self.ts) != 0:
            if self.printed_time is False:
                if ((time.monotonic() - self.start_time) > (2 * self.ts[-1])):
                    print("The settling time is {} seconds".format(self.ts[-1]))
                    self.printed_time = True
                    # Checks if the current time is greater than two times the last time the 5% boundary was reached
                    # Not the best solution, but should work


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
