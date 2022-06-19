import os
import pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

path = ''

class TextureLoader:
    generate_on_init = True

    def __init__(self, filename, swapyz=False):
        self.faces = []
        self.normals = []
        self.texcoords = []
        self.vertices = []
        self.gl_list = 0
        material = None
        dirname = os.path.dirname(filename)

        for line in open(path + filename, "r"):
            if line.startswith('#'): continue
            codes = line.split()
            if not codes: continue
            if line.startswith('@'):
                return
            if line.startswith('!'):
                return
            if line.startswith('$'):
                return
            if line.startswith('*'):
                return
            if codes[0] == 'v':
                vertex = list(map(float, codes[1:4]))
                if swapyz:
                    vertex = vertex[0], vertex[2], vertex[1]
                self.vertices.append(vertex)

            elif codes[0] == 'vt':
                self.texcoords.append(list(map(float, codes[1:3])))

            elif codes[0] == 'vn':
                normal = list(map(float, codes[1:4]))
                if swapyz:
                    normal = normal[0], normal[2], normal[1]
                self.normals.append(normal)

            elif codes[0] == 'mtllib':
                self.mtl = self.materialLoad(os.path.join(dirname, codes[1]))

            elif codes[0] in ('usemtl', 'usemat'):
                material = codes[1]

            elif codes[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in codes[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))

        if self.generate_on_init:
            self.generate()

    def normal(self):
            return self.normals
    def faces(self):
            return self.faces
    def texcoords(self):
            return self.texcoords
    def vertices(self):
            return self.vertices
    def gl_list(self):
            return self.gl_list

    @classmethod
    def textureLoad(cls, imagefile, text=1):
        surf = pygame.image.load(imagefile)
        image = pygame.image.tostring(surf, 'RGBA', text)
        ix, iy = surf.get_rect().size
        texid = glGenTextures(text)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        return texid

    @classmethod
    def materialLoad(cls, filename, mtl=None, contents={}):

        dirname = os.path.dirname(path + filename)
        if (filename == None):
            print("the file doesnot exist")
            return
        if(dirname==None):
            print("the directory doesnot exist")
            return

        for line in open(filename, "r"):
            if line.startswith('#'): continue
            items = line.split()
            if not items: continue

            if items[0] == 'newmtl':
                mtl = contents[items[1]] = {}
            elif mtl is None:
                raise ValueError("MTL file doesn't start with newmtl stmt")
            elif items[0] == 'map_Kd':
                mtl[items[0]] = items[1]
                imagefile = os.path.join(dirname, mtl['map_Kd'])
                mtl['texture_Kd'] = cls.textureLoad(imagefile)
            else:
                mtl[items[0]] = list(map(float, items[1:]))
        return contents

    def filereading(self,file):
        for i in file:
            lin = i.split(" ")
            if(lin==None):
                return
        if (self.normals != None):
            return self.normals
        if (self.gl_list != None):
            return self.gl_list
        if (self.faces != None):
            return self.faces
        if (self.texcoords != None):
            return self.texcoords

    def generate(self,glGenlist_value=1):
        self.gl_list = glGenLists(glGenlist_value)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face

            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                glColor(*mtl['Kd'])

            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - glGenlist_value])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - glGenlist_value])
                glVertex3fv(self.vertices[vertices[i] - glGenlist_value])
            glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()

    def render(self):
        glCallList(self.gl_list)

    def free(self):
        glDeleteLists([self.gl_list])
    def no_reader(self, file):
        return


class Display:
    def __init__(self, viewsize, gl_ambient, gl_diffuse, gl_position=(-40, 200, 100, 0.0)):
        self.viewsize = viewsize
        self.gl_ambient = gl_ambient
        self.gl_diffuse = gl_diffuse
        self.gl_position = gl_position

    def viewsize(self):
        return self.viewsize()
    def gl_ambient(self):
        return self.gl_ambient
    def gldiffuse(self):
        return self.gl_diffuse
    def gl_position(self):
        return self.gl_position
    def start(self, filename):
        pygame.init()
        srf = pygame.display.set_mode(self.viewsize, OPENGL | DOUBLEBUF | pygame.RESIZABLE)
        cl = pygame.time.Clock()

        # Lighting
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.gl_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.gl_diffuse)
        glLightfv(GL_LIGHT0, GL_POSITION, self.gl_position)

        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        global specref
        specref = (1.0, 1.0, 1.0, 1.0)

        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specref)
        glMateriali(GL_FRONT, GL_SHININESS, 128)
        glShadeModel(GL_SMOOTH)

        # Texture
        objkepler_90 = TextureLoader(filename)
        objkepler_90.generate()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(80.0, self.viewsize[0] / float(self.viewsize[1]), 1, 1000.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glMatrixMode(GL_MODELVIEW)

        z = 5
        rx, ry = (0, 0)
        tx, ty = (0, 0)

        rotate, move = False, False
        while True:
            cl.tick(30)

            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_UP]:
                z = z - 1
            elif keys_pressed[pygame.K_DOWN]:
                z = z + 1

            elif keys_pressed[pygame.K_RIGHT]:
                tx = tx - 3.5
            elif keys_pressed[pygame.K_LEFT]:
                tx = tx + 3.5
            elif keys_pressed[pygame.K_a]:
                glPushMatrix()
                glTranslate(rx, ry, 90)
                glPopMatrix()
                glLoadIdentity()

            for e in pygame.event.get():
                if e.type == QUIT:
                    run = False
                elif e.type == KEYDOWN and e.key == K_ESCAPE:
                    run = False

                elif e.type == MOUSEBUTTONUP:
                    if e.button == 1:
                        rotate = False
                    elif e.button == 3:
                        move = False
                elif e.type == MOUSEBUTTONDOWN:
                    if e.button == 4:
                        z = max(1, z - 1)
                    elif e.button == 5:
                        z = z + 1
                    elif e.button == 1:
                        rotate = True
                    elif e.button == 3:
                        move = True
                elif e.type == MOUSEMOTION:
                    l, r = e.rel

                    if move:
                        ty = ty + r
                        tx = tx + l
                    if rotate:
                        ry = ry + r
                        rx = rx + l


            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            lightPos = (-50.0, 50.0, 100.0, 1.0)

            glTranslate(tx / 20., ty / 20., - z)
            glRotate(rx, 0, 1, 0)
            glRotate(ry, 1, 0, 0)

            # RENDER OBJECT
            objkepler_90.render()

            glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

            pygame.display.flip()

        pygame.quit()

display = Display((1300, 900), (0.2, 0.2, 0.2, 1.0), (0.5, 0.5, 0.5, 1.0))
display.start('kepler-90.obj')
