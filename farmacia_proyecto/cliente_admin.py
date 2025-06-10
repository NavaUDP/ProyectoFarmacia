import socket
import ast
import os
import platform
import sys
import json

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
    amount_received = 0
    data = b""
    while amount_received < amount_expected:
        chunk = sock.recv(amount_expected - amount_received)
        amount_received += len(chunk)
        data += chunk

    respuesta = data.decode()
    print(respuesta)
    contenido = respuesta[7:]
    return contenido


def gestion_clientes_miembros():
    prefijo = b"serv8"
    while True:
        print("\nGestión de Clientes Miembros:")
        print("  1) Listar clientes miembros")
        print("  2) Agregar cliente miembro")
        print("  3) Eliminar cliente miembro")
        print("  4) Volver al menú")
        opcion = input("Seleccione una opción: ")

        if opcion == "4":
            print("Volviendo al menú...\n")
            break

        # 1) LISTAR
        if opcion == "1":
            mensaje = prefijo + b"LIST"
            contenido = com_bus(mensaje)   # e.g. "OK[...json...]"
            if contenido.startswith("OK"):
                cuerpo = contenido[2:]
                try:
                    lista = json.loads(cuerpo)
                    print("\nRUT     │ Nombre      │ Apellido    │ Correo               │ Puntos")
                    print("─────────┼──────────────┼─────────────┼──────────────────────┼────────")
                    for m in lista:
                        print(f"{m['rut']} ┃ {m['nombre']:<12} ┃ {m['apellido']:<11} ┃ "
                              f"{m['correo']:<20} ┃ {m['puntos']}")
                except json.JSONDecodeError:
                    print("Error al decodificar JSON:", cuerpo)
            else:
                print("Error al listar:", contenido)

        # 2) AGREGAR
        elif opcion == "2":
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

        # 3) ELIMINAR
        elif opcion == "3":
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
        print("  1) Listar proveedores")
        print("  2) Agregar proveedor")
        print("  3) Eliminar proveedor")
        print("  4) Agregar producto a proveedor")
        print("  5) Volver al menú")
        opcion = input("Seleccione una opción: ")

        if opcion == "5":
            break

        # 1) LISTAR
        if opcion == "1":
            mensaje = prefijo + b"LIST"
            contenido = com_bus(mensaje)  # e.g. "OK[{...},...]"
            if contenido.startswith("OK"):
                cuerpo = contenido[2:]
                try:
                    lista = json.loads(cuerpo)
                    print("\nRUT       │ Nombre        │ Correo")
                    print("───────────┼───────────────┼──────────────────────")
                    for p in lista:
                        print(f"{p['rut']:<10} ┃ {p['nombre']:<13} ┃ {p['correo']}")
                        if p.get("productos"):
                            for prod in p["productos"]:
                                print(f"    • {prod['codigo_producto']} @ ${prod['precio_compra']}")
                except json.JSONDecodeError:
                    print("Error al parsear lista:", cuerpo)
            else:
                print("ERROR:", contenido)

        # 2) AGREGAR PROVEEDOR
        elif opcion == "2":
            rut  = input("RUT (8 dígitos): ")
            nom  = input("Nombre: ")
            mail = input("Correo electrónico: ")
            datos    = f"ADD|{rut}|{nom}|{mail}".encode()
            contenido = com_bus(prefijo + datos)  # puede llegar "OK", "OKOK", "NK…", etc.
            if contenido.startswith("OK"):
                print("Proveedor agregado correctamente.")
            else:
                print("Error al agregar:", contenido[2:] if contenido.startswith("NK") else contenido)

        # 3) ELIMINAR PROVEEDOR
        elif opcion == "3":
            rut = input("RUT a eliminar: ")
            datos = f"DEL|{rut}".encode()
            contenido = com_bus(prefijo + datos)
            if contenido.startswith("OK"):
                print("Proveedor eliminado correctamente.")
            else:
                print("Error al eliminar:", contenido[2:] if contenido.startswith("NK") else contenido)

        # 4) AGREGAR PRODUCTO A PROVEEDOR
        elif opcion == "4":
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
    prefijo = b"serv4"
    while True:
        print("\nOpciones:")
        print("1. Generar reporte")
        print("2. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "2":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
        else:
            print("Opción no válida.") 

def registro_compras():
    prefijo = b"serv3"
    while True:
        print("\nOpciones:")
        print("1. Registrar comprar")
        print("2. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "2":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
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
    finally:
        sock.close()
        print("Cliente desconectado del servicio de ventas.")

def gestion_trabajadores():
    prefijo = b"serv1"
    while True:
        print("\nGestión de Trabajadores:")
        print("  1) Listar trabajadores")
        print("  2) Agregar trabajador")
        print("  3) Eliminar trabajador")
        print("  4) Volver al menú")
        opcion = input("Seleccione una opción: ")

        if opcion == "4":
            print("Volviendo al menú...\n")
            break

        # 1) LISTAR
        if opcion == "1":
            mensaje = prefijo + b"fun0"
            contenido = com_bus(mensaje)  # e.g. "OK[...json...]"
            if contenido.startswith("OK"):
                cuerpo = contenido[2:]
                try:
                    lista = json.loads(cuerpo)
                    print("\nRUT     │ Nombre      │ Apellido    │ Cuenta   │ Correo               │ Rol")
                    print("─────────┼──────────────┼─────────────┼──────────┼──────────────────────┼─────")
                    for t in lista:
                        print(f"{t['rut']} ┃ {t['nombre']:<12} ┃ {t['apellido']:<11} ┃ "
                              f"{t['nombre_cuenta']:<8} ┃ {t['correo']:<20} ┃ {t['rol']}")
                except json.JSONDecodeError:
                    print("Error al decodificar JSON:", cuerpo)
            else:
                # si llegó NK o algo inesperado
                print("Error al listar:", contenido[2:] if contenido.startswith("NK") else contenido)

        # 2) AGREGAR
        elif opcion == "2":
            rut     = input("RUT (8 dígitos): ")
            nombre  = input("Nombre: ")
            apellido= input("Apellido: ")
            correo  = input("Correo electrónico: ")
            datos   = f"fun1{rut}|{nombre}|{apellido}|{correo}".encode()
            mensaje = prefijo + datos
            contenido = com_bus(mensaje)  # e.g. "OK{"..."}" o "NK<error>"
            if contenido.startswith("OK"):
                payload = contenido[2:]
                try:
                    info = json.loads(payload)
                    print(f"Trabajador agregado. Cuenta: {info['nombre_cuenta']}, Contraseña: {info['contrasena']}")
                except json.JSONDecodeError:
                    print("Respuesta inesperada al agregar:", payload)
            else:
                print("Error al agregar:", contenido[2:] if contenido.startswith("NK") else contenido)

        # 3) ELIMINAR
        elif opcion == "3":
            rut = input("RUT a eliminar: ")
            datos = f"fun2{rut}".encode()
            mensaje = prefijo + datos
            contenido = com_bus(mensaje)      
            if contenido.startswith("OK"):
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
                usuario = input("Usuario: ")
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