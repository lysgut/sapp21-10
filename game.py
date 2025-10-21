import pygame
import sys
import time

pygame.init()

# --- CONFIGURACIÓN ---
ANCHO, ALTO = 900, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Cuidado con el CO - Juego educativo")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 120, 255)
ROJO = (200, 0, 0)
VERDE = (0, 200, 0)
GRIS = (60, 60, 60)
AMARILLO = (255, 200, 0)

# Fuentes
font = pygame.font.SysFont("arial", 26)
font_big = pygame.font.SysFont("arial", 40, bold=True)

# Reloj
clock = pygame.time.Clock()

# --- JUGADOR ---
jugador = pygame.Rect(100, 400, 40, 60)
velocidad = 5

# --- OBJETOS INTERACTIVOS ---
objetos = [
    {"rect": pygame.Rect(300, 420, 60, 60), "color": ROJO, "texto": "El calefactor sin ventilación puede producir CO.\nAsegúrate de que tenga salida al exterior."},
    {"rect": pygame.Rect(550, 420, 80, 60), "color": GRIS, "texto": "Nunca uses el horno para calefaccionar.\nEl CO puede acumularse sin que te des cuenta."},
    {"rect": pygame.Rect(750, 380, 60, 100), "color": AZUL, "texto": "Abrí la ventana para ventilar la casa.\nVentilar salva vidas."},
]

# Estado del juego
indice_mensaje = None
mensaje_tiempo = 0
mensajes_vistos = set()
ventana_abierta = False
nivel_CO = 50  # arranca moderado
juego_activo = True
mostrar_resumen = False

# --- FUNCIONES ---
def mostrar_texto_centrado(texto, color, y):
    t = font.render(texto, True, color)
    pantalla.blit(t, (ANCHO//2 - t.get_width()//2, y))

def burbuja_info(texto, color_fondo=AMARILLO):
    lineas = texto.split("\n")
    max_ancho = max(font.size(l)[0] for l in lineas) + 40
    alto_total = len(lineas)*30 + 20
    x = ANCHO//2 - max_ancho//2
    y = ALTO - alto_total - 40
    pygame.draw.rect(pantalla, color_fondo, (x, y, max_ancho, alto_total), border_radius=10)
    pygame.draw.rect(pantalla, NEGRO, (x, y, max_ancho, alto_total), 3, border_radius=10)
    for i, l in enumerate(lineas):
        t = font.render(l, True, NEGRO)
        pantalla.blit(t, (x+20, y+15 + i*30))

def resumen_final():
    pantalla.fill(GRIS)
    mostrar_texto_centrado("¡Bien hecho!", VERDE, 100)
    mostrar_texto_centrado("Aprendiste cómo prevenir el monóxido de carbono:", BLANCO, 180)
    texto = [
        "✔ Ventilar los ambientes con frecuencia.",
        "✔ Controlar los calefactores y evitar braseros en lugares cerrados.",
        "✔ No usar el horno como calefacción.",
        "✔ Ante síntomas (mareo, náusea, dolor de cabeza), salir al aire libre y llamar al 107.",
    ]
    for i, t in enumerate(texto):
        mostrar_texto_centrado(t, AMARILLO, 250 + i*50)
    mostrar_texto_centrado("Presioná R para volver a jugar o ESC para salir", BLANCO, 520)

# --- BUCLE PRINCIPAL ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    teclas = pygame.key.get_pressed()

    if juego_activo:
        # Movimiento
        if teclas[pygame.K_LEFT]: jugador.x -= velocidad
        if teclas[pygame.K_RIGHT]: jugador.x += velocidad
        jugador.x = max(0, min(ANCHO - jugador.width, jugador.x))

        # Interacciones
        indice_mensaje = None
        for i, obj in enumerate(objetos):
            if jugador.colliderect(obj["rect"]):
                indice_mensaje = i
                if teclas[pygame.K_SPACE]:
                    mensaje_tiempo = time.time()
                    mensajes_vistos.add(i)
                    if "ventana" in obj["texto"].lower():
                        ventana_abierta = True
                        nivel_CO -= 30

        # Cambia el nivel de CO
        if not ventana_abierta:
            nivel_CO += 0.1
        else:
            nivel_CO -= 0.2

        nivel_CO = max(0, min(100, nivel_CO))

        # Fin de juego
        if nivel_CO >= 100:
            juego_activo = False
            mostrar_resumen = True
        if len(mensajes_vistos) == len(objetos) and nivel_CO < 30:
            juego_activo = False
            mostrar_resumen = True

        # --- DIBUJO ---
        intensidad = min(255, int(nivel_CO * 2.5))
        pantalla.fill((intensidad, intensidad//3, intensidad//3))
        pygame.draw.rect(pantalla, VERDE, jugador)

        for obj in objetos:
            pygame.draw.rect(pantalla, obj["color"], obj["rect"])

        # HUD
        texto_co = font.render(f"Nivel de CO: {int(nivel_CO)}", True, BLANCO)
        pantalla.blit(texto_co, (20, 20))
        instrucciones = font.render("Usá ← → para moverte. Presioná ESPACIO para interactuar.", True, BLANCO)
        pantalla.blit(instrucciones, (20, 60))

        # Burbujas de información
        if indice_mensaje is not None and time.time() - mensaje_tiempo < 5:
            burbuja_info(objetos[indice_mensaje]["texto"])

    else:
        if mostrar_resumen:
            resumen_final()
            if teclas[pygame.K_r]:
                # Reiniciar
                jugador.x = 100
                nivel_CO = 50
                mensajes_vistos.clear()
                ventana_abierta = False
                juego_activo = True
                mostrar_resumen = False
            elif teclas[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

    pygame.display.flip()
    clock.tick(60)
