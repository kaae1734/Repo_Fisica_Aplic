import math # Biblioteca matemática estándar para calcular raíces cuadradas y distancias.

# =========================================================
# LÓGICA DE NEGOCIO (PROCESAMIENTO DE DATOS Y FÍSICA)
# =========================================================

def calcular_fuerza_neta_matematica(K, Q, XQ, YQ, cargas_fuente):
    """
    Realiza el cálculo puro de la Ley de Coulomb.
    Itera sobre las cargas en memoria y realiza la sumatoria vectorial.
    Retorna la fuerza en X, la fuerza en Y, y la Magnitud Total.
    """
    fx_total = 0.0
    fy_total = 0.0
    
    for carga in cargas_fuente:
        dx, dy = XQ - carga['x'], YQ - carga['y']
        r_cuadrado = dx**2 + dy**2
        r = math.sqrt(r_cuadrado)
        
        if r == 0: 
            # Evita error matemático Div/0
            raise ValueError("Superposición de cargas detectada. Revisa las coordenadas.")
            
        # Descomposición vectorial implícita
        factor_fuerza = (K * Q * carga['q']) / (r_cuadrado * r)
        fx_total += factor_fuerza * dx
        fy_total += factor_fuerza * dy
        
    magnitud = math.sqrt(fx_total**2 + fy_total**2)
    
    return fx_total, fy_total, magnitud


def generar_texto_paso_a_paso(K, Q, XQ, YQ, cargas_fuente):
    """
    Tutor Matemático Dinámico (Lógica de Formateo de Texto).
    Itera sobre las cargas y reconstruye paso a paso los cálculos,
    retornando un string completo con la demostración matemática 
    sin interactuar directamente con la interfaz gráfica.
    """
    texto = f"=================================================\n"
    texto += f"     CÁLCULO DINÁMICO DE LA FUERZA NETA\n"
    texto += f"=================================================\n\n"
    texto += f"DATOS INICIALES:\n"
    texto += f"- Constante K = {K:.4e} N·m²/C²\n"
    texto += f"- Carga Objetivo (Q) = {Q:.4e} C en la posición ({XQ}, {YQ})\n\n"

    fx_total = 0.0
    fy_total = 0.0

    # Iterar simulando el cálculo para documentarlo
    for i, carga in enumerate(cargas_fuente, 1):
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
        
        factor_fuerza = (K * Q * q_i) / (r_cuadrado * r)
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

    return texto