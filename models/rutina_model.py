import mysql.connector
from mysql.connector import Error
from .database import Database

class RutinaModel:
    def __init__(self):
        self.db = Database()
    
    def insert_rutina(self, nombre_rutina, nivel, descripcion, creado_por):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `rutinas` 
                (`nombre_rutina`, `nivel`, `descripcion`, `creado_por`) 
                VALUES (%s, %s, %s, %s)
            """, (nombre_rutina, nivel, descripcion, creado_por))
            self.db.connection.commit()
            return cursor.lastrowid

        except mysql.connector.Error as error:
            print(f"Error al insertar rutina: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def read_rutinas(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `rutinas`")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al leer rutinas: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def insert_ejercicio(self, nombre_ejercicio, tipo_ejercicio, descripcion, instrucciones):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `ejercicios` 
                (`nombre_ejercicio`, `tipo_ejercicio`, `descripcion`, `instrucciones`) 
                VALUES (%s, %s, %s, %s)
            """, (nombre_ejercicio, tipo_ejercicio, descripcion, instrucciones))
            self.db.connection.commit()
            return cursor.lastrowid

        except mysql.connector.Error as error:
            print(f"Error al insertar ejercicio: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def read_ejercicios(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `ejercicios`")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al leer ejercicios: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def asignar_ejercicio_rutina(self, id_rutina, id_ejercicio, nivel, series, rondas, orden_ejercicio):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `rutina_ejercicios` 
                (`id_rutina`, `id_ejercicio`, `nivel`, `series`, `rondas`, `orden_ejercicio`) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_rutina, id_ejercicio, nivel, series, rondas, orden_ejercicio))
            self.db.connection.commit()
            return cursor.lastrowid

        except mysql.connector.Error as error:
            print(f"Error al asignar ejercicio: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def get_rutina_completa(self, id_rutina):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT r.nombre_rutina, e.nombre_ejercicio, re.nivel, re.series, re.rondas, re.orden_ejercicio
                FROM rutinas r
                JOIN rutina_ejercicios re ON r.id_rutina = re.id_rutina
                JOIN ejercicios e ON re.id_ejercicio = e.id_ejercicio
                WHERE r.id_rutina = %s
                ORDER BY re.orden_ejercicio
            """, (id_rutina,))
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al obtener rutina completa: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def contar_ejercicios_rutina(self, id_rutina):
        """Cuenta cuántos ejercicios tiene una rutina"""
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM rutina_ejercicios WHERE id_rutina = %s", (id_rutina,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0

        except mysql.connector.Error as error:
            print(f"Error al contar ejercicios: {error}")
            return 0

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def update_rutina(self, id_rutina, nombre_rutina, nivel, descripcion):
        """NECESARIO para editar rutinas"""
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE `rutinas` SET 
                `nombre_rutina`=%s, `nivel`=%s, `descripcion`=%s 
                WHERE `id_rutina`=%s
            """, (nombre_rutina, nivel, descripcion, id_rutina))
            self.db.connection.commit()
            return cursor.rowcount > 0

        except mysql.connector.Error as error:
            print(f"Error al actualizar rutina: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def delete_rutina(self, id_rutina):
        """NECESARIO para eliminar rutinas"""
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            
            # Primero eliminar ejercicios asociados
            cursor.execute("DELETE FROM `rutina_ejercicios` WHERE `id_rutina`=%s", (id_rutina,))
            
            # Luego eliminar la rutina
            cursor.execute("DELETE FROM `rutinas` WHERE `id_rutina`=%s", (id_rutina,))
            
            self.db.connection.commit()
            return cursor.rowcount > 0

        except mysql.connector.Error as error:
            print(f"Error al eliminar rutina: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def eliminar_ejercicio_de_rutina(self, id_rutina, id_ejercicio):
        """NECESARIO para quitar ejercicios de rutinas"""
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                DELETE FROM `rutina_ejercicios` 
                WHERE `id_rutina`=%s AND `id_ejercicio`=%s
            """, (id_rutina, id_ejercicio))
            self.db.connection.commit()
            return cursor.rowcount > 0

        except mysql.connector.Error as error:
            print(f"Error al eliminar ejercicio de rutina: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()