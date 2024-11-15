"""
Este módulo implementa una aplicación de banco simple utilizando una
arquitectura limpia.

Clases:
    Cuenta: Entidad que representa una cuenta bancaria.
    CasoDeUsoCuenta: Caso de uso para la gestión de cuentas bancarias.
    RepositorioCuentaSQLite: Adaptador que implementa un repositorio usando
    SQLite.
    AplicacionBanco: Aplicación de GUI para interactuar con el caso de uso de
    cuentas bancarias.

Funciones:
    main: Configuración e inicialización del módulo principal.

Ejemplo de uso:
    Para ejecutar la aplicación, simplemente ejecute este módulo. Se creará
    una cuenta de prueba con ID "12345" y un saldo inicial de 100.0 si no
    existe.
"""
import sqlite3
from tkinter import Tk, Label, Entry, Button, messagebox


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


# Puertos y adaptadores (repositorio SQLite)
class RepositorioCuentaSQLite:
    """Adaptador que implementa un repositorio usando SQLite."""

    def __init__(self, nombre_bd='banco.db'):
        self.conn = sqlite3.connect(nombre_bd)
        self._crear_tabla()

    def _crear_tabla(self):
        """Crea la tabla de cuentas si no existe."""
        with self.conn:
            self.conn.execute(
                ('CREATE TABLE IF NOT EXISTS cuentas '
                 '(id_cuenta TEXT PRIMARY KEY, saldo REAL NOT NULL)')
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
                ('INSERT OR REPLACE INTO cuentas (id_cuenta, saldo) '
                 'VALUES (?, ?)'),
                (cuenta.id_cuenta, cuenta.saldo)
            )


# GUI con Tkinter
class AplicacionBanco:
    """Aplicación de GUI para interactuar con el caso de uso de cuentas
    bancarias."""

    def __init__(self, caso_uso_instancia):
        self.caso_uso = caso_uso_instancia
        self.ventana = Tk()
        self.ventana.title("Banco Simple")

        # Elementos de la interfaz
        Label(self.ventana, text="ID de la cuenta:").grid(row=0, column=0)
        self.entrada_id_cuenta = Entry(self.ventana)
        self.entrada_id_cuenta.grid(row=0, column=1)

        Label(self.ventana, text="Monto:").grid(row=1, column=0)
        self.entrada_monto = Entry(self.ventana)
        self.entrada_monto.grid(row=1, column=1)

        Button(
            self.ventana, text="Depositar", command=self.depositar
        ).grid(row=2, column=0)
        Button(
            self.ventana, text="Retirar", command=self.retirar
        ).grid(row=2, column=1)

    def depositar(self):
        """Lógica de la operación de depósito."""
        try:
            id_cuenta = self.entrada_id_cuenta.get()
            monto = float(self.entrada_monto.get())
            self.caso_uso.depositar(id_cuenta, monto)
            nuevo_saldo = self.caso_uso.repositorio_cuentas.obtener_por_id(
                id_cuenta
            ).saldo
            messagebox.showinfo(
                "Éxito", f"Depósito realizado. Nuevo saldo: {nuevo_saldo}"
            )
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except sqlite3.DatabaseError as e:
            messagebox.showerror("Error", str(e))

    def retirar(self):
        """Lógica de la operación de retiro."""
        try:
            id_cuenta = self.entrada_id_cuenta.get()
            monto = float(self.entrada_monto.get())
            self.caso_uso.retirar(id_cuenta, monto)
            nuevo_saldo = self.caso_uso.repositorio_cuentas.obtener_por_id(
                id_cuenta
            ).saldo
            messagebox.showinfo(
                "Éxito", f"Retiro realizado. Nuevo saldo: {nuevo_saldo}"
            )
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except sqlite3.DatabaseError as e:
            messagebox.showerror("Error", str(e))
            messagebox.showerror("Error", str(e))

    def ejecutar(self):
        """Inicia la aplicación de la GUI."""
        self.ventana.mainloop()


# Configuración e inicialización del módulo principal
if __name__ == "__main__":
    repositorio = RepositorioCuentaSQLite()
    caso_uso = CasoDeUsoCuenta(repositorio)

    # Agregar una cuenta de prueba si no existe
    try:
        repositorio.obtener_por_id("12345")
    except ValueError:
        repositorio.guardar(Cuenta("12345", 100.0))

    app = AplicacionBanco(caso_uso)
    app.ejecutar()
