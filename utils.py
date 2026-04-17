import tkinter as tk # Módulo principal de interfaz gráfica (GUI)

# --- FUNCIÓN DE UTILIDAD (UX) CORREGIDA ---
def agregar_placeholder(entry, texto):
    """
    Función de Experiencia de Usuario (UX). 
    Inserta un texto gris de ejemplo dentro de una caja de entrada ('entry'). 
    Corregido: Se basa en el color para borrar el texto, evitando que se mezcle
    con lo que escribe el usuario.
    """
    entry.delete(0, tk.END) 
    entry.insert(0, texto) 
    entry.config(foreground='grey')

    def al_entrar(event): # Evento disparado al hacer clic dentro de la caja.
        # Si el texto está en gris, lo borra por completo y prepara para escribir en negro.
        if entry.cget('foreground') == 'grey':
            entry.delete(0, tk.END)
            entry.config(foreground='black') 

    def al_salir(event): # Evento disparado al hacer clic fuera de la caja.
        # Si el usuario no escribió nada (o dejó espacios), restaura el gris.
        if not entry.get().strip():
            entry.delete(0, tk.END)
            entry.insert(0, texto)
            entry.config(foreground='grey')

    # 'bind' conecta las acciones del ratón con las funciones internas.
    entry.bind("<FocusIn>", al_entrar)
    entry.bind("<FocusOut>", al_salir)