# Modelo para gestión de ingresos
from .database import Database

class IngresoModel:
    def __init__(self):
        self.db = Database()
    
    # Aquí van los métodos para ingresos
