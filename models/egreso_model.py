# Modelo para gestión de egresos
from .database import Database

class EgresoModel:
    def __init__(self):
        self.db = Database()
    
    # Aquí van los métodos para egresos
