#Script correspondiente al registro de ventas
#Ingreso de productos desde una lista
#Ingreso de cantidad a vender
#Ingreso del rut del cliente miembro y los puntos que desea canjear
import uuid
from datetime import datetime

import datos_compartidos as db

def registrar_venta(rut_trabajador_actual):
    print("\n --- Registro de Venta ---")
    db.mostrar_productos_disponibles(para_venta=True)
    if not db.productos_db:
        print("No hay productos disponibles para la venta.")
        return {"estado": "fallido", "mensaje": "No hay productos disponibles para la venta."}
    
    items_venta = []
    total_venta_bruto = 0

    while True: 
        cod_producto = input("Ingrese el código del producto a vender (o '0' para finalizar): ").strip().upper()
        if cod_producto == '0':
            if not items_venta:
                print("No se han agregado productos a la venta.")
                return {"estado": "fallido", "mensaje": "No se han agregado productos a la venta."}
            break
        if cod_producto not in db.productos_db:
            print(f"Error: Producto con código '{cod_producto}' no encontrado.")
            continue

        producto = db.productos_db[cod_producto]
        cantidad = db.obtener_input_numerico(f"Ingrese la cantidad de '{producto['nombre'] }' a vender: (Stock actual: {producto['stock']}): ")

        if cantidad > producto['stock']:
            print(f"Error: Stock insuficiente para '{producto['nombre']}'. Stock disponible: {producto['stock']}.")
            continue

        items_venta.append({
            "codigo_producto": cod_producto,
            "nombre": producto["nombre"],
            "cantidad": cantidad,
            "precio_unitario": producto["precio_venta"]
        })
        total_venta_bruto += cantidad * producto["precio_venta"]
        print(f"Agregado: {cantidad} x {producto['nombre']}. Subtotal actual: ${total_venta_bruto:,}")

        print(f"\nTotal bruto de la venta: ${total_venta_bruto:,}")

        rut_miembro = None
        puntos_usados = 0
        puntos_ganados_esta_venta = 0

        es_miembro = input("¿El cliente es miembro? (s/n): ").strip().lower()
        if es_miembro == 's':
            rut_miembro_input = input("Ingrese RUT del cliente miembro (formato XXXXXXXX-X): ").strip()
            if rut_miembro_input in db.miembros_db:
                rut_miembro = rut_miembro_input
                miembro_data = db.miembros_db[rut_miembro]
                print(f"Cliente: {miembro_data['nombre']} {miembro_data['apellido']}, Puntos disponibles: {miembro_data['puntos_acumulados']}")

            if miembro_data['puntos_acumulados'] > 0:
                usar_puntos_opcion = input("¿Desea usar puntos para esta compra? (s/n): ").strip().lower()
                if usar_puntos_opcion == 's':
                    max_puntos_a_usar = min(miembro_data['puntos_acumulados'], total_venta_bruto)
                    puntos_usados = db.obtener_input_numerico(f"¿Cuántos puntos desea usar? (Máx: {max_puntos_a_usar}, 1 punto = $1 descuento): ", permitir_cero=True)
                    if puntos_usados > max_puntos_a_usar:
                        print(f"No puede usar más de {max_puntos_a_usar} puntos. Se usarán {max_puntos_a_usar}.")
                        puntos_usados = max_puntos_a_usar
            puntos_ganados_esta_venta = (total_venta_bruto // 1000) * 150
        else:
            print("RUT de miembro no encontrado. La venta se registrará sin miembro.")

        total_venta_final = total_venta_bruto - puntos_usados

        print(f"\n--- Resumen de la Venta ---")
        for item in items_venta:
            print(f"- {item['cantidad']} x {item['nombre']} @ ${item['precio_unitario']:,} c/u = ${item['cantidad'] * item['precio_unitario']:,}")
        print(f"Total Bruto: ${total_venta_bruto:,}")
        if puntos_usados > 0:
            print(f"Puntos Usados: {puntos_usados} (Descuento: ${puntos_usados:,})")
        print(f"Total Final a Pagar: ${total_venta_final:,}")
        if rut_miembro and puntos_ganados_esta_venta > 0:
            print(f"Puntos Ganados en esta compra: {puntos_ganados_esta_venta}")

        confirmar = input("¿Confirmar venta? (s/n): ").strip().lower()
        if confirmar == 's':
            id_venta_nueva = str(uuid.uuid4())
            fecha_actual = datetime.now().strftime("%Y-%m-%d")

        db.ventas_db.append({
            'id_venta': id_venta_nueva,
            'fecha': fecha_actual,
            'rut_trabajador': rut_trabajador_actual,
            'rut_miembro': rut_miembro,
            'total_venta_bruto': total_venta_bruto,
            'puntos_usados': puntos_usados,
            'total_venta_final': total_venta_final
        })

        for item in items_venta:
            db.detalle_ventas_db.append({
                'id_detalle_venta': str(uuid.uuid4()),
                'id_venta': id_venta_nueva,
                'codigo_producto': item['codigo_producto'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario']
            })
            db.productos_db[item['codigo_producto']]['stock'] -= item['cantidad']

        if rut_miembro:
            db.miembros_db[rut_miembro]['puntos_acumulados'] -= puntos_usados
            db.miembros_db[rut_miembro]['puntos_acumulados'] += puntos_ganados_esta_venta

        mensaje_exito = f"¡Venta registrada exitosamente! ID de Venta: {id_venta_nueva}"
        print(mensaje_exito)
        return {"estado": "exitoso", "mensaje": mensaje_exito, "id_venta": id_venta_nueva}
    else:
        print("Venta cancelada.")
        return {"estado": "cancelado", "mensaje": "Venta cancelada por el usuario."}

if __name__ == "__main__":
    # Simular el RUT del trabajador para la prueba
    rut_trabajador_prueba = "33333333-3"
    if rut_trabajador_prueba not in db.trabajadores_db:
        print(f"Error: El RUT de trabajador de prueba '{rut_trabajador_prueba}' no existe en datos_compartidos.")
    else:
        print(f"Probando servicio de registro de ventas como trabajador: {rut_trabajador_prueba}")
        resultado_venta = registrar_venta(rut_trabajador_prueba)
        print(f"\nResultado del servicio: {resultado_venta}")

        print("\nEstado de la 'base de datos' después de la prueba:")
        print("Productos:", db.productos_db)
        print("Miembros:", db.miembros_db)
        print("Ventas:", db.ventas_db)
        print("Detalle Ventas:", db.detalle_ventas_db)