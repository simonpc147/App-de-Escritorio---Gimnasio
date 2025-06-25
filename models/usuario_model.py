# Modelo para gestión de usuarios
import mysql.connector
from mysql.connector import Error
from .database import Database


class UsuarioModel:
    def __init__(self):
        self.db = Database()
    
    # Aquí van los métodos para usuarios
    
    def insert_usuario(self, nombre, apellido, edad, direccion, telefono, email, contraseña, rol, creado_por, estado_activo=True):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                INSERT INTO `usuarios` 
                (`nombre`, `apellido`, `edad`, `direccion`, `telefono`, `email`, `contraseña`, `rol`, `creado_por`, `estado_activo`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre, apellido, edad, direccion, telefono, email, contraseña, rol, creado_por, estado_activo))
            self.db.connection.commit()
            print(cursor.rowcount)
            return cursor.lastrowid  # Retorna el ID del usuario insertado

        except mysql.connector.Error as error:
            print(f"Error al insertar usuario: {error}")
            return None

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def read_usuarios(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `usuarios`")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error al leer usuarios: {error}")
            return []

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def update_usuario(self, id, nombre, apellido, edad, direccion, telefono, email, contraseña, rol, estado_activo):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("""
                UPDATE `usuarios` SET 
                    `nombre`=%s, `apellido`=%s, `edad`=%s, `direccion`=%s, `telefono`=%s, 
                    `email`=%s, `contraseña`=%s, `rol`=%s, `estado_activo`=%s 
                WHERE `id`=%s
            """, (nombre, apellido, edad, direccion, telefono, email, contraseña, rol, estado_activo, id))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al actualizar usuario: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()

    def delete_usuario(self, id):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM `usuarios` WHERE `id`=%s", (id,))
            self.db.connection.commit()
            print(cursor.rowcount)
            return True

        except mysql.connector.Error as error:
            print(f"Error al eliminar usuario: {error}")
            return False

        finally:
            if cursor:
                cursor.close()
            self.db.disconnect()