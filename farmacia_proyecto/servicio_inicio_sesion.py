import socket
import psycopg2

def verificar_credenciales(payload):
    try:
        mensaje = payload.decode()
        contenido = mensaje[5:]
        usuario, password, rol = contenido.split('|')
        rol = rol.strip().lower() in ['true', '1', 'yes']
        conn = psycopg2.connect(
            dbname="farmacia",
            user="postgres", #poner su nombre
            password="postgres", #poner su contraseña
            host="localhost"
        )

        cursor = conn.cursor()

        query = """
        SELECT EXISTS (
            SELECT 1 FROM trabajador
            WHERE rut_trabajador = %s AND contraseña = %s AND rol = %s
        );
        """
        cursor.execute(query, (usuario, password, rol))
        estado = cursor.fetchone()[0]

        return estado
    except Exception as e:
        print("Ocurrió un error:", e)
        return False
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
    message = b'00010sinitserv0'
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
            #print(f"Mensaje recibido: {data}")

            if sinit == 1:
                sinit = 0
                print("Handshake aceptado por bus.")
            else:
                # Verificar credenciales
                valido = verificar_credenciales(data)

                # Preparar respuesta
                respuesta_texto = "serv0VALID" if valido else "serv0INVALID"
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
