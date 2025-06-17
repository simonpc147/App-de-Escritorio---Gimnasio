# Controlador para gestión de atletas
from models.atleta_model import AtletaModel
from models.usuario_model import UsuarioModel
from controllers.user_controller import UserController
from controllers.finance_controller import FinanceController
from datetime import datetime, date
import re


class AtletaController:
    def __init__(self):
        self.atleta_model = AtletaModel()
        self.usuario_model = UsuarioModel()
        self.user_controller = UserController()
        self.finance_controller = FinanceController()
    
    # ==================== REGISTRO COMPLETO DE ATLETA ====================
    
    def registrar_atleta_completo(self, datos_atleta, datos_usuario, metodo_pago, registrado_por_id):
        """
        Registro completo de atleta siguiendo el flujo de la aplicación:
        1. Crear usuario
        2. Crear perfil de atleta
        3. Procesar pago automático
        4. Actualizar fecha de vencimiento y estado
        """
        try:
            # PASO 1: Validar permisos (solo secretarias pueden registrar atletas)
            if not self._puede_registrar_atletas(registrado_por_id):
                return {"success": False, "message": "No tienes permisos para registrar atletas"}
            
            # PASO 2: Validar datos del atleta
            validacion = self._validar_datos_completos(datos_atleta, datos_usuario)
            if not validacion["success"]:
                return validacion
            
            # PASO 3: Validar que el plan existe y está activo
            plan_valido = self.finance_controller.validar_plan_para_atleta(datos_atleta['id_plan'])
            if not plan_valido["success"]:
                return {"success": False, "message": f"Plan inválido: {plan_valido['message']}"}
            
            # PASO 4: Crear usuario base
            datos_usuario['rol'] = 'atleta'
            usuario_result = self.user_controller.crear_usuario(datos_usuario, registrado_por_id)
            if not usuario_result["success"]:
                return {"success": False, "message": f"Error al crear usuario: {usuario_result['message']}"}
            
            usuario_id = usuario_result["usuario_id"]
            
            try:
                # PASO 5: Crear perfil de atleta
                atleta_creado = self.atleta_model.insert_atleta(
                    id_usuario=usuario_id,
                    cedula=datos_atleta['cedula'],
                    peso=datos_atleta.get('peso'),
                    fecha_nacimiento=datos_atleta.get('fecha_nacimiento'),
                    id_plan=datos_atleta['id_plan'],
                    id_coach=datos_atleta.get('id_coach'),
                    meta_largo_plazo=datos_atleta.get('meta_largo_plazo', ''),
                    valoracion_especiales=datos_atleta.get('valoracion_especiales', '')
                )
                
                if not atleta_creado:
                    # Si falla, limpiar el usuario creado
                    self.user_controller.desactivar_usuario(usuario_id, registrado_por_id)
                    return {"success": False, "message": "Error al crear perfil de atleta"}
                
                # PASO 6: Obtener ID del atleta recién creado
                atleta_id = self._obtener_atleta_id_por_usuario(usuario_id)
                if not atleta_id:
                    return {"success": False, "message": "Error al obtener ID del atleta"}
                
                # PASO 7: Procesar pago automático de inscripción
                pago_result = self.finance_controller.procesar_pago_inscripcion(
                    id_atleta=atleta_id,
                    id_plan=datos_atleta['id_plan'],
                    metodo_pago=metodo_pago,
                    procesado_por_id=registrado_por_id,
                    descripcion="Pago inicial de membresía"
                )
                
                if not pago_result["success"]:
                    return {"success": False, "message": f"Error al procesar pago: {pago_result['message']}"}
                
                # PASO 8: Actualizar atleta con fecha de vencimiento y estado solvente
                fecha_vencimiento = pago_result["fecha_vencimiento"]
                self._actualizar_estado_membresia(atleta_id, fecha_vencimiento, 'solvente', datetime.now().date())
                
                return {
                    "success": True,
                    "message": "Atleta registrado exitosamente",
                    "atleta_id": atleta_id,
                    "usuario_id": usuario_id,
                    "fecha_vencimiento": fecha_vencimiento,
                    "monto_pagado": pago_result["monto"]
                }
                
            except Exception as e:
                # Si algo falla después de crear el usuario, desactivarlo
                self.user_controller.desactivar_usuario(usuario_id, registrado_por_id)
                return {"success": False, "message": f"Error en el proceso de registro: {str(e)}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    # ==================== GESTIÓN DE MEMBRESÍAS ====================
    
    def renovar_membresia(self, atleta_id, metodo_pago, procesado_por_id):
        """Renueva la membresía de un atleta"""
        try:
            if not self._puede_gestionar_atletas(procesado_por_id):
                return {"success": False, "message": "No tienes permisos para renovar membresías"}
            
            # Obtener datos del atleta
            atleta = self.obtener_atleta_por_id(atleta_id)
            if not atleta["success"]:
                return {"success": False, "message": "Atleta no encontrado"}
            
            atleta_data = atleta["atleta"]
            id_plan = atleta_data[5]  # id_plan en posición 5
            fecha_vencimiento_actual = atleta_data[7]  # fecha_vencimiento en posición 7
            
            # Procesar renovación
            renovacion_result = self.finance_controller.procesar_renovacion_membresia(
                id_atleta=atleta_id,
                id_plan=id_plan,
                metodo_pago=metodo_pago,
                procesado_por_id=procesado_por_id,
                fecha_vencimiento_actual=fecha_vencimiento_actual
            )
            
            if not renovacion_result["success"]:
                return renovacion_result
            
            # Actualizar estado del atleta
            nueva_fecha_vencimiento = renovacion_result["fecha_vencimiento_nueva"]
            self._actualizar_estado_membresia(atleta_id, nueva_fecha_vencimiento, 'solvente', datetime.now().date())
            
            return {
                "success": True,
                "message": "Membresía renovada exitosamente",
                "fecha_vencimiento_anterior": fecha_vencimiento_actual,
                "fecha_vencimiento_nueva": nueva_fecha_vencimiento,
                "monto": renovacion_result["monto"]
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def cambiar_plan_atleta(self, atleta_id, nuevo_plan_id, metodo_pago, procesado_por_id):
        """Cambia el plan de un atleta y procesa el pago correspondiente"""
        try:
            if not self._puede_gestionar_atletas(procesado_por_id):
                return {"success": False, "message": "No tienes permisos para cambiar planes"}
            
            # Validar nuevo plan
            plan_valido = self.finance_controller.validar_plan_para_atleta(nuevo_plan_id)
            if not plan_valido["success"]:
                return {"success": False, "message": f"Plan inválido: {plan_valido['message']}"}
            
            # Obtener atleta actual
            atleta = self.obtener_atleta_por_id(atleta_id)
            if not atleta["success"]:
                return {"success": False, "message": "Atleta no encontrado"}
            
            atleta_data = atleta["atleta"]
            fecha_vencimiento_actual = atleta_data[7]
            
            # Procesar pago del nuevo plan (como renovación)
            cambio_result = self.finance_controller.procesar_renovacion_membresia(
                id_atleta=atleta_id,
                id_plan=nuevo_plan_id,
                metodo_pago=metodo_pago,
                procesado_por_id=procesado_por_id,
                fecha_vencimiento_actual=fecha_vencimiento_actual,
                descripcion=f"Cambio de plan a {plan_valido['plan']['nombre']}"
            )
            
            if not cambio_result["success"]:
                return cambio_result
            
            # Actualizar atleta con nuevo plan y fecha
            nueva_fecha_vencimiento = cambio_result["fecha_vencimiento_nueva"]
            self._actualizar_plan_y_membresia(atleta_id, nuevo_plan_id, nueva_fecha_vencimiento, 'solvente', datetime.now().date())
            
            return {
                "success": True,
                "message": "Plan cambiado exitosamente",
                "nuevo_plan": plan_valido['plan']['nombre'],
                "fecha_vencimiento_nueva": nueva_fecha_vencimiento,
                "monto": cambio_result["monto"]
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    # ==================== CONSULTAS Y FILTROS ====================
    
    def obtener_todos_atletas(self):
        """Obtiene todos los atletas con información del usuario"""
        try:
            atletas = self.atleta_model.read_atletas()
            usuarios = self.usuario_model.read_usuarios()
            
            # Combinar datos de atletas con usuarios
            atletas_completos = []
            for atleta in atletas:
                usuario = next((u for u in usuarios if u[0] == atleta[1]), None)  # id_usuario
                if usuario:
                    atleta_completo = {
                        'atleta_data': atleta,
                        'usuario_data': usuario
                    }
                    atletas_completos.append(atleta_completo)
            
            return {"success": True, "atletas": atletas_completos}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener atletas: {str(e)}"}
    
    def obtener_atleta_por_id(self, atleta_id):
        """Obtiene un atleta específico por ID"""
        try:
            atletas = self.atleta_model.read_atletas()
            for atleta in atletas:
                if atleta[0] == atleta_id:  # id_atleta en posición 0
                    return {"success": True, "atleta": atleta}
            return {"success": False, "message": "Atleta no encontrado"}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener atleta: {str(e)}"}
    
    def obtener_atletas_por_coach(self, coach_id):
        """Obtiene atletas asignados a un coach específico"""
        try:
            atletas = self.atleta_model.read_atletas()
            atletas_coach = [a for a in atletas if a[6] == coach_id]  # id_coach en posición 6
            return {"success": True, "atletas": atletas_coach}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener atletas del coach: {str(e)}"}
    
    def obtener_atletas_por_estado_solvencia(self, estado):
        """Obtiene atletas filtrados por estado de solvencia"""
        try:
            atletas = self.atleta_model.read_atletas()
            atletas_filtrados = [a for a in atletas if a[9] == estado]  # estado_solvencia en posición 9
            return {"success": True, "atletas": atletas_filtrados}
        except Exception as e:
            return {"success": False, "message": f"Error al filtrar atletas: {str(e)}"}
    
    def obtener_atletas_proximos_vencer(self, dias_adelanto=7):
        """Obtiene atletas cuya membresía vence en los próximos días"""
        try:
            fecha_limite = datetime.now().date() + datetime.timedelta(days=dias_adelanto)
            atletas = self.atleta_model.read_atletas()
            
            atletas_proximos = []
            for atleta in atletas:
                fecha_vencimiento = atleta[7]  # fecha_vencimiento en posición 7
                if fecha_vencimiento and fecha_vencimiento <= fecha_limite and atleta[9] == 'solvente':
                    atletas_proximos.append(atleta)
            
            return {"success": True, "atletas": atletas_proximos}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener atletas próximos a vencer: {str(e)}"}
    
    # ==================== ASIGNACIÓN DE COACHES ====================
    
    def asignar_coach(self, atleta_id, coach_id, asignado_por_id):
        """Asigna o cambia el coach de un atleta"""
        try:
            if not self._puede_gestionar_atletas(asignado_por_id):
                return {"success": False, "message": "No tienes permisos para asignar coaches"}
            
            # Verificar que el atleta existe
            atleta = self.obtener_atleta_por_id(atleta_id)
            if not atleta["success"]:
                return {"success": False, "message": "Atleta no encontrado"}
            
            # Verificar que el coach existe
            if coach_id and not self._coach_existe(coach_id):
                return {"success": False, "message": "Coach no encontrado"}
            
            atleta_data = atleta["atleta"]
            
            # Actualizar atleta con nuevo coach
            resultado = self.atleta_model.update_atleta(
                id_atleta=atleta_id,
                id_usuario=atleta_data[1],
                cedula=atleta_data[2],
                peso=atleta_data[3],
                fecha_nacimiento=atleta_data[4],
                id_plan=atleta_data[5],
                id_coach=coach_id,
                meta_largo_plazo=atleta_data[8],
                valoracion_especiales=atleta_data[10]
            )
            
            if resultado:
                mensaje = "Coach asignado exitosamente" if coach_id else "Coach removido exitosamente"
                return {"success": True, "message": mensaje}
            else:
                return {"success": False, "message": "Error al asignar coach"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def _puede_registrar_atletas(self, user_id):
        """Verifica si el usuario puede registrar atletas (solo secretarias)"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == user_id:
                    return usuario[8] == 'secretaria'  # rol en posición 8
            return False
        except Exception:
            return False
    
    def _puede_gestionar_atletas(self, user_id):
        """Verifica si el usuario puede gestionar atletas (admin_principal y secretarias)"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == user_id:
                    rol = usuario[8]
                    return rol in ['admin_principal', 'secretaria']
            return False
        except Exception:
            return False
    
    def _validar_datos_completos(self, datos_atleta, datos_usuario):
        """Valida todos los datos necesarios para el registro"""
        # Validar datos de usuario
        campos_usuario_req = ['nombre', 'apellido', 'email', 'contraseña']
        for campo in campos_usuario_req:
            if not datos_usuario.get(campo):
                return {"success": False, "message": f"Campo requerido: {campo}"}
        
        # Validar email
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', datos_usuario['email']):
            return {"success": False, "message": "Email inválido"}
        
        # Validar datos de atleta
        campos_atleta_req = ['cedula', 'id_plan']
        for campo in campos_atleta_req:
            if not datos_atleta.get(campo):
                return {"success": False, "message": f"Campo requerido: {campo}"}
        
        # Validar que la cédula sea única
        if self._cedula_existe(datos_atleta['cedula']):
            return {"success": False, "message": "La cédula ya está registrada"}
        
        # Validar fecha de nacimiento si se proporciona
        if datos_atleta.get('fecha_nacimiento'):
            try:
                fecha_nac = datetime.strptime(str(datos_atleta['fecha_nacimiento']), '%Y-%m-%d').date()
                edad = (datetime.now().date() - fecha_nac).days // 365
                if edad < 16 or edad > 80:
                    return {"success": False, "message": "Edad debe estar entre 16 y 80 años"}
            except ValueError:
                return {"success": False, "message": "Fecha de nacimiento inválida"}
        
        return {"success": True}
    
    def _cedula_existe(self, cedula):
        """Verifica si la cédula ya está registrada"""
        try:
            atletas = self.atleta_model.read_atletas()
            for atleta in atletas:
                if atleta[2] == cedula:  # cedula en posición 2
                    return True
            return False
        except Exception:
            return False
    
    def _coach_existe(self, coach_id):
        """Verifica si el coach existe"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == coach_id and usuario[8] == 'coach':  # rol coach
                    return True
            return False
        except Exception:
            return False
    
    def _obtener_atleta_id_por_usuario(self, usuario_id):
        """Obtiene el ID del atleta por ID de usuario"""
        try:
            atletas = self.atleta_model.read_atletas()
            for atleta in atletas:
                if atleta[1] == usuario_id:  # id_usuario en posición 1
                    return atleta[0]  # id_atleta en posición 0
            return None
        except Exception:
            return None
    
    def _actualizar_estado_membresia(self, atleta_id, fecha_vencimiento, estado_solvencia, fecha_ultimo_pago):
        """Actualiza el estado de membresía del atleta"""
        try:
            atleta = self.obtener_atleta_por_id(atleta_id)
            if atleta["success"]:
                atleta_data = atleta["atleta"]
                
                # Actualizar con nueva fecha de vencimiento y estado
                self.atleta_model.update_atleta(
                    id_atleta=atleta_id,
                    id_usuario=atleta_data[1],
                    cedula=atleta_data[2],
                    peso=atleta_data[3],
                    fecha_nacimiento=atleta_data[4],
                    id_plan=atleta_data[5],
                    id_coach=atleta_data[6],
                    meta_largo_plazo=atleta_data[8],
                    valoracion_especiales=atleta_data[10]
                )
                # Nota: El modelo actual no incluye fecha_vencimiento y estado_solvencia
                # Deberías agregarlos al método update_atleta del modelo
                
        except Exception as e:
            print(f"Error al actualizar estado de membresía: {str(e)}")
    
    def _actualizar_plan_y_membresia(self, atleta_id, nuevo_plan_id, fecha_vencimiento, estado_solvencia, fecha_ultimo_pago):
        """Actualiza el plan y estado de membresía del atleta"""
        try:
            atleta = self.obtener_atleta_por_id(atleta_id)
            if atleta["success"]:
                atleta_data = atleta["atleta"]
                
                # Actualizar con nuevo plan y fechas
                self.atleta_model.update_atleta(
                    id_atleta=atleta_id,
                    id_usuario=atleta_data[1],
                    cedula=atleta_data[2],
                    peso=atleta_data[3],
                    fecha_nacimiento=atleta_data[4],
                    id_plan=nuevo_plan_id,  # Nuevo plan
                    id_coach=atleta_data[6],
                    meta_largo_plazo=atleta_data[8],
                    valoracion_especiales=atleta_data[10]
                )
                
        except Exception as e:
            print(f"Error al actualizar plan y membresía: {str(e)}")
    
    def actualizar_perfil_atleta(self, atleta_id, datos_atleta, actualizado_por_id):
        """Actualiza el perfil del atleta (sin afectar membresía)"""
        try:
            if not self._puede_gestionar_atletas(actualizado_por_id):
                return {"success": False, "message": "No tienes permisos para actualizar atletas"}
            
            atleta = self.obtener_atleta_por_id(atleta_id)
            if not atleta["success"]:
                return {"success": False, "message": "Atleta no encontrado"}
            
            atleta_data = atleta["atleta"]
            
            # Validar cédula si se está cambiando
            if 'cedula' in datos_atleta and datos_atleta['cedula'] != atleta_data[2]:
                if self._cedula_existe(datos_atleta['cedula']):
                    return {"success": False, "message": "La cédula ya está registrada"}
            
            # Actualizar datos
            resultado = self.atleta_model.update_atleta(
                id_atleta=atleta_id,
                id_usuario=atleta_data[1],
                cedula=datos_atleta.get('cedula', atleta_data[2]),
                peso=datos_atleta.get('peso', atleta_data[3]),
                fecha_nacimiento=datos_atleta.get('fecha_nacimiento', atleta_data[4]),
                id_plan=atleta_data[5],  # Mantener plan actual
                id_coach=datos_atleta.get('id_coach', atleta_data[6]),
                meta_largo_plazo=datos_atleta.get('meta_largo_plazo', atleta_data[8]),
                valoracion_especiales=datos_atleta.get('valoracion_especiales', atleta_data[10])
            )
            
            if resultado:
                return {"success": True, "message": "Perfil de atleta actualizado exitosamente"}
            else:
                return {"success": False, "message": "Error al actualizar el perfil"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}