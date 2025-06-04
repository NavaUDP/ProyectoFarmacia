import uuid
from datetime import datetime

import datos_compartidos as db

def registrar_compra(rut_trabajador_actual):
    #Mostramos productos disponibles para la compra
    print("\n --- Registro de Compra ---")
    db.mostrar_productos_disponibles(para_venta=False)
    if not db.productos_db:
        print("No hay productos disponibles para la compra.")
        return {"estado": "fallido", "mensaje": "No hay productos disponibles para la compra."}
    
    #Arreglo par almacenar items de la compra
    items_compra = []
    total_compra = 0

    while True:
        codigo_producto = input("Ingrese el código del producto a comprar (o '0' para finalizar): ").strip().upper()
        if codigo_producto == '0':
            if not items_compra:
                print("No se han agregado productos a la compra.")
                return {"estado": "fallido", "mensaje": "No se han agregado productos a la compra."}
            break
        if codigo_producto not in db.productos_db:
            print(f"Error: Producto con código '{codigo_producto}' no existe.")
            continue

        producto = db.productos_db[codigo_producto]
        cantidad = db.obtener_input_numerico(f"Ingrese cantidad de '{producto['nombre']} a comprar:")
        precio_compra_unitario = producto['precio_compra']

        items_compra.append({
            "codigo_producto": codigo_producto,
            "nombre": producto["nombre"],
            "cantidad": cantidad,
            "precio_unitario": precio_compra_unitario
        })

        total_compra += cantidad*precio_compra_unitario
        print(f"Agregado: {cantidad} x {producto['nombre']}. Subtotal actual de compra: ${total_compra:,}")

        print(f"\nTotal de la compra: ${total_compra:,}")

        #confirmación de la compra
        confirmar = input("¿Confirmar compra? (s/n): ").strip().lower()
        if confirmar == 's':
            id_compra_nueva = str(uuid.uuid4())
            fecha_actual = datetime.now().strftime("%d - %m - %Y")

            db.compras_db.append({
                'id_compra': id_compra_nueva,
                'fecha': fecha_actual,
                'rut_trabajador': rut_trabajador_actual,
                'total_compra': total_compra
            })

            for item in items_compra:
                db.detalle_compras_db.append({
                    'id_detalle_compra': str(uuid.uuid4()),
                    'id_compra': id_compra_nueva,
                    'codigo_producto': item['codigo_producto'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario']
                })
                db.productos_db[item['codigo_producto']]['stock'] += item['cantidad']

            mensaje_exito = f"¡Compra registrada exitosamente! ID de Compra: {id_compra_nueva}"
            print(mensaje_exito)
            return {"estado": "exitoso", "mensaje": mensaje_exito, "id_compra": id_compra_nueva}
        else:
            print("Compra cancelada.")
            return {"estado": "cancelado", "mensaje": "Compra cancelada por el usuario."}
        
# Para probar este script individualmente (opcional):
if __name__ == "__main__":
    rut_trabajador_prueba = "33333333-3"
    if rut_trabajador_prueba not in db.trabajadores_db:
        print(f"Error: El RUT de trabajador de prueba '{rut_trabajador_prueba}' no existe en datos_compartidos.")
    else:
        print(f"Probando servicio de registro de compras como trabajador: {rut_trabajador_prueba}")
        resultado_compra = registrar_compra(rut_trabajador_prueba)
        print(f"\nResultado del servicio: {resultado_compra}")

        print("\nEstado de la 'base de datos' después de la prueba:")
        print("Productos:", db.productos_db)
        print("Compras:", db.compras_db)
        print("Detalle Compras:", db.detalle_compras_db)

