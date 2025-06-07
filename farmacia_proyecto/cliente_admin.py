import socket
import ast
import os
import platform
import sys

nombre_usuario = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('localhost', 5000)
print('Conectando al bus en {} puerto {}'.format(*bus_address))
sock.connect(bus_address)


def limpiar_consola():
    comando = 'cls' if platform.system() == 'Windows' else 'clear'
    os.system(comando)

#Función para comunicarse con el bus
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
        print("\nOpciones:")
        print("1. Agregar cliente miembro")
        print("2. Eliminar cliente miembro")
        print("3. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "3":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
        elif opcion == "2":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
        else:
            print("Opción no válida.") 

def gestion_proveedores():
    prefijo = b"serv7"
    while True:
        print("\nOpciones:")
        print("1. Agregar proveedor")
        print("2. Eliminar proveedor")
        print("3. Agregar producto a proveedor")
        print("4. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "4":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
        elif opcion == "2":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
        elif opcion == "3":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
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
    while True:
        print("\nOpciones:")
        print("1. Registrar venta")
        print("2. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "2":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
        else:
            print("Opción no válida.") 

def gestion_trabajadores():
    prefijo = b"serv1"
    while True:
        print("\nOpciones:")
        print("1. Agregar trabajador")
        print("2. Eliminar trabajador")
        print("3. Volver al menú")

        opcion = input("Seleccione una opción: ")
        if opcion == "3":
            print("Volviendo al menú...\n")
            break
        elif opcion == "1":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
        elif opcion == "2":
            print(f"Ejecutando función {opcion} (sin acción por ahora).")
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
