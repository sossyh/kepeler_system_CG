import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import numpy as np


def init():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45,1,0.1,50)
    gluLookAt(10,10,10,0,0,0,0,1,0)
    glEnable(GL_DEPTH_TEST)
def dispay():