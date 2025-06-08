#!/usr/bin/env python3
import socket
import json

class Proveedor:
    def __init__(self, rut, nombre, correo):
        self.rut = rut
        self.nombre = nombre
        self.correo = correo
        self._productos = {}  # {codigo: precio}

    def to_dict(self):
        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "correo_electronico": self.correo,
            "productos": [
                {"codigo_producto": c, "precio_compra": p}
                for c, p in self._productos.items()
            ]
        }

class ProveedorService:
    def __init__(self):
        self._p = {}

    def listar(self):
        return [prov.to_dict() for prov in self._p.values()]

    def agregar(self, rut, nombre, correo):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        if rut in self._p:
            raise ValueError("Ya existe ese RUT")
        self._p[rut] = Proveedor(rut, nombre, correo)

    def eliminar(self, rut):
        if rut not in self._p:
            raise ValueError("No existe ese RUT")
        del self._p[rut]

    def add_prod(self, rut, cod, precio):
        prov = self._p.get(rut)
        if not prov:
            raise ValueError("Proveedor no existe")
        if len(cod) != 8:
            raise ValueError("Código inválido")
        if precio <= 0:
            raise ValueError("Precio debe ser positivo")
        if cod in prov._productos:
            raise ValueError("Producto ya existe")
        prov._productos[cod] = precio

    def del_prod(self, rut, cod):
        prov = self._p.get(rut)
        if not prov or cod not in prov._productos:
            raise ValueError("Asociación no existe")
        del prov._productos[cod]

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
    svc_name = "serv7"  # 5 caracteres únicos para Gestión de Proveedores
    ps = ProveedorService()

    # 1) Conectar al bus
    host, port = "localhost", 5000
    print(f"Conectando al bus en {host} puerto {port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # 2) Enviar handshake
    handshake = b"00010sinit" + svc_name.encode()
    print(f"Enviando handshake: {handshake!r}")
    sock.sendall(handshake)

    # 3) Esperar ACK
    _, _ = recv_tx(sock)
    print("Handshake aceptado por bus.")

    # 4) Bucle de procesamiento
    while True:
        origen, datos = recv_tx(sock)
        if origen != svc_name:
            continue

        try:
            parts = datos.split("|")
            cmd = parts[0]

            if cmd == "LIST":
                resp = json.dumps(ps.listar())

            elif cmd == "ADD":
                _, rut, nom, mail = parts
                ps.agregar(rut, nom, mail)
                resp = "OK"

            elif cmd == "DEL":
                _, rut = parts
                ps.eliminar(rut)
                resp = "OK"

            elif cmd == "APROD":
                _, rut, cod, pr = parts
                ps.add_prod(rut, cod, int(pr))
                resp = "OK"

            elif cmd == "DPROD":
                _, rut, cod = parts
                ps.del_prod(rut, cod)
                resp = "OK"

            else:
                raise ValueError(f"Código desconocido: {cmd}")

            send_tx(sock, svc_name, "OK" + resp)

        except Exception as e:
            send_tx(sock, svc_name, "NK" + str(e))

if __name__ == "__main__":
    main()
