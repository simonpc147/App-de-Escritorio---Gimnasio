# Modelo para gestión de usuarios
from .database import Database

class UsuarioModel:
    def __init__(self):
        self.db = Database()
    
    # Aquí van los métodos para usuarios
