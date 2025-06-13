# Modelo para gestión de atletas
from .database import Database

class AtletaModel:
    def __init__(self):
        self.db = Database()
    
    # Aquí van los métodos para atletas
