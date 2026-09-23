import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
import numpy as np

# --- PARÁMETROS DEL HARDWARE ---
G_GRAVITY = 9.81
DT = 0.005
EPSILON_VL = 0.2  

K_SUELO = 5000.0
K_DAMPING_SUELO = 120.0
K_TRACCION_REVERSA = 300.0  
K_TRACCION_AVANCE = 5.0     

K_TENSION = 400.0    
FRECUENCIA = 4.0     
AMPLITUD = 0.8       

# --- NUEVOS PARÁMETROS DE DIRECCIÓN ---
K_FRICCION_LATERAL = 15.0  # El neumático: Agarre lateral, bajó de 50 (freno de mano) a 15
FUERZA_GIRO = 150.0        # El servo de dirección: Cuánta fuerza hace la cabeza para doblar

# --- FÍSICA EN 3D ---
class Node:
    def __init__(self, x, y, z):
        # Ahora los vectores tienen 3 dimensiones (X, Y, Z)
        self.pos = np.array([x, y, z], dtype=float)
        self.vel = np.array([0.0, 0.0, 0.0], dtype=float)
        self.force = np.array([0.0, 0.0, 0.0])

def compute_physics(nodes, t, volante):
    for n in nodes:
        n.force = np.array([0.0, -1.0 * G_GRAVITY, 0.0])

    for i in range(len(nodes)-1):
        n1, n2 = nodes[i], nodes[i+1]
        
        fase = i * 1.5 
        target_len = 1.5 + np.sin(t * FRECUENCIA - fase) * AMPLITUD
        
        delta_p = n2.pos - n1.pos
        dist = np.linalg.norm(delta_p)
        dir_p = delta_p / (dist + 1e-9)
        
        f_tension = K_TENSION * (dist - target_len) * dir_p
        f_damp = 10.0 * (n2.vel - n1.vel)
        
        n1.force += f_tension + f_damp
        n2.force -= f_tension + f_damp

    for n in nodes:
        dist_floor = n.pos[1]
        if dist_floor < EPSILON_VL:
            penetration = EPSILON_VL - dist_floor
            n.force[1] += K_SUELO * penetration - K_DAMPING_SUELO * n.vel[1]
            
            # Tracción en X (Avance)
            if n.vel[0] < 0:
                n.force[0] -= n.vel[0] * K_TRACCION_REVERSA
            else:
                n.force[0] -= n.vel[0] * K_TRACCION_AVANCE
                
            # 🛠️ SACAMOS EL FRENO DE MANO: Fricción lateral domada
            n.force[2] -= n.vel[2] * K_FRICCION_LATERAL

    # 🛠️ INYECCIÓN DE DIRECCIÓN: La cabeza (el último nodo en +X) tira hacia los costados
    # nodes[-1] es la "trompa" de la oruga porque construiste los nodos de 0 a 6 en X.
    if nodes[-1].pos[1] < EPSILON_VL + 0.5: # Solo dobla si la cabeza está tocando el piso
        nodes[-1].force[2] += volante * FUERZA_GIRO

def update(nodes, t, volante):
    compute_physics(nodes, t, volante)
    for n in nodes:
        n.vel += n.force * DT
        n.pos += n.vel * DT
        n.vel *= 0.995

# --- RENDERIZADO 3D CON OPENGL ---
def build_grid_vbo(grid_size=60, step=2):
    vertices = []
    
    # Líneas Z (Longitudinales)
    for z in range(-20, 21, 2):
        vertices.extend([-grid_size, 0.0, z,  grid_size, 0.0, z])
        
    # Líneas X (Transversales)
    for x in range(-grid_size, grid_size + step, step):
        vertices.extend([x, 0.0, -20,  x, 0.0, 20])
        
    # CRÍTICO: PyOpenGL necesita que el array sea np.float32 estricto
    vertex_data = np.array(vertices, dtype=np.float32)
    
    # Mandamos el bloque a la VRAM de la placa de video
    return vbo.VBO(vertex_data)

def draw_ground_vbo(cam_x, grid_vbo):
    # 1. SUELO BASE (Plano oscuro)
    glDisable(GL_LIGHTING)
    glColor3f(0.05, 0.05, 0.1)
    
    base_x = cam_x
    w = 100.0
    
    glBegin(GL_QUADS)
    glVertex3f(base_x - w, -0.1, -w)
    glVertex3f(base_x - w, -0.1,  w)
    glVertex3f(base_x + w, -0.1,  w)
    glVertex3f(base_x + w, -0.1, -w)
    glEnd()

    # 2. GRILLA "CYBER" CON INYECCIÓN ELECTRÓNICA (VBO)
    glLineWidth(1.0)
    glColor3f(0.0, 0.4, 0.4) 
    
    glPushMatrix()
    # TRUCO DE TALLER: Movemos la grilla pre-fabricada junto con la cámara.
    # Usamos int() para que calce perfecto y no "tiemble" visualmente.
    glTranslatef(int(cam_x), 0.0, 0.0)
    
    # Conectamos la manguera de datos (VBO)
    grid_vbo.bind()
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, grid_vbo)
    
    # ¡BAM! Dibujamos todos los vértices de un solo golpe
    num_vertices = len(grid_vbo.data) // 3
    glDrawArrays(GL_LINES, 0, num_vertices)
    
    # Desconectamos todo para no ensuciar el resto del render
    glDisableClientState(GL_VERTEX_ARRAY)
    grid_vbo.unbind()
    glPopMatrix()
    
    glEnable(GL_LIGHTING)

def draw_caterpillar(nodes, quadric):
    
    # Dibujar conexiones (Músculos)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(4.0)
    glBegin(GL_LINE_STRIP)
    for n in nodes:
        glVertex3f(n.pos[0], n.pos[1], n.pos[2])
    glEnd()

    # Dibujar Nodos (Esferas)
    glColor3f(1.0, 0.0, 1.0) # Color Magenta
    for n in nodes:
        glPushMatrix()
        glTranslatef(n.pos[0], n.pos[1], n.pos[2])
        gluSphere(quadric, 0.3, 16, 16)
        glPopMatrix()

def main():
    pygame.init()
    display = (1024, 768)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    # --- LA MAGIA QUE FALTABA ---
    glMatrixMode(GL_PROJECTION) # 1. Avisamos que configuramos la "lente"
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 100.0)
    
    glMatrixMode(GL_MODELVIEW)  # 2. Volvemos al modo de mover objetos y cámara
    # ----------------------------

    # --- CONFIGURACIÓN VISUAL NEXT-GEN ---
    glEnable(GL_DEPTH_TEST)
    
    # 1. ILUMINACIÓN (Para que se vea 3D de verdad)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL) # Para que glColor funcione con luces
    glEnable(GL_NORMALIZE)
    
    # Luz del Sol (Directional)
    glLightfv(GL_LIGHT0, GL_POSITION, (10.0, 20.0, 10.0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.3, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
    
    # 2. ATMÓSFERA (Niebla y Fondo)
    dark_blue = (0.02, 0.02, 0.05, 1.0)
    glClearColor(*dark_blue) # Fondo
    
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, dark_blue)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 50.0) # Todo desaparece suavemente a 50m

    # Inicializar Oruga y Herramientas
    oruga = [Node(i * 1.5, 1.0, 0.0) for i in range(6)]
    esfera_quadric = gluNewQuadric()
    
    # 🛠️ CREAMOS EL VBO EN LA VRAM AL ARRANCAR
    mi_grid_vbo = build_grid_vbo()

    t = 0.0
    clock = pygame.time.Clock()

    print("🚀 Simulación 3D Iniciada con Inyección VBO.")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 🛠️ LEEMOS EL VOLANTE (A/D o Flechas)
        keys = pygame.key.get_pressed()
        volante = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            volante = -1.0 # Volantazo a la izquierda (-Z)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            volante = 1.0  # Volantazo a la derecha (+Z)

        # Actualizar física
        for _ in range(3):
            # 🛠️ LE PASAMOS EL VOLANTE AL MOTOR
            update(oruga, float(t), volante)
                
            t += DT

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity() # Ahora esto limpia la posición, no la lente

        # CÁMARA DINÁMICA
        cam_x = float(oruga[2].pos[0]) # Asegurar float para gluLookAt
        gluLookAt(cam_x - 5.0, 4.0, 12.0, 
                  cam_x + 2.0, 1.0, 0.0,   
                  0.0, 1.0, 0.0)           

        # 🛠️ USAMOS LA NUEVA FUNCIÓN OPTIMIZADA
        draw_ground_vbo(cam_x, mi_grid_vbo)
        draw_caterpillar(oruga, esfera_quadric)

        pygame.display.flip()
        clock.tick(60)

    # Limpieza final
    gluDeleteQuadric(esfera_quadric)
    mi_grid_vbo.delete() # Borramos el VBO de la placa de video
    pygame.quit()

if __name__ == "__main__":
    main()