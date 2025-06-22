# Modelo para gestión de coaches
import mysql.connector
from mysql.connector import Error
from .database import Database

class CoachModel:
    def __init__(self):
        self.db = Database()

    def insert_coach(self, id_usuario, especialidades, horario_disponible, fecha_contratacion, salario):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `coaches`
                (`id_usuario`, `especialidades`, `horario_disponible`, `fecha_contratacion`, `salario`)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_usuario, especialidades, horario_disponible, fecha_contratacion, salario))
            self.db.connection.commit()
            print(cursor.rowcount)
            return cursor.lastrowid  # Opcional: retornar ID del coach

        except mysql.connector.Error as error:
            print(f"Error al insertar coach: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def read_coaches(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `coaches`")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al leer coaches: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def update_coach(self, id_coach, id_usuario, especialidades, horario_disponible, fecha_contratacion, salario):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE `coaches` SET 
                    `id_usuario`=%s, 
                    `especialidades`=%s, 
                    `horario_disponible`=%s, 
                    `fecha_contratacion`=%s, 
                    `salario`=%s 
                WHERE `id_coach`=%s
            """, (id_usuario, especialidades, horario_disponible, fecha_contratacion, salario, id_coach))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al actualizar coach: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def delete_coach(self, id_coach):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM `coaches` WHERE `id_coach`=%s", (id_coach,))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al eliminar coach: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()
