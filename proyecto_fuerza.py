import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

# Intentar importar matplotlib para la visualización gráfica
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

# --- LÓGICA FÍSICA (COULOMB CORE) ---
class FisicaCoulomb:
    K = 8.9875517923e9  # Constante de Coulomb (N·m²/C²)

    @staticmethod
    def calcular_fuerza_individual(q_obj, x_obj, y_obj, q_i, x_i, y_i):
        dx = x_obj - x_i
        dy = y_obj - y_i
        r2 = dx**2 + dy**2
        
        if r2 == 0:
            raise ValueError("Distancia cero: una carga coincide con el objetivo.")
        
        r = math.sqrt(r2)
        # La fuerza vectorial: F = (k * q1 * q2 / r^2) * unit_vector
        # unit_vector = (dx/r, dy/r)
        factor = (FisicaCoulomb.K * q_obj * q_i) / (r2 * r)
        return factor * dx, factor * dy

# --- INTERFAZ GRÁFICA (APP PRINCIPAL) ---
class AppCoulomb(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto 1: Ley de Coulomb - Principio de Superposición")
        self.geometry("1100x700")
        self.configure(bg="#f0f0f0")

        self.cargas_fuente = []
        self._setup_ui()

    def _setup_ui(self):
        # Estilo
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))

        # Contenedor Principal
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # PANEL IZQUIERDO (Entradas)
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side="left", fill="y", padx=(0, 20))

        # 1. Carga Objetivo
        obj_frame = ttk.LabelFrame(left_panel, text=" Carga Objetivo (Q) ", padding=10)
        obj_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(obj_frame, text="Magnitud (C):").grid(row=0, column=0, sticky="w")
        self.ent_q_obj = ttk.Entry(obj_frame, width=15)
        self.ent_q_obj.insert(0, "1e-6")
        self.ent_q_obj.grid(row=0, column=1, pady=2)

        ttk.Label(obj_frame, text="Posición X (m):").grid(row=1, column=0, sticky="w")
        self.ent_x_obj = ttk.Entry(obj_frame, width=15)
        self.ent_x_obj.insert(0, "0")
        self.ent_x_obj.grid(row=1, column=1, pady=2)

        ttk.Label(obj_frame, text="Posición Y (m):").grid(row=2, column=0, sticky="w")
        self.ent_y_obj = ttk.Entry(obj_frame, width=15)
        self.ent_y_obj.insert(0, "0")
        self.ent_y_obj.grid(row=2, column=1, pady=2)

        # 2. Agregar Cargas n
        add_frame = ttk.LabelFrame(left_panel, text=" Agregar Cargas Puntuales (n) ", padding=10)
        add_frame.pack(fill="x")

        ttk.Label(add_frame, text="Magnitud (C):").grid(row=0, column=0, sticky="w")
        self.ent_qi = ttk.Entry(add_frame, width=15)
        self.ent_qi.grid(row=0, column=1, pady=2)

        ttk.Label(add_frame, text="Pos X (m):").grid(row=1, column=0, sticky="w")
        self.ent_xi = ttk.Entry(add_frame, width=15)
        self.ent_xi.grid(row=1, column=1, pady=2)

        ttk.Label(add_frame, text="Pos Y (m):").grid(row=2, column=0, sticky="w")
        self.ent_yi = ttk.Entry(add_frame, width=15)
        self.ent_yi.grid(row=2, column=1, pady=2)

        btn_add = tk.Button(add_frame, text="Añadir a la lista", bg="#2196F3", fg="white", 
                           command=self.agregar_carga_a_lista)
        btn_add.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        # 3. Tabla de cargas
        self.tree = ttk.Treeview(left_panel, columns=("q", "x", "y"), show="headings", height=8)
        self.tree.heading("q", text="Carga (C)")
        self.tree.heading("x", text="X (m)")
        self.tree.heading("y", text="Y (m)")
        self.tree.column("q", width=100)
        self.tree.column("x", width=70)
        self.tree.column("y", width=70)
        self.tree.pack(fill="both", expand=True, pady=10)

        # PANEL DERECHO (Resultados y Gráfica)
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)

        # Botones de Acción
        action_frame = ttk.Frame(right_panel)
        action_frame.pack(fill="x", pady=(0, 10))

        btn_calc = tk.Button(action_frame, text="CALCULAR FUERZA NETA", bg="#4CAF50", fg="white", 
                            font=("Arial", 10, "bold"), command=self.ejecutar_calculo)
        btn_calc.pack(side="left", padx=5)

        btn_clear = tk.Button(action_frame, text="Limpiar Todo", bg="#f44336", fg="white", command=self.limpiar)
        btn_clear.pack(side="left", padx=5)

        # Resultados
        self.res_label = ttk.Label(right_panel, text="Vector Fuerza Neta: < 0, 0 > N\nMagnitud: 0 N", 
                                  font=("Courier New", 12, "bold"), justify="left")
        self.res_label.pack(pady=10)

        # Gráfica
        self.plot_frame = ttk.Frame(right_panel)
        self.plot_frame.pack(fill="both", expand=True)
        
        if MATPLOTLIB_DISPONIBLE:
            self.fig = Figure(figsize=(5, 4), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            self._reset_plot()
        else:
            ttk.Label(self.plot_frame, text="Matplotlib no detectado.\nGráfica no disponible.").pack()

    def agregar_carga_a_lista(self):
        try:
            q, x, y = float(self.ent_qi.get()), float(self.ent_xi.get()), float(self.ent_yi.get())
            self.cargas_fuente.append({'q': q, 'x': x, 'y': y})
            self.tree.insert("", "end", values=(f"{q:.2e}", x, y))
            # Limpiar entradas
            for e in [self.ent_qi, self.ent_xi, self.ent_yi]: e.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Entradas inválidas en cargas puntuales.")

    def ejecutar_calculo(self):
        try:
            Q = float(self.ent_q_obj.get())
            XQ = float(self.ent_x_obj.get())
            YQ = float(self.ent_y_obj.get())
            
            if not self.cargas_fuente:
                messagebox.showwarning("Aviso", "Agregue al menos una carga puntual.")
                return

            fx_total, fy_total = 0.0, 0.0
            
            for c in self.cargas_fuente:
                fx, fy = FisicaCoulomb.calcular_fuerza_individual(Q, XQ, YQ, c['q'], c['x'], c['y'])
                fx_total += fx
                fy_total += fy

            mag = math.sqrt(fx_total**2 + fy_total**2)
            
            # Actualizar Texto
            self.res_label.config(text=f"Vector Fuerza Neta: <{fx_total:.4e}, {fy_total:.4e}> N\nMagnitud: {mag:.4e} N")
            
            # Actualizar Gráfica
            if MATPLOTLIB_DISPONIBLE:
                self._update_plot(XQ, YQ, fx_total, fy_total)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _reset_plot(self):
        self.ax.clear()
        self.ax.set_title("Distribución de Cargas")
        self.ax.set_xlabel("x (m)")
        self.ax.set_ylabel("y (m)")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.canvas.draw()

    def _update_plot(self, xq, yq, fx, fy):
        self.ax.clear()
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Dibujar cargas fuente
        for c in self.cargas_fuente:
            color = 'red' if c['q'] > 0 else 'blue'
            self.ax.scatter(c['x'], c['y'], c=color, s=100, label='_nolegend_')
            self.ax.text(c['x'], c['y'], f" {c['q']:.1e}C", fontsize=8)

        # Dibujar carga objetivo
        self.ax.scatter(xq, yq, c='green', s=200, marker='*', label='Objetivo (Q)')
        
        # Dibujar vector fuerza (normalizado para visibilidad)
        if fx != 0 or fy != 0:
            self.ax.quiver(xq, yq, fx, fy, color='black', scale_units='dots', scale=0.1, width=0.015)

        self.ax.legend()
        self.canvas.draw()

    def limpiar(self):
        self.cargas_fuente = []
        for i in self.tree.get_children(): self.tree.delete(i)
        self.res_label.config(text="Vector Fuerza Neta: < 0, 0 > N\nMagnitud: 0 N")
        if MATPLOTLIB_DISPONIBLE: self._reset_plot()

if __name__ == "__main__":
    app = AppCoulomb()
    app.mainloop()