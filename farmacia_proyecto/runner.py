# runner.py
# Script de Python para iniciar todos los servicios como subprocesos.

import subprocess
import time
import sys

# Lista de los scripts de los servicios a ejecutar
servicios = [
    "servicio_inicio_sesion.py",
    "servicio_gestion_trabajadores.py",
    "reg_ventas.py",
    "reg_compras.py",
    "gen_reportes.py",
    "servicio_inventario.py",
    "servicio_productos.py",
    "servicio_gestion_proveedores.py",
    "servicio_gestion_clientes_miembros.py"
]

procesos = []

print("--- Iniciando todos los servicios ---")

try:
    # Iniciar cada servicio como un subproceso
    for servicio_script in servicios:
        # Usamos Popen para que el proceso no bloquee la ejecución del runner
        proceso = subprocess.Popen([sys.executable, servicio_script])
        procesos.append(proceso)
        print(f"[OK] Servicio '{servicio_script}' iniciado con PID: {proceso.pid}")
        time.sleep(0.5) # Pequeña pausa

    print("\n--- Todos los servicios están corriendo en segundo plano. ---")
    print("--- Presiona CTRL+C en esta ventana para detener todos los servicios. ---")
    
    # Mantener el script principal vivo para poder detener los subprocesos al final
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n--- Recibida señal de interrupción (CTRL+C). Deteniendo todos los servicios... ---")

finally:
    # Asegurarnos de que todos los procesos hijos se terminen
    for i, proceso in enumerate(procesos):
        print(f"Deteniendo '{servicios[i]}' (PID: {proceso.pid})...")
        proceso.terminate() # Envía una señal de terminación
    
    # Esperar a que los procesos realmente terminen
    for proceso in procesos:
        proceso.wait()
        
    print("--- Todos los servicios han sido detenidos. ---")