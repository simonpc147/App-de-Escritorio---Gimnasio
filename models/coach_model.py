# Modelo para gestión de coaches
from .database import Database

class CoachModel:
    def __init__(self):
        self.db = Database()
    
    # Aquí van los métodos para coaches
