# app/views/vista.py

from app.controllers.controlador import Controlador
from datetime import datetime

class Vista:
    """
    Clase Vista que maneja la interacción con el usuario y presenta la información.
    En un proyecto real con interfaz web, esta clase podría integrarse con Flask,
    Django o cualquier otro framework web.
    """
    
    def __init__(self):
        """Inicializa la vista con una instancia del controlador."""
        self.controlador = Controlador()
    
    # ======== MÉTODOS GENERALES ========
    
    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje al usuario."""
        print(mensaje)
    
    def solicitar_entrada(self, mensaje):
        """Solicita entrada de texto al usuario."""
        return input(f"{mensaje}: ")
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal de la aplicación."""
        print("\n===== SISTEMA DE GESTIÓN DE GIMNASIO =====")
        print("1. Gestión de Usuarios")
        print("2. Gestión de Ejercicios")
        print("3. Gestión de Rutinas")
        print("4. Control de Asistencia")
        print("5. Gestión de Pagos")
        print("6. Reportes y Estadísticas")
        print("0. Salir")
        return self.solicitar_entrada("Seleccione una opción")
    
    # ======== MÉTODOS PARA USUARIOS ========
    
    def mostrar_menu_usuarios(self):
        """Muestra el menú de gestión de usuarios."""
        print("\n===== GESTIÓN DE USUARIOS =====")
        print("1. Registrar nuevo usuario")
        print("2. Buscar usuario")
        print("3. Listar todos los usuarios")
        print("4. Modificar usuario")
        print("5. Eliminar usuario")
        print("0. Volver al menú principal")
        return self.solicitar_entrada("Seleccione una opción")
    
    def formulario_registro_usuario(self):
        """Muestra el formulario para registrar un nuevo usuario."""
        print("\n===== REGISTRO DE NUEVO USUARIO =====")
        id_usuario = self.solicitar_entrada("ID de Usuario")
        nombre = self.solicitar_entrada("Nombre completo")
        email = self.solicitar_entrada("Email")
        telefono = self.solicitar_entrada("Teléfono")
        fecha_registro = datetime.now().strftime("%Y-%m-%d")
        
        resultado = self.controlador.registrar_usuario(id_usuario, nombre, email, telefono, fecha_registro)
        
        if isinstance(resultado, int) and resultado > 0:
            self.mostrar_mensaje("Usuario registrado exitosamente.")
        else:
            self.mostrar_mensaje(f"Error al registrar usuario: {resultado}")
    
    def buscar_usuario(self):
        """Busca y muestra la información de un usuario."""
        id_usuario = self.solicitar_entrada("Ingrese el ID del usuario a buscar")
        usuario = self.controlador.buscar_usuario_por_id(id_usuario)
        
        if usuario:
            print("\n===== INFORMACIÓN DEL USUARIO =====")
            print(f"ID: {usuario[0]}")
            print(f"Nombre: {usuario[1]}")
            print(f"Email: {usuario[2]}")
            print(f"Teléfono: {usuario[3]}")
            print(f"Fecha de registro: {usuario[4]}")
        else:
            self.mostrar_mensaje("Usuario no encontrado.")
    
    def listar_usuarios(self):
        """Lista todos los usuarios registrados."""
        usuarios = self.controlador.obtener_usuarios()
        
        if usuarios:
            print("\n===== LISTA DE USUARIOS =====")
            print("ID\tNombre\t\tEmail\t\tTeléfono")
            print("--------------------------------------------------")
            for usuario in usuarios:
                print(f"{usuario[0]}\t{usuario[1]}\t{usuario[2]}\t{usuario[3]}")
        else:
            self.mostrar_mensaje("No hay usuarios registrados.")
    
    # ======== MÉTODOS PARA EJERCICIOS ========
    
    def mostrar_menu_ejercicios(self):
        """Muestra el menú de gestión de ejercicios."""
        print("\n===== GESTIÓN DE EJERCICIOS =====")
        print("1. Registrar nuevo ejercicio")
        print("2. Buscar ejercicio")
        print("3. Listar todos los ejercicios")
        print("4. Buscar por grupo muscular")
        print("0. Volver al menú principal")
        return self.solicitar_entrada("Seleccione una opción")
    
    def formulario_registro_ejercicio(self):
        """Muestra el formulario para registrar un nuevo ejercicio."""
        print("\n===== REGISTRO DE NUEVO EJERCICIO =====")
        id_ejercicio = self.solicitar_entrada("ID de Ejercicio")
        nombre = self.solicitar_entrada("Nombre del ejercicio")
        descripcion = self.solicitar_entrada("Descripción")
        grupo_muscular = self.solicitar_entrada("Grupo muscular")
        
        resultado = self.controlador.registrar_ejercicio(id_ejercicio, nombre, descripcion, grupo_muscular)
        
        if isinstance(resultado, int) and resultado > 0:
            self.mostrar_mensaje("Ejercicio registrado exitosamente.")
        else:
            self.mostrar_mensaje(f"Error al registrar ejercicio: {resultado}")
    
    def listar_ejercicios(self):
        """Lista todos los ejercicios registrados."""
        ejercicios = self.controlador.obtener_ejercicios()
        
        if ejercicios:
            print("\n===== LISTA DE EJERCICIOS =====")
            print("ID\tNombre\t\tGrupo Muscular")
            print("--------------------------------------------------")
            for ejercicio in ejercicios:
                print(f"{ejercicio[0]}\t{ejercicio[1]}\t{ejercicio[3]}")
        else:
            self.mostrar_mensaje("No hay ejercicios registrados.")
    
    # ======== MÉTODOS PARA RUTINAS ========
    
    def mostrar_menu_rutinas(self):
        """Muestra el menú de gestión de rutinas."""
        print("\n===== GESTIÓN DE RUTINAS =====")
        print("1. Crear nueva rutina")
        print("2. Asignar rutina a usuario")
        print("3. Listar rutinas")
        print("4. Ver rutinas de usuario")
        print("0. Volver al menú principal")
        return self.solicitar_entrada("Seleccione una opción")
    
    def formulario_crear_rutina(self):
        """Muestra el formulario para crear una nueva rutina."""
        print("\n===== CREACIÓN DE NUEVA RUTINA =====")
        id_rutina = self.solicitar_entrada("ID de Rutina")
        nombre = self.solicitar_entrada("Nombre de la rutina")
        descripcion = self.solicitar_entrada("Descripción")
        nivel_dificultad = self.solicitar_entrada("Nivel de dificultad (Principiante/Intermedio/Avanzado)")
        
        resultado = self.controlador.registrar_rutina(id_rutina, nombre, descripcion, nivel_dificultad)
        
        if isinstance(resultado, int) and resultado > 0:
            self.mostrar_mensaje("Rutina creada exitosamente.")
        else:
            self.mostrar_mensaje(f"Error al crear rutina: {resultado}")
    
    def formulario_asignar_rutina(self):
        """Muestra el formulario para asignar una rutina a un usuario."""
        print("\n===== ASIGNACIÓN DE RUTINA A USUARIO =====")
        
        # Primero mostramos los usuarios para seleccionar
        self.listar_usuarios()
        id_usuario = self.solicitar_entrada("ID del Usuario")
        
        # Luego mostramos las rutinas disponibles
        self.listar_rutinas()
        id_rutina = self.solicitar_entrada("ID de la Rutina")
        
        fecha_asignacion = datetime.now().strftime("%Y-%m-%d")
        fecha_fin = self.solicitar_entrada("Fecha de finalización (YYYY-MM-DD)")
        
        resultado = self.controlador.asignar_rutina_a_usuario(id_usuario, id_rutina, fecha_asignacion, fecha_fin)
        
        if isinstance(resultado, int) and resultado > 0:
            self.mostrar_mensaje("Rutina asignada exitosamente.")
        else:
            self.mostrar_mensaje(f"Error al asignar rutina: {resultado}")
    
    def listar_rutinas(self):
        """Lista todas las rutinas disponibles."""
        rutinas = self.controlador.obtener_rutinas()
        
        if rutinas:
            print("\n===== LISTA DE RUTINAS =====")
            print("ID\tNombre\t\tNivel de Dificultad")
            print("--------------------------------------------------")
            for rutina in rutinas:
                print(f"{rutina[0]}\t{rutina[1]}\t{rutina[3]}")
        else:
            self.mostrar_mensaje("No hay rutinas registradas.")
    
    # ======== MÉTODOS PARA ASISTENCIA ========
    
    def mostrar_menu_asistencia(self):
        """Muestra el menú de control de asistencia."""
        print("\n===== CONTROL DE ASISTENCIA =====")
        print("1. Registrar entrada")
        print("2. Registrar salida")
        print("3. Ver asistencias de hoy")
        print("0. Volver al menú principal")
        return self.solicitar_entrada("Seleccione una opción")
    
    def registrar_entrada_usuario(self):
        """Registra la entrada de un usuario al gimnasio."""
        print("\n===== REGISTRO DE ENTRADA =====")
        id_usuario = self.solicitar_entrada("ID del Usuario")
        fecha = datetime.now().strftime("%Y-%m-%d")
        hora_entrada = datetime.now().strftime("%H:%M:%S")
        
        resultado = self.controlador.registrar_asistencia(id_usuario, fecha, hora_entrada)
        
        if isinstance(resultado, int) and resultado > 0:
            self.mostrar_mensaje(f"Entrada registrada: {hora_entrada}")
        else:
            self.mostrar_mensaje(f"Error al registrar entrada: {resultado}")
    
    # ======== MÉTODOS PARA PAGOS ========
    
    def mostrar_menu_pagos(self):
        """Muestra el menú de gestión de pagos."""
        print("\n===== GESTIÓN DE PAGOS =====")
        print("1. Registrar nuevo pago")
        print("2. Ver pagos de usuario")
        print("3. Reporte de pagos mensual")
        print("0. Volver al menú principal")
        return self.solicitar_entrada("Seleccione una opción")
    
    def formulario_registrar_pago(self):
        """Muestra el formulario para registrar un nuevo pago."""
        print("\n===== REGISTRO DE PAGO =====")
        
        # Primero mostramos los usuarios para seleccionar
        self.listar_usuarios()
        id_usuario = self.solicitar_entrada("ID del Usuario")
        
        monto = float(self.solicitar_entrada("Monto"))
        fecha_pago = datetime.now().strftime("%Y-%m-%d")
        
        print("\nConceptos disponibles:")
        print("1. Mensualidad")
        print("2. Matrícula")
        print("3. Clase especial")
        print("4. Producto")
        opcion = self.solicitar_entrada("Seleccione concepto")
        
        conceptos = {
            "1": "Mensualidad",
            "2": "Matrícula",
            "3": "Clase especial",
            "4": "Producto"
        }
        
        concepto = conceptos.get(opcion, "Otro")
        
        print("\nMétodos de pago:")
        print("1. Efectivo")
        print("2. Tarjeta de crédito")
        print("3. Transferencia")
        opcion = self.solicitar_entrada("Seleccione método de pago")
        
        metodos = {
            "1": "Efectivo",
            "2": "Tarjeta de crédito",
            "3": "Transferencia"
        }
        
        metodo_pago = metodos.get(opcion, "Otro")
        
        resultado = self.controlador.registrar_pago(id_usuario, monto, fecha_pago, concepto, metodo_pago)
        
        if isinstance(resultado, int) and resultado > 0:
            self.mostrar_mensaje("Pago registrado exitosamente.")
        else:
            self.mostrar_mensaje(f"Error al registrar pago: {resultado}")
    
    # ======== MÉTODOS PARA REPORTES ========
    
    def mostrar_menu_reportes(self):
        """Muestra el menú de reportes y estadísticas."""
        print("\n===== REPORTES Y ESTADÍSTICAS =====")
        print("1. Reporte de asistencia")
        print("2. Reporte de pagos")
        print("3. Usuarios activos")
        print("0. Volver al menú principal")
        return self.solicitar_entrada("Seleccione una opción")
    
    def reporte_asistencia(self):
        """Genera y muestra un reporte de asistencia."""
        print("\n===== REPORTE DE ASISTENCIA =====")
        fecha_inicio = self.solicitar_entrada("Fecha de inicio (YYYY-MM-DD)")
        fecha_fin = self.solicitar_entrada("Fecha de fin (YYYY-MM-DD)")
        
        estadisticas = self.controlador.obtener_estadisticas_asistencia(fecha_inicio, fecha_fin)
        
        if estadisticas:
            print("\nFecha\t\tTotal de Asistencias")
            print("----------------------------------")
            for stat in estadisticas:
                print(f"{stat[0]}\t{stat[1]}")
        else:
            self.mostrar_mensaje("No hay datos de asistencia para el período seleccionado.")
    
    # ======== MÉTODO PRINCIPAL ========
    
    def iniciar(self):
        """Método principal que inicia la aplicación."""
        salir = False
        
        while not salir:
            opcion = self.mostrar_menu_principal()
            
            if opcion == "1":  # Gestión de Usuarios
                self.gestionar_usuarios()
            elif opcion == "2":  # Gestión de Ejercicios
                self.gestionar_ejercicios()
            elif opcion == "3":  # Gestión de Rutinas
                self.gestionar_rutinas()
            elif opcion == "4":  # Control de Asistencia
                self.gestionar_asistencia()
            elif opcion == "5":  # Gestión de Pagos
                self.gestionar_pagos()
            elif opcion == "6":  # Reportes y Estadísticas
                self.gestionar_reportes()
            elif opcion == "0":  # Salir
                salir = True
                self.mostrar_mensaje("¡Gracias por usar el Sistema de Gestión de Gimnasio!")
            else:
                self.mostrar_mensaje("Opción no válida. Intente de nuevo.")
    
    def gestionar_usuarios(self):
        """Gestiona el menú de usuarios."""
        salir = False
        
        while not salir:
            opcion = self.mostrar_menu_usuarios()
            
            if opcion == "1":  # Registrar nuevo usuario
                self.formulario_registro_usuario()
            elif opcion == "2":  # Buscar usuario
                self.buscar_usuario()
            elif opcion == "3":  # Listar todos los usuarios
                self.listar_usuarios()
            elif opcion == "4":  # Modificar usuario
                self.mostrar_mensaje("Funcionalidad no implementada aún.")
            elif opcion == "5":  # Eliminar usuario
                self.mostrar_mensaje("Funcionalidad no implementada aún.")
            elif opcion == "0":  # Volver al menú principal
                salir = True
            else:
                self.mostrar_mensaje("Opción no válida. Intente de nuevo.")
    
    # ... Implementa los métodos restantes para gestionar los otros menús...
    
    def gestionar_ejercicios(self):
        """Gestiona el menú de ejercicios."""
        # Implementación similar a gestionar_usuarios
        pass
    
    def gestionar_rutinas(self):
        """Gestiona el menú de rutinas."""
        # Implementación similar a gestionar_usuarios
        pass
    
    def gestionar_asistencia(self):
        """Gestiona el menú de asistencia."""
        # Implementación similar a gestionar_usuarios
        pass
    
    def gestionar_pagos(self):
        """Gestiona el menú de pagos."""
        # Implementación similar a gestionar_usuarios
        pass
    
    def gestionar_reportes(self):
        """Gestiona el menú de reportes."""
        # Implementación similar a gestionar_usuarios
        pass