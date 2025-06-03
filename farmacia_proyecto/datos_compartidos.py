# datos_compartidos.py
import uuid
from datetime import datetime
from collections import Counter

# --- Mock Data (simulando la base de datos) ---
productos_db = {
    "P001": {"nombre": "Paracetamol 500mg", "precio_venta": 1200, "precio_compra": 700, "stock": 100},
    "P002": {"nombre": "Ibuprofeno 400mg", "precio_venta": 1500, "precio_compra": 900, "stock": 50},
    "P003": {"nombre": "Amoxicilina 250mg", "precio_venta": 3000, "precio_compra": 1800, "stock": 30},
    "P004": {"nombre": "Vitamina C", "precio_venta": 5000, "precio_compra": 3000, "stock": 75},
    "P005": {"nombre": "Jarabe Tos Adulto", "precio_venta": 4500, "precio_compra": 2500, "stock": 20},
}

miembros_db = {
    "11111111-1": {"nombre": "Juan Perez", "apellido": "Gonzalez", "correo_electronico": "juan@example.com", "puntos_acumulados": 1500},
    "22222222-2": {"nombre": "Ana Lopez", "apellido": "Smith", "correo_electronico": "ana@example.com", "puntos_acumulados": 300},
}

trabajadores_db = { # Simplificado
    "33333333-3": {"nombre_cuenta": "admin", "rol": "administrador"},
    "44444444-4": {"nombre_cuenta": "op01", "rol": "operativo"},
}

ventas_db = []
detalle_ventas_db = []
compras_db = []
detalle_compras_db = []

# --- Helper Functions ---
def mostrar_productos_disponibles(para_venta=True):
    print("\n--- Productos Disponibles ---")
    if not productos_db:
        print("No hay productos registrados.")
        return
    for codigo, data in productos_db.items():
        if para_venta:
            print(f"Código: {codigo}, Nombre: {data['nombre']}, Precio Venta: ${data['precio_venta']:,}, Stock: {data['stock']}")
        else: # para compra
            print(f"Código: {codigo}, Nombre: {data['nombre']}, Precio Compra: ${data['precio_compra']:,}, Stock: {data['stock']}")
    print("---------------------------")

def obtener_input_numerico(mensaje, tipo=int, permitir_cero=False):
    while True:
        try:
            valor = tipo(input(mensaje))
            if valor < 0 or (valor == 0 and not permitir_cero):
                print(f"El valor debe ser {'mayor o igual a cero' if permitir_cero else 'mayor que cero'}.")
            else:
                return valor
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número.")

# Más helpers si son necesarios

#Prueba de la función mostrar_productos_disponibles
if __name__ == "__main__":

    mostrar_productos_disponibles(para_venta=True)