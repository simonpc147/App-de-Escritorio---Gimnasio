import tkinter as tk
import tkinter.simpledialog
from tkinter import ttk, messagebox

from tkcalendar import DateEntry
import sys
import os
from datetime import datetime, timedelta

import tkfontawesome as tkfa
import customtkinter as ctk

from controllers.auth_controller import AuthController
from controllers.rutina_controller import RutinaController
from controllers.user_controller import UserController
from controllers.atleta_controller import AtletaController
from controllers.finance_controller import FinanceController 
from controllers.coach_controller import CoachController
from views.login_view import LoginView
from models.database import Database


class GimnasioApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏋️ Gimnasio Athenas - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  
        
        # Controladores
        self.auth_controller = AuthController()
        self.user_controller = UserController()
        self.atleta_controller = AtletaController()
        self.finance_controller = FinanceController() 
        self.coach_controller = CoachController()
        self.rutina_controller = RutinaController()
        self.db = Database()
        
        self.usuario_actual = None
        self.token_sesion = None
        
        self.configurar_estilos()
        
        self.inicializar_aplicacion()

        self.iconos_cache = {}
        
    def crear_icono(self, nombre_icono, tamaño=16, color="black"):
        """
        Crea un icono de Font Awesome con cache para mejor rendimiento
        """
        cache_key = f"{nombre_icono}_{tamaño}_{color}"
        
        if cache_key not in self.iconos_cache:
            try:
                icono = tkfa.icon_to_image(nombre_icono, scale_to_width=tamaño, fill=color)
                self.iconos_cache[cache_key] = icono
            except Exception as e:
                print(f"⚠️ Error creando icono '{nombre_icono}': {e}")
                return None
                
        return self.iconos_cache[cache_key] 
    
    def configurar_estilos(self):
        """Configura estilos globales de la aplicación - ATHENA STYLE COMPLETO"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.colores = {
            'primary_green': '#1F0E45',     
            'primary_purple': '#dcdad5',    
            'dark_purple': '#6B46C1',       
            'accent_lime': '#CCFF00',       
            'dark_bg': '#FFFFFF',           
            'card_bg': '#FFFFFF',           
            'text_primary': '#0F0F23',     
            'text_secondary': '#FFFFFF',   
            'border_color': '#8B5CF633',   
            'hover_bg': '#FFFFFF',          
            'shadow_color': '#8B5CF64D',    
            'success': '#10b981',
            'warning': '#f59e0b', 
            'error': '#ef4444'
        }
        
        self.root.configure(bg=self.colores['dark_bg'])

        self.style.configure('TLabelFrame',
                            background='#FFFFFF', 
                            foreground=self.colores['text_primary'],
                            font=('Segoe UI', 11, 'bold'),
                            relief='raised',
                            borderwidth=1)
        
        # ===== ESTILOS BÁSICOS NECESARIOS =====
        
        # Configuraciones básicas para widgets principales
        self.style.configure('TFrame', 
                             background=self.colores['card_bg'], 
                             relief='flat',
                             borderwidth=0)


        self.style.configure('TLabel', 
                            background=self.colores['card_bg'], 
                            foreground=self.colores['text_primary'])
        self.style.configure('TButton', font=('Segoe UI', 10))
        
        # ===== ESTILOS PARA FRAMES =====
        
        self.style.configure('Main.TFrame', 
                            background=self.colores['dark_bg'],
                            relief='flat',
                            borderwidth=0)
        
        self.style.configure('Card.TFrame',
                            background=self.colores['card_bg'],
                            relief='flat',
                            borderwidth=0)
        
        # ===== ESTILOS PARA LABELS =====
        
        self.style.configure('Header.TLabel',
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_primary'],
                            font=('Segoe UI', 20, 'bold'))
        
        self.style.configure('HeaderSub.TLabel',
                            background=self.colores['card_bg'], 
                            foreground=self.colores['text_secondary'],
                            font=('Segoe UI', 10))
        
        self.style.configure('User.TLabel',
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_primary'],
                            font=('Segoe UI', 11, 'bold'))
        
        self.style.configure('Title.TLabel',
                            background=self.colores['card_bg'],
                            foreground=self.colores['primary_green'],
                            font=('Segoe UI', 18, 'bold'))
        
        self.style.configure('Info.TLabel',
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_secondary'],
                            font=('Segoe UI', 10))
        
        # ===== ESTILOS PARA BOTONES =====
        
        self.style.configure('Menu.TButton',
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_primary'],
                            font=('Segoe UI', 10, 'normal'),
                            relief='flat',
                            borderwidth=0,
                            focuscolor='none')
        
        self.style.map('Menu.TButton',
                    background=[('active', self.colores['hover_bg']),
                                ('pressed', self.colores['primary_green'])],
                    foreground=[('active', self.colores['dark_bg']),
                                ('pressed', self.colores['dark_bg'])],
                    relief=[('pressed', 'sunken')])
        
        self.style.configure('MenuActive.TButton',
                            background=self.colores['primary_green'],
                            foreground=self.colores['dark_bg'],
                            font=('Segoe UI', 10, 'bold'),
                            relief='raised',
                            borderwidth=0)
        
        self.style.configure('Logout.TButton',
                            background='#EF4444',
                            foreground=self.colores['text_primary'],
                            font=('Segoe UI', 10, 'bold'),
                            relief='raised',
                            borderwidth=0)
        
        self.style.map('Logout.TButton',
                    background=[('active', '#DC2626')],
                    relief=[('pressed', 'sunken')])
        
        
        self.style.configure('Section.TLabelFrame',
                            background=self.colores['card_bg'],
                            foreground=self.colores['primary_purple'],
                            font=('Segoe UI', 11, 'bold'),
                            relief='raised',
                            borderwidth=1)
        
        self.style.configure('Module.TLabelFrame',
                            background=self.colores['card_bg'],
                            foreground=self.colores['primary_green'],
                            font=('Segoe UI', 11, 'bold'),
                            relief='raised',
                            borderwidth=1)
        
        # ===== ESTILOS PARA TREEVIEW =====
        
        self.style.configure('Treeview',
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_primary'],
                            fieldbackground=self.colores['card_bg'],
                            borderwidth=1,
                            relief='solid')
        
        self.style.configure('Treeview.Heading',
                            background=self.colores['primary_purple'],
                            foreground=self.colores['text_primary'],
                            font=('Segoe UI', 10, 'bold'),
                            relief='raised',
                            borderwidth=1)
        
        self.style.map('Treeview',
                    background=[('selected', self.colores['primary_green'])],
                    foreground=[('selected', self.colores['dark_bg'])])
        
        # ===== ESTILOS PARA ENTRY Y COMBOBOX =====
        
        self.style.configure('TEntry',
                            fieldbackground=self.colores['card_bg'],
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_primary'],
                            borderwidth=1,
                            relief='solid',
                            insertcolor=self.colores['primary_green'])
        
        self.style.configure('TCombobox',
                            fieldbackground=self.colores['card_bg'],
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_primary'],
                            borderwidth=1,
                            relief='solid',
                            arrowcolor=self.colores['primary_green'])
        
        # ===== ESTILOS PARA SCROLLBAR =====
        
        self.style.configure('TScrollbar',
                            background=self.colores['card_bg'],
                            troughcolor=self.colores['dark_bg'],
                            borderwidth=1,
                            relief='solid',
                            arrowcolor=self.colores['primary_green'])
        
        # ===== SEPARADORES =====
        
        self.style.configure('Athena.TSeparator',
                            background=self.colores['border_color'])
        
        # ===== CHECKBUTTON =====
        
        self.style.configure('TCheckbutton',
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_primary'],
                            focuscolor='none')
        
        # ===== RADIOBUTTON =====
        
        self.style.configure('TRadiobutton',
                            background=self.colores['card_bg'],
                            foreground=self.colores['text_primary'],
                            focuscolor='none')
        
        # ===== PROGRESSBAR =====
        
        self.style.configure('TProgressbar',
                            background=self.colores['primary_green'],
                            troughcolor=self.colores['dark_bg'],
                            borderwidth=1,
                            relief='solid')
        
        # ===== NOTEBOOK (TABS) =====
        
        self.style.configure('TNotebook',
                            background=self.colores['card_bg'],
                            borderwidth=1,
                            relief='solid')
        
        self.style.configure('TNotebook.Tab',
                            background=self.colores['dark_bg'],
                            foreground=self.colores['text_secondary'],
                            padding=[20, 10],
                            font=('Segoe UI', 10))
        
        self.style.map('TNotebook.Tab',
                    background=[('selected', self.colores['primary_green']),
                                ('active', self.colores['hover_bg'])],
                    foreground=[('selected', self.colores['dark_bg']),
                                ('active', self.colores['dark_bg'])])     
        
    def inicializar_aplicacion(self):
        """Inicializa la aplicación verificando la conexión a BD"""
        print("🏋️ === INICIANDO GIMNASIO ATHENAS ===")
        
        # Verificar conexión a base de datos
        if not self.verificar_conexion_bd():
            self.mostrar_error_conexion()
            return
        
        print("✅ Conexión a BD establecida")
        print("🔐 Cargando sistema de autenticación...")
        
        # Cargar vista de login
        self.mostrar_login()
    
    def verificar_conexion_bd(self):
        """Verifica la conexión a la base de datos"""
        try:
            if self.db.connect():
                self.db.disconnect()
                return True
            return False
        except Exception as e:
            print(f"❌ Error de conexión BD: {e}")
            return False
    
    def mostrar_error_conexion(self):
        """Muestra error de conexión y cierra la aplicación"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame de error
        error_frame = ttk.Frame(self.root)
        error_frame.pack(expand=True)
        
        # Icono de error
        error_label = ttk.Label(
            error_frame,
            text="❌",
            font=('Segoe UI', 48)
        )
        error_label.pack(pady=(50, 20))
        
        # Título de error
        title_label = ttk.Label(
            error_frame,
            text="Error de Conexión",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Mensaje de error
        msg_label = ttk.Label(
            error_frame,
            text="No se pudo conectar a la base de datos.\nVerifica que MySQL esté ejecutándose y la configuración sea correcta.",
            font=('Segoe UI', 12),
            justify='center'
        )
        msg_label.pack(pady=(0, 30))
        
        # Botón de reintento
        retry_btn = ttk.Button(
            error_frame,
            text="🔄 Reintentar",
            command=self.inicializar_aplicacion
        )
        retry_btn.pack(pady=5)
        
        # Botón de salir
        exit_btn = ttk.Button(
            error_frame,
            text="🚪 Salir",
            command=self.root.quit
        )
        exit_btn.pack(pady=5)
    
    def mostrar_login(self):
        """Muestra la vista de login"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Crear frame principal para login
        login_frame = ttk.Frame(self.root)
        login_frame.pack(fill='both', expand=True)
        
        # Crear vista de login
        self.login_view = LoginView(
            login_frame, 
            self.auth_controller, 
            self.on_login_exitoso
        )
        
        print("🔐 Vista de login cargada")
    
    def on_login_exitoso(self, resultado_login):
        """Callback cuando el login es exitoso"""
        print(f"✅ Login exitoso: {resultado_login['usuario']['nombre']}")
        
        # Guardar datos de sesión
        self.usuario_actual = resultado_login['usuario']
        self.token_sesion = resultado_login['token_sesion']
        
        # Cargar dashboard según el rol
        self.cargar_dashboard()
    
    def cargar_dashboard(self):
        """Carga el dashboard principal según el rol del usuario"""
        print(f"📊 Cargando dashboard para rol: {self.usuario_actual['rol']}")
        
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Crear dashboard según el rol
        if self.usuario_actual['rol'] == 'admin_principal':
            self.crear_dashboard_admin()
        elif self.usuario_actual['rol'] == 'secretaria':
            self.crear_dashboard_secretaria()
        elif self.usuario_actual['rol'] == 'coach':
            self.crear_dashboard_coach()
        elif self.usuario_actual['rol'] == 'atleta':
            self.crear_dashboard_atleta()
        else:
            self.crear_dashboard_default()
    
    def crear_dashboard_admin(self):
        """Dashboard para administrador principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        self.crear_header(main_frame)
        
        # Contenido principal
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Menú lateral
        self.crear_menu_lateral(content_frame)
        
        # Área de trabajo
        self.crear_area_trabajo(content_frame)
        
        # Mostrar dashboard inicial
        self.mostrar_dashboard_resumen()
    
    def crear_header(self, parent):
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 5))
        
        header_container = ttk.Frame(header_frame, style='Card.TFrame')
        header_container.pack(fill='x', padx=10, pady=15)
        
        left_section = ttk.Frame(header_container, style='Card.TFrame')
        left_section.pack(side='left', fill='y')
        
        logo_frame = ttk.Frame(left_section, style='Card.TFrame')
        logo_frame.pack(side='left', padx=(0, 15))
        
        try:
            from PIL import Image, ImageTk
            
            logo_image = Image.open('assets/logo_athena.png')
            original_width, original_height = logo_image.size
            aspect_ratio = original_width / original_height
            
            desired_height = 75 
            desired_width = int(desired_height * aspect_ratio)
            
            logo_image = logo_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
            self.logo_header = ImageTk.PhotoImage(logo_image)
            
            logo_label = tk.Label(
                logo_frame,
                image=self.logo_header,
                bg=self.colores['card_bg'],
                relief='flat',
                borderwidth=0
            )
            logo_label.pack()
            
        except Exception as e:
            print(f"⚠️ No se pudo cargar el logo: {e}")
            logo_label = tk.Label(
                logo_frame,
                text="🏋️",
                font=('Segoe UI', 24, 'bold'),
                bg=self.colores['primary_green'],
                fg=self.colores['dark_bg'],
                width=3,
                height=1,
                relief='raised',
                borderwidth=0
            )
            logo_label.pack()
        
        title_frame = ttk.Frame(left_section, style='Card.TFrame')
        title_frame.pack(side='left', fill='y')
        
        title_label = ttk.Label(
            title_frame,
            text="GIMNASIO ATHENA",
            style='Header.TLabel',
            font=('Trebuchet MS', 28, 'bold'),
        )
        title_label.pack(anchor='w', pady=(15, 0))
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Sistema de Gestión Integral",
            style='HeaderSub.TLabel'
        )
        subtitle_label.pack(anchor='w')
        
        right_section = ttk.Frame(header_container, style='Card.TFrame')
        right_section.pack(side='right', fill='y')
        
        user_info_frame = ttk.Frame(right_section, style='Card.TFrame')
        user_info_frame.pack(side='left', padx=(0, 15))
        
        user_label = ttk.Label(
            user_info_frame,
            text=f"👤 {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
            style='User.TLabel'
        )
        user_label.pack(anchor='e')
        
        role_container = tk.Frame(user_info_frame, bg=self.colores['card_bg'])
        role_container.pack(anchor='e', pady=(5, 0))
        
        role_label = tk.Label(
            role_container,
            text=f"{self.usuario_actual['rol'].replace('_', ' ').title()}",
            font=('Segoe UI', 9, 'normal'),
            fg=self.colores['text_primary'],
            padx=8,
            pady=2,
            relief='raised',
            borderwidth=0
        )
        role_label.pack()
        
        avatar_label = ctk.CTkLabel(
            right_section,
            text=self.usuario_actual['nombre'][0].upper(),
            font=('Segoe UI', 18, 'bold'),
            fg_color=self.colores['accent_lime'],
            text_color="black",
            width=50,
            height=50,
            corner_radius=25
        )
        avatar_label.pack(side='right')
        
        separator = ttk.Separator(parent, orient='horizontal', style='Athena.TSeparator')
        separator.pack(fill='x', pady=(5, 15), padx=10)

    def crear_menu_lateral(self, parent):
        """Crea el menú lateral de navegación"""
        self.menu_frame = tk.Frame(parent, bg='#FFFFFF', relief='flat', bd=0)
        self.menu_frame.pack(side='left', fill='y', padx=(10, 10))

        

        titulo_label = tk.Label(self.menu_frame, 
                           text="📋 MÓDULOS DEL SISTEMA", 
                           bg='#FFFFFF',
                           fg=self.colores['text_primary'],
                           font=('Segoe UI', 11, 'bold'),
                           pady=10)
        titulo_label.pack(fill='x')
        
        botones = self.obtener_botones_por_rol()

        self.botones_menu = []
        
        for icono, texto, comando in botones:
            icono_imagen = self.crear_icono(icono, tamaño=16)

            btn = ctk.CTkButton(
                self.menu_frame,
                text=texto,
                image=icono_imagen, 
                compound='left', 
                anchor='w',
                corner_radius=3,       
                fg_color='#dcdad5',     
                text_color='black',  
                font=('Trebuchet MS', 16, 'normal'),  
                height=45,
                hover_color="#CCFF00", 
                command=comando
            )
            

            btn.pack(fill='x', pady=8)
            self.botones_menu.append(btn)

        ttk.Separator(self.menu_frame, orient='horizontal').pack(fill='x', pady=(15, 0))
        
        self.crear_botones_sistema()

    def activar_boton_menu(self, boton_activo):
        for btn in self.botones_menu:
            btn.configure(fg_color='#dcdad5') 
        
        boton_activo.configure(fg_color="#CCFF00")  
    
    
    # ==================== MÉTODO MENU LATERAL ====================

    def obtener_botones_por_rol(self):
        """Retorna los botones del menú según el rol del usuario con iconos Font Awesome"""
        rol = self.usuario_actual['rol']
        
        if rol == 'admin_principal':
            return [
                ("users", "Administrar Usuarios", self.abrir_gestion_usuarios),
                ("running", "Gestión de Atletas", self.abrir_gestion_atletas),
                ("user-tie", "Entrenadores", self.abrir_gestion_coaches),
                ("dollar-sign", "Control de Pagos", self.abrir_gestion_pagos),
                ("money-bill-wave", "Registrar Gastos", self.abrir_gestion_egresos),
                ("chart-bar", "Reportes Financieros", self.abrir_reportes),
                ("dumbbell", "Rutinas", self.abrir_gestion_rutinas),
            ]
        elif rol == 'secretaria':
            return [
                ("running", "Gestión de Atletas", self.abrir_gestion_atletas),
                ("user-tie", "Entrenadores", self.abrir_gestion_coaches),
                ("dollar-sign", "Control de Pagos", self.abrir_gestion_pagos),
                ("chart-bar", "Reportes Financieros", self.abrir_reportes),
            ]
        elif rol == 'coach':
            return [
                ("users", "Mis Atletas", self.mostrar_mis_atletas_coach),
                ("dumbbell", "Rutinas", self.abrir_gestion_rutinas)
            ]
        else:
            return [("tachometer-alt", "Dashboard", self.mostrar_dashboard_resumen)]

    def crear_botones_sistema(self):
        """Crea botones de sistema (cerrar sesión, etc.)"""

        spacer_frame = tk.Frame(self.menu_frame, bg='#FFFFFF')
        spacer_frame.pack(fill='both', expand=True)

        logout_icono = self.crear_icono("sign-out-alt", tamaño=16, color="white")  # ← Icono Font Awesome

        logout_btn = ctk.CTkButton( 
            self.menu_frame,
            text="Cerrar Sesión",
            image=logout_icono,
            compound='left',
            anchor='center',
            corner_radius=3,
            fg_color='#8B1538',       
            hover_color='#A91D47',    
            text_color='white',
            font=('Segoe UI', 14, 'bold'),
            height=45,
            command=self.cerrar_sesion
        )
        logout_btn.pack(fill='x', pady=(15))
    
    def crear_area_trabajo(self, parent):
        """Crea el área principal de trabajo"""
        self.work_frame = tk.Frame(parent, bg='#FFFFFF', padx=5, pady=5)
        self.work_frame.pack(side='right', fill='both', expand=True)
    
    def mostrar_dashboard_resumen(self):
        """Muestra el resumen principal del dashboard"""
        self.limpiar_area_trabajo()
        
        # Título
        title = ttk.Label(
            self.work_frame,
            text="📊 DASHBOARD PRINCIPAL",
            font=('Segoe UI', 16, 'bold')
        )
        title.pack(pady=(0, 20))
        
        welcome_msg = ttk.Label(
            self.work_frame,
            text=f"¡Bienvenido/a {self.usuario_actual['nombre']}!\nSelecciona un módulo del menú lateral para comenzar.",
            font=('Segoe UI', 12),
            justify='center'
        )
        welcome_msg.pack(pady=20)
        
        # Información de sesión
        session_frame = ttk.LabelFrame(self.work_frame, text="🔐 Información de Sesión", padding=10)
        session_frame.pack(fill='x', pady=20)
        
        session_info = [
            f"👤 Usuario: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
            f"📧 Email: {self.usuario_actual['email']}",
            f"🎭 Rol: {self.usuario_actual['rol'].replace('_', ' ').title()}",
            f"🔑 Token: {self.token_sesion[:10]}..."
        ]
        
        for info in session_info:
            label = ttk.Label(session_frame, text=info, font=('Segoe UI', 10))
            label.pack(anchor='w', pady=2)
    
    def limpiar_area_trabajo(self):
        """Limpia el área de trabajo de forma segura"""
        try:
            if hasattr(self, 'work_frame') and self.work_frame and self.work_frame.winfo_exists():
                for widget in self.work_frame.winfo_children():
                    widget.destroy()
        except (tk.TclError, AttributeError):
            # El widget no existe o ya fue destruido
            pass
    
    # ==================== ADMINISTRAR USUARIOS ====================
    
    def abrir_gestion_usuarios(self):
        """Abre la gestión de usuarios"""
        if not self.verificar_permisos(['admin_principal']):
            return
        
        self.activar_boton_menu(self.botones_menu[0])

        self.mostrar_gestion_usuarios()

    def mostrar_gestion_usuarios(self):
        """Muestra el módulo completo de gestión de usuarios"""
        self.limpiar_area_trabajo()
        
        # Variables para el módulo
        self.usuarios_data = []
        self.usuario_seleccionado = None
        
        # Título del módulo
        title_frame = ttk.Frame(self.work_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="👥 GESTIÓN DE USUARIOS",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(side='left')
        
        # Botón de actualizar
        refresh_btn = ttk.Button(
            title_frame,
            text="🔄 Actualizar",
            command=self.cargar_usuarios
        )
        refresh_btn.pack(side='right')
        
        # Frame de controles
        controls_frame = ttk.Frame(self.work_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Búsqueda
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side='left', padx=(0, 10))
        self.search_var.trace('w', self.filtrar_usuarios)
        
        # Filtro por rol
        ttk.Label(search_frame, text="🎭 Rol:").pack(side='left', padx=(10, 5))
        
        self.rol_filter_var = tk.StringVar(value="Todos")
        rol_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.rol_filter_var,
            values=["Todos", "admin_principal", "secretaria", "coach", "atleta"],
            state="readonly",
            width=15
        )
        rol_combo.pack(side='left')
        rol_combo.bind('<<ComboboxSelected>>', self.filtrar_usuarios)
        
        # Botones de acción
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side='right')
        
        self.create_btn = ttk.Button(
            buttons_frame,
            text="➕ Crear Usuario",
            command=self.crear_usuario
        )
        self.create_btn.pack(side='left', padx=2)
        
        self.toggle_btn = ttk.Button(
            buttons_frame,
            text="🔄 Activar/Desactivar",
            command=self.toggle_usuario_estado,
            state='disabled'
        )
        self.toggle_btn.pack(side='left', padx=2)


        self.edit_btn = ttk.Button(
            buttons_frame,
            text="✏️ Editar", 
            command=self.editar_usuario,
            state='disabled'
        )
        self.edit_btn.pack(side='left', padx=1)

        self.toggle_btn = ttk.Button(
            buttons_frame,
            text="🗑️ Eliminar",
            command=self.eliminar_usuario,
            state='disabled'
        )
        self.toggle_btn.pack(side='left', padx=1)
        
        # Tabla de usuarios
        self.crear_tabla_usuarios()
        
        # Cargar datos iniciales
        self.cargar_usuarios()

    def crear_tabla_usuarios(self):
        """Crea la tabla de usuarios con Treeview"""
        # Frame para la tabla
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        # Configurar Treeview
        columns = ('ID', 'Nombre', 'Apellido', 'Email', 'Rol', 'Estado', 'Creado')
        self.usuarios_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        # Configurar encabezados
        self.usuarios_tree.heading('ID', text='ID')
        self.usuarios_tree.heading('Nombre', text='Nombre')
        self.usuarios_tree.heading('Apellido', text='Apellido')
        self.usuarios_tree.heading('Email', text='Email')
        self.usuarios_tree.heading('Rol', text='Rol')
        self.usuarios_tree.heading('Estado', text='Estado')
        self.usuarios_tree.heading('Creado', text='Fecha Creación')
        
        # Configurar anchos
        self.usuarios_tree.column('ID', width=10, anchor='center')
        self.usuarios_tree.column('Nombre', width=70)
        self.usuarios_tree.column('Apellido', width=70)
        self.usuarios_tree.column('Email', width=120)
        self.usuarios_tree.column('Rol', width=70, anchor='center')
        self.usuarios_tree.column('Estado', width=30, anchor='center')
        self.usuarios_tree.column('Creado', width=50, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.usuarios_tree.yview)
        self.usuarios_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Empaquetar
        self.usuarios_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        # Eventos
        self.usuarios_tree.bind('<<TreeviewSelect>>', self.on_usuario_selected)
        self.usuarios_tree.bind('<Double-1>', self.editar_usuario)

    def cargar_usuarios(self):
        """Carga los usuarios desde la base de datos"""
        try:
            print("🔄 Cargando usuarios...")
            
            # Obtener usuarios del modelo
            usuarios = self.auth_controller.usuario_model.read_usuarios()
            self.usuarios_data = usuarios
            
            print(f"✅ Cargados {len(usuarios)} usuarios")
            
            # Actualizar tabla
            self.actualizar_tabla_usuarios()
            
        except Exception as e:
            print(f"❌ Error cargando usuarios: {e}")
            messagebox.showerror("Error", f"Error al cargar usuarios:\n{e}")

    def actualizar_tabla_usuarios(self, usuarios_filtrados=None):
        """Actualiza la tabla con los usuarios"""
        for item in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item)
        
        usuarios = usuarios_filtrados if usuarios_filtrados is not None else self.usuarios_data
        
        
        # Llenar tabla
        for usuario in usuarios:
            user_id = usuario[0]
            nombre = usuario[1]
            apellido = usuario[2]
            email = usuario[6]
            rol = usuario[8].replace('_', ' ').title()
            estado = "Activo" if usuario[9] else "Inactivo"
            try:
                if usuario[12]:
                    fecha_str = str(usuario[12])
                    fecha = fecha_str[:10]  
                else:
                    fecha = "N/A"
            except:
                fecha = "N/A"
            
            item = self.usuarios_tree.insert('', 'end', values=(
                user_id, nombre, apellido, email, rol, estado, fecha
            ))

            
            
            if not usuario[9]:
                self.usuarios_tree.set(item, 'Estado', 'Inactivo')
            else:
                self.usuarios_tree.set(item, 'Estado', 'Activo')

    def filtrar_usuarios(self, *args):
        """Filtra usuarios según búsqueda y rol"""
        search_text = self.search_var.get().lower()
        rol_filter = self.rol_filter_var.get()
        
        usuarios_filtrados = []
        
        for usuario in self.usuarios_data:
            # Filtro de texto
            texto_busqueda = f"{usuario[1]} {usuario[2]} {usuario[6]}".lower()
            if search_text and search_text not in texto_busqueda:
                continue
            
            # Filtro de rol
            if rol_filter != "Todos" and usuario[8] != rol_filter:
                continue
            
            usuarios_filtrados.append(usuario)
        
        self.actualizar_tabla_usuarios(usuarios_filtrados)

    def on_usuario_selected(self, event):
        """Maneja la selección de usuario en la tabla"""
        selection = self.usuarios_tree.selection()
        if selection:
            # Habilitar botones
            self.edit_btn.config(state='normal')
            self.toggle_btn.config(state='normal')
            
            # Obtener usuario seleccionado
            item = self.usuarios_tree.item(selection[0])
            user_id = item['values'][0]
            
            # Buscar usuario completo en los datos
            for usuario in self.usuarios_data:
                if usuario[0] == user_id:
                    self.usuario_seleccionado = usuario
                    break
        else:
            # Deshabilitar botones
            self.edit_btn.config(state='disabled')
            self.toggle_btn.config(state='disabled')
            self.usuario_seleccionado = None

    def crear_usuario(self):
        """Abre el formulario para crear un nuevo usuario"""
        self.abrir_formulario_usuario(modo='crear')

    def editar_usuario(self, event=None):
        """Abre el formulario para editar el usuario seleccionado"""

        if not self.usuario_seleccionado:
            print(self.usuario_seleccionado)
            messagebox.showwarning("Advertencia", "Selecciona un usuario para editar")
            return
        
        self.abrir_formulario_usuario(modo='editar', usuario=self.usuario_seleccionado)

    def eliminar_usuario(self):
        """Eliminar_usuario"""
        
        selection = self.usuarios_tree.selection()
        item = self.usuarios_tree.item(selection[0])
        user_id = item['values'][0]

        print(f"id del USUARIOS {user_id}")

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación","¿Está seguro que desea eliminar el usuario seleccionado, esta acción es irreversible"
        )

        if confirmar:
            self.user_controller.eliminar_usuario(user_id)
            messagebox.showinfo("Éxito", "Usuario eliminado exitosamente")
            self.cargar_usuarios()  


    def toggle_usuario_estado(self):
        """Activa/Desactiva el usuario seleccionado"""
        if not self.usuario_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un usuario")
            return
        
        usuario = self.usuario_seleccionado
        nuevo_estado = not usuario[9]  # Invertir estado actual
        estado_texto = "activar" if nuevo_estado else "desactivar"
        
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Estás seguro que deseas {estado_texto} a {usuario[1]} {usuario[2]}?"
        )
        
        if respuesta:
            try:
                # Actualizar en base de datos usando UserController
                resultado = self.user_controller.actualizar_usuario(
                    usuario[0], 
                    {"estado_activo": nuevo_estado},
                    self.usuario_actual['id']
                )
                
                if resultado['success']:
                    messagebox.showinfo("Éxito", f"Usuario {estado_texto} exitosamente")
                    self.cargar_usuarios()  # Recargar tabla
                else:
                    messagebox.showerror("Error", resultado['message'])
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al {estado_texto} usuario:\n{e}")

    def abrir_formulario_usuario(self, modo='crear', usuario=None):
        """Abre el formulario modal para crear/editar usuario"""
        # Crear ventana modal
        self.form_window = tk.Toplevel(self.root)
        self.form_window.title(f"{'Crear' if modo == 'crear' else 'Editar'} Usuario")
        self.form_window.geometry("500x600")
        self.form_window.resizable(False, False)
        self.form_window.transient(self.root)
        self.form_window.grab_set()
        
        # Centrar ventana
        self.form_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Frame principal del formulario
        main_frame = ttk.Frame(self.form_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text=f"{'➕ CREAR' if modo == 'crear' else '✏️ EDITAR'} USUARIO",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Variables del formulario
        self.form_vars = {
            'nombre': tk.StringVar(),
            'apellido': tk.StringVar(),
            'edad': tk.StringVar(),
            'direccion': tk.StringVar(),
            'telefono': tk.StringVar(),
            'email': tk.StringVar(),
            'contraseña': tk.StringVar(),
            'rol': tk.StringVar(),
            'estado_activo': tk.BooleanVar(value=True)
        }
        
        # Si es edición, cargar datos
        if modo == 'editar' and usuario:
            self.form_vars['nombre'].set(usuario[1])
            self.form_vars['apellido'].set(usuario[2])
            self.form_vars['edad'].set(usuario[3] if usuario[3] else '')
            self.form_vars['direccion'].set(usuario[4] if usuario[4] else '')
            self.form_vars['telefono'].set(usuario[5] if usuario[5] else '')
            self.form_vars['email'].set(usuario[6])
            self.form_vars['contraseña'].set(usuario[7])
            self.form_vars['rol'].set(usuario[8])
            self.form_vars['estado_activo'].set(usuario[9])
        
        # Crear campos del formulario
        self.crear_campos_formulario(main_frame, modo)
        
        # Botones
        self.crear_botones_formulario(main_frame, modo)

    def crear_campos_formulario(self, parent, modo):
        """Crea los campos del formulario"""
        # Frame para campos
        fields_frame = ttk.Frame(parent)
        fields_frame.pack(fill='both', expand=True)
        
        # Campos del formulario
        campos = [
            ('Nombre *', 'nombre', 'entry'),
            ('Apellido *', 'apellido', 'entry'),
            ('Edad', 'edad', 'entry'),
            ('Dirección', 'direccion', 'text'),
            ('Teléfono', 'telefono', 'entry'),
            ('Email *', 'email', 'entry'),
            ('Contraseña *', 'contraseña', 'password'),
            ('Rol *', 'rol', 'combo'),
            ('Estado', 'estado_activo', 'checkbox')
        ]
        
        for i, (label, var_name, field_type) in enumerate(campos):
            # Frame para cada campo
            field_frame = ttk.Frame(fields_frame)
            field_frame.pack(fill='x', pady=5)
            
            # Label
            ttk.Label(field_frame, text=label, width=15).pack(side='left', anchor='w')
            
            # Campo según tipo
            if field_type == 'entry':
                entry = ttk.Entry(field_frame, textvariable=self.form_vars[var_name], width=30)
                entry.pack(side='right', fill='x', expand=True)
                
            elif field_type == 'password':
                entry = ttk.Entry(field_frame, textvariable=self.form_vars[var_name], show='*', width=30)
                entry.pack(side='right', fill='x', expand=True)
                
            elif field_type == 'text':
                text_frame = ttk.Frame(field_frame)
                text_frame.pack(side='right', fill='x', expand=True)
                text_widget = tk.Text(text_frame, height=3, width=30)
                text_widget.pack(fill='x')
                text_widget.insert('1.0', self.form_vars[var_name].get())
                setattr(self, f'{var_name}_text', text_widget)
                
            elif field_type == 'combo':
                combo = ttk.Combobox(
                    field_frame,
                    textvariable=self.form_vars[var_name],
                    values=['admin_principal', 'secretaria', 'coach', 'atleta'],
                    state='readonly',
                    width=28
                )
                combo.pack(side='right', fill='x', expand=True)
                
            elif field_type == 'checkbox':
                check = ttk.Checkbutton(
                    field_frame,
                    text="Usuario activo",
                    variable=self.form_vars[var_name]
                )
                check.pack(side='right')

    def crear_botones_formulario(self, parent, modo):
        """Crea los botones del formulario"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Botón cancelar
        cancel_btn = ttk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=self.form_window.destroy
        )
        cancel_btn.pack(side='right', padx=(5, 0))
        
        # Botón guardar
        save_btn = ttk.Button(
            buttons_frame,
            text=f"💾 {'Crear' if modo == 'crear' else 'Guardar'}",
            command=lambda: self.guardar_usuario(modo)
        )
        save_btn.pack(side='right')

    def guardar_usuario(self, modo):
        """Guarda el usuario (crear o editar)"""
        try:
            # Validar campos requeridos
            if not self.validar_formulario():
                return
            
            # Recoger datos del formulario
            datos = {}
            for campo, var in self.form_vars.items():
                if campo == 'direccion':
                    # Para el campo de texto
                    datos[campo] = self.direccion_text.get('1.0', 'end-1c')
                else:
                    datos[campo] = var.get()
            
            # Convertir edad a int si no está vacía
            if datos['edad']:
                try:
                    datos['edad'] = int(datos['edad'])
                except ValueError:
                    messagebox.showerror("Error", "La edad debe ser un número")
                    return
            else:
                datos['edad'] = None
            
            # Llamar al controlador
            if modo == 'crear':
                resultado = self.user_controller.crear_usuario(datos, self.usuario_actual['id'])
            else:
                # Para editar, usar el ID del usuario seleccionado
                resultado = self.user_controller.actualizar_usuario(
                    self.usuario_seleccionado[0], 
                    datos, 
                    self.usuario_actual['id']
                )
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['message'])
                self.form_window.destroy()
                self.cargar_usuarios()  # Recargar tabla
            else:
                messagebox.showerror("Error", resultado['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar usuario:\n{e}")

    def validar_formulario(self):
        """Valida los campos requeridos del formulario"""
        # Campos requeridos
        requeridos = ['nombre', 'apellido', 'email', 'contraseña', 'rol']
        
        for campo in requeridos:
            if not self.form_vars[campo].get().strip():
                messagebox.showerror("Error", f"El campo {campo} es requerido")
                return False
        
        # Validar email
        email = self.form_vars['email'].get().strip()
        if '@' not in email:
            messagebox.showerror("Error", "Email inválido")
            return False
        
        return True


    # ==================== GESTION DE ATLETAS ====================

    def abrir_gestion_atletas(self):
        """Abre la gestión de atletas"""
        if not self.verificar_permisos(['admin_principal', 'secretaria']):
            return
        
        self.activar_boton_menu(self.botones_menu[1])
        
        self.mostrar_gestion_atletas()

    def mostrar_gestion_atletas(self):
        """Muestra el módulo completo de gestión de atletas"""
        self.limpiar_area_trabajo()
        
        # Variables para el módulo
        self.atletas_data = []
        self.atleta_seleccionado = None
        
        # Título del módulo - CAMBIAR A tk.Frame con fondo gris
        title_frame = tk.Frame(self.work_frame, bg='#FFFFFF')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🏃‍♂️ GESTIÓN DE ATLETAS",
            font=('Segoe UI', 18, 'bold'),
            bg='#FFFFFF',
            fg='#0F0F23'
        )
        title_label.pack(side='left')
        
        # Botón de actualizar
        refresh_btn = ttk.Button(
            title_frame,
            text="🔄 Actualizar",
            command=self.cargar_atletas
        )
        refresh_btn.pack(side='right')
        
        # Frame de controles - CAMBIAR A tk.Frame con fondo gris
        controls_frame = tk.Frame(self.work_frame, bg='#FFFFFF')
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Búsqueda y filtros
        self.crear_filtros_atletas(controls_frame)
        
        # Botones de acción
        self.crear_botones_atletas(controls_frame)
        
        # Tabla de atletas
        self.crear_tabla_atletas()
        
        # Cargar datos iniciales
        self.cargar_atletas()

    def crear_filtros_atletas(self, parent):
        """Crea los filtros de búsqueda para atletas"""
        # Frame de búsqueda
        search_frame = ttk.Frame(parent)
        search_frame.pack(side='left', fill='x', expand=True)
        
        # Búsqueda por texto
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side='left', padx=(0, 5))
        
        self.search_atletas_var = tk.StringVar()
        self.search_atletas_entry = ttk.Entry(search_frame, textvariable=self.search_atletas_var, width=25)
        self.search_atletas_entry.pack(side='left', padx=(0, 10))
        self.search_atletas_var.trace('w', self.filtrar_atletas)
        
        # Filtro por estado de solvencia
        ttk.Label(search_frame, text="💰 Estado:").pack(side='left', padx=(10, 5))
        
        self.estado_filter_var = tk.StringVar(value="Todos")
        estado_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.estado_filter_var,
            values=["Todos", "solvente", "vencido", "suspendido"],
            state="readonly",
            width=12
        )
        estado_combo.pack(side='left', padx=(0, 10))
        estado_combo.bind('<<ComboboxSelected>>', self.filtrar_atletas)
        
        # Filtro por coach
        ttk.Label(search_frame, text="💪 Coach:").pack(side='left', padx=(10, 5))
        
        self.coach_filter_var = tk.StringVar(value="Todos")
        self.coach_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.coach_filter_var,
            state="readonly",
            width=15
        )
        self.coach_combo.pack(side='left')
        self.coach_combo.bind('<<ComboboxSelected>>', self.filtrar_atletas)

    def crear_botones_atletas(self, parent):
        """Crea los botones de acción para atletas"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(side='right')
        
        # Botón crear atleta
        self.create_atleta_btn = ttk.Button(
            buttons_frame,
            text="➕ Registrar Atleta",
            command=self.registrar_atleta
        )
        self.create_atleta_btn.pack(side='left', padx=2)
        
        # Botón editar
        self.edit_atleta_btn = ttk.Button(
            buttons_frame,
            text="✏️ Editar Perfil",
            command=self.editar_atleta,
            state='disabled'
        )
        self.edit_atleta_btn.pack(side='left', padx=2)
        
        # Botón renovar membresía
        self.renovar_btn = ttk.Button(
            buttons_frame,
            text="🔄 Renovar Membresía",
            command=self.renovar_membresia,
            state='disabled'
        )
        self.renovar_btn.pack(side='left', padx=2)
        
        # Botón asignar coach
        self.assign_coach_btn = ttk.Button(
            buttons_frame,
            text="💪 Asignar Coach",
            command=self.asignar_coach,
            state='disabled'
        )
        self.assign_coach_btn.pack(side='left', padx=2)

    def crear_tabla_atletas(self):
        """Crea la tabla de atletas con Treeview"""
        # Frame para la tabla
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Configurar Treeview
        columns = ('ID', 'Nombre', 'Apellido', 'Cédula', 'Email', 'Plan', 'Coach', 'Estado', 'Vencimiento')
        self.atletas_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.atletas_tree.heading('ID', text='ID')
        self.atletas_tree.heading('Nombre', text='Nombre')
        self.atletas_tree.heading('Apellido', text='Apellido')
        self.atletas_tree.heading('Cédula', text='Cédula')
        self.atletas_tree.heading('Email', text='Email')
        self.atletas_tree.heading('Plan', text='Plan')
        self.atletas_tree.heading('Coach', text='Coach')
        self.atletas_tree.heading('Estado', text='Estado')
        self.atletas_tree.heading('Vencimiento', text='Vencimiento')
        
        # Configurar anchos
        self.atletas_tree.column('ID', width=50, anchor='center')
        self.atletas_tree.column('Nombre', width=100)
        self.atletas_tree.column('Apellido', width=100)
        self.atletas_tree.column('Cédula', width=100)
        self.atletas_tree.column('Email', width=180)
        self.atletas_tree.column('Plan', width=100)
        self.atletas_tree.column('Coach', width=120)
        self.atletas_tree.column('Estado', width=80, anchor='center')
        self.atletas_tree.column('Vencimiento', width=100, anchor='center')
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.atletas_tree.yview)
        self.atletas_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.atletas_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        self.atletas_tree.bind('<<TreeviewSelect>>', self.on_atleta_selected)

    def cargar_atletas(self):
        """Carga los atletas desde la base de datos"""
        try:
            print("🔄 Cargando atletas...")
            
            # Obtener atletas del controlador
            resultado = self.atleta_controller.obtener_todos_atletas()
            if not resultado["success"]:
                messagebox.showerror("Error", resultado["message"])
                return
            
            self.atletas_data = resultado["atletas"]
            print(f"✅ Cargados {len(self.atletas_data)} atletas")
            
            # Cargar coaches para el filtro
            self.cargar_coaches_filtro()
            
            # Actualizar tabla
            self.actualizar_tabla_atletas()
            
        except Exception as e:
            print(f"❌ Error cargando atletas: {e}")
            messagebox.showerror("Error", f"Error al cargar atletas:\n{e}")

    def cargar_coaches_filtro(self):
        """Carga la lista de coaches para el filtro"""
        try:
            # Obtener coaches del user controller
            resultado = self.user_controller.obtener_usuarios_por_rol('coach')
            if resultado["success"]:
                coaches = ["Todos", "Sin Coach"]
                for coach in resultado["usuarios"]:
                    coaches.append(f"{coach[1]} {coach[2]}")  # nombre apellido
                self.coach_combo['values'] = coaches
            else:
                self.coach_combo['values'] = ["Todos", "Sin Coach"]
        except Exception as e:
            print(f"Error cargando coaches: {e}")
            self.coach_combo['values'] = ["Todos", "Sin Coach"]


    def _obtener_nombre_coach(self, coach_id):
        """Obtiene el nombre del coach por su ID"""
        try:
            resultado = self.coach_controller.obtener_todos_coaches()
            if resultado["success"]:
                for coach_completo in resultado["coaches"]:
                    if coach_completo['coach_data'][0] == coach_id:
                        usuario_data = coach_completo['usuario_data']
                        return f"{usuario_data[1]} {usuario_data[2]}"  # nombre + apellido
            return f"Coach ID: {coach_id}"
        except Exception as e:
            print(f"Error obteniendo nombre coach: {e}")
            return f"Coach ID: {coach_id}"

    def actualizar_tabla_atletas(self, atletas_filtrados=None):
        """Actualiza la tabla con los atletas"""
        # Limpiar tabla
        for item in self.atletas_tree.get_children():
            self.atletas_tree.delete(item)
        
        # Usar atletas filtrados o todos
        atletas = atletas_filtrados if atletas_filtrados is not None else self.atletas_data
        
        # Llenar tabla
        for atleta_completo in atletas:
            try:
                atleta_data = atleta_completo['atleta_data']
                usuario_data = atleta_completo['usuario_data']
                
                atleta_id = atleta_data[0]
                nombre = usuario_data[1]
                apellido = usuario_data[2]
                cedula = atleta_data[2] if len(atleta_data) > 2 else "N/A"
                email = usuario_data[6]
                
                plan = f"Plan {atleta_data[5]}" if len(atleta_data) > 5 else "N/A"
                
                plan = f"Plan {atleta_data[7]}" if len(atleta_data) > 7 else "N/A"

                coach_id = atleta_data[8] if len(atleta_data) > 8 else None 
                coach_nombre = self._obtener_nombre_coach(coach_id) if coach_id else "Sin Coach"

                # Estado de solvencia
                estado = atleta_data[9] if len(atleta_data) > 9 else "N/A"
                
                # Fecha de vencimiento
                try:
                    if len(atleta_data) > 7 and atleta_data[7]:
                        if isinstance(atleta_data[7], str):
                            vencimiento = atleta_data[7][:10]
                        else:
                            vencimiento = str(atleta_data[7])[:10]
                    else:
                        vencimiento = "N/A"
                except:
                    vencimiento = "N/A"
                
                # Insertar fila
                item = self.atletas_tree.insert('', 'end', values=(
                    atleta_id, nombre, apellido, cedula, email, plan, coach_nombre, estado, vencimiento
                ))
                
                # Colorear según estado
                if estado == 'vencido':
                    self.atletas_tree.set(item, 'Estado', '🔴 Vencido')
                elif estado == 'suspendido':
                    self.atletas_tree.set(item, 'Estado', '⏸️ Suspendido')
                else:
                    self.atletas_tree.set(item, 'Estado', '🟢 Solvente')
                    
            except Exception as e:
                print(f"Error procesando atleta: {e}")
                continue

    def filtrar_atletas(self, *args):
        """Filtra atletas según búsqueda y filtros"""
        search_text = self.search_atletas_var.get().lower()
        estado_filter = self.estado_filter_var.get()
        coach_filter = self.coach_filter_var.get()
        
        atletas_filtrados = []
        
        for atleta_completo in self.atletas_data:
            try:
                atleta_data = atleta_completo['atleta_data']
                usuario_data = atleta_completo['usuario_data']
                
                # Filtro de texto
                texto_busqueda = f"{usuario_data[1]} {usuario_data[2]} {atleta_data[2]} {usuario_data[6]}".lower()
                if search_text and search_text not in texto_busqueda:
                    continue
                
                # Filtro de estado
                if estado_filter != "Todos":
                    estado_atleta = atleta_data[9] if len(atleta_data) > 9 else "N/A"
                    if estado_atleta != estado_filter:
                        continue
                
                # Filtro de coach
                if coach_filter != "Todos":
                    coach_id = atleta_data[8] if len(atleta_data) > 8 else None
                    if coach_filter == "Sin Coach" and coach_id:
                        continue
                    elif coach_filter != "Sin Coach" and not coach_id:
                        continue
                
                atletas_filtrados.append(atleta_completo)
                
            except Exception as e:
                print(f"Error filtrando atleta: {e}")
                continue
        
        self.actualizar_tabla_atletas(atletas_filtrados)

    def on_atleta_selected(self, event):
        """Maneja la selección de atleta en la tabla"""
        selection = self.atletas_tree.selection()
        if selection:
            # Habilitar botones
            self.edit_atleta_btn.config(state='normal')
            self.renovar_btn.config(state='normal')
            self.assign_coach_btn.config(state='normal')
            
            # Obtener atleta seleccionado
            item = self.atletas_tree.item(selection[0])
            atleta_id = item['values'][0]
            
            # Buscar atleta completo en los datos
            for atleta_completo in self.atletas_data:
                if atleta_completo['atleta_data'][0] == atleta_id:
                    self.atleta_seleccionado = atleta_completo
                    break
        else:
            # Deshabilitar botones
            self.edit_atleta_btn.config(state='disabled')
            self.renovar_btn.config(state='disabled')
            self.assign_coach_btn.config(state='disabled')
            self.atleta_seleccionado = None

    def registrar_atleta(self):
        """Abre el formulario para registrar un nuevo atleta"""
        self.abrir_formulario_atleta(modo='registrar')

    def editar_atleta(self, event=None):
        """Abre el formulario para editar el atleta seleccionado"""
        if not self.atleta_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un atleta para editar")
            return
        
        self.abrir_formulario_atleta(modo='editar', atleta=self.atleta_seleccionado)

    def renovar_membresia(self):
        """Abre diálogo para renovar membresía"""
        if not self.atleta_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un atleta")
            return
        
        atleta_data = self.atleta_seleccionado['atleta_data']
        usuario_data = self.atleta_seleccionado['usuario_data']
        
        # Ventana simple para renovación
        ventana = tk.Toplevel(self.root)
        ventana.title("Renovar Membresía")
        ventana.geometry("500x300")
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Información del atleta
        ttk.Label(ventana, text=f"Renovar membresía de:", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        ttk.Label(ventana, text=f"{usuario_data[1]} {usuario_data[2]}", font=('Segoe UI', 14)).pack()
        
        # Método de pago
        ttk.Label(ventana, text="Método de pago:", font=('Segoe UI', 10)).pack(pady=(20, 5))
        metodo_var = tk.StringVar(value="efectivo")
        metodo_combo = ttk.Combobox(ventana, textvariable=metodo_var, 
                                values=["efectivo", "tarjeta", "transferencia"], 
                                state="readonly")
        metodo_combo.pack(pady=5)
        
        # Botones
        btn_frame = ttk.Frame(ventana)
        btn_frame.pack(pady=20)
        
        def procesar_renovacion():
            try:
                resultado = self.atleta_controller.renovar_membresia(
                    atleta_data[0], metodo_var.get(), self.usuario_actual['id']
                )
                if resultado["success"]:
                    messagebox.showinfo("Éxito", resultado["message"])
                    ventana.destroy()
                    self.cargar_atletas()
                else:
                    messagebox.showerror("Error", resultado["message"])
            except Exception as e:
                messagebox.showerror("Error", f"Error al renovar: {e}")
        
        ttk.Button(btn_frame, text="✅ Renovar", command=procesar_renovacion).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Cancelar", command=ventana.destroy).pack(side='left', padx=5)

    
    def asignar_coach(self):
        """Abre diálogo para asignar coach con lista de disponibles"""
        if not self.atleta_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un atleta")
            return
        
        # Obtener coaches disponibles
        resultado_coaches = self.atleta_controller.obtener_coaches_disponibles()
        if not resultado_coaches["success"]:
            messagebox.showerror("Error", "No se pudieron cargar los coaches disponibles")
            return
        
        coaches_disponibles = resultado_coaches["coaches"]
        
        if not coaches_disponibles:
            messagebox.showinfo("Sin coaches", "No hay coaches disponibles en el sistema")
            return
        
        # Crear ventana modal para selección
        coach_window = tk.Toplevel(self.root)
        coach_window.title("Asignar Coach")
        coach_window.geometry("500x400")
        coach_window.transient(self.root)
        coach_window.grab_set()
        
        # Centrar ventana
        x = (coach_window.winfo_screenwidth() // 2) - 250
        y = (coach_window.winfo_screenheight() // 2) - 200
        coach_window.geometry(f"500x400+{x}+{y}")
        
        main_frame = ttk.Frame(coach_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        atleta_data = self.atleta_seleccionado['atleta_data']
        usuario_data = self.atleta_seleccionado['usuario_data']
        
        ttk.Label(main_frame, 
                text=f"Asignar Coach a: {usuario_data[1]} {usuario_data[2]}", 
                font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Lista de coaches
        ttk.Label(main_frame, text="Selecciona un Coach:", font=('Segoe UI', 12)).pack(anchor='w', pady=(0, 10))
        
        # Frame para lista
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Crear Treeview
        columns = ('Coach', 'Especialidades', 'Horario')
        coaches_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        coaches_tree.heading('Coach', text='Coach')
        coaches_tree.heading('Especialidades', text='Especialidades')
        coaches_tree.heading('Horario', text='Horario Disponible')
        
        coaches_tree.column('Coach', width=150)
        coaches_tree.column('Especialidades', width=150)
        coaches_tree.column('Horario', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=coaches_tree.yview)
        coaches_tree.configure(yscrollcommand=scrollbar.set)
        
        coaches_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Llenar lista con coaches
        coaches_dict = {}  # Para mapear selección a ID
        for coach in coaches_disponibles:
            coach_id = coach[0]
            nombre_completo = coach[4]  # nombre_completo de la consulta JOIN
            especialidades = coach[5] or "No especificado"
            horario = coach[6] or "No especificado"
            
            item_id = coaches_tree.insert('', 'end', values=(nombre_completo, especialidades, horario))
            coaches_dict[item_id] = coach_id
        
        # Variable para coach seleccionado
        coach_seleccionado_id = None
        
        def on_coach_selected(event):
            nonlocal coach_seleccionado_id
            selection = coaches_tree.selection()
            if selection:
                coach_seleccionado_id = coaches_dict[selection[0]]
                asignar_btn.config(state='normal')
            else:
                coach_seleccionado_id = None
                asignar_btn.config(state='disabled')
        
        coaches_tree.bind('<<TreeviewSelect>>', on_coach_selected)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        def asignar_coach_seleccionado():
            if coach_seleccionado_id:
                try:
                    resultado = self.atleta_controller.asignar_coach(
                        atleta_data[0],  # id_atleta
                        coach_seleccionado_id, 
                        self.usuario_actual['id']
                    )
                    if resultado["success"]:
                        messagebox.showinfo("Éxito", resultado["message"])
                        coach_window.destroy()
                        self.cargar_atletas()
                    else:
                        messagebox.showerror("Error", resultado["message"])
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {e}")
        
        def remover_coach():
            try:
                resultado = self.atleta_controller.asignar_coach(
                    atleta_data[0],  # id_atleta
                    None,  # Sin coach
                    self.usuario_actual['id']
                )
                if resultado["success"]:
                    messagebox.showinfo("Éxito", resultado["message"])
                    coach_window.destroy()
                    self.cargar_atletas()
                else:
                    messagebox.showerror("Error", resultado["message"])
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
        
        # Botones
        ttk.Button(buttons_frame, text="❌ Cancelar", command=coach_window.destroy).pack(side='right', padx=(5, 0))
        ttk.Button(buttons_frame, text="🚫 Remover Coach", command=remover_coach).pack(side='right', padx=(5, 0))
        
        asignar_btn = ttk.Button(buttons_frame, text="✅ Asignar Coach", command=asignar_coach_seleccionado, state='disabled')
        asignar_btn.pack(side='right', padx=(5, 0))


    def abrir_formulario_atleta(self, modo='registrar', atleta=None):
        """Abre el formulario modal para registrar/editar atleta con scrollbar"""
        # Crear ventana modal
        self.atleta_form_window = tk.Toplevel(self.root)
        self.atleta_form_window.title(f"{'Registrar' if modo == 'registrar' else 'Editar'} Atleta")
        
        # Dimensiones de ventana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.6)  
        window_height = int(screen_height * 0.9)  

        self.atleta_form_window.geometry(f"{window_width}x{window_height}")
        self.atleta_form_window.resizable(True, True)
        self.atleta_form_window.transient(self.root)
        self.atleta_form_window.grab_set()
        
        self.atleta_form_window.geometry("+%d+%d" % (
            (screen_width - window_width) // 2,
            (screen_height - window_height) // 2
        ))
        
        # Canvas con Scrollbar
        main_canvas = tk.Canvas(self.atleta_form_window, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.atleta_form_window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Contenido del Formulario
        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text=f"{'➕ REGISTRAR' if modo == 'registrar' else '✏️ EDITAR'} ATLETA",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.pack(pady=(0, 30))
        
        self.atleta_form_vars = {
            'nombre': tk.StringVar(), 'apellido': tk.StringVar(), 'cedula': tk.StringVar(),
            'edad': tk.StringVar(), 'telefono': tk.StringVar(), 'direccion': tk.StringVar(),
            'email': tk.StringVar(), 'peso': tk.StringVar(), 'fecha_nacimiento': tk.StringVar(),
            'meta_largo_plazo': tk.StringVar(), 'valoracion_especiales': tk.StringVar(),
            'id_plan': tk.StringVar(), 'metodo_pago': tk.StringVar(value='efectivo')
        }
        
        # ******** CORRECCIÓN DE ORDEN ********
        
        self.crear_seccion_datos_personales_atleta(main_frame)
        self.crear_seccion_datos_fisicos_atleta(main_frame)
        
        if modo == 'registrar':
            self.crear_seccion_plan_pago_atleta(main_frame)

        self.crear_botones_atleta_form(main_frame, modo)

        if modo == 'editar' and atleta:
            self.cargar_datos_atleta_form(atleta)
        
        # Empaquetar y configurar scroll
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            main_canvas.unbind_all("<MouseWheel>")
        
        main_canvas.bind('<Enter>', _bind_to_mousewheel)
        main_canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        def _configure_canvas_width(event):
            canvas_width = event.width
            main_canvas.itemconfig(main_canvas.find_all()[0], width=canvas_width)
        
        main_canvas.bind('<Configure>', _configure_canvas_width)

        
        # ==================== EMPAQUETAR CANVAS Y SCROLLBAR ====================
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ==================== CONFIGURAR SCROLL CON MOUSE ====================
        
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            main_canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel cuando el mouse está sobre la ventana
        main_canvas.bind('<Enter>', _bind_to_mousewheel)
        main_canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # También configurar scroll con teclas
        def _on_key_scroll(event):
            if event.keysym == 'Up':
                main_canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                main_canvas.yview_scroll(1, "units")
            elif event.keysym == 'Prior':  # Page Up
                main_canvas.yview_scroll(-10, "units")
            elif event.keysym == 'Next':   # Page Down
                main_canvas.yview_scroll(10, "units")
        
        self.atleta_form_window.bind('<Key>', _on_key_scroll)
        self.atleta_form_window.focus_set()
        
        # ==================== CONFIGURAR ANCHO DEL CANVAS ====================
        
        def _configure_canvas_width(event):
            canvas_width = event.width
            main_canvas.itemconfig(main_canvas.find_all()[0], width=canvas_width)
        
        main_canvas.bind('<Configure>', _configure_canvas_width)
        
        # ==================== FOCUS INICIAL ====================
        
        # Dar focus al primer campo después de un delay
        def set_initial_focus():
            try:
                # Buscar el primer Entry widget y darle focus
                for widget in main_frame.winfo_children():
                    if isinstance(widget, ttk.LabelFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Entry):
                                child.focus_set()
                                return
            except:
                pass
        
        self.atleta_form_window.after(100, set_initial_focus)
        
    def cargar_datos_atleta_form(self, atleta_completo):
        """Carga los datos de un atleta existente en las variables del formulario de edición."""
        try:
            atleta_data = atleta_completo['atleta_data']
            usuario_data = atleta_completo['usuario_data']
            
            # Cargar datos personales
            self.atleta_form_vars['nombre'].set(usuario_data[1])
            self.atleta_form_vars['apellido'].set(usuario_data[2])
            self.atleta_form_vars['cedula'].set(atleta_data[2] if len(atleta_data) > 2 else '')
            self.atleta_form_vars['edad'].set(usuario_data[3] if len(usuario_data) > 3 and usuario_data[3] else '')
            self.atleta_form_vars['telefono'].set(usuario_data[5] if len(usuario_data) > 5 and usuario_data[5] else '')
            self.atleta_form_vars['email'].set(usuario_data[6] if len(usuario_data) > 6 else '')
            
            # Cargar datos en los widgets de texto (importante limpiar antes)
            self.direccion_text_atleta.delete('1.0', tk.END)
            self.direccion_text_atleta.insert('1.0', usuario_data[4] if len(usuario_data) > 4 and usuario_data[4] else '')
            
            # Cargar datos deportivos
            self.atleta_form_vars['peso'].set(atleta_data[3] if len(atleta_data) > 3 and atleta_data[3] else '')
            self.atleta_form_vars['fecha_nacimiento'].set(str(atleta_data[4]) if len(atleta_data) > 4 and atleta_data[4] else '')
            
            self.meta_text_atleta.delete('1.0', tk.END)
            self.meta_text_atleta.insert('1.0', atleta_data[7] if len(atleta_data) > 7 and atleta_data[7] else '')
            
            self.valoracion_text_atleta.delete('1.0', tk.END)
            self.valoracion_text_atleta.insert('1.0', atleta_data[8] if len(atleta_data) > 8 and atleta_data[8] else '')

        except IndexError as ie:
            messagebox.showerror("Error de Datos", f"No se pudieron cargar todos los datos del atleta. Estructura de datos incompleta. {ie}")
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error al cargar el formulario: {e}")

    def crear_botones_atleta_form(self, parent, modo):
        """Crea los botones del formulario de atleta"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=(30, 0))
        
        # Botón cancelar
        cancel_btn = ttk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=self.atleta_form_window.destroy
        )
        cancel_btn.pack(side='right', padx=(5, 0))
        
        # Botón guardar
        save_text = "💾 Registrar Atleta" if modo == 'registrar' else "💾 Guardar Cambios"
        save_btn = ttk.Button(
            buttons_frame,
            text=save_text,
            command=lambda: self.guardar_atleta_form(modo)
        )
        save_btn.pack(side='right')

    def crear_seccion_datos_personales_atleta(self, parent):
        """Crea la sección de datos personales del atleta"""
        seccion_frame = ttk.LabelFrame(parent, text="👤 DATOS PERSONALES", padding=15)
        seccion_frame.pack(fill='x', pady=(0, 20))
        
        # Grid 2x3 para campos básicos
        campos_basicos = [
            ('Nombre *', 'nombre', 0, 0),
            ('Apellido *', 'apellido', 0, 2),
            ('Cédula *', 'cedula', 1, 0),
            ('Edad', 'edad', 1, 2),
            ('Teléfono', 'telefono', 2, 0),
        ]
        
        for label_text, var_name, row, col in campos_basicos:
            ttk.Label(seccion_frame, text=label_text).grid(
                row=row, column=col, sticky='w', padx=(0, 10), pady=5
            )
            ttk.Entry(seccion_frame, textvariable=self.atleta_form_vars[var_name], width=20).grid(
                row=row, column=col+1, sticky='ew', padx=(0, 20), pady=5
            )
        
        # Email para contacto (una sola línea)
        ttk.Label(seccion_frame, text="Email (contacto)").grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Entry(seccion_frame, textvariable=self.atleta_form_vars['email'], width=40).grid(
            row=3, column=1, columnspan=3, sticky='ew', pady=5
        )
        
        # Dirección (área de texto)
        ttk.Label(seccion_frame, text="Dirección").grid(row=4, column=0, sticky='nw', padx=(0, 10), pady=(10, 5))
        self.direccion_text_atleta = tk.Text(seccion_frame, height=2, width=50)
        self.direccion_text_atleta.grid(row=4, column=1, columnspan=3, sticky='ew', pady=(10, 5))
        
        # Configurar expansión de columnas
        seccion_frame.grid_columnconfigure(1, weight=1)
        seccion_frame.grid_columnconfigure(3, weight=1)

    def crear_seccion_datos_fisicos_atleta(self, parent):
        """Crea la sección de datos físicos y deportivos del atleta"""
        seccion_frame = ttk.LabelFrame(parent, text="🏃‍♂️ DATOS DEPORTIVOS", padding=15)
        seccion_frame.pack(fill='x', pady=(0, 20))
        
        # Primera fila: Peso y Fecha de nacimiento
        ttk.Label(seccion_frame, text="Peso (kg)").grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Entry(seccion_frame, textvariable=self.atleta_form_vars['peso'], width=15).grid(
            row=0, column=1, sticky='w', pady=5
        )
        
        ttk.Label(seccion_frame, text="Fecha Nacimiento").grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        date_frame = ttk.Frame(seccion_frame)
        date_frame.grid(row=0, column=3, sticky='w', pady=5)
        ttk.Entry(date_frame, textvariable=self.atleta_form_vars['fecha_nacimiento'], width=15).pack(side='left')
        ttk.Label(date_frame, text="(YYYY-MM-DD)", font=('Segoe UI', 8)).pack(side='left', padx=(5, 0))
        
        # Meta a largo plazo
        ttk.Label(seccion_frame, text="Meta Largo Plazo").grid(row=1, column=0, sticky='nw', padx=(0, 10), pady=(15, 5))
        self.meta_text_atleta = tk.Text(seccion_frame, height=3, width=60)
        self.meta_text_atleta.grid(row=1, column=1, columnspan=3, sticky='ew', pady=(15, 5))
        
        # Valoración especial / Observaciones médicas
        ttk.Label(seccion_frame, text="Observaciones Médicas").grid(row=2, column=0, sticky='nw', padx=(0, 10), pady=(15, 5))
        self.valoracion_text_atleta = tk.Text(seccion_frame, height=3, width=60)
        self.valoracion_text_atleta.grid(row=2, column=1, columnspan=3, sticky='ew', pady=(15, 5))
        
        seccion_frame.grid_columnconfigure(1, weight=1)
        seccion_frame.grid_columnconfigure(3, weight=1)

    def crear_seccion_plan_pago_atleta(self, parent):
        """Crea la sección de plan y pago para atletas"""
        seccion_frame = ttk.LabelFrame(parent, text="💰 PLAN DE MEMBRESÍA", padding=15)
        seccion_frame.pack(fill='x', pady=(0, 20))
        
        # Plan de membresía
        ttk.Label(seccion_frame, text="Plan de Membresía *").grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        plan_combo = ttk.Combobox(
            seccion_frame,
            textvariable=self.atleta_form_vars['id_plan'],
            values=[
                "1 - Plan Básico ($25.00)",
                "2 - Plan Premium ($40.00)", 
                "3 - Plan VIP ($65.00)",
                "4 - Plan Semanal ($12.00)",
                "5 - Plan Estudiantil ($20.00)"
            ],
            state="readonly",
            width=35
        )
        plan_combo.grid(row=0, column=1, sticky='w', pady=5)
        
        # Método de pago
        ttk.Label(seccion_frame, text="Método de Pago *").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        metodo_combo = ttk.Combobox(
            seccion_frame,
            textvariable=self.atleta_form_vars['metodo_pago'],
            values=["efectivo", "tarjeta", "transferencia"],
            state="readonly",
            width=20
        )
        metodo_combo.grid(row=1, column=1, sticky='w', pady=5)
        
        # Nota informativa
        nota_label = ttk.Label(
            seccion_frame,
            text="💡 El pago inicial se procesará automáticamente al registrar el atleta",
            font=('Segoe UI', 9),
            foreground='gray'
        )
        nota_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=(15, 0))

    def guardar_atleta_form(self, modo):
        """Guarda el atleta (SIMPLIFICADO - solo datos de atleta)"""
        try:
            # Validar campos requeridos
            if not self.validar_formulario_atleta_simple():
                return
            
            # Recoger SOLO datos del atleta
            datos_atleta = {
                'nombre': self.atleta_form_vars['nombre'].get().strip(),
                'apellido': self.atleta_form_vars['apellido'].get().strip(),
                'cedula': self.atleta_form_vars['cedula'].get().strip(),
                'email': self.atleta_form_vars['email'].get().strip(),
                'telefono': self.atleta_form_vars['telefono'].get().strip(),
                'direccion': self.direccion_text_atleta.get('1.0', 'end-1c').strip(),
            }
            
            # Datos opcionales con conversión de tipos
            if self.atleta_form_vars['edad'].get().strip():
                try:
                    datos_atleta['edad'] = int(self.atleta_form_vars['edad'].get())
                except ValueError:
                    messagebox.showerror("Error", "La edad debe ser un número")
                    return
            
            if self.atleta_form_vars['peso'].get().strip():
                try:
                    datos_atleta['peso'] = float(self.atleta_form_vars['peso'].get())
                except ValueError:
                    messagebox.showerror("Error", "El peso debe ser un número")
                    return
            
            if self.atleta_form_vars['fecha_nacimiento'].get().strip():
                datos_atleta['fecha_nacimiento'] = self.atleta_form_vars['fecha_nacimiento'].get().strip()
            
            # Campos de texto
            datos_atleta['meta_largo_plazo'] = self.meta_text_atleta.get('1.0', 'end-1c').strip()
            datos_atleta['valoracion_especiales'] = self.valoracion_text_atleta.get('1.0', 'end-1c').strip()
            
            if modo == 'registrar':
                # Extraer ID del plan
                plan_seleccionado = self.atleta_form_vars['id_plan'].get()
                if not plan_seleccionado:
                    messagebox.showerror("Error", "Selecciona un plan de membresía")
                    return
                
                try:
                    datos_atleta['id_plan'] = int(plan_seleccionado.split(' - ')[0])
                except (ValueError, IndexError):
                    messagebox.showerror("Error", "Plan inválido seleccionado")
                    return
                
                metodo_pago = self.atleta_form_vars['metodo_pago'].get()
                
                resultado = self.atleta_controller.registrar_atleta_completo(
                        datos_atleta=datos_atleta,
                        metodo_pago=metodo_pago,
                        registrado_por_id=self.usuario_actual['id']
                )
                
            else:
                # Editar atleta existente
                resultado = self.atleta_controller.actualizar_perfil_atleta(
                    atleta_id=self.atleta_seleccionado['atleta_data'][0],
                    datos_atleta=datos_atleta,
                    actualizado_por_id=self.usuario_actual['id']
                )
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['message'])
                self.atleta_form_window.destroy()
                self.cargar_atletas()
            else:
                messagebox.showerror("Error", resultado['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar atleta:\n{e}")

    def validar_formulario_atleta_simple(self):
        """Valida los campos requeridos del formulario simplificado"""
        # Solo campos básicos requeridos
        requeridos = ['nombre', 'apellido', 'cedula']
        
        for campo in requeridos:
            if not self.atleta_form_vars[campo].get().strip():
                messagebox.showerror("Error", f"El campo {campo} es requerido")
                return False
        
        # Validar email si se proporciona
        email = self.atleta_form_vars['email'].get().strip()
        if email and '@' not in email:
            messagebox.showerror("Error", "Email inválido")
            return False
        
        # Validar fecha de nacimiento si se proporciona
        fecha_nac = self.atleta_form_vars['fecha_nacimiento'].get().strip()
        if fecha_nac:
            try:
                from datetime import datetime
                datetime.strptime(fecha_nac, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Fecha de nacimiento inválida. Usa formato YYYY-MM-DD")
                return False
        
        return True


    # ==================== GESTION DE COACHES ====================

    def abrir_gestion_coaches(self):
        """Abre la gestión de coaches"""
        if not self.verificar_permisos(['admin_principal', 'secretaria']):
            return
        
        self.activar_boton_menu(self.botones_menu[2])

        self.mostrar_gestion_coaches()

    def mostrar_gestion_coaches(self):
        """Muestra el módulo completo de gestión de coaches"""
        self.limpiar_area_trabajo()
        
        # Variables para el módulo
        self.coaches_data = []
        self.coach_seleccionado = None
        
        # Título del módulo
        title_frame = ttk.Frame(self.work_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="👨‍🏫 GESTIÓN PROFESIONAL DE COACHES",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(side='left')
        
        # Botón de actualizar
        refresh_btn = ttk.Button(
            title_frame,
            text="🔄 Actualizar",
            command=self.cargar_coaches
        )
        refresh_btn.pack(side='right')
        
        # Frame de controles
        controls_frame = ttk.Frame(self.work_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Búsqueda simple
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side='left', padx=(0, 5))
        
        self.search_coaches_var = tk.StringVar()
        self.search_coaches_entry = ttk.Entry(search_frame, textvariable=self.search_coaches_var, width=25)
        self.search_coaches_entry.pack(side='left', padx=(0, 10))
        self.search_coaches_var.trace('w', self.filtrar_coaches)
        
        # Botones de acción AJUSTADOS
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side='right')
        
        self.edit_coach_btn = ttk.Button(
            buttons_frame,
            text="✏️ Editar Perfil",
            command=self.editar_perfil_coach,
            state='disabled'
        )
        self.edit_coach_btn.pack(side='left', padx=2)
        
        self.asignaciones_btn = ttk.Button(
            buttons_frame,
            text="👥 Gestionar Asignaciones",
            command=self.gestionar_asignaciones_coach,
            state='disabled'
        )
        self.asignaciones_btn.pack(side='left', padx=2)
        
        self.estadisticas_btn = ttk.Button(
            buttons_frame,
            text="📊 Ver Estadísticas",
            command=self.ver_estadisticas_coach,
            state='disabled'
        )
        self.estadisticas_btn.pack(side='left', padx=2)
        
        # Tabla de coaches (sin cambios)
        self.crear_tabla_coaches()
        
        # Cargar datos iniciales
        self.cargar_coaches()

    def on_coach_selected(self, event):
        """Maneja la selección de coach en la tabla"""
        selection = self.coaches_tree.selection()
        if selection:
            # Habilitar botones
            self.edit_coach_btn.config(state='normal')
            self.asignaciones_btn.config(state='normal')
            self.estadisticas_btn.config(state='normal')
            
            # Obtener coach seleccionado
            item = self.coaches_tree.item(selection[0])
            coach_id = item['values'][0]
            
            # Buscar coach completo en los datos
            for coach_completo in self.coaches_data:
                if coach_completo['coach_data'][0] == coach_id:
                    self.coach_seleccionado = coach_completo
                    break
        else:
            # Deshabilitar botones
            self.edit_coach_btn.config(state='disabled')
            self.asignaciones_btn.config(state='disabled')
            self.estadisticas_btn.config(state='disabled')
            self.coach_seleccionado = None

    def editar_perfil_coach(self):
        """Abre formulario para editar SOLO datos profesionales del coach"""
        if not self.coach_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un coach para editar")
            return
        
        # Crear ventana modal
        self.coach_edit_window = tk.Toplevel(self.root)
        self.coach_edit_window.title("Editar Perfil Profesional")
        self.coach_edit_window.geometry("450x400")
        self.coach_edit_window.resizable(False, False)
        self.coach_edit_window.transient(self.root)
        self.coach_edit_window.grab_set()
        
        # Centrar ventana
        x = (self.coach_edit_window.winfo_screenwidth() // 2) - 225
        y = (self.coach_edit_window.winfo_screenheight() // 2) - 200
        self.coach_edit_window.geometry(f"450x400+{x}+{y}")
        
        main_frame = ttk.Frame(self.coach_edit_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        coach_data = self.coach_seleccionado['coach_data']
        usuario_data = self.coach_seleccionado['usuario_data']
        
        # Título con nombre del coach
        title_label = ttk.Label(
            main_frame,
            text=f"✏️ PERFIL PROFESIONAL\n{usuario_data[1]} {usuario_data[2]}",
            font=('Segoe UI', 14, 'bold'),
            justify='center'
        )
        title_label.pack(pady=(0, 20))
        
        # Variables del formulario
        self.edit_coach_vars = {
            'especialidades': tk.StringVar(value=coach_data[2] if coach_data[2] else ''),
            'horario_disponible': tk.StringVar(value=coach_data[3] if coach_data[3] else ''),
            'salario': tk.StringVar(value=str(coach_data[5]) if coach_data[5] else ''),
            'fecha_contratacion': tk.StringVar(value=str(coach_data[4]) if coach_data[4] else '')
        }
        
        # Campos del formulario
        fields_frame = ttk.LabelFrame(main_frame, text="Datos Profesionales", padding=15)
        fields_frame.pack(fill='x', pady=(0, 20))
        
        # Especialidades
        ttk.Label(fields_frame, text="Especialidades:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(fields_frame, textvariable=self.edit_coach_vars['especialidades'], width=35).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Horario disponible
        ttk.Label(fields_frame, text="Horario Disponible:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(fields_frame, textvariable=self.edit_coach_vars['horario_disponible'], width=35).grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Salario
        ttk.Label(fields_frame, text="Salario:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(fields_frame, textvariable=self.edit_coach_vars['salario'], width=35).grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Fecha de contratación
        ttk.Label(fields_frame, text="Fecha Contratación:").grid(row=3, column=0, sticky='w', pady=5)
        fecha_frame = ttk.Frame(fields_frame)
        fecha_frame.grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=5)
        ttk.Entry(fecha_frame, textvariable=self.edit_coach_vars['fecha_contratacion'], width=25).pack(side='left')
        ttk.Label(fecha_frame, text="(YYYY-MM-DD)", font=('Segoe UI', 8)).pack(side='left', padx=(5, 0))
        
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        ttk.Button(buttons_frame, text="❌ Cancelar", command=self.coach_edit_window.destroy).pack(side='right', padx=(5, 0))
        ttk.Button(buttons_frame, text="💾 Guardar Cambios", command=self.guardar_perfil_coach).pack(side='right')

    def guardar_perfil_coach(self):
        """Guarda los cambios del perfil profesional"""
        try:
            datos_coach = {
                'especialidades': self.edit_coach_vars['especialidades'].get().strip(),
                'horario_disponible': self.edit_coach_vars['horario_disponible'].get().strip(),
                'fecha_contratacion': self.edit_coach_vars['fecha_contratacion'].get().strip(),
                'salario': self.edit_coach_vars['salario'].get().strip()
            }
            
            # Validar salario
            if datos_coach['salario']:
                try:
                    datos_coach['salario'] = float(datos_coach['salario'])
                except ValueError:
                    messagebox.showerror("Error", "El salario debe ser un número válido")
                    return
            
            # Validar fecha
            if datos_coach['fecha_contratacion']:
                try:
                    from datetime import datetime
                    datetime.strptime(datos_coach['fecha_contratacion'], '%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "Fecha inválida. Usa formato YYYY-MM-DD")
                    return
            
            coach_id = self.coach_seleccionado['coach_data'][0]
            resultado = self.coach_controller.actualizar_perfil_coach(
                coach_id, datos_coach, self.usuario_actual['id']
            )
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['message'])
                self.coach_edit_window.destroy()
                self.cargar_coaches()
            else:
                messagebox.showerror("Error", resultado['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")

    def gestionar_asignaciones_coach(self):
        """Gestiona asignaciones del coach seleccionado"""
        if not self.coach_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un coach")
            return
        
        coach_data = self.coach_seleccionado['coach_data']
        usuario_data = self.coach_seleccionado['usuario_data']
        coach_id = coach_data[0]
        
        # Ventana de gestión de asignaciones
        asign_window = tk.Toplevel(self.root)
        asign_window.title(f"Gestionar Asignaciones - {usuario_data[1]} {usuario_data[2]}")
        asign_window.geometry("1200x600")
        asign_window.transient(self.root)
        
        main_frame = ttk.Frame(asign_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(main_frame, 
                text=f"👥 ASIGNACIONES DE {usuario_data[1]} {usuario_data[2]}", 
                font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        
        resultado = self._obtener_atletas_por_coach_directo(coach_id)        
        
        if resultado["success"]:
            atletas = resultado["atletas"]
            
            if atletas:
                # Lista de atletas asignados
                atletas_frame = ttk.LabelFrame(main_frame, text="Atletas Asignados", padding=15)
                atletas_frame.pack(fill='both', expand=True, pady=(0, 15))
                
                # Crear treeview para atletas
                columns = ('Atleta', 'Email', 'Cédula', 'Fecha Inscripción', 'Metas', 'Valoraciones', 'Solvencia', 'Estado')
                atletas_tree = ttk.Treeview(atletas_frame, columns=columns, show='headings', height=10)
                
                column_configs = {
                    'Atleta': 130,
                    'Email': 150,
                    'Cédula': 80,
                    'Fecha Inscripción': 100,
                    'Metas': 200,
                    'Valoraciones': 150,
                    'Solvencia': 80,
                    'Estado': 80
                }
                

                for col, width in column_configs.items():
                    atletas_tree.heading(col, text=col)
                    atletas_tree.column(col, width=width)
                
                for atleta in atletas:
                    estado = "🟢 Activo" if atleta['estado_activo'] else "🔴 Finalizado"
                    solvencia = "💚 Solvente" if atleta['estado_solvencia'] == 'solvente' else "⚠️ Vencido"
                    
                    atletas_tree.insert('', 'end', values=(
                        atleta['nombre_completo'],
                        atleta['email'],
                        atleta['cedula'],
                        atleta['fecha_inscripcion'],
                        atleta['meta_largo_plazo'][:50] + "..." if len(str(atleta['meta_largo_plazo'])) > 50 else atleta['meta_largo_plazo'],
                        atleta['valoracion_especiales'][:40] + "..." if len(str(atleta['valoracion_especiales'])) > 40 else atleta['valoracion_especiales'],
                        solvencia,
                        estado
                    ))
                
                atletas_tree.pack(fill='both', expand=True)
            else:
                ttk.Label(main_frame, text="👤 No tiene atletas asignados actualmente", 
                        font=('Segoe UI', 12)).pack(pady=30)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=asign_window.destroy).pack(pady=15)

    def ver_estadisticas_coach(self):
        """Muestra estadísticas del coach seleccionado"""
        if not self.coach_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un coach")
            return
        
        coach_data = self.coach_seleccionado['coach_data']
        usuario_data = self.coach_seleccionado['usuario_data']
        coach_id = coach_data[0]
        
        resultado = self._generar_reporte_coach_directo(coach_id)
        
        if resultado["success"]:
            reporte = resultado["reporte"]
            stats = reporte["estadisticas"]
            
            # Ventana de estadísticas
            stats_window = tk.Toplevel(self.root)
            stats_window.title(f"Estadísticas - {usuario_data[1]} {usuario_data[2]}")
            stats_window.geometry("500x400")
            stats_window.transient(self.root)
            
            main_frame = ttk.Frame(stats_window, padding=20)
            main_frame.pack(fill='both', expand=True)
            
            # Título
            ttk.Label(main_frame, 
                    text=f"📊 ESTADÍSTICAS\n{usuario_data[1]} {usuario_data[2]}", 
                    font=('Segoe UI', 14, 'bold'),
                    justify='center').pack(pady=(0, 20))
            
            # Frame de estadísticas
            stats_frame = ttk.LabelFrame(main_frame, text="Resumen de Rendimiento", padding=15)
            stats_frame.pack(fill='x', pady=(0, 15))
            
            # Mostrar estadísticas
            estadisticas = [
                f"👥 Atletas Actuales: {stats['atletas_actuales']}",
                f"📈 Total Atletas Histórico: {stats['total_atletas_historico']}",
                f"⏱️ Tiempo Promedio por Atleta: {stats['tiempo_promedio_asignacion_dias']} días",
                f"💰 Salario: ${coach_data[5]:.2f}" if coach_data[5] else "💰 Salario: No especificado",
                f"🎯 Especialidades: {coach_data[2] if coach_data[2] else 'No especificado'}",
                f"📅 Contratado desde: {coach_data[4] if coach_data[4] else 'No especificado'}"
            ]
            
            for stat in estadisticas:
                ttk.Label(stats_frame, text=stat, font=('Segoe UI', 10)).pack(anchor='w', pady=2)
            
            # Botón cerrar
            ttk.Button(main_frame, text="Cerrar", command=stats_window.destroy).pack(pady=15)
            
        else:
            messagebox.showerror("Error", resultado["message"])

    def cargar_coaches(self):
        """Carga los coaches desde la base de datos"""
        try:
            print("🔄 Cargando coaches...")
            
            # Obtener coaches del controlador
            resultado = self.coach_controller.obtener_todos_coaches()
            if not resultado["success"]:
                messagebox.showerror("Error", resultado["message"])
                return
            
            self.coaches_data = resultado["coaches"]
            print(f"✅ Cargados {len(self.coaches_data)} coaches")
            
            # Actualizar tabla
            self.actualizar_tabla_coaches()
            
        except Exception as e:
            print(f"❌ Error cargando coaches: {e}")
            messagebox.showerror("Error", f"Error al cargar coaches:\n{e}")


    def _obtener_atletas_por_coach_directo(self, coach_id):
        """Obtiene atletas asignados a un coach específico"""
        try:
            from controllers.atleta_controller import AtletaController
            atleta_controller = AtletaController()
            
            resultado = atleta_controller.obtener_todos_atletas()
            if not resultado["success"]:
                return {"success": False, "atletas": []}
            
            atletas_del_coach = []
            
            for atleta_completo in resultado["atletas"]:
                atleta_data = atleta_completo['atleta_data']
                usuario_data = atleta_completo['usuario_data']
                
                coach_atleta_id = atleta_data[8] if len(atleta_data) > 8 else None
                
                if coach_atleta_id == coach_id:
                    atletas_del_coach.append({
                        'nombre_completo': f"{usuario_data[1]} {usuario_data[2]}",
                        'email': usuario_data[6],
                        'cedula': atleta_data[2] if len(atleta_data) > 2 else "N/A",
                        'fecha_inscripcion': atleta_data[5] if len(atleta_data) > 5 else "N/A",  # fecha_inscripcion (índice 5)
                        'meta_largo_plazo': atleta_data[9] if len(atleta_data) > 9 else "No especificada",
                        'valoracion_especiales': atleta_data[10] if len(atleta_data) > 10 else "No especificada",
                        'estado_solvencia': atleta_data[11] if len(atleta_data) > 11 else "N/A",
                        'estado_activo': True
                    })
            
            return {"success": True, "atletas": atletas_del_coach}
            
        except Exception as e:
            print(f"Error: {e}")
            return {"success": False, "atletas": []}

    def _generar_reporte_coach_directo(self, coach_id):
        """Genera reporte del coach usando datos directos"""
        try:
            # Contar atletas
            atletas_actuales = self.contar_atletas_asignados(coach_id)
            
            # Obtener info del coach
            coach_data = self.coach_seleccionado['coach_data']
            usuario_data = self.coach_seleccionado['usuario_data']
            
            reporte = {
                "estadisticas": {
                    "atletas_actuales": atletas_actuales,
                    "total_atletas_historico": atletas_actuales,  
                    "tiempo_promedio_asignacion_dias": 0  
                }
            }
            
            return {"success": True, "reporte": reporte}
            
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

    def crear_tabla_coaches(self):
        """Crea la tabla de coaches con Treeview"""
        # Frame para la tabla
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Configurar Treeview
        columns = ('ID', 'Nombre Completo', 'Email', 'Especialidades', 'Salario', 'Atletas Asignados', 'Fecha Contratación', 'Estado')
        self.coaches_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        for col in columns:
            self.coaches_tree.heading(col, text=col)
        
        # Configurar anchos
        self.coaches_tree.column('ID', width=50, anchor='center')
        self.coaches_tree.column('Nombre Completo', width=150)
        self.coaches_tree.column('Email', width=180)
        self.coaches_tree.column('Especialidades', width=150)
        self.coaches_tree.column('Salario', width=100, anchor='center')
        self.coaches_tree.column('Atletas Asignados', width=120, anchor='center')
        self.coaches_tree.column('Fecha Contratación', width=120, anchor='center')
        self.coaches_tree.column('Estado', width=80, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.coaches_tree.yview)
        self.coaches_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Empaquetar
        self.coaches_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
       
        
        # Eventos
        self.coaches_tree.bind('<<TreeviewSelect>>', self.on_coach_selected)

    def actualizar_tabla_coaches(self, coaches_filtrados=None):
        """Actualiza la tabla con los coaches"""
        for item in self.coaches_tree.get_children():
            self.coaches_tree.delete(item)
        
        coaches = coaches_filtrados if coaches_filtrados is not None else self.coaches_data
        
        for coach_completo in coaches:
            try:
                coach_data = coach_completo['coach_data']
                usuario_data = coach_completo['usuario_data']
                
                # Extraer datos
                coach_id = coach_data[0]
                nombre_completo = f"{usuario_data[1]} {usuario_data[2]}"
                email = usuario_data[6]
                especialidades = coach_data[2] if coach_data[2] else "No especificado"
                salario = f"${coach_data[5]:.2f}" if coach_data[5] else "$0.00"
                
                # Contar atletas asignados
                atletas_asignados = self.contar_atletas_asignados(coach_id)
                
                # Fecha de contratación
                try:
                    if coach_data[4]:
                        if isinstance(coach_data[4], str):
                            fecha_contratacion = coach_data[4][:10]
                        else:
                            fecha_contratacion = str(coach_data[4])[:10]
                    else:
                        fecha_contratacion = "N/A"
                except:
                    fecha_contratacion = "N/A"
                
                # Estado (basado en si el usuario está activo)
                estado = "🟢 Activo" if usuario_data[9] else "🔴 Inactivo"
                
                # Insertar fila
                self.coaches_tree.insert('', 'end', values=(
                    coach_id, nombre_completo, email, especialidades, salario, 
                    atletas_asignados, fecha_contratacion, estado
                ))
                    
            except Exception as e:
                print(f"Error procesando coach: {e}")
                continue

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
    
    def filtrar_coaches(self, *args):
        """Filtra coaches según búsqueda"""
        search_text = self.search_coaches_var.get().lower()
        
        if not search_text:
            self.actualizar_tabla_coaches()
            return
        
        coaches_filtrados = []
        
        for coach_completo in self.coaches_data:
            try:
                usuario_data = coach_completo['usuario_data']
                coach_data = coach_completo['coach_data']
                
                # Texto de búsqueda
                texto_busqueda = f"{usuario_data[1]} {usuario_data[2]} {usuario_data[6]} {coach_data[2] or ''}".lower()
                
                if search_text in texto_busqueda:
                    coaches_filtrados.append(coach_completo)
                    
            except Exception as e:
                print(f"Error filtrando coach: {e}")
                continue
        
        self.actualizar_tabla_coaches(coaches_filtrados)
    
    # ==================== GESTION DE PAGOS ====================       
        
    def abrir_gestion_pagos(self):
         """Abre la gestión de pagos"""
        # Se agrega la verificación de permisos y se indenta la línea siguiente
         if not self.verificar_permisos(['admin_principal', 'secretaria']):
            return
         
         self.activar_boton_menu(self.botones_menu[3])

         self.mostrar_gestion_pagos()

    def mostrar_gestion_pagos(self):
        """Muestra el módulo completo de gestión de pagos/ingresos"""
        self.limpiar_area_trabajo()
        
        self.pagos_data = []
        self.pago_seleccionado = None
        
        # Título del módulo
        title_frame = ttk.Frame(self.work_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="💰 GESTIÓN DE PAGOS",
            font=('Segoe UI', 18, 'bold')
        ).pack(side='left')
        
        ttk.Button(
            title_frame,
            text="🔄 Actualizar",
            command=self.cargar_pagos
        ).pack(side='right')
        
        # Frame de controles y filtros
        controls_frame = ttk.Frame(self.work_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        self.crear_filtros_pagos(controls_frame)
        
        # Tabla de pagos
        self.crear_tabla_pagos()
        
        # Cargar datos iniciales
        self.cargar_pagos()
        
    def crear_filtros_pagos(self, parent):
        """Crea los filtros para la gestión de pagos - VERSIÓN OPTIMIZADA"""
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill='x')

        # Búsqueda por texto
        ttk.Label(filter_frame, text="🔍 Buscar (Atleta/Desc):").pack(side='left', padx=(0, 5))
        self.search_pagos_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_pagos_var, width=20)
        search_entry.pack(side='left', padx=(0, 15))
        self.search_pagos_var.trace('w', self.filtrar_pagos)

        # Filtro por tipo de pago
        ttk.Label(filter_frame, text="Tipo Pago:").pack(side='left', padx=(0, 5))
        self.tipo_pago_filter_var = tk.StringVar(value="Todos")
        tipo_pago_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.tipo_pago_filter_var,
            values=["Todos", "Inscripcion", "Renovacion", "Servicio Extra"],
            state="readonly", width=15
        )
        tipo_pago_combo.pack(side='left', padx=(0, 15))
        tipo_pago_combo.bind('<<ComboboxSelected>>', self.filtrar_pagos)

        # REEMPLAZAR DateEntry por Entry simple
        ttk.Label(filter_frame, text="Desde:").pack(side='left', padx=(10, 5))
        self.fecha_desde_var = tk.StringVar()
        self.fecha_desde_entry = ttk.Entry(filter_frame, textvariable=self.fecha_desde_var, width=12)
        self.fecha_desde_entry.pack(side='left', padx=(0, 5))
        
        # Valor por defecto (hace 30 días)
        fecha_default = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.fecha_desde_var.set(fecha_default)
        
        ttk.Label(filter_frame, text="(YYYY-MM-DD)", font=('Segoe UI', 8)).pack(side='left', padx=(0, 10))

        ttk.Label(filter_frame, text="Hasta:").pack(side='left', padx=(0, 5))
        self.fecha_hasta_var = tk.StringVar()
        self.fecha_hasta_entry = ttk.Entry(filter_frame, textvariable=self.fecha_hasta_var, width=12)
        self.fecha_hasta_entry.pack(side='left', padx=(0, 5))
        
        # Valor por defecto (hoy)
        self.fecha_hasta_var.set(datetime.now().strftime('%Y-%m-%d'))
        
        ttk.Label(filter_frame, text="(YYYY-MM-DD)", font=('Segoe UI', 8)).pack(side='left', padx=(0, 10))

        ttk.Button(filter_frame, text="🔍 Aplicar Fechas", command=self.filtrar_pagos).pack(side='left', padx=(0,20))

        # Botones de Editar y Eliminar
        self.edit_pago_btn = ttk.Button(filter_frame, text="✏️ Editar Pago", command=self._editar_pago_action, state='disabled')
        self.edit_pago_btn.pack(side='left', padx=5)

        self.delete_pago_btn = ttk.Button(filter_frame, text="🗑️ Eliminar Pago", command=self._eliminar_pago_action, state='disabled')
        self.delete_pago_btn.pack(side='left', padx=5)
   
    def cargar_pagos(self):
        """Carga todos los pagos usando el controlador - VERSIÓN OPTIMIZADA"""
        try:
            # Mostrar indicador de carga
            self._mostrar_loading_pagos()
            
            # Usar after para no bloquear la UI
            self.root.after(50, self._cargar_pagos_async)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error crítico al cargar pagos: {e}")

    def crear_tabla_pagos(self):
        """Crea la tabla (Treeview) para mostrar los pagos"""
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        columns = ('ID', 'Fecha', 'Atleta', 'Plan', 'Monto', 'Tipo', 'Método', 'Procesado Por', 'Descripción')
        self.pagos_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        col_widths = {'ID': 60, 'Fecha': 100, 'Atleta': 180, 'Plan': 120, 'Monto': 80, 
                      'Tipo': 100, 'Método': 100, 'Procesado Por': 150, 'Descripción': 200}
        
        for col, width in col_widths.items():
            self.pagos_tree.heading(col, text=col)
            self.pagos_tree.column(col, width=width, anchor='w')
        
        self.pagos_tree.column('Monto', anchor='e')

        v_scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.pagos_tree.yview)
        self.pagos_tree.configure(yscrollcommand=v_scroll.set)
        
        self.pagos_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')

        self.pagos_tree.bind('<<TreeviewSelect>>', self.on_pago_selected)

    def _mostrar_loading_reporte(self):
        """Muestra loading en el reporte"""
        # Limpiar tabla
        self.reporte_detalles_tree.delete(*self.reporte_detalles_tree.get_children())
        
        # Mostrar loading
        self.reporte_detalles_tree.insert('', 'end', values=("🔄", "Generando reporte...", ""))
        
        # Actualizar labels
        self.resumen_ingresos_label.config(text="Total Ingresos: Calculando...")
        self.resumen_egresos_label.config(text="Total Egresos: Calculando...")
        self.resumen_balance_label.config(text="Balance: Calculando...")
   
    def _mostrar_loading_pagos(self):
        """Muestra indicador de carga en la tabla"""
        # Limpiar tabla
        for item in self.pagos_tree.get_children():
            self.pagos_tree.delete(item)
        
        # Mostrar mensaje de carga
        self.pagos_tree.insert('', 'end', values=("", "", "🔄 Cargando pagos...", "", "", "", "", "", ""))

    def _cargar_pagos_async(self):
        """Carga los pagos de forma asíncrona"""
        try:
            resultado = self.finance_controller.obtener_ingresos_detallados()
            if resultado['success']:
                self.pagos_data = resultado['ingresos']
                self.actualizar_tabla_pagos()
                print(f"✅ Cargados {len(self.pagos_data)} registros de pago.")
            else:
                # Limpiar tabla si hay error
                for item in self.pagos_tree.get_children():
                    self.pagos_tree.delete(item)
                messagebox.showerror("Error", f"No se pudieron cargar los pagos: {resultado['message']}")
        except Exception as e:
            # Limpiar tabla si hay error
            for item in self.pagos_tree.get_children():
                self.pagos_tree.delete(item)
            messagebox.showerror("Error", f"Error crítico al cargar pagos: {e}")

    def actualizar_tabla_pagos(self, pagos_filtrados=None):
        """Limpia y rellena la tabla de pagos con los datos proporcionados"""
        for item in self.pagos_tree.get_children():
            self.pagos_tree.delete(item)

        pagos_a_mostrar = pagos_filtrados if pagos_filtrados is not None else self.pagos_data

        for pago in pagos_a_mostrar:
            monto_formateado = f"${pago['monto']:.2f}"
            values = (
                pago['id_pago'],
                pago['fecha_pago'],
                pago['nombre_atleta'],
                pago['nombre_plan'],
                monto_formateado,
                pago['tipo_pago'],
                pago['metodo_pago'],
                pago['nombre_procesador'],
                pago['descripcion']
            )
            self.pagos_tree.insert('', 'end', values=values)
   
    def filtrar_pagos(self, *args):
        """Filtra los pagos según los criterios de búsqueda y filtros - VERSIÓN OPTIMIZADA"""
        search_text = self.search_pagos_var.get().lower()
        tipo_pago_filter = self.tipo_pago_filter_var.get()
        
        # Validación segura de fechas
        fecha_desde = None
        fecha_hasta = None
        
        try:
            fecha_desde_str = self.fecha_desde_var.get().strip()
            if fecha_desde_str:
                fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%d').date()
        except (ValueError, AttributeError):
            fecha_desde = None
        
        try:
            fecha_hasta_str = self.fecha_hasta_var.get().strip()
            if fecha_hasta_str:
                fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%d').date()
        except (ValueError, AttributeError):
            fecha_hasta = None

        pagos_filtrados = []
        for pago in self.pagos_data:
            # Filtro por fecha (solo si ambas fechas son válidas)
            if fecha_desde and fecha_hasta:
                try:
                    if not (fecha_desde <= pago['fecha_pago'] <= fecha_hasta):
                        continue
                except (TypeError, KeyError):
                    # Si hay problema con la fecha del pago, incluirlo
                    pass
            
            # Filtro por tipo de pago
            if tipo_pago_filter != "Todos":
                try:
                    if tipo_pago_filter.lower() not in pago['tipo_pago'].lower():
                        continue
                except (KeyError, AttributeError):
                    continue

            # Filtro por texto de búsqueda
            if search_text:
                try:
                    texto_busqueda = f"{pago['nombre_atleta']} {pago['descripcion']}".lower()
                    if search_text not in texto_busqueda:
                        continue
                except (KeyError, AttributeError):
                    continue

            pagos_filtrados.append(pago)
        
        self.actualizar_tabla_pagos(pagos_filtrados)

    def on_pago_selected(self, event):
        """Maneja la selección de un pago en la tabla y activa/desactiva botones."""
        selection = self.pagos_tree.selection()
        if selection:
            item = self.pagos_tree.item(selection[0])
            pago_id = item['values'][0]
            for pago in self.pagos_data:
                if pago['id_pago'] == pago_id:
                    self.pago_seleccionado = pago
                    # Activar botones
                    self.edit_pago_btn.config(state='normal')
                    self.delete_pago_btn.config(state='normal')
                    break
        else:
            self.pago_seleccionado = None
            # Desactivar botones
            self.edit_pago_btn.config(state='disabled')
            self.delete_pago_btn.config(state='disabled')
        
    def _eliminar_pago_action(self):
        """Función para el botón de eliminar pago."""
        if not self.pago_seleccionado:
            messagebox.showwarning("Acción Requerida", "Por favor, selecciona un pago de la lista para eliminar.")
            return

        pago_id = self.pago_seleccionado['id_pago']
        atleta = self.pago_seleccionado['nombre_atleta']
        monto = self.pago_seleccionado['monto']

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar el pago de ${monto:.2f} de {atleta} (ID: {pago_id})?\n\nEsta acción no se puede deshacer."
        )


        if confirmar:
            try:
                resultado = self.finance_controller.eliminar_ingreso(pago_id, self.usuario_actual['id'])
                if resultado['success']:
                    messagebox.showinfo("Éxito", resultado['message'])
                    self.cargar_pagos() # Recargar la lista de pagos
                else:
                    messagebox.showerror("Error", resultado['message'])
            except Exception as e:
                messagebox.showerror("Error Crítico", f"Ocurrió un error: {e}")

    def _editar_pago_action(self):
        """Función para el botón de editar pago. Abre un formulario."""
        if not self.pago_seleccionado:
            messagebox.showwarning("Acción Requerida", "Por favor, selecciona un pago de la lista para editar.")
            return

        # Crear la ventana del formulario
        self.pago_form_window = tk.Toplevel(self.root)
        self.pago_form_window.title("✏️ Editar Registro de Pago")
        self.pago_form_window.geometry("450x350")
        self.pago_form_window.transient(self.root)
        self.pago_form_window.grab_set()

        frame = ttk.Frame(self.pago_form_window, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Editar Pago", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        pago = self.pago_seleccionado
        
        # --- Campos del formulario ---
        form_fields = ttk.Frame(frame)
        form_fields.pack(fill='x')

        # Monto
        ttk.Label(form_fields, text="Monto:").grid(row=0, column=0, sticky='w', pady=5)
        self.monto_var = tk.StringVar(value=f"{pago['monto']:.2f}")
        ttk.Entry(form_fields, textvariable=self.monto_var, width=30).grid(row=0, column=1, sticky='ew', pady=5)

        # Método de pago
        ttk.Label(form_fields, text="Método de Pago:").grid(row=1, column=0, sticky='w', pady=5)
        self.metodo_var = tk.StringVar(value=pago['metodo_pago'].lower())
        ttk.Combobox(form_fields, textvariable=self.metodo_var, values=["efectivo", "tarjeta", "transferencia"], state='readonly').grid(row=1, column=1, sticky='ew', pady=5)
        
        # Descripción
        ttk.Label(form_fields, text="Descripción:").grid(row=2, column=0, sticky='w', pady=5)
        self.desc_var = tk.StringVar(value=pago['descripcion'])
        ttk.Entry(form_fields, textvariable=self.desc_var).grid(row=2, column=1, sticky='ew', pady=5)

        form_fields.grid_columnconfigure(1, weight=1)

        # --- Botones ---
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=(30, 0))

        ttk.Button(btn_frame, text="💾 Guardar Cambios", command=self._guardar_pago_editado_action).pack(side='right')
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.pago_form_window.destroy).pack(side='right', padx=10)

    def _guardar_pago_editado_action(self):
        """Recoge los datos del formulario de edición y los envía al controlador."""
        try:
            nuevo_monto = float(self.monto_var.get())
            if nuevo_monto <= 0:
                messagebox.showerror("Dato Inválido", "El monto debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Dato Inválido", "El monto debe ser un número válido.")
            return

        datos_actualizados = {
            'monto': nuevo_monto,
            'metodo_pago': self.metodo_var.get(),
            'descripcion': self.desc_var.get()
        }

        pago_id = self.pago_seleccionado['id_pago']
        resultado = self.finance_controller.actualizar_ingreso(pago_id, datos_actualizados, self.usuario_actual['id'])

        if resultado['success']:
            messagebox.showinfo("Éxito", resultado['message'])
            self.pago_form_window.destroy()
            self.cargar_pagos()
        else:
            messagebox.showerror("Error", resultado['message'])

    def abrir_reportes(self):
        """Abre la vista de Reportes Financieros."""
        if not self.verificar_permisos(['admin_principal', 'secretaria']):
            return
        
        self.activar_boton_menu(self.botones_menu[5])

        self.mostrar_reportes_financieros()

    def mostrar_reportes_financieros(self):
        """Crea y muestra la interfaz para el módulo de Reportes Financieros - VERSIÓN OPTIMIZADA"""
        self.limpiar_area_trabajo()

        # Título del módulo
        title_frame = ttk.Frame(self.work_frame)
        title_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(title_frame, text="📊 REPORTES FINANCIEROS", 
                font=('Segoe UI', 18, 'bold')).pack(side='left')

        # --- Frame de Filtros SIMPLIFICADO ---
        filter_frame = ttk.LabelFrame(self.work_frame, text="Período de Análisis", padding=10)
        filter_frame.pack(fill='x', pady=(0, 15))

        # Una sola fila para fechas
        dates_frame = ttk.Frame(filter_frame)
        dates_frame.pack()

        ttk.Label(dates_frame, text="Desde:").pack(side='left', padx=(0, 5))
        self.reporte_fecha_desde_var = tk.StringVar()
        self.reporte_fecha_desde_entry = ttk.Entry(dates_frame, textvariable=self.reporte_fecha_desde_var, width=12)
        self.reporte_fecha_desde_entry.pack(side='left', padx=(0, 20))
        
        # Valor por defecto
        self.reporte_fecha_desde_var.set((datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))

        ttk.Label(dates_frame, text="Hasta:").pack(side='left', padx=(0, 5))
        self.reporte_fecha_hasta_var = tk.StringVar()
        self.reporte_fecha_hasta_entry = ttk.Entry(dates_frame, textvariable=self.reporte_fecha_hasta_var, width=12)
        self.reporte_fecha_hasta_entry.pack(side='left', padx=(0, 20))
        
        # Valor por defecto
        self.reporte_fecha_hasta_var.set(datetime.now().strftime('%Y-%m-%d'))

        ttk.Button(dates_frame, text="📈 Generar Reporte", 
                command=self._generar_y_mostrar_reporte_action).pack(side='left', padx=(20, 0))

        ttk.Separator(self.work_frame, orient='horizontal').pack(fill='x', pady=10)

        # --- Frame de Resumen SIMPLIFICADO ---
        resumen_frame = ttk.LabelFrame(self.work_frame, text="Resumen del Período", padding=15)
        resumen_frame.pack(fill='x', pady=(0, 15))

        # Labels directos en lugar de StringVars
        self.resumen_ingresos_label = ttk.Label(resumen_frame, text="Total Ingresos: $0.00", 
                                            font=('Segoe UI', 12, 'bold'), foreground='green')
        self.resumen_ingresos_label.pack(side='left', padx=20)

        self.resumen_egresos_label = ttk.Label(resumen_frame, text="Total Egresos: $0.00", 
                                            font=('Segoe UI', 12, 'bold'), foreground='red')
        self.resumen_egresos_label.pack(side='left', padx=20)

        self.resumen_balance_label = ttk.Label(resumen_frame, text="Balance: $0.00", 
                                            font=('Segoe UI', 14, 'bold'), foreground='blue')
        self.resumen_balance_label.pack(side='right', padx=20)

        # --- Frame de Detalles SIMPLIFICADO (Una sola tabla) ---
        details_frame = ttk.LabelFrame(self.work_frame, text="Desglose Detallado", padding=10)
        details_frame.pack(fill='both', expand=True, pady=10)

        # Una sola tabla para todo
        columns = ('Categoría', 'Tipo', 'Monto')
        self.reporte_detalles_tree = ttk.Treeview(details_frame, columns=columns, show='headings')
        
        for col in columns:
            self.reporte_detalles_tree.heading(col, text=col)
        
        self.reporte_detalles_tree.column('Categoría', width=120)
        self.reporte_detalles_tree.column('Tipo', width=200)
        self.reporte_detalles_tree.column('Monto', width=120, anchor='e')

        # Scrollbar
        scrollbar_detalles = ttk.Scrollbar(details_frame, orient='vertical', 
                                        command=self.reporte_detalles_tree.yview)
        self.reporte_detalles_tree.configure(yscrollcommand=scrollbar_detalles.set)

        self.reporte_detalles_tree.pack(side='left', fill='both', expand=True)
        scrollbar_detalles.pack(side='right', fill='y')

        # Generar reporte inicial
        self._generar_y_mostrar_reporte_action()
    
    def _generar_y_mostrar_reporte_action(self):
        """Función que llama al controlador y actualiza la UI del reporte - VERSIÓN OPTIMIZADA"""
        
        # Validación de fechas
        try:
            fecha_inicio_str = self.reporte_fecha_desde_var.get().strip()
            fecha_fin_str = self.reporte_fecha_hasta_var.get().strip()
            
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            
            if fecha_inicio > fecha_fin:
                messagebox.showerror("Error de Fechas", "La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.")
                return
                
        except ValueError:
            messagebox.showerror("Error de Formato", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        self._mostrar_loading_reporte()
        
        self.root.after(50, lambda: self._ejecutar_reporte_async(fecha_inicio, fecha_fin))   

    def _ejecutar_reporte_async(self, fecha_inicio, fecha_fin):
        """Ejecuta el reporte de forma asíncrona"""
        try:
            resultado = self.finance_controller.generar_reporte_financiero(fecha_inicio, fecha_fin)

            if not resultado['success']:
                messagebox.showerror("Error al generar reporte", resultado['message'])
                return

            reporte = resultado['reporte']
            resumen = reporte['resumen']
            desglose_ingresos = reporte['desglose_ingresos']
            desglose_egresos = reporte['desglose_egresos']

            self.resumen_ingresos_label.config(text=f"Total Ingresos: ${resumen['total_ingresos']:.2f}")
            self.resumen_egresos_label.config(text=f"Total Egresos: ${resumen['total_egresos']:.2f}")
            
            balance_color = 'green' if resumen['balance'] >= 0 else 'red'
            self.resumen_balance_label.config(text=f"Balance: ${resumen['balance']:.2f}", 
                                            foreground=balance_color)

            self.reporte_detalles_tree.delete(*self.reporte_detalles_tree.get_children())
            
            for tipo, monto in desglose_ingresos.items():
                tipo_legible = tipo.replace('_', ' ').title()
                self.reporte_detalles_tree.insert('', 'end', values=("📈 INGRESO", tipo_legible, f"${monto:.2f}"))
            
            for tipo, monto in desglose_egresos.items():
                tipo_legible = tipo.replace('_', ' ').title()
                self.reporte_detalles_tree.insert('', 'end', values=("📉 EGRESO", tipo_legible, f"${monto:.2f}"))

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error al procesar el reporte: {e}")
            import traceback
            traceback.print_exc()
    
     # ==================== OTRA GESTION ====================       

    def mostrar_mis_atletas_coach(self):
        """Muestra la vista COMPLETA de atletas para coach - VERSIÓN FINAL"""
        self.limpiar_area_trabajo()
        
        # Variables para el módulo
        self.mis_atletas_data = []
        self.mi_atleta_seleccionado = None
        
        # PASO 1: Verificar que soy coach y obtener mi coach_id
        self.coach_actual_id = self._obtener_coach_id_usuario_actual()
        if not self.coach_actual_id:
            self._mostrar_error_no_coach()
            return
        
        print(f"✅ Coach ID: {self.coach_actual_id} - Cargando vista completa")
        
        # PASO 2: Título del módulo
        title_frame = ttk.Frame(self.work_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="👥 MIS ATLETAS ASIGNADOS",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(side='left')
        
        # Botón de actualizar
        refresh_btn = ttk.Button(
            title_frame,
            text="🔄 Actualizar",
            command=self.cargar_mis_atletas_completo
        )
        refresh_btn.pack(side='right')
        
        # PASO 3: Frame de controles (usar tu función existente)
        controls_frame = ttk.Frame(self.work_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Filtros (usar tu implementación)
        self.crear_filtros_mis_atletas(controls_frame)
        
        # Botones de acción (usar tu implementación)
        self.crear_botones_mis_atletas(controls_frame)
        
        # PASO 4: Tabla detallada (usar tu implementación)
        self.crear_tabla_mis_atletas()
        
        # PASO 5: Cargar datos iniciales
        self.cargar_mis_atletas_completo()

    def cargar_mis_atletas_completo(self):
        """Carga solo los atletas asignados al coach actual - VERSIÓN MEJORADA"""
        try:
            if not hasattr(self, 'coach_actual_id') or not self.coach_actual_id:
                messagebox.showerror("Error", "No se pudo identificar el coach")
                return
                
            print(f"🔄 Cargando atletas del coach ID: {self.coach_actual_id}")
            
            # Obtener todos los atletas y filtrar
            resultado = self.atleta_controller.obtener_todos_atletas()
            if not resultado["success"]:
                messagebox.showerror("Error", "No se pudieron cargar los atletas")
                return
            
            # Filtrar solo mis atletas
            self.mis_atletas_data = []
            
            for atleta_completo in resultado["atletas"]:
                atleta_data = atleta_completo['atleta_data']
                coach_atleta_id = atleta_data[8] if len(atleta_data) > 8 else None
                
                if coach_atleta_id == self.coach_actual_id:
                    self.mis_atletas_data.append(atleta_completo)
            
            print(f"✅ Cargados {len(self.mis_atletas_data)} atletas asignados")
            self.actualizar_tabla_mis_atletas()
            
        except Exception as e:
            print(f"❌ Error cargando mis atletas: {e}")
            messagebox.showerror("Error", f"Error al cargar atletas:\n{e}")



    def ver_progreso_atleta(self):
        """Muestra el progreso y estadísticas del atleta seleccionado"""
        if not self.mi_atleta_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un atleta")
            return
        
        atleta_data = self.mi_atleta_seleccionado['atleta_data']
        usuario_data = self.mi_atleta_seleccionado['usuario_data']
        
        # Ventana modal para mostrar progreso
        progreso_window = tk.Toplevel(self.root)
        progreso_window.title(f"Progreso de {usuario_data[1]} {usuario_data[2]}")
        progreso_window.geometry("700x600")
        progreso_window.transient(self.root)
        
        main_frame = ttk.Frame(progreso_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(main_frame, 
                text=f"📊 PROGRESO DE {usuario_data[1]} {usuario_data[2]}", 
                font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # Información básica de progreso
        info_frame = ttk.LabelFrame(main_frame, text="Información General", padding=15)
        info_frame.pack(fill='x', pady=(0, 15))
        
        # Calcular días en el gimnasio
        try:
            if len(atleta_data) > 5 and atleta_data[5]:  # fecha_inscripcion
                from datetime import datetime, date
                if isinstance(atleta_data[5], str):
                    fecha_inscripcion = datetime.strptime(atleta_data[5][:10], '%Y-%m-%d').date()
                else:
                    fecha_inscripcion = atleta_data[5]
                
                dias_en_gym = (date.today() - fecha_inscripcion).days
                
                # Fecha de vencimiento
                if len(atleta_data) > 6 and atleta_data[6]:
                    if isinstance(atleta_data[6], str):
                        fecha_venc = datetime.strptime(atleta_data[6][:10], '%Y-%m-%d').date()
                    else:
                        fecha_venc = atleta_data[6]
                    
                    dias_restantes = (fecha_venc - date.today()).days
                else:
                    dias_restantes = 0
            else:
                dias_en_gym = 0
                dias_restantes = 0
        except:
            dias_en_gym = 0
            dias_restantes = 0
        
        # Mostrar estadísticas básicas
        estadisticas_basicas = [
            f"📅 Días en el gimnasio: {dias_en_gym} días",
            f"⏰ Días restantes de membresía: {dias_restantes} días",
            f"💪 Peso actual: {atleta_data[3]} kg" if len(atleta_data) > 3 and atleta_data[3] else "💪 Peso: No registrado",
            f"🎯 Estado de solvencia: {atleta_data[11] if len(atleta_data) > 11 else 'No especificado'}",
            f"📋 Plan actual: Plan {atleta_data[7]}" if len(atleta_data) > 7 and atleta_data[7] else "📋 Plan: No asignado"
        ]
        
        for stat in estadisticas_basicas:
            ttk.Label(info_frame, text=stat, font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        
        # Metas y observaciones del atleta
        metas_frame = ttk.LabelFrame(main_frame, text="Metas y Seguimiento", padding=15)
        metas_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Meta a largo plazo
        ttk.Label(metas_frame, text="🎯 Meta a Largo Plazo:", font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        meta_text = tk.Text(metas_frame, height=3, wrap=tk.WORD, state='disabled')
        meta_text.pack(fill='x', pady=(5, 10))
        
        meta = atleta_data[9] if len(atleta_data) > 9 and atleta_data[9] else "No se ha establecido una meta específica"
        meta_text.config(state='normal')
        meta_text.insert('1.0', meta)
        meta_text.config(state='disabled')
        
        # Observaciones médicas/especiales
        ttk.Label(metas_frame, text="🩺 Observaciones Médicas:", font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        obs_text = tk.Text(metas_frame, height=3, wrap=tk.WORD, state='disabled')
        obs_text.pack(fill='x', pady=(5, 10))
        
        observaciones = atleta_data[10] if len(atleta_data) > 10 and atleta_data[10] else "Sin observaciones médicas especiales"
        obs_text.config(state='normal')
        obs_text.insert('1.0', observaciones)
        obs_text.config(state='disabled')
        
        # Sección para notas del coach (futura implementación)
        notas_frame = ttk.LabelFrame(main_frame, text="📝 Notas del Coach", padding=15)
        notas_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(notas_frame, 
                text="💡 Próximamente: Aquí podrás agregar y ver tus notas sobre el progreso del atleta", 
                font=('Segoe UI', 9), foreground='gray').pack()
        
        # Botones de acción
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')
        
        # Botón para agregar nota (futuro)
        ttk.Button(buttons_frame, 
                text="📝 Agregar Nota de Progreso", 
                state='disabled',
                command=lambda: messagebox.showinfo("Próximamente", "Función en desarrollo")).pack(side='left')
        
        ttk.Button(buttons_frame, text="Cerrar", command=progreso_window.destroy).pack(side='right')
    # ==================== MÉTODOS DE SOPORTE ====================

    def _obtener_coach_id_usuario_actual(self):
        """Obtiene el coach_id del usuario actual - VERSIÓN CON MÁS DEBUG"""
        try:
            print(f"🔍 DEBUG: Buscando coach_id para usuario: {self.usuario_actual['id']} ({self.usuario_actual['nombre']})")
            
            # Obtener coaches directamente del modelo
            coaches = self.coach_controller.coach_model.read_coaches()
            
            print(f"🔍 DEBUG: Total coaches en BD: {len(coaches) if coaches else 0}")
            
            if coaches:
                for coach in coaches:
                    coach_id = coach[0]      # id_coach
                    user_id = coach[1]       # id_usuario
                    
                    print(f"🔍 DEBUG: Coach {coach_id} -> Usuario {user_id}")
                    
                    if user_id == self.usuario_actual['id']:
                        print(f"✅ MATCH: Coach ID {coach_id} para usuario {user_id}")
                        return coach_id
            
            print(f"❌ NO MATCH: Usuario {self.usuario_actual['id']} no es coach o no está en la tabla coaches")
            return None
            
        except Exception as e:
            print(f"❌ ERROR en _obtener_coach_id_usuario_actual: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def cargar_mis_atletas(self):
        """Redirige al método principal"""
        self.mostrar_mis_atletas_coach()

    def _mostrar_error_no_coach(self):
        """Muestra error cuando no se puede encontrar el coach - MEJORADO"""
        error_frame = ttk.Frame(self.work_frame)
        error_frame.pack(expand=True)
        
        ttk.Label(error_frame, text="❌", font=('Segoe UI', 48)).pack(pady=(50, 20))
        
        ttk.Label(error_frame,
                text="Error de Acceso",
                font=('Segoe UI', 18, 'bold')).pack(pady=(0, 10))
        
        ttk.Label(error_frame,
                text="No se pudo encontrar tu perfil de coach en el sistema.\n\nPosibles causas:\n• Tu usuario no está registrado como coach\n• Hay un problema con la base de datos\n\nContacta al administrador para resolver este problema.",
                font=('Segoe UI', 12),
                justify='center').pack(pady=(0, 30))
        
        ttk.Button(error_frame,
                text="🏠 Volver al Dashboard",
                command=self.mostrar_dashboard_resumen).pack()

    def crear_filtros_mis_atletas(self, parent):
        """Crea filtros básicos de búsqueda (solo lectura)"""
        search_frame = ttk.Frame(parent)
        search_frame.pack(side='left', fill='x', expand=True)
        
        # Búsqueda por texto
        ttk.Label(search_frame, text="🔍 Buscar atleta:").pack(side='left', padx=(0, 5))
        
        self.search_mis_atletas_var = tk.StringVar()
        self.search_mis_atletas_entry = ttk.Entry(search_frame, textvariable=self.search_mis_atletas_var, width=25)
        self.search_mis_atletas_entry.pack(side='left', padx=(0, 10))
        self.search_mis_atletas_var.trace('w', self.filtrar_mis_atletas)
        
        # Filtro por estado de solvencia
        ttk.Label(search_frame, text="💰 Estado:").pack(side='left', padx=(10, 5))
        
        self.estado_mis_atletas_var = tk.StringVar(value="Todos")
        estado_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.estado_mis_atletas_var,
            values=["Todos", "solvente", "vencido", "suspendido"],
            state="readonly",
            width=12
        )
        estado_combo.pack(side='left')
        estado_combo.bind('<<ComboboxSelected>>', self.filtrar_mis_atletas)

    def crear_botones_mis_atletas(self, parent):
        """Crea botones de solo lectura para coach"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(side='right')
        
        # Solo botones de visualización, NO de edición
        self.ver_perfil_btn = ttk.Button(
            buttons_frame,
            text="👁️ Ver Perfil Completo",
            command=self.ver_perfil_atleta_completo,
            state='disabled'
        )
        self.ver_perfil_btn.pack(side='left', padx=2)
        
        self.ver_progreso_btn = ttk.Button(
            buttons_frame,
            text="📊 Ver Progreso",
            command=self.ver_progreso_atleta,
            state='disabled'
        )
        self.ver_progreso_btn.pack(side='left', padx=2)

    def crear_tabla_mis_atletas(self):
        """Crea la tabla de mis atletas (solo lectura)"""
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Configurar Treeview - columnas optimizadas para coach
        columns = ('Nombre', 'Apellido', 'Cédula', 'Email', 'Plan', 'Estado', 'Vencimiento', 'Días Restantes')
        self.mis_atletas_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        column_configs = {
            'Nombre': 120,
            'Apellido': 120, 
            'Cédula': 100,
            'Email': 180,
            'Plan': 100,
            'Estado': 100,
            'Vencimiento': 110,
            'Días Restantes': 120
        }
        
        for col, width in column_configs.items():
            self.mis_atletas_tree.heading(col, text=col)
            self.mis_atletas_tree.column(col, width=width, anchor='center' if col in ['Estado', 'Días Restantes'] else 'w')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.mis_atletas_tree.yview)
        self.mis_atletas_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Empaquetar
        self.mis_atletas_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        self.mis_atletas_tree.bind('<<TreeviewSelect>>', self.on_mi_atleta_selected)

    
    def actualizar_tabla_mis_atletas(self, atletas_filtrados=None):
        """Actualiza la tabla con mis atletas"""
        # Limpiar tabla
        for item in self.mis_atletas_tree.get_children():
            self.mis_atletas_tree.delete(item)
        
        # Usar atletas filtrados o todos
        atletas = atletas_filtrados if atletas_filtrados is not None else self.mis_atletas_data
        
        # Si no hay atletas, mostrar mensaje
        if not atletas:
            self.mis_atletas_tree.insert('', 'end', values=(
                "No tienes atletas", "asignados", "actualmente", "", "", "", "", ""
            ))
            return
        
        # Llenar tabla
        for atleta_completo in atletas:
            try:
                atleta_data = atleta_completo['atleta_data']
                usuario_data = atleta_completo['usuario_data']
                
                nombre = usuario_data[1]
                apellido = usuario_data[2]
                cedula = atleta_data[2] if len(atleta_data) > 2 else "N/A"
                email = usuario_data[6]
                
                # Obtener nombre del plan (simplificado)
                plan_id = atleta_data[7] if len(atleta_data) > 7 else None
                plan_nombre = f"Plan {plan_id}" if plan_id else "Sin Plan"
                
                # Estado de solvencia
                estado = atleta_data[11] if len(atleta_data) > 11 else "N/A"
                
                # Fecha de vencimiento y días restantes
                try:
                    if len(atleta_data) > 6 and atleta_data[6]:
                        from datetime import datetime, date
                        if isinstance(atleta_data[6], str):
                            fecha_venc = datetime.strptime(atleta_data[6][:10], '%Y-%m-%d').date()
                        else:
                            fecha_venc = atleta_data[6]
                        
                        # Calcular días restantes
                        dias_restantes = (fecha_venc - date.today()).days
                        vencimiento = str(fecha_venc)
                        
                        if dias_restantes < 0:
                            dias_texto = f"Vencido hace {abs(dias_restantes)} días"
                        elif dias_restantes == 0:
                            dias_texto = "Vence HOY"
                        else:
                            dias_texto = f"{dias_restantes} días"
                    else:
                        vencimiento = "N/A"
                        dias_texto = "N/A"
                except:
                    vencimiento = "N/A"
                    dias_texto = "N/A"
                
                # Insertar fila
                item = self.mis_atletas_tree.insert('', 'end', values=(
                    nombre, apellido, cedula, email, plan_nombre, estado, vencimiento, dias_texto
                ))
                
                # Colorear según estado
                if estado == 'vencido' or (dias_texto != "N/A" and "Vencido" in dias_texto):
                    self.mis_atletas_tree.set(item, 'Estado', '🔴 Vencido')
                elif estado == 'suspendido':
                    self.mis_atletas_tree.set(item, 'Estado', '⏸️ Suspendido')
                elif dias_texto != "N/A" and "Vence HOY" in dias_texto:
                    self.mis_atletas_tree.set(item, 'Estado', '⚠️ Vence Hoy')
                else:
                    self.mis_atletas_tree.set(item, 'Estado', '🟢 Solvente')
                    
            except Exception as e:
                print(f"Error procesando atleta: {e}")
                continue

    def filtrar_mis_atletas(self, *args):
        """Filtra mis atletas según búsqueda y estado"""
        search_text = self.search_mis_atletas_var.get().lower()
        estado_filter = self.estado_mis_atletas_var.get()
        
        if not search_text and estado_filter == "Todos":
            self.actualizar_tabla_mis_atletas()
            return
        
        atletas_filtrados = []
        
        for atleta_completo in self.mis_atletas_data:
            try:
                atleta_data = atleta_completo['atleta_data']
                usuario_data = atleta_completo['usuario_data']
                
                # Filtro de texto
                texto_busqueda = f"{usuario_data[1]} {usuario_data[2]} {atleta_data[2]} {usuario_data[6]}".lower()
                if search_text and search_text not in texto_busqueda:
                    continue
                
                # Filtro de estado
                if estado_filter != "Todos":
                    estado_atleta = atleta_data[11] if len(atleta_data) > 11 else "N/A"
                    if estado_atleta != estado_filter:
                        continue
                
                atletas_filtrados.append(atleta_completo)
                
            except Exception as e:
                print(f"Error filtrando atleta: {e}")
                continue
        
        self.actualizar_tabla_mis_atletas(atletas_filtrados)

    def on_mi_atleta_selected(self, event):
        """Maneja la selección de atleta en la tabla"""
        selection = self.mis_atletas_tree.selection()
        if selection:
            # Habilitar botones de solo lectura
            self.ver_perfil_btn.config(state='normal')
            self.ver_progreso_btn.config(state='normal')
            
            # Obtener atleta seleccionado
            item = self.mis_atletas_tree.item(selection[0])
            nombre_completo = f"{item['values'][0]} {item['values'][1]}"
            
            # Buscar atleta completo en los datos
            for atleta_completo in self.mis_atletas_data:
                usuario_data = atleta_completo['usuario_data']
                if f"{usuario_data[1]} {usuario_data[2]}" == nombre_completo:
                    self.mi_atleta_seleccionado = atleta_completo
                    break
        else:
            # Deshabilitar botones
            self.ver_perfil_btn.config(state='disabled')
            self.ver_progreso_btn.config(state='disabled')
            self.mi_atleta_seleccionado = None

    def ver_perfil_atleta_completo(self):
        """Muestra el perfil completo del atleta (solo lectura)"""
        if not self.mi_atleta_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un atleta")
            return
        
        atleta_data = self.mi_atleta_seleccionado['atleta_data']
        usuario_data = self.mi_atleta_seleccionado['usuario_data']
        
        # Ventana modal para mostrar perfil
        perfil_window = tk.Toplevel(self.root)
        perfil_window.title(f"Perfil de {usuario_data[1]} {usuario_data[2]}")
        perfil_window.geometry("600x700")
        perfil_window.transient(self.root)
        
        main_frame = ttk.Frame(perfil_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(main_frame, 
                text=f"👤 PERFIL DE {usuario_data[1]} {usuario_data[2]}", 
                font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # Datos personales
        personal_frame = ttk.LabelFrame(main_frame, text="Datos Personales", padding=15)
        personal_frame.pack(fill='x', pady=(0, 15))
        
        datos_personales = [
            ("Nombre Completo:", f"{usuario_data[1]} {usuario_data[2]}"),
            ("Cédula:", atleta_data[2] if len(atleta_data) > 2 else "No especificada"),
            ("Email:", usuario_data[6]),
            ("Teléfono:", usuario_data[5] if usuario_data[5] else "No especificado"),
            ("Dirección:", usuario_data[4] if usuario_data[4] else "No especificada"),
            ("Edad:", usuario_data[3] if usuario_data[3] else "No especificada"),
        ]
        
        for label, valor in datos_personales:
            info_frame = ttk.Frame(personal_frame)
            info_frame.pack(fill='x', pady=2)
            ttk.Label(info_frame, text=label, font=('Segoe UI', 10, 'bold')).pack(side='left')
            ttk.Label(info_frame, text=str(valor)).pack(side='left', padx=(10, 0))
        
        # Datos deportivos
        deportivo_frame = ttk.LabelFrame(main_frame, text="Información Deportiva", padding=15)
        deportivo_frame.pack(fill='x', pady=(0, 15))
        
        datos_deportivos = [
            ("Peso:", f"{atleta_data[3]} kg" if len(atleta_data) > 3 and atleta_data[3] else "No especificado"),
            ("Fecha Nacimiento:", str(atleta_data[4]) if len(atleta_data) > 4 and atleta_data[4] else "No especificada"),
            ("Fecha Inscripción:", str(atleta_data[5]) if len(atleta_data) > 5 and atleta_data[5] else "No especificada"),
            ("Estado Solvencia:", atleta_data[11] if len(atleta_data) > 11 else "No especificado"),
        ]
        
        for label, valor in datos_deportivos:
            info_frame = ttk.Frame(deportivo_frame)
            info_frame.pack(fill='x', pady=2)
            ttk.Label(info_frame, text=label, font=('Segoe UI', 10, 'bold')).pack(side='left')
            ttk.Label(info_frame, text=str(valor)).pack(side='left', padx=(10, 0))
        
        # Metas y observaciones
        metas_frame = ttk.LabelFrame(main_frame, text="Metas y Observaciones", padding=15)
        metas_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Meta a largo plazo
        ttk.Label(metas_frame, text="Meta a Largo Plazo:", font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        meta_text = tk.Text(metas_frame, height=3, wrap=tk.WORD, state='disabled')
        meta_text.pack(fill='x', pady=(5, 10))
        
        meta = atleta_data[9] if len(atleta_data) > 9 and atleta_data[9] else "No especificada"
        meta_text.config(state='normal')
        meta_text.insert('1.0', meta)
        meta_text.config(state='disabled')
        
        # Valoraciones especiales
        ttk.Label(metas_frame, text="Observaciones Médicas:", font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        obs_text = tk.Text(metas_frame, height=3, wrap=tk.WORD, state='disabled')
        obs_text.pack(fill='x', pady=(5, 0))
        
        observaciones = atleta_data[10] if len(atleta_data) > 10 and atleta_data[10] else "Ninguna"
        obs_text.config(state='normal')
        obs_text.insert('1.0', observaciones)
        obs_text.config(state='disabled')
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=perfil_window.destroy).pack(pady=15)
    
    def abrir_asignaciones(self):
        """Abre las asignaciones del coach"""
        self.mostrar_modulo_pendiente("📋 ASIGNACIONES", 
                                     "Módulo para ver tus asignaciones de entrenamiento.")
    
    def abrir_coach_dashboard(self):
        """Dashboard específico para coaches"""
        self.mostrar_modulo_pendiente("📊 MI DASHBOARD", 
                                     "Dashboard personalizado para coaches.")
    
    def abrir_mi_perfil(self):
        """Perfil del atleta"""
        self.mostrar_modulo_pendiente("👤 MI PERFIL", 
                                     "Módulo para ver y editar tu información personal.")
    
    def abrir_mis_pagos(self):
        """Pagos del atleta"""
        self.mostrar_modulo_pendiente("💰 MIS PAGOS", 
                                     "Módulo para ver tu historial de pagos y estado de cuenta.")
    
    def abrir_mi_coach(self):
        """Coach del atleta"""
        self.mostrar_modulo_pendiente("💪 MI COACH", 
                                     "Módulo para ver información de tu entrenador asignado.")
    
    def mostrar_modulo_pendiente(self, titulo, descripcion):
        """Muestra un mensaje para módulos pendientes de implementar"""
        self.limpiar_area_trabajo()
        
        # Título del módulo
        title_label = ttk.Label(
            self.work_frame,
            text=titulo,
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(pady=(30, 20))
        
        # Descripción
        desc_label = ttk.Label(
            self.work_frame,
            text=descripcion,
            font=('Segoe UI', 12),
            justify='center'
        )
        desc_label.pack(pady=(0, 30))
        
        # Mensaje de desarrollo
        dev_label = ttk.Label(
            self.work_frame,
            text="🚧 MÓDULO EN DESARROLLO 🚧\n\nEsta funcionalidad se implementará próximamente.",
            font=('Segoe UI', 11),
            justify='center',
            foreground='orange'
        )
        dev_label.pack(pady=20)
        
        # Botón para volver al dashboard
        back_btn = ttk.Button(
            self.work_frame,
            text="🏠 Volver al Dashboard",
            command=self.mostrar_dashboard_resumen
        )
        back_btn.pack(pady=20)
    
    # ==================== GESTION DE RUTINAS ====================

    def abrir_gestion_rutinas(self):
        """Abre la gestión de rutinas"""
        if not self.verificar_permisos(['admin_principal', 'coach']):
            return
        
        self.activar_boton_menu(self.botones_menu[6])

        self.mostrar_gestion_rutinas()

    def mostrar_gestion_rutinas(self):
        """Muestra el módulo completo de gestión de rutinas"""
        self.limpiar_area_trabajo()
        
        # Variables para el módulo
        self.rutinas_data = []
        self.rutina_seleccionada = None
        
        # Título del módulo
        title_frame = ttk.Frame(self.work_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="🏃‍♂️ GESTIÓN DE RUTINAS",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(side='left')
        
        # Botón de actualizar
        refresh_btn = ttk.Button(
            title_frame,
            text="🔄 Actualizar",
            command=self.cargar_rutinas
        )
        refresh_btn.pack(side='right')
        
        # Frame de controles
        controls_frame = ttk.Frame(self.work_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Búsqueda y filtros
        self.crear_filtros_rutinas(controls_frame)
        
        # Botones de acción
        self.crear_botones_rutinas(controls_frame)
        
        # Tabla de rutinas
        self.crear_tabla_rutinas()
        
        # Cargar datos iniciales
        self.cargar_rutinas()

    def crear_filtros_rutinas(self, parent):
        """Crea los filtros de búsqueda para rutinas"""
        search_frame = ttk.Frame(parent)
        search_frame.pack(side='left', fill='x', expand=True)
        
        # Búsqueda por texto
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side='left', padx=(0, 5))
        
        self.search_rutinas_var = tk.StringVar()
        self.search_rutinas_entry = ttk.Entry(search_frame, textvariable=self.search_rutinas_var, width=25)
        self.search_rutinas_entry.pack(side='left', padx=(0, 10))
        self.search_rutinas_var.trace('w', self.filtrar_rutinas)
        
        # Filtro por nivel
        ttk.Label(search_frame, text="📊 Nivel:").pack(side='left', padx=(10, 5))
        
        self.nivel_filter_var = tk.StringVar(value="Todos")
        nivel_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.nivel_filter_var,
            values=["Todos", "Principiante", "Intermedio", "Avanzado"],
            state="readonly",
            width=12
        )
        nivel_combo.pack(side='left')
        nivel_combo.bind('<<ComboboxSelected>>', self.filtrar_rutinas)

    def crear_botones_rutinas(self, parent):
        """Crea los botones de acción para rutinas"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(side='right')
        
        # Botón crear rutina
        self.create_rutina_btn = ttk.Button(
            buttons_frame,
            text="➕ Crear Rutina",
            command=self.crear_rutina
        )
        self.create_rutina_btn.pack(side='left', padx=2)
        
        # Botón ver rutina completa
        self.view_rutina_btn = ttk.Button(
            buttons_frame,
            text="👁️ Ver Rutina",
            command=self.ver_rutina_completa,
            state='disabled'
        )
        self.view_rutina_btn.pack(side='left', padx=2)
        
        # Botón editar rutina
        self.edit_rutina_btn = ttk.Button(
            buttons_frame,
            text="✏️ Editar",
            command=self.editar_rutina,
            state='disabled'
        )
        self.edit_rutina_btn.pack(side='left', padx=2)

        self.delete_rutina_btn = ttk.Button(
            buttons_frame,
            text="🗑️ Eliminar",
            command=self.eliminar_rutina,
            state='disabled'
        )
        self.delete_rutina_btn.pack(side='left', padx=2)

    def crear_tabla_rutinas(self):
        """Crea la tabla de rutinas con Treeview"""
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Configurar Treeview
        columns = ('ID', 'Nombre', 'Nivel', 'Ejercicios', 'Creado Por', 'Fecha Creación')
        self.rutinas_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.rutinas_tree.heading('ID', text='ID')
        self.rutinas_tree.heading('Nombre', text='Nombre Rutina')
        self.rutinas_tree.heading('Nivel', text='Nivel')
        self.rutinas_tree.heading('Ejercicios', text='# Ejercicios')
        self.rutinas_tree.heading('Creado Por', text='Creado Por')
        self.rutinas_tree.heading('Fecha Creación', text='Fecha Creación')
        
        # Configurar anchos
        self.rutinas_tree.column('ID', width=50, anchor='center')
        self.rutinas_tree.column('Nombre', width=200)
        self.rutinas_tree.column('Nivel', width=100, anchor='center')
        self.rutinas_tree.column('Ejercicios', width=100, anchor='center')
        self.rutinas_tree.column('Creado Por', width=150)
        self.rutinas_tree.column('Fecha Creación', width=120, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.rutinas_tree.yview)
        self.rutinas_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Empaquetar
        self.rutinas_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        self.rutinas_tree.bind('<<TreeviewSelect>>', self.on_rutina_selected)

    def cargar_rutinas(self):
        """Carga las rutinas desde la base de datos"""
        try:
            print("🔄 Cargando rutinas...")
            
            rutinas = self.rutina_controller.obtener_rutinas()
            self.rutinas_data = rutinas if rutinas else []
            
            print(f"✅ Cargadas {len(self.rutinas_data)} rutinas")
            
            # Actualizar tabla
            self.actualizar_tabla_rutinas()
            
        except Exception as e:
            print(f"❌ Error cargando rutinas: {e}")
            messagebox.showerror("Error", f"Error al cargar rutinas:\n{e}")

    def on_rutina_selected(self, event):
        """Maneja la selección de rutina en la tabla"""
        selection = self.rutinas_tree.selection()
        if selection:
            # Habilitar botones
            self.view_rutina_btn.config(state='normal')
            self.edit_rutina_btn.config(state='normal')
            self.delete_rutina_btn.config(state='normal')
            
            # Obtener rutina seleccionada
            item = self.rutinas_tree.item(selection[0])
            rutina_id = item['values'][0]
            
            # Buscar rutina completa en los datos
            for rutina in self.rutinas_data:
                if rutina[0] == rutina_id:
                    self.rutina_seleccionada = rutina
                    break
        else:
            # Deshabilitar botones
            self.view_rutina_btn.config(state='disabled')
            self.edit_rutina_btn.config(state='disabled')
            self.delete_rutina_btn.config(state='disabled')
            self.rutina_seleccionada = None

    def crear_rutina(self):
        """Abre el formulario para crear una nueva rutina"""
        self.abrir_formulario_rutina(modo='crear')

    def ver_rutina_completa(self):
        """Muestra la rutina completa con sus ejercicios"""
        if not self.rutina_seleccionada:
            return
        
        rutina_id = self.rutina_seleccionada[0]
        rutina_completa = self.rutina_controller.obtener_rutina_completa(rutina_id)
        
        # Ventana modal para mostrar la rutina
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Rutina: {self.rutina_seleccionada[1]}")
        ventana.geometry("600x400")
        ventana.transient(self.root)
        
        # Mostrar ejercicios de la rutina
        for ejercicio in rutina_completa:
            texto = f"{ejercicio[1]} - {ejercicio[2]} series x {ejercicio[3]} rondas ({ejercicio[4]})"
            ttk.Label(ventana, text=texto).pack(pady=2)

    def filtrar_rutinas(self, *args):
        """Filtra rutinas según búsqueda y nivel"""
        search_text = self.search_rutinas_var.get().lower()
        nivel_filter = self.nivel_filter_var.get()
        
        if not search_text and nivel_filter == "Todos":
            self.actualizar_tabla_rutinas()
            return
        
        rutinas_filtradas = []
        
        for rutina in self.rutinas_data:
            # Filtro de texto
            texto_busqueda = f"{rutina[1]} {rutina[3]}".lower()  # nombre + descripcion
            if search_text and search_text not in texto_busqueda:
                continue
            
            # Filtro de nivel
            if nivel_filter != "Todos" and rutina[2] != nivel_filter:
                continue
            
            rutinas_filtradas.append(rutina)
        
        self.actualizar_tabla_rutinas(rutinas_filtradas)

    def actualizar_tabla_rutinas(self, rutinas_filtradas=None):
        """Actualiza la tabla con las rutinas"""
        # Limpiar tabla
        for item in self.rutinas_tree.get_children():
            self.rutinas_tree.delete(item)
        
        # Usar rutinas filtradas o todas
        rutinas = rutinas_filtradas if rutinas_filtradas is not None else self.rutinas_data
        
        # Llenar tabla
        for rutina in rutinas:
            try:
                # rutina = (id, nombre, nivel, descripcion, creado_por, fecha_creacion)
                rutina_id = rutina[0]
                nombre = rutina[1]
                nivel = rutina[2]
                creado_por = f"Usuario {rutina[4]}"  # Por ahora ID, después puedes mapear a nombre
                
                # Contar ejercicios de esta rutina
                num_ejercicios = self.rutina_controller.contar_ejercicios_rutina(rutina_id)
                
                # Formatear fecha
                try:
                    if rutina[5]:
                        fecha = str(rutina[5])[:10]
                    else:
                        fecha = "N/A"
                except:
                    fecha = "N/A"
                
                # Insertar fila
                self.rutinas_tree.insert('', 'end', values=(
                    rutina_id, nombre, nivel, num_ejercicios, creado_por, fecha
                ))
                
            except Exception as e:
                print(f"Error procesando rutina: {e}")
                continue

    def editar_rutina(self):
        """Abre formulario para editar rutina"""
        if not self.rutina_seleccionada:
            messagebox.showwarning("Advertencia", "Selecciona una rutina para editar")
            return
        
        self.abrir_formulario_rutina(modo='editar', rutina=self.rutina_seleccionada)

    def eliminar_rutina(self):
        """Elimina la rutina seleccionada"""
        if not self.rutina_seleccionada:
            messagebox.showwarning("Advertencia", "Selecciona una rutina para eliminar")
            return
        
        rutina_nombre = self.rutina_seleccionada[1]
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro que deseas eliminar la rutina '{rutina_nombre}'?\n\nEsta acción eliminará también todos los ejercicios asociados."
        )
        
        if respuesta:
            try:
                rutina_id = self.rutina_seleccionada[0]
                resultado = self.rutina_controller.eliminar_rutina(rutina_id)
                
                if resultado:
                    messagebox.showinfo("Éxito", "Rutina eliminada exitosamente")
                    self.cargar_rutinas()
                else:
                    messagebox.showerror("Error", "Error al eliminar la rutina")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar rutina:\n{e}")

    def abrir_formulario_rutina(self, modo='crear', rutina=None):
        """Formulario ÚNICO para crear rutina completa con ejercicios"""
        # Crear ventana modal
        self.rutina_form_window = tk.Toplevel(self.root)
        self.rutina_form_window.title(f"{'Crear' if modo == 'crear' else 'Editar'} Rutina Completa")
        self.rutina_form_window.geometry("800x1200")
        self.rutina_form_window.transient(self.root)
        self.rutina_form_window.grab_set()
        
        main_frame = ttk.Frame(self.rutina_form_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(main_frame, text=f"{'➕ CREAR' if modo == 'crear' else '✏️ EDITAR'} RUTINA",
                font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # SECCIÓN 1: DATOS DE LA RUTINA
        rutina_frame = ttk.LabelFrame(main_frame, text="📋 DATOS DE LA RUTINA", padding=15)
        rutina_frame.pack(fill='x', pady=(0, 20))
        
        # Variables del formulario
        self.nombre_rutina_var = tk.StringVar()
        self.nivel_rutina_var = tk.StringVar()
        
        # Campos básicos
        ttk.Label(rutina_frame, text="Nombre de la Rutina *:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(rutina_frame, textvariable=self.nombre_rutina_var, width=40).grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(rutina_frame, text="Nivel *:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Combobox(rutina_frame, textvariable=self.nivel_rutina_var, 
                    values=['Principiante', 'Intermedio', 'Avanzado'], 
                    state='readonly', width=37).grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(rutina_frame, text="Descripción:").grid(row=2, column=0, sticky='nw', pady=5)
        self.descripcion_rutina_text = tk.Text(rutina_frame, height=3, width=40)
        self.descripcion_rutina_text.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        rutina_frame.grid_columnconfigure(1, weight=1)
        
        # SECCIÓN 2: AGREGAR EJERCICIOS
        ejercicios_frame = ttk.LabelFrame(main_frame, text="💪 AGREGAR EJERCICIOS", padding=15)
        ejercicios_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Formulario para agregar ejercicio
        add_frame = ttk.Frame(ejercicios_frame)
        add_frame.pack(fill='x', pady=(0, 15))
        
        # Variables para ejercicios
        self.nombre_ejercicio_var = tk.StringVar()
        self.tipo_ejercicio_var = tk.StringVar(value='Fuerza')
        self.series_var = tk.StringVar(value='3')
        self.rondas_var = tk.StringVar(value='10')
        
        # Primera fila: Nombre y Tipo
        ttk.Label(add_frame, text="Ejercicio:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        ttk.Entry(add_frame, textvariable=self.nombre_ejercicio_var, width=25).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(add_frame, text="Tipo:").grid(row=0, column=2, sticky='w', padx=(0, 5))
        ttk.Combobox(add_frame, textvariable=self.tipo_ejercicio_var, 
                    values=['Fuerza', 'Cardio', 'Flexibilidad'], 
                    state='readonly', width=15).grid(row=0, column=3, padx=(0, 10))
        
        # Segunda fila: Series y Rondas
        ttk.Label(add_frame, text="Series:").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(10, 0))
        ttk.Entry(add_frame, textvariable=self.series_var, width=10).grid(row=1, column=1, sticky='w', pady=(10, 0))
        
        ttk.Label(add_frame, text="Rondas:").grid(row=1, column=2, sticky='w', padx=(0, 5), pady=(10, 0))
        ttk.Entry(add_frame, textvariable=self.rondas_var, width=10).grid(row=1, column=3, sticky='w', pady=(10, 0))
        
        # Botón agregar ejercicio
        ttk.Button(add_frame, text="➕ Agregar a Rutina", 
                command=self.agregar_ejercicio_a_lista).grid(row=1, column=4, padx=(10, 0), pady=(10, 0))
        
        # Lista de ejercicios agregados
        self.ejercicios_rutina = []
        
        # Tabla de ejercicios
        list_frame = ttk.Frame(ejercicios_frame)
        list_frame.pack(fill='both', expand=True)
        
        columns = ('Ejercicio', 'Tipo', 'Series', 'Rondas')
        self.ejercicios_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=4)
        
        for col in columns:
            self.ejercicios_tree.heading(col, text=col)
            self.ejercicios_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.ejercicios_tree.yview)
        self.ejercicios_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ejercicios_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind para selección
        self.ejercicios_tree.bind('<<TreeviewSelect>>', self.on_ejercicio_form_selected)
        
        # Botón quitar ejercicio
        ttk.Button(ejercicios_frame, text="➖ Quitar Seleccionado", 
                command=self.quitar_ejercicio_seleccionado).pack(pady=(10, 0))
        
        # BOTONES FINALES
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                command=self.rutina_form_window.destroy).pack(side='right', padx=(5, 0))
        
        ttk.Button(buttons_frame, text=f"💾 {'Crear Rutina Completa' if modo == 'crear' else 'Guardar Cambios'}", 
                command=lambda: self.guardar_rutina_final(modo)).pack(side='right')


    def agregar_ejercicio_a_lista(self):
        """Agrega ejercicio a la lista de la rutina"""
        # Validar campos
        if not self.nombre_ejercicio_var.get().strip():
            messagebox.showerror("Error", "Ingresa el nombre del ejercicio")
            return
        
        try:
            series = int(self.series_var.get())
            rondas = int(self.rondas_var.get())
            if series <= 0 or rondas <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Series y rondas deben ser números positivos")
            return
        
        # Agregar a la lista
        ejercicio = {
            'nombre': self.nombre_ejercicio_var.get().strip(),
            'tipo': self.tipo_ejercicio_var.get(),
            'series': series,
            'rondas': rondas
        }
        
        self.ejercicios_rutina.append(ejercicio)
        
        # Actualizar tabla
        self.actualizar_tabla_ejercicios()
        
        # Limpiar campos
        self.nombre_ejercicio_var.set('')
        self.series_var.set('3')
        self.rondas_var.set('10')

    def guardar_rutina_final(self, modo):
        """Guarda la rutina completa con todos los ejercicios"""
        try:
            # Validar rutina
            if not self.nombre_rutina_var.get().strip():
                messagebox.showerror("Error", "Ingresa el nombre de la rutina")
                return
            
            if not self.nivel_rutina_var.get():
                messagebox.showerror("Error", "Selecciona el nivel")
                return
            
            if len(self.ejercicios_rutina) == 0:
                messagebox.showerror("Error", "Agrega al menos un ejercicio")
                return
            
            # Crear rutina
            nombre_rutina = self.nombre_rutina_var.get().strip()
            nivel = self.nivel_rutina_var.get()
            descripcion = self.descripcion_rutina_text.get('1.0', 'end-1c').strip()
            
            rutina_id = self.rutina_controller.crear_rutina(
                nombre_rutina, nivel, descripcion, self.usuario_actual['id']
            )
            
            if rutina_id:
                # Crear y asignar cada ejercicio
                for i, ejercicio in enumerate(self.ejercicios_rutina):
                    # Crear ejercicio en BD
                    ejercicio_id = self.rutina_controller.crear_ejercicio(
                        ejercicio['nombre'],
                        ejercicio['tipo'],
                        f"Ejercicio de {ejercicio['tipo'].lower()}",
                        f"Realizar {ejercicio['series']} series de {ejercicio['rondas']} repeticiones"
                    )
                    
                    if ejercicio_id:
                        # Asignar a rutina
                        self.rutina_controller.asignar_ejercicio_a_rutina(
                            rutina_id, ejercicio_id, nivel,
                            ejercicio['series'], ejercicio['rondas'], i + 1
                        )
                
                messagebox.showinfo("Éxito", f"Rutina '{nombre_rutina}' creada con {len(self.ejercicios_rutina)} ejercicios")
                self.rutina_form_window.destroy()
                self.cargar_rutinas()
            else:
                messagebox.showerror("Error", "Error al crear la rutina")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")


    def quitar_ejercicio_seleccionado(self):
        """Quita el ejercicio seleccionado de la lista"""
        selection = self.ejercicios_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un ejercicio para quitar")
            return
        
        # Obtener índice
        item = self.ejercicios_tree.item(selection[0])
        nombre_ejercicio = item['values'][0]
        
        # Quitar de la lista
        self.ejercicios_rutina = [ej for ej in self.ejercicios_rutina if ej['nombre'] != nombre_ejercicio]
        
        # Actualizar tabla
        self.actualizar_tabla_ejercicios()

    def validar_formulario_rutina_completa(self):
        """Valida el formulario completo de rutina"""
        if not self.rutina_form_vars['nombre_rutina'].get().strip():
            messagebox.showerror("Error", "El nombre de la rutina es requerido")
            return False
        
        if not self.rutina_form_vars['nivel'].get():
            messagebox.showerror("Error", "El nivel es requerido")
            return False
        
        if len(self.ejercicios_rutina) == 0:
            messagebox.showerror("Error", "Debes agregar al menos un ejercicio a la rutina")
            return False
        
        return True
    

    def crear_seccion_datos_rutina(self, parent):
        """Crea la sección de datos básicos de la rutina"""
        seccion_frame = ttk.LabelFrame(parent, text="📋 DATOS DE LA RUTINA", padding=15)
        seccion_frame.pack(fill='x', pady=(0, 20))
        
        # Nombre de la rutina
        ttk.Label(seccion_frame, text="Nombre de la Rutina *").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(seccion_frame, textvariable=self.rutina_form_vars['nombre_rutina'], width=50).grid(
            row=0, column=1, sticky='ew', pady=5, padx=(10, 0)
        )
        
        # Nivel
        ttk.Label(seccion_frame, text="Nivel *").grid(row=1, column=0, sticky='w', pady=5)
        nivel_combo = ttk.Combobox(
            seccion_frame,
            textvariable=self.rutina_form_vars['nivel'],
            values=['Principiante', 'Intermedio', 'Avanzado'],
            state='readonly',
            width=47
        )
        nivel_combo.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Descripción
        ttk.Label(seccion_frame, text="Descripción").grid(row=2, column=0, sticky='nw', pady=(5, 0))
        self.descripcion_rutina_text = tk.Text(seccion_frame, height=4, width=50)
        self.descripcion_rutina_text.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Si hay descripción previa, cargarla
        if self.rutina_form_vars['descripcion'].get():
            self.descripcion_rutina_text.insert('1.0', self.rutina_form_vars['descripcion'].get())
        
        seccion_frame.grid_columnconfigure(1, weight=1)

    def crear_seccion_ejercicios_rutina(self, parent):
        """Crea la sección para gestionar ejercicios de la rutina"""
        seccion_frame = ttk.LabelFrame(parent, text="💪 EJERCICIOS DE LA RUTINA", padding=15)
        seccion_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Botones para gestionar ejercicios
        btn_frame = ttk.Frame(seccion_frame)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="➕ Agregar Ejercicio",
            command=self.agregar_ejercicio_a_rutina_form
        ).pack(side='left', padx=(0, 10))
        
        self.quitar_ejercicio_btn = ttk.Button(
            btn_frame,
            text="➖ Quitar Ejercicio",
            command=self.quitar_ejercicio_de_rutina_form,
            state='disabled'
        )
        self.quitar_ejercicio_btn.pack(side='left')
        
        # Tabla de ejercicios agregados
        self.crear_tabla_ejercicios_form(seccion_frame)
        
        # Actualizar tabla si hay ejercicios
        self.actualizar_tabla_ejercicios_form()

    def crear_tabla_ejercicios_form(self, parent):
        """Crea la tabla de ejercicios en el formulario"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)
        
        columns = ('Orden', 'Ejercicio', 'Tipo', 'Nivel', 'Series', 'Rondas')
        self.ejercicios_form_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        # Configurar encabezados
        for col in columns:
            self.ejercicios_form_tree.heading(col, text=col)
            self.ejercicios_form_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar_ej = ttk.Scrollbar(table_frame, orient='vertical', command=self.ejercicios_form_tree.yview)
        self.ejercicios_form_tree.configure(yscrollcommand=scrollbar_ej.set)
        
        self.ejercicios_form_tree.pack(side='left', fill='both', expand=True)
        scrollbar_ej.pack(side='right', fill='y')
        
        # Bind para selección
        self.ejercicios_form_tree.bind('<<TreeviewSelect>>', self.on_ejercicio_form_selected)

    def agregar_ejercicio_a_rutina_form(self):
        """Abre formulario para CREAR Y agregar ejercicio a la rutina"""
        # Ventana para crear nuevo ejercicio
        ejercicio_window = tk.Toplevel(self.rutina_form_window)
        ejercicio_window.title("Crear Nuevo Ejercicio")
        ejercicio_window.geometry("600x400")
        ejercicio_window.transient(self.rutina_form_window)
        ejercicio_window.grab_set()
        
        main_frame = ttk.Frame(ejercicio_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="➕ CREAR NUEVO EJERCICIO", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Variables para el ejercicio
        nombre_ejercicio_var = tk.StringVar()
        tipo_ejercicio_var = tk.StringVar(value='Fuerza')
        descripcion_ejercicio_var = tk.StringVar()
        
        # Variables para parámetros en rutina
        nivel_var = tk.StringVar(value='Principiante')
        series_var = tk.StringVar(value='3')
        rondas_var = tk.StringVar(value='10')
        
        # Formulario del ejercicio
        form_frame = ttk.LabelFrame(main_frame, text="Datos del Ejercicio", padding=10)
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Nombre del ejercicio
        ttk.Label(form_frame, text="Nombre del Ejercicio *:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(form_frame, textvariable=nombre_ejercicio_var, width=40).grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Tipo de ejercicio
        ttk.Label(form_frame, text="Tipo *:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Combobox(form_frame, textvariable=tipo_ejercicio_var, 
                    values=['Fuerza', 'Cardio', 'Flexibilidad'], 
                    state='readonly', width=37).grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(form_frame, textvariable=descripcion_ejercicio_var, width=40).grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Instrucciones
        ttk.Label(form_frame, text="Instrucciones:").grid(row=3, column=0, sticky='nw', pady=5)
        instrucciones_text = tk.Text(form_frame, height=3, width=40)
        instrucciones_text.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Parámetros para la rutina
        params_frame = ttk.LabelFrame(main_frame, text="Parámetros en la Rutina", padding=10)
        params_frame.pack(fill='x', pady=(0, 20))
        
        # Primera fila
        ttk.Label(params_frame, text="Nivel:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Combobox(params_frame, textvariable=nivel_var, 
                    values=['Principiante', 'Intermedio', 'Avanzado'], 
                    state='readonly', width=15).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(params_frame, text="Series:").grid(row=0, column=2, sticky='w', padx=(0, 10))
        ttk.Entry(params_frame, textvariable=series_var, width=10).grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(params_frame, text="Rondas:").grid(row=0, column=4, sticky='w', padx=(0, 10))
        ttk.Entry(params_frame, textvariable=rondas_var, width=10).grid(row=0, column=5)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        def crear_y_agregar_ejercicio():
            # Validar campos requeridos
            if not nombre_ejercicio_var.get().strip():
                messagebox.showerror("Error", "El nombre del ejercicio es requerido")
                return
            
            if not tipo_ejercicio_var.get():
                messagebox.showerror("Error", "El tipo de ejercicio es requerido")
                return
            
            # Validar series y rondas
            try:
                series = int(series_var.get())
                rondas = int(rondas_var.get())
                if series <= 0 or rondas <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Series y rondas deben ser números positivos")
                return
            
            # Crear ejercicio en la base de datos
            instrucciones = instrucciones_text.get('1.0', 'end-1c').strip()
            ejercicio_id = self.rutina_controller.crear_ejercicio(
                nombre_ejercicio_var.get().strip(),
                tipo_ejercicio_var.get(),
                descripcion_ejercicio_var.get().strip(),
                instrucciones
            )
            
            if ejercicio_id:
                # Agregar a la lista de ejercicios de la rutina
                nuevo_ejercicio = {
                    'id': ejercicio_id,
                    'nombre': nombre_ejercicio_var.get().strip(),
                    'tipo': tipo_ejercicio_var.get(),
                    'nivel': nivel_var.get(),
                    'series': series,
                    'rondas': rondas,
                    'orden': len(self.ejercicios_rutina) + 1
                }
                
                self.ejercicios_rutina.append(nuevo_ejercicio)
                self.actualizar_tabla_ejercicios_form()
                ejercicio_window.destroy()
                messagebox.showinfo("Éxito", f"Ejercicio '{nuevo_ejercicio['nombre']}' creado y agregado")
            else:
                messagebox.showerror("Error", "Error al crear el ejercicio")
        
        ttk.Button(btn_frame, text="➕ Crear y Agregar", command=crear_y_agregar_ejercicio).pack(side='right')
        ttk.Button(btn_frame, text="❌ Cancelar", command=ejercicio_window.destroy).pack(side='right', padx=(0, 10))

    def actualizar_tabla_ejercicios(self):
        """Actualiza la tabla de ejercicios"""
        # Limpiar tabla
        for item in self.ejercicios_tree.get_children():
            self.ejercicios_tree.delete(item)
        
        # Llenar con ejercicios
        for ejercicio in self.ejercicios_rutina:
            self.ejercicios_tree.insert('', 'end', values=(
                ejercicio['nombre'],
                ejercicio['tipo'],
                ejercicio['series'],
                ejercicio['rondas']
            ))

    def on_ejercicio_form_selected(self, event):
        """Maneja selección en tabla de ejercicios del formulario"""
        selection = self.ejercicios_form_tree.selection()
        if selection:
            self.quitar_ejercicio_btn.config(state='normal')
        else:
            self.quitar_ejercicio_btn.config(state='disabled')

    def quitar_ejercicio_de_rutina_form(self):
        """Quita ejercicio seleccionado de la rutina"""
        messagebox.showinfo("Función pendiente", "Quitar ejercicios próximamente")

    def crear_botones_formulario_rutina_completa(self, parent, modo):
        """Crea botones del formulario completo"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=self.rutina_form_window.destroy
        ).pack(side='right', padx=(5, 0))
        
        ttk.Button(
            buttons_frame,
            text=f"💾 {'Crear Rutina' if modo == 'crear' else 'Guardar Cambios'}",
            command=lambda: self.guardar_rutina_completa(modo)
        ).pack(side='right')

    def guardar_rutina_completa(self, modo):
        """Guarda la rutina completa con ejercicios"""
        try:
            # Validar datos básicos
            if not self.validar_formulario_rutina_completa():
                return
            
            # Recoger datos
            nombre_rutina = self.rutina_form_vars['nombre_rutina'].get().strip()
            nivel = self.rutina_form_vars['nivel'].get()
            descripcion = self.descripcion_rutina_text.get('1.0', 'end-1c').strip()
            
            if modo == 'crear':
                # Crear rutina
                rutina_id = self.rutina_controller.crear_rutina(
                    nombre_rutina, nivel, descripcion, self.usuario_actual['id']
                )
                
                if rutina_id:
                    # Agregar cada ejercicio a la rutina
                    for ejercicio in self.ejercicios_rutina:
                        self.rutina_controller.asignar_ejercicio_a_rutina(
                            rutina_id, 
                            ejercicio['id'], 
                            ejercicio['nivel'],
                            ejercicio['series'], 
                            ejercicio['rondas'], 
                            ejercicio['orden']
                        )
                    
                    messagebox.showinfo("Éxito", f"Rutina '{nombre_rutina}' creada con {len(self.ejercicios_rutina)} ejercicios")
                    self.rutina_form_window.destroy()
                    self.cargar_rutinas()
                else:
                    messagebox.showerror("Error", "Error al crear la rutina")
            
            else:
                # Editar rutina existente
                rutina_id = self.rutina_seleccionada[0]
                
                if self.rutina_controller.actualizar_rutina(rutina_id, nombre_rutina, nivel, descripcion):
                    messagebox.showinfo("Éxito", "Rutina actualizada exitosamente")
                    self.rutina_form_window.destroy()
                    self.cargar_rutinas()
                else:
                    messagebox.showerror("Error", "Error al actualizar la rutina")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar rutina:\n{e}")

    # ==================== VERIFICACIÓN DE PERMISOS ====================
    
    def verificar_permisos(self, roles_permitidos):
        """Verifica si el usuario actual tiene permisos para acceder"""
        if self.usuario_actual['rol'] in roles_permitidos:
            return True
        else:
            messagebox.showwarning(
                "Acceso Denegado", 
                f"No tienes permisos para acceder a esta función.\n\nRequiere rol: {', '.join(roles_permitidos)}"
            )
            return False
    
    # ==================== CERRAR SESIÓN ====================
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        respuesta = messagebox.askyesno(
            "Cerrar Sesión", 
            "¿Estás seguro que deseas cerrar sesión?"
        )
        
        if respuesta:
            # Cerrar sesión en el controlador
            if self.token_sesion:
                resultado = self.auth_controller.cerrar_sesion(self.token_sesion)
                print(f"🚪 {resultado['message']}")
            
            # Limpiar variables de sesión
            self.usuario_actual = None
            self.token_sesion = None
            
            # Volver al login
            self.mostrar_login()
    
    # ==================== MÉTODOS PARA OTROS ROLES ====================
    
    def crear_dashboard_secretaria(self):
        """Dashboard para secretaria (mismo que admin por ahora)"""
        self.crear_dashboard_admin()
    
    def crear_dashboard_coach(self):
        """Dashboard para coach (mismo layout pero con menú diferente)"""
        self.crear_dashboard_admin()
    
    def crear_dashboard_atleta(self):
        """Dashboard para atleta (mismo layout pero con menú diferente)"""
        self.crear_dashboard_admin()
    
    def crear_dashboard_default(self):
        """Dashboard por defecto"""
        self.crear_dashboard_admin()
        
    def abrir_gestion_egresos(self):
        """Abre la vista de Gestión de Egresos."""
        if not self.verificar_permisos(['admin_principal', 'secretaria']):
            return
        
        self.activar_boton_menu(self.botones_menu[4])

        self.mostrar_gestion_egresos()

    def mostrar_gestion_egresos(self):
        """Crea y muestra la interfaz para el módulo de Gestión de Egresos."""
        self.limpiar_area_trabajo()
        self.egresos_data = []

        # Título
        title_frame = ttk.Frame(self.work_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(title_frame, text="💸 GESTIÓN DE EGRESOS", font=('Segoe UI', 18, 'bold')).pack(side='left')
        
        # Frame de Controles
        controls_frame = ttk.Frame(self.work_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(controls_frame, text="🔄 Actualizar", command=self.cargar_egresos).pack(side='right', padx=5)
        ttk.Button(controls_frame, text="➕ Registrar Egreso", command=self._registrar_nuevo_egreso_action).pack(side='right', padx=5)
        
        # Tabla de Egresos
        self.crear_tabla_egresos()
        
        # Cargar datos iniciales
        self.cargar_egresos()

    def crear_tabla_egresos(self):
        """Crea la tabla (Treeview) para mostrar los egresos."""
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        columns = ('ID', 'Fecha', 'Tipo', 'Monto', 'Descripción', 'Beneficiario', 'Método', 'Registrado Por')
        self.egresos_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        col_widths = {'ID': 50, 'Fecha': 100, 'Tipo': 120, 'Monto': 90, 'Descripción': 250, 'Beneficiario': 150, 'Método': 100, 'Registrado Por': 120}
        
        for col, width in col_widths.items():
            self.egresos_tree.heading(col, text=col)
            self.egresos_tree.column(col, width=width, anchor='w')
        self.egresos_tree.column('Monto', anchor='e')

        v_scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.egresos_tree.yview)
        
        self.egresos_tree.configure(yscrollcommand=v_scroll.set)
        
        self.egresos_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
       

    def cargar_egresos(self):
        """Carga los datos de egresos desde el controlador y actualiza la tabla."""
        try:
            resultado = self.finance_controller.obtener_todos_los_egresos()
            if resultado['success']:
                self.egresos_data = resultado['egresos']
                self.actualizar_tabla_egresos()
            else:
                messagebox.showerror("Error", f"No se pudieron cargar los egresos: {resultado['message']}")
        except Exception as e:
            messagebox.showerror("Error Crítico", f"Error al cargar egresos: {e}")

    def actualizar_tabla_egresos(self):
        """Limpia y rellena la tabla de egresos con los datos actuales."""
        self.egresos_tree.delete(*self.egresos_tree.get_children())
        for egreso in self.egresos_data:
            monto_formateado = f"${egreso[1]:.2f}"
            tipo_legible = egreso[2].replace('_', ' ').title()
            
            # Obtener nombre del registrador (asumiendo que tienes una forma de mapear ID a nombre)
            registrado_por_id = egreso[7]
            # Aquí podrías llamar a un método para obtener el nombre del usuario por ID
            registrado_por_nombre = f"Usuario ID: {registrado_por_id}" 

            values = (
                egreso[0], # ID
                egreso[6], # Fecha
                tipo_legible, # Tipo
                monto_formateado, # Monto
                egreso[3], # Descripción
                egreso[4], # Beneficiario
                egreso[5], # Método
                registrado_por_nombre
            )
            self.egresos_tree.insert('', 'end', values=values)
            
    def _registrar_nuevo_egreso_action(self):
        """Abre el formulario para registrar un nuevo egreso."""
        self.egreso_form_window = tk.Toplevel(self.root)
        self.egreso_form_window.title("➕ Registrar Nuevo Egreso")
        self.egreso_form_window.geometry("500x450")
        self.egreso_form_window.transient(self.root)
        self.egreso_form_window.grab_set()

        frame = ttk.Frame(self.egreso_form_window, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Registrar Nuevo Egreso", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        form_fields = ttk.Frame(frame)
        form_fields.pack(fill='x')
        
        # Variables del formulario
        self.egreso_vars = {
            'monto': tk.StringVar(),
            'tipo_egreso': tk.StringVar(),
            'descripcion': tk.StringVar(),
            'beneficiario': tk.StringVar(),
            'metodo_pago': tk.StringVar(value="transferencia")
        }

        # Campos
        ttk.Label(form_fields, text="Monto *:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(form_fields, textvariable=self.egreso_vars['monto']).grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(form_fields, text="Tipo de Egreso *:").grid(row=1, column=0, sticky='w', pady=5)
        tipos_egreso = ['salario_empleado', 'compra_equipos', 'mantenimiento', 'servicios', 'alquiler', 'otro']
        ttk.Combobox(form_fields, textvariable=self.egreso_vars['tipo_egreso'], values=tipos_egreso, state='readonly').grid(row=1, column=1, sticky='ew', pady=5)

        ttk.Label(form_fields, text="Método de Pago *:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Combobox(form_fields, textvariable=self.egreso_vars['metodo_pago'], values=["efectivo", "tarjeta", "transferencia"], state='readonly').grid(row=2, column=1, sticky='ew', pady=5)

        ttk.Label(form_fields, text="Beneficiario:").grid(row=3, column=0, sticky='w', pady=5)
        ttk.Entry(form_fields, textvariable=self.egreso_vars['beneficiario']).grid(row=3, column=1, sticky='ew', pady=5)

        ttk.Label(form_fields, text="Descripción *:").grid(row=4, column=0, sticky='nw', pady=5)
        self.egreso_desc_text = tk.Text(form_fields, height=4)
        self.egreso_desc_text.grid(row=4, column=1, sticky='ew', pady=5)
        
        form_fields.grid_columnconfigure(1, weight=1)

        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        ttk.Button(btn_frame, text="💾 Guardar Egreso", command=self._guardar_nuevo_egreso_action).pack(side='right')
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.egreso_form_window.destroy).pack(side='right', padx=10)

    def _guardar_nuevo_egreso_action(self):
        """Recoge los datos del formulario de egreso y los envía al controlador."""
        datos_egreso = {
            'monto': self.egreso_vars['monto'].get(),
            'tipo_egreso': self.egreso_vars['tipo_egreso'].get(),
            'descripcion': self.egreso_desc_text.get('1.0', 'end-1c').strip(),
            'beneficiario': self.egreso_vars['beneficiario'].get(),
            'metodo_pago': self.egreso_vars['metodo_pago'].get()
        }

        # Validación simple
        if not datos_egreso['monto'] or not datos_egreso['tipo_egreso'] or not datos_egreso['descripcion']:
            messagebox.showerror("Campos Requeridos", "Monto, Tipo de Egreso y Descripción son obligatorios.")
            return
        
        try:
            float(datos_egreso['monto'])
        except ValueError:
            messagebox.showerror("Dato Inválido", "El monto debe ser un número.")
            return

        resultado = self.finance_controller.registrar_egreso(datos_egreso, self.usuario_actual['id'])

        if resultado['success']:
            messagebox.showinfo("Éxito", resultado['message'])
            self.egreso_form_window.destroy()
            self.cargar_egresos() # Recargar la tabla
        else:
            messagebox.showerror("Error", resultado['message'])
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🛑 Aplicación interrumpida por el usuario")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            messagebox.showerror("Error", f"Error inesperado en la aplicación:\n{e}")
        finally:
            print("👋 Cerrando Gimnasio Athenas...")


# ==================== PUNTO DE ENTRADA ====================

def main():
    """Función principal de la aplicación"""
    try:
        print("🏋️ Iniciando Gimnasio Athenas...")
        app = GimnasioApp()
        app.run()
    except Exception as e:
        print(f"💥 Error fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()