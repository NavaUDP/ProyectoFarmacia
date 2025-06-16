import socket
import ast
import os
import platform
import sys
import json

rut_trabajador = ""

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
    #print(respuesta)
    contenido = respuesta[7:]
    return contenido


def gestion_clientes_miembros():
    prefijo = b"serv8"
    while True:
        mensaje = prefijo + b"LIST"
        contenido = com_bus(mensaje)   # e.g. "OK[...json...]"
        if contenido.startswith("OK"):
            cuerpo = contenido[2:]
            try:
                lista = json.loads(cuerpo)

                # Imprimir encabezado
                print("+--------------+--------------+--------------+--------------------------+--------+")
                print("| RUT          | Nombre       | Apellido     | Correo                   | Puntos |")
                print("+--------------+--------------+--------------+--------------------------+--------+")

                for m in lista:
                    print(f"| {m['rut']:<12} | {m['nombre']:<12} | {m['apellido']:<12} | {m['correo']:<24} | {str(m['puntos']):>6} |")

                print("+--------------+--------------+--------------+--------------------------+--------+")
            except json.JSONDecodeError:
                print("Error al decodificar JSON:", cuerpo)
        else:
            print("Error al listar:", contenido)

        print("\nGestión de Clientes Miembros:")
        print("  1) Agregar cliente miembro")
        print("  2) Eliminar cliente miembro")
        print("  3) Volver al menú")
        opcion = input("Seleccione una opción: ")

        if opcion == "3":
            print("Volviendo al menú...\n")
            break

        # 1) AGREGAR
        if opcion == "1":
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

def gestion_inventario():
    prefijo = b"serv5"
    while True:
        mensaje = b"serv6" + b"fun0"
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
            stock = input("Stock a agregar (+) o restar (-): ")
            datos = f"{codigo}|{stock}".encode()
            mensaje = prefijo + datos
            contenido = com_bus(mensaje)
            if contenido == "VALID":
                print("Cambio de stock válido.")
            else:
                print("Cambio de stock inválido.")
        else:
            print("Opción no válida.") 

def registro_compras():
    prefijo = b"serv3"
    while True:
        mensaje = b"serv7" + b"LIST"
        contenido = com_bus(mensaje)
        if contenido.startswith("OK"):
            cuerpo = contenido[2:]
            try:
                lista = json.loads(cuerpo)
                print("-" * 80) 
                for proveedor in lista:
                    print(f"Proveedor: {proveedor['nombre']} (RUT: {proveedor['rut']})")
                    print(f"Correo: {proveedor['correo']}")
                    print("Productos asociados:")
                    for producto in proveedor['productos']:
                        print(f"  - Código: {producto['codigo_producto']:<10} | "
                            f"Nombre: {producto['nombre_producto']:<20} | "
                            f"Precio Compra: ${producto['precio_compra']}")
                    print("-" * 80)
            except json.JSONDecodeError:
                print("Error al parsear lista:", cuerpo)
        else:
            print("ERROR:", contenido)

        print("\nOpciones:")
        print("1. Registrar compra")
        print("2. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "2":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            # Ejecuta el servicio de registro de compras
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
            mensaje = b"serv6" + b"fun0"
            contenido = com_bus(mensaje)

            productos = ast.literal_eval(contenido)
            print("\nLista de productos:")
            for p in productos:
                codigo, nombre, stock, precio = p
                print(f"Código: {codigo:<10} | Nombre: {nombre:<15} | Stock: {stock:<5} | Precio: ${precio}")
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
                #rut_trabajador = input("Ingrese su RUT (8 dígitos): ")
                #if len(rut_trabajador) != 8 or not rut_trabajador.isdigit():
                 #   print("RUT inválido. Debe tener 8 dígitos.")
                  #  continue
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

def mostrar_menu():
    while True:
        print("\nOpciones:")
        print("1. Registro de ventas")
        print("2. Registro de compras")
        print("3. Gestión de inventario")
        print("4. Gestión de clientes miembros")
        print("5. Volver a inicio de sesión")

        opcion = input("Seleccione una opción: ")
        if opcion == "5":
            print("Volviendo a inicio de sesión...\n")
            break
        elif opcion == "1" :
            registro_ventas()
        elif opcion == "2":
            registro_compras()
        elif opcion == "3":
            gestion_inventario()
        elif opcion == "4":
            gestion_clientes_miembros()
        else:
            print("Opción no válida.")
     
def main():
    limpiar_consola()
    prefijo = b"serv0"
    global rut_trabajador
    try:
        while True:
            print("1. Iniciar Sesión")
            print("2. Salir del sistema")

            opcion = input("Seleccione una opción: ")
            if opcion == "1":
                usuario = input("RUT: ")
                password = input("Password: ")
                
                credenciales = f"{usuario}|{password}|False".encode()
                mensaje = prefijo + credenciales
                
                contenido = com_bus(mensaje)
                if contenido == "VALID":
                    print("Inicio de sesión válido.")
                    rut_trabajador = usuario
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