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
        self.hijos = []
        self.costos = costo
        self.altura = altura
        
        
class Laberinto:
    def __init__(self, root, rows=4, cols=4, expansiones_por_actualizacion=2):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_width = 100  # aqui acomoda el Ancho de cada celda
        self.cell_height = 80  # lo mismo Alto de cada celda
        self.image_scale_factor = 0.93  # esta mkd es para que la imagen no tape los bordes de las celdas, se escala un poco menos al 93
        self.expansiones_por_actualizacion = expansiones_por_actualizacion
        self.nodo_padre_coords = {}
        self.hijos_contador = {}  # Agregar un contador de hijos por nodo

        self.maze = [[0 for _ in range(cols)] for _ in range(rows)]  
        
        
        self.raton_pos = (1, 0)  # aqui define la Posición del ratón
        self.queso_pos = (1, 2)  # lo mismo con la Posición del queso
        self.bloques_grises = [(1,1), (3,2), (3,3), (2,1)]  # aqui ubica las Paredes/bloques grises donde le de la gana

        
        self.raton_image = self.cargar_imagenes(r"Images/Raton.png")#no se le olvide combiar la ruta de las imagenes o paila no se ejecuta esta monda
        self.queso_image = self.cargar_imagenes(r"Images/queso.png")

        self.iniciar_laberinto()

    
        self.dibujar_laberinto()
        self.crear_area_arbol()

        
        self.boton_iniciar = tk.Button(self.root, text="Iniciar", command=self.iniciar_busqueda)
        self.boton_iniciar.grid(row=1, column=0, pady=10)

    def cargar_imagenes(self, path):
        adjusted_width = int(self.cell_width * self.image_scale_factor)
        adjusted_height = int(self.cell_height * self.image_scale_factor)
        image = Image.open(path).resize((adjusted_width, adjusted_height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def iniciar_laberinto(self):
        for bloque in self.bloques_grises:
            row, col = bloque
            self.maze[row][col] = 1  # esto representa un bloque o pared

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
        self.boton_iniciar.config(state=tk.DISABLED)  # Desactivar el botón para evitar múltiples búsquedas
        self.realizar_busqueda_hibrida()  # Comenzar la búsqueda por amplitud la unica que tengo daa

    def solicitar_limite_expansiones(self, tipo_busqueda):
        try:
            n = int(input(f"Ingrese el límite de expansiones para la búsqueda {tipo_busqueda}: "))
            return n
        except ValueError:
            print("Por favor, ingrese un número entero.")
            return self.solicitar_limite_expansiones(tipo_busqueda)

    ##TODO:  Busqueda por amplitud y profundidad hibrida, ejecutar cambios

    def realizar_busqueda_hibrida(self):
        pila_dfs = [NodoArbol(self.raton_pos)]
        cola_bfs = deque()
        visitados = set([self.raton_pos])
        expansiones_totales = 0
        
        # Banderas para alternar entre las estrategias de búsqueda
        usando_dfs = True
        usando_bfs = False
        usando_iterativa = False
        usando_costo_uniforme = False
        
        # Variables para indicar si cada búsqueda ya fue aplicada
        dfs_aplicada = False
        bfs_aplicada = False
        iterativa_aplicada = False
        costo_uniforme_aplicada = False

        while True:
            # Búsqueda en profundidad
            if usando_dfs and not dfs_aplicada:
                max_expansiones = self.solicitar_limite_expansiones("DFS")
                resultado, expansiones = self.busqueda_dfs(pila_dfs, visitados, max_expansiones)
                expansiones_totales += expansiones
                if resultado:
                    return
                dfs_aplicada = True
                usando_dfs = False
                usando_bfs = True

                # Transfer nodes from DFS stack to BFS queue
                while pila_dfs:
                    cola_bfs.append(pila_dfs.pop())

            # Búsqueda en amplitud
            elif usando_bfs and not bfs_aplicada:
                max_expansiones = self.solicitar_limite_expansiones("BFS")
                resultado, expansiones = self.busqueda_bfs(cola_bfs, visitados, max_expansiones)
                expansiones_totales += expansiones
                if resultado:
                    return
                bfs_aplicada = True
                usando_bfs = False
                usando_iterativa = True

            # Búsqueda en profundidad iterativa
            elif usando_iterativa and not iterativa_aplicada:
                profundidad_max_inicial = self.solicitar_limite_expansiones("IDDFS")
                resultado = self.busqueda_iddfs(profundidad_max_inicial)
                if resultado:
                    return
                iterativa_aplicada = True
                usando_iterativa = False
                usando_costo_uniforme = True

            # Búsqueda por costo uniforme
            elif usando_costo_uniforme and not costo_uniforme_aplicada:
                print("Iniciando búsqueda por costo uniforme...")
                resultado, expansiones = self.busqueda_costo_uniforme()
                expansiones_totales += expansiones
                if resultado:
                    return
                costo_uniforme_aplicada = True
                usando_costo_uniforme = False

            # Si todas las búsquedas fallan, terminamos
            else:
                print(f"Expansiones totales: {expansiones_totales}")
                print("No se encontró el queso después de probar todas las búsquedas.")
                break
    def busqueda_dfs(self, pila_dfs, visitados, max_expansiones):
        expansiones = 0
        while pila_dfs:
            print("Using DFS")
            nodo_actual = pila_dfs.pop()
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con DFS!")
                return True, expansiones

            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nodo_actual.hijos.append(nuevo_nodo)
                    pila_dfs.append(nuevo_nodo)
                    visitados.add(nueva_posicion)
                    expansiones += 1

                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

                    if expansiones >= max_expansiones:
                        print(f"Límite de expansiones alcanzado en DFS ({expansiones})")
                        return False, expansiones

        print("No quedan nodos en la pila de DFS.")
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

            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nodo_actual.hijos.append(nuevo_nodo)
                    cola_bfs.append(nuevo_nodo)
                    visitados.add(nueva_posicion)
                    expansiones += 1

                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

                    if expansiones >= max_expansiones:
                        print(f"Límite de expansiones alcanzado en BFS ({expansiones})")
                        return False, expansiones

        # Asegurar retorno de False y el número de expansiones si no se encuentra el queso
        print("No quedan nodos en la cola de BFS.")
        return False, expansiones

    def busqueda_iddfs(self, profundidad_max_inicial):
        profundidad_max = profundidad_max_inicial
        while True:
            encontrado = self.busqueda_dfs_limitada(profundidad_max)
            if encontrado:
                return True
            profundidad_max += 1
            print(f"Aumentando la profundidad a {profundidad_max}.")


    def busqueda_dfs_limitada(self, profundidad_max):
        pila_dfs = [(NodoArbol(self.raton_pos), 0)]  # La pila contendrá el nodo y la profundidad
        visitados = set([self.raton_pos])

        while pila_dfs:
            nodo_actual, profundidad = pila_dfs.pop()
            posicion_actual = nodo_actual.posicion

            # Si encuentra el queso, retorna éxito
            if posicion_actual == self.queso_pos:
                print(f"¡Queso encontrado con DFS limitada a profundidad {profundidad_max}!")
                self.mostrar_camino(nodo_actual)  # Mostrar el camino si es necesario
                return True

            # Solo seguir expandiendo si no hemos alcanzado la profundidad máxima
            if profundidad < profundidad_max:
                for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                    # Verificar si la nueva posición es válida y no ha sido visitada
                    if (0 <= nueva_posicion[0] < self.rows and
                        0 <= nueva_posicion[1] < self.cols and
                        self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                        nueva_posicion not in visitados):

                        nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                        nodo_actual.hijos.append(nuevo_nodo)
                        pila_dfs.append((nuevo_nodo, profundidad + 1))  # Añadir a la pila con la nueva profundidad
                        visitados.add(nueva_posicion)

                        # Dibujar el nodo en el laberinto y el árbol
                        self.dibujar_nodo_lab(nueva_posicion)
                        self.dibujar_arbol(nodo_actual, nuevo_nodo)
                        self.root.update()
                        time.sleep(0.5)

        # Si la búsqueda DFS limitada no encuentra el queso, retornar False
        return False
        
        
    def busqueda_costo_uniforme(self):
        cola_prioridad = [(0, NodoArbol(self.raton_pos))]
        visitados = {self.raton_pos: 0}
        expansiones = 0

        while cola_prioridad:
            costo_acumulado, nodo_actual = heapq.heappop(cola_prioridad)
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print(f"¡Queso encontrado con búsqueda de costo uniforme! Costo total: {costo_acumulado}")
                self.mostrar_camino(nodo_actual)
                return True, expansiones

            for movimiento, costo in [((0, 1), 1), ((1, 0), 1), ((0, -1), 1), ((-1, 0), 1)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                nuevo_costo = costo_acumulado + costo

                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    (nueva_posicion not in visitados or nuevo_costo < visitados[nueva_posicion])):

                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nodo_actual.hijos.append(nuevo_nodo)
                    visitados[nueva_posicion] = nuevo_costo
                    heapq.heappush(cola_prioridad, (nuevo_costo, nuevo_nodo))
                    expansiones += 1

                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

        print("No se encontró el queso con la búsqueda de costo uniforme.")
        return False, expansiones

   
    def dibujar_nodo_lab(self, posicion):
        time.sleep(0.4)
        x1 = posicion[1] * self.cell_width
        y1 = posicion[0] * self.cell_height
        x2 = x1 + self.cell_width
        y2 = y1 + self.cell_height
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black")

    def dibujar_arbol(self, nodo_padre, nodo_hijo):
        # Obtener el tamaño del canvas para centrar la raíz
        canvas_ancho = self.canvas_arbol.winfo_width()

        # Inicializar el contador de hijos para el nodo padre si no existe
        if nodo_padre not in self.hijos_contador:
            self.hijos_contador[nodo_padre] = 0  # Contador de hijos para el nodo padre

        # Si el nodo hijo ya ha sido agregado, no hacer nada (evitar duplicados)
        if nodo_hijo in self.nodo_padre_coords:
            print(f"El nodo {nodo_hijo} ya existe. Evitando duplicado.")
            return

        # Si es la raíz, centrarla en el canvas
        if nodo_padre not in self.nodo_padre_coords:
            x_centro = canvas_ancho // 2  # Centrar la raíz
            self.nodo_padre_coords[nodo_padre] = (x_centro, 20)  # Coordenadas iniciales centradas
            self.canvas_arbol.create_oval(x_centro - 5, 15, x_centro + 5, 25, fill="blue")  # Dibujar la raíz

        # Obtener coordenadas del nodo padre
        x_padre, y_padre = self.nodo_padre_coords[nodo_padre]

        # Verificar si el nodo padre es la raíz (no tiene padre)
        es_raiz = nodo_padre.padre is None

        # Calcular la posición del nuevo hijo
        if es_raiz and self.hijos_contador[nodo_padre] < 2:
            x_hijo = x_padre + (self.hijos_contador[nodo_padre] * 160) - 80
        else:
            num_hijos = len(nodo_padre.hijos)
            x_hijo = x_padre + (self.hijos_contador[nodo_padre] - num_hijos / 2) * 60

        y_hijo = y_padre + 80  # Aumento en altura para el hijo

        # Dibujar la línea entre el nodo padre y el hijo
        self.canvas_arbol.create_line(x_padre, y_padre, x_hijo, y_hijo, fill="black")

        # Dibujar el nodo hijo
        self.canvas_arbol.create_oval(x_hijo - 5, y_hijo - 5, x_hijo + 5, y_hijo + 5, fill="blue")

        # Almacenar las coordenadas del nuevo nodo hijo
        self.nodo_padre_coords[nodo_hijo] = (x_hijo, y_hijo)

        # Incrementar el contador de hijos para el nodo padre
        self.hijos_contador[nodo_padre] += 1


    def mostrar_camino(self, nodo):
        while nodo:
            self.dibujar_nodo_lab(nodo.posicion)
            nodo = nodo.padre
        self.root.update() 


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Laberinto - Búsqueda por Amplitud")
    app = Laberinto(root, expansiones_por_actualizacion=2)
    root.mainloop()
