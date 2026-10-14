from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys, math

# Game state variables
player_pos = [0.0, 0.0, 0.0]
move_speed = 0.2
pressed_keys = set()
yaw = 0.0
pitch = 0.0
last_mouse_x = None
last_mouse_y = None
mouse_sensitivity = 0.2

crystal_angle = 0.0
crystals = [[5, 0, 5], [-5, 0, -5], [10, 0, -2], [-8, 0, 7]]
collected_crystals = 0
collection_radius = 1.5

enemies = [[10.0, 0.0, -10.0], [-12.0, 0.0, 8.0]]
enemy_speed = 0.02
enemy_radius = 1.0

lava_height = -2.0
lava_speed = 0.001
game_over = False
needs_redraw = True
boosting = False
boost_speed = 0.4
normal_speed = 0.2

platform_pos = [0.0, 0.0, -8.0]
platform_amplitude = 3.0
platform_speed = 0.002

obstacles = [[-4, 0, 5, 2, 2, 2], [3, 0, -3, 2, 4, 1.5], [0, 0, 10, 5, 1, 1], [-6, 0, -7, 1, 3, 5]]
moving_obstacles = [{"base": [0, 0, -5], "amp": 2.5, "speed": 0.003, "size": [1.5, 2, 1.5]}]

def init():
    glClearColor(0.05, 0.05, 0.08, 1.0)
    glEnable(GL_DEPTH_TEST)

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(75.0, float(w)/float(h), 0.1, 150.0)
    glMatrixMode(GL_MODELVIEW)

def draw_cave():
    glColor3f(0.15, 0.1, 0.1)
    size = 40
    height = 30
    glBegin(GL_QUADS)
    for wall in [(-size, 1, -size), (size, 1, -size), (size, 1, size), (-size, 1, size)]:
        glVertex3f(*wall)
    glEnd()

def draw_crystals():
    global crystal_angle
    time = glutGet(GLUT_ELAPSED_TIME) * 0.002
    for pos in crystals:
        glPushMatrix()
        glTranslatef(*pos)
        glRotatef(crystal_angle, 0, 1, 0)
        intensity = 0.5 + 0.5 * math.sin(time)
        glColor3f(0.2 * intensity, 0.6 * intensity, 1.0 * intensity)
        glutSolidCube(1.2)
        glPopMatrix()

def draw_enemies():
    time = glutGet(GLUT_ELAPSED_TIME) * 0.002
    for i, pos in enumerate(enemies):
        ex, ey, ez = pos
        bob = math.sin(time + i) * 0.5
        float_y = ey + bob
        glPushMatrix()
        glTranslatef(ex, float_y, ez)
        glColor3f(1.0, 0.1, 0.1)
        glutSolidSphere(1.2, 16, 16)
        glPopMatrix()

def draw_lava():
    glPushMatrix()
    glTranslatef(0.0, lava_height, 0.0)
    glColor3f(1.0, 0.3, 0.0)
    glBegin(GL_QUADS)
    for x in range(-25, 25, 2):
        for z in range(-25, 25, 2):
            wave = math.sin((x + z + glutGet(GLUT_ELAPSED_TIME) * 0.005)) * 0.1
            glVertex3f(x, wave, z)
            glVertex3f(x+2, wave, z)
            glVertex3f(x+2, wave, z+2)
            glVertex3f(x, wave, z+2)
    glEnd()
    glPopMatrix()

def draw_obstacles():
    glColor3f(0.3, 0.3, 0.3)
    for obs in obstacles:
        x, y, z, w, h, d = obs
        glPushMatrix()
        glTranslatef(x, y + h / 2, z)
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

def draw_moving_obstacles():
    time = glutGet(GLUT_ELAPSED_TIME)
    glColor3f(0.8, 0.2, 0.2)
    for mob in moving_obstacles:
        bx, by, bz = mob["base"]
        amp = mob["amp"]
        speed = mob["speed"]
        w, h, d = mob["size"]
        y = by + math.sin(time * speed) * amp
        glPushMatrix()
        glTranslatef(bx, y + h/2, bz)
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

def draw_platform():
    time = glutGet(GLUT_ELAPSED_TIME)
    y = math.sin(time * platform_speed) * platform_amplitude
    platform_pos[1] = y
    glPushMatrix()
    glTranslatef(platform_pos[0], y, platform_pos[2])
    glColor3f(0.6, 0.6, 0.8)
    glScalef(4, 0.5, 4)
    glutSolidCube(1)
    glPopMatrix()

def draw_player():
    time = glutGet(GLUT_ELAPSED_TIME) * 0.002
    bob = math.sin(time) * 0.2
    tilt = math.sin(time) * 2.5
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1] + bob, player_pos[2])
    glRotatef(-yaw, 0, 1, 0)
    glRotatef(tilt, 1, 0, 0)
    glPushMatrix()
    glScalef(2.5, 0.3, 1.2)
    glColor3f(0.2, 0.8, 1.0)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-1.0, -0.2, 0.5)
    glColor3f(1.0, 0.3, 0.3)
    glutSolidSphere(0.3, 12, 12)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(1.0, -0.2, 0.5)
    glColor3f(1.0, 0.3, 0.3)
    glutSolidSphere(0.3, 12, 12)
    glPopMatrix()
    glPopMatrix()
