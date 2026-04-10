import math # Para operaciones de raíces cuadradas y potencias
import tkinter as tk # Biblioteca base para la interfaz de usuario
from tkinter import ttk, messagebox # Componentes modernos y ventanas de mensajes

# Gestión de Matplotlib para renderizar la gráfica científica
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
        self.geometry("1150x700")
        self.configure(bg="#e9ecef") 
        
        self.K = 8.9875517923e9  
        self.cargas_fuente = [] 
        
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
        # BOTÓN NUEVO: Limpiar Todo
        tk.Button(marco_botones_lista, text="🧹 Limpiar Todo", bg="#fd7e14", fg="white", 
                command=self.limpiar_todo, width=12).pack(side="left", padx=2)

        # Inicializar Placeholders
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

        self.marco_grafica = ttk.Frame(panel_der)
        self.marco_grafica.pack(fill="both", expand=True)
        
        if MATPLOTLIB_DISPONIBLE:
            self.fig = Figure(figsize=(5, 4), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.marco_grafica)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            self.limpiar_grafica()

    def restaurar_placeholders(self):
        """Asigna los textos de ejemplo a todas las cajas."""
        agregar_placeholder(self.ent_q_obj, "1e-6")
        agregar_placeholder(self.ent_x_obj, "0")
        agregar_placeholder(self.ent_y_obj, "0")
        agregar_placeholder(self.ent_qi, "Ej: -5e-6")
        agregar_placeholder(self.ent_xi, "0.5")
        agregar_placeholder(self.ent_yi, "0.5")

    def limpiar_todo(self):
        """Borra todos los datos, la tabla, los resultados y reinicia la gráfica."""
        # 1. Limpiar lista interna y tabla visual
        self.cargas_fuente = []
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # 2. Restaurar cajas de texto con placeholders
        self.restaurar_placeholders()

        # 3. Limpiar etiquetas de resultados
        self.lbl_vector.config(text="Vector Fuerza: < 0.00, 0.00 > N")
        self.lbl_magnitud.config(text="Magnitud Total: 0.00 N")

        # 4. Limpiar gráfica
        if MATPLOTLIB_DISPONIBLE:
            self.limpiar_grafica()
            self.ax.legend().remove() # Quita la leyenda si existe
            self.canvas.draw()

    def agregar_carga(self):
        try:
            q = float(self.ent_qi.get())
            x = float(self.ent_xi.get())
            y = float(self.ent_yi.get())
            item_id = self.tabla.insert("", "end", values=(f"{q:.2e}", x, y))
            self.cargas_fuente.append({'id': item_id, 'q': q, 'x': x, 'y': y})
            
            # Limpiar solo las cajas de entrada de carga puntual tras añadir
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
            if not self.cargas_fuente:
                messagebox.showerror("Error", "¡Añade al menos una carga fuente!")
                return
            fx_total = fy_total = 0.0
            for carga in self.cargas_fuente:
                dx, dy = XQ - carga['x'], YQ - carga['y']
                r_cuadrado = dx**2 + dy**2
                r = math.sqrt(r_cuadrado)
                if r == 0:
                    messagebox.showerror("Error Físico", "Superposición de cargas detectada.")
                    return
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
        self.ax.clear()
        self.ax.set_title("Plano Cartesiano de Cargas")
        self.ax.set_xlabel("Eje X (m)")
        self.ax.set_ylabel("Eje Y (m)")
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.ax.axhline(0, color='black', linewidth=0.5)
        self.ax.axvline(0, color='black', linewidth=0.5)
        self.canvas.draw()

    def dibujar_vectores(self, xq, yq, fx, fy):
        self.limpiar_grafica()
        for c in self.cargas_fuente:
            color = 'red' if c['q'] > 0 else 'blue'
            self.ax.scatter(c['x'], c['y'], color=color, s=100, zorder=5)
            self.ax.text(c['x'], c['y']+0.05, f" {c['q']:.1e}C", fontsize=9, ha='center')
        self.ax.scatter(xq, yq, color='green', s=150, marker='*', zorder=6, label='Objetivo')
        if fx != 0 or fy != 0:
            escala = max(abs(fx), abs(fy)) / (max(abs(xq), abs(yq), 1) * 0.3)
            self.ax.arrow(xq, yq, fx/escala, fy/escala, head_width=0.08, head_length=0.1, fc='black', ec='black', zorder=10, label='Fuerza Neta')
        self.ax.legend(loc="upper right")
        self.canvas.draw()

if __name__ == "__main__":
    app = AppFuerzaElectrica()
    app.mainloop()