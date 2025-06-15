import socket
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import smtplib

class TrabajadorServiceDB:
    def __init__(self):
        
        self.conn = psycopg2.connect(
            dbname="farmacia",
            user="postgres", # Poner nombre
            password="postgres", # Poner contraseña
            host="localhost",
        )
        # Usamos RealDictCursor para obtener filas como dict
        self.conn.autocommit = True

    def listar(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT rut_trabajador AS rut,
                       nombre,
                       apellido,
                       contraseña   AS contrasena,
                       correo_electronico AS correo,
                       rol
                  FROM trabajador
                  ORDER BY rut_trabajador
            """)
            return cur.fetchall()  # lista de dicts

    def agregar(self, rut, nombre, apellido, correo):
        # Validaciones iguales a antes
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        # Generamos password al vuelo
        pwd = self._gen_pass()

        with self.conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO trabajador (
                      rut_trabajador, nombre, apellido, contraseña, correo_electronico, rol
                    ) VALUES (
                      %s, %s, %s,
                      %s, %s, %s
                    )
                """, (rut, nombre, apellido, pwd, correo, False))
            except psycopg2.IntegrityError:
                raise ValueError(f"Ya existe un trabajador con RUT '{rut}'.")
            try:
                smtp_server = 'smtp.gmail.com'
                smtp_user = '' #tu correo
                smtp_password = '' #tu app password

                # Enviar el correo
                with smtplib.SMTP(smtp_server, 587) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.sendmail(smtp_user, correo, 
                                    f"Subject: Usuario creado en la farmacia para el rut {rut} \nTu contrasena es {pwd}")
            except smtplib.SMTPRecipientsRefused:
                cur.execute("""
                DELETE FROM trabajador
                  WHERE rut_trabajador = %s
                """, (rut,))
                raise ValueError(f"Correo rechazado: '{correo}' no existe")
        return {"rut": rut}

    def eliminar(self, rut):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM trabajador
                  WHERE rut_trabajador = %s
            """, (rut,))
            if cur.rowcount == 0:
                raise ValueError(f"No existe trabajador con RUT '{rut}'.")

    def _gen_pass(self, length=8):
        import string, random
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(length))

    def close(self):
        self.conn.close()

# -------------------------
# COMUNICACIÓN CON EL BUS
# -------------------------

def send_tx(sock, svc, datos):
    payload = svc + datos
    header = f"{len(payload):05d}"
    sock.sendall(header.encode() + payload.encode())

def recv_tx(sock):
    header = sock.recv(5)
    if not header:
        raise ConnectionError("Bus desconectado")
    n = int(header.decode())
    buf = b''
    while len(buf) < n:
        buf += sock.recv(n - len(buf))
    data = buf.decode()
    return data[:5], data[5:]

def main():
    svc_name = "serv1"  # coincide con cliente_admin
    servicio = TrabajadorServiceDB()

    # 1) Conexión al BUS
    bus_host, bus_port = "localhost", 5000
    print(f"Conectando al bus en {bus_host} puerto {bus_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((bus_host, bus_port))

    # 2) Handshake
    handshake = b'00010sinit' + svc_name.encode()
    print(f"Enviando handshake: {handshake!r}")
    sock.sendall(handshake)

    # 3) Esperar ACK
    _, _ = recv_tx(sock)
    print("Handshake aceptado por bus.")

    # 4) Bucle de procesamiento
    try:
        while True:
            origen, datos = recv_tx(sock)
            if origen != svc_name:
                continue

            try:
                funcion = datos[:4]
                contenido = datos[4:]
                if funcion == "fun0":
                    # Listar
                    lista = servicio.listar()
                    resp = json.dumps(lista)
                elif funcion == "fun1":
                    # Agregar: contenido = "RUT|Nombre|Apellido|Correo"
                    rut, nombre, apellido, correo = contenido.split("|")
                    out = servicio.agregar(rut, nombre, apellido, correo)
                    resp = json.dumps(out)
                elif funcion == "fun2":
                    # Eliminar: contenido = "RUT"
                    servicio.eliminar(contenido)
                    resp = "OK"
                else:
                    raise ValueError(f"Código de función desconocido: {funcion}")

                send_tx(sock, svc_name, "OK" + resp)

            except Exception as e:
                send_tx(sock, svc_name, "NK" + str(e))

    finally:
        servicio.close()
        sock.close()

if __name__ == "__main__":
    main()
