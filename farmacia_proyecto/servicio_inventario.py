import socket
import psycopg2

def modificar_stock(payload):
    try:
        codigo, stock = payload.split('|')
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres", #Poner su usuario
            password="postgres", #poner su contraseña
            host="localhost",
            port=5432
        )

        cursor = conn.cursor()
        query = """
            UPDATE producto
            SET stock = stock + %s
            WHERE codigo_producto = %s AND stock + %s >= 0;
        """
        cursor.execute(query, (stock, codigo, stock))
        conn.commit()

        if cursor.rowcount == 1:
            return True
        else:
            return False
    except Exception as e:
        print("Ocurrió un error:", e)
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def listar_productos():
    try:
        conn = psycopg2.connect(
            dbname="farmacia",
            user="", #Poner su usuario
            password="", #poner su contraseña
            host="localhost"
        )
        cursor = conn.cursor()
        
        query = "SELECT * FROM producto;"
        cursor.execute(query)
        
        productos = cursor.fetchall()
        return str(productos)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()



def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    print('Conectando al bus en {} puerto {}'.format(*bus_address))
    sock.connect(bus_address)

    # Enviar handshake inicial
    message = b'00010sinitserv5'
    print('Enviando handshake: {!r}'.format(message))
    sock.sendall(message)
    sinit = 1

    try:
        while True:
            # Esperar respuesta del bus (handshake o login requests)
            amount_expected = int(sock.recv(5))
            amount_received = 0
            data = b""
            while amount_received < amount_expected:
                chunk = sock.recv(amount_expected - amount_received)
                amount_received += len(chunk)
                data += chunk
            print(f"Mensaje recibido: {data}")

            if sinit == 1:
                sinit = 0
                print("Handshake aceptado por bus.")
            else:
                #print(f"Mensaje recibido completo (raw): {data}")

                mensaje = data.decode()
                prefijo = mensaje[:5]
                funcion = mensaje[5:9]
                contenido = mensaje[9:]
                if funcion == "fun0":
                    respuesta_texto = "serv5" + listar_productos()
                else:
                    valido = modificar_stock(contenido)
                    respuesta_texto = "serv5VALID" if valido else "serv5INVALID"
                
                # Preparar respuesta

                respuesta_bytes = respuesta_texto.encode()
                size = f"{len(respuesta_bytes):05}".encode()
                respuesta = size + respuesta_bytes

                #print(f"Enviando respuesta: {respuesta}")
                sock.sendall(respuesta)

    except Exception as e:
        print(f"Error en servicio: {e}")
    finally:
        sock.close()
        print("Servicio desconectado.")

if __name__ == "__main__":
    main()
