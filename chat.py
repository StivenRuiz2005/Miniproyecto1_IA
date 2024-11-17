import tkinter as tk
from PIL import Image, ImageTk
from collections import deque
import time
import random
import heapq

class NodoArbol:
    def __init__(self, posicion, padre=None, costo=None, altura=None):
        self.posicion = posicion
        self.padre = padre
        self.costo = costo
        self.altura = altura  # Esto puede ser la heurística (en A*)
        self.hijos = []

    def __lt__(self, other):
        return self.costo < other.costo  # Esto es necesario para que heapq funcione correctamente

class Laberinto:
    def __init__(self, root, rows=8, cols=8):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_width = 50  # Ancho de cada celda
        self.cell_height = 40  # Alto de cada celda
        self.image_scale_factor = 0.93  # Factor de escala de la imagen
        self.nodo_padre_coords = {}
        self.hijos_contador = {}  # Contador de hijos por nodo

        self.maze = [[0 for _ in range(cols)] for _ in range(rows)]  
        self.raton_pos = (0, 0)  # Posición del ratón
        self.queso_pos = (6, 6)  # Posición del queso
        self.bloques_grises = [(1,1), (4,3), (2,1), (3,4),(7,2), (6,5),(4,2),(1,3),(1,1)]  # Paredes

        self.raton_image = self.cargar_imagenes(r"Images/Raton.png")
        self.queso_image = self.cargar_imagenes(r"Images/queso.png")

        self.iniciar_laberinto()
        self.dibujar_laberinto()
        self.crear_area_arbol()

        self.boton_iniciar = tk.Button(self.root, text="Iniciar", command=self.iniciar_busqueda)
        self.boton_iniciar.grid(row=1, column=0, pady=10)

        self.etiqueta_expansiones = tk.Label(self.root, text="Número de expansiones: ")
        self.etiqueta_expansiones.grid(row=2, column=0, pady=10)

        self.entry_expansiones = tk.Entry(self.root)
        self.entry_expansiones.grid(row=3, column=0, pady=10)

    def cargar_imagenes(self, path):
        adjusted_width = int(self.cell_width * self.image_scale_factor)
        adjusted_height = int(self.cell_height * self.image_scale_factor)
        image = Image.open(path).resize((adjusted_width, adjusted_height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def iniciar_laberinto(self):
        for bloque in self.bloques_grises:
            row, col = bloque
            self.maze[row][col] = 1  # Representa un bloque o pared

    def dibujar_laberinto(self):
        self.canvas = tk.Canvas(self.root, width=self.cols * self.cell_width, height=self.rows * self.cell_height)
        self.canvas.grid(row=0, column=0)

        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_width
                y1 = i * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                if self.maze[i][j] == 1:  
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="gray")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

        raton_x, raton_y = self.raton_pos
        raton_cx = raton_y * self.cell_width + (self.cell_width - self.raton_image.width()) // 2
        raton_cy = raton_x * self.cell_height + (self.cell_height - self.raton_image.height()) // 2
        self.canvas.create_image(raton_cx, raton_cy, anchor="nw", image=self.raton_image)

        queso_x, queso_y = self.queso_pos
        queso_cx = queso_y * self.cell_width + (self.cell_width - self.queso_image.width()) // 2
        queso_cy = queso_x * self.cell_height + (self.cell_height - self.queso_image.height()) // 2
        self.canvas.create_image(queso_cx, queso_cy, anchor="nw", image=self.queso_image)

    def crear_area_arbol(self):
        self.canvas_arbol = tk.Canvas(self.root, width=700, height=600, bg="white")
        self.canvas_arbol.grid(row=0, column=1, padx=20, pady=20)
        self.nodo_padre_coords = {}

    def iniciar_busqueda(self):
        try:
            n = int(self.entry_expansiones.get())  # Obtener el número de expansiones desde el Entry
        except ValueError:
            print("Por favor, ingrese un número entero válido para las expansiones.")
            return

        self.boton_iniciar.config(state=tk.DISABLED)  # Desactivar el botón para evitar múltiples búsquedas
        self.realizar_busqueda_hibrida(n)  # Comenzar la búsqueda híbrida con el número de expansiones

    def realizar_busqueda_hibrida(self, n):
        pila_dfs = []
        cola_bfs = deque()
        visitados = set([self.raton_pos])
        expansiones_totales = 0
        
        # Métodos disponibles para búsqueda
        metodos_disponibles = ["DFS", "BFS", "IDDFS", "UCS", "A*"]
        metodo_actual = random.choice(metodos_disponibles)
        metodos_disponibles.remove(metodo_actual)

        # Nodo inicial
        nodo_inicial = NodoArbol(self.raton_pos, costo=0)

        # Añadir el nodo inicial a la estructura de datos correspondiente
        if metodo_actual == "DFS":
            pila_dfs.append(nodo_inicial)
        elif metodo_actual == "BFS":
            cola_bfs.append(nodo_inicial)

        while True:
            # DFS
            if metodo_actual == "DFS":
                resultado, expansiones = self.busqueda_dfs(pila_dfs, visitados, n)
                expansiones_totales += expansiones
                if resultado:
                    return

                # Transferir nodos de DFS a BFS
                while pila_dfs:
                    cola_bfs.append(pila_dfs.pop())

            # BFS
            elif metodo_actual == "BFS":
                resultado, expansiones = self.busqueda_bfs(cola_bfs, visitados, n)
                expansiones_totales += expansiones
                if resultado:
                    return

                # Transferir nodos de BFS a DFS
                while cola_bfs:
                    pila_dfs.append(cola_bfs.popleft())

            # IDDFS
            elif metodo_actual == "IDDFS":
                resultado, expansiones = self.busqueda_iddfs(n, n)
                if resultado:
                    return

            # UCS
            elif metodo_actual == "UCS":
                resultado, expansiones = self.busqueda_costo_uniforme()
                if resultado:
                    return

            # A*
            elif metodo_actual == "A*":
                resultado, expansiones = self.busqueda_a_star()
                if resultado:
                    return

            # Si no quedan más métodos
            if not metodos_disponibles:
                print(f"Expansiones totales: {expansiones_totales}")
                print("No se encontró el queso después de probar todos los métodos.")
                break

            # Elegir el siguiente método
            metodo_actual = random.choice(metodos_disponibles)
            metodos_disponibles.remove(metodo_actual)

    def busqueda_dfs(self, pila_dfs, visitados, max_expansiones):
        expansiones = 0
        while pila_dfs:
            print("Using DFS")
            nodo_actual = pila_dfs.pop()
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con DFS!")
                return True, expansiones

            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    pila_dfs.append(nuevo_nodo)
                    visitados.add(nueva_posicion)
            
            expansiones += 1
            if expansiones >= max_expansiones:
                break

        return False, expansiones

    def busqueda_bfs(self, cola_bfs, visitados, max_expansiones):
        expansiones = 0
        while cola_bfs:
            print("Using BFS")
            nodo_actual = cola_bfs.popleft()
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con BFS!")
                return True, expansiones

            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    cola_bfs.append(nuevo_nodo)
                    visitados.add(nueva_posicion)

            expansiones += 1
            if expansiones >= max_expansiones:
                break

        return False, expansiones

    def busqueda_iddfs(self, limite, max_expansiones):
        for profundidad in range(limite):
            visitados = set()
            print(f"Buscando con IDDFS hasta profundidad {profundidad}")
            resultado, expansiones = self.busqueda_dfs([NodoArbol(self.raton_pos)], visitados, max_expansiones)
            if resultado:
                return True, expansiones
        return False, max_expansiones

    def busqueda_costo_uniforme(self):
        print("Buscando con UCS...")
        cola_ucs = []
        heapq.heappush(cola_ucs, NodoArbol(self.raton_pos, costo=0))
        visitados = set()
        expansiones = 0

        while cola_ucs:
            nodo_actual = heapq.heappop(cola_ucs)
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con UCS!")
                return True, expansiones

            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):

                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual, costo=nodo_actual.costo + 1)
                    heapq.heappush(cola_ucs, nuevo_nodo)
                    visitados.add(nueva_posicion)

            expansiones += 1
            if expansiones >= 100:
                break

        return False, expansiones

    def busqueda_a_star(self):
        print("Buscando con A*...")
        cola_a_star = []
        heuristica = lambda pos: abs(pos[0] - self.queso_pos[0]) + abs(pos[1] - self.queso_pos[1])
        heapq.heappush(cola_a_star, NodoArbol(self.raton_pos, costo=0, altura=heuristica(self.raton_pos)))
        visitados = set()
        expansiones = 0

        while cola_a_star:
            nodo_actual = heapq.heappop(cola_a_star)
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con A*!")
                return True, expansiones

            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):

                    costo = nodo_actual.costo + 1
                    h = heuristica(nueva_posicion)
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual, costo=costo, altura=h)
                    heapq.heappush(cola_a_star, nuevo_nodo)
                    visitados.add(nueva_posicion)

            expansiones += 1
            if expansiones >= 100:
                break

        return False, expansiones


if __name__ == "__main__":
    root = tk.Tk()
    laberinto = Laberinto(root)
    root.mainloop()
