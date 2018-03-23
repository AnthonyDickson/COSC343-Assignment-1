#!/usr/bin/env python3
from ev3dev.ev3 import *


class RobotController:
    """An interface to control a LEGO ev3 robot."""

    def __init__(self):
        """Set up the controller by getting handles to the robot's various
        sensors and motors.
        """
        # Setup the sonar sensor
        self.turn_ratio = 1.7
        self.uss = UltrasonicSensor()
        # Setup the touch sensor.
        self.ts = TouchSensor()
        # Setup the colour sensor.
        self.cs = ColorSensor()
        self.cs.mode = 'COL-REFLECT'
        self.black = 14
        self.white = 40

        # Setup the motors.
        self.mLeft = LargeMotor('outB')
        self.mRight = LargeMotor('outC')

    def calibrate(self):
        while not self.ts.value():
            pass

        Sound.speak(str(self.cs.value()))
        print(self.cs.value())

        return self.cs.value()

    def move_to_rel(self, degrees, speed=360):
        """Move the robot forward a certain distance.

        Args:
            degrees (int): How many degrees to turn the robot's wheels.
            speed (int): How fast to run the motors.
        """
        self.mLeft.run_to_rel_pos(position_sp=degrees, speed_sp=speed)
        self.mRight.run_to_rel_pos(position_sp=degrees, speed_sp=speed)
        self.mLeft.wait_while('running')
        self.mRight.wait_while('running')

    def move_for_tiles(self, num_tiles, speed=360):
        """Move the robot forward in a straight line for a number of
        black tiles.

        Args:
            num_tiles (int): How many squares to return.
            speed (int): How fast to run the motors.
        """
        prev_val = self.cs.value()
        n = 0  # The number of black tiles counted.
        direction = 1  # The direction to correct the path.
        num_other = 0
        can_count = True

        self.mLeft.run_forever(speed_sp=speed)
        self.mRight.run_forever(speed_sp=speed)

        while n < num_tiles:
            curr_val = self.cs.value()
            print('Tile value: ' + str(curr_val))

            if not (curr_val < self.black or curr_val > self.white):
                num_other += 1
            else:
                num_other = 0

            if num_other > 2:
                self.mLeft.stop()
                self.mRight.stop()

                direction = self._correct_path(direction, 80)
                self.rotate(5 * -direction)

                prev_val = 0
                num_other = 0

                self.mLeft.run_forever(speed_sp=speed)
                self.mRight.run_forever(speed_sp=speed)

            # If the robot was over something white and now it is over
            # something black:
            if prev_val < self.black <= self.cs.value() and can_count:
                n += 1
                can_count = False
                Sound.speak(str(n))

            elif curr_val > self.white:
                can_count = True
            
            prev_val = self.cs.value()
            time.sleep(0.05)

        self.mLeft.stop()
        self.mRight.stop()

        return direction

    def _correct_path(self, direction, speed=360):
        """Correct the robot's heading.

        Args:
            direction (int): The direction to try first (-1 for left, 1 for right).
            speed (int): How fast to turn while trying to correct.

        Returns:
              int: The direction the robot turned to correct it's heading.
        """
        # Try turning right.
        for angle in range(0, 90, 10):
            self.rotate(10 * direction, speed)

            colour = self.cs.value()

            if colour < self.black or colour > self.white:
                return direction

        # Reset to starting direction.
        self.rotate(-90 * direction, speed)

        direction = direction * -1
        # Try turning left.
        for angle in range(0, 90, 10):
            self.rotate(10 * direction, speed)

            colour = self.cs.value()

            if colour < self.black or colour > self.white:
                return direction

        # Reset to starting direction.
        self.rotate(-90 * direction, speed)
        # Backup
        self.move_to_rel(-180)

        return self.correct_path(direction * -1)

    def rotate(self, degrees, speed=360):
        """Rotate the robot either clockwise or counter-clockwise.

        Args:
            degrees (int): How many degrees to turn the robot. Use a negative
                number to rotate the robot counter-clockwise.
            speed (int): How fast to run the motors whilst rotating.
        """
        # Multiplier needed to modify the degrees parameter so that the robot
        # turns that many degrees.
        self.mLeft.run_to_rel_pos(position_sp=degrees * self.turn_ratio, speed_sp=speed)
        self.mRight.run_to_rel_pos(position_sp=-degrees * self.turn_ratio, speed_sp=speed)
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

    def find_tower(self, degrees=180, threshold=800):
        """Find the tower, align the robot with it and find the distance to it.

        Args:
            degrees (int): How many degrees to check when searching for the tower.
            threshold (int): The maximum distance (mm) to detect the tower,
                anything further away than this value will be ignored.

        Returns:
            int: The distance to the tower. Returns sys.maxsize if nothing was
            found within the threshold distance.
        """
        distance = sys.maxsize
        prev_distance = sys.maxsize
        was_found = False  # Whether or not an object was detected within the distance threshold.

        if self.uss.value() < threshold:
            return self.uss.value()

        self.rotate(int(-degrees / 2))

        self.mLeft.run_to_rel_pos(position_sp=degrees * self.turn_ratio, speed_sp=90)
        self.mRight.run_to_rel_pos(position_sp=-degrees * self.turn_ratio, speed_sp=90)

        while 'running' in self.mLeft.state or 'running' in self.mRight.state:
            distance = self.uss.value()
            print('Distance: ' + str(distance))

            # If we found an object previously and now it is getting further
            # away, break
            if was_found and distance > prev_distance:
                # Turn back a bit to correct the angle.
                self.rotate(-10, 180)
                break

            if distance <= threshold:
                was_found = True
                prev_distance = distance

            time.sleep(0.1)

        self.mLeft.stop()
        self.mRight.stop()

        # If nothing was found or the thing found was not within range.
        if not was_found or distance > threshold:
            self.rotate(int(-degrees / 2), speed=180)
            return sys.maxsize

        return distance


def main():
    rbt = RobotController()
    rbt.move_to_rel(degrees=320)
    rbt.rotate(degrees=90)
    rbt.move_for_tiles(num_tiles=15, speed=180)
    rbt.rotate(degrees=90)
    rbt.move_to_rel(degrees=360 * 10, speed=720)
    # Offset the rotation due to the robot veering to the left.
    rbt.rotate(degrees=5, speed=180)
    distance = rbt.find_tower(threshold=800)

    # While nothing is in range...
    while distance == sys.maxsize:
        # Move forward a bit
        rbt.move_to_rel(degrees=360, speed=180)
        # Try find the tower again
        distance = rbt.find_tower(degrees=260, threshold=800)

    rbt.move_to_rel(degrees=360 * (distance / 90), speed=900)  # Ramming speed!
    rbt.beep()


if __name__ == '__main__':
    try:
        btn = Button()
        main()
    except:
        import traceback

        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

        while not btn.any():
            pass
