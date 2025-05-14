# app/models/modelo.py

import mysql.connector
from mysql.connector import Error
import os 
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Modelo():
    def conectar(self):
        """Establece conexión con la base de datos MySQL usando credenciales del archivo .env"""
        try:
            # Obtener credenciales desde variables de entorno
            host = os.getenv("DB_HOST")
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            database = os.getenv("DB_NAME")
            port = int(os.getenv("DB_PORT", "3306"))
            
            conexion = mysql.connector.connect(
                host=host,
                user=user,
                passwd=password,
                db=database,
                port=port
            )
            return conexion
        except Error as e:
            print(f"Error de conexión: {e}")
            return None

    def ejecutar_consulta(self, sql, params=None, fetchone=False):
        """Método genérico para ejecutar consultas"""
        con = None
        try:
            con = self.conectar()
            if con is None:
                return "Error de conexión a la base de datos"
                
            cursor = con.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
                
            if sql.upper().startswith("SELECT"):
                if fetchone:
                    info = cursor.fetchone()
                else:
                    info = cursor.fetchall()
                con.close()
                return info
            else:
                result = cursor.rowcount  # Número de filas afectadas
                con.commit()
                con.close()
                return result
        except Error as e:
            print(f"Error en la consulta: {e}")
            if con and con.is_connected():
                con.close()
            return f"Error: {e}"

    # MÉTODOS PARA CLIENTES
    def SelectAll_cliente(self):
        """Obtiene todos los clientes"""
        sql = "SELECT * FROM cliente"
        return self.ejecutar_consulta(sql)

    def Insert_cliente(self, id_cliente, nom_cliente, ciu_cliente):
        """Inserta un nuevo cliente usando parámetros seguros"""
        sql = "INSERT INTO cliente VALUES (%s, %s, %s)"
        params = (id_cliente, nom_cliente, ciu_cliente)
        return self.ejecutar_consulta(sql, params)

    def Select_cliente(self, id_cliente):
        """Obtiene un cliente por su ID usando parámetros seguros"""
        sql = "SELECT * FROM cliente WHERE id_cliente = %s"
        params = (id_cliente,)
        return self.ejecutar_consulta(sql, params, fetchone=True)

    # MÉTODOS PARA ARTÍCULOS
    def SelectAll_articulo(self):
        """Obtiene todos los artículos"""
        sql = "SELECT * FROM articulo"
        return self.ejecutar_consulta(sql)

    def Insert_articulo(self, id_art, nom_art, pre_art):
        """Inserta un nuevo artículo usando parámetros seguros"""
        sql = "INSERT INTO articulo VALUES (%s, %s, %s)"
        params = (id_art, nom_art, pre_art)
        return self.ejecutar_consulta(sql, params)

    def Select_articulo(self, id_art):
        """Obtiene un artículo por su ID usando parámetros seguros"""
        sql = "SELECT * FROM articulo WHERE id_art = %s"
        params = (id_art,)
        return self.ejecutar_consulta(sql, params, fetchone=True)

    # MÉTODOS PARA ÓRDENES
    def Insert_orden(self, id_orden, fec_orden, id_cliente):
        """Inserta una nueva orden usando parámetros seguros"""
        sql = "INSERT INTO orden VALUES (%s, %s, %s)"
        params = (id_orden, fec_orden, id_cliente)
        return self.ejecutar_consulta(sql, params)
    
    # Métodos específicos para la aplicación de gimnasio
    
    # MÉTODOS PARA USUARIOS DEL GIMNASIO
    def SelectAll_usuarios(self):
        """Obtiene todos los usuarios del gimnasio"""
        sql = "SELECT * FROM usuarios"
        return self.ejecutar_consulta(sql)
        
    def Insert_usuario(self, id_usuario, nombre, email, telefono, fecha_registro):
        """Inserta un nuevo usuario del gimnasio"""
        sql = "INSERT INTO usuarios (id_usuario, nombre, email, telefono, fecha_registro) VALUES (%s, %s, %s, %s, %s)"
        params = (id_usuario, nombre, email, telefono, fecha_registro)
        return self.ejecutar_consulta(sql, params)
    
    # MÉTODOS PARA EJERCICIOS
    def SelectAll_ejercicios(self):
        """Obtiene todos los ejercicios"""
        sql = "SELECT * FROM ejercicios"
        return self.ejecutar_consulta(sql)
        
    def Insert_ejercicio(self, id_ejercicio, nombre, descripcion, grupo_muscular):
        """Inserta un nuevo ejercicio"""
        sql = "INSERT INTO ejercicios (id_ejercicio, nombre, descripcion, grupo_muscular) VALUES (%s, %s, %s, %s)"
        params = (id_ejercicio, nombre, descripcion, grupo_muscular)
        return self.ejecutar_consulta(sql, params)
    
    # MÉTODOS PARA RUTINAS
    def SelectAll_rutinas(self):
        """Obtiene todas las rutinas"""
        sql = "SELECT * FROM rutinas"
        return self.ejecutar_consulta(sql)
        
    def Insert_rutina(self, id_rutina, nombre, descripcion, nivel_dificultad):
        """Inserta una nueva rutina"""
        sql = "INSERT INTO rutinas (id_rutina, nombre, descripcion, nivel_dificultad) VALUES (%s, %s, %s, %s)"
        params = (id_rutina, nombre, descripcion, nivel_dificultad)
        return self.ejecutar_consulta(sql, params)
    
    # MÉTODOS PARA ASIGNACIÓN DE RUTINAS A USUARIOS
    def Asignar_rutina(self, id_usuario, id_rutina, fecha_asignacion, fecha_fin):
        """Asigna una rutina a un usuario"""
        sql = "INSERT INTO usuario_rutina (id_usuario, id_rutina, fecha_asignacion, fecha_fin) VALUES (%s, %s, %s, %s)"
        params = (id_usuario, id_rutina, fecha_asignacion, fecha_fin)
        return self.ejecutar_consulta(sql, params)