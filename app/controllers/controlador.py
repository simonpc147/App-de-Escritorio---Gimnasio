# app/controllers/controlador.py

from app.models.modelo import Modelo

class Controlador:
    """
    Controlador principal que maneja la lógica de negocio entre las vistas y el modelo de datos.
    Implementa el patrón MVC para la aplicación de gimnasio.
    """
    
    def __init__(self):
        """Inicializa el controlador con una instancia del modelo."""
        self.modelo = Modelo()
    
    # ======== MÉTODOS PARA USUARIOS DEL GIMNASIO ========
    
    def obtener_usuarios(self):
        """Obtiene la lista de todos los usuarios registrados en el gimnasio."""
        try:
            return self.modelo.SelectAll_usuarios()
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []
    
    def registrar_usuario(self, id_usuario, nombre, email, telefono, fecha_registro):
        """Registra un nuevo usuario en el sistema."""
        try:
            return self.modelo.Insert_usuario(id_usuario, nombre, email, telefono, fecha_registro)
        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            return f"Error: {e}"
    
    def buscar_usuario_por_id(self, id_usuario):
        """Busca un usuario por su ID."""
        try:
            # Asumiendo que tienes un método similar en el modelo
            return self.modelo.Select_cliente(id_usuario)  # Ajusta este método según tu modelo
        except Exception as e:
            print(f"Error al buscar usuario: {e}")
            return None
    
    # ======== MÉTODOS PARA EJERCICIOS ========
    
    def obtener_ejercicios(self):
        """Obtiene la lista de todos los ejercicios disponibles."""
        try:
            return self.modelo.SelectAll_ejercicios()
        except Exception as e:
            print(f"Error al obtener ejercicios: {e}")
            return []
    
    def registrar_ejercicio(self, id_ejercicio, nombre, descripcion, grupo_muscular):
        """Registra un nuevo ejercicio en el sistema."""
        try:
            return self.modelo.Insert_ejercicio(id_ejercicio, nombre, descripcion, grupo_muscular)
        except Exception as e:
            print(f"Error al registrar ejercicio: {e}")
            return f"Error: {e}"
    
    def buscar_ejercicio_por_id(self, id_ejercicio):
        """Busca un ejercicio por su ID."""
        try:
            # Asumiendo que tienes un método similar al Select_articulo
            return self.modelo.Select_articulo(id_ejercicio)  # Ajusta este método según tu modelo
        except Exception as e:
            print(f"Error al buscar ejercicio: {e}")
            return None
    
    def buscar_ejercicios_por_grupo_muscular(self, grupo_muscular):
        """Busca ejercicios por grupo muscular."""
        try:
            # Implementa este método en el modelo si es necesario
            sql = "SELECT * FROM ejercicios WHERE grupo_muscular = %s"
            params = (grupo_muscular,)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al buscar ejercicios por grupo muscular: {e}")
            return []
    
    # ======== MÉTODOS PARA RUTINAS ========
    
    def obtener_rutinas(self):
        """Obtiene la lista de todas las rutinas disponibles."""
        try:
            return self.modelo.SelectAll_rutinas()
        except Exception as e:
            print(f"Error al obtener rutinas: {e}")
            return []
    
    def registrar_rutina(self, id_rutina, nombre, descripcion, nivel_dificultad):
        """Registra una nueva rutina en el sistema."""
        try:
            return self.modelo.Insert_rutina(id_rutina, nombre, descripcion, nivel_dificultad)
        except Exception as e:
            print(f"Error al registrar rutina: {e}")
            return f"Error: {e}"
    
    def asignar_rutina_a_usuario(self, id_usuario, id_rutina, fecha_asignacion, fecha_fin):
        """Asigna una rutina a un usuario específico."""
        try:
            return self.modelo.Asignar_rutina(id_usuario, id_rutina, fecha_asignacion, fecha_fin)
        except Exception as e:
            print(f"Error al asignar rutina: {e}")
            return f"Error: {e}"
    
    def obtener_rutinas_de_usuario(self, id_usuario):
        """Obtiene todas las rutinas asignadas a un usuario específico."""
        try:
            sql = """
            SELECT r.* FROM rutinas r 
            JOIN usuario_rutina ur ON r.id_rutina = ur.id_rutina 
            WHERE ur.id_usuario = %s
            """
            params = (id_usuario,)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al obtener rutinas del usuario: {e}")
            return []
    
    # ======== MÉTODOS PARA ASISTENCIA ========
    
    def registrar_asistencia(self, id_usuario, fecha, hora_entrada):
        """Registra la asistencia de un usuario al gimnasio."""
        try:
            sql = "INSERT INTO asistencia (id_usuario, fecha, hora_entrada) VALUES (%s, %s, %s)"
            params = (id_usuario, fecha, hora_entrada)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al registrar asistencia: {e}")
            return f"Error: {e}"
    
    def registrar_salida(self, id_usuario, fecha, hora_salida):
        """Registra la salida de un usuario del gimnasio."""
        try:
            sql = """
            UPDATE asistencia 
            SET hora_salida = %s 
            WHERE id_usuario = %s AND fecha = %s AND hora_salida IS NULL
            """
            params = (hora_salida, id_usuario, fecha)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al registrar salida: {e}")
            return f"Error: {e}"
    
    def obtener_asistencias_por_fecha(self, fecha):
        """Obtiene todas las asistencias registradas en una fecha específica."""
        try:
            sql = """
            SELECT a.*, u.nombre 
            FROM asistencia a 
            JOIN usuarios u ON a.id_usuario = u.id_usuario 
            WHERE a.fecha = %s
            """
            params = (fecha,)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al obtener asistencias: {e}")
            return []
    
    # ======== MÉTODOS PARA PAGOS ========
    
    def registrar_pago(self, id_usuario, monto, fecha_pago, concepto, metodo_pago):
        """Registra un pago realizado por un usuario."""
        try:
            sql = """
            INSERT INTO pagos (id_usuario, monto, fecha_pago, concepto, metodo_pago)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (id_usuario, monto, fecha_pago, concepto, metodo_pago)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al registrar pago: {e}")
            return f"Error: {e}"
    
    def obtener_pagos_por_usuario(self, id_usuario):
        """Obtiene todos los pagos realizados por un usuario específico."""
        try:
            sql = "SELECT * FROM pagos WHERE id_usuario = %s ORDER BY fecha_pago DESC"
            params = (id_usuario,)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al obtener pagos: {e}")
            return []
    
    # ======== MÉTODOS PARA ESTADÍSTICAS ========
    
    def obtener_estadisticas_asistencia(self, fecha_inicio, fecha_fin):
        """Obtiene estadísticas de asistencia en un rango de fechas."""
        try:
            sql = """
            SELECT DATE(fecha) as dia, COUNT(*) as total_asistencias
            FROM asistencia
            WHERE fecha BETWEEN %s AND %s
            GROUP BY DATE(fecha)
            ORDER BY DATE(fecha)
            """
            params = (fecha_inicio, fecha_fin)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return []
    
    def obtener_estadisticas_pagos(self, mes, año):
        """Obtiene estadísticas de pagos para un mes y año específicos."""
        try:
            sql = """
            SELECT concepto, SUM(monto) as total
            FROM pagos
            WHERE MONTH(fecha_pago) = %s AND YEAR(fecha_pago) = %s
            GROUP BY concepto
            """
            params = (mes, año)
            return self.modelo.ejecutar_consulta(sql, params)
        except Exception as e:
            print(f"Error al obtener estadísticas de pagos: {e}")
            return []