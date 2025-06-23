# main.py - Aplicación Real del Gimnasio Athenas
import tkinter as tk
import tkinter.simpledialog
from tkinter import ttk, messagebox
# Asegúrate de importar DateEntry si aún no está
from tkcalendar import DateEntry
import sys
import os
from datetime import datetime, timedelta

# Importar controladores y vistas
# (Asegúrate de que FinanceController esté importado si vas a usarlo directamente)
from controllers.auth_controller import AuthController
from controllers.user_controller import UserController
from controllers.atleta_controller import AtletaController
from controllers.finance_controller import FinanceController 
from views.login_view import LoginView
from models.database import Database


class GimnasioApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏋️ Gimnasio Athenas - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Maximizado en Windows
        
        # Controladores
        self.auth_controller = AuthController()
        self.user_controller = UserController()
        self.atleta_controller = AtletaController()
        self.finance_controller = FinanceController() 
        self.db = Database()
        
        # Variables de sesión
        self.usuario_actual = None
        self.token_sesion = None
        
        # Configurar estilos
        self.configurar_estilos()
        
        # Verificar conexión a BD e inicializar
        self.inicializar_aplicacion()
        
    
    def configurar_estilos(self):
        """Configura estilos globales de la aplicación"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colores del sistema
        self.colores = {
            'primario': '#1e3a8a',
            'secundario': '#3b82f6', 
            'acento': '#60a5fa',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'fondo': '#f8fafc',
            'texto': '#1f2937'
        }
    
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
        """Crea el header de la aplicación"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título y logo
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left')
        
        title_label = ttk.Label(
            title_frame,
            text="🏋️ GIMNASIO ATHENAS",
            font=('Segoe UI', 20, 'bold')
        )
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Sistema de Gestión Integral",
            font=('Segoe UI', 10),
            foreground='gray'
        )
        subtitle_label.pack(anchor='w')
        
        # Información del usuario
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side='right')
        
        user_label = ttk.Label(
            user_frame,
            text=f"👤 {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
            font=('Segoe UI', 11, 'bold')
        )
        user_label.pack(anchor='e')
        
        role_label = ttk.Label(
            user_frame,
            text=f"🎭 {self.usuario_actual['rol'].replace('_', ' ').title()}",
            font=('Segoe UI', 9),
            foreground='gray'
        )
        role_label.pack(anchor='e')
        
        # Separador
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill='x', pady=(10, 20))
    
    def crear_menu_lateral(self, parent):
        """Crea el menú lateral de navegación"""
        self.menu_frame = ttk.LabelFrame(parent, text="📋 MÓDULOS DEL SISTEMA", padding=10)
        self.menu_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Botones según el rol del usuario
        botones = self.obtener_botones_por_rol()
        
        for texto, comando in botones:
            btn = ttk.Button(
                self.menu_frame,
                text=texto,
                command=comando,
                width=25
            )
            btn.pack(fill='x', pady=2)
        
        # Separador
        ttk.Separator(self.menu_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Botones de sistema
        self.crear_botones_sistema()
    
    
    def obtener_botones_por_rol(self):
        """Retorna los botones del menú según el rol del usuario"""
        rol = self.usuario_actual['rol']
        
        if rol == 'admin_principal':
            return [
                ("👥 Gestión de Usuarios", self.abrir_gestion_usuarios),
                ("🏃‍♂️ Gestión de Atletas", self.abrir_gestion_atletas),
                ("💪 Gestión de Coaches", self.abrir_gestion_coaches),
                ("💰 Gestión de Pagos", self.abrir_gestion_pagos),
                ("💸 Gestión de Egresos", self.abrir_gestion_egresos),
                ("📊 Reportes Financieros", self.abrir_reportes),
                # ("⚙️ Configuración", self.abrir_configuracion),
            ]
        elif rol == 'secretaria':
            return [
                ("🏃‍♂️ Gestión de Atletas", self.abrir_gestion_atletas),
                ("💪 Gestión de Coaches", self.abrir_gestion_coaches),
                ("💰 Gestión de Pagos", self.abrir_gestion_pagos), 
                ("📊 Reportes", self.abrir_reportes)
            ]
        elif rol == 'coach':
            return [
                ("👥 Mis Atletas", self.abrir_mis_atletas),
                ("📋 Asignaciones", self.abrir_asignaciones),
                ("📊 Mi Dashboard", self.abrir_coach_dashboard)
            ]
        elif rol == 'atleta':
            return [
                ("👤 Mi Perfil", self.abrir_mi_perfil),
                ("💰 Mis Pagos", self.abrir_mis_pagos),
                ("💪 Mi Coach", self.abrir_mi_coach)
            ]
        else:
            return [("📊 Dashboard", self.mostrar_dashboard_resumen)]
    
    def crear_botones_sistema(self):
        """Crea botones de sistema (cerrar sesión, etc.)"""
        # Botón de cerrar sesión
        logout_btn = ttk.Button(
            self.menu_frame,
            text="🚪 Cerrar Sesión",
            command=self.cerrar_sesion
        )
        logout_btn.pack(fill='x', pady=5)
    
    def crear_area_trabajo(self, parent):
        """Crea el área principal de trabajo"""
        self.work_frame = ttk.LabelFrame(parent, text="📄 ÁREA DE TRABAJO", padding=10)
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
        
        # Mensaje de bienvenida personalizado
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
        """Limpia el área de trabajo"""
        for widget in self.work_frame.winfo_children():
            widget.destroy()
    
    # ==================== MÉTODOS DE NAVEGACIÓN ====================
    
    def abrir_gestion_usuarios(self):
        """Abre la gestión de usuarios"""
        if not self.verificar_permisos(['admin_principal']):
            return
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
        
        self.edit_btn = ttk.Button(
            buttons_frame,
            text="✏️ Editar",
            command=self.editar_usuario,
            state='disabled'
        )
        self.edit_btn.pack(side='left', padx=2)
        
        self.toggle_btn = ttk.Button(
            buttons_frame,
            text="🔄 Activar/Desactivar",
            command=self.toggle_usuario_estado,
            state='disabled'
        )
        self.toggle_btn.pack(side='left', padx=2)
        
        # Tabla de usuarios
        self.crear_tabla_usuarios()
        
        # Cargar datos iniciales
        self.cargar_usuarios()

    def crear_tabla_usuarios(self):
        """Crea la tabla de usuarios con Treeview"""
        # Frame para la tabla
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Configurar Treeview
        columns = ('ID', 'Nombre', 'Apellido', 'Email', 'Rol', 'Estado', 'Creado')
        self.usuarios_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.usuarios_tree.heading('ID', text='ID')
        self.usuarios_tree.heading('Nombre', text='Nombre')
        self.usuarios_tree.heading('Apellido', text='Apellido')
        self.usuarios_tree.heading('Email', text='Email')
        self.usuarios_tree.heading('Rol', text='Rol')
        self.usuarios_tree.heading('Estado', text='Estado')
        self.usuarios_tree.heading('Creado', text='Fecha Creación')
        
        # Configurar anchos
        self.usuarios_tree.column('ID', width=50, anchor='center')
        self.usuarios_tree.column('Nombre', width=100)
        self.usuarios_tree.column('Apellido', width=100)
        self.usuarios_tree.column('Email', width=200)
        self.usuarios_tree.column('Rol', width=120)
        self.usuarios_tree.column('Estado', width=80, anchor='center')
        self.usuarios_tree.column('Creado', width=120, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.usuarios_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.usuarios_tree.xview)
        self.usuarios_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.usuarios_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
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
        # Limpiar tabla
        for item in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item)
        
        # Usar usuarios filtrados o todos
        usuarios = usuarios_filtrados if usuarios_filtrados is not None else self.usuarios_data
        
        # Llenar tabla
        for usuario in usuarios:
            # Formatear datos
            user_id = usuario[0]
            nombre = usuario[1]
            apellido = usuario[2]
            email = usuario[6]
            rol = usuario[8].replace('_', ' ').title()
            estado = "Activo" if usuario[9] else "Inactivo"
            # Fecha de creación - simple y efectiva
            try:
                if usuario[12]:
                    fecha_str = str(usuario[12])
                    fecha = fecha_str[:10]  # Tomar solo YYYY-MM-DD
                else:
                    fecha = "N/A"
            except:
                fecha = "N/A"
            
            # Insertar fila
            item = self.usuarios_tree.insert('', 'end', values=(
                user_id, nombre, apellido, email, rol, estado, fecha
            ))
            
            # Colorear según estado
            if not usuario[9]:  # Inactivo
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
            messagebox.showwarning("Advertencia", "Selecciona un usuario para editar")
            return
        
        self.abrir_formulario_usuario(modo='editar', usuario=self.usuario_seleccionado)

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


    def abrir_gestion_atletas(self):
        """Abre la gestión de atletas"""
        if not self.verificar_permisos(['admin_principal', 'secretaria']):
            return
        self.mostrar_gestion_atletas()

    def mostrar_gestion_atletas(self):
        """Muestra el módulo completo de gestión de atletas"""
        self.limpiar_area_trabajo()
        
        # Variables para el módulo
        self.atletas_data = []
        self.atleta_seleccionado = None
        
        # Título del módulo
        title_frame = ttk.Frame(self.work_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="🏃‍♂️ GESTIÓN DE ATLETAS",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(side='left')
        
        # Botón de actualizar
        refresh_btn = ttk.Button(
            title_frame,
            text="🔄 Actualizar",
            command=self.cargar_atletas
        )
        refresh_btn.pack(side='right')
        
        # Frame de controles
        controls_frame = ttk.Frame(self.work_frame)
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
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.atletas_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.atletas_tree.xview)
        self.atletas_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.atletas_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
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
                
                # Extraer datos
                atleta_id = atleta_data[0]
                nombre = usuario_data[1]
                apellido = usuario_data[2]
                cedula = atleta_data[2] if len(atleta_data) > 2 else "N/A"
                email = usuario_data[6]
                
                # Plan (por ahora ID, luego podemos mapear a nombres)
                plan = f"Plan {atleta_data[5]}" if len(atleta_data) > 5 else "N/A"
                
                # Coach (por ahora ID, luego podemos mapear a nombres)
                coach_id = atleta_data[6] if len(atleta_data) > 6 else None
                coach = f"Coach {coach_id}" if coach_id else "Sin Coach"
                
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
                    atleta_id, nombre, apellido, cedula, email, plan, coach, estado, vencimiento
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
                    coach_id = atleta_data[6] if len(atleta_data) > 6 else None
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
        ventana.geometry("400x200")
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
        """Abre diálogo para asignar coach"""
        if not self.atleta_seleccionado:
            messagebox.showwarning("Advertencia", "Selecciona un atleta")
            return
        
        # Por ahora un diálogo simple
        nuevo_coach = tk.simpledialog.askstring(
            "Asignar Coach", 
            "Ingresa el ID del coach (o deja vacío para remover):"
        )
        
        if nuevo_coach is not None:  # Usuario no canceló
            try:
                coach_id = int(nuevo_coach) if nuevo_coach.strip() else None
                resultado = self.atleta_controller.asignar_coach(
                    self.atleta_seleccionado['atleta_data'][0], 
                    coach_id, 
                    self.usuario_actual['id']
                )
                if resultado["success"]:
                    messagebox.showinfo("Éxito", resultado["message"])
                    self.cargar_atletas()
                else:
                    messagebox.showerror("Error", resultado["message"])
            except ValueError:
                messagebox.showerror("Error", "ID de coach inválido")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")




    
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



    
    def abrir_gestion_coaches(self):
        """Abre la gestión de coaches"""
        if not self.verificar_permisos(['admin_principal', 'secretaria']):
            return

            
        
    def abrir_gestion_pagos(self):
         """Abre la gestión de pagos"""
        # Se agrega la verificación de permisos y se indenta la línea siguiente
         if not self.verificar_permisos(['admin_principal', 'secretaria']):
            return
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
        """Crea los filtros para la gestión de pagos"""
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

        # Filtros de fecha
        ttk.Label(filter_frame, text="Desde:").pack(side='left', padx=(10, 5))
        self.fecha_desde_pagos = DateEntry(filter_frame, width=10, date_pattern='yyyy-mm-dd')
        self.fecha_desde_pagos.set_date(datetime.now() - timedelta(days=30))
        self.fecha_desde_pagos.pack(side='left', padx=(0, 10))

        ttk.Label(filter_frame, text="Hasta:").pack(side='left', padx=(0, 5))
        self.fecha_hasta_pagos = DateEntry(filter_frame, width=10, date_pattern='yyyy-mm-dd')
        self.fecha_hasta_pagos.set_date(datetime.now())
        self.fecha_hasta_pagos.pack(side='left', padx=(0, 10))

        ttk.Button(filter_frame, text="🔍 Aplicar Fechas", command=self.filtrar_pagos).pack(side='left', padx=(0,20))

        # Botones de Editar y Eliminar
        self.edit_pago_btn = ttk.Button(filter_frame, text="✏️ Editar Pago", command=self._editar_pago_action, state='disabled')
        self.edit_pago_btn.pack(side='left', padx=5)

        self.delete_pago_btn = ttk.Button(filter_frame, text="🗑️ Eliminar Pago", command=self._eliminar_pago_action, state='disabled')
        self.delete_pago_btn.pack(side='left', padx=5)

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
        h_scroll = ttk.Scrollbar(table_frame, orient='horizontal', command=self.pagos_tree.xview)
        self.pagos_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.pagos_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')

        self.pagos_tree.bind('<<TreeviewSelect>>', self.on_pago_selected)

    def cargar_pagos(self):
        """Carga todos los pagos usando el controlador y los muestra en la tabla"""
        try:
            resultado = self.finance_controller.obtener_ingresos_detallados()
            if resultado['success']:
                self.pagos_data = resultado['ingresos']
                self.actualizar_tabla_pagos()
                print(f"✅ Cargados {len(self.pagos_data)} registros de pago.")
            else:
                messagebox.showerror("Error", f"No se pudieron cargar los pagos: {resultado['message']}")
        except Exception as e:
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
        """Filtra los pagos según los criterios de búsqueda y filtros"""
        search_text = self.search_pagos_var.get().lower()
        tipo_pago_filter = self.tipo_pago_filter_var.get()
        fecha_desde = self.fecha_desde_pagos.get_date()
        fecha_hasta = self.fecha_hasta_pagos.get_date()

        pagos_filtrados = []
        for pago in self.pagos_data:
            # Filtro por fecha
            if not (fecha_desde <= pago['fecha_pago'] <= fecha_hasta):
                continue
            
            # Filtro por tipo de pago
            if tipo_pago_filter != "Todos" and tipo_pago_filter.lower() not in pago['tipo_pago'].lower():
                continue

            # Filtro por texto de búsqueda
            texto_busqueda = f"{pago['nombre_atleta']} {pago['descripcion']}".lower()
            if search_text and search_text not in texto_busqueda:
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
        self.mostrar_reportes_financieros()
    # PEGA ESTOS DOS NUEVOS MÉTODOS EN TU CLASE GimnasioApp

    def mostrar_reportes_financieros(self):
        """Crea y muestra la interfaz para el módulo de Reportes Financieros."""
        self.limpiar_area_trabajo()

        # Título del módulo
        ttk.Label(self.work_frame, text="📊 REPORTES FINANCIEROS", font=('Segoe UI', 18, 'bold')).pack(pady=(0, 20))

        # --- Frame de Filtros ---
        filter_frame = ttk.Frame(self.work_frame)
        filter_frame.pack(fill='x', pady=5)

        ttk.Label(filter_frame, text="Desde:").pack(side='left', padx=(0, 5))
        self.reporte_fecha_desde = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.reporte_fecha_desde.set_date(datetime.now() - timedelta(days=30))
        self.reporte_fecha_desde.pack(side='left', padx=(0, 20))

        ttk.Label(filter_frame, text="Hasta:").pack(side='left', padx=(0, 5))
        self.reporte_fecha_hasta = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.reporte_fecha_hasta.set_date(datetime.now())
        self.reporte_fecha_hasta.pack(side='left', padx=(0, 20))

        ttk.Button(filter_frame, text="📈 Generar Reporte", command=self._generar_y_mostrar_reporte_action).pack(side='left')

        ttk.Separator(self.work_frame, orient='horizontal').pack(fill='x', pady=15)

        # --- Frame de Resumen ---
        resumen_frame = ttk.LabelFrame(self.work_frame, text="Resumen del Período", padding=15)
        resumen_frame.pack(fill='x', pady=10)

        # Usamos StringVars para actualizar fácilmente los textos
        self.resumen_ingresos_var = tk.StringVar(value="Total Ingresos: $0.00")
        self.resumen_egresos_var = tk.StringVar(value="Total Egresos: $0.00")
        self.resumen_balance_var = tk.StringVar(value="Balance: $0.00")

        ttk.Label(resumen_frame, textvariable=self.resumen_ingresos_var, font=('Segoe UI', 12, 'bold'), foreground=self.colores['success']).pack(side='left', padx=20)
        ttk.Label(resumen_frame, textvariable=self.resumen_egresos_var, font=('Segoe UI', 12, 'bold'), foreground=self.colores['error']).pack(side='left', padx=20)
        ttk.Label(resumen_frame, textvariable=self.resumen_balance_var, font=('Segoe UI', 14, 'bold'), foreground=self.colores['primario']).pack(side='right', padx=20)

        # --- Frame de Detalles ---
        details_frame = ttk.Frame(self.work_frame)
        details_frame.pack(fill='both', expand=True, pady=10)
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_columnconfigure(1, weight=1) # Dos columnas de igual tamaño

        # Tabla de Desglose de Ingresos
        ingresos_frame = ttk.LabelFrame(details_frame, text="Desglose de Ingresos", padding=10)
        ingresos_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        self.reporte_ingresos_tree = ttk.Treeview(ingresos_frame, columns=('Tipo', 'Monto'), show='headings')
        self.reporte_ingresos_tree.heading('Tipo', text='Tipo de Ingreso')
        self.reporte_ingresos_tree.heading('Monto', text='Monto Total')
        self.reporte_ingresos_tree.column('Monto', anchor='e')
        self.reporte_ingresos_tree.pack(fill='both', expand=True)

        # Tabla de Desglose de Egresos
        egresos_frame = ttk.LabelFrame(details_frame, text="Desglose de Egresos", padding=10)
        egresos_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))

        self.reporte_egresos_tree = ttk.Treeview(egresos_frame, columns=('Tipo', 'Monto'), show='headings')
        self.reporte_egresos_tree.heading('Tipo', text='Tipo de Egreso')
        self.reporte_egresos_tree.heading('Monto', text='Monto Total')
        self.reporte_egresos_tree.column('Monto', anchor='e')
        self.reporte_egresos_tree.pack(fill='both', expand=True)

        # Generar reporte inicial para el último mes
        self._generar_y_mostrar_reporte_action()

    def _generar_y_mostrar_reporte_action(self):
        """Función interna que llama al controlador y actualiza la UI del reporte."""
        fecha_inicio = self.reporte_fecha_desde.get_date()
        fecha_fin = self.reporte_fecha_hasta.get_date()

        if fecha_inicio > fecha_fin:
            messagebox.showerror("Error de Fechas", "La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.")
            return

        try:
            resultado = self.finance_controller.generar_reporte_financiero(fecha_inicio, fecha_fin)

            if not resultado['success']:
                messagebox.showerror("Error al generar reporte", resultado['message'])
                return

            reporte = resultado['reporte']
            resumen = reporte['resumen']
            desglose_ingresos = reporte['desglose_ingresos']
            desglose_egresos = reporte['desglose_egresos']

            self.resumen_ingresos_var.set(f"Total Ingresos: ${resumen['total_ingresos']:.2f}")
            self.resumen_egresos_var.set(f"Total Egresos: ${resumen['total_egresos']:.2f}")
            balance_color = self.colores['success'] if resumen['balance'] >= 0 else self.colores['error']
            self.resumen_balance_var.set(f"Balance: ${resumen['balance']:.2f}")

            self.reporte_ingresos_tree.delete(*self.reporte_ingresos_tree.get_children())
            for tipo, monto in desglose_ingresos.items():
                tipo_legible = tipo.replace('_', ' ').title()
                self.reporte_ingresos_tree.insert('', 'end', values=(tipo_legible, f"${monto:.2f}"))

            # Actualizar Tabla de Egresos
            self.reporte_egresos_tree.delete(*self.reporte_egresos_tree.get_children())
            for tipo, monto in desglose_egresos.items():
                tipo_legible = tipo.replace('_', ' ').title()
                self.reporte_egresos_tree.insert('', 'end', values=(tipo_legible, f"${monto:.2f}"))

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error al procesar el reporte: {e}")
            import traceback
            traceback.print_exc()
        
    
    # def abrir_configuracion(self):
    #     """Abre la configuración"""
    #     if not self.verificar_permisos(['admin_principal']):
    #         return
    #     self.mostrar_modulo_pendiente("⚙️ CONFIGURACIÓN", 
    #                                  "Módulo para configurar parámetros del sistema.")
    
    
    # Métodos específicos para otros roles
    def abrir_mis_atletas(self):
        """Abre los atletas del coach"""
        self.mostrar_modulo_pendiente("👥 MIS ATLETAS", 
                                     "Módulo para ver y gestionar tus atletas asignados.")
    
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
        h_scroll = ttk.Scrollbar(table_frame, orient='horizontal', command=self.egresos_tree.xview)
        self.egresos_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.egresos_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')

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