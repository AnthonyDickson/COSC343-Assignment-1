#!/usr/bin/env python3
from ev3dev.ev3 import *


class RobotController:
    """An interface to control a LEGO ev3 robot."""

    def __init__(self):
        """Set up the controller by getting handles to the robot's various
        sensors and motors.
        """
        # Setup the sonar sensor
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
        dir = -1  # to remember if the last correct was left or right
        num_other = 0
        can_count = True

        self.mLeft.run_forever(speed_sp=speed)
        self.mRight.run_forever(speed_sp=speed)

        while n < num_tiles:
            curr_val = self.cs.value()
            print(curr_val)

            if not (curr_val < self.black or curr_val > self.white):
                num_other += 1
            else:
                num_other = 0

            if num_other > 2:
                self.mLeft.stop()
                self.mRight.stop()

                dir = self.correct_path(dir, 80)
                self.rotate(5 * -dir)

                prev_val = 0
                num_other = 0

                self.mLeft.run_forever(speed_sp=speed)
                self.mRight.run_forever(speed_sp=speed)

            # If the robot was over something white and now it is over
            # something black:
            if prev_val < self.black <= self.cs.value() and can_count:
                n += 1
                can_count = False
                self.beep()

            elif curr_val > self.white:
                can_count = True
            
            prev_val = self.cs.value()
            time.sleep(0.05)

        self.mLeft.stop()
        self.mRight.stop()
        return dir

    def correct_path(self, dir, speed=360):
        # TODO: Check tile count.
        # TODO: Remember which side it went off last time, then next time it
        # goes off it needs to turn in the opposite direction.
        # TODO: Try moving 90 degrees in one direction first.

        # Try turning right.
        for angle in range(0, 90, 10):
            self.rotate(10 * dir, speed)

            colour = self.cs.value()

            if colour < self.black or colour > self.white:
                return dir * -1

        # Reset to starting direction.
        self.rotate(-90 * dir, speed)

        dir = dir * -1
        # Try turning left.
        for angle in range(0, 90, 10):
            self.rotate(10 * dir, speed)

            colour = self.cs.value()

            if colour < self.black or colour > self.white:
                return dir * -1

        # Reset to starting direction.
        self.rotate(-90 * dir, speed)
        # Backup
        self.move_to_rel(-180)

        return self.correct_path(dir * -1)

    def rotate(self, degrees, speed=360):
        """Rotate the robot either clockwise or counter-clockwise.

        Args:
            degrees (int): How many degrees to turn the robot. Use a negative
                number to rotate the robot counter-clockwise.
            speed (int): How fast to run the motors whilst rotating.
        """
        ratio = 1.7
        self.mLeft.run_to_rel_pos(position_sp=degrees * ratio, speed_sp=speed)
        self.mRight.run_to_rel_pos(position_sp=-degrees * ratio, speed_sp=speed)
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

    def find_tower(self, deg=180):
        """Finds the tower by rotating the robot and using the sonar sensor
        finds the closed object.
        """
        distance = 9999
        where = 0
        distance_threshold = 800

        if self.uss.value() < distance_threshold:
            return self.uss.value()

        self.rotate(-deg/2)

        for angle in range(0, deg, 5):
            new_distance = self.uss.value()
            print('Distance: ' + str(new_distance))

            if new_distance < distance:
                if new_distance < distance_threshold:
                    return new_distance

                distance = new_distance
                where = angle

            self.rotate(5, 60)
            time.sleep(0.5)

        angle_to_turn = where - deg

        self.rotate(angle_to_turn, deg)
        print('Where:' + str(where), 'Angle to turn: ' + str(angle_to_turn))
        return distance


def main():
    rbt = RobotController()
    rbt.move_to_rel(320)
    rbt.rotate(90)
    rbt.move_for_tiles(15, 180)
    rbt.rotate(90)
    rbt.move_to_rel(360 * 10, 720)
    distance = rbt.find_tower()
    rbt.move_to_rel(360 * (distance / 250), 360)

    distance = rbt.find_tower(90)
    rbt.move_to_rel(360 * (distance / 100), 900)  # Ramming speed!
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