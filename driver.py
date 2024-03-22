from arcade import clamp
import time
import matplotlib.pyplot as plt
import numpy as np
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

        self.ts_time = []
        self.ship_x_values = []
        super().__init__(state)

    def tick(self, ct):
        inputs = self.get_inputs(ct)

        if inputs:
            inputs["enabled"] = True

        if self.reset:
            inputs["reset"] = True
            self.reset = False

        self.get_settling_time(False)   # Check for settling time every tick
        self.make_plot(False)

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
            "i": 0.025 * self.i,
        }

    def get_settling_time(self, reset):
        """"
        Calculates the time the to reach the steady state within 5% tolerance
        """
        if reset is True:
            print('THE LAST REPORTED BOUNDARY TIME IS THE SETTLING TIME!\n')
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
            self.ts_time.append(len(self.ship_x_values)+1)
            self.pos = 'to_r'
            print('time left bound is {}'.format(self.ts[-1]))
        elif (self.ship.x <= 0.05) and (self.pos == 'r'):
            self.ts.append(time.monotonic() - self.start_time)
            self.ts_time.append(len(self.ship_x_values) + 1)
            self.pos = 'to_l'
            print('time right bound is {}'.format(self.ts[-1]))
        """
        if len(self.ts) != 0:   # i.e. has not reached within 5% tolerance
            if self.printed_time is False:      # To stop repeating the text
                if ((time.monotonic() - self.start_time) > (2 * self.ts[-1])):        # For checking crically damped or overdamped systems
                    # Can take a long time if there's a large settling time
                    print("The settling time is {} seconds".format(self.ts[-1]))
                    self.printed_time = True
        """
    def make_plot(self, plot):
        if plot is True:
            self.ship_x_values[0] = -1      # When R is pressed it goes to 0 instead of 1, this creates weird plots
            xpoints = np.arange(len(self.ship_x_values))
            ypoints = np.asarray(self.ship_x_values, dtype=np.float32)
            plt.plot(xpoints, ypoints)
            plt.axhline(y=0, lw=0.5, color='black')
            plt.axhline(y=-0.05, lw=0.5, color='red', ds='steps')
            plt.axhline(y=0.05, lw=0.5, color='red', ls='-')
            plt.title('Step Response')
            plt.ylabel("Amplitude")
            plt.xlabel("Time (ticks)")
            print(len(self.ts))
            for x in range(len(self.ts)):
                if (x % 2) == 0:
                    plt.annotate('{:.2f} s'.format(self.ts[x]), (self.ts_time[x], -0.05))
                else:
                    plt.annotate('{:.2f} s'.format(self.ts[x]), (self.ts_time[x], 0.05))
            plt.show()
        else:
            self.ship_x_values.append(self.ship.x)





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
