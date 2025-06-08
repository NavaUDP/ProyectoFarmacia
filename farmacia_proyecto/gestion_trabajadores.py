import string
import random

class Trabajador:
    def __init__(self, rut: str, nombre: str, apellido: str, correo_electronico: str,
                 nombre_cuenta: str, contrasena: str, rol: int):
        self.rut = rut
        self.nombre = nombre
        self.apellido = apellido
        self.nombre_cuenta = nombre_cuenta
        self.contrasena = contrasena
        self.correo_electronico = correo_electronico
        self.rol = rol

    def to_dict(self) -> dict:

        # Entrega un diccionario con los datos del trabajador.
        return {
            "rut": self.rut,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_cuenta": self.nombre_cuenta,
            "contrasena": self.contrasena,
            "correo_electronico": self.correo_electronico,
            "rol": self.rol
        }

class TrabajadorService:

    def __init__(self):

        # Clave: RUT (string de 8 caracteres); Valor: instancia de Trabajador
        self._trabajadores: dict[str, Trabajador] = {}

    @staticmethod
    def _generar_contrasena_aleatoria(length: int = 8) -> str:

        # Se crea una contraseña aleatoria de longitud 'length' usando letras (mayúsculas/minúsculas) y dígitos.
        caracteres = string.ascii_letters + string.digits
        return "".join(random.choice(caracteres) for _ in range(length))

    def listar_trabajadores(self) -> list[dict]:
        
        # Retorna una lista de diccionarios, cada uno con los datos de un trabajador.
        return [t.to_dict() for t in self._trabajadores.values()]

    def agregar_trabajador(self, rut: str, nombre: str, apellido: str, correo_electronico: str) -> dict:

        rut = rut.strip()
        nombre = nombre.strip()
        apellido = apellido.strip()
        correo = correo_electronico.strip()

        # 1) Validación del RUT
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("El RUT debe tener exactamente 8 dígitos (sin dígito verificador).")

        # 2) Validación de longitud del nombre y apellido
        if len(nombre) == 0 or len(nombre) > 15:
            raise ValueError("El nombre debe tener entre 1 y 15 caracteres.")
        if len(apellido) == 0 or len(apellido) > 15:
            raise ValueError("El apellido debe tener entre 1 y 15 caracteres.")

        # 3) Se valida correo electrónico (longitud y formato)
        if len(correo) == 0 or len(correo) > 20:
            raise ValueError("El correo electrónico debe tener entre 1 y 20 caracteres.")
        if "@" not in correo or "." not in correo:
            raise ValueError("El correo electrónico no tiene un formato válido.")

        # 4) Verificar existencia previa
        if rut in self._trabajadores:
            raise ValueError(f"Ya existe un trabajador con RUT '{rut}'.")

        # 5) Se crean campos automáticos para nombre de la cuenta y su contraseña asociada
        nombre_cuenta = rut[:7]  # hasta 7 caracteres
        contrasena = self._generar_contrasena_aleatoria(8)
        rol = 0  # Rol de Operativo establecido por defecto

        # 6) Creación de la instancia de Trabajador y se agrega al diccionario
        nuevo = Trabajador(
            rut=rut,
            nombre=nombre,
            apellido=apellido,
            correo_electronico=correo,
            nombre_cuenta=nombre_cuenta,
            contrasena=contrasena,
            rol=rol
        )
        self._trabajadores[rut] = nuevo

        return {
            "nombre_cuenta": nombre_cuenta,
            "contrasena": contrasena
        }

    def eliminar_trabajador(self, rut: str) -> None:
        rut = rut.strip()
        if len(rut) != 8 or not rut.isdigit():
            raise ValueError("El RUT debe tener exactamente 8 dígitos (sin dígito verificador).")

        if rut not in self._trabajadores:
            raise ValueError(f"No existe un trabajador con RUT '{rut}' para eliminar.")

        del self._trabajadores[rut]

# Interfaz de línea de comandos (terminal)
def mostrar_menu():
    print("\n=== Servicio de Gestión de Trabajadores ===")
    print("1) Listar todos los trabajadores")
    print("2) Agregar un nuevo trabajador")
    print("3) Eliminar un trabajador existente")
    print("4) Salir")


def input_trabajador() -> tuple[str, str, str, str]:

    # Solicita al usuario que ingrese RUT, nombre, apellido y correo y retorna una tupla (rut, nombre, apellido, correo_electronico).
    rut = input("Ingrese RUT (8 dígitos, sin dígito verificador): ").strip()
    nombre = input("Ingrese nombre (hasta 15 caracteres): ").strip()
    apellido = input("Ingrese apellido (hasta 15 caracteres): ").strip()
    correo = input("Ingrese correo electrónico (hasta 20 caracteres): ").strip()
    return rut, nombre, apellido, correo


def main():
    servicio = TrabajadorService()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-4): ").strip()

        if opcion == "1":

            # Se listan los trabajadores
            lista = servicio.listar_trabajadores()
            if not lista:
                print("\nNo existen trabajadores registrados.")
            else:
                print("\nLista de trabajadores:")
                for idx, t in enumerate(lista, start=1):
                    print(f" {idx}) RUT: {t['rut']}, Nombre y apellido: {t['nombre']} {t['apellido']}, "
                          f"Cuenta: {t['nombre_cuenta']}, Correo: {t['correo_electronico']}, Rol: {t['rol']}")

        elif opcion == "2":

            # Se agrega un trabajador
            try:
                rut, nombre, apellido, correo = input_trabajador()
                datos_generados = servicio.agregar_trabajador(rut, nombre, apellido, correo)
                print("\nTrabajador agregado exitosamente.")
                print(f"  Nombre de cuenta: {datos_generados['nombre_cuenta']}")
                print(f"  Contraseña: {datos_generados['contrasena']}")
            except ValueError as e:
                print(f"\nError al agregar trabajador: {e}")

        elif opcion == "3":

            # Se elimina un trabajador
            rut = input("Ingrese RUT del trabajador a eliminar (8 dígitos, sin dígito verificador): ").strip()
            try:
                servicio.eliminar_trabajador(rut)
                print(f"\nTrabajador con RUT '{rut}' eliminado exitosamente.")
            except ValueError as e:
                print(f"\nError al eliminar trabajador: {e}")

        elif opcion == "4":

            # Salir del servicio
            print("\nSaliendo del servicio...")
            break

        else:
            print("\nOpción inválida. Por favor, ingrese un número del 1 al 4.")

if __name__ == "__main__":
    main()
