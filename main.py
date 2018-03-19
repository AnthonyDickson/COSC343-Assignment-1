#!/usr/bin/env python3
from ev3dev.ev3 import *


class RobotController:
    """An interface to control a LEGO ev3 robot."""

    def __init__(self):
        """Set up the controller by getting handles to the robot's various
        sensors and motors.
        """
        # Setup the touch sensor.
        self.ts = TouchSensor()
        # Setup the colour sensor.
        self.cs = ColorSensor()
        self.cs.mode = 'COL-REFLECT'
        self.black_threshold = 30
        # Setup the motors.
        self.mLeft = LargeMotor('outB')
        self.mRight = LargeMotor('outC')

    def move_for_tiles(self, num_tiles, speed=360):
        """Move the robot forward in a straight line for a number of
        black tiles.

        Args:
            num_tiles (int): How many squares to return.
            speed (int): How fast to run the motors.
        """
        prev_val = self.cs.value()
        n = 0  # The number of black tiles counted.

        self.mLeft.run_forever(speed_sp=speed)
        self.mRight.run_forever(speed_sp=speed)

        while n < num_tiles:
            # If the robot was over something white and now it is over
            # something black:
            if prev_val < self.black_threshold <= self.cs.value():
                n += 1
                self.beep()

            prev_val = self.cs.value()
            time.sleep(0.1)

        self.mLeft.stop()
        self.mRight.stop()

    def rotate(self, degrees, speed=360):
        """Rotate the robot either clockwise or counter-clockwise.

        Args:
            degrees (int): How many degrees to turn the robot. Use a negative
                number to rotate the robot counter-clockwise.
            speed (int): How fast to run the motors whilst rotating.
        """
        self.mLeft.run_to_rel_pos(position_sp=degrees, speed_sp=speed)
        self.mRight.run_to_rel_pos(position_sp=-degrees, speed_sp=speed)
        self.mLeft.wait_while('running')
        self.mRight.wait_while('running')

    def move_until_touching(self, speed=360):
        """Move the robot until it is touching something with it's
        touch sensor.

        Args:
            speed (int): How fast to run the motors.
        """
        self.mLeft.run_forever(speed_sp=speed)
        self.mRight.run_forever(speed_sp=speed)

        while not self.ts.value():
            time.sleep(0.1)

        self.mLeft.stop()
        self.mRight.stop()

    def beep(self):
        """Play a beep sound."""
        Sound.beep()


def main():
    rbt = RobotController()
    rbt.move_for_tiles(15)
    rbt.rotate(90)
    rbt.move_for_tiles(7)
    rbt.move_until_touching()
    rbt.move_for_tiles(1)
    rbt.beep()


if __name__ == '__main__':
    main()