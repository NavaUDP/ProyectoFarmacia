import socket
import ast
import os
import platform
import sys
import json
import re


nombre_usuario = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('localhost', 5000)
print('Conectando al bus en {} puerto {}'.format(*bus_address))
sock.connect(bus_address)


def limpiar_consola():
    comando = 'cls' if platform.system() == 'Windows' else 'clear'
    os.system(comando)

# Función para comunicarse con el bus
def com_bus(mensaje):
    size = f"{len(mensaje):05}".encode()
    sock.sendall(size + mensaje)
    amount_expected = int(sock.recv(5))
    data = b""
    while len(data) < amount_expected:
        data += sock.recv(amount_expected - len(data))
    # ignorar bytes corruptos
    respuesta = data.decode('utf-8', 'ignore')
    # quita el prefijo de servicio + "OK"
    return respuesta[7:]



def com_bus_safe(mensaje):
    # solo para gestión de trabajadores: si hay byte inválido, lo reemplaza
    size = f"{len(mensaje):05}".encode()
    sock.sendall(size + mensaje)
    amount_expected = int(sock.recv(5))
    data = b""
    while len(data) < amount_expected:
        data += sock.recv(amount_expected - len(data))
    try:
        respuesta = data.decode()
    except UnicodeDecodeError:
        respuesta = data.decode('utf-8', 'replace')
    print(respuesta)
    return respuesta[7:]



def gestion_clientes_miembros():
    prefijo = b"serv8"
    while True:
        print("\nGestión de Clientes Miembros:")
        
        print("  1) Agregar cliente miembro")
        print("  2) Eliminar cliente miembro")
        print("  3) Volver al menú")
        opcion = input("Seleccione una opción: ")

        if opcion == "3":
            print("Volviendo al menú...\n")
            break

     

        # 1) AGREGAR
        elif opcion == "1":
            rut     = input("RUT (8 dígitos): ")
            nombre  = input("Nombre: ")
            apellido= input("Apellido: ")
            correo  = input("Correo electrónico: ")
            datos   = f"ADD|{rut}|{nombre}|{apellido}|{correo}".encode()
            contenido = com_bus(prefijo + datos)   # e.g. "OK" or "NK..."
            if contenido.startswith("OK"):
                print("Cliente miembro agregado correctamente.")
            else:
                print("Error al agregar:", contenido[2:] if contenido.startswith("NK") else contenido)

        # 2) ELIMINAR
        elif opcion == "2":
            rut     = input("RUT a eliminar: ")
            datos   = f"DEL|{rut}".encode()
            contenido = com_bus(prefijo + datos)   # e.g. "OK" or "NK..."
            if contenido.startswith("OK"):
                print("Cliente miembro eliminado correctamente.")
            else:
                print("Error al eliminar:", contenido[2:] if contenido.startswith("NK") else contenido)

        else:
            print("Opción no válida.")

def gestion_proveedores():
    prefijo = b"serv7"
    while True:
        print("\nGestión de Proveedores:")

        print("  1) Agregar proveedor")
        print("  2) Eliminar proveedor")
        print("  3) Agregar producto a proveedor")
        print("  4) Volver al menú")
        opcion = input("Seleccione una opción: ")

        if opcion == "4":
            break


        # 1) AGREGAR PROVEEDOR
        elif opcion == "1":
            rut  = input("RUT (8 dígitos): ")
            nom  = input("Nombre: ")
            mail = input("Correo electrónico: ")
            datos    = f"ADD|{rut}|{nom}|{mail}".encode()
            contenido = com_bus(prefijo + datos)  # puede llegar "OK", "OKOK", "NK…", etc.
            if contenido.startswith("OK"):
                print("Proveedor agregado correctamente.")
            else:
                print("Error al agregar:", contenido[2:] if contenido.startswith("NK") else contenido)

        # 2) ELIMINAR PROVEEDOR
        elif opcion == "2":
            rut = input("RUT a eliminar: ")
            datos = f"DEL|{rut}".encode()
            contenido = com_bus(prefijo + datos)
            if contenido.startswith("OK"):
                print("Proveedor eliminado correctamente.")
            else:
                print("Error al eliminar:", contenido[2:] if contenido.startswith("NK") else contenido)

        # 3) AGREGAR PRODUCTO A PROVEEDOR
        elif opcion == "3":
            rut    = input("RUT del proveedor: ")
            prod   = input("Código producto (8): ")
            precio = input("Precio de compra: ")
            datos = f"APROD|{rut}|{prod}|{precio}".encode()
            contenido = com_bus(prefijo + datos)
            if contenido.startswith("OK"):
                print("Producto asociado correctamente.")
            else:
                print("Error al asociar producto:", contenido[2:] if contenido.startswith("NK") else contenido)

        else:
            print("Opción no válida.")

def gestion_productos():
    prefijo = b"serv6"
    while True:
        mensaje = prefijo + b"fun0"
        contenido = com_bus(mensaje)

        productos = ast.literal_eval(contenido)
        print("\nLista de productos:")
        for p in productos:
            codigo, nombre, stock, precio = p
            print(f"Código: {codigo:<10} | Nombre: {nombre:<15} | Stock: {stock:<5} | Precio: ${precio}")
        
        print("\nOpciones:")
        print("1. Agregar producto")
        print("2. Eliminar producto")
        print("3. Modificar precio de producto")
        print("4. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "4":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            codigo = input("Código del prodcuto: ")
            nombre = input("Nombre del producto: ")
            stock = input("Stock inicial: ")
            precio = input("Precio unitario: ")
            datos = f"fun1{codigo}|{nombre}|{stock}|{precio}".encode()
            mensaje = prefijo + datos
            
            contenido = com_bus(mensaje)
            if contenido == "VALID":
                print("Agregación de producto exitosa.")
            else:
                print("Agregación de producto fallida.")
        elif opcion == "2":
            codigo = input("Código del prodcuto: ")
            datos = f"fun2{codigo}".encode()
            mensaje = prefijo + datos
            
            contenido = com_bus(mensaje)
            if contenido == "VALID":
                print("Eliminación de producto exitosa.")
            else:
                print("Eliminación de producto fallida.")
        elif opcion == "3":
            codigo = input("Código del prodcuto: ")
            precio = input("Precio unitario nuevo: ")
            datos = f"fun3{codigo}|{precio}".encode()
            mensaje = prefijo + datos
            
            contenido = com_bus(mensaje)
            if contenido == "VALID":
                print("Modificación de precio exitosa .")
            else:
                print("Modificación de precio fallida.")
        else:
            print("Opción no válida.") 

def gestion_inventario():
    prefijo = b"serv5"
    while True:
        mensaje = prefijo + b"fun0"
        contenido = com_bus(mensaje)

        productos = ast.literal_eval(contenido)
        print("\nLista de productos:")
        for p in productos:
            codigo, nombre, stock, precio = p
            print(f"Código: {codigo:<10} | Nombre: {nombre:<15} | Stock: {stock:<5} | Precio: ${precio}")

        print("\nOpciones:")
        print("1. Modificar stock")
        print("2. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "2":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            codigo = input("Código del prodcuto: ")
            stock = input("Nuevo stock: ")
            datos = f"fun1{codigo}|{stock}".encode()
            mensaje = prefijo + datos
            contenido = com_bus(mensaje)
            if contenido == "VALID":
                print("Cambio de stock válido.")
            else:
                print("Cambio de stock inválido.")
        else:
            print("Opción no válida.") 

def generacion_reportes():
    service_name = "serv4"
    prefijo = service_name.encode('utf-8')

    while True:
        print("\n--- Generación de Reportes ---")
        print("1. Generar reporte por mes")
        print("2. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "2":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            fecha_reporte = input("Ingrese el mes y año del reporte (formato AAAA-MM): ")
            # Validar formato simple (puede mejorarse con regex o datetime)
            if len(fecha_reporte) != 7 or fecha_reporte[4] != '-':
                print("Formato inválido. Use AAAA-MM.")
                continue

            mensaje = prefijo + fecha_reporte.encode()
            contenido = com_bus(mensaje) # com_bus ya imprime la respuesta raw

            if contenido.startswith("OK"):
                cuerpo_json = contenido[2:]
                try:
                    reporte = json.loads(cuerpo_json)
                    print("\n--- Reporte para el período", fecha_reporte, "---")
                    print("\n[ VENTAS ]")
                    print(f"  - Monto Total Vendido: ${reporte.get('ventas_monto_total', 0):,}".replace(",", "."))
                    print(f"  - Cantidad de Productos Vendidos: {reporte.get('ventas_cantidad_total', 0)}")
                    print(f"  - Top 3 Productos Vendidos: {', '.join(reporte.get('ventas_top_3_productos', [])) or 'N/A'}")
                    
                    print("\n[ COMPRAS ]")
                    print(f"  - Monto Total Comprado: ${reporte.get('compras_monto_total', 0):,}".replace(",", "."))
                    print(f"  - Cantidad de Productos Comprados: {reporte.get('compras_cantidad_total', 0)}")
                    print(f"  - Top 3 Productos Comprados: {', '.join(reporte.get('compras_top_3_productos', [])) or 'N/A'}")

                    print("\n[ RESUMEN ]")
                    print(f"  - Ganancia Total: ${reporte.get('ganancia_total', 0):,}".replace(",", "."))
                    print("-----------------------------------------\n")

                except json.JSONDecodeError:
                    print("Error: La respuesta del servidor no es un JSON válido:", cuerpo_json)
            else:
                # Si la respuesta es NK<error> u otra cosa
                error_msg = contenido[2:] if contenido.startswith("NK") else contenido
                print("Error al generar el reporte:", error_msg)
        else:
            print("Opción no válida.")

def registro_compras():
    prefijo = b"serv3"
    while True:
        print("\nOpciones:")
        print("1. Registrar compra")
        print("2. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "2":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            # Ejecuta el servicio de registro de compras
            rut_trabajador = input("Ingrese su RUT (8 dígitos): ")
            if len(rut_trabajador) != 8 or not rut_trabajador.isdigit():
                print("RUT inválido. Debe tener 8 dígitos.")
                continue

            rut_proveedor = input("Ingrese el RUT del proveedor (8 dígitos): ")
            if len(rut_proveedor) != 8 or not rut_proveedor.isdigit():
                print("RUT inválido. Debe tener 8 dígitos.")
                continue

            productos = []
            while True: 
                codigo_producto = input("Ingrese el código del producto o 'fin' para finalizar: ")
                if codigo_producto.lower() == 'fin':
                    break
                cantidad = input(f"Ingrese la cantidad de {codigo_producto}: ")
                productos.append(f"{codigo_producto},{cantidad}")
            if not productos:
                print("Debe ingresar al menos un producto.")
                continue
            datos_compra = f"{rut_trabajador};{rut_proveedor};" + ";".join(productos)
            payload = prefijo + datos_compra.encode()

            contenido = com_bus(payload)  
            if contenido.startswith("OK"):
                print("Compra registrada correctamente.")
            else:
                print("Error al registrar la compra:", contenido[2:] if contenido.startswith("NK") else contenido)

        else:
            print("Opción no válida.") 

def registro_ventas():
    prefijo = b"serv2"
    try:
        while True:
            print("\nOpciones:")
            print("1. Registrar venta")
            print("2. Volver al menú")

            opcion = input("Seleccione una opción: ")
            if opcion == "2":
                print("Volviendo al menú...\n")
                break
            elif opcion == "1":
                #Ejecuta el servicio de registro de ventas
                # El rut el trabajador se vuelve a ingresar
                rut_trabajador = input("Ingrese su RUT (8 dígitos): ")
                if len(rut_trabajador) != 8 or not rut_trabajador.isdigit():
                    print("RUT inválido. Debe tener 8 dígitos.")
                    continue
                rut_cliente = input("Ingrese el rut del cliente (8 dígitos) o 'None' si es público general: ")
                puntos = input("Ingrese los puntos a usar (0 si no es miembro): ")
                productos = []
                while True:
                    codigo_producto = input("Ingrese el código del producto o 'fin' para finalizar: ")
                    if codigo_producto.lower() == 'fin':
                        break
                    cantidad = input(f"Ingrese la cantidad de {codigo_producto}: ")
                    productos.append(f"{codigo_producto},{cantidad}")
                if not productos:
                    print("Debe ingresar al menos un producto.")
                    continue
                datos_venta = f"{rut_cliente};{puntos};{rut_trabajador};" + ";".join(productos)
                payload = prefijo + datos_venta.encode()

                contenido = com_bus(payload)  # e.g. "OK" or "NK<error>"
                if contenido.startswith("OK"):
                    print("Venta registrada correctamente.")
                else:
                    print("Error al registrar la venta:", contenido[2:] if contenido.startswith("NK") else contenido)

            else:
                print("Opción no válida.") 
    except Exception as e:
        print(f"Error en registro de ventas: {e}")

def gestion_trabajadores():
    prefijo = b"serv1"

   

    while True:
        print("\nGestión de Trabajadores:")
        print("  1) Agregar trabajador")
        print("  2) Eliminar trabajador")
        print("  3) Volver al menú")
        opcion = input("Seleccione una opción: ")

        if opcion == "3":
            break

        elif opcion == "1":
            rut      = input("RUT (8 dígitos): ")
            nombre   = input("Nombre: ")
            apellido = input("Apellido: ")
            correo   = input("Correo electrónico: ")
            datos    = f"fun1{rut}|{nombre}|{apellido}|{correo}".encode()
            contenido = com_bus(prefijo + datos)

            if contenido.startswith("OK"):
                payload = contenido[2:]
                try:
                    info = json.loads(payload)
                    print(f"Trabajador agregado. RUT: {info['rut']}  Contraseña: {info['contrasena']}")
                except json.JSONDecodeError:
                    print("Respuesta inesperada al agregar:", payload)
            else:
                print("Error al agregar:", contenido[2:] if contenido.startswith("NK") else contenido)

        elif opcion == "2":
            rut       = input("RUT a eliminar: ")
            datos     = f"fun2{rut}".encode()
            contenido = com_bus(prefijo + datos)
            if contenido.strip() == "OK":
                print("Trabajador eliminado correctamente.")
            else:
                print("Error al eliminar:", contenido[2:] if contenido.startswith("NK") else contenido)

        else:
            print("Opción no válida.")

def mostrar_menu():
    while True:
        print("\nOpciones:")
        print("1. Gestión de trabajadores")
        print("2. Registro de ventas")
        print("3. Registro de compras")
        print("4. Generación de reportes")
        print("5. Gestión de inventario")
        print("6. Gestión de productos")
        print("7. Gestión de proveedores")
        print("8. Gestión de clientes miembros")
        print("9. Volver a inicio de sesión")

        opcion = input("Seleccione una opción: ")
        if opcion == "9":
            print("Volviendo a inicio de sesión...\n")
            break
        elif opcion == "1" :
            gestion_trabajadores()
        elif opcion == "2":
            registro_ventas()
        elif opcion == "3":
            registro_compras()
        elif opcion == "4":
            generacion_reportes()
        elif opcion == "5":
            gestion_inventario()
        elif opcion == "6":
            gestion_productos()
        elif opcion == "7":
            gestion_proveedores()
        elif opcion == "8":
            gestion_clientes_miembros()
        else:
            print("Opción no válida.")
     
def main():
    limpiar_consola()
    prefijo = b"serv0"
    try:
        while True:
            print("1. Iniciar Sesión")
            print("2. Salir del sistema")

            opcion = input("Seleccione una opción: ")
            if opcion == "1":
                usuario = input("Usuario (RUT): ")
                password = input("Password: ")
                
                credenciales = f"{usuario}|{password}|True".encode()
                mensaje = prefijo + credenciales
                
                contenido = com_bus(mensaje)
                if contenido == "VALID":
                    print("Inicio de sesión válido.")
                    nombre_usuario = usuario
                    mostrar_menu()
                else:
                    #limpiar_consola()
                    print("Inicio de sesión inválido.")
            elif opcion == "2":
                print("Saliendo del sistema.")
                sys.exit()
            else:
                print("Opción no válida.")
    except Exception as e:
        print(f"Error en cliente: {e}")
    finally:
        sock.close()
        print("Cliente desconectado.")

if __name__ == "__main__":
    main()
