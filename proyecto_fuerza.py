import math # Biblioteca matemática estándar para calcular raíces cuadradas y distancias (Pitágoras).
import tkinter as tk # Módulo principal de interfaz gráfica (GUI) para crear ventanas, botones y etiquetas.
from tkinter import ttk, messagebox # 'ttk' provee widgets con estilo moderno. 'messagebox' permite mostrar ventanas emergentes de error o información.

# --- GESTIÓN DE MATPLOTLIB ---
# Matplotlib es la biblioteca que permite dibujar el plano cartesiano y los vectores.
# Se usa un bloque try-except para evitar que el programa falle (crashee) si la computadora no tiene instalada la librería.
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Puente para incrustar gráficas de Matplotlib dentro de una ventana de Tkinter.
    import matplotlib.ticker as ticker # Herramienta para controlar la separación de las medidas (los 'ticks') en los ejes X e Y.
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

# --- FUNCIÓN DE UTILIDAD (UX) ---
def agregar_placeholder(entry, texto):
    """
    Función de Experiencia de Usuario (UX). 
    Inserta un texto gris de ejemplo dentro de una caja de entrada ('entry'). 
    Este texto desaparece automáticamente cuando el usuario hace clic para escribir, 
    y vuelve a aparecer si el usuario deja la caja vacía.
    """
    entry.delete(0, tk.END) 
    entry.insert(0, texto) 
    entry.config(foreground='grey')

    def al_entrar(event): # Evento disparado al hacer clic dentro de la caja.
        if entry.get() == texto:
            entry.delete(0, tk.END)
            entry.config(foreground='black') # Cambia el color a negro para el texto del usuario.

    def al_salir(event): # Evento disparado al hacer clic fuera de la caja.
        if not entry.get():
            entry.insert(0, texto)
            entry.config(foreground='grey')

    # 'bind' conecta las acciones del ratón (<FocusIn> y <FocusOut>) con las funciones internas.
    entry.bind("<FocusIn>", al_entrar)
    entry.bind("<FocusOut>", al_salir)

# --- CLASE PRINCIPAL DE LA APLICACIÓN ---
class AppFuerzaElectrica(tk.Tk):
    """
    Clase principal que hereda de 'tk.Tk', representando la ventana principal de la aplicación.
    Contiene toda la interfaz, las variables de estado y la lógica de negocio (física).
    """
    def __init__(self):
        super().__init__()
        # Configuración básica de la ventana de Windows
        self.title("Calculadora Avanzada - Ley de Coulomb")
        self.geometry("1200x900") # Tamaño inicial. Se hizo más alto para los sliders de zoom.
        self.configure(bg="#e9ecef") # Fondo gris claro para un aspecto limpio.
        
        # Constante dieléctrica del vacío (k) necesaria para la Ley de Coulomb (N·m²/C²)
        self.K = 8.9875517923e9  
        
        # Lista en memoria RAM que guardará todas las cargas puntuales que el usuario agregue.
        self.cargas_fuente = [] 
        
        # --- VARIABLES DE CÁMARA (VISTA) ---
        # Controlan qué parte del plano cartesiano se está mostrando actualmente.
        self.desplazamiento_x = 0.0 # Posición horizontal de la cámara
        self.desplazamiento_y = 0.0 # Posición vertical de la cámara
        self.zoom_actual = 1.0 # Multiplicador de escala. Define qué tan "cerca" o "lejos" está la cámara.
        
        # Llamada a la función que dibuja todos los botones y cuadros.
        self._construir_interfaz()

    def _construir_interfaz(self):
        """
        Método monolítico que construye y posiciona todos los elementos visuales (Widgets) en la ventana.
        Utiliza el gestor de geometría '.pack()' para bloques grandes y '.grid()' para formularios internos.
        """
        # Configuración global de estilos para que los widgets se vean modernos
        estilo = ttk.Style()
        estilo.configure("TFrame", background="#e9ecef")
        estilo.configure("TLabelframe", background="#e9ecef", font=("Helvetica", 11, "bold"))
        estilo.configure("TButton", font=("Helvetica", 10))

        # --- CONTENEDOR PRINCIPAL ---
        marco_principal = ttk.Frame(self)
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # --- PANEL IZQUIERDO: FORMULARIOS Y TABLA ---
        panel_izq = ttk.Frame(marco_principal)
        panel_izq.pack(side="left", fill="y", padx=(0, 20))

        # 1. Cuadro de la Carga Objetivo (La partícula que recibe las fuerzas)
        marco_obj = ttk.LabelFrame(panel_izq, text=" 🎯 Carga Objetivo (Q) ", padding=15)
        marco_obj.pack(fill="x", pady=(0, 15))

        ttk.Label(marco_obj, text="Magnitud (C):").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_q_obj = ttk.Entry(marco_obj, width=18)
        self.ent_q_obj.grid(row=0, column=1, pady=5)

        ttk.Label(marco_obj, text="Posición X (m):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_x_obj = ttk.Entry(marco_obj, width=18)
        self.ent_x_obj.grid(row=1, column=1, pady=5)

        ttk.Label(marco_obj, text="Posición Y (m):").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_y_obj = ttk.Entry(marco_obj, width=18)
        self.ent_y_obj.grid(row=2, column=1, pady=5)

        # 2. Cuadro para añadir Cargas Puntuales Externas
        marco_fuente = ttk.LabelFrame(panel_izq, text=" ⚡ Agregar Cargas Puntuales (n) ", padding=15)
        marco_fuente.pack(fill="x")

        ttk.Label(marco_fuente, text="Magnitud (C):").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_qi = ttk.Entry(marco_fuente, width=18)
        self.ent_qi.grid(row=0, column=1, pady=5)

        ttk.Label(marco_fuente, text="Pos X (m):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_xi = ttk.Entry(marco_fuente, width=18)
        self.ent_xi.grid(row=1, column=1, pady=5)

        ttk.Label(marco_fuente, text="Pos Y (m):").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_yi = ttk.Entry(marco_fuente, width=18)
        self.ent_yi.grid(row=2, column=1, pady=5)

        # Fila de botones de control para la lista
        marco_botones_lista = ttk.Frame(marco_fuente)
        marco_botones_lista.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 'command=self.funcion' asocia el clic del botón a la ejecución de un método de la clase.
        tk.Button(marco_botones_lista, text="➕ Añadir", bg="#0d6efd", fg="white", 
                command=self.agregar_carga, width=12).pack(side="left", padx=2)
        tk.Button(marco_botones_lista, text="🗑️ Eliminar", bg="#dc3545", fg="white", 
                command=self.eliminar_carga, width=12).pack(side="left", padx=2)
        tk.Button(marco_botones_lista, text="🧹 Limpiar Todo", bg="#fd7e14", fg="white", 
                command=self.limpiar_todo, width=12).pack(side="left", padx=2)

        # Rellena los Entry con los textos grises por primera vez.
        self.restaurar_placeholders()

        # 3. Tabla Visual (Treeview) para inventariar las cargas agregadas.
        marco_tabla = ttk.Frame(panel_izq)
        marco_tabla.pack(fill="both", expand=True, pady=10)
        self.tabla = ttk.Treeview(marco_tabla, columns=("q", "x", "y"), show="headings", height=8)
        self.tabla.heading("q", text="Carga (C)")
        self.tabla.heading("x", text="X (m)")
        self.tabla.heading("y", text="Y (m)")
        self.tabla.column("q", width=100, anchor="center")
        self.tabla.column("x", width=70, anchor="center")
        self.tabla.column("y", width=70, anchor="center")
        self.tabla.pack(fill="both", expand=True)

        # --- PANEL DERECHO: RESULTADOS, BOTONES Y GRÁFICA ---
        panel_der = ttk.Frame(marco_principal)
        panel_der.pack(side="right", fill="both", expand=True)

        # Botón maestro de ejecución matemática
        tk.Button(panel_der, text="🚀 CALCULAR FUERZA NETA", bg="#198754", fg="white", 
                font=("Helvetica", 12, "bold"), command=self.calcular_fuerza, pady=10).pack(fill="x")

        # Zona de despliegue de resultados numéricos
        marco_res = ttk.Frame(panel_der)
        marco_res.pack(fill="x", pady=15)
        self.lbl_vector = tk.Label(marco_res, text="Vector Fuerza: < 0.00, 0.00 > N", font=("Courier", 14, "bold"), bg="#e9ecef")
        self.lbl_vector.pack(anchor="w")
        self.lbl_magnitud = tk.Label(marco_res, text="Magnitud Total: 0.00 N", font=("Courier", 14, "bold"), bg="#e9ecef", fg="#0dcaf0")
        self.lbl_magnitud.pack(anchor="w")

        # --- BOTONES DE APOYO TEÓRICO (Pop-ups) ---
        tk.Button(marco_res, text="📝 Ver Fórmula y Procedimiento", bg="#6f42c1", fg="white",
                  font=("Helvetica", 10, "italic"), command=self.mostrar_procedimiento).pack(anchor="w", pady=2)
        
        tk.Button(marco_res, text="📐 Ver Cálculo de Magnitud", bg="#17a2b8", fg="white",
                  font=("Helvetica", 10, "italic"), command=self.mostrar_procedimiento_magnitud).pack(anchor="w", pady=2)

        tk.Button(marco_res, text="🔢 Ver Resolución Paso a Paso", bg="#e83e8c", fg="white",
                  font=("Helvetica", 10, "bold"), command=self.mostrar_resolucion_paso_a_paso).pack(anchor="w", pady=2)

        # --- CONTROLES DE VISTA (Deslizadores / Sliders) ---
        # Scale Horizontal para manejar el Zoom
        self.scroll_zoom = tk.Scale(panel_der, from_=0.1, to=5.0, resolution=0.1,
                                    orient="horizontal", label="🔍 Nivel de Zoom (Rango de Visión)",
                                    command=self.actualizar_desplazamiento)
        self.scroll_zoom.set(1.0) 
        self.scroll_zoom.pack(fill="x", padx=40, pady=(0, 10))

        # Contenedor para integrar la gráfica con el slider vertical
        marco_visualizacion = ttk.Frame(panel_der)
        marco_visualizacion.pack(fill="both", expand=True)

        if MATPLOTLIB_DISPONIBLE:
            # Creación del lienzo matemático
            self.fig = Figure(figsize=(5, 4), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=marco_visualizacion)
            
            # Gráfica a la izquierda
            self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

            # Scale Vertical para mover la cámara en Y
            self.scroll_y = tk.Scale(marco_visualizacion, from_=5, to=-5, resolution=0.1, 
                                     orient="vertical", label="Eje Y", length=300,
                                     command=self.actualizar_desplazamiento)
            self.scroll_y.pack(side="right", fill="y", padx=5)

            # Scale Horizontal para mover la cámara en X
            self.scroll_x = tk.Scale(panel_der, from_=-5, to=5, resolution=0.1, 
                                     orient="horizontal", label="Desplazar Eje X",
                                     command=self.actualizar_desplazamiento)
            self.scroll_x.pack(fill="x", padx=40)

            # Botón rápido para regresar la cámara al centro
            tk.Button(panel_der, text="🔄 Resetear Vista y Zoom", bg="#6c757d", fg="white",
                      font=("Helvetica", 10, "bold"), command=self.reset_posicion).pack(pady=10)

            self.limpiar_grafica()

    # =========================================================
    # FUNCIONES INFORMATIVAS (POPUPS DE TEORÍA)
    # =========================================================
    
    def mostrar_procedimiento(self):
        """
        Dispara un cuadro de diálogo 'showinfo' estático.
        Provee al usuario la fórmula analítica de la Ley de Coulomb 
        y explica brevemente la arquitectura lógica usada en 'calcular_fuerza()'.
        """
        mensaje = (
            "ESTRUCTURA DEL CÁLCULO (LEY DE COULOMB)\n"
            "----------------------------------------\n\n"
            "1. FÓRMULA VECTORIAL:\n"
            "   F = K * (Q * q) / r² * û\n\n"
            "   Donde:\n"
            "   - K: Constante (8.98e9 N·m²/C²)\n"
            "   - Q: Magnitud Carga Objetivo\n"
            "   - q: Magnitud Carga Puntual\n"
            "   - r: Distancia entre cargas\n\n"
            "2. PROCEDIMIENTO DEL CÓDIGO:\n"
            "   a) Calcula dx = XQ - xq  y  dy = YQ - yq\n"
            "   b) Halla la distancia r = sqrt(dx² + dy²)\n"
            "   c) Obtiene la fuerza escalar para cada carga.\n"
            "   d) Aplica el Principio de Superposición:\n"
            "      Suma todas las Fx y todas las Fy."
        )
        messagebox.showinfo("Teoría y Procedimiento", mensaje)

    def mostrar_procedimiento_magnitud(self):
        """
        Dispara un cuadro de diálogo 'showinfo' estático.
        Explica cómo se utiliza el Teorema de Pitágoras sobre las sumatorias vectoriales
        para obtener la hipotenusa (que representa la Magnitud Total Resultante).
        """
        mensaje = (
            "CÁLCULO DE LA MAGNITUD TOTAL (TEOREMA DE PITÁGORAS)\n"
            "---------------------------------------------------\n\n"
            "1. FÓRMULA DE MAGNITUD:\n"
            "   |F| = sqrt( (ΣFx)² + (ΣFy)² )\n\n"
            "2. PROCEDIMIENTO PASO A PASO:\n"
            "   a) Suma de Componentes en X (ΣFx):\n"
            "      Suma todas las fuerzas horizontales considerando su signo\n"
            "      (Negativo = Izquierda, Positivo = Derecha).\n\n"
            "   b) Suma de Componentes en Y (ΣFy):\n"
            "      Suma todas las fuerzas verticales considerando su signo\n"
            "      (Negativo = Abajo, Positivo = Arriba).\n\n"
            "   c) Elevar al Cuadrado:\n"
            "      Se elevan ambas sumas al cuadrado. Esto convierte cualquier\n"
            "      valor negativo en positivo (Ej: -1.34² = 1.81).\n\n"
            "   d) Raíz Cuadrada Final:\n"
            "      Se suman ambos cuadrados y se les aplica la raíz cuadrada\n"
            "      para obtener la longitud real de la flecha (Magnitud Total)."
        )
        messagebox.showinfo("Procedimiento de Magnitud", mensaje)

    def mostrar_resolucion_paso_a_paso(self):
        """
        Tutor Matemático Dinámico.
        Abre una nueva ventana (Toplevel) que funciona como una consola de texto.
        Itera sobre las cargas en memoria y reconstruye paso a paso los cálculos,
        imprimiendo el resultado de la sustitución matemática basándose en los 
        datos reales que el usuario tiene ingresados en ese instante.
        """
        try:
            # Captura de la Carga Objetivo
            Q = float(self.ent_q_obj.get())
            XQ = float(self.ent_x_obj.get())
            YQ = float(self.ent_y_obj.get())

            if not self.cargas_fuente:
                messagebox.showwarning("Aviso", "¡Necesitas agregar al menos una carga fuente para ver el cálculo!")
                return

            # Crear una nueva sub-ventana (Toplevel) para no cerrar la aplicación principal
            ventana_pasos = tk.Toplevel(self)
            ventana_pasos.title("Resolución Matemática Paso a Paso")
            ventana_pasos.geometry("700x500")
            ventana_pasos.configure(bg="#f8f9fa")

            # Construcción de un 'Text' con Scrollbar para mostrar texto largo
            marco_texto = ttk.Frame(ventana_pasos)
            marco_texto.pack(fill="both", expand=True, padx=15, pady=15)
            
            scroll_texto = ttk.Scrollbar(marco_texto)
            scroll_texto.pack(side="right", fill="y")
            
            caja_texto = tk.Text(marco_texto, font=("Consolas", 11), bg="white", yscrollcommand=scroll_texto.set)
            caja_texto.pack(side="left", fill="both", expand=True)
            scroll_texto.config(command=caja_texto.yview)

            # Construcción dinámica del string que contiene la demostración matemática
            texto = f"=================================================\n"
            texto += f"     CÁLCULO DINÁMICO DE LA FUERZA NETA\n"
            texto += f"=================================================\n\n"
            texto += f"DATOS INICIALES:\n"
            texto += f"- Constante K = {self.K:.4e} N·m²/C²\n"
            texto += f"- Carga Objetivo (Q) = {Q:.4e} C en la posición ({XQ}, {YQ})\n\n"

            fx_total = 0.0
            fy_total = 0.0

            # Iterar simulando el cálculo para documentarlo
            for i, carga in enumerate(self.cargas_fuente, 1):
                q_i = carga['q']
                x_i = carga['x']
                y_i = carga['y']
                
                texto += f"-------------------------------------------------\n"
                texto += f" INTERACCIÓN CON LA CARGA FUENTE #{i}\n"
                texto += f"-------------------------------------------------\n"
                texto += f"Carga q{i} = {q_i:.4e} C en la posición ({x_i}, {y_i})\n\n"
                
                dx = XQ - x_i
                dy = YQ - y_i
                r_cuadrado = dx**2 + dy**2
                r = math.sqrt(r_cuadrado)
                
                if r == 0: # Prevención de división por cero
                    texto += "¡ADVERTENCIA! Las cargas están superpuestas (Distancia r = 0).\n"
                    texto += "El cálculo se detiene para esta carga.\n\n"
                    continue

                texto += f"Paso 1: Calcular vector de distancia (dx, dy)\n"
                texto += f"  dx = X_obj - X_fuente = {XQ} - ({x_i}) = {dx} m\n"
                texto += f"  dy = Y_obj - Y_fuente = {YQ} - ({y_i}) = {dy} m\n\n"
                
                texto += f"Paso 2: Calcular distancia radial (r)\n"
                texto += f"  r² = ({dx})² + ({dy})² = {r_cuadrado:.4e} m²\n"
                texto += f"  r = √({r_cuadrado:.4e}) = {r:.4e} m\n\n"
                
                factor_fuerza = (self.K * Q * q_i) / (r_cuadrado * r)
                fx = factor_fuerza * dx
                fy = factor_fuerza * dy
                
                texto += f"Paso 3: Aplicar Ley de Coulomb y descomponer (F = k*Q*q/r³ * d)\n"
                texto += f"  Fx{i} = {fx:.6e} N\n"
                texto += f"  Fy{i} = {fy:.6e} N\n\n"
                
                fx_total += fx
                fy_total += fy

            # Cierre de la demostración con la resultante y magnitud
            texto += f"=================================================\n"
            texto += f" SUMATORIA FINAL (PRINCIPIO DE SUPERPOSICIÓN)\n"
            texto += f"=================================================\n"
            texto += f"ΣFx (Fuerza Total en X) = {fx_total:.6e} N\n"
            texto += f"ΣFy (Fuerza Total en Y) = {fy_total:.6e} N\n\n"
            
            magnitud = math.sqrt(fx_total**2 + fy_total**2)
            texto += f"Paso 4: Calcular Magnitud Total (Pitágoras)\n"
            texto += f"  |F| = √((ΣFx)² + (ΣFy)²)\n"
            texto += f"  |F| = √({fx_total:.4e}² + {fy_total:.4e}²)\n"
            texto += f"  |F| = {magnitud:.6e} N\n"
            texto += f"=================================================\n"

            # Insertar texto final y bloquear edición (Read-Only)
            caja_texto.insert(tk.END, texto)
            caja_texto.config(state=tk.DISABLED)

        except ValueError:
            messagebox.showerror("Error de Datos", "Por favor, asegúrate de que los campos de la Carga Objetivo tengan números válidos.")

    # =========================================================
    # LÓGICA DE CONTROL VISUAL DE LA GRÁFICA (CÁMARA)
    # =========================================================

    def actualizar_desplazamiento(self, _):
        """
        Función atada (Callback) a los movimientos de los 3 Sliders (X, Y, Zoom).
        Se dispara automáticamente cada vez que el usuario mueve una barra.
        Lee los valores de los Sliders y ajusta los límites (xlim, ylim) del plano cartesiano.
        """
        if MATPLOTLIB_DISPONIBLE:
            # 1. Leer estado actual de los sliders
            self.desplazamiento_x = float(self.scroll_x.get())
            self.desplazamiento_y = float(self.scroll_y.get())
            self.zoom_actual = float(self.scroll_zoom.get())
            
            # 2. Definir ventana de visión basada en el centro y el nivel de zoom
            self.ax.set_xlim(self.desplazamiento_x - self.zoom_actual, self.desplazamiento_x + self.zoom_actual)
            self.ax.set_ylim(self.desplazamiento_y - self.zoom_actual, self.desplazamiento_y + self.zoom_actual)
            
            # 3. Adaptar la separación numérica de la cuadrícula para que no se vea amontonada al alejar.
            intervalo = self.zoom_actual / 5.0
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
            self.ax.yaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
            
            # 4. Refrescar la pantalla
            self.canvas.draw()

    def reset_posicion(self):
        """Devuelve los desplazadores (Sliders) y el zoom a sus valores predeterminados (Centro: 0,0 - Zoom: 1x)."""
        if MATPLOTLIB_DISPONIBLE:
            self.scroll_x.set(0)
            self.scroll_y.set(0)
            self.scroll_zoom.set(1.0)
            self.actualizar_desplazamiento(None) # Fuerza a redibujar la gráfica con los nuevos valores.

    def restaurar_placeholders(self):
        """Método de apoyo que llama a la función global 'agregar_placeholder' para todas las cajas simultáneamente."""
        agregar_placeholder(self.ent_q_obj, "1e-6")
        agregar_placeholder(self.ent_x_obj, "0")
        agregar_placeholder(self.ent_y_obj, "0")
        agregar_placeholder(self.ent_qi, "Ej: -5e-6")
        agregar_placeholder(self.ent_xi, "0.5")
        agregar_placeholder(self.ent_yi, "0.5")

    # =========================================================
    # LÓGICA DE NEGOCIO (PROCESAMIENTO DE DATOS Y FÍSICA)
    # =========================================================

    def limpiar_todo(self):
        """
        Función del Botón Naranja ('Limpiar Todo').
        Ejecuta un reseteo maestro de la aplicación entera, borrando listas,
        limpiando la vista de la tabla y reiniciando cámara, resultados y placeholders.
        """
        self.cargas_fuente = [] # Vacía la memoria
        # Borra todos los elementos visuales de la tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.restaurar_placeholders()
        # Resetea resultados a 0
        self.lbl_vector.config(text="Vector Fuerza: < 0.00, 0.00 > N")
        self.lbl_magnitud.config(text="Magnitud Total: 0.00 N")
        if MATPLOTLIB_DISPONIBLE:
            self.reset_posicion()
            self.limpiar_grafica()
            self.canvas.draw()

    def agregar_carga(self):
        """
        Lee el formulario inferior. Si los datos son números válidos,
        los inserta en el TreeView (Tabla) y los añade a la lista interna 'self.cargas_fuente' 
        como un diccionario con una ID única.
        """
        try:
            q = float(self.ent_qi.get())
            x = float(self.ent_xi.get())
            y = float(self.ent_yi.get())
            
            # Insertar en tabla devuelve un ID único generado por Tkinter
            item_id = self.tabla.insert("", "end", values=(f"{q:.2e}", x, y))
            
            # Se guarda ese ID en el diccionario para poder vincular la tabla con la memoria
            self.cargas_fuente.append({'id': item_id, 'q': q, 'x': x, 'y': y})
            
            # Se limpian SÓLO las cajas de carga fuente para el siguiente registro
            agregar_placeholder(self.ent_qi, "Ej: -5e-6")
            agregar_placeholder(self.ent_xi, "0.5")
            agregar_placeholder(self.ent_yi, "0.5")
        except ValueError:
            messagebox.showerror("Error", "Ingresa números válidos.")

    def eliminar_carga(self):
        """
        Lee la selección actual de la tabla. Utiliza el ID único para eliminar
        tanto el registro visual como el registro de la lista en memoria mediante comprensión de listas.
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una carga de la tabla para eliminarla.")
            return
        for item_id in seleccion:
            self.tabla.delete(item_id)
            # Filtra la lista reteniendo solo los elementos cuyo ID no coincida con el borrado
            self.cargas_fuente = [c for c in self.cargas_fuente if c['id'] != item_id]

    def calcular_fuerza(self):
        """
        MÉTODO CORE MATEMÁTICO:
        1. Lee la carga central.
        2. Aplica Coulomb mediante un ciclo For que recorre las n cargas.
        3. Realiza la sumatoria vectorial (ΣFx, ΣFy).
        4. Envía resultados a las etiquetas y manda la orden de dibujar la flecha.
        """
        try:
            Q, XQ, YQ = float(self.ent_q_obj.get()), float(self.ent_x_obj.get()), float(self.ent_y_obj.get())
            if not self.cargas_fuente: return # Bloqueo si no hay cargas externas
            
            fx_total = fy_total = 0.0
            
            for carga in self.cargas_fuente:
                dx, dy = XQ - carga['x'], YQ - carga['y']
                r_cuadrado = dx**2 + dy**2
                r = math.sqrt(r_cuadrado)
                if r == 0: continue # Evita error matemático Div/0
                
                # Descomposición vectorial implícita
                factor_fuerza = (self.K * Q * carga['q']) / (r_cuadrado * r)
                fx_total += factor_fuerza * dx
                fy_total += factor_fuerza * dy
                
            magnitud = math.sqrt(fx_total**2 + fy_total**2)
            
            # Actualiza la vista de texto (.4e formatea a Notación Científica con 4 decimales)
            self.lbl_vector.config(text=f"Vector Fuerza: < {fx_total:.4e}, {fy_total:.4e} > N")
            self.lbl_magnitud.config(text=f"Magnitud Total: {magnitud:.4e} N")
            
            # Activa el renderizado gráfico si Matplotlib está operando
            if MATPLOTLIB_DISPONIBLE:
                self.dibujar_vectores(XQ, YQ, fx_total, fy_total)
        except ValueError:
            messagebox.showerror("Error", "Revisa los datos numéricos.")

    def limpiar_grafica(self):
        """
        Pone el plano cartesiano en "blanco", redibujando ejes centrales, 
        cuadrícula y configurando los límites actuales dictados por los Sliders.
        """
        self.ax.clear()
        self.ax.set_title("Plano Cartesiano de Cargas")
        self.ax.set_xlabel("Eje X (m)")
        self.ax.set_ylabel("Eje Y (m)")
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.ax.axhline(0, color='black', linewidth=0.5) # Línea central X
        self.ax.axvline(0, color='black', linewidth=0.5) # Línea central Y
        
        # Ajuste adaptativo de la cuadrícula basado en el Zoom
        intervalo = self.zoom_actual / 5.0
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
        
        # Recupera los límites fijados por la cámara
        self.ax.set_xlim(self.desplazamiento_x - self.zoom_actual, self.desplazamiento_x + self.zoom_actual)
        self.ax.set_ylim(self.desplazamiento_y - self.zoom_actual, self.desplazamiento_y + self.zoom_actual)
        
        self.canvas.draw()

    def dibujar_vectores(self, xq, yq, fx, fy):
        """
        Renderizador Final. 
        Itera sobre 'cargas_fuente' dibujando círculos azules/rojos.
        Dibuja la estrella central.
        Finalmente, pinta la flecha escalada direccional que representa la Fuerza Neta.
        """
        self.limpiar_grafica()
        
        # Dibujar n cargas
        for c in self.cargas_fuente:
            color = 'red' if c['q'] > 0 else 'blue' # Condicional corto para color
            self.ax.scatter(c['x'], c['y'], color=color, s=100, zorder=5) # scatter pinta puntos
            self.ax.text(c['x'], c['y']+0.05, f" {c['q']:.1e}C", fontsize=9, ha='center') # Etiqueta numérica
            
        # Dibujar Carga Objetivo
        self.ax.scatter(xq, yq, color='green', s=150, marker='*', zorder=6, label='Objetivo')
        
        # Dibujar Vector de Fuerza Neta (Si no es cero)
        if fx != 0 or fy != 0:
            # Algoritmo de escalado: Asegura que la flecha siempre mida 1/3 del nivel de zoom actual,
            # independientemente de si la fuerza es de millones de Newtons o milésimas.
            escala = max(abs(fx), abs(fy)) / (self.zoom_actual * 0.3)
            self.ax.arrow(xq, yq, fx/escala, fy/escala, 
                        head_width=self.zoom_actual*0.05, head_length=self.zoom_actual*0.08, 
                        fc='black', ec='black', zorder=10, label='Fuerza Neta')
                        
        self.ax.legend(loc="upper right") # Añadir leyenda en la esquina
        self.canvas.draw()

# --- EJECUCIÓN DEL PROGRAMA ---
# Este bloque verifica si el archivo se está ejecutando directamente y arranca el loop de la interfaz.
if __name__ == "__main__":
    app = AppFuerzaElectrica()
    app.mainloop() # Bucle infinito que mantiene viva la ventana y "escucha" clics y teclas.