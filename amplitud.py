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
        self.left_value = 0  # Initialize default value
        
        # Calculate cumulative left_value from the root to this node
        if padre is not None:
            parent_x = padre.posicion[1]
            current_x = posicion[1]
            # If this node is to the right of its parent
            if current_x > parent_x:
                self.left_value = padre.left_value + 1
            # If this node is to the left of its parent
            elif current_x < parent_x:
                self.left_value = padre.left_value - 1
            # If same x position
            else:
                self.left_value = padre.left_value
            # Accumulate the left_value from the parent
            self.left_value += padre.left_value

    
class Laberinto:
    def __init__(self, root, rows=8, cols=8, expansiones_por_actualizacion=2):
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
        
        
        self.raton_pos = (1, 5)  # aqui define la Posición del ratón
        self.queso_pos = (6, 6)  # lo mismo con la Posición del queso
        self.bloques_grises = [(1,1), (4,3), (2,1), (3,4),(7,2), (6,5),(4,2),(1,3),(1,1)]  # aqui ubica las Paredes/bloques grises donde le de la gana

        
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


    def realizar_busqueda_hibrida(self):
        pila_dfs = []
        cola_bfs = deque()
        visitados = set([self.raton_pos])
        expansiones_totales = 0
        
        # List of available search methods

        metodos_disponibles = ["DFSLI"]  #uqsar el metodo que deseo para realizar la prueba 
        metodo_actual = random.choice(metodos_disponibles)
        metodos_disponibles.remove(metodo_actual)

        # Initialize the starting node
        nodo_inicial = NodoArbol(self.raton_pos)

        # Add the initial node to the appropriate data structure
        if metodo_actual == "DFS":
            pila_dfs.append(nodo_inicial)
        elif metodo_actual == "BFS":
            cola_bfs.append((nodo_inicial, 0))  # Add a tuple with the node and its order

        order_counter = 1  # Initialize order counter

        while True:
            # Búsqueda en profundidad
            if metodo_actual == "DFS":
                max_expansiones = self.solicitar_limite_expansiones("DFS")
                resultado, expansiones = self.busqueda_dfs(pila_dfs, visitados, max_expansiones)
                expansiones_totales += expansiones
                if resultado:
                    return

                # Transfer nodes from DFS to BFS
                while pila_dfs:
                    cola_bfs.append((pila_dfs.pop(), order_counter))
                    order_counter += 1

            # Búsqueda en amplitud
            elif metodo_actual == "BFS":
                max_expansiones = self.solicitar_limite_expansiones("BFS")
                resultado, expansiones = self.busqueda_bfs(cola_bfs, visitados, max_expansiones)
                expansiones_totales += expansiones
                if resultado:
                    return


                # Transfer remaining nodes from BFS queue to DFS stack
                while cola_bfs:
                    pila_dfs.append(cola_bfs.popleft())

            # Búsqueda en profundidad iterativa
            elif metodo_actual == "IDDFS":
                profundidad_max_inicial = self.solicitar_limite_expansiones("IDDFS")
                max_expansiones = profundidad_max_inicial
                resultado = self.busqueda_iddfs(profundidad_max_inicial, max_expansiones)
                if resultado:
                    return
                
            # Búsqueda en profundidad limitada
            elif metodo_actual == "DFSLI":
                profundidad_max = self.solicitar_limite_expansiones("DFSLI")
                
                resultado = self.busqueda_dfs_limitada(profundidad_max)
                if resultado:
                    return
            
                

                # Sort remaining nodes by cumulative left_value and order before transferring to DFS
                sorted_nodes = sorted(cola_bfs, key=lambda item: (self.calculate_cumulative_left_value(item[0]), item[1]))
                pila_dfs.extend(node for node, _ in sorted_nodes)
                cola_bfs.clear()


            # Check if there are any methods left to apply
            if not metodos_disponibles:
                print(f"Expansiones totales: {expansiones_totales}")
                print("No se encontró el queso después de probar todas las búsquedas.")
                break

            # Select the next method randomly from the remaining methods
            metodo_actual = random.choice(metodos_disponibles)
            metodos_disponibles.remove(metodo_actual)

    def calculate_cumulative_left_value(self, nodo):
        cumulative_value = 0
        current = nodo
        while current:
            cumulative_value += current.left_value
            current = current.padre
        return cumulative_value
    def calculate_cumulative_left_value(self, nodo):
        cumulative_value = 0
        current = nodo
        while current:
            cumulative_value += current.left_value
            current = current.padre
        return cumulative_value
    
    def busqueda_dfs(self, pila_dfs, visitados, max_expansiones):
        expansiones = 0
        while pila_dfs:
            # Find the node with the lowest cumulative left_value sum
            min_cumulative_value = float('inf')
            min_index = 0
            for i, nodo in enumerate(pila_dfs):
                # Calculate cumulative left_value sum
                cumulative_value = self.calculate_cumulative_left_value(nodo)

                if cumulative_value < min_cumulative_value:
                    min_cumulative_value = cumulative_value
                    min_index = i
            
            # Remove and process the node with the lowest cumulative left_value sum
            nodo_actual = pila_dfs.pop(min_index)
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con DFS!")
                return True, expansiones

            # Process movements
            for movimiento in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
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

        return False, expansiones
    def busqueda_bfs(self, cola_bfs, visitados, max_expansiones):
        expansiones = 0
        while cola_bfs:
            # Unpack the node and its order from the queue
            nodo_actual, _ = cola_bfs.popleft()
            posicion_actual = nodo_actual.posicion

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con BFS!")
                return True, expansiones

            # Process movements in the order: Left, Up, Right, Down
            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    
                    # Calculate left_value based on the parent's position
                    parent_x = nodo_actual.posicion[1]
                    current_x = nueva_posicion[1]
                    if current_x > parent_x:
                        nuevo_nodo.left_value = nodo_actual.left_value + 1
                    elif current_x < parent_x:
                        nuevo_nodo.left_value = nodo_actual.left_value - 1
                    else:
                        nuevo_nodo.left_value = nodo_actual.left_value

                    nodo_actual.hijos.append(nuevo_nodo)
                    cola_bfs.append((nuevo_nodo, _))  # Keep track of the order
                    visitados.add(nueva_posicion)
                    expansiones += 1

                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

                    if expansiones >= max_expansiones:
                        print(f"Límite de expansiones alcanzado en BFS ({expansiones})")
                        return False, expansiones

        print("No quedan nodos en la cola de BFS.")
        return False, expansiones
    
    def busqueda_iddfs(self, profundidad_max_inicial, max_expansiones):
        profundidad_max = profundidad_max_inicial
        expansiones_totales = 0

        while profundidad_max <= max_expansiones:
            encontrado = self.busqueda_dfs_limitada(profundidad_max)
            if encontrado:
                return True
            profundidad_max += 1
            expansiones_totales += 1
            print(f"Aumentando la profundidad a {profundidad_max}.")

        print("Se alcanzó el límite máximo de expansiones para IDDFS.")
        return False

    def busqueda_dfs_limitada(self, profundidad_max):

        # Solicitar el límite de profundidad
        try:
            limite_profu = int(input("Ingrese el límite de profundidad deseado: "))
        except ValueError:
            print("Por favor, ingrese un número entero.")
            return self.busqueda_dfs_limitada()


        pila_dfs = [(NodoArbol(self.raton_pos), 0)]  # La pila contendrá el nodo y la profundidad
        visitados = set([self.raton_pos])
        expansiones_realizadas = 0  # Contador de expansiones


        while pila_dfs:
            nodo_actual, profundidad = pila_dfs.pop()
            posicion_actual = nodo_actual.posicion

            # Si encuentra el queso, retorna éxito
            if posicion_actual == self.queso_pos:
                print(f"¡Queso encontrado con DFS limitada a profundidad {profundidad_max}!")
                self.mostrar_camino(nodo_actual)  # Mostrar el camino si es necesario
                return True

            # Solo seguir expandiendo si no hemos alcanzado la profundidad máxima
            if profundidad < limite_profu and expansiones_realizadas < profundidad_max:
                for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                    # Verificar si la nueva posición es válida
                    if (0 <= nueva_posicion[0] < self.rows and
                        0 <= nueva_posicion[1] < self.cols and
                        self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0
                        and nueva_posicion not in visitados):

                        # Crear un nuevo nodo y añadirlo a la pila
                        nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                        nodo_actual.hijos.append(nuevo_nodo)
                        pila_dfs.append((nuevo_nodo, profundidad + 1))  # Añadir a la pila con la nueva profundidad
                        visitados.add(nueva_posicion)

                        # Contar la expansión realizada
                        expansiones_realizadas += 1

                        # Dibujar el nodo en el laberinto y el árbol
                        self.dibujar_nodo_lab(nueva_posicion)
                        self.dibujar_arbol(nodo_actual, nuevo_nodo)
                        self.root.update()
                        time.sleep(0.5)

                        # Verificar si se alcanzó el límite de expansiones
                    if expansiones_realizadas >= profundidad_max:
                        print(f"Límite de expansiones alcanzado: {profundidad_max}")
                        return False

            # Detener si se alcanza el límite de profundidad
        if profundidad >= profundidad_max:
            print(f"Límite de profundidad alcanzado: {profundidad_max}")
            return False


        # Si la búsqueda DFS limitada no encuentra el queso, retornar False
        print(f"No se encontró el queso con DFS limitada a profundidad {profundidad_max}.")
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
            x_hijo = x_padre - (self.hijos_contador[nodo_padre] * 160) + 80
        else:
            num_hijos = len(nodo_padre.hijos)

            # Invierta el orden de posicionamiento para agregar primero el nodo derecho
            x_hijo = x_padre - ((num_hijos / 2) - self.hijos_contador[nodo_padre]) * 60

            x_hijo = x_padre + (self.hijos_contador[nodo_padre] - num_hijos / 2) * 60


        y_hijo = y_padre + 80  # Aumento en altura para el hijo

        # Dibujar la línea entre el nodo padre y el hijo
        self.canvas_arbol.create_line(x_padre, y_padre, x_hijo, y_hijo, fill="black")

        # Dibujar el nodo hijo
        self.canvas_arbol.create_oval(x_hijo - 5, y_hijo - 5, x_hijo + 5, y_hijo + 5, fill="blue")

        # Mostrar las coordenadas de la cuadrícula del nodo hijo encima de él
        grid_x, grid_y = nodo_hijo.posicion  # Obtener las coordenadas de la cuadrícula
        self.canvas_arbol.create_text(x_hijo, y_hijo - 20, text=f"({grid_x}, {grid_y})", fill="black")

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
