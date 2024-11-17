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
        self.nivel = 0  # El nivel es 0 por defecto
        self.profundidad = 0  # La profundidad es 0 por defecto (se usará en DFS)
        self.left_value = 0  # Para identificar el nodo más a la izquierda

        if padre is not None:
            self.nivel = padre.nivel + 1  # El nivel es uno más que el del padre
            self.profundidad = padre.profundidad + 1  # La profundidad es uno más que el del padre
            
            parent_x = padre.posicion[1]
            current_x = posicion[1]
            if current_x > parent_x:
                self.left_value = padre.left_value + 1
            elif current_x < parent_x:
                self.left_value = padre.left_value - 1
            else:
                self.left_value = padre.left_value
            self.left_value += padre.left_value

    def agregar_hijo(self, hijo):
        """Agrega un hijo manteniendo el orden por posición y ajustando el valor de left_value"""
        self.hijos.append(hijo)
        # Ordenar hijos primero por columna (izquierda a derecha), luego por fila (arriba a abajo)
        self.hijos.sort(key=lambda n: (n.posicion[1], n.posicion[0]))  # Ordena por columna, luego por fila
        

class EstadoBusqueda:
    def __init__(self, nodo_raiz, estructura_datos, visitados=None, expansiones=0, max_expansiones=100):
        self.nodo_raiz = nodo_raiz  # Nodo raíz del árbol de búsqueda
        self.estructura_datos = estructura_datos  # Pila, cola, heap, etc.
        self.visitados = visitados or set()  # Conjunto de posiciones visitadas
        self.expansiones = expansiones  # Número de expansiones realizadas
        self.max_expansiones = max_expansiones  # Límite de expansiones
        self.nodos_creados = []  # Lista de nodos creados

    def agregar_nodo(self, nodo):
        """Agrega un nodo a la estructura de datos y al árbol de búsqueda."""
        self.estructura_datos.append(nodo)
        self.nodos_creados.append(nodo)
        
class Laberinto:
    def __init__(self, root, rows=8, cols=8, expansiones_por_actualizacion=2):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_width = 50  # aqui acomoda el Ancho de cada celda
        self.cell_height = 50  # lo mismo Alto de cada celda
        self.image_scale_factor = 0.93  # esta mkd es para que la imagen no tape los bordes de las celdas, se escala un poco menos al 93
        self.expansiones_por_actualizacion = expansiones_por_actualizacion
        self.nodo_padre_coords = {}
        self.hijos_contador = {}  # Agregar un contador de hijos por nodo

        self.maze = [[0 for _ in range(cols)] for _ in range(rows)]  
        
        
        self.raton_pos = (0, 0)  # aqui define la Posición del ratón
        self.queso_pos = (0, 6)  # lo mismo con la Posición del queso
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
        self.boton_iniciar.config(state=tk.DISABLED)  
        self.realizar_busqueda_hibrida()  

    def solicitar_limite_expansiones(self, tipo_busqueda):
        try:
            n = int(input(f"Ingrese el límite de expansiones para la búsqueda {tipo_busqueda}: "))
            return n
        except ValueError:
            print("Por favor, ingrese un número entero.")
            return self.solicitar_limite_expansiones(tipo_busqueda)

    def busqueda_costo_uniforme(self, estado):
        # Inicializa el heap (asegúrate de agregar la tupla (costo, nodo))
        nodo_inicial = NodoArbol(self.raton_pos)
        heapq.heappush(estado.estructura_datos, (0, nodo_inicial))  # Agregar la tupla (costo, nodo)

        while estado.estructura_datos and estado.expansiones < estado.max_expansiones:
            # Verifica que lo que sacas del heap sea una tupla (costo, nodo)
            if isinstance(estado.estructura_datos[0], tuple) and len(estado.estructura_datos[0]) == 2:
                costo_actual, nodo_actual = heapq.heappop(estado.estructura_datos)
            else:
                print("Error: La estructura de datos no contiene una tupla (costo, nodo)")
                return False, estado

            posicion_actual = nodo_actual.posicion

            if posicion_actual in estado.visitados:
                continue

            estado.visitados.add(posicion_actual)
            estado.expansiones += 1

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con UCS!")
                return True, estado

            # Generar hijos
            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in estado.visitados):
                    nuevo_costo = costo_actual + 1
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual, costo=nuevo_costo)
                    nodo_actual.agregar_hijo(nuevo_nodo)
                    estado.agregar_nodo(nuevo_nodo)

                    # Asegúrate de agregar la tupla (costo, nodo) en la cola
                    heapq.heappush(estado.estructura_datos, (nuevo_costo, nuevo_nodo))

                    # Visualización
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

        print("No se encontró el queso con UCS.")
        return False, estado


    def realizar_busqueda_hibrida(self):
        nodo_inicial = NodoArbol(self.raton_pos)
        estado = EstadoBusqueda(nodo_inicial, estructura_datos=[nodo_inicial], max_expansiones=2)
        
        resultado, estado = self.busqueda_costo_uniforme(estado)
        if resultado:
            return
        
        
    def dibujar_nodo_lab(self, posicion):
        time.sleep(1)
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

        # Calcular la posición de los nuevos hijos
        if es_raiz:
            # Para la raíz, distribuimos los hijos uniformemente en el eje X
            num_hijos = len(nodo_padre.hijos)
            espacio = 160  # Espacio entre los nodos (puedes ajustarlo según el tamaño deseado)
            x_inicio = x_padre - (num_hijos - 1) * espacio // 2  # Ajustar para centrar los hijos
        else:
            # Para nodos no raíz, también distribuimos los hijos uniformemente
            num_hijos = len(nodo_padre.hijos)
            espacio = 60  # Espacio entre los nodos hijos
            x_inicio = x_padre - (num_hijos - 1) * espacio // 2  # Ajustar para centrar los hijos

        # Determinar la posición del hijo en el eje X
        x_hijo = x_inicio + self.hijos_contador[nodo_padre] * espacio
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
