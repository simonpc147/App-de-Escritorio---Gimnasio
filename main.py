# MODIFICA tu archivo main.py o donde inicializes la aplicación:

import tkinter as tk
from tkinter import ttk
# Importa tus vistas y controladores aquí
# from views.main_view import MainView
# from controllers.auth_controller import AuthController

class GimnasioApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏋️ Gimnasio Athenas - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Maximizado en Windows
        
        # Datos de usuario simulados (bypass del login)
        self.usuario_actual = {
            "success": True,
            "message": "Bienvenido María González",
            "token_sesion": "token_simulado_123",
            "usuario": {
                "id": 1,
                "nombre": "María",
                "apellido": "González", 
                "email": "duena@gimnasio.com",
                "rol": "admin_principal"
            },
            "dashboard_url": "/dashboard/admin"
        }
        
        self.inicializar_app()
    
    def inicializar_app(self):
        """Inicializa la aplicación directamente en el dashboard"""
        print("🚀 === INICIANDO GIMNASIO ATHENAS (MODO DESARROLLO) ===")
        print(f"👤 Usuario: {self.usuario_actual['usuario']['nombre']} {self.usuario_actual['usuario']['apellido']}")
        print(f"🎭 Rol: {self.usuario_actual['usuario']['rol']}")
        print("=" * 60)
        
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # AQUÍ CARGAS TU VISTA PRINCIPAL/DASHBOARD
        self.cargar_dashboard()
    
    def cargar_dashboard(self):
        """Carga el dashboard principal según el rol"""
        rol = self.usuario_actual['usuario']['rol']
        
        if rol == 'admin_principal':
            self.cargar_dashboard_admin()
        elif rol == 'secretaria':
            self.cargar_dashboard_secretaria()
        elif rol == 'coach':
            self.cargar_dashboard_coach()
        elif rol == 'atleta':
            self.cargar_dashboard_atleta()
        else:
            self.cargar_dashboard_default()
    
    def cargar_dashboard_admin(self):
        """Dashboard para administrador principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="🏋️ DASHBOARD ADMINISTRADOR",
            font=('Segoe UI', 20, 'bold')
        )
        title_label.pack(side='left')
        
        user_label = ttk.Label(
            header_frame,
            text=f"👤 {self.usuario_actual['usuario']['nombre']} {self.usuario_actual['usuario']['apellido']} | 🎭 {self.usuario_actual['usuario']['rol']}",
            font=('Segoe UI', 10)
        )
        user_label.pack(side='right')
        
        # Separador
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 20))
        
        # Contenido principal
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Menú de navegación
        self.crear_menu_navegacion(content_frame)
        
        # Área de contenido
        self.crear_area_contenido(content_frame)
    
    def crear_menu_navegacion(self, parent):
        """Crea el menú de navegación lateral"""
        # Frame del menú
        menu_frame = ttk.LabelFrame(parent, text="📋 MÓDULOS DEL SISTEMA", padding=10)
        menu_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Botones del menú
        botones_menu = [
            ("👥 Gestión de Usuarios", self.abrir_gestion_usuarios),
            ("🏃‍♂️ Gestión de Atletas", self.abrir_gestion_atletas),
            ("💪 Gestión de Coaches", self.abrir_gestion_coaches),
            ("💰 Gestión de Pagos", self.abrir_gestion_pagos),
            ("📊 Reportes Financieros", self.abrir_reportes),
            ("⚙️ Configuración", self.abrir_configuracion),
            ("🔐 Gestión de Sesiones", self.abrir_sesiones),
            ("📈 Dashboard Analytics", self.abrir_analytics)
        ]
        
        for texto, comando in botones_menu:
            btn = ttk.Button(
                menu_frame,
                text=texto,
                command=comando,
                width=25
            )
            btn.pack(fill='x', pady=2)
        
        # Separador
        ttk.Separator(menu_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Botón de cerrar sesión
        logout_btn = ttk.Button(
            menu_frame,
            text="🚪 Cerrar Sesión",
            command=self.cerrar_sesion
        )
        logout_btn.pack(fill='x', pady=5)
    
    def crear_area_contenido(self, parent):
        """Crea el área principal de contenido"""
        # Frame de contenido
        self.content_frame = ttk.LabelFrame(parent, text="📄 ÁREA DE TRABAJO", padding=10)
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # Contenido inicial - Dashboard resumen
        self.mostrar_dashboard_resumen()
    
    def mostrar_dashboard_resumen(self):
        """Muestra el resumen principal del dashboard"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Título
        title = ttk.Label(
            self.content_frame,
            text="📊 RESUMEN GENERAL DEL GIMNASIO",
            font=('Segoe UI', 16, 'bold')
        )
        title.pack(pady=(0, 20))
        
        # Frame para estadísticas
        stats_frame = ttk.Frame(self.content_frame)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Tarjetas de estadísticas (simuladas)
        estadisticas = [
            ("👥 Usuarios Totales", "45", "#3b82f6"),
            ("🏃‍♂️ Atletas Activos", "38", "#10b981"),
            ("💪 Coaches", "8", "#f59e0b"),
            ("💰 Ingresos del Mes", "$12,450", "#ef4444")
        ]
        
        for i, (titulo, valor, color) in enumerate(estadisticas):
            card_frame = ttk.LabelFrame(stats_frame, text=titulo, padding=10)
            card_frame.grid(row=0, column=i, padx=5, sticky='ew')
            stats_frame.grid_columnconfigure(i, weight=1)
            
            valor_label = ttk.Label(
                card_frame,
                text=valor,
                font=('Segoe UI', 18, 'bold')
            )
            valor_label.pack()
        
        # Actividades recientes
        recent_frame = ttk.LabelFrame(self.content_frame, text="📝 ACTIVIDADES RECIENTES", padding=10)
        recent_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Lista de actividades simuladas
        actividades = [
            "✅ Nuevo atleta registrado: Juan Pérez",
            "💰 Pago recibido: $150 - María López",
            "👥 Nuevo coach asignado: Carlos Ruiz",
            "📊 Reporte mensual generado",
            "🔄 Sistema actualizado a v1.0.1"
        ]
        
        for actividad in actividades:
            act_label = ttk.Label(recent_frame, text=actividad, font=('Segoe UI', 10))
            act_label.pack(anchor='w', pady=2)
        
        # Mensaje de bienvenida
        welcome_frame = ttk.Frame(self.content_frame)
        welcome_frame.pack(fill='x', pady=(20, 0))
        
        welcome_msg = ttk.Label(
            welcome_frame,
            text="🎉 ¡Bienvenido al Sistema de Gestión del Gimnasio Athenas!\nSelecciona un módulo del menú lateral para comenzar.",
            font=('Segoe UI', 11),
            justify='center'
        )
        welcome_msg.pack()
    
    # ==================== MÉTODOS DE NAVEGACIÓN ====================
    
    def abrir_gestion_usuarios(self):
        """Abre la gestión de usuarios"""
        self.mostrar_mensaje_modulo("👥 GESTIÓN DE USUARIOS", 
                                   "Aquí podrás crear, editar y administrar todos los usuarios del sistema.")
    
    def abrir_gestion_atletas(self):
        """Abre la gestión de atletas"""
        self.mostrar_mensaje_modulo("🏃‍♂️ GESTIÓN DE ATLETAS", 
                                   "Administra los atletas, sus datos personales y asignaciones.")
    
    def abrir_gestion_coaches(self):
        """Abre la gestión de coaches"""
        self.mostrar_mensaje_modulo("💪 GESTIÓN DE COACHES", 
                                   "Gestiona los entrenadores y sus asignaciones con atletas.")
    
    def abrir_gestion_pagos(self):
        """Abre la gestión de pagos"""
        self.mostrar_mensaje_modulo("💰 GESTIÓN DE PAGOS", 
                                   "Controla los pagos, cuotas y estado financiero de los atletas.")
    
    def abrir_reportes(self):
        """Abre los reportes"""
        self.mostrar_mensaje_modulo("📊 REPORTES FINANCIEROS", 
                                   "Genera y visualiza reportes del rendimiento financiero.")
    
    def abrir_configuracion(self):
        """Abre la configuración"""
        self.mostrar_mensaje_modulo("⚙️ CONFIGURACIÓN", 
                                   "Configura los parámetros del sistema y preferencias.")
    
    def abrir_sesiones(self):
        """Abre gestión de sesiones"""
        self.mostrar_mensaje_modulo("🔐 GESTIÓN DE SESIONES", 
                                   "Administra las sesiones activas y la seguridad del sistema.")
    
    def abrir_analytics(self):
        """Abre analytics"""
        self.mostrar_mensaje_modulo("📈 DASHBOARD ANALYTICS", 
                                   "Visualiza métricas y análisis avanzados del gimnasio.")
    
    def mostrar_mensaje_modulo(self, titulo, descripcion):
        """Muestra un mensaje temporal para módulos en desarrollo"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Título del módulo
        title_label = ttk.Label(
            self.content_frame,
            text=titulo,
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(pady=(50, 20))
        
        # Descripción
        desc_label = ttk.Label(
            self.content_frame,
            text=descripcion,
            font=('Segoe UI', 12),
            justify='center'
        )
        desc_label.pack(pady=(0, 30))
        
        # Mensaje de desarrollo
        dev_label = ttk.Label(
            self.content_frame,
            text="🚧 MÓDULO EN DESARROLLO 🚧\n\nEsta funcionalidad se implementará próximamente.\nPor ahora puedes navegar entre los diferentes módulos.",
            font=('Segoe UI', 11),
            justify='center',
            foreground='gray'
        )
        dev_label.pack(pady=20)
        
        # Botón para volver al dashboard
        back_btn = ttk.Button(
            self.content_frame,
            text="🏠 Volver al Dashboard",
            command=self.mostrar_dashboard_resumen
        )
        back_btn.pack(pady=20)
    
    def cerrar_sesion(self):
        """Simula cerrar sesión"""
        print("🚪 Cerrando sesión...")
        self.root.quit()
    
    # Métodos adicionales para otros roles
    def cargar_dashboard_secretaria(self):
        """Dashboard para secretaria"""
        self.cargar_dashboard_admin()  # Por ahora mismo que admin
    
    def cargar_dashboard_coach(self):
        """Dashboard para coach"""
        self.cargar_dashboard_admin()  # Por ahora mismo que admin
    
    def cargar_dashboard_atleta(self):
        """Dashboard para atleta"""
        self.cargar_dashboard_admin()  # Por ahora mismo que admin
    
    def cargar_dashboard_default(self):
        """Dashboard por defecto"""
        self.cargar_dashboard_admin()  # Por ahora mismo que admin
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

# PARA EJECUTAR:
if __name__ == "__main__":
    app = GimnasioApp()
    app.run()