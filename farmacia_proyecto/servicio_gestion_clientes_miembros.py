#!/usr/bin/env python3
import socket
import json


class ClienteMiembro:
    def __init__(self, rut, nombre, apellido, correo):
        self.rut = rut
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.puntos = 0

    def to_dict(self):
        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo_electronico": self.correo,
            "puntos_acumulados": self.puntos
        }

class MiembroService:
    def __init__(self):
        self._m = {}

    def listar(self):
        return [m.to_dict() for m in self._m.values()]

    def agregar(self, rut, nombre, apellido, correo):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        if rut in self._m:
            raise ValueError("Ya existe ese RUT")
        self._m[rut] = ClienteMiembro(rut, nombre, apellido, correo)

    def eliminar(self, rut):
        if rut not in self._m:
            raise ValueError("No existe ese RUT")
        del self._m[rut]

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
    svc_name = "serv8"  # 5 caracteres para Gestión de Clientes Miembros
    ms = MiembroService()

    # Conectar al bus
    host, port = "localhost", 5000
    print(f"Conectando al bus en {host} puerto {port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # Handshake
    handshake = b"00010sinit" + svc_name.encode()
    print(f"Enviando handshake: {handshake!r}")
    sock.sendall(handshake)

    # Esperar ACK
    _, _ = recv_tx(sock)
    print("Handshake aceptado por bus.")

    # Bucle de procesamiento
    while True:
        origen, datos = recv_tx(sock)
        if origen != svc_name:
            continue

        try:
            parts = datos.split("|")
            cmd = parts[0]

            if cmd == "LIST":
                resp = json.dumps(ms.listar())

            elif cmd == "ADD":
                _, rut, nom, ape, mail = parts
                ms.agregar(rut, nom, ape, mail)
                resp = "OK"

            elif cmd == "DEL":
                _, rut = parts
                ms.eliminar(rut)
                resp = "OK"

            else:
                raise ValueError(f"Código desconocido: {cmd}")

            send_tx(sock, svc_name, "OK" + resp)

        except Exception as e:
            send_tx(sock, svc_name, "NK" + str(e))

if __name__ == "__main__":
    main()
