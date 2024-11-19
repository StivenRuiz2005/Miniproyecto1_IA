import tkinter as tk
from PIL import Image, ImageTk
from collections import deque
import time
import random
import heapq

class NodoArbol:
    def __init__(self, posicion, padre=None, costo=0, altura=0):
        self.posicion = posicion
        self.padre = padre
        self.hijos = []
        self.costos = costo
        self.altura = altura
        self.nivel = 0 #Nivel inicial
        self.profundidad = 0  # Profundidad Inicial
        self.left_value = 0  

        if padre is not None:
            self.nivel = padre.nivel + 1  
            self.profundidad = padre.profundidad + 1  
            
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
        self.hijos.append(hijo)
        self.hijos.sort(key=lambda n: (n.posicion[1], n.posicion[0])) 
        
        
class Laberinto:
    def __init__(self, root, rows=6, cols=6, expansiones_por_actualizacion=2):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_width = 50  #Ancho Celda
        self.cell_height = 50  # Alto Celda
        self.image_scale_factor = 0.93  # Esto es para que la imagen no tape los bordes de las celdas, se escala un poco menos al 93
        self.expansiones_por_actualizacion = expansiones_por_actualizacion
        self.nodo_padre_coords = {}
        self.hijos_contador = {}  # Contador de Hijos

        self.maze = [[0 for _ in range(cols)] for _ in range(rows)]  
        
        
        self.raton_pos = (0, 3)  # Posición del Ratón
        self.queso_pos = (2, 5)  # Posición del Queso
        self.bloques_grises = [(0,2), (3,3), (1,4), (3,2)]  # Paredes y obstaculos

        
        self.raton_image = self.cargar_imagenes(r"Images/Raton.png")
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
        
        self.estrategia_label.config(text=f"Estrategia: {nombre_estrategia}")

    def cargar_imagenes(self, path):
        adjusted_width = int(self.cell_width * self.image_scale_factor)
        adjusted_height = int(self.cell_height * self.image_scale_factor)
        image = Image.open(path).resize((adjusted_width, adjusted_height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def iniciar_laberinto(self):
        for bloque in self.bloques_grises:
            row, col = bloque
            self.maze[row][col] = 1 

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
        frame_contenedor = tk.Frame(self.root, bg="white")
        frame_contenedor.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")


        self.canvas_arbol = tk.Canvas(frame_contenedor, width=700, height=600, bg="white")
        self.canvas_arbol.grid(row=0, column=0, sticky="nsew")


        scrollbar_y = tk.Scrollbar(frame_contenedor, orient="vertical", command=self.canvas_arbol.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")  


        scrollbar_x = tk.Scrollbar(frame_contenedor, orient="horizontal", command=self.canvas_arbol.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew") 


        self.canvas_arbol.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.canvas_arbol.configure(scrollregion=(0, 0, 3000, 3000))


        frame_contenedor.grid_rowconfigure(0, weight=1)
        frame_contenedor.grid_columnconfigure(0, weight=1)

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
        expansiones_totales = 0

        metodos_disponibles = ["BFS", "avara"]
        metodo_actual = random.choice(metodos_disponibles)
        metodos_disponibles.remove(metodo_actual)

        global nodo_inicial
        nodo_inicial = NodoArbol(self.raton_pos)

        while True:
            if metodo_actual == "DFS":
                self.actualizar_interfaz_estrategia("DFS")
                max_expansiones = self.solicitar_limite_expansiones("DFS")
                resultado, expansiones = self.busqueda_dfs(
                    max_expansiones
                )
                expansiones_totales += expansiones
                if resultado:
                    return

            elif metodo_actual == "BFS":
                self.actualizar_interfaz_estrategia("BFS")
                max_expansiones = self.solicitar_limite_expansiones("BFS")
                resultado, expansiones = self.busqueda_bfs(
                    max_expansiones
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
                    
            elif metodo_actual == "DFSLI":
                self.actualizar_interfaz_estrategia("DFSLI")
                max_expansiones = self.solicitar_limite_expansiones("DFSLI")
                resultado = self.busqueda_dfs_limitada(max_expansiones)
                expansiones_totales += max_expansiones
                if resultado:
                    print(f"¡Queso encontrado con DFS limitada después de {expansiones_totales} expansiones!")
                
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

            metodo_actual = random.choice(metodos_disponibles)
            metodos_disponibles.remove(metodo_actual)

    #Funciona solita
    def busqueda_dfs(self, max_expansiones):
        global nodos_no_expandidos
        visitados = set([self.raton_pos])  #Puse esto para poder guardar los visitados
        pila_dfs = []

        # Si hay nodos no expandidos, los procesamos primero
        if nodos_no_expandidos:
            nodos_no_expandidos.sort(key=lambda nodo: nodo.altura, reverse=True) 
            for nodo in nodos_no_expandidos:
                pila_dfs.append(nodo)
            nodos_no_expandidos = [] 
        else:
            nodo_inicial = NodoArbol(self.raton_pos)
            pila_dfs.append(nodo_inicial)

        expansiones = 0

        while pila_dfs:
            nodo_actual = pila_dfs.pop()  #Aquí saco el ultimo añadido a la pila
            posicion_actual = nodo_actual.posicion
            print(f"Expandiendo nodo DFS: {posicion_actual}")
            expansiones += 1


            if posicion_actual == self.queso_pos:
                self.estrategia_label1.config(text="¡Queso encontrado con DFS!")
                return True, expansiones


            movimientos_validos = []
            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    movimientos_validos.append(nueva_posicion)

            #Añado sus hijos de izq a derecha
            nodos_hijos = []
            for nueva_posicion in movimientos_validos:
                nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                nodo_actual.agregar_hijo(nuevo_nodo)
                nodos_hijos.append(nuevo_nodo)
                visitados.add(nueva_posicion)


                self.dibujar_nodo_lab(nueva_posicion)
                self.dibujar_arbol(nodo_actual, nuevo_nodo)
                self.root.update()
                time.sleep(0.5)

            # Se tienen que invertir los nodos para que se respete el orden
            for nodo in reversed(nodos_hijos):
                pila_dfs.append(nodo)


            if expansiones >= max_expansiones:
                print(f"Límite de expansiones alcanzado en DFS ({expansiones})")
                nodos_no_expandidos.extend(pila_dfs)  
                self.estrategia_label1.config(text="Límite de expansiones alcanzado")
                return False, expansiones

        nodos_no_expandidos.extend(pila_dfs)
        return False, expansiones


    def busqueda_bfs(self, max_expansiones):
        global nodos_no_expandidos

        cola_bfs = deque()
        if nodos_no_expandidos:
            nodos_no_expandidos.sort(key=lambda nodo: nodo.altura)

            for nodo in nodos_no_expandidos:
                cola_bfs.append((nodo, 0))  
            nodos_no_expandidos = []  
        else:

            nodo_inicial = NodoArbol(self.raton_pos)
            cola_bfs.append((nodo_inicial, 0))

        expansiones = 0
        visitados = set([self.raton_pos]) 

        while cola_bfs:
            nodo_actual, profundidad = cola_bfs.popleft()
            posicion_actual = nodo_actual.posicion
            print(f"Expandiendo nodo BFS: {posicion_actual}")

            if posicion_actual == self.queso_pos:
                print("¡Queso encontrado con BFS!")
                return True, expansiones


            movimientos_validos = []
            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):
                    movimientos_validos.append(nueva_posicion)


            nodos_hijos = []
            for nueva_posicion in movimientos_validos:
                nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                nodo_actual.agregar_hijo(nuevo_nodo)
                nodos_hijos.append(nuevo_nodo)
                visitados.add(nueva_posicion)


                self.dibujar_nodo_lab(nueva_posicion)
                self.dibujar_arbol(nodo_actual, nuevo_nodo)
                self.root.update()
                time.sleep(0.5)


            if nodos_hijos:
                expansiones += 1


            if expansiones >= max_expansiones:
                print(f"Límite de expansiones alcanzado en BFS ({expansiones})")
                nodos_no_expandidos.extend([nodo for nodo, _ in cola_bfs])
                return False, expansiones

            cola_bfs.extend((nodo, profundidad + 1) for nodo in nodos_hijos)
            
            
            if cola_bfs:
                    nodos_no_expandidos.extend([nodo for nodo, _ in cola_bfs])
                    print(f"Agregando {len(cola_bfs)} nodos a la lista de no expandidos.")
            else:
                    print("No se encontraron más nodos para expandir.")

        return False, expansiones


    def busqueda_dfs_limitada(self, profundidad_max):
        global nodos_no_expandidos 

        try:
            limite_profu = int(input("Ingrese el límite de profundidad deseado: "))
        except ValueError:
            print("Por favor, ingrese un número entero válido.")
            return self.busqueda_dfs_limitada(profundidad_max)

        pila_dfs = [(NodoArbol(self.raton_pos), 0)]  
        visitados = set([self.raton_pos])
        expansiones_realizadas = 0  
        nodos_espera = []  # Esta lista me va a guardar los nodos que dejó sin expandir

        while pila_dfs or nodos_espera:
            if not pila_dfs:  # Si no hay nodos para expandir, usamos los nodos en espera
                pila_dfs = nodos_espera
                nodos_espera = []

            if nodos_no_expandidos:  # Si hay nodos no expandidos, los ordenamos por altura
                nodos_no_expandidos.sort(key=lambda nodo: nodo.altura)  # Ordeno según altura de menor a mayor
                for nodo in nodos_no_expandidos:
                    pila_dfs.append((nodo, nodo.altura))
                nodos_no_expandidos = []  

            nodo_actual, altura = pila_dfs.pop()
            
            # Solo contar una expansión si realmente estamos expandiendo un nodo
            if altura < limite_profu: 
                expansiones_realizadas += 1

            posicion_actual = nodo_actual.posicion


            if posicion_actual == self.queso_pos:
                print(f"¡Queso encontrado con DFS limitada a profundidad {profundidad_max}!")
                self.mostrar_camino(nodo_actual) 
                return True

            nodos_hijos = [] 


            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])


                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0
                    and nueva_posicion not in visitados):


                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual, altura=altura + 1)  
                    nodo_actual.agregar_hijo(nuevo_nodo)
                    nodos_hijos.append(nuevo_nodo)
                    visitados.add(nueva_posicion)


                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

            if altura >= limite_profu:
                print(f"Límite de altura alcanzado en la rama de {nodo_actual.posicion}")

                for nodo in nodos_hijos:
                    nodos_espera.append(nodo)  

            else:

                for nodo in reversed(nodos_hijos):
                    pila_dfs.append((nodo, altura + 1))


            if expansiones_realizadas >= profundidad_max:
                print(f"Límite de expansiones alcanzado: {profundidad_max}")
                nodos_no_expandidos.extend(pila_dfs)  
                return False

        print(f"No se encontró el queso con DFS limitada a profundidad {profundidad_max}.")
        nodos_no_expandidos.extend(pila_dfs)  
        return False


    def busqueda_costo_uniforme(self, max_expansiones):
            global nodos_no_expandidos
            # Aquí tocó usar una cola de prioridad para ordenar por costos
            # El formato es (costo_acumulado, contador, nodo)
            # El contador es para desempatar cuando hay costos iguales
            cola_prioridad = []
            contador = 0
            visitados = set()
            costos = {}


            if nodos_no_expandidos:
                for nodo in nodos_no_expandidos:
                    heapq.heappush(cola_prioridad, (nodo.costos, contador, nodo))
                    contador += 1
                    costos[nodo.posicion] = nodo.costos
                print(f"Continuando desde nodos no expandidos: {len(nodos_no_expandidos)} nodos")
                nodos_no_expandidos = []  
            else:

                nodo_inicial = NodoArbol(self.raton_pos)
                heapq.heappush(cola_prioridad, (0, contador, nodo_inicial))
                contador += 1
                costos[self.raton_pos] = 0

            expansiones = 0

            while expansiones < max_expansiones:
                costo_actual, _, nodo_actual = heapq.heappop(cola_prioridad)
                posicion_actual = nodo_actual.posicion


                if posicion_actual in visitados:
                    continue

                visitados.add(posicion_actual)
                expansiones += 1
                print(f"Expandiendo nodo: {posicion_actual} con costo {costo_actual}")


                if posicion_actual == self.queso_pos:
                    print(f"¡Queso encontrado con búsqueda de costo uniforme!")
                    print(f"Costo total del camino: {costo_actual}")
                    return True, expansiones


                for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:  
                    nueva_posicion = (
                        posicion_actual[0] + movimiento[0],
                        posicion_actual[1] + movimiento[1]
                    )

                    if (0 <= nueva_posicion[0] < self.rows and 
                        0 <= nueva_posicion[1] < self.cols and 
                        self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0):

                        nuevo_costo = costo_actual + 1
                        
                        

                        if nueva_posicion not in costos or nuevo_costo < costos[nueva_posicion]:
                            costos[nueva_posicion] = nuevo_costo
                            contador += 1
                            
                            nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual, costo=nuevo_costo)
                            nuevo_nodo.altura = nodo_actual.altura + 1  
                            nodo_actual.agregar_hijo(nuevo_nodo)
                            
                            heapq.heappush(cola_prioridad, (nuevo_costo, contador, nuevo_nodo))
                            
                            # Visualización
                            self.dibujar_nodo_lab(nueva_posicion)
                            self.dibujar_arbol(nodo_actual, nuevo_nodo)
                            self.root.update()
                            time.sleep(0.5)

            if cola_prioridad:
                nodos_no_expandidos.extend([nodo for _, _, nodo in cola_prioridad])
                print(f"Agregando {len(cola_prioridad)} nodos a la lista de no expandidos.")
            else:
                print("No se encontraron más nodos para expandir.")

            print("No se encontró el queso")
            return False, expansiones


    def heuristica_manhattan(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


    def busqueda_avara(self, max_expansiones):
        global nodos_no_expandidos
        #Para la avara se hizo lo mismo, una cola de prioridad para ordenarlos en base a su manhattan
        cola_prioridad = []
        contador = 0
        visitados = set()
        
        if nodos_no_expandidos:
            for nodo in nodos_no_expandidos:
                heuristica = self.heuristica_manhattan(nodo.posicion, self.queso_pos)
                heapq.heappush(cola_prioridad, (heuristica, contador, nodo))
                contador += 1
            print(f"Continuando desde nodos no expandidos: {len(nodos_no_expandidos)} nodos")
            nodos_no_expandidos = [] 
        else:
            nodo_inicial = NodoArbol(self.raton_pos)
            heuristica_inicial = self.heuristica_manhattan(self.raton_pos, self.queso_pos)
            heapq.heappush(cola_prioridad, (heuristica_inicial, contador, nodo_inicial))
            contador += 1

        expansiones = 0

        while cola_prioridad and expansiones < max_expansiones:
            heuristica_actual, _, nodo_actual = heapq.heappop(cola_prioridad)
            posicion_actual = nodo_actual.posicion

            if posicion_actual in visitados:
                continue

            visitados.add(posicion_actual)
            expansiones += 1
            print(f"Expandiendo nodo: {posicion_actual} con heurística {heuristica_actual}")


            if posicion_actual == self.queso_pos:
                print(f"¡Queso encontrado con búsqueda Avara!")
                print(f"Total de expansiones realizadas: {expansiones}")
                return True, expansiones

            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:  # Izquierda, Arriba, Derecha, Abajo
                nueva_posicion = (
                    posicion_actual[0] + movimiento[0],
                    posicion_actual[1] + movimiento[1]
                )

                if (0 <= nueva_posicion[0] < self.rows and 
                    0 <= nueva_posicion[1] < self.cols and 
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in visitados):

                    nueva_heuristica = self.heuristica_manhattan(nueva_posicion, self.queso_pos)
                    contador += 1
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nuevo_nodo.costos = nodo_actual.costos + 1 
                    nuevo_nodo.altura = nodo_actual.altura + 1
                    nodo_actual.agregar_hijo(nuevo_nodo)

                    heapq.heappush(cola_prioridad, (nueva_heuristica, contador, nuevo_nodo))
                    
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)


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
        canvas_ancho = self.canvas_arbol.winfo_width()

        if nodo_padre not in self.hijos_contador:
            self.hijos_contador[nodo_padre] = 0  


        if nodo_hijo in self.nodo_padre_coords:
            print(f"El nodo {nodo_hijo} ya existe. Evitando duplicado.")
            return

        if nodo_padre not in self.nodo_padre_coords:
            x_centro = canvas_ancho // 2  
            self.nodo_padre_coords[nodo_padre] = (x_centro, 20)  
            self.canvas_arbol.create_oval(x_centro - 5, 15, x_centro + 5, 25, fill="blue")  

        # Obtener coordenadas del nodo padre
        x_padre, y_padre = self.nodo_padre_coords[nodo_padre]

        es_raiz = nodo_padre.padre is None

        if es_raiz:
            num_hijos = len(nodo_padre.hijos)
            espacio = 300 
            x_inicio = x_padre - (num_hijos - 1) * espacio // 2 
        else:
            num_hijos = len(nodo_padre.hijos)
            espacio = 100 
            x_inicio = x_padre - (num_hijos - 1) * espacio // 2  
    
 
        x_hijo = x_inicio + self.hijos_contador[nodo_padre] * espacio
        y_hijo = y_padre + 80 


        self.canvas_arbol.create_line(x_padre, y_padre, x_hijo, y_hijo, fill="black")

   
        self.canvas_arbol.create_oval(x_hijo - 5, y_hijo - 5, x_hijo + 5, y_hijo + 5, fill="blue")


        grid_x, grid_y = nodo_hijo.posicion  
        self.canvas_arbol.create_text(x_hijo, y_hijo - 20, text=f"({grid_x}, {grid_y})", fill="black")

        self.nodo_padre_coords[nodo_hijo] = (x_hijo, y_hijo)

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