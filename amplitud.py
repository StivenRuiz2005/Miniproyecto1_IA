import tkinter as tk
from PIL import Image, ImageTk
from collections import deque
import time
import random
import heapq

class NodoArbol:
    def __init__(self, posicion, padre=None, costo=0, altura=None):
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
        
        
        self.raton_pos = (6, 1)  # aqui define la Posición del ratón
        self.queso_pos = (0, 6)  # lo mismo con la Posición del queso
        self.bloques_grises = [(1,1), (4,3), (2,1), (3,4),(7,2), (6,5),(4,2),(1,3),(1,1)]  # aqui ubica las Paredes/bloques grises donde le de la gana

        
        self.raton_image = self.cargar_imagenes(r"Images/Raton.png")#no se le olvide combiar la ruta de las imagenes o paila no se ejecuta esta monda
        self.queso_image = self.cargar_imagenes(r"Images/queso.png")

        self.iniciar_laberinto()

    
        self.dibujar_laberinto()
        self.crear_area_arbol()
            
        self.estrategia_label = tk.Label(self.root, text="Estrategia: Ninguna")
        self.estrategia_label.grid(row=1, column=0, pady=10)
        
        self.estrategia_label1 = tk.Label(self.root, text="Sin encontrar queso")
        self.estrategia_label1.grid(row=1, column=1, pady=10)

        self.boton_iniciar = tk.Button(self.root, text="Iniciar programa", command=self.iniciar_busqueda)
        self.boton_iniciar.grid(row=2, column=0, pady=10)
    def actualizar_interfaz_estrategia(self, nombre_estrategia):
    # Actualizar la interfaz con el nombre de la estrategia actual
        self.estrategia_label.config(text=f"Estrategia: {nombre_estrategia}")

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

    
    def realizar_busqueda_hibrida(self):
        global nodos_no_expandidos
        nodos_no_expandidos = []
        pila_dfs = []
        cola_bfs = deque()
        visitados = set([self.raton_pos])
        expansiones_totales = 0

        metodos_disponibles = ["avara", "UCS"]
        metodo_actual = random.choice(metodos_disponibles)
        metodos_disponibles.remove(metodo_actual)

        global nodo_inicial
        nodo_inicial = NodoArbol(self.raton_pos)

        while True:
            if metodo_actual == "DFS":
                self.actualizar_interfaz_estrategia("DFS")
                max_expansiones = self.solicitar_limite_expansiones("DFS")
                resultado, expansiones = self.busqueda_dfs(
                    pila_dfs, visitados, max_expansiones
                )
                expansiones_totales += expansiones
                if resultado:
                    return

            elif metodo_actual == "BFS":
                self.actualizar_interfaz_estrategia("BFS")
                max_expansiones = self.solicitar_limite_expansiones("BFS")
                resultado, expansiones, nodos_creados = self.busqueda_bfs(
                    cola_bfs, visitados, max_expansiones
                )
                expansiones_totales += expansiones
                if resultado:
                    print(f"¡Queso encontrado con BFS después de {expansiones_totales} expansiones!")
                    return
                
            elif metodo_actual == "UCS":
                self.actualizar_interfaz_estrategia("UCS")
                max_expansiones = self.solicitar_limite_expansiones("de Costo Uniforme")
                resultado, expansiones = self.busqueda_costo_uniforme(
                    max_expansiones
                )
                expansiones_totales += expansiones
                if resultado:
                    print(f"¡Queso encontrado con búsqueda de costo uniforme después de {expansiones_totales} expansiones!")
                    return
            elif metodo_actual == "IDDFS":
                self.actualizar_interfaz_estrategia("IDDFS")
                max_expansiones = self.solicitar_limite_expansiones("IDDFS")
                resultado = self.busqueda_iddfs(1, max_expansiones)
                expansiones_totales += 1
                if resultado:
                    print(f"¡Queso encontrado con IDDFS después de {expansiones_totales} expansiones!")
                
            elif metodo_actual == "avara":
                self.actualizar_interfaz_estrategia("avara")
                max_expansiones = self.solicitar_limite_expansiones("Avara")
                resultado, expansiones = self.busqueda_avara(
                    max_expansiones
                )
                expansiones_totales += expansiones
                if resultado:
                    print(f"¡Queso encontrado con búsqueda Avara después de {expansiones_totales} expansiones!")
                    return    
                
            if not metodos_disponibles:
                print(f"Expansiones totales: {expansiones_totales}")
                print("No se encontró el queso después de probar todas las búsquedas.")
                break

            # Switch to the next available method
            metodo_actual = random.choice(metodos_disponibles)
            metodos_disponibles.remove(metodo_actual)

    #Funciona solita
    def busqueda_dfs(self, pila_dfs, visitados, max_expansiones):
        pila_dfs.append(nodo_inicial)
        expansiones = 0
        while pila_dfs:
            nodo_actual = pila_dfs.pop()  # Continuamos con el último nodo añadido a la pila
            expansiones += 1
            posicion_actual = nodo_actual.posicion
            print(f"Expandiendo nodo DFS: {posicion_actual}")  # Registro de la expansión

            if posicion_actual == self.queso_pos:
                self.estrategia_label1.config(text="¡Queso encontrado con DFS!")
                return True, expansiones

            # Recolectar movimientos válidos
            movimientos_validos = []
            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    movimientos_validos.append(nueva_posicion)
                    

            # Crear los nodos hijos (de izquierda a derecha)
            nodos_hijos = []
            for nueva_posicion in movimientos_validos:
                nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                nodo_actual.agregar_hijo(nuevo_nodo)
                nodos_hijos.append(nuevo_nodo)
                visitados.add(nueva_posicion)

                # Dibujar los nodos y actualizar el árbol
                self.dibujar_nodo_lab(nueva_posicion)
                self.dibujar_arbol(nodo_actual, nuevo_nodo)
                self.root.update()
                time.sleep(0.5)
 
                if expansiones >= max_expansiones:
                    self.estrategia_label1.config(text="Límite de expansiones alcanzado")
                    return False, expansiones

            # Ahora los hijos se añaden en orden inverso, para que el hijo izquierdo se expanda primero
            for nodo in reversed(nodos_hijos):
                pila_dfs.append(nodo)

        return False, expansiones

    #No funciona
    def busqueda_bfs(self, cola_bfs, visitados, max_expansiones):
        nodo_inicial = NodoArbol(self.raton_pos)
        cola_bfs.append((nodo_inicial, 0))
        expansiones = 0
        nodos_creados = []

        while cola_bfs:
            nodo_actual, profundidad = cola_bfs.popleft()
            posicion_actual = nodo_actual.posicion
            print(f"Expandiendo nodo BFS: {posicion_actual}")

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con BFS!")
                return True, expansiones, nodos_creados

            # Collect valid movements
            movimientos_validos = []
            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    movimientos_validos.append(nueva_posicion)

            # Create child nodes (left to right)
            nodos_hijos = []
            for nueva_posicion in movimientos_validos:
                nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                nodo_actual.agregar_hijo(nuevo_nodo)
                nodos_hijos.append(nuevo_nodo)
                visitados.add(nueva_posicion)

                # Draw nodes and update the tree
                self.dibujar_nodo_lab(nueva_posicion)
                self.dibujar_arbol(nodo_actual, nuevo_nodo)
                self.root.update()
                time.sleep(0.5)

            # Count the expansion after all children are created
            if nodos_hijos:
                expansiones += 1

            if expansiones >= max_expansiones:
                print(f"Límite de expansiones alcanzado en BFS ({expansiones})")
                return False, expansiones, nodos_creados

            nodos_creados.extend(nodos_hijos)  # Store created nodes for use by DFS
            cola_bfs.extend((nodo, profundidad + 1) for nodo in nodos_hijos)

        return False, expansiones, nodos_creados

    #No funciona
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
            expansiones_realizadas += 1
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
        
    #Funciona solita
 

    def busqueda_costo_uniforme(self, max_expansiones):
            global nodos_no_expandidos

            # Usamos una cola de prioridad (heap) para mantener los nodos ordenados por costo
            # El formato es (costo_acumulado, contador, nodo)
            # El contador es para desempatar cuando hay costos iguales
            cola_prioridad = []
            contador = 0
            visitados = set()
            costos = {}

            # Si hay nodos no expandidos, agrégalos a la cola
            if nodos_no_expandidos:
                for nodo in nodos_no_expandidos:
                    heapq.heappush(cola_prioridad, (nodo.costos, contador, nodo))
                    contador += 1
                    costos[nodo.posicion] = nodo.costos
                print(f"Continuando desde nodos no expandidos: {len(nodos_no_expandidos)} nodos")
                nodos_no_expandidos = []  # Reiniciamos la lista de nodos no expandidos
            else:
                # Crear y agregar el nodo inicial si no hay nodos previos
                nodo_inicial = NodoArbol(self.raton_pos)
                heapq.heappush(cola_prioridad, (0, contador, nodo_inicial))
                contador += 1
                costos[self.raton_pos] = 0

            expansiones = 0

            while expansiones < max_expansiones:
                # Obtener el nodo con menor costo
                costo_actual, _, nodo_actual = heapq.heappop(cola_prioridad)
                posicion_actual = nodo_actual.posicion

                # Si ya visitamos esta posición, continuamos
                if posicion_actual in visitados:
                    continue

                # Marcar como visitado
                visitados.add(posicion_actual)
                expansiones += 1
                print(f"Expandiendo nodo: {posicion_actual} con costo {costo_actual}")

                # Verificar si encontramos el queso
                if posicion_actual == self.queso_pos:
                    print(f"¡Queso encontrado con búsqueda de costo uniforme!")
                    print(f"Costo total del camino: {costo_actual}")
                    return True, expansiones

                # Expandir el nodo actual
                for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:  # Izquierda, Arriba, Derecha, Abajo
                    nueva_posicion = (
                        posicion_actual[0] + movimiento[0],
                        posicion_actual[1] + movimiento[1]
                    )

                    # Verificar si el movimiento es válido
                    if (0 <= nueva_posicion[0] < self.rows and 
                        0 <= nueva_posicion[1] < self.cols and 
                        self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0):

                        # Calcular el nuevo costo
                        nuevo_costo = costo_actual + 1  # Cada movimiento tiene costo 1
                        
                        # Si encontramos un camino mejor a esta posición
                        if nueva_posicion not in costos or nuevo_costo < costos[nueva_posicion]:
                            costos[nueva_posicion] = nuevo_costo
                            contador += 1
                            
                            # Crear nuevo nodo
                            nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual, costo=nuevo_costo)
                            nodo_actual.agregar_hijo(nuevo_nodo)
                            
                            # Agregar a la cola de prioridad
                            heapq.heappush(cola_prioridad, (nuevo_costo, contador, nuevo_nodo))
                            
                            # Visualización
                            self.dibujar_nodo_lab(nueva_posicion)
                            self.dibujar_arbol(nodo_actual, nuevo_nodo)
                            self.root.update()
                            time.sleep(0.5)

            # Si terminamos sin encontrar el queso
            if cola_prioridad:
                nodos_no_expandidos.extend([nodo for _, _, nodo in cola_prioridad])
                print(f"Agregando {len(cola_prioridad)} nodos a la lista de no expandidos.")
            else:
                print("No se encontraron más nodos para expandir.")

            print("No se encontró el queso")
            return False, expansiones

    #Heuristica
    def heuristica_manhattan(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    #Funciona solita
    def busqueda_avara(self, max_expansiones):
        global nodos_no_expandidos
        # Usamos una cola de prioridad (heap) para mantener los nodos ordenados por heurística
        # El formato es (heuristica, contador, nodo)
        cola_prioridad = []
        contador = 0
        visitados = set()
        
        # Si hay nodos no expandidos, agrégalos a la cola
        if nodos_no_expandidos:
            for nodo in nodos_no_expandidos:
                heuristica = self.heuristica_manhattan(nodo.posicion, self.queso_pos)
                heapq.heappush(cola_prioridad, (heuristica, contador, nodo))
                contador += 1
            print(f"Continuando desde nodos no expandidos: {len(nodos_no_expandidos)} nodos")
            nodos_no_expandidos = []  # Reiniciar la lista global de nodos no expandidos
        else:
            # Crear y agregar el nodo inicial si no hay nodos previos
            nodo_inicial = NodoArbol(self.raton_pos)
            heuristica_inicial = self.heuristica_manhattan(self.raton_pos, self.queso_pos)
            heapq.heappush(cola_prioridad, (heuristica_inicial, contador, nodo_inicial))
            contador += 1

        expansiones = 0

        while cola_prioridad and expansiones < max_expansiones:
            # Obtener el nodo con menor heurística
            heuristica_actual, _, nodo_actual = heapq.heappop(cola_prioridad)
            posicion_actual = nodo_actual.posicion

            # Si ya visitamos esta posición, continuamos
            if posicion_actual in visitados:
                continue

            # Marcar como visitado
            visitados.add(posicion_actual)
            expansiones += 1
            print(f"Expandiendo nodo: {posicion_actual} con heurística {heuristica_actual}")

            # Verificar si encontramos el queso
            if posicion_actual == self.queso_pos:
                print(f"¡Queso encontrado con búsqueda Avara!")
                print(f"Total de expansiones realizadas: {expansiones}")
                return True, expansiones

            # Expandir el nodo actual
            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:  # Izquierda, Arriba, Derecha, Abajo
                nueva_posicion = (
                    posicion_actual[0] + movimiento[0],
                    posicion_actual[1] + movimiento[1]
                )

                # Verificar si el movimiento es válido
                if (0 <= nueva_posicion[0] < self.rows and 
                    0 <= nueva_posicion[1] < self.cols and 
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):

                    # Calcular la heurística (distancia de Manhattan)
                    nueva_heuristica = self.heuristica_manhattan(nueva_posicion, self.queso_pos)
                    contador += 1
                    
                    # Crear nuevo nodo
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nuevo_nodo.costos = nodo_actual.costos + 1  # Costo de movimiento
                    nodo_actual.agregar_hijo(nuevo_nodo)
                    
                    # Agregar a la cola de prioridad
                    heapq.heappush(cola_prioridad, (nueva_heuristica, contador, nuevo_nodo))
                    
                    # Visualización
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

        # Si terminamos sin encontrar el queso
        if cola_prioridad:
            nodos_no_expandidos.extend([nodo for _, _, nodo in cola_prioridad])
            print(f"Agregando {len(cola_prioridad)} nodos a la lista de no expandidos.")
        else:
            print("No se encontraron más nodos para expandir.")

        print("No se encontró el queso")
        return False, expansiones

   
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
    root.title("Laberinto - Aplicando busquedas hibridas")
    app = Laberinto(root, expansiones_por_actualizacion=2)
    root.mainloop()
