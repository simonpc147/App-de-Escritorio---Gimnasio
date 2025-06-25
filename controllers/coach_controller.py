# Controlador para gestión de coaches y asignaciones
from models.coach_model import CoachModel
from models.asign_coch_atlh_model import AsignacionModel
from models.usuario_model import UsuarioModel
from models.atleta_model import AtletaModel
from controllers.user_controller import UserController
from datetime import datetime, date
from decimal import Decimal


class CoachController:
    def __init__(self):
        self.coach_model = CoachModel()
        self.asignacion_model = AsignacionModel()
        self.usuario_model = UsuarioModel()
        self.atleta_model = AtletaModel()
        self.user_controller = UserController()
        
    
    # ==================== GESTIÓN DE COACHES ====================
    
    def registrar_coach_completo(self, datos_usuario, datos_coach, creado_por_id):
        """
        Registro completo de coach siguiendo el flujo:
        1. Crear usuario con rol 'coach'
        2. Crear perfil de coach
        """
        try:
            # Validar permisos (solo secretarias pueden crear coaches)
            if not self._puede_crear_coaches(creado_por_id):
                return {"success": False, "message": "No tienes permisos para crear coaches"}
            
            # Validar datos
            if not self._validar_datos_coach(datos_usuario, datos_coach):
                return {"success": False, "message": "Datos incompletos o inválidos"}
            
            # Crear usuario base
            datos_usuario['rol'] = 'coach'
            usuario_result = self.user_controller.crear_usuario(datos_usuario, creado_por_id)
            if not usuario_result["success"]:
                return {"success": False, "message": f"Error al crear usuario: {usuario_result['message']}"}
            
            usuario_id = usuario_result["usuario_id"]
            
            try:
                # Crear perfil de coach
                coach_id = self.coach_model.insert_coach(
                    id_usuario=usuario_id,
                    especialidades=datos_coach.get('especialidades', ''),
                    horario_disponible=datos_coach.get('horario_disponible', ''),
                    fecha_contratacion=datos_coach.get('fecha_contratacion', datetime.now().date()),
                    salario=datos_coach.get('salario')
                )
                
                if coach_id:
                    return {
                        "success": True,
                        "message": "Coach registrado exitosamente",
                        "coach_id": coach_id,
                        "usuario_id": usuario_id
                    }
                else:
                    # Si falla, desactivar el usuario creado
                    self.user_controller.desactivar_usuario(usuario_id, creado_por_id)
                    return {"success": False, "message": "Error al crear perfil de coach"}
                    
            except Exception as e:
                # Si algo falla, limpiar el usuario creado
                self.user_controller.desactivar_usuario(usuario_id, creado_por_id)
                return {"success": False, "message": f"Error en el registro: {str(e)}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def obtener_todos_coaches(self):
        """Obtiene todos los coaches con información del usuario"""
        try:
            coaches = self.coach_model.read_coaches()
            usuarios = self.usuario_model.read_usuarios()
            
            coaches_completos = []
            for coach in coaches:
                usuario = next((u for u in usuarios if u[0] == coach[1]), None)  # id_usuario
                if usuario and usuario[9]:  # usuario activo
                    coach_completo = {
                        'coach_data': coach,
                        'usuario_data': usuario,
                        'nombre_completo': f"{usuario[1]} {usuario[2]}",  # nombre + apellido
                        'email': usuario[6],
                        'especialidades': coach[2],
                        'salario': float(coach[5]) if coach[5] else 0,
                        'fecha_contratacion': coach[4]
                    }
                    coaches_completos.append(coach_completo)
            
            return {"success": True, "coaches": coaches_completos}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener coaches: {str(e)}"}
    
    def obtener_coach_por_id(self, coach_id):
        """Obtiene un coach específico por ID"""
        try:
            coaches = self.coach_model.read_coaches()
            for coach in coaches:
                if coach[0] == coach_id:  # id_coach en posición 0
                    return {"success": True, "coach": coach}
            return {"success": False, "message": "Coach no encontrado"}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener coach: {str(e)}"}
    
    def actualizar_perfil_coach(self, coach_id, datos_coach, actualizado_por_id):
        """Actualiza el perfil profesional del coach"""
        try:
            if not self._puede_gestionar_coaches(actualizado_por_id):
                return {"success": False, "message": "No tienes permisos para actualizar coaches"}
            
            # Verificar que el coach existe
            coach_actual = self.obtener_coach_por_id(coach_id)
            if not coach_actual["success"]:
                return {"success": False, "message": "Coach no encontrado"}
            
            coach_data = coach_actual["coach"]
            
            # Validar salario si se proporciona
            if 'salario' in datos_coach and datos_coach['salario']:
                try:
                    salario = float(datos_coach['salario'])
                    if salario < 0:
                        return {"success": False, "message": "El salario no puede ser negativo"}
                except (ValueError, TypeError):
                    return {"success": False, "message": "Salario inválido"}
            
            # Actualizar coach
            resultado = self.coach_model.update_coach(
                id_coach=coach_id,
                id_usuario=coach_data[1],  # Mantener id_usuario
                especialidades=datos_coach.get('especialidades', coach_data[2]),
                horario_disponible=datos_coach.get('horario_disponible', coach_data[3]),
                fecha_contratacion=datos_coach.get('fecha_contratacion', coach_data[4]),
                salario=datos_coach.get('salario', coach_data[5])
            )
            
            if resultado:
                return {"success": True, "message": "Perfil de coach actualizado exitosamente"}
            else:
                return {"success": False, "message": "Error al actualizar el perfil"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def obtener_coaches_disponibles(self, especialidad_requerida=None):
        """Obtiene coaches disponibles para asignación"""
        try:
            coaches_result = self.obtener_todos_coaches()
            if not coaches_result["success"]:
                return coaches_result
            
            coaches_disponibles = []
            for coach in coaches_result["coaches"]:
                # Filtrar por especialidad si se especifica
                if especialidad_requerida:
                    especialidades = coach['especialidades'].lower()
                    if especialidad_requerida.lower() not in especialidades:
                        continue
                
                # Contar atletas actualmente asignados
                atletas_asignados = self.contar_atletas_asignados(coach['coach_data'][0])
                
                coach_disponible = coach.copy()
                coach_disponible['atletas_asignados'] = atletas_asignados
                coaches_disponibles.append(coach_disponible)
            
            return {"success": True, "coaches": coaches_disponibles}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener coaches disponibles: {str(e)}"}
    
    # ==================== GESTIÓN DE ASIGNACIONES ====================
    
    def asignar_atleta_a_coach(self, coach_id, atleta_id, asignado_por_id, notas=""):
        """Asigna un atleta a un coach"""
        try:
            if not self._puede_gestionar_asignaciones(asignado_por_id):
                return {"success": False, "message": "No tienes permisos para gestionar asignaciones"}
            
            # Verificar que el coach existe
            coach = self.obtener_coach_por_id(coach_id)
            if not coach["success"]:
                return {"success": False, "message": "Coach no encontrado"}
            
            # Verificar que el atleta existe
            if not self._atleta_existe(atleta_id):
                return {"success": False, "message": "Atleta no encontrado"}
            
            # Verificar si el atleta ya tiene asignación activa
            asignacion_activa = self._obtener_asignacion_activa_atleta(atleta_id)
            if asignacion_activa:
                return {"success": False, "message": "El atleta ya tiene un coach asignado actualmente"}
            
            # Crear nueva asignación
            fecha_asignacion = datetime.now().date()
            asignacion_id = self.asignacion_model.insert_asignacion(
                id_coach=coach_id,
                id_atleta=atleta_id,
                fecha_asignacion=fecha_asignacion,
                fecha_fin=None,
                estado_activo=True,
                notas=notas
            )
            
            if asignacion_id:
                # Actualizar el atleta con el coach asignado (si el modelo lo permite)
                # Esto mantiene consistencia con la tabla atletas
                try:
                    self._actualizar_coach_en_atleta(atleta_id, coach_id)
                except Exception:
                    pass  # No es crítico si falla
                
                return {
                    "success": True,
                    "message": "Atleta asignado al coach exitosamente",
                    "asignacion_id": asignacion_id
                }
            else:
                return {"success": False, "message": "Error al crear la asignación"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def finalizar_asignacion(self, asignacion_id, finalizado_por_id, motivo=""):
        """Finaliza una asignación coach-atleta"""
        try:
            if not self._puede_gestionar_asignaciones(finalizado_por_id):
                return {"success": False, "message": "No tienes permisos para finalizar asignaciones"}
            
            # Obtener la asignación
            asignacion = self._obtener_asignacion_por_id(asignacion_id)
            if not asignacion:
                return {"success": False, "message": "Asignación no encontrada"}
            
            # Verificar que esté activa
            if not asignacion[5]:  # estado_activo en posición 5
                return {"success": False, "message": "La asignación ya está finalizada"}
            
            # Finalizar asignación
            fecha_fin = datetime.now().date()
            notas_actualizadas = f"{asignacion[6] or ''}\n[{fecha_fin}] Finalizada: {motivo}".strip()
            
            resultado = self.asignacion_model.update_asignacion(
                id_asignacion=asignacion_id,
                id_coach=asignacion[1],
                id_atleta=asignacion[2],
                fecha_asignacion=asignacion[3],
                fecha_fin=fecha_fin,
                estado_activo=False,
                notas=notas_actualizadas
            )
            
            if resultado:
                # Remover coach del atleta
                try:
                    self._actualizar_coach_en_atleta(asignacion[2], None)
                except Exception:
                    pass
                
                return {"success": True, "message": "Asignación finalizada exitosamente"}
            else:
                return {"success": False, "message": "Error al finalizar la asignación"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def reasignar_atleta(self, atleta_id, nuevo_coach_id, reasignado_por_id, motivo=""):
        """Reasigna un atleta a un nuevo coach"""
        try:
            # Finalizar asignación actual
            asignacion_actual = self._obtener_asignacion_activa_atleta(atleta_id)
            if asignacion_actual:
                self.finalizar_asignacion(
                    asignacion_actual[0], 
                    reasignado_por_id, 
                    f"Reasignación: {motivo}"
                )
            
            # Crear nueva asignación
            return self.asignar_atleta_a_coach(
                nuevo_coach_id, 
                atleta_id, 
                reasignado_por_id, 
                f"Reasignado desde otro coach. {motivo}"
            )
            
        except Exception as e:
            return {"success": False, "message": f"Error en reasignación: {str(e)}"}
    
    def obtener_atletas_por_coach(self, coach_id, solo_activos=True):
        """Obtiene atletas asignados a un coach específico"""
        try:
            asignaciones = self.asignacion_model.read_asignaciones()
            atletas = self.atleta_model.read_atletas()
            usuarios = self.usuario_model.read_usuarios()
            
            # Filtrar asignaciones del coach
            asignaciones_coach = []
            for asignacion in asignaciones:
                if asignacion[1] == coach_id:  # id_coach
                    if not solo_activos or asignacion[5]:  # estado_activo
                        asignaciones_coach.append(asignacion)
            
            # Obtener información completa de atletas
            atletas_del_coach = []
            for asignacion in asignaciones_coach:
                atleta_id = asignacion[2]  # id_atleta
                
                # Buscar datos del atleta
                atleta = next((a for a in atletas if a[0] == atleta_id), None)
                if atleta:
                    # Buscar datos del usuario
                    usuario = next((u for u in usuarios if u[0] == atleta[1]), None)
                    if usuario:
                        atleta_info = {
                            'asignacion_data': asignacion,
                            'atleta_data': atleta,
                            'usuario_data': usuario,
                            'nombre_completo': f"{usuario[1]} {usuario[2]}",
                            'email': usuario[6],
                            'fecha_asignacion': asignacion[3],
                            'fecha_fin': asignacion[4],
                            'estado_activo': asignacion[5],
                            'notas': asignacion[6]
                        }
                        atletas_del_coach.append(atleta_info)
            
            return {"success": True, "atletas": atletas_del_coach}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener atletas del coach: {str(e)}"}
    
    def obtener_historial_asignaciones_atleta(self, atleta_id):
        """Obtiene el historial completo de asignaciones de un atleta"""
        try:
            asignaciones = self.asignacion_model.read_asignaciones()
            coaches = self.coach_model.read_coaches()
            usuarios = self.usuario_model.read_usuarios()
            
            # Filtrar asignaciones del atleta
            historial = []
            for asignacion in asignaciones:
                if asignacion[2] == atleta_id:  # id_atleta
                    # Obtener información del coach
                    coach = next((c for c in coaches if c[0] == asignacion[1]), None)
                    if coach:
                        usuario_coach = next((u for u in usuarios if u[0] == coach[1]), None)
                        if usuario_coach:
                            registro = {
                                'asignacion_id': asignacion[0],
                                'coach_nombre': f"{usuario_coach[1]} {usuario_coach[2]}",
                                'especialidades': coach[2],
                                'fecha_asignacion': asignacion[3],
                                'fecha_fin': asignacion[4],
                                'estado_activo': asignacion[5],
                                'notas': asignacion[6],
                                'duracion_dias': self._calcular_duracion_asignacion(asignacion)
                            }
                            historial.append(registro)
            
            # Ordenar por fecha de asignación
            historial.sort(key=lambda x: x['fecha_asignacion'], reverse=True)
            
            return {"success": True, "historial": historial}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener historial: {str(e)}"}
    
    # ==================== REPORTES Y ESTADÍSTICAS ====================
    
    def generar_reporte_coach(self, coach_id):
        """Genera un reporte completo de un coach"""
        try:
            # Información básica del coach
            coach_info = self.obtener_coach_por_id(coach_id)
            if not coach_info["success"]:
                return coach_info
            
            # Obtener datos del usuario
            usuarios = self.usuario_model.read_usuarios()
            coach_data = coach_info["coach"]
            usuario_coach = next((u for u in usuarios if u[0] == coach_data[1]), None)
            
            if not usuario_coach:
                return {"success": False, "message": "Datos del usuario no encontrados"}
            
            # Atletas asignados actualmente
            atletas_activos = self.obtener_atletas_por_coach(coach_id, solo_activos=True)
            
            # Historial total de asignaciones
            asignaciones_totales = self.obtener_atletas_por_coach(coach_id, solo_activos=False)
            
            # Estadísticas
            total_atletas_historico = len(asignaciones_totales["atletas"]) if asignaciones_totales["success"] else 0
            atletas_actuales = len(atletas_activos["atletas"]) if atletas_activos["success"] else 0
            
            # Tiempo promedio de asignaciones
            tiempo_promedio = self._calcular_tiempo_promedio_asignaciones(coach_id)
            
            reporte = {
                "coach_info": {
                    "id": coach_id,
                    "nombre": f"{usuario_coach[1]} {usuario_coach[2]}",
                    "email": usuario_coach[6],
                    "especialidades": coach_data[2],
                    "horario_disponible": coach_data[3],
                    "fecha_contratacion": coach_data[4],
                    "salario": float(coach_data[5]) if coach_data[5] else 0
                },
                "estadisticas": {
                    "atletas_actuales": atletas_actuales,
                    "total_atletas_historico": total_atletas_historico,
                    "tiempo_promedio_asignacion_dias": tiempo_promedio
                },
                "atletas_actuales": atletas_activos["atletas"] if atletas_activos["success"] else [],
                "historial_completo": asignaciones_totales["atletas"] if asignaciones_totales["success"] else []
            }
            
            return {"success": True, "reporte": reporte}
        except Exception as e:
            return {"success": False, "message": f"Error generando reporte: {str(e)}"}
    
    def obtener_resumen_coaches(self):
        """Obtiene resumen estadístico de todos los coaches"""
        try:
            coaches_result = self.obtener_todos_coaches()
            if not coaches_result["success"]:
                return coaches_result
            
            coaches = coaches_result["coaches"]
            resumen = {
                "total_coaches": len(coaches),
                "coaches_con_atletas": 0,
                "total_atletas_asignados": 0,
                "salario_promedio": 0,
                "coaches_por_especialidad": {}
            }
            
            salarios_totales = 0
            coaches_con_salario = 0
            
            for coach in coaches:
                coach_id = coach['coach_data'][0]
                
                # Contar atletas asignados
                atletas_asignados = self.contar_atletas_asignados(coach_id)
                if atletas_asignados > 0:
                    resumen["coaches_con_atletas"] += 1
                resumen["total_atletas_asignados"] += atletas_asignados
                
                # Calcular salario promedio
                if coach['salario'] > 0:
                    salarios_totales += coach['salario']
                    coaches_con_salario += 1
                
                # Agrupar por especialidades
                especialidades = coach['especialidades']
                if especialidades:
                    for esp in especialidades.split(','):
                        esp = esp.strip()
                        if esp:
                            resumen["coaches_por_especialidad"][esp] = resumen["coaches_por_especialidad"].get(esp, 0) + 1
            
            # Calcular promedio salarial
            if coaches_con_salario > 0:
                resumen["salario_promedio"] = round(salarios_totales / coaches_con_salario, 2)
            
            return {"success": True, "resumen": resumen}
        except Exception as e:
            return {"success": False, "message": f"Error generando resumen: {str(e)}"}
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def contar_atletas_asignados(self, coach_id):
        """Cuenta cuántos atletas tiene asignados un coach"""
        try:
            print(f"🔍 DEBUG: Buscando atletas para coach_id: {coach_id} (tipo: {type(coach_id)})")
            
            # Obtener todos los atletas
            resultado = self.atleta_controller.obtener_todos_atletas()
            print(f"🔍 DEBUG: Resultado obtener_todos_atletas: {resultado['success']}")
            
            if not resultado["success"]:
                return 0
            
            print(f"🔍 DEBUG: Total atletas encontrados: {len(resultado['atletas'])}")
            
            # Contar atletas con este coach
            contador = 0
            for i, atleta_completo in enumerate(resultado["atletas"]):
                atleta_data = atleta_completo['atleta_data']
                print(f"🔍 DEBUG: Atleta {i}: {atleta_data}")
                
                coach_atleta_id = atleta_data[8] if len(atleta_data) > 8 else None
                print(f"🔍 DEBUG: coach_atleta_id: {coach_atleta_id} (tipo: {type(coach_atleta_id)})")
                
                if coach_atleta_id == coach_id:
                    print(f"✅ MATCH: Atleta {i} pertenece al coach {coach_id}")
                    contador += 1
                else:
                    print(f"❌ NO MATCH: {coach_atleta_id} != {coach_id}")
            
            print(f"🔍 DEBUG: Contador final: {contador}")
            return contador
            
        except Exception as e:
            print(f"Error contando atletas: {e}")
            return 0
    
    def _puede_crear_coaches(self, user_id):
        """Verifica si el usuario puede crear coaches (solo secretarias)"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == user_id:
                    return usuario[8] == 'secretaria'  # rol en posición 8
            return False
        except Exception:
            return False
    
    def _puede_gestionar_coaches(self, user_id):
        """Verifica si el usuario puede gestionar coaches (admin y secretarias)"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == user_id:
                    rol = usuario[8]
                    return rol in ['admin_principal', 'secretaria']
            return False
        except Exception:
            return False
    
    def _puede_gestionar_asignaciones(self, user_id):
        """Verifica si el usuario puede gestionar asignaciones"""
        return self._puede_gestionar_coaches(user_id)
    
    def _validar_datos_coach(self, datos_usuario, datos_coach):
        """Valida los datos para crear un coach"""
        # Validar datos básicos de usuario
        campos_requeridos = ['nombre', 'apellido', 'email', 'contraseña']
        for campo in campos_requeridos:
            if not datos_usuario.get(campo):
                return False
        
        # Validar salario si se proporciona
        if 'salario' in datos_coach and datos_coach['salario']:
            try:
                salario = float(datos_coach['salario'])
                if salario < 0:
                    return False
            except (ValueError, TypeError):
                return False
        
        return True
    
    def _atleta_existe(self, atleta_id):
        """Verifica si un atleta existe"""
        try:
            atletas = self.atleta_model.read_atletas()
            return any(atleta[0] == atleta_id for atleta in atletas)
        except Exception:
            return False
    
    def _obtener_asignacion_por_id(self, asignacion_id):
        """Obtiene una asignación por ID"""
        try:
            asignaciones = self.asignacion_model.read_asignaciones()
            return next((a for a in asignaciones if a[0] == asignacion_id), None)
        except Exception:
            return None
    
    def _obtener_asignacion_activa_atleta(self, atleta_id):
        """Obtiene la asignación activa de un atleta"""
        try:
            asignaciones = self.asignacion_model.read_asignaciones()
            for asignacion in asignaciones:
                if asignacion[2] == atleta_id and asignacion[5]:  # id_atleta y estado_activo
                    return asignacion
            return None
        except Exception:
            return None
    
    def _actualizar_coach_en_atleta(self, atleta_id, coach_id):
        """Actualiza el coach asignado en la tabla atletas"""
        try:
            # Este método requeriría modificar el atleta_model para incluir solo el campo coach
            # Por simplicidad, no se implementa completamente aquí
            pass
        except Exception:
            pass
    
    def _calcular_duracion_asignacion(self, asignacion):
        """Calcula la duración de una asignación en días"""
        try:
            fecha_inicio = asignacion[3]  # fecha_asignacion
            fecha_fin = asignacion[4] or datetime.now().date()  # fecha_fin o hoy
            
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            return (fecha_fin - fecha_inicio).days
        except Exception:
            return 0
    
    def _calcular_tiempo_promedio_asignaciones(self, coach_id):
        """Calcula el tiempo promedio de asignaciones finalizadas de un coach"""
        try:
            asignaciones = self.asignacion_model.read_asignaciones()
            duraciones = []
            
            for asignacion in asignaciones:
                if asignacion[1] == coach_id and asignacion[4]:  # id_coach y fecha_fin
                    duracion = self._calcular_duracion_asignacion(asignacion)
                    if duracion > 0:
                        duraciones.append(duracion)
            
            if duraciones:
                return round(sum(duraciones) / len(duraciones), 1)
            return 0
        except Exception:
            return 0