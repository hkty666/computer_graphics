import math
import os
import sys

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

cam_radius = 5.0
cam_pos = [0.0, 0.0, cam_radius]
Lissa_t = 0.0
light_pos = np.array([3.0, 2.0, -1.0])
ambient_light = np.array([0.2, 0.4, 0.4])       # ambient light (k_a * I_a)
k_d = np.array([0.0, 0.6, 0.9])                 # diffuse reflectance
I_q = 10.0                                       # light intensity
g_theta = math.pi/2
g_phi = 0
bump = Image.open(os.path.dirname(__file__)+'/INIAD_bump.png')
w, h = bump.size
bump_data = [[[0] * 3 for i in range(h)] for j in range(w)]
texID = 0


def load_texture():
    global bump_data
    rgb_im = bump.convert('RGB')

    for i in range(w):
        for j in range(h):
            bump_data[i][h - 1 - j] = rgb_im.getpixel((i, j))


def draw_axis():
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3d(0, 0, 0)
    glVertex3d(1000, 0, 0)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3d(0, 0, 0)
    glVertex3d(0, 1000, 0)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3d(0, 0, 0)
    glVertex3d(0, 0, 1000)
    glEnd()


'''
point: a coordinate of a polygon
light: a coordinate of a point light source
xz_plane: y-coordinate of the plane parallel to the xz plane
'''


# def calculate_intersection_to_plane(point, light, xz_plane):
#     d = point - light
#     t = (xz_plane - light[1]) / d[1] if d[1] != 0 else 0
#     if t > 0:
#         ## calculate intersection point using t and return the coordinate  ##
#         return light + t * d
#     else:
#         return [math.inf, math.inf, math.inf]


'''
Calculate and draw each shadow on the xz plane created by a point light source for each polygon on a sphere
'''


def calculate_color(point, normal, light, intensity, ambient, diffuse):
    L = light - point
    r = np.linalg.norm(L)
    N = normal / \
        np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else normal
    L = L/r if r != 0 else L

    ## Calculate the color based on L, N, r, intensity, diffuse_coefficient and ambient_light. If the surface is hidden surface when looking from light, return only ambient_light ##
    color = diffuse * intensity * \
        np.dot(L, N)/(r**2) + ambient if np.dot(L, N) >= 0 else ambient
#    color = ambient
    return color


def draw_bump_plane():
    width = 50
    height = 50
    for j in range(0, height):
        for i in range(0, width):
            n00 = bump_data[(int)(w * i/width)][(int)(h * j/height)]
            # if (int)(h * (j+1)/height) < height else bump_data
            n01 = bump_data[(int)(w * i/width)][(int)(h * (j)/height)]
            # if (int)(w * (i+1)/width) < w and (int)(height[0]) else bump_data
            n11 = bump_data[(int)(w * (i)/width)][(int)(h * (j)/height)]
            # if (int)(w * (i+1)/width) < w else bump_data[w]
            n10 = bump_data[(int)(w * (i)/width)][(int)(h * j/height)]

            p00 = np.array([0., 1 - 2 * j/height, 2 * i/width - 1])
            p01 = np.array([0., 1 - 2 * (j+1)/height, 2 * i/width - 1])
            p11 = np.array([0., 1 - 2 * (j+1)/height, 2 * (i+1)/width - 1])
            p10 = np.array([0., 1 - 2 * j/height, 2 * (i+1)/width - 1])

            c00 = calculate_color(p00, np.array(
                n00), light_pos, I_q, ambient_light, k_d)
            c01 = calculate_color(p01, np.array(
                n01), light_pos, I_q, ambient_light, k_d)
            c11 = calculate_color(p11, np.array(
                n11), light_pos, I_q, ambient_light, k_d)
            c10 = calculate_color(p10, np.array(
                n10), light_pos, I_q, ambient_light, k_d)

            glBegin(GL_QUADS)
            glColor3f(c00[0], c00[1], c00[2])
            glVertex3f(p00[0], p00[1], p00[2])

            glColor3f(c01[0], c01[1], c01[2])
            glVertex3f(p01[0], p01[1], p01[2])

            glColor3f(c11[0], c11[1], c11[2])
            glVertex3f(p11[0], p11[1], p11[2])

            glColor3f(c10[0], c10[1], c10[2])
            glVertex3f(p10[0], p10[1], p10[2])

            glEnd()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(400, 400)     # window size
    glutInitWindowPosition(100, 100)  # window position
    glutCreateWindow(b"bump mapping")  # show window
    glutDisplayFunc(display)         # draw callback function
    glutReshapeFunc(reshape)         # resize callback function
    glutKeyboardFunc(mykey)          # keyboad callback function
    glutSpecialFunc(mykey)
    init(400, 400)
    glutIdleFunc(idle)
    glutMainLoop()


def init(width, height):
    global texID
    """ initialize """
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)  # enable shading

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # set perspective
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    texID = load_texture()


def mykey(key, x, y):
    global g_theta, g_phi, draw_line_flag
    if key == GLUT_KEY_RIGHT:
        g_phi -= 0.1
    if key == GLUT_KEY_LEFT:
        g_phi += 0.1
    if key == GLUT_KEY_UP:
        g_theta -= 0.1
        if g_theta < -math.pi:
            g_theta = math.pi
    if key == GLUT_KEY_DOWN:
        g_theta += 0.1
        if g_theta > math.pi:
            g_theta = -math.pi


def display():
    """ display """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
   # set camera
    global cam_pos
    cam_x = cam_radius * math.sin(g_theta) * math.cos(g_phi)
    cam_y = cam_radius * math.cos(g_theta) + 2
    cam_z = cam_radius * math.sin(g_theta) * math.sin(g_phi)
    top = 1.0 if g_theta >= 0.0 else -1.0
    gluLookAt(cam_x, cam_y, cam_z, 0.0, 0.0, 0.0, 0.0, top, 0.0)
    cam_pos = [cam_x, cam_y, cam_z]
#    gluLookAt(0.0, 0.1, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    # draw_floor()
    # draw_sphere_shadow(50, 50)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    draw_axis()
    draw_bump_plane()
    glFlush()  # enforce OpenGL command
    glutSwapBuffers()


def idle():
    # global Lissa_t, light_pos
    # Lissa_t += 0.1
    # light_pos = np.array(
    #     [2*math.sin(3*Lissa_t)+1.0, 4.0, 2*math.sin(4*Lissa_t)])
    glutPostRedisplay()


def reshape(width, height):
    """callback function resize window"""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)


if __name__ == "__main__":
    main()
