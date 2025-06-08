#!/usr/bin/env python3
import socket
import string
import random
import json

class Trabajador:
    def __init__(self, rut, nombre, apellido, correo, cuenta, contrasena, rol):
        self.rut = rut
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.cuenta = cuenta
        self.contrasena = contrasena
        self.rol = rol

    def to_dict(self):
        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_cuenta": self.cuenta,
            "correo_electronico": self.correo,
            "rol": self.rol
        }

class TrabajadorService:
    def __init__(self):
        self._trabajadores = {}

    def _gen_pass(self, length=8):
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(length))

    def listar(self):
        return [t.to_dict() for t in self._trabajadores.values()]

    def agregar(self, rut, nombre, apellido, correo):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        if rut in self._trabajadores:
            raise ValueError("Ya existe ese RUT")
        cuenta = rut[:7]
        pwd = self._gen_pass()
        t = Trabajador(rut, nombre, apellido, correo, cuenta, pwd, 0)
        self._trabajadores[rut] = t
        return {"nombre_cuenta": cuenta, "contrasena": pwd}

    def eliminar(self, rut):
        if rut not in self._trabajadores:
            raise ValueError("No existe ese RUT")
        del self._trabajadores[rut]

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
    svc_name = "serv1"  # para gestión de Trabajadores
    ts = TrabajadorService()

    # Conexión
    bus_address = ("localhost", 5000)
    print(f"Conectando al bus en {bus_address[0]} puerto {bus_address[1]}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(bus_address)

    # Handshake
    handshake = b"00010sinit" + svc_name.encode()
    print(f"Enviando handshake: {handshake!r}")
    sock.sendall(handshake)

    # Esperar ACK
    _, _ = recv_tx(sock)
    print("Handshake aceptado por bus.")

    # Procesamiento de peticiones
    while True:
        origen, datos = recv_tx(sock)
        if origen != svc_name:
            continue

        try:
            parts = datos.split("|")
            cmd = parts[0]
            if cmd == "LIST":
                resp = json.dumps(ts.listar())
            elif cmd == "ADD":
                _, rut, nombre, apellido, correo = parts
                out = ts.agregar(rut, nombre, apellido, correo)
                resp = json.dumps(out)
            elif cmd == "DEL":
                _, rut = parts
                ts.eliminar(rut)
                resp = "OK"
            else:
                raise ValueError(f"Código desconocido: {cmd}")

            send_tx(sock, svc_name, "OK" + resp)
        except Exception as e:
            send_tx(sock, svc_name, "NK" + str(e))

if __name__ == "__main__":
    main()
