import socket
import psycopg2
import os
import uuid
from datetime import date
import math

# Configuración de base de datos
DB_NAME = os.getenv("DB_NAME", "farmacia")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Configuracion del servicio
SERVICE_NAME = "serv2" #5 caracteres
HOST = 'localhost'
PORT = 5000

# -- Lógica del servicio --
#Recibe la informaicion en forma de : 
# "RUT_CLIENTE, PUNTOS_USADOS, RUT_TRABAJADOR; CODIGO1, CANTIDAD1, CODIGO2, CANTIDAD2, ..."

def process_sale(payload: str):
    """
    Procesa la lógica de registrar una venta.
    Formato del payload esperado:
    RUT_MIEMBRO;PUNTOS_USADOS;RUT_TRABAJADOR;CODIGO1,CANTIDAD1;CODIGO2,CANTIDAD2;...
    - RUT_MIEMBRO y PUNTOS_USADOS pueden ser 'None' si no aplica.
    - RUT_TRABAJADOR es el RUT del empleado que realiza la venta.
    """
    conn = None
    try:
        # Descomponer el payload
        parts = payload.strip().split(';')
        rut_miembro = parts[0] if parts[0].upper() != 'NONE' else None
        puntos_usados_str = parts[1] if parts[1].upper() != 'NONE' else '0'
        puntos_usados = int(puntos_usados_str)
        rut_trabajador = parts[2]
        
        # Lista de productos y cantidades
        items_str = parts[3:]
        if not items_str:
            return "NK", "No se especificaron productos para la venta."
            
        items_to_sell = []
        for item in items_str:
            code, qty_str = item.split(',')
            items_to_sell.append({'codigo': code, 'cantidad': int(qty_str)})

        # Conectar a la base de datos
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()

        # --- Iniciar Transacción ---
        total_venta_bruto = 0
        productos_info = {}

        # 1. Validar stock y calcular total bruto
        for item in items_to_sell:
            cursor.execute(
                "SELECT stock, precio_venta, nombre FROM producto WHERE codigo_producto = %s",
                (item['codigo'],)
            )
            producto = cursor.fetchone()
            if not producto:
                conn.rollback()
                return "NK", f"Producto con código {item['codigo']} no existe."
            
            stock_actual, precio_venta, nombre_prod = producto
            if stock_actual < item['cantidad']:
                conn.rollback()
                return "NK", f"Stock insuficiente para el producto '{nombre_prod}'. Stock actual: {stock_actual}."
            
            total_venta_bruto += item['cantidad'] * precio_venta
            productos_info[item['codigo']] = {'precio_venta': precio_venta}

        # 2. Validar y procesar puntos del miembro (si aplica)
        puntos_ganados = 0
        if rut_miembro:
            cursor.execute("SELECT puntos_acumulados FROM miembro WHERE rut_miembro = %s FOR UPDATE", (rut_miembro,))
            miembro = cursor.fetchone()
            if not miembro:
                conn.rollback()
                return "NK", f"Cliente miembro con RUT {rut_miembro} no existe."
            
            puntos_actuales = miembro[0]
            if puntos_usados > puntos_actuales:
                conn.rollback()
                return "NK", f"El cliente no tiene suficientes puntos. Puntos actuales: {puntos_actuales}."
            
            # 1 punto = 1 peso. No se pueden usar más puntos que el total de la venta.
            if puntos_usados > total_venta_bruto:
                conn.rollback()
                return "NK", "No se pueden usar más puntos que el monto total de la venta."

        # 3. Calcular total final y puntos ganados
        total_venta_final = total_venta_bruto - puntos_usados
        # Gana 150 puntos por cada 1000 pesos del monto final pagado
        puntos_ganados = math.floor(total_venta_final / 1000) * 150

        # 4. Actualizar stock de productos
        for item in items_to_sell:
            cursor.execute(
                "UPDATE producto SET stock = stock - %s WHERE codigo_producto = %s",
                (item['cantidad'], item['codigo'])
            )

        # 5. Actualizar puntos del miembro (si aplica)
        if rut_miembro:
            puntos_finales = puntos_actuales - puntos_usados + puntos_ganados
            cursor.execute(
                "UPDATE miembro SET puntos_acumulados = %s WHERE rut_miembro = %s",
                (puntos_finales, rut_miembro)
            )
        
        # 6. Insertar en la tabla 'venta'
        id_venta = uuid.uuid4()
        cursor.execute(
            """
            INSERT INTO venta (id_venta, rut_miembro, rut_trabajador, fecha, total_venta_bruto, puntos_usados, total_venta_final)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (str(id_venta), rut_miembro, rut_trabajador, date.today(), total_venta_bruto, puntos_usados, total_venta_final)
        )

        # 7. Insertar en 'detalle_venta'
        for item in items_to_sell:
            id_detalle = uuid.uuid4()
            cursor.execute(
                """
                INSERT INTO detalle_venta (id_detalle, id_venta, codigo_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (str(id_detalle), str(id_venta), item['codigo'], item['cantidad'], productos_info[item['codigo']]['precio_venta'])
            )

        # --- Finalizar Transacción ---
        conn.commit()
        return "OK", f"Venta registrada exitosamente. ID de Venta: {id_venta}"

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        #print(f"Error de base de datos: {e}")
        return "NK", "Error interno en la base de datos."
    except (ValueError, IndexError, KeyError) as e:
        #print(f"Error en el formato del payload: {e}")
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
    message = b'00010sinitserv2'
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

            if payload.startswith("serv2"):
                command = payload[5:] if payload[5] != ' ' else payload[6:]
                status, message = process_sale(command)

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