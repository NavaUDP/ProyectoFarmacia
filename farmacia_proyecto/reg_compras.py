#Código para las compras de la farmacia
import socket
import psycopg2
import os
import uuid
from datetime import datetime
import math

# COnfiguración de base de datos
DB_NAME = os.getenv("DB_NAME", "farmacia")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

#Configuración del servicio
SERVICE_NAME = "serv3"
HOST = 'localhost'
PORT = 5000

#Lógica del servicio
#Información en forma de:
# "RUT_TRABAJADOR; RUT_PROVEEDOR; CODIGO1, CANTIDAD1, CODIGO2, CANTIDAD2, ...""

def process_purchase(payload: str):
    conn = None
    try:
        #Descomponer el payload
        parts = payload.strip().split(';')
        rut_trabajador = parts[0]
        rut_proveedor = parts[1]

        #Lista de productos y cantidades
        items_str = parts[2:]
        if not items_str:
            return "NK", "No se especificaron productos para la compra."
        
        items_to_buy = []
        for item in items_str:
            code, qty_str = item.split(',')
            items_to_buy.append({'codigo': code, 'cantidad': int(qty_str)})

        #Conexión con la base de datos
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()

        # -- Inicio de compra --
        total_compra_bruto = 0
        productos_info = {}

        #Verificar proveedor existe 
        for item in items_to_buy:
            cursor.execute(
                "SELECT rut_proveedor, precio_compra, codigo_producto FROM producto_proveedor WHERE rut_proveedor = %s AND codigo_producto = %s",
                (rut_proveedor, item['codigo'])
            )
            producto = cursor.fetchone()
            if not producto:
                return "NK", f"El producto {item['codigo']} no está asociado al proveedor {rut_proveedor}."
            

            rut_proveedor_db, precio_compra, codigo_producto = producto
            total_compra_bruto += item['cantidad'] * precio_compra
            productos_info[item['codigo']] = {'precio_compra': precio_compra}

        #Registrar en la tabla de compras
        id_compra = uuid.uuid4()
        cursor.execute(
             """
            INSERT INTO compra (id_compra, fecha, total_compra)
            VALUES (%s, %s, %s)
            """,
            (str(id_compra), datetime.now(), total_compra_bruto)
        )

        #Insertar en detalle compra
        for item in items_to_buy:
            id_detalle = uuid.uuid4()
            cursor.execute(
                """
                INSERT INTO detalle_compra (id_detalle, id_compra, id_producto_proveedor, cantidad, precio_unitario)
                VALUES (%s, %s, (SELECT id_producto_proveedor FROM producto_proveedor WHERE rut_proveedor = %s AND codigo_producto = %s), %s, %s)
                """,
                (str(id_detalle), str(id_compra), rut_proveedor, item['codigo'], item['cantidad'], productos_info[item['codigo']]['precio_compra'])
            )       
        #Finalizar transacción
        conn.commit()
        return "OK", f"Compra registrada exitosamente. ID de compra: {id_compra}."

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        #print(f"Error de base de datos: {e}")
        return "NK", "Error interno en la base de datos."
    except (ValueError, IndexError, KeyError) as e:
        print(f"Error en el formato del payload: {e}")
        return "NK", "Formato de payload incorrecto."
    finally:
        if conn:
            cursor.close()
            conn.close()

# -- Funciones del bus --
def format_response(service_name, status, data):
    response_body = f"{service_name}{status}{data}"
    # NNNNN es la longitud de SSSSS + STATUS + DATOS
    # SSSSS: 5, STATUS: 2, DATOS: len(data)
    length = 5 + 2 + len(data) 
    header = f"{length:05d}"
    return f"{header}{response_body}"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    print('Conectando al bus en {} puerto {}'.format(*bus_address))
    sock.connect(bus_address)

    # Enviar handshake inicial
    message = b'00010sinitserv3'
    print('Enviando handshake: {!r}'.format(message))
    sock.sendall(message)
    sinit = 1

    try:
        while True:
            # Esperar respuesta del bus
            amount_expected = int(sock.recv(5))
            amount_received = 0
            data = b""
            while amount_received < amount_expected:
                chunk = sock.recv(amount_expected - amount_received)
                amount_received += len(chunk)   
                data += chunk

            if sinit == 1:
                sinit = 0
                print("Handshake aceptado por bus.")
                continue

            # Procesar el payload recibido
            payload = data.decode()
            #print(f"Mensaje recibido: {payload}")
            #print(f"Mensaje recibido (repr): {repr(payload)}")

            if payload.startswith("serv3"):
                command = payload[5:] if payload[5] != ' ' else payload[6:]
                status, message = process_purchase(command)

                response = format_response(SERVICE_NAME, status, message)
                #print(f"Enviando respuesta: {response}")
                sock.sendall(response.encode())
            else:
                print("Mensaje recibido no es para este servicio.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:    
        sock.close()

if __name__ == "__main__":
    main()