# Modelo para gestión de atletas
import mysql.connector
from mysql.connector import Error
from .database import Database

class AtletaModel:
    def __init__(self):
        self.db = Database()
    # Aquí van los métodos para atletas
    def insert_atleta(self, id_usuario, cedula, peso, fecha_nacimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("INSERT INTO `atletas`(`id_usuario`, `cedula`, `peso`, `fecha_nacimiento`, `id_plan`, `id_coach`, `meta_largo_plazo`, `valoracion_especiales`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id_usuario, cedula, peso, fecha_nacimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al ingresar datos {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()
    
    def read_atletas(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `atletas` WHERE 1")
            result = cursor.fetchall()
            return result
        
        except mysql.connector.Error as error:
            print(f"Error al consultar datos {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def update_atleta(self, id_atleta, id_usuario, cedula, peso, fecha_nacimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("UPDATE `atletas` SET `id_usuario`=%s,`cedula`=%s,`peso`=%s,`fecha_nacimiento`=%s,`id_plan`=%s,`id_coach`=%s,`meta_largo_plazo`=%s,`valoracion_especiales`=%s WHERE `id_atleta`=%s", (id_usuario, cedula, peso, fecha_nacimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales, id_atleta))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al actualizar datos {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def delete_atleta(self, id_atleta):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM `atletas` WHERE `id_atleta`=%s", (id_atleta,))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al eliminar datos {error}")
            return False
            
        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()
    
