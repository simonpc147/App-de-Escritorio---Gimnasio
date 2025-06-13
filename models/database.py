import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        # Configuración de la base de datos
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # Cambiar por tu contraseña
            'database': 'ahenas',
            'port': 3306
        }
        self.connection = None
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            
            if self.connection.is_connected():
                print("✅ Conexión exitosa a la base de datos")
                print(f"📊 Base de datos: {self.config['database']}")
                return True
                
        except Error as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    def disconnect(self):
        """Desconectar"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Conexión cerrada")
