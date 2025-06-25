# Controlador para autenticación y sesiones
from controllers.user_controller import UserController
from models.usuario_model import UsuarioModel
import hashlib
import secrets
import time
from datetime import datetime, timedelta


class AuthController:
    def __init__(self):
        self.user_controller = UserController()
        self.usuario_model = UsuarioModel()
        # Almacén de sesiones en memoria (en producción usar Redis/Base de datos)
        self.sesiones_activas = {}
        self.tiempo_expiracion = 3600  
        self.intentos_fallidos = {}
        self.tiempo_bloqueo = 300  
    
    # ==================== SISTEMA DE LOGIN ====================
  
    def iniciar_sesion(self, email, password, ip_cliente=""):
        """
        Inicia sesión de usuario con validaciones de seguridad
        """
        try:
            # Verificar si la IP está bloqueada por intentos fallidos
            if self._ip_esta_bloqueada(ip_cliente):
                tiempo_restante = self._tiempo_restante_bloqueo(ip_cliente)
                return {
                    "success": False, 
                    "message": f"IP bloqueada por intentos fallidos. Intenta en {tiempo_restante} minutos"
                }
            
            # Validar que se proporcionen credenciales
            if not email or not password:
                return {"success": False, "message": "Email y contraseña son requeridos"}
            
            # Validar credenciales
            validacion = self.user_controller.validar_credenciales(email, password)
            
            if not validacion["success"]:
                # Registrar intento fallido
                self._registrar_intento_fallido(ip_cliente)
                return {"success": False, "message": "Credenciales incorrectas"}
            
            usuario = validacion["usuario"]
            
            # Verificar que el usuario esté activo
            if not self._usuario_esta_activo(usuario["id"]):
                return {"success": False, "message": "Usuario desactivado. Contacta al administrador"}
            
            # Generar token de sesión único
            token_sesion = self._generar_token_sesion()
            
            # Crear sesión
            self._crear_sesion(token_sesion, usuario, ip_cliente)
            
            # Limpiar intentos fallidos exitosos
            self._limpiar_intentos_fallidos(ip_cliente)
            
            return {
                "success": True,
                "message": f"Bienvenido {usuario['nombre']} {usuario['apellido']}",
                "token_sesion": token_sesion,
                "usuario": {
                    "id": usuario["id"],
                    "nombre": usuario["nombre"],
                    "apellido": usuario["apellido"],
                    "email": usuario["email"],
                    "rol": usuario["rol"]
                },
                "dashboard_url": self._obtener_dashboard_por_rol(usuario["rol"])
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error interno en login: {str(e)}"}
    
    def cerrar_sesion(self, token_sesion):
        """Cierra la sesión del usuario"""
        try:
            if token_sesion in self.sesiones_activas:
                usuario_info = self.sesiones_activas[token_sesion]["usuario"]
                del self.sesiones_activas[token_sesion]
                
                return {
                    "success": True,
                    "message": f"Sesión cerrada. ¡Hasta luego {usuario_info['nombre']}!"
                }
            else:
                return {"success": False, "message": "Sesión no encontrada"}
                
        except Exception as e:
            return {"success": False, "message": f"Error al cerrar sesión: {str(e)}"}
    
    def cerrar_todas_sesiones_usuario(self, user_id):
        """Cierra todas las sesiones activas de un usuario específico"""
        try:
            sesiones_cerradas = 0
            tokens_a_eliminar = []
            
            for token, sesion in self.sesiones_activas.items():
                if sesion["usuario"]["id"] == user_id:
                    tokens_a_eliminar.append(token)
                    sesiones_cerradas += 1
            
            for token in tokens_a_eliminar:
                del self.sesiones_activas[token]
            
            return {
                "success": True,
                "message": f"Se cerraron {sesiones_cerradas} sesiones del usuario"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error al cerrar sesiones: {str(e)}"}
    
    # ==================== GESTIÓN DE SESIONES ====================
    
    def validar_sesion(self, token_sesion):
        """Valida si una sesión es válida y activa"""
        try:
            if not token_sesion or token_sesion not in self.sesiones_activas:
                return {"success": False, "message": "Sesión no válida"}
            
            sesion = self.sesiones_activas[token_sesion]
            
            # Verificar si la sesión ha expirado
            if self._sesion_expirada(sesion):
                del self.sesiones_activas[token_sesion]
                return {"success": False, "message": "Sesión expirada. Inicia sesión nuevamente"}
            
            # Verificar que el usuario siga activo
            if not self._usuario_esta_activo(sesion["usuario"]["id"]):
                del self.sesiones_activas[token_sesion]
                return {"success": False, "message": "Usuario desactivado"}
            
            # Actualizar último acceso
            sesion["ultimo_acceso"] = time.time()
            
            return {
                "success": True,
                "usuario": sesion["usuario"],
                "tiempo_restante": self._tiempo_restante_sesion(sesion)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error validando sesión: {str(e)}"}
    
    def obtener_sesiones_activas(self, admin_user_id):
        """Obtiene todas las sesiones activas (solo para administradores)"""
        try:
            # Verificar que el usuario sea administrador
            if not self._es_administrador(admin_user_id):
                return {"success": False, "message": "No tienes permisos para ver sesiones activas"}
            
            # Limpiar sesiones expiradas primero
            self._limpiar_sesiones_expiradas()
            
            sesiones_info = []
            for token, sesion in self.sesiones_activas.items():
                sesiones_info.append({
                    "token": token[:10] + "...",  # Solo mostrar parte del token por seguridad
                    "usuario": sesion["usuario"]["nombre"] + " " + sesion["usuario"]["apellido"],
                    "email": sesion["usuario"]["email"],
                    "rol": sesion["usuario"]["rol"],
                    "ip": sesion["ip_cliente"],
                    "inicio_sesion": datetime.fromtimestamp(sesion["inicio_sesion"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "ultimo_acceso": datetime.fromtimestamp(sesion["ultimo_acceso"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "tiempo_restante": self._tiempo_restante_sesion(sesion)
                })
            
            return {
                "success": True,
                "sesiones_activas": sesiones_info,
                "total_sesiones": len(sesiones_info)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error obteniendo sesiones: {str(e)}"}
    
    def extender_sesion(self, token_sesion):
        """Extiende el tiempo de vida de una sesión"""
        try:
            validacion = self.validar_sesion(token_sesion)
            if not validacion["success"]:
                return validacion
            
            sesion = self.sesiones_activas[token_sesion]
            sesion["ultimo_acceso"] = time.time()
            
            return {
                "success": True,
                "message": "Sesión extendida exitosamente",
                "tiempo_restante": self._tiempo_restante_sesion(sesion)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error extendiendo sesión: {str(e)}"}
    
    # ==================== CONTROL DE ACCESO POR ROL ====================
    
    def verificar_permisos(self, token_sesion, roles_permitidos):
        """Verifica si el usuario tiene permisos para acceder a una función"""
        try:
            validacion = self.validar_sesion(token_sesion)
            if not validacion["success"]:
                return validacion
            
            usuario_rol = validacion["usuario"]["rol"]
            
            if usuario_rol in roles_permitidos:
                return {"success": True, "usuario": validacion["usuario"]}
            else:
                return {
                    "success": False, 
                    "message": f"Acceso denegado. Requiere rol: {', '.join(roles_permitidos)}"
                }
                
        except Exception as e:
            return {"success": False, "message": f"Error verificando permisos: {str(e)}"}
    
    def requiere_admin(self, token_sesion):
        """Verificación rápida para operaciones que requieren admin"""
        return self.verificar_permisos(token_sesion, ['admin_principal'])
    
    def requiere_secretaria_o_admin(self, token_sesion):
        """Verificación para operaciones que requieren secretaria o admin"""
        return self.verificar_permisos(token_sesion, ['admin_principal', 'secretaria'])
    
    def requiere_coach_o_superior(self, token_sesion):
        """Verificación para operaciones que requieren coach o superior"""
        return self.verificar_permisos(token_sesion, ['admin_principal', 'secretaria', 'coach'])
    
    # ==================== CAMBIO DE CONTRASEÑA ====================
    
    def cambiar_contraseña(self, token_sesion, contraseña_actual, contraseña_nueva):
        """Permite al usuario cambiar su contraseña"""
        try:
            # Validar sesión
            validacion = self.validar_sesion(token_sesion)
            if not validacion["success"]:
                return validacion
            
            usuario = validacion["usuario"]
            
            # Validar contraseña actual
            credenciales_validas = self.user_controller.validar_credenciales(
                usuario["email"], contraseña_actual
            )
            
            if not credenciales_validas["success"]:
                return {"success": False, "message": "Contraseña actual incorrecta"}
            
            # Validar nueva contraseña
            if not self._validar_nueva_contraseña(contraseña_nueva):
                return {
                    "success": False, 
                    "message": "La nueva contraseña debe tener al menos 6 caracteres"
                }
            
            # Actualizar contraseña
            datos_actualizacion = {"contraseña": contraseña_nueva}
            resultado = self.user_controller.actualizar_usuario(
                usuario["id"], datos_actualizacion, usuario["id"]
            )
            
            if resultado["success"]:
                # Cerrar todas las demás sesiones del usuario por seguridad
                self.cerrar_todas_sesiones_usuario(usuario["id"])
                
                # Crear nueva sesión
                nuevo_token = self._generar_token_sesion()
                self._crear_sesion(nuevo_token, usuario, "")
                
                return {
                    "success": True,
                    "message": "Contraseña cambiada exitosamente",
                    "nuevo_token": nuevo_token
                }
            else:
                return {"success": False, "message": "Error al cambiar contraseña"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    # ==================== MÉTODOS PRIVADOS ====================
    
    def _generar_token_sesion(self):
        """Genera un token único para la sesión"""
        return secrets.token_urlsafe(32)
    
    def _crear_sesion(self, token, usuario, ip_cliente):
        """Crea una nueva sesión"""
        self.sesiones_activas[token] = {
            "usuario": usuario,
            "inicio_sesion": time.time(),
            "ultimo_acceso": time.time(),
            "ip_cliente": ip_cliente
        }
    
    def _sesion_expirada(self, sesion):
        """Verifica si una sesión ha expirado"""
        return (time.time() - sesion["ultimo_acceso"]) > self.tiempo_expiracion
    
    def _tiempo_restante_sesion(self, sesion):
        """Calcula el tiempo restante de una sesión en minutos"""
        tiempo_transcurrido = time.time() - sesion["ultimo_acceso"]
        tiempo_restante = self.tiempo_expiracion - tiempo_transcurrido
        return max(0, int(tiempo_restante / 60))  # En minutos
    
    def _usuario_esta_activo(self, user_id):
        """Verifica si un usuario está activo"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == user_id:
                    return usuario[9]  # estado_activo en posición 9
            return False
        except Exception:
            return False
    
    def _es_administrador(self, user_id):
        """Verifica si un usuario es administrador"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == user_id:
                    return usuario[8] == 'admin_principal'  # rol en posición 8
            return False
        except Exception:
            return False
    
    def _obtener_dashboard_por_rol(self, rol):
        """Retorna la URL del dashboard según el rol"""
        dashboard_urls = {
            'admin_principal': '/dashboard/admin',
            'secretaria': '/dashboard/secretaria',
            'coach': '/dashboard/coach',
            'atleta': '/dashboard/atleta'
        }
        return dashboard_urls.get(rol, '/dashboard/default')
    
    def _limpiar_sesiones_expiradas(self):
        """Limpia sesiones expiradas del almacén"""
        try:
            tokens_expirados = []
            for token, sesion in self.sesiones_activas.items():
                if self._sesion_expirada(sesion):
                    tokens_expirados.append(token)
            
            for token in tokens_expirados:
                del self.sesiones_activas[token]
                
        except Exception as e:
            print(f"Error limpiando sesiones: {str(e)}")
    
    # ==================== CONTROL DE INTENTOS FALLIDOS ====================
    
    def _ip_esta_bloqueada(self, ip):
        """Verifica si una IP está bloqueada por intentos fallidos"""
        if ip not in self.intentos_fallidos:
            return False
        
        datos_ip = self.intentos_fallidos[ip]
        
        # Si tiene más de 5 intentos fallidos
        if datos_ip["intentos"] >= 5:
            # Y el último intento fue hace menos del tiempo de bloqueo
            if (time.time() - datos_ip["ultimo_intento"]) < self.tiempo_bloqueo:
                return True
            else:
                # Si ya pasó el tiempo de bloqueo, limpiar
                del self.intentos_fallidos[ip]
                return False
        
        return False
    
    def _registrar_intento_fallido(self, ip):
        """Registra un intento fallido de login"""
        if ip:
            if ip not in self.intentos_fallidos:
                self.intentos_fallidos[ip] = {"intentos": 0, "ultimo_intento": 0}
            
            self.intentos_fallidos[ip]["intentos"] += 1
            self.intentos_fallidos[ip]["ultimo_intento"] = time.time()
    
    def _limpiar_intentos_fallidos(self, ip):
        """Limpia los intentos fallidos de una IP tras login exitoso"""
        if ip in self.intentos_fallidos:
            del self.intentos_fallidos[ip]
    
    def _tiempo_restante_bloqueo(self, ip):
        """Calcula el tiempo restante de bloqueo en minutos"""
        if ip in self.intentos_fallidos:
            tiempo_transcurrido = time.time() - self.intentos_fallidos[ip]["ultimo_intento"]
            tiempo_restante = self.tiempo_bloqueo - tiempo_transcurrido
            return max(0, int(tiempo_restante / 60))
        return 0
    
    def _validar_nueva_contraseña(self, contraseña):
        """Valida que la nueva contraseña cumpla los requisitos mínimos"""
        return len(contraseña) >= 6
    
    # ==================== UTILIDADES PARA LAS VISTAS ====================
    
    def obtener_usuario_actual(self, token_sesion):
        """Obtiene los datos del usuario actual de la sesión"""
        validacion = self.validar_sesion(token_sesion)
        if validacion["success"]:
            return validacion["usuario"]
        return None
    
    def middleware_auth(self, token_sesion, roles_requeridos=None):
        """Middleware para validar autenticación en las vistas"""
        # Validar sesión
        validacion = self.validar_sesion(token_sesion)
        if not validacion["success"]:
            return {
                "autenticado": False,
                "mensaje": validacion["message"],
                "redirect": "/login"
            }
        
        # Si se especifican roles, validarlos
        if roles_requeridos:
            permisos = self.verificar_permisos(token_sesion, roles_requeridos)
            if not permisos["success"]:
                return {
                    "autenticado": True,
                    "autorizado": False,
                    "mensaje": permisos["message"],
                    "redirect": "/acceso-denegado"
                }
        
        return {
            "autenticado": True,
            "autorizado": True,
            "usuario": validacion["usuario"]
        }

    def iniciar_sesion_debug(self, email, password, ip_cliente=""):
        """MÉTODO DE DEBUG - USA ESTE TEMPORALMENTE"""
        print(f"\n🔍 === DEBUG LOGIN AuthController ===")
        print(f"Email recibido: '{email}'")
        print(f"Password recibido: '{password}'")
        print(f"IP cliente: '{ip_cliente}'")
        
        try:
            # BYPASS: validación directa con base de datos
            print("🔍 Consultando directamente la base de datos...")
            usuarios = self.usuario_model.read_usuarios()
            print(f"🔍 Total usuarios en BD: {len(usuarios)}")
            
            for usuario in usuarios:
                print(f"\n🔍 Verificando usuario:")
                print(f"  ID: {usuario[0]}")
                print(f"  Nombre: {usuario[1]} {usuario[2]}")
                print(f"  Email BD: '{usuario[6]}'")
                print(f"  Password BD: '{usuario[7]}'")
                print(f"  Rol: '{usuario[8]}'")
                print(f"  Activo: {usuario[9]}")
                
                # Comparación exacta
                email_match = str(usuario[6]).strip().lower() == email.strip().lower()
                password_match = self.user_controller._verify_password(password.strip(), usuario[7])

                
                print(f"  Email match: {email_match}")
                print(f"  Password match: {password_match}")
                
                if email_match and password_match:
                    print("✅ ¡CREDENCIALES VÁLIDAS! Creando sesión...")
                    
                    # Crear datos de usuario
                    usuario_data = {
                        "id": usuario[0],
                        "nombre": usuario[1],
                        "apellido": usuario[2],
                        "email": usuario[6],
                        "rol": usuario[8]
                    }
                    
                    # Generar token y crear sesión
                    token_sesion = self._generar_token_sesion()
                    self._crear_sesion(token_sesion, usuario_data, ip_cliente)
                    
                    return {
                        "success": True,
                        "message": f"Bienvenido {usuario[1]} {usuario[2]}",
                        "token_sesion": token_sesion,
                        "usuario": usuario_data,
                        "dashboard_url": self._obtener_dashboard_por_rol(usuario[8])
                    }
            
            print("❌ No se encontraron credenciales válidas")
            return {"success": False, "message": "Credenciales incorrectas"}
            
        except Exception as e:
            print(f"❌ Error en debug login: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Error interno: {str(e)}"}

    def iniciar_sesion(self, email, password, ip_cliente=""):
        """TEMPORALMENTE USA EL DEBUG"""
        return self.iniciar_sesion_debug(email, password, ip_cliente)