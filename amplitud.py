import tkinter as tk
from PIL import Image, ImageTk
from collections import deque
import time
import random

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
        self.bloques_grises = [(1,1), (3,2)]  # aqui ubica las Paredes/bloques grises donde le de la gana

        
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
        self.realizar_busqueda_hibrida(4)  # Comenzar la búsqueda por amplitud la unica que tengo daa


    busquedas_aplicadas = [] 
    
    ##TODO:  Busqueda por amplitud y profundidad hibrida, ejecutar cambios
    def realizar_busqueda_hibrida(self, max_expansiones):
        # Inicializar estructuras de control para ambas búsquedas
        pila_dfs = [NodoArbol(self.raton_pos)]  # Para DFS
        cola_bfs = deque()  # Para BFS (inicialmente vacía)
        visitados = set([self.raton_pos])  # Nodos ya visitados
        expansiones = 0  # Contador de expansiones de cada fase
        expansiones_totales = 0  # Contador total de expansiones
        usando_dfs = True  # Comenzamos con DFS

        while True:
            if usando_dfs:
                # Realizar búsqueda por profundidad (DFS)
                if not pila_dfs:
                    print("No quedan nodos en la pila de DFS para expandir.")
                    # Cambiar a BFS si no hay más nodos en DFS
                    if not cola_bfs:  # Si BFS también está vacío, terminamos
                        break
                    usando_dfs = False  # Cambiar a BFS
                    expansiones = 0  # Resetear el contador de expansiones
                    print("Cambiando de búsqueda. Usando BFS ahora.")
                    continue  # Volver a comenzar el bucle con BFS

                nodo_actual = pila_dfs.pop()
            else:
                # Realizar búsqueda por amplitud (BFS)
                if not cola_bfs:
                    # Si no hay nodos en BFS, volver a DFS si hay nodos
                    if pila_dfs:
                        usando_dfs = True  # Cambiar a DFS
                        expansiones = 0  # Resetear el contador de expansiones
                        print("Cambiando de búsqueda. Usando DFS ahora.")
                        continue  # Volver a comenzar el bucle con DFS
                    else:
                        print("No quedan nodos en la cola de BFS para expandir.")
                        break

                nodo_actual = cola_bfs.popleft()

            posicion_actual = nodo_actual.posicion

            # Si encuentra el queso, muestra el camino y termina
            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado!")
                self.mostrar_camino(nodo_actual)
                return

            # Explorar los movimientos posibles
            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                # Verificar si la nueva posición es válida y no ha sido visitada
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nodo_actual.hijos.append(nuevo_nodo)

                    # Agregar a la pila o cola dependiendo del algoritmo en uso
                    if usando_dfs:
                        pila_dfs.append(nuevo_nodo)
                    else:
                        cola_bfs.append(nuevo_nodo)

                    visitados.add(nueva_posicion)
                    expansiones += 1
                    expansiones_totales += 1

                    # Dibujar el nodo en el laberinto y el árbol en la interfaz gráfica
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)

                    # Actualizar la interfaz gráfica
                    self.root.update()
                    time.sleep(0.5)  # Ajustar el tiempo de visualización si es necesario

                    # Si alcanza el límite de expansiones, cambiar de búsqueda
                    if expansiones >= max_expansiones:
                        print(f"Límite de expansiones ({max_expansiones}) alcanzado.")
                        if usando_dfs:
                            # Si está usando DFS, mover nodos a BFS
                            cola_bfs.extend(pila_dfs)  # Agregar los nodos restantes de DFS a BFS
                            pila_dfs.clear()  # Limpiar la pila DFS
                            usando_dfs = False  # Cambiar a BFS
                            print("Cambiando de búsqueda. Usando BFS ahora.")
                        else:
                            usando_dfs = True  # Cambiar de nuevo a DFS
                            print("Cambiando de búsqueda. Usando DFS ahora.")
                        expansiones = 0  # Resetear el contador de expansiones
                        break

        # Si no se encuentra el queso después de todas las expansiones
        print(f"Expansiones totales: {expansiones_totales}")
        print(f"No se encontró el queso después de {expansiones_totales} expansiones.")


    def realizar_dfs_limitada(self, max_expansiones):
        # Limitar el número de expansiones a N (max_expansiones)
        pila = [(NodoArbol(self.raton_pos), 0)]  # (nodo, profundidad actual)
        visitados = set([self.raton_pos])
        expansiones = 0

        while pila:
            nodo_actual, profundidad_actual = pila.pop()
            posicion_actual = nodo_actual.posicion

            # Si encuentra el queso, muestra el camino
            if posicion_actual == self.queso_pos:
                print("Queso encontrado!")
                self.mostrar_camino(nodo_actual)
                return

            # Solo se expanden nodos si no se ha alcanzado la profundidad máxima
            if profundidad_actual < max_expansiones:
                # Explorar los movimientos posibles
                for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                    # Verificar si la nueva posición es válida y no ha sido visitada
                    if (0 <= nueva_posicion[0] < self.rows and
                        0 <= nueva_posicion[1] < self.cols and
                        self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                        nueva_posicion not in visitados):
                        
                        nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                        nodo_actual.hijos.append(nuevo_nodo)
                        pila.append((nuevo_nodo, profundidad_actual + 1))  # Incrementar la profundidad
                        visitados.add(nueva_posicion)

                        # Contar la expansión
                        expansiones += 1

                        # Dibujar el nodo en el laberinto y el árbol en la interfaz gráfica
                        self.dibujar_nodo_lab(nueva_posicion)
                        self.dibujar_arbol(nodo_actual, nuevo_nodo)

                        # Actualizar la interfaz
                        self.root.update()
                        time.sleep(0.5)  # Puedes ajustar el tiempo de visualización

            # Mensaje al llegar al límite de expansiones
            if expansiones >= max_expansiones:
                print(f"Límite de expansiones ({max_expansiones}) alcanzado. Cambiando de rama...")
                # No hay un break aquí, simplemente el bucle continúa y el método cambia de rama.

        # Este mensaje solo se imprimirá si se sale del bucle sin encontrar el queso.
        print("No se encontró el queso.")



    def busqueda_por_profundidad_iterativa(self):
        return 0
    
    def dibujar_nodo_lab(self, posicion):
        time.sleep(5)
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

        # Si es la raíz, centrarla en el canvas
        if nodo_padre not in self.nodo_padre_coords:
            x_centro = canvas_ancho // 2  # Centrar la raíz
            self.nodo_padre_coords[nodo_padre] = (x_centro, 20)  # Coordenadas iniciales centradas
            self.canvas_arbol.create_oval(x_centro - 5, 15, x_centro + 5, 25, fill="blue")  # Dibujar la raíz

        # Obtener coordenadas del nodo padre
        x_padre, y_padre = self.nodo_padre_coords[nodo_padre]

        # Verificar si el nodo padre es la raíz (no tiene padre)
        es_raiz = nodo_padre.padre is None

        # Mayor separación solo para los dos primeros hijos de la raíz
        if es_raiz and self.hijos_contador[nodo_padre] < 2:
            x_hijo = x_padre + (self.hijos_contador[nodo_padre] * 160) - 80  # Separar más los dos primeros hijos (160 en vez de 200)
        else:
            # Calcular la posición del nuevo hijo para otros nodos
            num_hijos = len(nodo_padre.hijos)
            x_hijo = x_padre + (self.hijos_contador[nodo_padre] - num_hijos / 2) * 40  # Separación normal entre hijos (40 en vez de 50)
        
        y_hijo = y_padre + 80  # Incrementar la altura para el hijo (80 en vez de 100)

        # Verificar si ya hay un nodo en la posición del hijo
        while (x_hijo, y_hijo) in self.nodo_padre_coords.values():
            print(f"Advertencia: Ya existe un nodo en la posición ({x_hijo}, {y_hijo}). Moviendo a la derecha.")
            x_hijo += 20  # Desplazar el nodo a la derecha si ya hay un nodo en la misma posición

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
