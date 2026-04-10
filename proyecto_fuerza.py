import math # Para operaciones de raíces cuadradas y potencias
import tkinter as tk # Biblioteca base para la interfaz de usuario
from tkinter import ttk, messagebox # Componentes modernos y ventanas de mensajes

# Gestión de Matplotlib para renderizar la gráfica científica
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.ticker as ticker # Para manejar las medidas de los ejes
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

# --- FUNCIÓN PARA LOS PLACEHOLDERS (GUI) ---
def agregar_placeholder(entry, texto):
    """Inserta texto sugerido en gris que desaparece al escribir."""
    entry.delete(0, tk.END) 
    entry.insert(0, texto) 
    entry.config(foreground='grey')

    def al_entrar(event): # Borra el ejemplo al hacer clic
        if entry.get() == texto:
            entry.delete(0, tk.END)
            entry.config(foreground='black')

    def al_salir(event): # Restaura el ejemplo si la caja queda vacía
        if not entry.get():
            entry.insert(0, texto)
            entry.config(foreground='grey')

    entry.bind("<FocusIn>", al_entrar)
    entry.bind("<FocusOut>", al_salir)

# --- CLASE PRINCIPAL DE LA APLICACIÓN ---
class AppFuerzaElectrica(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora Avanzada - Ley de Coulomb")
        self.geometry("1200x900") # Espacio extra para el control de zoom
        self.configure(bg="#e9ecef") 
        
        self.K = 8.9875517923e9  
        self.cargas_fuente = [] 
        
        # Variables de control para el visor
        self.desplazamiento_x = 0.0
        self.desplazamiento_y = 0.0
        self.zoom_actual = 1.0 # Variable para controlar el zoom
        
        self._construir_interfaz()

    def _construir_interfaz(self):
        """Configura visualmente toda la ventana."""
        estilo = ttk.Style()
        estilo.configure("TFrame", background="#e9ecef")
        estilo.configure("TLabelframe", background="#e9ecef", font=("Helvetica", 11, "bold"))
        estilo.configure("TButton", font=("Helvetica", 10))

        marco_principal = ttk.Frame(self)
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        panel_izq = ttk.Frame(marco_principal)
        panel_izq.pack(side="left", fill="y", padx=(0, 20))

        # 1. Formulario de la Carga Objetivo
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

        # 2. Formulario para añadir Cargas Fuente
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

        # Botones para gestionar la lista
        marco_botones_lista = ttk.Frame(marco_fuente)
        marco_botones_lista.grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Button(marco_botones_lista, text="➕ Añadir", bg="#0d6efd", fg="white", 
                command=self.agregar_carga, width=12).pack(side="left", padx=2)
        tk.Button(marco_botones_lista, text="🗑️ Eliminar", bg="#dc3545", fg="white", 
                command=self.eliminar_carga, width=12).pack(side="left", padx=2)
        tk.Button(marco_botones_lista, text="🧹 Limpiar Todo", bg="#fd7e14", fg="white", 
                command=self.limpiar_todo, width=12).pack(side="left", padx=2)

        self.restaurar_placeholders()

        # 3. Tabla visual
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

        # Panel Derecho
        panel_der = ttk.Frame(marco_principal)
        panel_der.pack(side="right", fill="both", expand=True)

        # Botón de cálculo general
        tk.Button(panel_der, text="🚀 CALCULAR FUERZA NETA", bg="#198754", fg="white", 
                font=("Helvetica", 12, "bold"), command=self.calcular_fuerza, pady=10).pack(fill="x")

        marco_res = ttk.Frame(panel_der)
        marco_res.pack(fill="x", pady=15)
        self.lbl_vector = tk.Label(marco_res, text="Vector Fuerza: < 0.00, 0.00 > N", font=("Courier", 14, "bold"), bg="#e9ecef")
        self.lbl_vector.pack(anchor="w")
        self.lbl_magnitud = tk.Label(marco_res, text="Magnitud Total: 0.00 N", font=("Courier", 14, "bold"), bg="#e9ecef", fg="#0dcaf0")
        self.lbl_magnitud.pack(anchor="w")

        # --- BOTONES TEÓRICOS ---
        tk.Button(marco_res, text="📝 Ver Fórmula y Procedimiento", bg="#6f42c1", fg="white",
                  font=("Helvetica", 10, "italic"), command=self.mostrar_procedimiento).pack(anchor="w", pady=2)
        
        tk.Button(marco_res, text="📐 Ver Cálculo de Magnitud", bg="#17a2b8", fg="white",
                  font=("Helvetica", 10, "italic"), command=self.mostrar_procedimiento_magnitud).pack(anchor="w", pady=2)

        # --- NUEVO: BOTÓN DE RESOLUCIÓN PASO A PASO ---
        tk.Button(marco_res, text="🔢 Ver Resolución Paso a Paso", bg="#e83e8c", fg="white",
                  font=("Helvetica", 10, "bold"), command=self.mostrar_resolucion_paso_a_paso).pack(anchor="w", pady=2)

        # Deslizador de Zoom
        self.scroll_zoom = tk.Scale(panel_der, from_=0.1, to=5.0, resolution=0.1,
                                    orient="horizontal", label="🔍 Nivel de Zoom (Rango de Visión)",
                                    command=self.actualizar_desplazamiento)
        self.scroll_zoom.set(1.0) # Zoom inicial estándar
        self.scroll_zoom.pack(fill="x", padx=40, pady=(0, 10))

        # Contenedor para Gráfica y Desplazador Y
        marco_visualizacion = ttk.Frame(panel_der)
        marco_visualizacion.pack(fill="both", expand=True)

        if MATPLOTLIB_DISPONIBLE:
            self.fig = Figure(figsize=(5, 4), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=marco_visualizacion)
            
            # Gráfica a la izquierda
            self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

            # Desplazador Eje Y (Derecha de la gráfica)
            self.scroll_y = tk.Scale(marco_visualizacion, from_=5, to=-5, resolution=0.1, 
                                     orient="vertical", label="Eje Y", length=300,
                                     command=self.actualizar_desplazamiento)
            self.scroll_y.pack(side="right", fill="y", padx=5)

            # Desplazador Eje X (Debajo de la gráfica)
            self.scroll_x = tk.Scale(panel_der, from_=-5, to=5, resolution=0.1, 
                                     orient="horizontal", label="Desplazar Eje X",
                                     command=self.actualizar_desplazamiento)
            self.scroll_x.pack(fill="x", padx=40)

            # Botón Reset Posición
            tk.Button(panel_der, text="🔄 Resetear Vista y Zoom", bg="#6c757d", fg="white",
                      font=("Helvetica", 10, "bold"), command=self.reset_posicion).pack(pady=10)

            self.limpiar_grafica()

    # --- FUNCIONES INFORMATIVAS (TEORÍA) ---
    def mostrar_procedimiento(self):
        """Muestra una ventana informativa con la base teórica del cálculo."""
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
        """Muestra una ventana informativa detallando el Teorema de Pitágoras para la magnitud."""
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

    # --- NUEVA FUNCIÓN: TUTOR MATEMÁTICO DINÁMICO ---
    def mostrar_resolucion_paso_a_paso(self):
        """Extrae los datos ingresados y genera una ventana con las matemáticas resueltas."""
        try:
            Q = float(self.ent_q_obj.get())
            XQ = float(self.ent_x_obj.get())
            YQ = float(self.ent_y_obj.get())

            if not self.cargas_fuente:
                messagebox.showwarning("Aviso", "¡Necesitas agregar al menos una carga fuente para ver el cálculo!")
                return

            # Crear una nueva sub-ventana (Toplevel) para mostrar el texto largo
            ventana_pasos = tk.Toplevel(self)
            ventana_pasos.title("Resolución Matemática Paso a Paso")
            ventana_pasos.geometry("700x500")
            ventana_pasos.configure(bg="#f8f9fa")

            # Área de texto con barra de desplazamiento
            marco_texto = ttk.Frame(ventana_pasos)
            marco_texto.pack(fill="both", expand=True, padx=15, pady=15)
            
            scroll_texto = ttk.Scrollbar(marco_texto)
            scroll_texto.pack(side="right", fill="y")
            
            caja_texto = tk.Text(marco_texto, font=("Consolas", 11), bg="white", yscrollcommand=scroll_texto.set)
            caja_texto.pack(side="left", fill="both", expand=True)
            scroll_texto.config(command=caja_texto.yview)

            # Construcción dinámica del texto matemático
            texto = f"=================================================\n"
            texto += f"     CÁLCULO DINÁMICO DE LA FUERZA NETA\n"
            texto += f"=================================================\n\n"
            texto += f"DATOS INICIALES:\n"
            texto += f"- Constante K = {self.K:.4e} N·m²/C²\n"
            texto += f"- Carga Objetivo (Q) = {Q:.4e} C en la posición ({XQ}, {YQ})\n\n"

            fx_total = 0.0
            fy_total = 0.0

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
                
                if r == 0:
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

            # Insertar texto y bloquear edición
            caja_texto.insert(tk.END, texto)
            caja_texto.config(state=tk.DISABLED)

        except ValueError:
            messagebox.showerror("Error de Datos", "Por favor, asegúrate de que los campos de la Carga Objetivo tengan números válidos.")

    def actualizar_desplazamiento(self, _):
        """Actualiza la vista de la gráfica según los desplazadores y el zoom."""
        if MATPLOTLIB_DISPONIBLE:
            self.desplazamiento_x = float(self.scroll_x.get())
            self.desplazamiento_y = float(self.scroll_y.get())
            self.zoom_actual = float(self.scroll_zoom.get())
            
            # El zoom define el rango de visión alrededor del centro
            self.ax.set_xlim(self.desplazamiento_x - self.zoom_actual, self.desplazamiento_x + self.zoom_actual)
            self.ax.set_ylim(self.desplazamiento_y - self.zoom_actual, self.desplazamiento_y + self.zoom_actual)
            
            # Adaptar los ticks para que no se amontonen al hacer zoom out
            intervalo = self.zoom_actual / 5.0
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
            self.ax.yaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
            
            self.canvas.draw()

    def reset_posicion(self):
        """Devuelve los desplazadores y el zoom a la posición inicial."""
        if MATPLOTLIB_DISPONIBLE:
            self.scroll_x.set(0)
            self.scroll_y.set(0)
            self.scroll_zoom.set(1.0)
            self.actualizar_desplazamiento(None)

    def restaurar_placeholders(self):
        """Asigna los textos de ejemplo a todas las cajas."""
        agregar_placeholder(self.ent_q_obj, "1e-6")
        agregar_placeholder(self.ent_x_obj, "0")
        agregar_placeholder(self.ent_y_obj, "0")
        agregar_placeholder(self.ent_qi, "Ej: -5e-6")
        agregar_placeholder(self.ent_xi, "0.5")
        agregar_placeholder(self.ent_yi, "0.5")

    def limpiar_todo(self):
        """Borra todos los datos, la tabla, los resultados y reinicia la gráfica y su posición."""
        self.cargas_fuente = []
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.restaurar_placeholders()
        self.lbl_vector.config(text="Vector Fuerza: < 0.00, 0.00 > N")
        self.lbl_magnitud.config(text="Magnitud Total: 0.00 N")
        if MATPLOTLIB_DISPONIBLE:
            self.reset_posicion()
            self.limpiar_grafica()
            self.canvas.draw()

    def agregar_carga(self):
        try:
            q = float(self.ent_qi.get())
            x = float(self.ent_xi.get())
            y = float(self.ent_yi.get())
            item_id = self.tabla.insert("", "end", values=(f"{q:.2e}", x, y))
            self.cargas_fuente.append({'id': item_id, 'q': q, 'x': x, 'y': y})
            agregar_placeholder(self.ent_qi, "Ej: -5e-6")
            agregar_placeholder(self.ent_xi, "0.5")
            agregar_placeholder(self.ent_yi, "0.5")
        except ValueError:
            messagebox.showerror("Error", "Ingresa números válidos.")

    def eliminar_carga(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una carga de la tabla para eliminarla.")
            return
        for item_id in seleccion:
            self.tabla.delete(item_id)
            self.cargas_fuente = [c for c in self.cargas_fuente if c['id'] != item_id]

    def calcular_fuerza(self):
        try:
            Q, XQ, YQ = float(self.ent_q_obj.get()), float(self.ent_x_obj.get()), float(self.ent_y_obj.get())
            if not self.cargas_fuente: return
            fx_total = fy_total = 0.0
            for carga in self.cargas_fuente:
                dx, dy = XQ - carga['x'], YQ - carga['y']
                r_cuadrado = dx**2 + dy**2
                r = math.sqrt(r_cuadrado)
                if r == 0: continue
                factor_fuerza = (self.K * Q * carga['q']) / (r_cuadrado * r)
                fx_total += factor_fuerza * dx
                fy_total += factor_fuerza * dy
            magnitud = math.sqrt(fx_total**2 + fy_total**2)
            self.lbl_vector.config(text=f"Vector Fuerza: < {fx_total:.4e}, {fy_total:.4e} > N")
            self.lbl_magnitud.config(text=f"Magnitud Total: {magnitud:.4e} N")
            if MATPLOTLIB_DISPONIBLE:
                self.dibujar_vectores(XQ, YQ, fx_total, fy_total)
        except ValueError:
            messagebox.showerror("Error", "Revisa los datos numéricos.")

    def limpiar_grafica(self):
        """Reinicia los ejes y cuadrícula del gráfico."""
        self.ax.clear()
        self.ax.set_title("Plano Cartesiano de Cargas")
        self.ax.set_xlabel("Eje X (m)")
        self.ax.set_ylabel("Eje Y (m)")
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.ax.axhline(0, color='black', linewidth=0.5)
        self.ax.axvline(0, color='black', linewidth=0.5)
        
        # Unidades de medida adaptables al zoom
        intervalo = self.zoom_actual / 5.0
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
        
        self.ax.set_xlim(self.desplazamiento_x - self.zoom_actual, self.desplazamiento_x + self.zoom_actual)
        self.ax.set_ylim(self.desplazamiento_y - self.zoom_actual, self.desplazamiento_y + self.zoom_actual)
        self.canvas.draw()

    def dibujar_vectores(self, xq, yq, fx, fy):
        self.limpiar_grafica()
        for c in self.cargas_fuente:
            color = 'red' if c['q'] > 0 else 'blue'
            self.ax.scatter(c['x'], c['y'], color=color, s=100, zorder=5)
            self.ax.text(c['x'], c['y']+0.05, f" {c['q']:.1e}C", fontsize=9, ha='center')
        self.ax.scatter(xq, yq, color='green', s=150, marker='*', zorder=6, label='Objetivo')
        if fx != 0 or fy != 0:
            escala = max(abs(fx), abs(fy)) / (self.zoom_actual * 0.3)
            self.ax.arrow(xq, yq, fx/escala, fy/escala, head_width=self.zoom_actual*0.05, 
                        head_length=self.zoom_actual*0.08, fc='black', ec='black', zorder=10)
        self.canvas.draw()

if __name__ == "__main__":
    app = AppFuerzaElectrica()
    app.mainloop()