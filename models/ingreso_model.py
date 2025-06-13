# Modelo para gestión de ingresos
import mysql.connector
from mysql.connector import Error
from .database import Database

class IngresoModel:
    def __init__(self):
        self.db = Database()

    def insert_ingreso(self, id_atleta, id_plan, monto, tipo_pago, metodo_pago, descripcion, fecha_pago, fecha_vencimiento_anterior, fecha_vencimiento_nueva, procesado_por):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `ingresos`
                (`id_atleta`, `id_plan`, `monto`, `tipo_pago`, `metodo_pago`, `descripcion`, `fecha_pago`, `fecha_vencimiento_anterior`, `fecha_vencimiento_nueva`, `procesado_por`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_atleta, id_plan, monto, tipo_pago, metodo_pago, descripcion, fecha_pago, fecha_vencimiento_anterior, fecha_vencimiento_nueva, procesado_por))
            self.db.connection.commit()
            print(cursor.rowcount)
            return cursor.lastrowid  # Útil para seguimiento

        except mysql.connector.Error as error:
            print(f"Error al insertar ingreso: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def read_ingresos(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `ingresos`")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al leer ingresos: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def update_ingreso(self, id_pago, id_atleta, id_plan, monto, tipo_pago, metodo_pago, descripcion, fecha_pago, fecha_vencimiento_anterior, fecha_vencimiento_nueva, procesado_por):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE `ingresos` SET 
                    `id_atleta`=%s, `id_plan`=%s, `monto`=%s, `tipo_pago`=%s, `metodo_pago`=%s,
                    `descripcion`=%s, `fecha_pago`=%s, `fecha_vencimiento_anterior`=%s, 
                    `fecha_vencimiento_nueva`=%s, `procesado_por`=%s
                WHERE `id_pago`=%s
            """, (id_atleta, id_plan, monto, tipo_pago, metodo_pago, descripcion, fecha_pago, fecha_vencimiento_anterior, fecha_vencimiento_nueva, procesado_por, id_pago))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al actualizar ingreso: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def delete_ingreso(self, id_pago):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM `ingresos` WHERE `id_pago`=%s", (id_pago,))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al eliminar ingreso: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()