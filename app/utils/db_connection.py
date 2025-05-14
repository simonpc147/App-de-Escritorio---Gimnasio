# app/utils/db_connection.py

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno (opcional pero recomendado para seguridad)
load_dotenv()

class DatabaseConnection:
    """
    Clase para manejar la conexión a la base de datos MySQL.
    Implementa el patrón Singleton para evitar múltiples conexiones.
    """
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Configuración de la base de datos
        # Es mejor obtener estos valores de variables de entorno
        self.host = os.getenv("DB_HOST", "sql109.infinityfree.com")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.user = os.getenv("DB_USER", "if0_38958987")
        self.password = os.getenv("DB_PASSWORD", "tu_contraseña_aquí")
        self.database = os.getenv("DB_NAME", "if0_38958987_athenas")
        
        # No conectamos automáticamente en la inicialización
        self._connection = None

    def connect(self):
        """Establece la conexión a la base de datos."""
        if self._connection is None:
            try:
                self._connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                if self._connection.is_connected():
                    print("Conexión a MySQL establecida correctamente")
                    return True
            except Error as e:
                print(f"Error al conectar a MySQL: {e}")
                return False
        return True

    def get_connection(self):
        """Retorna la conexión actual o crea una nueva si no existe."""
        if self._connection is None or not self._connection.is_connected():
            self.connect()
        return self._connection

    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL y devuelve los resultados.
        :param query: Consulta SQL
        :param params: Parámetros para la consulta (opcional)
        :return: Resultados de la consulta o None en caso de error
        """
        connection = self.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Para consultas que devuelven resultados (SELECT)
            if cursor.description:
                return cursor.fetchall()
            
            # Para consultas que modifican datos (INSERT, UPDATE, DELETE)
            connection.commit()
            return {"affected_rows": cursor.rowcount}
            
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            if connection.is_connected():
                connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
            print("Conexión a MySQL cerrada")

# Crear una instancia global para fácil importación
db = DatabaseConnection()

# Ejemplo de uso simple
def test_connection():
    """Prueba la conexión a la base de datos."""
    connection = db.get_connection()
    if connection and connection.is_connected():
        print(f"Conectado a MySQL versión: {connection.get_server_info()}")
        return True
    return False

# Si ejecutamos este archivo directamente, probar la conexión
if __name__ == "__main__":
    test_connection()
    
    # Ejemplo de consulta
    result = db.execute_query("SELECT VERSION() as version")
    if result:
        print(f"Versión de MySQL: {result[0]['version']}")
    
    # Cerrar conexión
    db.close()