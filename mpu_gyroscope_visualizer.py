import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import mpu_lib
import time
from math import pi


Vertices = (
    (1, 1, 1),
    (1, 1, -1),
    (1, -1, -1),
    (1, -1, 1),
    (-1, 1, 1),
    (-1, -1, -1),
    (-1, -1, 1),
    (-1, 1, -1),
)
Edges = (
    (0, 1),
    (0, 3),
    (0, 4),
    (1, 2),
    (1, 7),
    (2, 5),
    (2, 3),
    (3, 6),
    (4, 6),
    (4, 7),
    (5, 6),
    (5, 7),
)
Quads = (
    (0, 3, 6, 4),
    (2, 5, 6, 3),
    (1, 2, 5, 7),
    (1, 0, 4, 7),
    (7, 4, 6, 5),
    (2, 3, 0, 1),
)


def wireCube():
    glBegin(GL_LINES)
    for cubeEdge in Edges:
        for vertex in cubeEdge:
            glVertex3fv(Vertices[vertex])
    glEnd()


if __name__ == "__main__":
    # Setup Display
    pg.init()
    display = (800, 600)
    pg.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    # Setup MPU
    sensor = mpu_lib.mpu_6050()
    # Setup Timing variables

    lasttime = time.time()
    now = time.time()
    while True:

        # Get latest Gyro data and the time
        gyro_data = sensor.get_gyro_data()
        accel_data = sensor.get_accel_data()

        now = time.time()
        time_delta = now - lasttime
        lasttime = now

        # Deterimine how much sensor has rotated with some deadzone limit
        x_rotate_degrees = gyro_data["x"] / time_delta
        y_rotate_degrees = gyro_data["y"] / time_delta
        z_rotate_degrees = gyro_data["z"] / time_delta
        deadzone = 3
        damping_parameter = 100
        if abs(gyro_data["x"]) < deadzone:
            x_rotate_degrees = 0
        else:
            x_rotate_degrees = x_rotate_degrees / damping_parameter
        if abs(gyro_data["y"]) < deadzone:
            y_rotate_degrees = 0
        else:
            y_rotate_degrees = y_rotate_degrees / damping_parameter
        if abs(gyro_data["z"]) < deadzone:
            z_rotate_degrees = 0
        else:
            z_rotate_degrees = z_rotate_degrees / damping_parameter

        # Rotate the display
        glRotatef(x_rotate_degrees, 0, 1, 0)
        glRotatef(y_rotate_degrees, 1, 0, 0)
        glRotatef(z_rotate_degrees, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        wireCube()
        pg.display.flip()

        debug_print = True
        if debug_print:
            print("---------------------------------------------------")
            print("-------------Gyroscope-----------------")
            print("Time Delta Since Last Update: " + str(time_delta) + " seconds")
            print("Gyro X: " + str(gyro_data["x"]) + " degrees/second")
            print("Gyro Y: " + str(gyro_data["y"]) + " degrees/second")
            print("Gyro Z: " + str(gyro_data["z"]) + " degrees/second")
            print("Change in X: " + str(x_rotate_degrees) + " degrees")
            print("Change in Y: " + str(y_rotate_degrees) + " degrees")
            print("Change in Z: " + str(z_rotate_degrees) + " degrees")
            print("-------------Accelerometer-----------------")
            print("Acc X : " + str(accel_data["x"]))
            print("Acc Y : " + str(accel_data["y"]))
            print("Acc Z : " + str(accel_data["z"]))
            print("-------------Temperature-----------------")
            print("Temperature in Celcius: " + str(sensor.readTemp(False)))
            print("Temperature in Farenheit: " + str(sensor.readTemp(True)))
            print("---------------------------------------------------")
        pg.time.wait(200)
