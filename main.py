import math # Biblioteca matemática estándar.
import tkinter as tk # Módulo principal de interfaz gráfica (GUI).
from tkinter import ttk, messagebox # Componentes modernos y ventanas de mensajes.

# --- IMPORTACIONES DE LOS MÓDULOS CREADOS ---
from utils import agregar_placeholder
from logica_fisica import calcular_fuerza_neta_matematica, generar_texto_paso_a_paso

# --- GESTIÓN DE MATPLOTLIB ---
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
    import matplotlib.ticker as ticker 
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

# --- CLASE PRINCIPAL DE LA APLICACIÓN (VISTA/CONTROLADOR) ---
class AppFuerzaElectrica(tk.Tk):
    """
    Clase principal que hereda de 'tk.Tk', representando la ventana principal de la aplicación.
    Contiene toda la interfaz gráfica y delega los cálculos pesados a 'logica_fisica.py'.
    """
    def __init__(self):
        super().__init__()
        # Configuración básica de la ventana de Windows
        self.title("Calculadora Avanzada - Ley de Coulomb")
        self.geometry("1200x900") 
        self.configure(bg="#e9ecef") 
        
        self.K = 8.9875517923e9  
        self.cargas_fuente = [] 
        
        # --- VARIABLES DE CÁMARA (VISTA) ---
        self.desplazamiento_x = 0.0 
        self.desplazamiento_y = 0.0 
        self.zoom_actual = 1.0 
        
        self._construir_interfaz()

    # =========================================================
    # CONSTRUCCIÓN DE LA INTERFAZ GRÁFICA
    # =========================================================
    def _construir_interfaz(self):
        """
        Método monolítico que construye y posiciona todos los elementos visuales.
        """
        estilo = ttk.Style()
        estilo.configure("TFrame", background="#e9ecef")
        estilo.configure("TLabelframe", background="#e9ecef", font=("Helvetica", 11, "bold"))
        estilo.configure("TButton", font=("Helvetica", 10))

        marco_principal = ttk.Frame(self)
        marco_principal.pack(fill="both", expand=True, padx=20, pady=20)

        panel_izq = ttk.Frame(marco_principal)
        panel_izq.pack(side="left", fill="y", padx=(0, 20))

        # 1. Cuadro de la Carga Objetivo
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

        marco_botones_lista = ttk.Frame(marco_fuente)
        marco_botones_lista.grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Button(marco_botones_lista, text="➕ Añadir", bg="#0d6efd", fg="white", 
                command=self.agregar_carga, width=12).pack(side="left", padx=2)
        tk.Button(marco_botones_lista, text="🗑️ Eliminar", bg="#dc3545", fg="white", 
                command=self.eliminar_carga, width=12).pack(side="left", padx=2)
        tk.Button(marco_botones_lista, text="🧹 Limpiar Todo", bg="#fd7e14", fg="white", 
                command=self.limpiar_todo, width=12).pack(side="left", padx=2)

        self.restaurar_placeholders()

        # Botones de apoyo teórico
        marco_teoria = ttk.Frame(panel_izq)
        marco_teoria.pack(fill="x", pady=(5, 10))
        
        tk.Button(marco_teoria, text="📝 Ver Fórmula y Procedimiento", bg="#6f42c1", fg="white",
                font=("Helvetica", 10, "italic"), command=self.mostrar_procedimiento).pack(fill="x", pady=2)
        
        tk.Button(marco_teoria, text="📐 Ver Cálculo de Magnitud", bg="#17a2b8", fg="white",
                font=("Helvetica", 10, "italic"), command=self.mostrar_procedimiento_magnitud).pack(fill="x", pady=2)

        tk.Button(marco_teoria, text="🔢 Ver Resolución Paso a Paso", bg="#e83e8c", fg="white",
                font=("Helvetica", 10, "bold"), command=self.mostrar_resolucion_paso_a_paso).pack(fill="x", pady=2)

        # 3. Tabla Visual
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

        panel_der = ttk.Frame(marco_principal)
        panel_der.pack(side="right", fill="both", expand=True)

        tk.Button(panel_der, text="🚀 CALCULAR FUERZA NETA", bg="#198754", fg="white", 
                font=("Helvetica", 12, "bold"), command=self.calcular_fuerza, pady=10).pack(fill="x")

        marco_res = ttk.Frame(panel_der)
        marco_res.pack(fill="x", pady=15)
        self.lbl_vector = tk.Label(marco_res, text="Vector Fuerza: < 0.00, 0.00 > N", font=("Courier", 14, "bold"), bg="#e9ecef")
        self.lbl_vector.pack(anchor="w")
        self.lbl_magnitud = tk.Label(marco_res, text="Magnitud Total: 0.00 N", font=("Courier", 14, "bold"), bg="#e9ecef", fg="#0dcaf0")
        self.lbl_magnitud.pack(anchor="w")

        self.scroll_zoom = tk.Scale(panel_der, from_=0.1, to=5.0, resolution=0.1,
                                    orient="horizontal", label="🔍 Nivel de Zoom (Rango de Visión)",
                                    command=self.actualizar_desplazamiento)
        self.scroll_zoom.set(1.0) 
        self.scroll_zoom.pack(fill="x", padx=40, pady=(0, 10))

        marco_visualizacion = ttk.Frame(panel_der)
        marco_visualizacion.pack(fill="both", expand=True)

        if MATPLOTLIB_DISPONIBLE:
            self.fig = Figure(figsize=(5, 4), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=marco_visualizacion)
            
            self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

            self.scroll_y = tk.Scale(marco_visualizacion, from_=5, to=-5, resolution=0.1, 
                                    orient="vertical", label="Eje Y", length=300,
                                    command=self.actualizar_desplazamiento)
            self.scroll_y.pack(side="right", fill="y", padx=5)

            self.scroll_x = tk.Scale(panel_der, from_=-5, to=5, resolution=0.1, 
                                    orient="horizontal", label="Desplazar Eje X",
                                    command=self.actualizar_desplazamiento)
            self.scroll_x.pack(fill="x", padx=40)

            tk.Button(panel_der, text="🔄 Resetear Vista y Zoom", bg="#6c757d", fg="white",
                    font=("Helvetica", 10, "bold"), command=self.reset_posicion).pack(pady=10)

            self.limpiar_grafica()

    # =========================================================
    # FUNCIONES INFORMATIVAS (TEORÍA)
    # =========================================================
    def mostrar_procedimiento(self):
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
        try:
            Q = float(self.ent_q_obj.get())
            XQ = float(self.ent_x_obj.get())
            YQ = float(self.ent_y_obj.get())

            if not self.cargas_fuente:
                messagebox.showwarning("Aviso", "¡Necesitas agregar al menos una carga fuente para ver el cálculo!")
                return

            ventana_pasos = tk.Toplevel(self)
            ventana_pasos.title("Resolución Matemática Paso a Paso")
            ventana_pasos.geometry("700x500")
            ventana_pasos.configure(bg="#f8f9fa")

            marco_texto = ttk.Frame(ventana_pasos)
            marco_texto.pack(fill="both", expand=True, padx=15, pady=15)
            
            scroll_texto = ttk.Scrollbar(marco_texto)
            scroll_texto.pack(side="right", fill="y")
            
            caja_texto = tk.Text(marco_texto, font=("Consolas", 11), bg="white", yscrollcommand=scroll_texto.set)
            caja_texto.pack(side="left", fill="both", expand=True)
            scroll_texto.config(command=caja_texto.yview)

            # DELEGACIÓN AL MÓDULO LÓGICO
            texto = generar_texto_paso_a_paso(self.K, Q, XQ, YQ, self.cargas_fuente)

            caja_texto.insert(tk.END, texto)
            caja_texto.config(state=tk.DISABLED)

        except ValueError:
            messagebox.showerror("Error de Datos", "Por favor, asegúrate de que los campos de la Carga Objetivo tengan números válidos.")

    # =========================================================
    # LÓGICA DE CONTROL VISUAL DE LA GRÁFICA (CÁMARA)
    # =========================================================
    def actualizar_desplazamiento(self, _):
        if MATPLOTLIB_DISPONIBLE:
            self.desplazamiento_x = float(self.scroll_x.get())
            self.desplazamiento_y = float(self.scroll_y.get())
            self.zoom_actual = float(self.scroll_zoom.get())
            
            self.ax.set_xlim(self.desplazamiento_x - self.zoom_actual, self.desplazamiento_x + self.zoom_actual)
            self.ax.set_ylim(self.desplazamiento_y - self.zoom_actual, self.desplazamiento_y + self.zoom_actual)
            
            intervalo = self.zoom_actual / 5.0
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
            self.ax.yaxis.set_major_locator(ticker.MultipleLocator(base=intervalo))
            
            self.canvas.draw()

    def reset_posicion(self):
        if MATPLOTLIB_DISPONIBLE:
            self.scroll_x.set(0)
            self.scroll_y.set(0)
            self.scroll_zoom.set(1.0)
            self.actualizar_desplazamiento(None) 

    def restaurar_placeholders(self):
        agregar_placeholder(self.ent_q_obj, "1e-6")
        agregar_placeholder(self.ent_x_obj, "0")
        agregar_placeholder(self.ent_y_obj, "0")
        agregar_placeholder(self.ent_qi, "Ej: -5e-6")
        agregar_placeholder(self.ent_xi, "0.5")
        agregar_placeholder(self.ent_yi, "0.5")

    # =========================================================
    # LÓGICA DE INTERFAZ (BOTONES DE DATOS)
    # =========================================================
    def limpiar_todo(self):
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

    # =========================================================
    # LÓGICA DE CÁLCULO Y RENDERIZADO
    # =========================================================
    def calcular_fuerza(self):
        try:
            Q, XQ, YQ = float(self.ent_q_obj.get()), float(self.ent_x_obj.get()), float(self.ent_y_obj.get())
            if not self.cargas_fuente: return 
            
            try:
                # DELEGACIÓN AL MÓDULO LÓGICO
                fx_total, fy_total, magnitud = calcular_fuerza_neta_matematica(self.K, Q, XQ, YQ, self.cargas_fuente)
            except ValueError as error_fisico:
                messagebox.showerror("Error Físico", str(error_fisico))
                return
            
            self.lbl_vector.config(text=f"Vector Fuerza: < {fx_total:.4e}, {fy_total:.4e} > N")
            self.lbl_magnitud.config(text=f"Magnitud Total: {magnitud:.4e} N")
            
            if MATPLOTLIB_DISPONIBLE:
                self.dibujar_vectores(XQ, YQ, fx_total, fy_total)
        except ValueError:
            messagebox.showerror("Error", "Revisa los datos numéricos.")

    def limpiar_grafica(self):
        self.ax.clear()
        self.ax.set_title("Plano Cartesiano de Cargas")
        self.ax.set_xlabel("Eje X (m)")
        self.ax.set_ylabel("Eje Y (m)")
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.ax.axhline(0, color='black', linewidth=0.5)
        self.ax.axvline(0, color='black', linewidth=0.5)
        
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
            self.ax.arrow(xq, yq, fx/escala, fy/escala, 
                        head_width=self.zoom_actual*0.05, head_length=self.zoom_actual*0.08, 
                        fc='black', ec='black', zorder=10, label='Fuerza Neta')
                        
        self.ax.legend(loc="upper right") 
        self.canvas.draw()

# --- EJECUCIÓN DEL PROGRAMA ---
if __name__ == "__main__":
    app = AppFuerzaElectrica()  
    app.mainloop()