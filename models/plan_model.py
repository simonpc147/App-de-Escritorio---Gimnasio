# Modelo para gestión de planes
from .database import Database

class PlanModel:
    def __init__(self):
        self.db = Database()
    
    # Aquí van los métodos para planes
