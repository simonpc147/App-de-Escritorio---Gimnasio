# Controlador de autenticación
from models.usuario_model import UsuarioModel

class AuthController:
    def __init__(self):
        self.usuario_model = UsuarioModel()
    
    # Aquí van los métodos de autenticación
