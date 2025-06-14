import socket
import psycopg2
import os
import json
from datetime import date
import math

# Configuración de base de datos
DB_NAME = os.getenv("DB_NAME", "farmacia")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Configuracion del servicio
SERVICE_NAME = "serv4" #5 caracteres
HOST = 'localhost'
PORT = 5000

def generar_reporte(mes_anio: str):
    """
    Genera un reporte de ventas y compras para un mes y año específicos.
    Args:
        mes_anio: String en formato 'YYYY-MM'.
    Returns:
        Un diccionario con los datos del reporte.
    """
    conn = None
    reporte = {}
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()

        # 1. Métricas de Ventas
        cur.execute("""
            SELECT 
                COALESCE(SUM(total_venta_final), 0) AS monto_total,
                COALESCE(SUM(dv.cantidad), 0) AS cantidad_total
            FROM venta v
            JOIN detalle_venta dv ON v.id_venta = dv.id_venta
            WHERE TO_CHAR(v.fecha, 'YYYY-MM') = %s;
        """, (mes_anio,))
        ventas_res = cur.fetchone()
        reporte['ventas_monto_total'] = int(ventas_res[0])
        reporte['ventas_cantidad_total'] = int(ventas_res[1])

        # 2. Top 3 Productos Vendidos
        cur.execute("""
            SELECT p.nombre, SUM(dv.cantidad) as total_vendido
            FROM detalle_venta dv
            JOIN venta v ON dv.id_venta = v.id_venta
            JOIN producto p ON dv.codigo_producto = p.codigo_producto
            WHERE TO_CHAR(v.fecha, 'YYYY-MM') = %s
            GROUP BY p.nombre
            ORDER BY total_vendido DESC
            LIMIT 3;
        """, (mes_anio,))
        reporte['ventas_top_3_productos'] = [row[0] for row in cur.fetchall()]

        # 3. Métricas de Compras
        cur.execute("""
            SELECT
                COALESCE(SUM(c.total_compra), 0) as monto_total,
                COALESCE(SUM(dc.cantidad), 0) as cantidad_total
            FROM compra c
            JOIN detalle_compra dc ON c.id_compra = dc.id_compra
            WHERE TO_CHAR(c.fecha, 'YYYY-MM') = %s;
        """, (mes_anio,))
        compras_res = cur.fetchone()
        reporte['compras_monto_total'] = int(compras_res[0])
        reporte['compras_cantidad_total'] = int(compras_res[1])

        # 4. Top 3 Productos Comprados
        cur.execute("""
            SELECT p.nombre, SUM(dc.cantidad) as total_comprado
            FROM detalle_compra dc
            JOIN compra c ON dc.id_compra = c.id_compra
            JOIN producto_proveedor pp ON dc.id_producto_proveedor = pp.id_producto_proveedor
            JOIN producto p ON pp.codigo_producto = p.codigo_producto
            WHERE TO_CHAR(c.fecha, 'YYYY-MM') = %s
            GROUP BY p.nombre
            ORDER BY total_comprado DESC
            LIMIT 3;
        """, (mes_anio,))
        reporte['compras_top_3_productos'] = [row[0] for row in cur.fetchall()]

        # 5. Ganancia
        reporte['ganancia_total'] = reporte['ventas_monto_total'] - reporte['compras_monto_total']

        return "OK", reporte

    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        return "NK", "Error interno en la base de datos."
    except Exception as e:
        print(f"Error inesperado: {e}")
        return "NK", str(e)
    finally:
        if conn:
            cur.close()
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
    message = b'00010sinitserv4'
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

            #Procesar el payload recibido
            payload = data.decode()
            print(f"Mensaje recibido: {payload}")

            if payload.startswith("serv4"):
                command = payload[5:] if payload[5] != ' ' else payload[6:]
                status, reporte_data = generar_reporte(command)

                if status == "OK":
                    response_data = json.dumps(reporte_data)
                else:
                    response_data = "NK" + str(reporte_data)
                
                response = format_response(SERVICE_NAME, status, response_data)
                print(f"Enviando respuesta: {response}")
                sock.sendall(response.encode())
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
