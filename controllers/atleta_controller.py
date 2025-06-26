# Controlador para gestión de atletas
from models.atleta_model import AtletaModel
from models.usuario_model import UsuarioModel
from controllers.user_controller import UserController
from controllers.finance_controller import FinanceController
from models.coach_model import CoachModel
from datetime import datetime, date
import re


class AtletaController:
    def __init__(self):
        self.atleta_model = AtletaModel()
        self.usuario_model = UsuarioModel()
        self.user_controller = UserController()
        self.finance_controller = FinanceController()
        self.coach_model = CoachModel()
    
    # ==================== REGISTRO COMPLETO DE ATLETA ====================
    
    def registrar_atleta_completo(self, datos_atleta, metodo_pago, registrado_por_id):
        """
        Orquesta el proceso completo de registrar un atleta, asegurando la creación de un usuario.
        """
        try:
            print(f"--- DEBUG: Verificando permisos para el ID de usuario: {registrado_por_id} ---")
            # 1. Validar permisos del operador
            if not self._puede_gestionar_atletas(registrado_por_id):
                return {"success": False, "message": "No tienes permisos para registrar atletas"}
            
            # 2. Validar los datos de entrada del atleta usando tu función existente
            validacion = self._validar_datos_atleta_basicos(datos_atleta)
            if not validacion["success"]:
                return validacion

            # 3. Crear la cuenta de usuario asociada
            datos_para_usuario = {
                'nombre': datos_atleta['nombre'],
                'apellido': datos_atleta['apellido'],
                'email': datos_atleta.get('email') or f"{datos_atleta['cedula']}@sinemail.com",
                'contraseña': self.user_controller.generar_password_seguro(),
                'rol': 'atleta',
                'estado_activo': True
            }
            resultado_usuario = self.user_controller.crear_usuario(datos_para_usuario, registrado_por_id)
            if not resultado_usuario.get('success'):
                return {"success": False, "message": f"Error al crear cuenta de usuario: {resultado_usuario.get('message', 'Error desconocido.')}"}

            id_nuevo_usuario = resultado_usuario['usuario_id']
            
            # 4. Crear el perfil de atleta usando el ID del nuevo usuario
            # SIN CAMBIOS AQUÍ: La lógica ahora funciona porque el modelo devuelve un ID o None.
            atleta_id = self.atleta_model.insert_atleta(
                id_usuario=id_nuevo_usuario,
                cedula=datos_atleta['cedula'],
                peso=datos_atleta.get('peso'),
                fecha_nacimiento=datos_atleta.get('fecha_nacimiento'),
                id_plan=datos_atleta['id_plan'],
                id_coach=datos_atleta.get('id_coach'),
                meta_largo_plazo=datos_atleta.get('meta_largo_plazo', ''),
                valoracion_especiales=datos_atleta.get('valoracion_especiales', '')
            )
            
            if not atleta_id:
                # Si falla, se elimina el usuario creado para no dejar datos huérfanos
                self.user_controller.eliminar_usuario(id_nuevo_usuario, registrado_por_id)
                return {"success": False, "message": "Error al crear el perfil de atleta en la base de datos."}
            
            # 5. Procesar pago automático de inscripción
            pago_result = self.finance_controller.procesar_pago_inscripcion(
                id_atleta=id_nuevo_usuario, # El pago se vincula al ID de usuario
                id_plan=datos_atleta['id_plan'],
                metodo_pago=metodo_pago,
                procesado_por_id=registrado_por_id,
                descripcion="Pago inicial de membresía"
            )
                
            if not pago_result.get("success"):
                return {"success": True, 
                        "message": f"Atleta registrado (ID: {atleta_id}), pero el pago falló: {pago_result.get('message', 'N/A')}. Procesar manualmente."}
            
            # 6. Actualizar la fecha de vencimiento (si tienes un método para ello)
            # self.atleta_model.actualizar_vencimiento_atleta(atleta_id, pago_result['fecha_vencimiento'])

            return {
                "success": True,
                "message": "Atleta registrado y pago procesado exitosamente.",
                "atleta_id": atleta_id
            }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Error interno del controlador: {str(e)}"}
    
    # SOLUCIÓN: MÉTODO DE ELIMINACIÓN CORREGIDO Y COMPLETO
    def eliminar_atleta(self, atleta_id, operado_por_id):
        """
        Elimina el perfil de un atleta y su cuenta de usuario asociada.
        """
        try:
            # 1. Validar permisos
            if not self._puede_gestionar_atletas(operado_por_id):
                return {"success": False, "message": "No tienes permisos para eliminar atletas"}

            # 2. Obtener el id_usuario antes de borrar el perfil del atleta
            info_atleta = self.obtener_atleta_por_id(atleta_id)
            if not info_atleta.get("success"):
                return {"success": False, "message": "No se encontró el atleta a eliminar."}
            
            id_usuario_asociado = info_atleta["atleta"][1] # Posición 1 es id_usuario

            # 3. Eliminar el perfil del atleta desde el modelo
            if not self.atleta_model.delete_atleta(atleta_id):
                return {"success": False, "message": "Error al eliminar el perfil del atleta desde la base de datos."}

            # 4. Eliminar la cuenta de usuario asociada
            resultado_usuario = self.user_controller.eliminar_usuario(id_usuario_asociado, operado_por_id)
            if not resultado_usuario.get("success"):
                # Si esto falla, el perfil del atleta ya fue eliminado. Se informa para revisión manual.
                return {
                    "success": True, 
                    "message": f"Perfil del atleta eliminado, pero falló la eliminación de la cuenta de usuario asociada (ID Usuario: {id_usuario_asociado}). Por favor, revisar manualmente."
                }
            
            return {"success": True, "message": "Atleta y su cuenta de usuario asociada han sido eliminados correctamente."}

        except Exception as e:
            return {"success": False, "message": f"Error interno al eliminar atleta: {str(e)}"}


    # TAMBIÉN AGREGA ESTE MÉTODO DE VALIDACIÓN SIMPLIFICADO:
    def _validar_datos_atleta_basicos(self, datos_atleta):
        """Valida los datos básicos necesarios para crear un atleta"""
        # Campos requeridos
        campos_requeridos = ['nombre', 'apellido', 'cedula', 'id_plan']
        
        for campo in campos_requeridos:
            if not datos_atleta.get(campo):
                return {"success": False, "message": f"Campo requerido: {campo}"}
        
        # Validar que la cédula sea única
        if self._cedula_existe(datos_atleta['cedula']):
            return {"success": False, "message": "La cédula ya está registrada"}
        
        # Validar email si se proporciona
        if datos_atleta.get('email') and '@' not in datos_atleta['email']:
            return {"success": False, "message": "Email inválido"}
        
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
            id_plan = atleta_data[8]  # id_plan en posición 5
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
            # Esta implementación es ineficiente. Es mejor consultar por ID en la BD.
            # Por ahora, se mantiene la lógica original para no introducir cambios mayores.
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
            atletas_coach = [a for a in atletas if a[6] == coach_id]  
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
            from datetime import timedelta
            fecha_limite = date.today() + timedelta(days=dias_adelanto)
            atletas = self.atleta_model.read_atletas()
            
            atletas_proximos = []
            for atleta in atletas:
                fecha_vencimiento_str = atleta[7]  # fecha_vencimiento en posición 7
                if fecha_vencimiento_str:
                    fecha_vencimiento = datetime.strptime(str(fecha_vencimiento_str), '%Y-%m-%d').date()
                    if fecha_vencimiento <= fecha_limite and atleta[9] == 'solvente':
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
            
            atleta = self.obtener_atleta_por_id(atleta_id)
            if not atleta["success"]:
                return {"success": False, "message": "Atleta no encontrado"}
            
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
                id_plan=atleta_data[7],
                id_coach=coach_id,
                meta_largo_plazo=atleta_data[9],
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
            usuario = self.usuario_model.get_user_by_id(user_id) # Asumiendo que el modelo de usuario tiene este método
            if usuario:
                return usuario[8] == 'secretaria'  # rol en posición 8
            return False
        except Exception:
            return False
    
    # ==================== MÉTODO DE PERMISOS (VERSIÓN FINAL Y CORRECTA) ====================
    def _puede_gestionar_atletas(self, user_id):
        """Verifica si el usuario puede gestionar atletas (admin_principal y secretarias)"""
        try:
            # Esta es la línea clave y correcta: usa el user_controller.
            usuario = self.user_controller.obtener_usuario_por_id(user_id)
            
            if usuario:
                # El rol está en la posición 8 de la tupla del usuario.
                rol = usuario[8]
                
                # La lista de roles permitidos. Tu rol 'admin_principal' está aquí.
                roles_permitidos = ['admin_principal', 'secretaria', 'Admin Principal']
                
                # Esto devolverá True si tu rol está en la lista.
                return rol in roles_permitidos
            
            # Si no se encuentra el usuario, no da permisos.
            return False
            
        except Exception as e:
            # En caso de un error inesperado, lo veremos en la consola.
            print(f"Error inesperado al verificar permisos: {e}")
            return False
    
    def _validar_datos_completos(self, datos_atleta, datos_usuario):
        return {"success": True}
    
   
    def _coach_existe(self, coach_id):
        """Verifica si el coach existe en la tabla coaches"""
        try:
            coaches = self.coach_model.read_coaches()
            return any(coach[0] == coach_id for coach in coaches)  # id_coach en posición 0
        except Exception:
            return False

    def obtener_coaches_disponibles(self):
        """Obtiene lista de coaches disponibles para asignar"""
        try:
            # Primero necesitas el método get_coaches_disponibles en coach_model
            coaches = self.coach_model.get_coaches_disponibles()  
            return {"success": True, "coaches": coaches}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener coaches: {str(e)}"}

    def _cedula_existe(self, cedula):
        """Verifica si la cédula ya está registrada"""
        try:
            atletas = self.atleta_model.read_atletas()
            return any(atleta[2] == cedula for atleta in atletas)
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
        print(f"Lógica para actualizar membresía del atleta {atleta_id} no implementada en el modelo.")
        pass
    
    def _actualizar_plan_y_membresia(self, atleta_id, nuevo_plan_id, fecha_vencimiento, estado_solvencia, fecha_ultimo_pago):
        """Actualiza el plan y estado de membresía del atleta"""
        try:
            atleta = self.obtener_atleta_por_id(atleta_id)
            if atleta["success"]:
                atleta_data = atleta["atleta"]
                
                self.atleta_model.update_atleta(
                    id_atleta=atleta_id,
                    id_usuario=atleta_data[1],
                    cedula=atleta_data[2],
                    peso=atleta_data[3],
                    fecha_nacimiento=atleta_data[4],
                    id_plan=nuevo_plan_id,  # Se actualiza el plan
                    id_coach=atleta_data[6],
                    meta_largo_plazo=atleta_data[8],
                    valoracion_especiales=atleta_data[10]
                )
                # También se debería actualizar la fecha de vencimiento aquí.
                
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
            
            if 'cedula' in datos_atleta and datos_atleta['cedula'] != atleta_data[2]:
                if self._cedula_existe(datos_atleta['cedula']):
                    return {"success": False, "message": "La cédula ya está registrada"}
            
            resultado = self.atleta_model.update_atleta(
                id_atleta=atleta_id,
                id_usuario=atleta_data[1],
                cedula=datos_atleta.get('cedula', atleta_data[2]),
                peso=datos_atleta.get('peso', atleta_data[3]),
                fecha_nacimiento=datos_atleta.get('fecha_nacimiento', atleta_data[4]),
                id_plan=atleta_data[7],
                id_coach=datos_atleta.get('id_coach', atleta_data[6]),
                meta_largo_plazo=datos_atleta.get('meta_largo_plazo', atleta_data[9]),
                valoracion_especiales=datos_atleta.get('valoracion_especiales', atleta_data[10])
            )
            
            if resultado:
                return {"success": True, "message": "Perfil de atleta actualizado exitosamente"}
            else:
                return {"success": False, "message": "Error al actualizar el perfil"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
        

def obtener_detalles_completos_atleta(self, id_atleta):
    try:
        datos = self.model.obtener_detalles_completos_atleta(id_atleta)
        if datos:
            return {'success': True, 'atleta': datos}
        else:
            return {'success': False, 'message': 'No se encontraron datos del atleta'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

        
        