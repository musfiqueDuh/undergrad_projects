from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import sys
import math

boss = {
    "active": False,
    "pos": [0.0, 0.0, -10.0],
    "hp": 5,
    "radius": 2.0
}
obstacles = [
    # x, y, z, width, height, depth
    [-4, 0, 5, 2, 2, 2],      # cube block
    [3, 0, -3, 2, 4, 1.5],    # tall wall
    [0, 0, 10, 5, 1, 1],      # long bar
    [-6, 0, -7, 1, 3, 5],     # vertical wall
]
yaw = 0.0        # left-right
pitch = 0.0      # up-down
last_mouse_x = None
last_mouse_y = None
mouse_sensitivity = 0.2
platform_pos = [0.0, 0.0, -8.0]  # x, y (animated), z
platform_amplitude = 3.0         # how high it moves
platform_speed = 0.002           # bobbing speed
player_pos = [0.0, 0.0, 0.0]
move_speed = 0.2
pressed_keys = set()

collected_names = []
crystal_angle = 0.0
crystal_types = {
    "sapphire":  {"color": (0.2, 0.6, 1.0), "real": True},
    "ruby":      {"color": (1.0, 0.1, 0.1), "real": True},
    "emerald":   {"color": (0.1, 0.9, 0.3), "real": True},
    "bracustone": {"color": (1.0, 0.6, 0.2), "real": False},
    "sadstone":   {"color": (0.5, 0.5, 0.5), "real": False}
}


collected_crystals = 0
collection_radius = 1.5  # how close player must be to collect
lava_height = -2.0 # starts below ground
lava_speed = 0.0001
game_over = False
needs_redraw = True  # Initial redraw needed
enemies = [
    [10.0, 0.0, -10.0],
    [-12.0, 0.0, 8.0]
]
enemy_speed = 0.02
enemy_radius = 1.0


def init():
    glClearColor(0.05, 0.05, 0.08, 1.0)
    glEnable(GL_DEPTH_TEST)

def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(75.0, float(w)/float(h), 0.1, 150.0)
    glMatrixMode(GL_MODELVIEW)



def draw_obstacles():
    glColor3f(0.3, 0.3, 0.3)  # stone gray
 

    for obs in obstacles:
        x, y, z, w, h, d = obs
        glPushMatrix()
        glTranslatef(x, y + h / 2, z)
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

def draw_boss():
    if not boss["active"]:
        return

    glPushMatrix()
    bx, by, bz = boss["pos"]
    time = glutGet(GLUT_ELAPSED_TIME) * 0.002
    bob = math.sin(time) * 0.5
    glTranslatef(bx, by + bob, bz)
    glColor3f(0.7, 0.0, 0.0)
    glutSolidSphere(2.5, 24, 24)
    glPopMatrix()


def draw_cave():
  
    glColor3f(0.15, 0.1, 0.1)  # Dark reddish   # Dim stone-gray

    size = 40   # wider cave
    height = 30 # taller ceiling

    glBegin(GL_QUADS)
    
    # Left wall
    glVertex3f(-size, -1, -size)
    glVertex3f(-size, -1,  size)
    glVertex3f(-size, height,  size)
    glVertex3f(-size, height, -size)

    # Right wall
    glVertex3f(size, -1, -size)
    glVertex3f(size, -1,  size)
    glVertex3f(size, height,  size)
    glVertex3f(size, height, -size)

    # Back wall
    glVertex3f(-size, -1, -size)
    glVertex3f(size, -1, -size)
    glVertex3f(size, height, -size)
    glVertex3f(-size, height, -size)

    # Front wall
    glVertex3f(-size, -1, size)
    glVertex3f(size, -1, size)
    glVertex3f(size, height, size)
    glVertex3f(-size, height, size)

    # Ceiling
    glVertex3f(-size, height, -size)
    glVertex3f(size, height, -size)
    glVertex3f(size, height, size)
    glVertex3f(-size, height, size)

    glEnd()




def draw_platform():
    time = glutGet(GLUT_ELAPSED_TIME)
    y = math.sin(time * platform_speed) * platform_amplitude
    platform_pos[1] = y

    glPushMatrix()
    glTranslatef(platform_pos[0], y, platform_pos[2])
    glColor3f(0.6, 0.6, 0.8)

    glScalef(4, 0.5, 4)  # make it a flat rectangle
    glutSolidCube(1)
    glPopMatrix()

    
def draw_enemies():
    time = glutGet(GLUT_ELAPSED_TIME) * 0.002  # smoother animation

    for i, pos in enumerate(enemies):
        ex, ey, ez = pos

        # Bobbing height using sine wave
        bob = math.sin(time + i) * 0.5  # offset each enemy for variety
        float_y = ey + bob

        glPushMatrix()
        glTranslatef(ex, float_y, ez)
        glColor3f(1.0, 0.1, 0.1)
        glutSolidSphere(1.2, 16, 16)
        glPopMatrix()

def generate_crystals(count=8, spread=20):
    result = []
    names = list(crystal_types.keys())
    for _ in range(count):
        name = random.choice(names)
        info = crystal_types[name]
        x = random.uniform(-spread, spread)
        z = random.uniform(-spread, spread)
        result.append({
            "pos": [x, 0, z],
            "name": name,
            "real": info["real"],
            "color": info["color"]
        })
    return result



def draw_crystals():
    global crystal_angle
    for crystal in crystals:
        pos = crystal["pos"]
        color = crystal["color"]
        glPushMatrix()
        glTranslatef(*pos)
        glRotatef(crystal_angle, 0, 1, 0)
        glColor3f(*color)
        glutSolidCube(1.2)
        glPopMatrix()



def draw_lava():
    glPushMatrix()
    glTranslatef(0.0, lava_height, 0.0)

    # Set red-orange base color
    intensity = 0.8 + 0.2 * math.sin(glutGet(GLUT_ELAPSED_TIME) * 0.005)
    glColor3f(intensity, 0.2 * intensity, 0.0)

    glBegin(GL_QUADS)

    segments = 50
    size = 25

    for x in range(-size, size, 2):
        for z in range(-size, size, 2):
            wave = math.sin((x + z + glutGet(GLUT_ELAPSED_TIME) * 0.005)) * 0.1

            glVertex3f(x, wave, z)
            glVertex3f(x+2, wave, z)
            glVertex3f(x+2, wave, z+2)
            glVertex3f(x, wave, z+2)
    
 
    glEnd()


    glPopMatrix()



def draw_player():
    time = glutGet(GLUT_ELAPSED_TIME) * 0.002
    bob = math.sin(time) * 0.2  # hover up/down effect
    tilt = math.sin(time) * 2.5  # slight forward/back tilt

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1] + bob, player_pos[2])
    glRotatef(-yaw, 0, 1, 0)  # rotate to face movement direction  # tilting animation

    # 🔷 Hoverboard Base
    glPushMatrix()
    glScalef(2.5, 0.3, 1.2)
    glColor3f(0.2, 0.8, 1.0)

    glMaterialf(GL_FRONT, GL_SHININESS, 40)
    glutSolidCube(1)
    glPopMatrix()


    # 🔴 Side Thruster Left
    glPushMatrix()
    glTranslatef(-1.0, -0.2, 0.5)
    glColor3f(1.0, 0.3, 0.3)
 
    glutSolidSphere(0.3, 12, 12)
    glPopMatrix()

    # 🔴 Side Thruster Right
    glPushMatrix()
    glTranslatef(1.0, -0.2, 0.5)
    glColor3f(1.0, 0.3, 0.3)

    glutSolidSphere(0.3, 12, 12)
    glPopMatrix()

    # 💡 (Future Torch Head): Add a front-mounted light here
    # e.g., glTranslatef(0, 0.2, -1.2)

    glPopMatrix()


def display():
    global needs_redraw
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    draw_cave()
    # Follow camera (relative to player)
    eye_x = player_pos[0]
    eye_y = player_pos[1] + 8
    eye_z = player_pos[2] + 20


        # Camera direction vector from yaw and pitch
    rad_yaw = math.radians(yaw)
    rad_pitch = math.radians(pitch)

    look_x = math.cos(rad_pitch) * math.sin(rad_yaw)
    look_y = math.sin(rad_pitch)
    look_z = -math.cos(rad_pitch) * math.cos(rad_yaw)

    # Third-person distance from player (we'll make this toggle later)
    cam_distance = 8
    cam_height = 3

    cam_x = player_pos[0] - look_x * cam_distance
    cam_y = player_pos[1] + cam_height
    cam_z = player_pos[2] - look_z * cam_distance

    gluLookAt(cam_x, cam_y, cam_z,
              player_pos[0], player_pos[1], player_pos[2],
              0, 1, 0)


    # Ground
    glColor3f(0.3, 0.3, 0.3)

    glBegin(GL_QUADS)
    glVertex3f(-20, -1, -20)
    glVertex3f(20, -1, -20)
    glVertex3f(20, -1, 20)
    glVertex3f(-20, -1, 20)
    glEnd()



    
    draw_platform()
    draw_obstacles
    draw_lava()
    # Draw crystals
    draw_crystals()
    draw_enemies()
    # Draw player
    draw_player()
    draw_boss()



    glColor3f(1.0, 1.0, 1.0)
    draw_text(10, 400, f"You must collect the Sacred Stones")
    draw_text(5, 580, f"Crystals: {collected_crystals} / 4")
   
    for i, name in enumerate(collected_names):
        draw_text(10, 560 - i * 20, f"✔ {name.title()}")

    

    if game_over:
        if boss["active"] and boss["hp"] <= 0:
            draw_text(340, 300, "🎉 YOU DEFEATED THE BOSS!", GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(300, 270, "The cavern begins to collapse...", GLUT_BITMAP_HELVETICA_18)

        else:
            draw_text(330, 300, "💀 GAME OVER!", GLUT_BITMAP_TIMES_ROMAN_24)




    glutSwapBuffers()
    needs_redraw = False  # Reset the flag after drawing

def update(value):
    global player_pos, crystal_angle, needs_redraw, lava_height, game_over
    moved = False
    speed = move_speed

    if game_over:
        glutPostRedisplay()
        glutTimerFunc(16, update, 0)
        return

    # --- Player Movement ---
    rad = math.radians(yaw)
    forward_x = math.sin(rad)
    forward_z = -math.cos(rad)
    right_x = math.cos(rad)
    right_z = math.sin(rad)

    if b'w' in pressed_keys:
        player_pos[0] += forward_x * speed
        player_pos[2] += forward_z * speed
        moved = True
    if b's' in pressed_keys:
        player_pos[0] -= forward_x * speed
        player_pos[2] -= forward_z * speed
        moved = True
    if b'd' in pressed_keys:
        player_pos[0] += right_x * speed
        player_pos[2] -= right_z * speed
        moved = True
    if b'a' in pressed_keys:
        player_pos[0] -= right_x * speed
        player_pos[2] += right_z * speed
        moved = True

    # --- Crystal Collection ---
    if moved or crystal_angle > 0:
        needs_redraw = True
        global collected_crystals
        remaining = []

        for crystal in crystals:
            pos = crystal["pos"]
            is_real = crystal["real"]
            dx = player_pos[0] - pos[0]
            dz = player_pos[2] - pos[2]
            distance = math.sqrt(dx*dx + dz*dz)

            if distance > collection_radius:
                remaining.append(crystal)
            else:
                if is_real:
                    collected_crystals += 1
                    collected_names.append(crystal["name"])
                    print(f"💎 Collected a real crystal! Total: {collected_crystals}")
        crystals[:] = remaining

    # --- Enemy Movement ---
    for i in range(len(enemies)):
        ex, ey, ez = enemies[i]
        dx = player_pos[0] - ex
        dz = player_pos[2] - ez
        dist = math.sqrt(dx*dx + dz*dz)
        if dist > 0:
            ex += enemy_speed * dx / dist
            ez += enemy_speed * dz / dist
            enemies[i] = [ex, ey, ez]
        if dist < enemy_radius + 1.0:
            print("💀 Game Over! A fire spirit caught you.")
            game_over = True

    # --- Boss Spawning ---
    if not boss["active"]:
        if all(c["real"] == False for c in crystals):
            print("👹 Boss has appeared!")
            boss["active"] = True
            enemies.clear()  # Remove all fire spirits

            glutPostRedisplay()

    # --- Boss Behavior ---
    if boss["active"]:
        bx, by, bz = boss["pos"]
        dx = player_pos[0] - bx
        dz = player_pos[2] - bz
        dist = math.sqrt(dx*dx + dz*dz)

        if dist > 0:
            bx += 0.01 * dx / dist
            bz += 0.01 * dz / dist
            boss["pos"] = [bx, by, bz]

        # Cooldown-based damage
        if dist < boss["radius"] + 1.0:
            if not boss.get("hit_cd"):
                boss["hp"] -= 1
                boss["hit_cd"] = 30
                print(f"⚔️ Hit the Boss! HP: {boss['hp']}")
        else:
            boss["hit_cd"] = max(0, boss.get("hit_cd", 0) - 1)

        if boss["hp"] <= 2:
            global lava_speed
            lava_speed = 0.05  # Lava detonation trigger

    # --- Platform Handling ---
    dx = player_pos[0] - platform_pos[0]
    dz = player_pos[2] - platform_pos[2]
    dist_xz = math.sqrt(dx*dx + dz*dz)
    if dist_xz < 2.0:
        if abs(player_pos[1] - platform_pos[1]) < 1.5:
            player_pos[1] = platform_pos[1] + 1.0
    else:
        player_pos[1] = 0.0

    # --- Rotate Crystals ---
    crystal_angle += 1.5
    if crystal_angle > 360:
        crystal_angle -= 360

    # --- Lava Rising ---
    lava_height += lava_speed
    if lava_height >= player_pos[1] - 1.0 and not game_over:
        print("🔥 Game Over! Lava reached you.")
        game_over = True

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


def mouse_motion(x, y):
    global yaw, pitch, last_mouse_x, last_mouse_y

    if last_mouse_x is None:
        last_mouse_x = x
        last_mouse_y = y
        return

    dx = x - last_mouse_x
    dy = y - last_mouse_y

    last_mouse_x = x
    last_mouse_y = y

    yaw += dx * mouse_sensitivity
    pitch -= dy * mouse_sensitivity  # invert y for FPS-style look

    # Clamp pitch to avoid flipping
    pitch = max(-89.0, min(89.0, pitch))


def key_down(key, x, y):
    global pressed_keys, needs_redraw
    pressed_keys.add(key)
    needs_redraw = True # Need to redraw when a key is pressed (even if no movement yet)
    if key == b'\x1b':
        sys.exit()

def key_up(key, x, y):
    global pressed_keys
    if key in pressed_keys:
        pressed_keys.remove(key)

def draw_text(x, y, text, font=GLUT_BITMAP_TIMES_ROMAN_24):
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

crystals = generate_crystals(8)




glutInit()

glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 600)
glutInitWindowPosition(100, 100)
glutCreateWindow(b"Crystal Rush 3D - Glowing Crystals")

init()

glutPassiveMotionFunc(mouse_motion)  # handles mouse move without click
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(key_down)
glutKeyboardUpFunc(key_up)
glutTimerFunc(0, update, 0)
glutMainLoop()