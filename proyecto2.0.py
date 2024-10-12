import tkinter as tk
from PIL import Image, ImageTk
from collections import deque
import time
import random
import heapq


class NodoArbol:
    def __init__(self, posicion, padre=None, costo=0):
        self.posicion = posicion
        self.padre = padre
        self.hijos = []
        self.costo = costo  # Para búsquedas que usan costo


class Laberinto:
    def __init__(self, root, rows=4, cols=4, expansiones_por_actualizacion=2):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_width = 100  # Ancho de cada celda
        self.cell_height = 80  # Alto de cada celda
        self.image_scale_factor = 0.93  # Escalar la imagen al 93% del tamaño de la celda
        self.expansiones_por_actualizacion = expansiones_por_actualizacion

        self.maze = [[0 for _ in range(cols)] for _ in range(rows)]  # Matriz del laberinto
        
        # Posiciones iniciales definidas por el usuario
        self.raton_pos = (2, 0)  # Posición del ratón
        self.queso_pos = (1, 3)  # Posición del queso
        self.bloques_grises = [(2, 1), (1, 1), (1, 2), (3, 3)]  # Paredes/bloques grises

        # Cargar imágenes
        self.raton_image = self.cargar_imagenes(r"Images/Raton.png")
        self.queso_image = self.cargar_imagenes(r"Images/queso.png")

        self.iniciar_laberinto()

        # Dibujar laberinto y el área del árbol
        self.dibujar_laberinto()
        self.crear_area_arbol()

        # Crear botón Iniciar y label para estrategia
        self.boton_iniciar = tk.Button(self.root, text="Iniciar", command=self.iniciar_busqueda)
        self.boton_iniciar.grid(row=1, column=0, pady=10)
        
        self.label_estrategia = tk.Label(self.root, text="Estrategia: ", font=("Arial", 12))
        self.label_estrategia.grid(row=2, column=0)

        self.estrategias = ["Búsqueda por amplitud", "Búsqueda preferente por profundidad", 
                            "Búsqueda por costo uniforme", "Búsqueda limitada por profundidad",
                            "Búsqueda por profundización iterativa", "Búsqueda avara"]
        self.estrategias_utilizadas = []  # Para evitar repetir estrategias

    def cargar_imagenes(self, path):
        """Carga y ajusta el tamaño de la imagen según las dimensiones de las celdas, respetando los bordes"""
        adjusted_width = int(self.cell_width * self.image_scale_factor)
        adjusted_height = int(self.cell_height * self.image_scale_factor)
        image = Image.open(path).resize((adjusted_width, adjusted_height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def iniciar_laberinto(self):
        # Colocar las paredes (bloques grises)
        for bloque in self.bloques_grises:
            row, col = bloque
            self.maze[row][col] = 1  # 1 representa un bloque gris

    def dibujar_laberinto(self):
        # Canvas para el laberinto
        self.canvas = tk.Canvas(self.root, width=self.cols * self.cell_width, height=self.rows * self.cell_height)
        self.canvas.grid(row=0, column=0)

        # Dibujar las celdas del laberinto
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_width
                y1 = i * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height

                # Dibujar bloques grises o celdas blancas
                if self.maze[i][j] == 1:  # Bloques grises
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="gray")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

        # Calcular posición centrada del ratón
        raton_x, raton_y = self.raton_pos
        raton_cx = raton_y * self.cell_width + (self.cell_width - self.raton_image.width()) // 2
        raton_cy = raton_x * self.cell_height + (self.cell_height - self.raton_image.height()) // 2
        self.canvas.create_image(raton_cx, raton_cy, anchor="nw", image=self.raton_image)

        # Calcular posición centrada del queso
        queso_x, queso_y = self.queso_pos
        queso_cx = queso_y * self.cell_width + (self.cell_width - self.queso_image.width()) // 2
        queso_cy = queso_x * self.cell_height + (self.cell_height - self.queso_image.height()) // 2
        self.canvas.create_image(queso_cx, queso_cy, anchor="nw", image=self.queso_image)

    def crear_area_arbol(self):
        """Crea un canvas donde se visualiza la construcción del árbol"""
        self.canvas_arbol = tk.Canvas(self.root, width=400, height=400, bg="white")
        self.canvas_arbol.grid(row=0, column=1, padx=20, pady=20)
        self.nodo_padre_coords = {}  # Almacena las posiciones (x, y) de los nodos ya dibujados en el árbol

    def iniciar_busqueda(self):
        """Función que se llama cuando se presiona el botón Iniciar"""
        self.boton_iniciar.config(state=tk.DISABLED)  # Desactivar el botón para evitar múltiples búsquedas
        self.seleccionar_estrategia()  # Comenzar seleccionando una estrategia

    def seleccionar_estrategia(self):
        """Selecciona una estrategia al azar, pero sin repetir"""
        if len(self.estrategias_utilizadas) == len(self.estrategias):
            print("Se han usado todas las estrategias, finalizando.")
            return

        # Selecciona una estrategia no utilizada
        estrategia = random.choice([e for e in self.estrategias if e not in self.estrategias_utilizadas])
        self.estrategias_utilizadas.append(estrategia)

        # Muestra la estrategia seleccionada en la interfaz
        self.label_estrategia.config(text=f"Estrategia: {estrategia}")

        # Asignar la estrategia correspondiente
        if estrategia == "Búsqueda por amplitud":
            self.realizar_bfs()
        elif estrategia == "Búsqueda preferente por profundidad":
            self.realizar_dfs()
        elif estrategia == "Búsqueda por costo uniforme":
            self.realizar_costo_uniforme()
        elif estrategia == "Búsqueda limitada por profundidad":
            self.realizar_dfs_limitada(3)  # Ejemplo: límite de 3 niveles
        elif estrategia == "Búsqueda por profundización iterativa":
            self.realizar_profundizacion_iterativa()
        elif estrategia == "Búsqueda avara":
            self.realizar_busqueda_avara()

    def realizar_bfs(self):
        """Realiza la búsqueda por amplitud (BFS) y expande nodo por nodo"""
        cola = deque([NodoArbol(self.raton_pos)])
        visitados = set([self.raton_pos])
        expansiones = 0

        while cola:
            nodo_actual = cola.popleft()
            posicion_actual = nodo_actual.posicion

            # Si el ratón encuentra el queso
            if posicion_actual == self.queso_pos:
                print("Queso encontrado!")
                self.mostrar_camino(nodo_actual)
                return

            # Expande los vecinos (arriba, abajo, izquierda, derecha)
            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                # Verifica si la nueva posición es válida (dentro de los límites, no visitada y no es un bloque gris)
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nodo_actual.hijos.append(nuevo_nodo)
                    cola.append(nuevo_nodo)
                    visitados.add(nueva_posicion)

                    expansiones += 1

                    # Dibuja el nodo en el laberinto y en el árbol
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    
                    # Actualiza la interfaz y pausa brevemente para visualizar la expansión paso a paso
                    self.root.update()
                    time.sleep(0.5)  # Pausa de medio segundo para visualizar el proceso

                    # Cambia de estrategia cada n expansiones
                    if expansiones % self.expansiones_por_actualizacion == 0:
                        self.seleccionar_estrategia()
                        return

        print("No se encontró el queso.")

    def realizar_dfs(self):
        """Realiza la búsqueda preferente por profundidad (DFS)"""
        pila = [NodoArbol(self.raton_pos)]
        visitados = set([self.raton_pos])
        expansiones = 0

        while pila:
            nodo_actual = pila.pop()
            posicion_actual = nodo_actual.posicion

            # Si el ratón encuentra el queso
            if posicion_actual == self.queso_pos:
                print("Queso encontrado!")
                self.mostrar_camino(nodo_actual)
                return

            # Expande los vecinos (arriba, abajo, izquierda, derecha)
            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                # Verifica si la nueva posición es válida (dentro de los límites, no visitada y no es un bloque gris)
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nodo_actual.hijos.append(nuevo_nodo)
                    pila.append(nuevo_nodo)
                    visitados.add(nueva_posicion)

                    expansiones += 1

                    # Dibuja el nodo en el laberinto y en el árbol
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    
                    # Actualiza la interfaz y pausa brevemente para visualizar la expansión paso a paso
                    self.root.update()
                    time.sleep(0.5)  # Pausa de medio segundo para visualizar el proceso

                    # Cambia de estrategia cada n expansiones
                    if expansiones % self.expansiones_por_actualizacion == 0:
                        self.seleccionar_estrategia()
                        return

        print("No se encontró el queso.")

    def realizar_costo_uniforme(self):
        """Realiza la búsqueda por costo uniforme (Uniform Cost Search)"""
        cola_prioridad = []
        heapq.heappush(cola_prioridad, (0, NodoArbol(self.raton_pos)))  # (costo, nodo)
        visitados = set([self.raton_pos])
        expansiones = 0

        while cola_prioridad:
            costo_actual, nodo_actual = heapq.heappop(cola_prioridad)
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("Queso encontrado!")
                self.mostrar_camino(nodo_actual)
                return

            # Expande los vecinos (arriba, abajo, izquierda, derecha)
            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual, costo=costo_actual + 1)
                    nodo_actual.hijos.append(nuevo_nodo)
                    heapq.heappush(cola_prioridad, (costo_actual + 1, nuevo_nodo))
                    visitados.add(nueva_posicion)

                    expansiones += 1

                    # Dibuja el nodo en el laberinto y en el árbol
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    
                    self.root.update()
                    time.sleep(0.5)

                    if expansiones % self.expansiones_por_actualizacion == 0:
                        self.seleccionar_estrategia()
                        return

    def realizar_dfs_limitada(self, limite):
        """Realiza la búsqueda limitada por profundidad"""
        pila = [(NodoArbol(self.raton_pos), 0)]  # (nodo, profundidad)
        visitados = set([self.raton_pos])
        expansiones = 0

        while pila:
            nodo_actual, profundidad = pila.pop()
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("Queso encontrado!")
                self.mostrar_camino(nodo_actual)
                return

            if profundidad < limite:
                for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                    if (0 <= nueva_posicion[0] < self.rows and
                        0 <= nueva_posicion[1] < self.cols and
                        self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                        nueva_posicion not in visitados):
                        
                        nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                        nodo_actual.hijos.append(nuevo_nodo)
                        pila.append((nuevo_nodo, profundidad + 1))
                        visitados.add(nueva_posicion)

                        expansiones += 1

                        # Dibuja el nodo en el laberinto y en el árbol
                        self.dibujar_nodo_lab(nueva_posicion)
                        self.dibujar_arbol(nodo_actual, nuevo_nodo)
                        
                        self.root.update()
                        time.sleep(0.5)

                        if expansiones % self.expansiones_por_actualizacion == 0:
                            self.seleccionar_estrategia()
                            return

    def realizar_profundizacion_iterativa(self):
        """Realiza la búsqueda por profundización iterativa"""
        for limite in range(1, 10):  # Por ejemplo, iteramos con profundidades de 1 a 10
            print(f"Profundidad actual: {limite}")
            self.realizar_dfs_limitada(limite)
            time.sleep(0.5)

    def heuristica(self, posicion):
        """Heurística: distancia Manhattan al queso"""
        return abs(posicion[0] - self.queso_pos[0]) + abs(posicion[1] - self.queso_pos[1])

    def realizar_busqueda_avara(self):
        """Realiza la búsqueda avara (greedy search)"""
        cola_prioridad = []
        heapq.heappush(cola_prioridad, (self.heuristica(self.raton_pos), NodoArbol(self.raton_pos)))
        visitados = set([self.raton_pos])
        expansiones = 0

        while cola_prioridad:
            heuristica_actual, nodo_actual = heapq.heappop(cola_prioridad)
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("Queso encontrado!")
                self.mostrar_camino(nodo_actual)
                return

            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nodo_actual.hijos.append(nuevo_nodo)
                    heapq.heappush(cola_prioridad, (self.heuristica(nueva_posicion), nuevo_nodo))
                    visitados.add(nueva_posicion)

                    expansiones += 1

                    # Dibuja el nodo en el laberinto y en el árbol
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    
                    self.root.update()
                    time.sleep(0.5)

                    if expansiones % self.expansiones_por_actualizacion == 0:
                        self.seleccionar_estrategia()
                        return

    def dibujar_nodo_lab(self, posicion):
        """Dibuja el nodo expandido en el laberinto"""
        x1 = posicion[1] * self.cell_width
        y1 = posicion[0] * self.cell_height
        x2 = x1 + self.cell_width
        y2 = y1 + self.cell_height
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black")

    def dibujar_arbol(self, nodo_padre, nodo_hijo):
        """Dibuja el árbol de búsqueda expandido"""
        if nodo_padre not in self.nodo_padre_coords:
            self.nodo_padre_coords[nodo_padre] = (200, 20)  # Posición inicial del nodo raíz
            self.canvas_arbol.create_oval(195, 15, 205, 25, fill="blue")  # Nodo raíz

        # Coordenadas del nodo padre
        x_padre, y_padre = self.nodo_padre_coords[nodo_padre]
        # Calcula nuevas coordenadas del hijo (un poco hacia abajo y hacia los lados)
        x_hijo = x_padre + len(nodo_padre.hijos) * 50 - 25
        y_hijo = y_padre + 50

        # Dibuja línea entre el padre y el hijo
        self.canvas_arbol.create_line(x_padre, y_padre, x_hijo, y_hijo, fill="black")
        # Dibuja el nodo hijo
        self.canvas_arbol.create_oval(x_hijo - 5, y_hijo - 5, x_hijo + 5, y_hijo + 5, fill="blue")

        # Guarda las coordenadas del hijo para futuras expansiones
        self.nodo_padre_coords[nodo_hijo] = (x_hijo, y_hijo)

    def mostrar_camino(self, nodo):
        """Muestra el camino final desde el ratón hasta el queso"""
        while nodo:
            self.dibujar_nodo_lab(nodo.posicion)
            nodo = nodo.padre
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Laberinto - Búsqueda por Amplitud (BFS)")
    app = Laberinto(root, expansiones_por_actualizacion=2)
    root.mainloop()