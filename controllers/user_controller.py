# Controlador para gestión de usuarios
import hashlib
from models.usuario_model import UsuarioModel
import secrets
import string


class UserController:
    def __init__(self):
        self.usuario_model = UsuarioModel()
    
    def _hash_password(self, password):
        """Cifra la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password, hashed_password):
        """Verifica si la contraseña coincide con el hash"""
        return self._hash_password(password) == hashed_password
    def generar_password_seguro(self, longitud=12):
        """
        Genera una contraseña segura con letras mayúsculas, minúsculas y números.
        """
        alfabeto = string.ascii_letters + string.digits
        while True:
            password = ''.join(secrets.choice(alfabeto) for _ in range(longitud))
            return password
    
    def crear_usuario(self, datos_usuario, creado_por_id):
        """
        Crea un nuevo usuario según las reglas de negocio
        """
        try:
            # Validar permisos según rol del creador
            if not self._validar_permisos_creacion(creado_por_id, datos_usuario['rol']):
                return {"success": False, "message": "No tienes permisos para crear este tipo de usuario"}
            
            # Validar datos requeridos
            if not self._validar_datos_usuario(datos_usuario):
                return {"success": False, "message": "Datos incompletos o inválidos"}
            
            # Verificar que el email no exista
            if self._email_existe(datos_usuario['email']):
                return {"success": False, "message": "El email ya está registrado"}
            
            # Cifrar contraseña
            password_hash = self._hash_password(datos_usuario['contraseña'])
            
            # Insertar usuario
            usuario_id = self.usuario_model.insert_usuario(
                datos_usuario['nombre'],
                datos_usuario['apellido'],
                datos_usuario.get('edad'),
                datos_usuario.get('direccion'),
                datos_usuario.get('telefono'),
                datos_usuario['email'],
                password_hash,
                datos_usuario['rol'],
                creado_por_id
            )
            
            if usuario_id:
                return {
                    "success": True, 
                    "message": f"Usuario {datos_usuario['rol']} creado exitosamente",
                    "usuario_id": usuario_id
                }
            else:
                return {"success": False, "message": "Error al crear el usuario"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def _validar_permisos_creacion(self, creador_id, rol_a_crear):
        """
        Valida permisos de creación según el flujo de la aplicación:
        - admin_principal: puede crear CUALQUIER usuario
        - secretaria: puede crear coaches y atletas
        """
        creador = self.obtener_usuario_por_id(creador_id)
        if not creador:
            return False
        
        creador_rol = creador[8]  # Posición del rol en la tupla
        
        # Reglas de creación CORREGIDAS
        
        if creador_rol == 'admin_principal':
            # Admin puede crear cualquier tipo de usuario
            return True
        elif creador_rol == 'secretaria' and rol_a_crear in ['coach', 'atleta']:
            # Secretaria puede crear coaches y atletas
            return True
        elif creador_rol== 'Admin Principal' and rol_a_crear in ['coach', 'atleta']:
            return True
        else:
            return False
    
    def _validar_datos_usuario(self, datos):
        """Valida que los datos del usuario sean correctos"""
        campos_requeridos = ['nombre', 'apellido', 'email', 'contraseña', 'rol']
        
        for campo in campos_requeridos:
            if not datos.get(campo) or datos[campo].strip() == '':
                return False
        
        # Validar email básico
        if '@' not in datos['email']:
            return False
        
        # Validar rol
        roles_validos = ['admin_principal', 'secretaria', 'coach', 'atleta']
        if datos['rol'] not in roles_validos:
            return False
        
        return True
    
    def _email_existe(self, email):
        """Verifica si el email ya existe en la base de datos"""
        usuarios = self.usuario_model.read_usuarios()
        for usuario in usuarios:
            if usuario[6] == email:  # email está en posición 6
                return True
        return False
    
    def obtener_todos_usuarios(self):
        """Obtiene todos los usuarios"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            return {"success": True, "usuarios": usuarios}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener usuarios: {str(e)}"}
    
    def obtener_usuario_por_id(self, user_id):
        """Obtiene un usuario específico por ID"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == user_id:  # ID está en posición 0
                    return usuario
            return None
        except Exception as e:
            print(f"Error al obtener usuario: {str(e)}")
            return None
    
    def obtener_usuarios_por_rol(self, rol):
        """Obtiene usuarios filtrados por rol"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            usuarios_filtrados = [u for u in usuarios if u[8] == rol]  # rol en posición 8
            return {"success": True, "usuarios": usuarios_filtrados}
        except Exception as e:
            return {"success": False, "message": f"Error al filtrar usuarios: {str(e)}"}
    
    def obtener_usuarios_creados_por(self, creador_id):
        """Obtiene usuarios creados por un usuario específico"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            usuarios_creados = [u for u in usuarios if u[10] == creador_id]  # CORREGIDO: creado_por en posición 10
            return {"success": True, "usuarios": usuarios_creados}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener usuarios creados: {str(e)}"}
    
    def actualizar_usuario(self, user_id, datos_usuario, quien_actualiza_id):
        """Actualiza un usuario existente"""
        try:
            # Validar que el usuario existe
            usuario_actual = self.obtener_usuario_por_id(user_id)
            if not usuario_actual:
                return {"success": False, "message": "Usuario no encontrado"}
            
            # Validar permisos de actualización
            if not self._puede_actualizar_usuario(quien_actualiza_id, user_id):
                return {"success": False, "message": "No tienes permisos para actualizar este usuario"}
            
            # Si se actualiza la contraseña, cifrarla
            if 'contraseña' in datos_usuario and datos_usuario['contraseña']:
                datos_usuario['contraseña'] = self._hash_password(datos_usuario['contraseña'])
            else:
                datos_usuario['contraseña'] = usuario_actual[7]  # Mantener contraseña actual
            
            # Actualizar usuario
            resultado = self.usuario_model.update_usuario(
                user_id,
                datos_usuario.get('nombre', usuario_actual[1]),
                datos_usuario.get('apellido', usuario_actual[2]),
                datos_usuario.get('edad', usuario_actual[3]),
                datos_usuario.get('direccion', usuario_actual[4]),
                datos_usuario.get('telefono', usuario_actual[5]),
                datos_usuario.get('email', usuario_actual[6]),
                datos_usuario['contraseña'],
                datos_usuario.get('rol', usuario_actual[8]),
                datos_usuario.get('estado_activo', usuario_actual[9])
            )
            
            if resultado:
                return {"success": True, "message": "Usuario actualizado exitosamente"}
            else:
                return {"success": False, "message": "Error al actualizar el usuario"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def _puede_actualizar_usuario(self, quien_actualiza_id, usuario_a_actualizar_id):
        """Verifica si un usuario puede actualizar a otro"""
        actualizador = self.obtener_usuario_por_id(quien_actualiza_id)
        if not actualizador:
            return False
        
        # admin_principal puede actualizar a todos
        if actualizador[8] == 'admin_principal':
            return True
        
        # Los usuarios pueden actualizar su propio perfil
        if quien_actualiza_id == usuario_a_actualizar_id:
            return True
        
        # Secretarias pueden actualizar coaches y atletas que crearon
        if actualizador[8] == 'secretaria':
            usuario_objetivo = self.obtener_usuario_por_id(usuario_a_actualizar_id)
            if usuario_objetivo and usuario_objetivo[10] == quien_actualiza_id:
                return True
        
        return False
    
    def desactivar_usuario(self, user_id, quien_desactiva_id):
        """Desactiva un usuario (no lo elimina)"""
        try:
            usuario = self.obtener_usuario_por_id(user_id)
            if not usuario:
                return {"success": False, "message": "Usuario no encontrado"}
            
            if not self._puede_actualizar_usuario(quien_desactiva_id, user_id):
                return {"success": False, "message": "No tienes permisos para desactivar este usuario"}
            
            # Actualizar solo el estado_activo
            resultado = self.usuario_model.update_usuario(
                user_id,
                usuario[1], usuario[2], usuario[3], usuario[4], usuario[5],
                usuario[6], usuario[7], usuario[8], False  # estado_activo = False
            )
            
            if resultado:
                return {"success": True, "message": "Usuario desactivado exitosamente"}
            else:
                return {"success": False, "message": "Error al desactivar el usuario"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    
    #ELIMINAR USUARIOS
    def eliminar_usuario(self, user_id):
        cursor = self.usuario_model.db.connection.cursor()
        query = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(query, (user_id,))
        self.usuario_model.db.connection.commit()
        cursor.close()
    

    def validar_credenciales(self, email, password):
        """Valida las credenciales de login"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[6] == email and usuario[9]:  # email y estado_activo (posición 9 CORRECTA)
                    if self._verify_password(password, usuario[7]):  # contraseña
                        return {
                            "success": True,
                            "usuario": {
                                "id": usuario[0],
                                "nombre": usuario[1],
                                "apellido": usuario[2],
                                "email": usuario[6],
                                "rol": usuario[8]
                            }
                        }
            
            return {"success": False, "message": "Credenciales incorrectas"}
            
        except Exception as e:
            return {"success": False, "message": f"Error en validación: {str(e)}"}

    def obtener_todos_usuarios_activos(self):
        """Obtiene solo usuarios activos"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            usuarios_activos = [u for u in usuarios if u[9]]  # estado_activo en posición 9
            return {"success": True, "usuarios": usuarios_activos}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener usuarios activos: {str(e)}"}