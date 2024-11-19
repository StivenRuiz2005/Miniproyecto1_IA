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
    def __init__(self, root, rows=6, cols=6, expansiones_por_actualizacion=2):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_width = 50 
        self.cell_height = 50  
        self.image_scale_factor = 0.93  
        self.expansiones_por_actualizacion = expansiones_por_actualizacion
        self.nodo_padre_coords = {}
        self.hijos_contador = {}  # Agregar un contador de hijos por nodo

        self.maze = [[0 for _ in range(cols)] for _ in range(rows)]  
        
        
        self.raton_pos = (5, 1) 
        self.queso_pos = (2, 5)  
        self.bloques_grises = [(0,2), (3,3), (1,4), (3,2), (4,1), (3,1),(0,0),(0,1),(2,4),(5,3), (5,4), (1,1), (2,3)]  

        
        self.raton_image = self.cargar_imagenes(r"Images/Raton.png")
        self.queso_image = self.cargar_imagenes(r"Images/queso.png")

        self.iniciar_laberinto()

    
        self.dibujar_laberinto()
        self.crear_area_arbol()
            
        self.estrategia_label = tk.Label(self.root, text="Estrategia: Ninguna", font=("Arial", 13))
        self.estrategia_label.place(x=80, y=530)
        
        self.estrategia_label1 = tk.Label(self.root, text="Sin encontrar el queso",font=("Arial", 13))
        self.estrategia_label1.place(x=600, y=670)

        

        self.boton_iniciar = tk.Button(self.root, text="Iniciar programa", command=self.iniciar_busqueda)
        self.boton_iniciar.grid(row=2, column=0, pady=30)

        


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
        frame_contenedor = tk.Frame(self.root, bg="white")
        frame_contenedor.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")


        self.canvas_arbol = tk.Canvas(frame_contenedor, width=700, height=600, bg="white")
        self.canvas_arbol.grid(row=0, column=0, sticky="nsew")


        scrollbar_y = tk.Scrollbar(frame_contenedor, orient="vertical", command=self.canvas_arbol.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")  # Colocar al borde derecho del canvas

 
        scrollbar_x = tk.Scrollbar(frame_contenedor, orient="horizontal", command=self.canvas_arbol.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")  # Colocar en la parte inferior del canvas


        self.canvas_arbol.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.canvas_arbol.configure(scrollregion=(0, 0, 3000, 3000))

        # Configurar el frame contenedor para redimensionarse correctamente
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
        global visitados
        visitados = set()
        expansiones_totales = 0

        metodos_disponibles = ["IDDFS", "DFS", "BFS", "UCS", "avara", "DFSLI"]
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
                    self.estrategia_label1.config(text="¡Queso encontrado con DFS!")
                    return
                else:
                    self.estrategia_label1.config(text="¡Queso NO encontrado con DFS")

            elif metodo_actual == "BFS":
                self.actualizar_interfaz_estrategia("BFS")
                max_expansiones = self.solicitar_limite_expansiones("BFS")
                resultado, expansiones = self.busqueda_bfs(
                    max_expansiones
                ) 
                expansiones_totales += expansiones
                if resultado:
                    self.estrategia_label1.config(text="¡Queso encontrado con búsqueda BFS")
                    return
                else:
                    self.estrategia_label1.config(text="¡Queso NO encontrado con BFS")
                
            elif metodo_actual == "UCS":
                self.actualizar_interfaz_estrategia("UCS")
                max_expansiones = self.solicitar_limite_expansiones("de Costo Uniforme")
                resultado, expansiones = self.busqueda_costo_uniforme(
                    max_expansiones
                )
                expansiones_totales += expansiones
                if resultado:
                    self.estrategia_label1.config(text="¡Queso encontrado con búsqueda por Costo Uniforme")
                    return
                else:
                    self.estrategia_label1.config(text="¡Queso NO encontrado con UCs")

            elif metodo_actual == "IDDFS":
                self.actualizar_interfaz_estrategia("IDDFS")
                max_expansiones = self.solicitar_limite_expansiones("IDDFS")
                resultado = self.busqueda_iddfs(max_expansiones)
                expansiones_totales += 1
                if resultado:
                    self.estrategia_label1.config(text="¡Queso encontrado con búsqueda IDDFS")
                else:
                    self.estrategia_label1.config(text="¡Queso NO encontrado con IDDFS")   

            elif metodo_actual == "DFSLI":
                self.actualizar_interfaz_estrategia("DFSLI")
                max_expansiones = self.solicitar_limite_expansiones("DFSLI")
                resultado = self.busqueda_dfs_limitada(max_expansiones)
                expansiones_totales += max_expansiones
                if resultado:
                    self.estrategia_label1.config(text="¡Queso encontrado con DFS LIMITADA")
                else:
                    self.estrategia_label1.config(text="¡Queso NO encontrado con DFSLI")

            elif metodo_actual == "avara":
                self.actualizar_interfaz_estrategia("avara")
                max_expansiones = self.solicitar_limite_expansiones("Avara")
                resultado, expansiones = self.busqueda_avara(
                    max_expansiones
                )
                expansiones_totales += expansiones
                if resultado:
                    self.estrategia_label1.config(text="¡Queso encontrado con búsqueda Avara")
                    return    
                else:
                    self.estrategia_label1.config(text="¡Queso NO encontrado con AVARA")

            if not metodos_disponibles:
                print(f"Expansiones totales: {expansiones_totales}")
                
                self.estrategia_label1.config(text="No se encontró el queso después de probar todas las búsquedas")
                break

            # Cambiar al siguiente método disponible
            metodo_actual = random.choice(metodos_disponibles)
            metodos_disponibles.remove(metodo_actual)


    def busqueda_dfs(self, max_expansiones):
        
        global nodos_no_expandidos
        global visitados

        pila_dfs = []
        contador = 0
        nodos_procesados = set()  
       
        if nodos_no_expandidos:
            print(f"Continuando desde nodos no expandidos: {len(nodos_no_expandidos)} nodos")
            # Debug: imprimir información de cada nodo
            for i, nodo in enumerate(nodos_no_expandidos):
                print(f"Nodo {i}: posición={nodo.posicion}, "
                    f"altura={getattr(nodo, 'altura', 'No definida')}, "
                    f"costos={getattr(nodo, 'costos', 'No definido')}")
                
                # Asegurarse de que cada nodo tiene costos y altura definidos
                if not hasattr(nodo, 'costos'):
                    nodo.costos = getattr(nodo, 'altura', 0)
                
                pila_dfs.append(nodo)   
            print(f"Pila DFS después de agregar nodos: {len(pila_dfs)} nodos")
            nodos_no_expandidos = []
        else:
            nodo_inicial = NodoArbol(self.raton_pos)
            nodo_inicial.costos = 0
            nodo_inicial.altura = 0
            pila_dfs.append(nodo_inicial)

        expansiones = 0

        while pila_dfs and expansiones < max_expansiones:
            nodo_actual = pila_dfs.pop()
            posicion_actual = nodo_actual.posicion

            
            if posicion_actual in nodos_procesados:
                print(f"Saltando posición ya procesada: {posicion_actual}")
                continue

            nodos_procesados.add(posicion_actual)
            expansiones += 1
            print(f"Expandiendo nodo {expansiones}: posición {posicion_actual} con altura {nodo_actual.altura}")

            if posicion_actual == self.queso_pos:
                return True, expansiones

            # Generar y evaluar movimientos
            movimientos_validos = []
            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
                
                if (0 <= nueva_posicion[0] < self.rows and 
                    0 <= nueva_posicion[1] < self.cols and 
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in nodos_procesados):
                    
                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nuevo_nodo.altura = nodo_actual.altura + 1
                    nuevo_nodo.costos = nodo_actual.costos + 1
                    nodo_actual.agregar_hijo(nuevo_nodo)
                    movimientos_validos.append(nuevo_nodo)

                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

            # Agregar nodos válidos a la pila en orden inverso
            for nodo in reversed(movimientos_validos):
                pila_dfs.append(nodo)
                print(f"Agregando nuevo nodo: posición {nodo.posicion} con altura {nodo.altura}")

        # Guardar los nodos no expandidos para la siguiente iteración
        nodos_restantes = [nodo for nodo in pila_dfs if nodo.posicion not in nodos_procesados]
        if nodos_restantes:
            nodos_no_expandidos.extend(nodos_restantes)
            print(f"Guardando {len(nodos_restantes)} nodos no expandidos para la siguiente búsqueda")

        if expansiones >= max_expansiones:
            print(f"Límite de expansiones alcanzado ({expansiones})")
        else:
            print("queso no encontrado")
            
        
        return False, expansiones

        
    def busqueda_bfs(self, max_expansiones):
            global nodos_no_expandidos
            global visitados

            cola_bfs = deque()  # Cola principal para BFS
            visitados = set()
            contador = 0

            # Si existen nodos no expandidos, comenzamos con ellos
            if nodos_no_expandidos:
                print("Procesando nodos no expandidos...")
                # Ordenamos por altura pero mantenemos la estructura de nodos
                nodos_no_expandidos.sort(key=lambda nodo: nodo.altura)
                for nodo in nodos_no_expandidos:
                    cola_bfs.append((nodo, nodo.altura))
                nodos_no_expandidos = []  # Limpiamos la lista global
            else:
                nodo_inicial = NodoArbol(self.raton_pos)
                nodo_inicial.costos = 0
                nodo_inicial.altura = 0
                cola_bfs.append((nodo_inicial, 0))
                visitados.add(self.raton_pos)

            expansiones = 0
            nodos_pendientes = []  # Lista temporal para nodos no expandidos

            while cola_bfs:
                # Ordenar la cola principal por altura
                cola_bfs = deque(sorted(cola_bfs, key=lambda x: x[1]))
                
                nodo_actual, profundidad = cola_bfs.popleft()
                posicion_actual = nodo_actual.posicion

                print(f"Expandiendo nodo BFS: {posicion_actual} en nivel {profundidad}")

                # Verificar si encontramos el queso
                if posicion_actual == self.queso_pos:
                    return True, expansiones

                # Generar nodos hijos
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
                    nuevo_nodo.costos = nodo_actual.costos + 1  # Importante para costo uniforme
                    nuevo_nodo.altura = profundidad + 1
                    nodo_actual.agregar_hijo(nuevo_nodo)
                    nodos_hijos.append(nuevo_nodo)
                    
                    visitados.add(nueva_posicion)

                    # Dibujar el nodo y el árbol
                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

                if nodos_hijos:
                    expansiones += 1

                # Verificar si alcanzamos el límite de expansiones
                if expansiones >= max_expansiones:
                    print(f"Límite de expansiones alcanzado en BFS ({expansiones})")
                    # Guardar todos los nodos no expandidos
                    nodos_pendientes.extend([nodo for nodo, _ in cola_bfs])
                    nodos_pendientes.extend(nodos_hijos)
                    # Asegurarnos de que todos los nodos tienen sus costos establecidos
                    for nodo in nodos_pendientes:
                        if not hasattr(nodo, 'costos'):
                            nodo.costos = nodo.altura  # Usar altura como costo si no está definido
                    nodos_no_expandidos = nodos_pendientes
                    return False, expansiones

                # Añadir los hijos a la cola BFS
                for nodo in nodos_hijos:
                    cola_bfs.append((nodo, nodo.altura))

            return False, expansiones


    def busqueda_dfs_limitada(self, profundidad_max):
        global nodos_no_expandidos

        try:
            limite_profu = int(input("Ingrese el límite de profundidad deseado: "))
        except ValueError:
            print("Por favor, ingrese un número entero válido.")
            return self.busqueda_dfs_limitada(profundidad_max)

        pila_dfs = []
        nodos_procesados = set()
        expansiones_realizadas = 0

        # Procesar nodos no expandidos
        if nodos_no_expandidos:
            print(f"Continuando desde nodos no expandidos: {len(nodos_no_expandidos)} nodos")
            for nodo in nodos_no_expandidos:
                pila_dfs.append((nodo, nodo.altura))
            nodos_no_expandidos = []
        else:
            nodo_inicial = NodoArbol(self.raton_pos)
            nodo_inicial.costos = 0
            nodo_inicial.altura = 0
            pila_dfs.append((nodo_inicial, 0))

        while pila_dfs and expansiones_realizadas < profundidad_max:
            nodo_actual, altura = pila_dfs.pop()
            posicion_actual = nodo_actual.posicion

            if posicion_actual in nodos_procesados:
                continue

            nodos_procesados.add(posicion_actual)
            
            if altura < limite_profu:
                expansiones_realizadas += 1

            if posicion_actual == self.queso_pos:
                self.mostrar_camino(nodo_actual)
                return True, expansiones_realizadas

            nodos_hijos = []
            for movimiento in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                if (0 <= nueva_posicion[0] < self.rows and
                    0 <= nueva_posicion[1] < self.cols and
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in nodos_procesados):

                    nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                    nuevo_nodo.altura = altura + 1
                    nuevo_nodo.costos = nodo_actual.costos + 1
                    nodo_actual.agregar_hijo(nuevo_nodo)
                    nodos_hijos.append(nuevo_nodo)

                    self.dibujar_nodo_lab(nueva_posicion)
                    self.dibujar_arbol(nodo_actual, nuevo_nodo)
                    self.root.update()
                    time.sleep(0.5)

            if altura >= limite_profu:
                # Guardar los nodos hijos para explorar más tarde
                nodos_no_expandidos.extend(nodos_hijos)
            else:
                # Agregar los hijos a la pila en orden inverso
                for nodo in reversed(nodos_hijos):
                    pila_dfs.append((nodo, altura + 1))

        # Guardar los nodos no expandidos para la siguiente iteración
        nodos_restantes = [nodo for nodo, _ in pila_dfs if nodo.posicion not in nodos_procesados]
        if nodos_restantes:
            nodos_no_expandidos.extend(nodos_restantes)
            print(f"Guardando {len(nodos_restantes)} nodos no expandidos para la siguiente búsqueda")

        if expansiones_realizadas >= profundidad_max:
            print(f"Límite de expansiones alcanzado: {profundidad_max}")
        else:
            print("queso no encontrado")

        return False, expansiones_realizadas


    def busqueda_costo_uniforme(self, max_expansiones):
            global nodos_no_expandidos
            global visitados

            cola_prioridad = []
            contador = 0
            costos = {}

    
            if nodos_no_expandidos:
                print(f"Continuando desde nodos no expandidos: {len(nodos_no_expandidos)} nodos")
                # Debug: imprimir información de cada nodo
                for i, nodo in enumerate(nodos_no_expandidos):
                    print(f"Nodo {i}: posición={nodo.posicion}, "
                        f"costos={getattr(nodo, 'costos', 'No definido')}, "
                        f"altura={getattr(nodo, 'altura', 'No definida')}")
                    
            
                    if not hasattr(nodo, 'costos'):
                        nodo.costos = getattr(nodo, 'altura', 0)
                    
                    # Agregar el nodo a la cola sin importar si está visitado
                    heapq.heappush(cola_prioridad, (nodo.costos, contador, nodo))
                    costos[nodo.posicion] = nodo.costos
                    contador += 1
                
                print(f"Cola de prioridad después de agregar nodos: {len(cola_prioridad)} nodos")
                nodos_no_expandidos = []
            else:
                nodo_inicial = NodoArbol(self.raton_pos)
                nodo_inicial.costos = 0
                heapq.heappush(cola_prioridad, (0, contador, nodo_inicial))
                costos[self.raton_pos] = 0

            expansiones = 0
            nodos_procesados = set()  # Conjunto para rastrear nodos ya procesados

            while cola_prioridad and expansiones < max_expansiones:
                costo_actual, _, nodo_actual = heapq.heappop(cola_prioridad)
                posicion_actual = nodo_actual.posicion

                # Si ya procesamos este nodo específico o su posición, continuamos
                if posicion_actual in nodos_procesados:
                    print(f"Saltando posición ya procesada: {posicion_actual}")
                    continue

                nodos_procesados.add(posicion_actual)
                expansiones += 1
                print(f"Expandiendo nodo {expansiones}: posición {posicion_actual} con costo {costo_actual}")

                if posicion_actual == self.queso_pos:
                    return True, expansiones

                # Generar y evaluar movimientos
                for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                    nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                    if (0 <= nueva_posicion[0] < self.rows and 
                        0 <= nueva_posicion[1] < self.cols and 
                        self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                        nueva_posicion not in nodos_procesados):

                        nuevo_costo = costo_actual + 1
                        
                        if nueva_posicion not in costos or nuevo_costo < costos[nueva_posicion]:
                            costos[nueva_posicion] = nuevo_costo
                            contador += 1
                            nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                            nuevo_nodo.costos = nuevo_costo
                            nuevo_nodo.altura = nodo_actual.altura + 1
                            nodo_actual.agregar_hijo(nuevo_nodo)
                            
                            heapq.heappush(cola_prioridad, (nuevo_costo, contador, nuevo_nodo))
                            print(f"Agregando nuevo nodo: posición {nueva_posicion} con costo {nuevo_costo}")
                            
                            self.dibujar_nodo_lab(nueva_posicion)
                            self.dibujar_arbol(nodo_actual, nuevo_nodo)
                            self.root.update()
                            time.sleep(0.5)

            # Guardar los nodos no expandidos para la siguiente iteración
            nodos_restantes = [nodo for _, _, nodo in cola_prioridad if nodo.posicion not in nodos_procesados]
            if nodos_restantes:
                nodos_no_expandidos.extend(nodos_restantes)
                print(f"Guardando {len(nodos_restantes)} nodos no expandidos para la siguiente búsqueda")

            if expansiones >= max_expansiones:
                print(f"Límite de expansiones alcanzado ({expansiones})")
            else:
                print("queso no encontrado")
            
            return False, expansiones
    

    def busqueda_iddfs(self, max_expansiones):

            print(f"Iniciando búsqueda IDDFS con límite de expansiones: {max_expansiones}")

            profundidad_max = 1  # Comienza con una profundidad inicial de 1
            expansiones_totales = 0  # Contador de expansiones
            nodo_inicial = NodoArbol(self.raton_pos)  # Nodo raíz del árbol
            visitados = set([self.raton_pos])  # Conjunto de posiciones ya visitadas
            cola_nodos = [(nodo_inicial, 0)]  # Contendrá los nodos finales de cada iteración

            while expansiones_totales < max_expansiones:
                print(f"Iniciando iteración con profundidad máxima: {profundidad_max}")

                nueva_cola = [] 
                for nodo_actual, profundidad in cola_nodos:
                    # Expandir los nodos hijos de los nodos finales generados previamente
                    posicion_actual = nodo_actual.posicion
                    for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                        nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

                        if (0 <= nueva_posicion[0] < self.rows and
                            0 <= nueva_posicion[1] < self.cols and
                            self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                            nueva_posicion not in visitados):

                            # Crear un nuevo nodo hijo
                            nuevo_nodo = NodoArbol(nueva_posicion, nodo_actual)
                            nodo_actual.agregar_hijo(nuevo_nodo)
                            nueva_cola.append((nuevo_nodo, profundidad + 1))
                            visitados.add(nueva_posicion)

        
                            self.dibujar_nodo_lab(nueva_posicion)
                            self.dibujar_arbol(nodo_actual, nuevo_nodo)
                            self.root.update()
                            time.sleep(0.5)

                            expansiones_totales += 1

            
                            if expansiones_totales >= max_expansiones:
                                print(f"Límite máximo de expansiones alcanzado: {max_expansiones}")
                                # Expansión de los últimos nodos creados
                                for nodo_final, _ in nueva_cola:
                                    posicion_final = nodo_final.posicion
                                    for movimiento_final in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                                        nueva_posicion_final = (posicion_final[0] + movimiento_final[0], posicion_final[1] + movimiento_final[1])

                                        # Validar la posición de los hijos finales
                                        if (0 <= nueva_posicion_final[0] < self.rows and
                                            0 <= nueva_posicion_final[1] < self.cols and
                                            self.maze[nueva_posicion_final[0]][nueva_posicion_final[1]] == 0 and
                                            nueva_posicion_final not in visitados):

                                            # Crear y dibujar los hijos de los nodos finales
                                            nodo_hijo_final = NodoArbol(nueva_posicion_final, nodo_final)
                                            nodo_final.agregar_hijo(nodo_hijo_final)
                                            self.dibujar_nodo_lab(nueva_posicion_final)
                                            self.dibujar_arbol(nodo_final, nodo_hijo_final)
                                            self.root.update()
                                            time.sleep(0.5)
                                return True


                cola_nodos = nueva_cola

                # Si no hay nuevos nodos para expandir, se detiene la búsqueda
                if not cola_nodos:
                    print("No hay más nodos para expandir.")
                    break

                # Incrementa la profundidad máxima
                profundidad_max += 1

            print(f"No se encontró el queso después de {expansiones_totales} expansiones con IDDFS.")
            return False


   
    def heuristica_manhattan(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


     
    def busqueda_avara(self, max_expansiones):
        global nodos_no_expandidos

        cola_prioridad = []
        contador = 0
        nodos_procesados = set()  # Reemplaza visitados
        
        # Procesar nodos no expandidos
        if nodos_no_expandidos:
            print(f"Continuando desde nodos no expandidos: {len(nodos_no_expandidos)} nodos")
            for nodo in nodos_no_expandidos:
                heuristica = self.heuristica_manhattan(nodo.posicion, self.queso_pos)
                heapq.heappush(cola_prioridad, (heuristica, contador, nodo))
                contador += 1
            print(f"Cola de prioridad después de agregar nodos: {len(cola_prioridad)} nodos")
            nodos_no_expandidos = []
        else:
            nodo_inicial = NodoArbol(self.raton_pos)
            nodo_inicial.costos = 0
            nodo_inicial.altura = 0
            heuristica_inicial = self.heuristica_manhattan(self.raton_pos, self.queso_pos)
            heapq.heappush(cola_prioridad, (heuristica_inicial, contador, nodo_inicial))

        expansiones = 0

        while cola_prioridad and expansiones < max_expansiones:
            heuristica_actual, _, nodo_actual = heapq.heappop(cola_prioridad)
            posicion_actual = nodo_actual.posicion

            if posicion_actual in nodos_procesados:
                continue

            nodos_procesados.add(posicion_actual)
            expansiones += 1
            print(f"Expandiendo nodo {expansiones}: posición {posicion_actual} con heurística {heuristica_actual}")

            if posicion_actual == self.queso_pos:
                self.estrategia_label1.config(text="Queso encontrado con Busqueda Avara")
                return True, expansiones

            for movimiento in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
                nueva_posicion = (
                    posicion_actual[0] + movimiento[0],
                    posicion_actual[1] + movimiento[1]
                )

                if (0 <= nueva_posicion[0] < self.rows and 
                    0 <= nueva_posicion[1] < self.cols and 
                    self.maze[nueva_posicion[0]][nueva_posicion[1]] == 0 and
                    nueva_posicion not in nodos_procesados):

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

        # Guardar los nodos no expandidos para la siguiente iteración
        nodos_restantes = [nodo for _, _, nodo in cola_prioridad if nodo.posicion not in nodos_procesados]
        if nodos_restantes:
            nodos_no_expandidos.extend(nodos_restantes)
            print(f"Guardando {len(nodos_restantes)} nodos no expandidos para la siguiente búsqueda")

        if expansiones >= max_expansiones:
            print(f"Límite de expansiones alcanzado ({expansiones})")
        else:
            print("No se encontró el queso y no hay más nodos para expandir")
        
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

        
        if nodo_padre not in self.hijos_contador:
            self.hijos_contador[nodo_padre] = 0  # Contador de hijos para el nodo padre

        # Si el nodo hijo ya ha sido agregado, no hacer nada (evitar duplicados)
        if nodo_hijo in self.nodo_padre_coords:
            print(f"El nodo {nodo_hijo} ya existe. Evitando duplicado.")
            return

    
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
            espacio = 300 # Espacio entre los nodos (puedes ajustarlo según el tamaño deseado)
            x_inicio = x_padre - (num_hijos - 1) * espacio // 1/3  # Ajustar para centrar los hijos
        else:
            # Para nodos no raíz, también distribuimos los hijos uniformemente
            num_hijos = len(nodo_padre.hijos)
            espacio = 100 # Espacio entre los nodos hijos
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