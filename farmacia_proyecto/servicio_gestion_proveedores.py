import socket
import json
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor


class ProveedorServiceDB:
    def __init__(self):
        # Conectar a la BD 'farmacia'
        self.conn = psycopg2.connect(
            dbname="farmacia",
            user="", # Poner nombre
            password="", # Poner contraseña
            host="localhost",
                                # Poner puerto
        )
        # Usamos RealDictCursor para obtener filas como dict
        self.conn.autocommit = True

    def listar(self):
        # Traer todos los proveedores
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT rut_proveedor AS rut,
                       nombre,
                       correo_electronico AS correo
                  FROM proveedor
                 ORDER BY rut_proveedor
            """)
            proveedores = cur.fetchall()

        # Traer todas las asociaciones producto_proveedor
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT codigo_producto,
                       rut_proveedor,
                       precio_compra
                  FROM producto_proveedor
            """)
            filas = cur.fetchall()

        # Mapear rut_proveedor → lista de productos
        prod_map: dict[str, list[dict]] = {}
        for f in filas:
            prod_map.setdefault(f['rut_proveedor'], []).append({
                "codigo_producto": f['codigo_producto'],
                "precio_compra": f['precio_compra']
            })

        # Adjuntar lista de productos a cada proveedor
        resultado = []
        for p in proveedores:
            p['productos'] = prod_map.get(p['rut'], [])
            resultado.append(p)
        return resultado

    def agregar(self, rut, nombre, correo):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        with self.conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO proveedor (
                      rut_proveedor, nombre, correo_electronico
                    ) VALUES (%s, %s, %s)
                """, (rut, nombre, correo))
            except psycopg2.IntegrityError:
                raise ValueError(f"Ya existe un proveedor con RUT '{rut}'.")
    
    def eliminar(self, rut):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM proveedor
                 WHERE rut_proveedor = %s
            """, (rut,))
            if cur.rowcount == 0:
                raise ValueError(f"No existe un proveedor con RUT '{rut}'.")

    def add_prod(self, rut, cod, precio):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        if len(cod) != 8:
            raise ValueError("Código de producto inválido")
        if precio <= 0:
            raise ValueError("Precio debe ser positivo")

        with self.conn.cursor() as cur:
            # Verificar que el proveedor existe
            cur.execute("""
                SELECT 1 FROM proveedor WHERE rut_proveedor = %s
            """, (rut,))
            if cur.fetchone() is None:
                raise ValueError("Proveedor no existe")
            # Verificar que no exista ya esa asociación
            cur.execute("""
                SELECT 1
                  FROM producto_proveedor
                 WHERE rut_proveedor = %s
                   AND codigo_producto = %s
            """, (rut, cod))
            if cur.fetchone():
                raise ValueError("Producto ya asociado a este proveedor")
            # Insertar asociación
            idpp = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO producto_proveedor (
                  id_producto_proveedor,
                  codigo_producto,
                  rut_proveedor,
                  precio_compra
                ) VALUES (%s, %s, %s, %s)
            """, (idpp, cod, rut, precio))

    def del_prod(self, rut, cod):
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("RUT inválido")
        if len(cod) != 8:
            raise ValueError("Código de producto inválido")

        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM producto_proveedor
                 WHERE rut_proveedor = %s
                   AND codigo_producto = %s
            """, (rut, cod))
            if cur.rowcount == 0:
                raise ValueError("Asociación no existe")

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
    svc_name = "serv7"
    servicio = ProveedorServiceDB()

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

    # 4) Procesar transacciones
    try:
        while True:
            origen, datos = recv_tx(sock)
            if origen != svc_name:
                continue

            try:
                parts = datos.split("|")
                cmd = parts[0]

                if cmd == "LIST":
                    resp = json.dumps(servicio.listar())

                elif cmd == "ADD":
                    _, rut, nom, mail = parts
                    servicio.agregar(rut, nom, mail)
                    resp = "OK"

                elif cmd == "DEL":
                    _, rut = parts
                    servicio.eliminar(rut)
                    resp = "OK"

                elif cmd == "APROD":
                    _, rut, cod, pr = parts
                    servicio.add_prod(rut, cod, int(pr))
                    resp = "OK"

                elif cmd == "DPROD":
                    _, rut, cod = parts
                    servicio.del_prod(rut, cod)
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
