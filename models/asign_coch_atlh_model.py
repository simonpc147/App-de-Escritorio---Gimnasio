# Modelo para gestión de asignaciones coach-atleta
import mysql.connector
from mysql.connector import Error
from .database import Database

class AsignacionModel:
    def __init__(self):
        self.db = Database()

    def insert_asignacion(self, id_coach, id_atleta, fecha_asignacion, fecha_fin, estado_activo, notas):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `asignaciones_coach_atleta`
                (`id_coach`, `id_atleta`, `fecha_asignacion`, `fecha_fin`, `estado_activo`, `notas`)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_coach, id_atleta, fecha_asignacion, fecha_fin, estado_activo, notas))
            self.db.connection.commit()
            print(cursor.rowcount)
            return cursor.lastrowid

        except mysql.connector.Error as error:
            print(f"Error al insertar asignación: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def read_asignaciones(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `asignaciones_coach_atleta`")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al leer asignaciones: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def update_asignacion(self, id_asignacion, id_coach, id_atleta, fecha_asignacion, fecha_fin, estado_activo, notas):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE `asignaciones_coach_atleta` SET 
                    `id_coach`=%s, `id_atleta`=%s, `fecha_asignacion`=%s,
                    `fecha_fin`=%s, `estado_activo`=%s, `notas`=%s
                WHERE `id_asignacion`=%s
            """, (id_coach, id_atleta, fecha_asignacion, fecha_fin, estado_activo, notas, id_asignacion))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al actualizar asignación: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def delete_asignacion(self, id_asignacion):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM `asignaciones_coach_atleta` WHERE `id_asignacion`=%s", (id_asignacion,))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al eliminar asignación: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()
