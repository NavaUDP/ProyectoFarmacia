class ClienteMiembro:

    def __init__(self, rut: str, nombre: str, apellido: str, correo_electronico: str):
        self.rut = rut
        self.nombre = nombre
        self.apellido = apellido
        self.correo_electronico = correo_electronico

        # Puntos comienzan en 0 cuando se agrega un miembro.
        self.puntos_acumulados = 0

    def to_dict(self) -> dict:

        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo_electronico": self.correo_electronico,
            "puntos_acumulados": self.puntos_acumulados
        }

class MiembroService:
    def __init__(self):

        # Clave: rut (8 dígitos). Valor: instancia de ClienteMiembro.
        self._miembros: dict[str, ClienteMiembro] = {}

    def listar_miembros(self) -> list[dict]:
       
        # Retorna una lista de diccionarios con todos los clientes miembros registrados.
        return [m.to_dict() for m in self._miembros.values()]

    def agregar_miembro(self, rut: str, nombre: str, apellido: str, correo_electronico: str) -> None:

        # Agrega un nuevo cliente miembro, validando los campos según el diccionario:
        rut = rut.strip()
        nombre = nombre.strip()
        apellido = apellido.strip()
        correo = correo_electronico.strip()

        # Valida RUT
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("El RUT debe tener exactamente 8 dígitos numéricos (sin dígito verificador).")

        # Valida nombre y apellido
        if len(nombre) == 0 or len(nombre) > 15:
            raise ValueError("El nombre debe tener entre 1 y 15 caracteres.")
        if len(apellido) == 0 or len(apellido) > 15:
            raise ValueError("El apellido debe tener entre 1 y 15 caracteres.")

        # Valida correo electrónico
        if len(correo) == 0 or len(correo) > 20:
            raise ValueError("El correo electrónico debe tener entre 1 y 20 caracteres.")
        if "@" not in correo or "." not in correo:
            raise ValueError("El correo electrónico no tiene un formato válido.")

        # Verifica existencia previa
        if rut in self._miembros:
            raise ValueError(f"Ya existe un cliente miembro con RUT '{rut}'.")

        # Se crea e inserta el nuevo miembro (puntos_acumulados = 0)
        nuevo = ClienteMiembro(
            rut=rut,
            nombre=nombre,
            apellido=apellido,
            correo_electronico=correo
        )
        self._miembros[rut] = nuevo

    def eliminar_miembro(self, rut: str) -> None:
        
        # Elimina al cliente miembro que tenga el RUT indicado.
        rut = rut.strip()
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("El RUT debe tener exactamente 8 dígitos numéricos (sin dígito verificador).")

        if rut not in self._miembros:
            raise ValueError(f"No existe un cliente miembro con RUT '{rut}' para eliminar.")

        del self._miembros[rut]


# Interfaz de línea de comandos (terminal)
def mostrar_menu():
    print("\n=== Servicio de Gestión de Clientes Miembros ===")
    print("1) Listar todos los clientes miembros")
    print("2) Agregar un nuevo cliente miembro")
    print("3) Eliminar un cliente miembro existente")
    print("4) Salir")

def input_miembro() -> tuple[str, str, str, str]:
    
    # Solicita al usuario que ingrese RUT, nombre, apellido y correo, y retorna una tupla: (rut, nombre, apellido, correo_electronico).
    rut = input("Ingrese RUT (8 dígitos, sin dígito verificador): ").strip()
    nombre = input("Ingrese nombre (hasta 15 caracteres): ").strip()
    apellido = input("Ingrese apellido (hasta 15 caracteres): ").strip()
    correo = input("Ingrese correo electrónico (hasta 20 caracteres): ").strip()
    return rut, nombre, apellido, correo

def main():
    servicio = MiembroService()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-4): ").strip()

        if opcion == "1":

            # Listar todos los miembros
            lista = servicio.listar_miembros()
            if not lista:
                print("\nNo hay clientes miembros registrados.")
            else:
                print("\nLista de Clientes Miembros:")
                for idx, m in enumerate(lista, start=1):
                    print(
                        f" {idx}) RUT: {m['rut']}, Nombre: {m['nombre']} {m['apellido']}, "
                        f"Correo: {m['correo_electronico']}, Puntos acumulados: {m['puntos_acumulados']}"
                    )

        elif opcion == "2":

            # Agregar un nuevo miembro
            try:
                rut, nombre, apellido, correo = input_miembro()
                servicio.agregar_miembro(rut, nombre, apellido, correo)
                print("\nCliente miembro agregado exitosamente (puntos iniciales = 0).")
            except ValueError as e:
                print(f"\nError al agregar cliente miembro: {e}")

        elif opcion == "3":

            # Eliminar un miembro existente
            rut = input("Ingrese RUT del cliente miembro a eliminar (8 dígitos): ").strip()
            try:
                servicio.eliminar_miembro(rut)
                print(f"\nCliente miembro con RUT '{rut}' eliminado exitosamente.")
            except ValueError as e:
                print(f"\nError al eliminar cliente miembro: {e}")

        elif opcion == "4":
            print("\nSaliendo del servicio...")
            break

        else:
            print("\nOpción inválida. Por favor, ingrese un número del 1 al 4.")

if __name__ == "__main__":
    main()