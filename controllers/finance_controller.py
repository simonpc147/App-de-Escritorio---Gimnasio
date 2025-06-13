# Controlador financiero
from models.ingreso_model import IngresoModel
from models.egreso_model import EgresoModel

class FinanceController:
    def __init__(self):
        self.ingreso_model = IngresoModel()
        self.egreso_model = EgresoModel()
    
    # Aquí van los métodos para gestión financiera
