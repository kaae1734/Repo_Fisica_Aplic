import tkinter as tk # Módulo principal de interfaz gráfica (GUI) para crear ventanas, botones y etiquetas.

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