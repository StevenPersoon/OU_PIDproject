import os
from importlib import reload

import arcade
import arcade.gui as gui
from arcade.experimental.uislider import UISlider
from arcade.gui import UIAnchorWidget, UILabel
from arcade.gui.events import UIOnChangeEvent

import driver
import ship
import stats

import random

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1280
SCREEN_TITLE = "PID"


class MyGame(arcade.Window):
    """
    Main application class.
    """
    random_wind = 0
    show_sliders = 0

    P = 1
    I = 0.025
    D = 60

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)
        self.ct = 0

        self.switch_time = 0

        self.manager = gui.UIManager()
        self.manager.enable()

        ui_slider_P = UISlider(value=self.P, min_value=0, max_value=10, width=120, height=20)
        label_P = UILabel(text="P: " + f"{ui_slider_P.value:02.1f}")

        @ui_slider_P.event()
        def on_change(event: UIOnChangeEvent):
            label_P.text = "P: " + f"{ui_slider_P.value:02.1f}"
            label_P.fit_content()
            self.P = ui_slider_P.value

        ui_slider_I = UISlider(value=self.I, min_value=0, max_value=0.1, width=120, height=20)
        label_I = UILabel(text="I: " + f"{ui_slider_I.value:02.3f}")

        @ui_slider_I.event()
        def on_change(event: UIOnChangeEvent):
            label_I.text = "I: " + f"{ui_slider_I.value:02.3f}"
            label_I.fit_content()
            self.I = ui_slider_I.value

        ui_slider_D = UISlider(value=self.D, min_value=0, max_value=100, width=120, height=20)
        label_D = UILabel(text="D: " + f"{ui_slider_D.value:02.0f}")

        @ui_slider_D.event()
        def on_change(event: UIOnChangeEvent):
            label_D.text = "D: " + f"{ui_slider_D.value:02.0f}"
            label_D.fit_content()
            self.D = ui_slider_D.value

        self.manager.add(UIAnchorWidget(child=ui_slider_P, align_x=-300))
        self.manager.add(UIAnchorWidget(child=label_P, align_x=-300, align_y=20))
        self.manager.add(UIAnchorWidget(child=ui_slider_I, align_x=0))
        self.manager.add(UIAnchorWidget(child=label_I, align_x=0, align_y=20))
        self.manager.add(UIAnchorWidget(child=ui_slider_D, align_x=300))
        self.manager.add(UIAnchorWidget(child=label_D, align_x=300, align_y=20))

    def setup(self):

        self.ship = ship.Ship()
        self.stats = stats.Stats(ship=self.ship)
        self.driver = driver.Driver(ship=self.ship)

    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()
        if self.show_sliders:
            self.manager.draw()
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

        self.driver.set_PID(self.P, self.I, self.D)

        self.ship = self.ship.reload()
        self.stats = self.stats.reload(ship=self.ship)
        self.driver = self.driver.reload(ship=self.ship)
        # TODO: we have to tell stats about the ship, esp. when it was reloaded

    def tick(self):
        self.ct += 1

        inputs = self.driver.tick(self.ct)

        if(self.random_wind):
            self.ship.star_wind_control = random.randint(1,6)

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
            self.driver.make_plot(False, True)      # Clears list for making plot
        elif key == 115:  # S
            self.random_wind = 0
            self.ship.star_wind = 3 - self.ship.star_wind
        elif key == 116:  # T
            self.random_wind = abs(self.random_wind - 1)    # Toggle 0->1->0->1->...
            # So when S pressed random wind starts/stops (at stop, solar wind slows down to 0)
        elif key == 112:  # P
            self.driver.make_plot(True, False)
            # Make a plot
        elif key == 100:  # D
            self.show_sliders = abs(self.show_sliders - 1)    # Toggle 0->1->0->1->...

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


# TODO: DONE BY DIRK: enable random star-wind
# TODO: "docked"
# TODO: DONE BY STEVEN: measure/show time until docked


if __name__ == "__main__":
    main()
