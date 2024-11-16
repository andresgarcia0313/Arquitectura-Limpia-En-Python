import sqlite3

# Dominio (Entidades y puertos)
class Cuenta:
    """Entidad que representa una cuenta bancaria."""

    def __init__(self, id_cuenta: str, saldo: float = 0.0):
        self.id_cuenta = id_cuenta
        self.saldo = saldo

    def depositar(self, monto: float):
        """Método para depositar dinero en la cuenta."""
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        self.saldo += monto

    def retirar(self, monto: float):
        """Método para retirar dinero de la cuenta."""
        if monto > self.saldo:
            raise ValueError("Fondos insuficientes")
        self.saldo -= monto


# Caso de uso
class CasoDeUsoCuenta:
    """Caso de uso para la gestión de cuentas bancarias."""

    def __init__(self, repositorio_cuentas):
        self.repositorio_cuentas = repositorio_cuentas

    def depositar(self, id_cuenta: str, monto: float):
        """Realiza el depósito en la cuenta especificada."""
        cuenta = self.repositorio_cuentas.obtener_por_id(id_cuenta)
        cuenta.depositar(monto)
        self.repositorio_cuentas.guardar(cuenta)

    def retirar(self, id_cuenta: str, monto: float):
        """Realiza el retiro en la cuenta especificada."""
        cuenta = self.repositorio_cuentas.obtener_por_id(id_cuenta)
        cuenta.retirar(monto)
        self.repositorio_cuentas.guardar(cuenta)


# Adaptador (repositorio SQLite)
class RepositorioCuentaSQLite:
    """Adaptador que implementa un repositorio usando SQLite."""

    def __init__(self, nombre_bd='banco.db'):
        self.conn = sqlite3.connect(nombre_bd)
        self._crear_tabla()

    def _crear_tabla(self):
        """Crea la tabla de cuentas si no existe."""
        with self.conn:
            self.conn.execute(
                'CREATE TABLE IF NOT EXISTS cuentas (id_cuenta TEXT PRIMARY KEY, saldo REAL NOT NULL)'
            )

    def obtener_por_id(self, id_cuenta: str) -> Cuenta:
        """Obtiene una cuenta por su ID desde la base de datos."""
        cursor = self.conn.execute(
            'SELECT * FROM cuentas WHERE id_cuenta = ?', (id_cuenta,)
        )
        fila = cursor.fetchone()
        if fila is None:
            raise ValueError("Cuenta no encontrada")
        return Cuenta(id_cuenta=fila[0], saldo=fila[1])

    def guardar(self, cuenta: Cuenta):
        """Guarda o actualiza la cuenta en la base de datos."""
        with self.conn:
            self.conn.execute(
                'INSERT OR REPLACE INTO cuentas (id_cuenta, saldo) VALUES (?, ?)',
                (cuenta.id_cuenta, cuenta.saldo)
            )


def main():
    repositorio = RepositorioCuentaSQLite()
    caso_uso = CasoDeUsoCuenta(repositorio)

    # Agregar una cuenta de prueba si no existe
    try:
        repositorio.obtener_por_id("12345")
    except ValueError:
        repositorio.guardar(Cuenta("12345", 100.0))

    while True:
        print("\nBienvenido al Banco CLI")
        print("1. Depositar")
        print("2. Retirar")
        print("3. Consultar saldo")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            id_cuenta = input("Ingrese el ID de la cuenta: ")
            monto = float(input("Ingrese el monto a depositar: "))
            try:
                caso_uso.depositar(id_cuenta, monto)
                nuevo_saldo = repositorio.obtener_por_id(id_cuenta).saldo
                print(f"Depósito exitoso. Nuevo saldo: {nuevo_saldo}")
            except ValueError as e:
                print(f"Error: {e}")

        elif opcion == "2":
            id_cuenta = input("Ingrese el ID de la cuenta: ")
            monto = float(input("Ingrese el monto a retirar: "))
            try:
                caso_uso.retirar(id_cuenta, monto)
                nuevo_saldo = repositorio.obtener_por_id(id_cuenta).saldo
                print(f"Retiro exitoso. Nuevo saldo: {nuevo_saldo}")
            except ValueError as e:
                print(f"Error: {e}")

        elif opcion == "3":
            id_cuenta = input("Ingrese el ID de la cuenta: ")
            try:
                cuenta = repositorio.obtener_por_id(id_cuenta)
                print(f"Saldo actual: {cuenta.saldo}")
            except ValueError as e:
                print(f"Error: {e}")

        elif opcion == "4":
            print("Gracias por usar el Banco CLI. ¡Adiós!")
            break

        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()
