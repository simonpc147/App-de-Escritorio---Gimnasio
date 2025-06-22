# Modelo para gestión de egresos
import mysql.connector
from mysql.connector import Error
from .database import Database

class EgresoModel:
    def __init__(self):
        self.db = Database()
    
    # Aquí van los métodos para egresos
    def insert_egreso(self, monto, tipo_egreso, descripcion, beneficiario, metodo_pago, fecha_egreso, registrado_por, comprobante):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `egresos`
                (`monto`, `tipo_egreso`, `descripcion`, `beneficiario`, `metodo_pago`, `fecha_egreso`, `registrado_por`, `comprobante`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (monto, tipo_egreso, descripcion, beneficiario, metodo_pago, fecha_egreso, registrado_por, comprobante))
            self.db.connection.commit()
            print(cursor.rowcount)
            return cursor.lastrowid  # útil para seguimiento/logs

        except mysql.connector.Error as error:
            print(f"Error al insertar egreso: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def read_egresos(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `egresos`")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al leer egresos: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def update_egreso(self, id_egreso, monto, tipo_egreso, descripcion, beneficiario, metodo_pago, fecha_egreso, registrado_por, comprobante):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE `egresos` SET 
                    `monto`=%s, `tipo_egreso`=%s, `descripcion`=%s, `beneficiario`=%s, 
                    `metodo_pago`=%s, `fecha_egreso`=%s, `registrado_por`=%s, `comprobante`=%s 
                WHERE `id_egreso`=%s
            """, (monto, tipo_egreso, descripcion, beneficiario, metodo_pago, fecha_egreso, registrado_por, comprobante, id_egreso))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al actualizar egreso: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def delete_egreso(self, id_egreso):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM `egresos` WHERE `id_egreso`=%s", (id_egreso,))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al eliminar egreso: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()