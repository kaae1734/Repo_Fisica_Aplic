from app import AppFuerzaElectrica

# --- EJECUCIÓN DEL PROGRAMA ---
# Este bloque verifica si el archivo se está ejecutando directamente y arranca el loop de la interfaz.
if __name__ == "__main__":
    app = AppFuerzaElectrica()  
    app.mainloop() # Bucle infinito que mantiene viva la ventana y "escucha" clics y teclas.
    
# MUCHAS GRACIAS :)