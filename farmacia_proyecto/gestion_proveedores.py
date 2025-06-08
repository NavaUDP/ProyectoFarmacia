class Proveedor:
    def __init__(self, rut: str, nombre: str, correo_electronico: str):
        self.rut = rut
        self.nombre = nombre
        self.correo_electronico = correo_electronico
        # Internamente, guardamos los productos que comercializa este proveedor
        self._productos: dict[str, int] = {}

    def to_dict(self) -> dict:

        lista_productos = [
            {"codigo_producto": codigo, "precio_compra": precio}
            for codigo, precio in self._productos.items()
        ]
        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "correo_electronico": self.correo_electronico,
            "productos": lista_productos
        }

class ProveedorService:
    
    def __init__(self):
        self._proveedores: dict[str, Proveedor] = {}

    def listar_proveedores(self) -> list[dict]:
    
        # Retorna una lista de diccionarios con todos los proveedores y los productos que cada uno comercializa.
        return [prov.to_dict() for prov in self._proveedores.values()]

    def agregar_proveedor(self, rut: str, nombre: str, correo_electronico: str) -> None:
        
        # Agrega un nuevo proveedor, validando campos. 
        rut = rut.strip()
        nombre = nombre.strip()
        correo = correo_electronico.strip()

        # 1) Validación de RUT
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("El RUT debe tener exactamente 8 dígitos (sin dígito verificador).")

        # 2) Validación de longitud de nombre
        if len(nombre) == 0 or len(nombre) > 15:
            raise ValueError("El nombre del proveedor debe tener entre 1 y 15 caracteres.")

        # 3) Validación del correo electrónico (longitud y formato)
        if len(correo) == 0 or len(correo) > 20:
            raise ValueError("El correo electrónico debe tener entre 1 y 20 caracteres.")
        if "@" not in correo or "." not in correo:
            raise ValueError("El correo electrónico no tiene un formato válido.")

        # 4) Se verifica que no exista ya ese RUT
        if rut in self._proveedores:
            raise ValueError(f"Ya existe un proveedor con RUT '{rut}'.")

        # 5) Se crea y almacena el nuevo proveedor
        nuevo = Proveedor(rut=rut, nombre=nombre, correo_electronico=correo)
        self._proveedores[rut] = nuevo

    def eliminar_proveedor(self, rut: str) -> None:
        
        # Elimina al proveedor con el RUT indicado.
        rut = rut.strip()
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("El RUT debe tener exactamente 8 dígitos (sin dígito verificador).")

        if rut not in self._proveedores:
            raise ValueError(f"No existe un proveedor con RUT '{rut}' para eliminar.")

        del self._proveedores[rut]

    def agregar_producto_a_proveedor(self, rut: str, codigo_producto: str, precio: int) -> None:

        # Asocia un producto (código de 8 caracteres) con un precio al proveedor indicado por RUT.
        rut = rut.strip()
        codigo = codigo_producto.strip()

        # 1) Valida el RUT
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("El RUT debe tener exactamente 8 dígitos (sin dígito verificador).")

        # 2) Verifica que el proveedor existe
        if rut not in self._proveedores:
            raise ValueError(f"No existe un proveedor con RUT '{rut}'.")

        # 3) Valida el código de producto
        if len(codigo) != 8:
            raise ValueError("El código de producto debe tener exactamente 8 caracteres.")

        # 4) Valida el precio
        if not isinstance(precio, int) or precio <= 0:
            raise ValueError("El precio debe ser un número entero positivo.")

        proveedor = self._proveedores[rut]
        if codigo in proveedor._productos:
            raise ValueError(f"El proveedor '{rut}' ya tiene asociado el producto '{codigo}'.")

        # 5) Se asocia el producto al proveedor
        proveedor._productos[codigo] = precio

    def eliminar_producto_de_proveedor(self, rut: str, codigo_producto: str) -> None:
    
        # Elimina la asociación de un producto de un proveedor.
        rut = rut.strip()
        codigo = codigo_producto.strip()

        # 1) Valida RUT
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("El RUT debe tener exactamente 8 dígitos (sin dígito verificador).")

        # 2) Verifica que el proveedor existe
        if rut not in self._proveedores:
            raise ValueError(f"No existe un proveedor con RUT '{rut}'.")

        proveedor = self._proveedores[rut]

        # 3) Verifica que el producto está asociado
        if codigo not in proveedor._productos:
            raise ValueError(f"El proveedor '{rut}' no tiene asociado el producto '{codigo}' para eliminar.")

        # 4) Elimina la asociación
        del proveedor._productos[codigo]

# Interfaz de línea de comandos (terminal)
def mostrar_menu():
    print("\n=== Servicio de Gestión de Proveedores ===")
    print("1) Listar todos los proveedores")
    print("2) Agregar un nuevo proveedor")
    print("3) Eliminar un proveedor existente")
    print("4) Agregar producto a un proveedor")
    print("5) Eliminar producto de un proveedor")
    print("6) Salir")


def input_proveedor() -> tuple[str, str, str]:

    # Solicita al usuario que ingrese RUT, nombre y correo, y retorna una tupla (rut, nombre, correo_electronico).
    rut = input("Ingrese RUT proveedor (8 dígitos, sin dígito verificador): ").strip()
    nombre = input("Ingrese nombre del proveedor (hasta 15 caracteres): ").strip()
    correo = input("Ingrese correo electrónico (hasta 20 caracteres): ").strip()
    return rut, nombre, correo

def input_producto_proveedor() -> tuple[str, str, int]:

    # Solicita al usuario RUT proveedor, código de producto y precio, y retorna una tupla (rut, codigo_producto, precio).
    rut = input("Ingrese RUT proveedor (8 dígitos, sin dígito verificador): ").strip()
    codigo = input("Ingrese código de producto (8 caracteres): ").strip()
    precio_str = input("Ingrese precio de compra (entero positivo): ").strip()
    try:
        precio = int(precio_str)
    except ValueError:
        precio = -1
    return rut, codigo, precio

def main():
    servicio = ProveedorService()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-6): ").strip()

        if opcion == "1":

            # Se listan los proveedores junto con sus productos
            lista = servicio.listar_proveedores()
            if not lista:
                print("\nNo hay proveedores registrados.")
            else:
                print("\nLista de Proveedores:")
                for idx, p in enumerate(lista, start=1):
                    print(f" {idx}) RUT: {p['rut']}, Nombre: {p['nombre']}, Correo: {p['correo_electronico']}")
                    if not p["productos"]:
                        print("     → No tiene productos asociados.")
                    else:
                        print("     → Productos comercializados:")
                        for prod in p["productos"]:
                            print(f"        • Código: {prod['codigo_producto']}, Precio compra: {prod['precio_compra']}")

        elif opcion == "2":

            # Agregar proveedor
            try:
                rut, nombre, correo = input_proveedor()
                servicio.agregar_proveedor(rut, nombre, correo)
                print("\nProveedor agregado exitosamente.")
            except ValueError as e:
                print(f"\nError al agregar proveedor: {e}")

        elif opcion == "3":

            # Eliminar proveedor
            rut = input("Ingrese RUT del proveedor a eliminar (8 dígitos): ").strip()
            try:
                servicio.eliminar_proveedor(rut)
                print(f"\nProveedor con RUT '{rut}' eliminado exitosamente.")
            except ValueError as e:
                print(f"\nError al eliminar proveedor: {e}")

        elif opcion == "4":

            # Agregar producto a proveedor
            try:
                rut, codigo, precio = input_producto_proveedor()
                servicio.agregar_producto_a_proveedor(rut, codigo, precio)
                print(f"\nProducto '{codigo}' agregado al proveedor '{rut}' con precio {precio}.")
            except ValueError as e:
                print(f"\nError al asociar producto al proveedor: {e}")

        elif opcion == "5":

            # Eliminar producto de proveedor
            rut = input("Ingrese RUT proveedor (8 dígitos): ").strip()
            codigo = input("Ingrese código de producto a eliminar (8 caracteres): ").strip()
            try:
                servicio.eliminar_producto_de_proveedor(rut, codigo)
                print(f"\nProducto '{codigo}' eliminado del proveedor '{rut}'.")
            except ValueError as e:
                print(f"\nError al eliminar producto del proveedor: {e}")

        elif opcion == "6":

            # Salir del servicio
            print("\nSaliendo del servicio...")
            break

        else:
            print("\nOpción inválida. Por favor, ingrese un número del 1 al 6.")

if __name__ == "__main__":
    main()