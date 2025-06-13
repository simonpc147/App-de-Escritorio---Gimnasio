# Controlador de usuarios
from models.usuario_model import UsuarioModel

class UserController:
    def __init__(self):
        self.usuario_model = UsuarioModel()
    
    # Aquí van los métodos para gestión de usuarios
