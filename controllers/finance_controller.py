# Controlador para gestión financiera completa (planes, ingresos, egresos)
from models.plan_model import PlanModel
from models.ingreso_model import IngresoModel
from models.egreso_model import EgresoModel
from models.usuario_model import UsuarioModel
from decimal import Decimal
from datetime import datetime, timedelta


class FinanceController:
    def __init__(self):
        self.plan_model = PlanModel()
        self.ingreso_model = IngresoModel()
        self.egreso_model = EgresoModel()
        self.usuario_model = UsuarioModel()
    
    # ==================== GESTIÓN DE PLANES ====================
    
    def crear_plan(self, datos_plan, creado_por_id):
        """Crea un nuevo plan de membresía"""
        try:
            if not self._tiene_permisos_financieros(creado_por_id):
                return {"success": False, "message": "No tienes permisos para crear planes"}
            
            if not self._validar_datos_plan(datos_plan):
                return {"success": False, "message": "Datos del plan incompletos o inválidos"}
            
            if self._nombre_plan_existe(datos_plan['nombre_plan']):
                return {"success": False, "message": "Ya existe un plan con ese nombre"}
            
            plan_id = self.plan_model.insert_plan(
                datos_plan['nombre_plan'],
                datos_plan.get('descripcion', ''),
                datos_plan['precio'],
                datos_plan.get('duracion_dias', 30),
                datos_plan.get('estado_activo', True)
            )
            
            if plan_id:
                return {"success": True, "message": "Plan creado exitosamente", "plan_id": plan_id}
            else:
                return {"success": False, "message": "Error al crear el plan"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def obtener_planes_activos(self):
        """Obtiene solo los planes activos"""
        try:
            planes = self.plan_model.read_planes()
            planes_activos = [p for p in planes if p[5]]  # estado_activo en posición 5
            return {"success": True, "planes": planes_activos}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener planes activos: {str(e)}"}
    
    def obtener_plan_por_id(self, plan_id):
        """Obtiene un plan específico por ID"""
        try:
            planes = self.plan_model.read_planes()
            for plan in planes:
                if plan[0] == plan_id:
                    return {"success": True, "plan": plan}
            return {"success": False, "message": "Plan no encontrado"}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener plan: {str(e)}"}
    
    # ==================== GESTIÓN DE INGRESOS ====================
    
    def procesar_pago_inscripcion(self, id_atleta, id_plan, metodo_pago, procesado_por_id, descripcion=""):
        """
        Procesa el pago inicial de inscripción de un atleta
        Se llama automáticamente cuando se registra un atleta
        """
        try:
            if not self._tiene_permisos_financieros(procesado_por_id):
                return {"success": False, "message": "No tienes permisos para procesar pagos"}
            
            plan_result = self.obtener_plan_por_id(id_plan)
            if not plan_result["success"]:
                return {"success": False, "message": "Plan no encontrado"}
            
            plan = plan_result["plan"]
            monto = float(plan[3])  # precio del plan
            
            fecha_pago = datetime.now().date()
            fecha_vencimiento_nueva = self.calcular_fecha_vencimiento(id_plan, fecha_pago)
            
            ingreso_id = self.ingreso_model.insert_ingreso(
                id_atleta=id_atleta,
                id_plan=id_plan,
                monto=monto,
                tipo_pago='inscripcion',
                metodo_pago=metodo_pago,
                descripcion=descripcion if descripcion else 'Pago de inscripción inicial',
                fecha_pago=fecha_pago,
                fecha_vencimiento_anterior=None,
                fecha_vencimiento_nueva=fecha_vencimiento_nueva,
                procesado_por=procesado_por_id
            )
            
            if ingreso_id:
                return {
                    "success": True,
                    "message": "Pago de inscripción procesado exitosamente",
                    "ingreso_id": ingreso_id,
                    "fecha_vencimiento": fecha_vencimiento_nueva,
                    "monto": monto
                }
            else:
                return {"success": False, "message": "Error al procesar el pago"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def procesar_renovacion_membresia(self, id_atleta, id_plan, metodo_pago, procesado_por_id, fecha_vencimiento_actual, descripcion=""):
        """Procesa la renovación de membresía de un atleta"""
        try:
            if not self._tiene_permisos_financieros(procesado_por_id):
                return {"success": False, "message": "No tienes permisos para procesar pagos"}
            
            plan_result = self.obtener_plan_por_id(id_plan)
            if not plan_result["success"]:
                return {"success": False, "message": "Plan no encontrado"}
            
            plan = plan_result["plan"]
            monto = float(plan[3])
            fecha_pago = datetime.now().date()
            
            # Si ya venció, renovar desde hoy; si no, desde la fecha de vencimiento actual
            if fecha_vencimiento_actual < fecha_pago:
                fecha_base = fecha_pago
            else:
                fecha_base = fecha_vencimiento_actual
            
            fecha_vencimiento_nueva = self.calcular_fecha_vencimiento(id_plan, fecha_base)
            
            ingreso_id = self.ingreso_model.insert_ingreso(
                id_atleta=id_atleta,
                id_plan=id_plan,
                monto=monto,
                tipo_pago='renovacion',
                metodo_pago=metodo_pago,
                descripcion=descripcion if descripcion else 'Renovación de membresía',
                fecha_pago=fecha_pago,
                fecha_vencimiento_anterior=fecha_vencimiento_actual,
                fecha_vencimiento_nueva=fecha_vencimiento_nueva,
                procesado_por=procesado_por_id
            )
            
            if ingreso_id:
                return {
                    "success": True,
                    "message": "Renovación procesada exitosamente",
                    "ingreso_id": ingreso_id,
                    "fecha_vencimiento_nueva": fecha_vencimiento_nueva,
                    "monto": monto
                }
            else:
                return {"success": False, "message": "Error al procesar la renovación"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def registrar_servicio_extra(self, id_atleta, monto, metodo_pago, descripcion, procesado_por_id):
        """Registra un pago por servicio extra (no afecta la membresía)"""
        try:
            if not self._tiene_permisos_financieros(procesado_por_id):
                return {"success": False, "message": "No tienes permisos para registrar pagos"}
            
            if not descripcion or descripcion.strip() == "":
                return {"success": False, "message": "La descripción es requerida para servicios extra"}
            
            try:
                monto_float = float(monto)
                if monto_float <= 0:
                    return {"success": False, "message": "El monto debe ser mayor a 0"}
            except (ValueError, TypeError):
                return {"success": False, "message": "Monto inválido"}
            
            fecha_pago = datetime.now().date()
            
            ingreso_id = self.ingreso_model.insert_ingreso(
                id_atleta=id_atleta,
                id_plan=None,  # No está asociado a un plan
                monto=monto_float,
                tipo_pago='servicio_extra',
                metodo_pago=metodo_pago,
                descripcion=descripcion,
                fecha_pago=fecha_pago,
                fecha_vencimiento_anterior=None,
                fecha_vencimiento_nueva=None,
                procesado_por=procesado_por_id
            )
            
            if ingreso_id:
                return {
                    "success": True,
                    "message": "Servicio extra registrado exitosamente",
                    "ingreso_id": ingreso_id,
                    "monto": monto_float
                }
            else:
                return {"success": False, "message": "Error al registrar el servicio extra"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def obtener_ingresos_por_atleta(self, id_atleta):
        """Obtiene todos los ingresos de un atleta específico"""
        try:
            ingresos = self.ingreso_model.read_ingresos()
            ingresos_atleta = [i for i in ingresos if i[1] == id_atleta]  # id_atleta en posición 1
            return {"success": True, "ingresos": ingresos_atleta}
        except Exception as e:
            return {"success": False, "message": f"Error al obtener ingresos: {str(e)}"}
    
    def obtener_ingresos_por_fecha(self, fecha_inicio, fecha_fin):
        """Obtiene ingresos en un rango de fechas"""
        try:
            ingresos = self.ingreso_model.read_ingresos()
            ingresos_filtrados = []
            
            for ingreso in ingresos:
                fecha_pago = ingreso[7]  # fecha_pago en posición 7
                if fecha_inicio <= fecha_pago <= fecha_fin:
                    ingresos_filtrados.append(ingreso)
            
            return {"success": True, "ingresos": ingresos_filtrados}
        except Exception as e:
            return {"success": False, "message": f"Error al filtrar ingresos: {str(e)}"}
    
    # ==================== GESTIÓN DE EGRESOS ====================
    
    def registrar_egreso(self, datos_egreso, registrado_por_id):
        """Registra un nuevo egreso"""
        try:
            if not self._tiene_permisos_financieros(registrado_por_id):
                return {"success": False, "message": "No tienes permisos para registrar egresos"}
            
            if not self._validar_datos_egreso(datos_egreso):
                return {"success": False, "message": "Datos del egreso incompletos o inválidos"}
            
            fecha_egreso = datos_egreso.get('fecha_egreso', datetime.now().date())
            
            egreso_id = self.egreso_model.insert_egreso(
                monto=datos_egreso['monto'],
                tipo_egreso=datos_egreso['tipo_egreso'],
                descripcion=datos_egreso['descripcion'],
                beneficiario=datos_egreso.get('beneficiario', ''),
                metodo_pago=datos_egreso['metodo_pago'],
                fecha_egreso=fecha_egreso,
                registrado_por=registrado_por_id,
                comprobante=datos_egreso.get('comprobante', '')
            )
            
            if egreso_id:
                return {
                    "success": True,
                    "message": "Egreso registrado exitosamente",
                    "egreso_id": egreso_id
                }
            else:
                return {"success": False, "message": "Error al registrar el egreso"}
                
        except Exception as e:
            return {"success": False, "message": f"Error interno: {str(e)}"}
    
    def obtener_egresos_por_tipo(self, tipo_egreso):
        """Obtiene egresos filtrados por tipo"""
        try:
            egresos = self.egreso_model.read_egresos()
            egresos_filtrados = [e for e in egresos if e[2] == tipo_egreso]  # tipo_egreso en posición 2
            return {"success": True, "egresos": egresos_filtrados}
        except Exception as e:
            return {"success": False, "message": f"Error al filtrar egresos: {str(e)}"}
    
    def obtener_egresos_por_fecha(self, fecha_inicio, fecha_fin):
        """Obtiene egresos en un rango de fechas"""
        try:
            egresos = self.egreso_model.read_egresos()
            egresos_filtrados = []
            
            for egreso in egresos:
                fecha_egreso = egreso[6]  # fecha_egreso en posición 6
                if fecha_inicio <= fecha_egreso <= fecha_fin:
                    egresos_filtrados.append(egreso)
            
            return {"success": True, "egresos": egresos_filtrados}
        except Exception as e:
            return {"success": False, "message": f"Error al filtrar egresos: {str(e)}"}
    
    # ==================== REPORTES FINANCIEROS ====================
    
    def generar_reporte_financiero(self, fecha_inicio, fecha_fin):
        """Genera un reporte financiero completo"""
        try:
            # Obtener ingresos del período
            ingresos_result = self.obtener_ingresos_por_fecha(fecha_inicio, fecha_fin)
            egresos_result = self.obtener_egresos_por_fecha(fecha_inicio, fecha_fin)
            
            if not ingresos_result["success"] or not egresos_result["success"]:
                return {"success": False, "message": "Error al obtener datos financieros"}
            
            ingresos = ingresos_result["ingresos"]
            egresos = egresos_result["egresos"]
            
            # Calcular totales
            total_ingresos = sum([float(i[3]) for i in ingresos])  # monto en posición 3
            total_egresos = sum([float(e[1]) for e in egresos])    # monto en posición 1
            balance = total_ingresos - total_egresos
            
            # Desglosar ingresos por tipo
            ingresos_por_tipo = {}
            for ingreso in ingresos:
                tipo = ingreso[4]  # tipo_pago en posición 4
                monto = float(ingreso[3])
                ingresos_por_tipo[tipo] = ingresos_por_tipo.get(tipo, 0) + monto
            
            # Desglosar egresos por tipo
            egresos_por_tipo = {}
            for egreso in egresos:
                tipo = egreso[2]  # tipo_egreso en posición 2
                monto = float(egreso[1])
                egresos_por_tipo[tipo] = egresos_por_tipo.get(tipo, 0) + monto
            
            return {
                "success": True,
                "reporte": {
                    "periodo": {
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin
                    },
                    "resumen": {
                        "total_ingresos": round(total_ingresos, 2),
                        "total_egresos": round(total_egresos, 2),
                        "balance": round(balance, 2),
                        "cantidad_ingresos": len(ingresos),
                        "cantidad_egresos": len(egresos)
                    },
                    "desglose_ingresos": {k: round(v, 2) for k, v in ingresos_por_tipo.items()},
                    "desglose_egresos": {k: round(v, 2) for k, v in egresos_por_tipo.items()}
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error al generar reporte: {str(e)}"}
    
    def obtener_resumen_mensual(self, año, mes):
        """Obtiene resumen financiero de un mes específico"""
        try:
            from calendar import monthrange
            
            # Calcular primer y último día del mes
            primer_dia = datetime(año, mes, 1).date()
            ultimo_dia = datetime(año, mes, monthrange(año, mes)[1]).date()
            
            return self.generar_reporte_financiero(primer_dia, ultimo_dia)
            
        except Exception as e:
            return {"success": False, "message": f"Error al obtener resumen mensual: {str(e)}"}
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def _tiene_permisos_financieros(self, user_id):
        """Verifica si el usuario tiene permisos para operaciones financieras"""
        try:
            usuarios = self.usuario_model.read_usuarios()
            for usuario in usuarios:
                if usuario[0] == user_id:
                    rol = usuario[8]
                    return rol in ['admin_principal', 'secretaria']
            return False
        except Exception:
            return False
    
    def _validar_datos_plan(self, datos):
        """Valida los datos del plan"""
        campos_requeridos = ['nombre_plan', 'precio']
        
        for campo in campos_requeridos:
            if not datos.get(campo):
                return False
        
        try:
            precio = float(datos['precio'])
            if precio <= 0:
                return False
        except (ValueError, TypeError):
            return False
        
        if 'duracion_dias' in datos:
            try:
                duracion = int(datos['duracion_dias'])
                if duracion <= 0:
                    return False
            except (ValueError, TypeError):
                return False
        
        return True
    
    def _validar_datos_egreso(self, datos):
        """Valida los datos del egreso"""
        campos_requeridos = ['monto', 'tipo_egreso', 'descripcion', 'metodo_pago']
        
        for campo in campos_requeridos:
            if not datos.get(campo):
                return False
        
        try:
            monto = float(datos['monto'])
            if monto <= 0:
                return False
        except (ValueError, TypeError):
            return False
        
        tipos_validos = ['salario_empleado', 'compra_equipos', 'mantenimiento', 'servicios', 'alquiler', 'otro']
        if datos['tipo_egreso'] not in tipos_validos:
            return False
        
        return True
    
    def _nombre_plan_existe(self, nombre_plan):
        """Verifica si ya existe un plan con ese nombre"""
        planes = self.plan_model.read_planes()
        for plan in planes:
            if plan[1].lower() == nombre_plan.lower():
                return True
        return False
    
    def calcular_fecha_vencimiento(self, plan_id, fecha_inicio=None):
        """Calcula la fecha de vencimiento basada en un plan"""
        try:
            if fecha_inicio is None:
                fecha_inicio = datetime.now().date()
            
            plan_result = self.obtener_plan_por_id(plan_id)
            if not plan_result["success"]:
                return None
            
            plan = plan_result["plan"]
            duracion_dias = plan[4]
            
            fecha_vencimiento = fecha_inicio + timedelta(days=duracion_dias)
            return fecha_vencimiento
            
        except Exception as e:
            print(f"Error al calcular fecha de vencimiento: {str(e)}")
            return None