import os
from importlib import reload

import arcade

import driver
import ship
import stats

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1280
SCREEN_TITLE = "PID"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)
        self.ct = 0

        self.switch_time = 0

    def setup(self):

        self.ship = ship.Ship()
        self.stats = stats.Stats(ship=self.ship)
        self.driver = driver.Driver(ship=self.ship)

    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()
        self.ship.draw()
        self.stats.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        self.switch_time += delta_time
        if self.switch_time > 0.0166:
            self.switch_time -= 0.0166
            self.tick()

        self.ship = self.ship.reload()
        self.stats = self.stats.reload(ship=self.ship)
        self.driver = self.driver.reload(ship=self.ship)
        # TODO: we have to tell stats about the ship, esp. when it was reloaded

    def tick(self):
        self.ct += 1

        inputs = self.driver.tick(self.ct)

        if inputs.get("reset"):
            self.driver.get_settling_time(True)
            self.ship.reset()

        p, d, i = inputs.get("p"), inputs.get("d"), inputs.get("i")
        if inputs.get("enabled"):
            thrust = (p if p else 0) + (d if d else 0) + (i if i else 0)
            thrust = thrust * inputs.get("factor", 1)
            self.ship.control = thrust
        else:
            self.ship.control = 0

        self.ship.tick(self.ct)
        self.stats.tick(self.ct, p, d, i)

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == 65361:  # left
            self.ship.thrust += -1
        elif key == 65363:  # right
            self.ship.thrust += 1
        elif key == 113:  # Q
            self.close()
        elif key == 114:  # R
            self.ship.reset()
            self.stats.ship = self.ship
            self.driver.ship = self.ship
            self.driver.get_settling_time(True)     # Resets the settling time timer
        elif key == 115:  # S
            self.ship.star_wind = 3 - self.ship.star_wind
        else:
            print("key press", key)

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == 65361:  # left
            self.ship.thrust += 1
        elif key == 65363:  # right
            self.ship.thrust += -1

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        # print("mouse motion", x, y, delta_x, delta_y)
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        print("mouse press", x, y, button)
        # self.close()
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        print("mouse release", x, y, button)
        pass


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


# TODO: enable random star-wind
# TODO: "docked"
# TODO: measure/show time until docked


if __name__ == "__main__":
    main()
