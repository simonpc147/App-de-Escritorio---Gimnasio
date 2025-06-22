# Modelo para gestión de planes
import mysql.connector
from mysql.connector import Error
from .database import Database

class PlanModel:
    def __init__(self):
        self.db = Database()

    def insert_plan(self, nombre_plan, descripcion, precio, duracion_dias, estado_activo):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `planes`
                (`nombre_plan`, `descripcion`, `precio`, `duracion_dias`, `estado_activo`)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre_plan, descripcion, precio, duracion_dias, estado_activo))
            self.db.connection.commit()
            print(cursor.rowcount)
            return cursor.lastrowid  # Retorna el ID del nuevo plan

        except mysql.connector.Error as error:
            print(f"Error al insertar plan: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def read_planes(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `planes`")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al leer planes: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def update_plan(self, id_plan, nombre_plan, descripcion, precio, duracion_dias, estado_activo):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE `planes` SET 
                    `nombre_plan`=%s, `descripcion`=%s, `precio`=%s, 
                    `duracion_dias`=%s, `estado_activo`=%s 
                WHERE `id_plan`=%s
            """, (nombre_plan, descripcion, precio, duracion_dias, estado_activo, id_plan))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al actualizar plan: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def delete_plan(self, id_plan):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM `planes` WHERE `id_plan`=%s", (id_plan,))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al eliminar plan: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()
