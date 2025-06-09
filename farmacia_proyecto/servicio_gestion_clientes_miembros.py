#!/usr/bin/env python3
import socket
import json
import psycopg2
from psycopg2.extras import RealDictCursor

class MiembroServiceDB:
    def __init__(self):
        
        self.conn = psycopg2.connect(
            dbname="farmacia",
            user="", # Poner nombre
            password="", # Poner contraseña
            host="localhost",
                                # Poner puerto (port=PUERTO)
        )
        # Usar RealDictCursor para obtener filas como dict
        self.conn.autocommit = True

    def listar(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                  rut_miembro   AS rut,
                  nombre,
                  apellido,
                  correo_electronico AS correo,
                  puntos_acumulados  AS puntos
                FROM miembro
                ORDER BY rut_miembro
            """)
            return cur.fetchall()  # lista de dicts

    def agregar(self, rut, nombre, apellido, correo):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        with self.conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO miembro (
                      rut_miembro, nombre, apellido, correo_electronico, puntos_acumulados
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (rut, nombre, apellido, correo, 0))
            except psycopg2.IntegrityError:
                raise ValueError(f"Ya existe un miembro con RUT '{rut}'.")

    def eliminar(self, rut):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM miembro
                 WHERE rut_miembro = %s
            """, (rut,))
            if cur.rowcount == 0:
                raise ValueError(f"No existe un miembro con RUT '{rut}'.")

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
    svc_name = "serv8"  # coincide con cliente_admin.py
    servicio = MiembroServiceDB()

    # 1) Conectar al bus
    host, port = "localhost", 5000
    print(f"Conectando al bus en {host} puerto {port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # 2) Handshake
    handshake = b"00010sinit" + svc_name.encode()
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
                parts = datos.split("|")
                cmd = parts[0]

                if cmd == "LIST":
                    miembros = servicio.listar()
                    resp = json.dumps(miembros)

                elif cmd == "ADD":
                    _, rut, nom, ape, mail = parts
                    servicio.agregar(rut, nom, ape, mail)
                    resp = "OK"

                elif cmd == "DEL":
                    _, rut = parts
                    servicio.eliminar(rut)
                    resp = "OK"

                else:
                    raise ValueError(f"Código desconocido: {cmd}")

                send_tx(sock, svc_name, "OK" + resp)

            except Exception as e:
                send_tx(sock, svc_name, "NK" + str(e))

    finally:
        servicio.close()
        sock.close()

if __name__ == "__main__":
    main()
