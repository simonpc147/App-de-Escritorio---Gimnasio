# Vista principal - Coordinador de toda la aplicación
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Importar controladores
from controllers.auth_controller import AuthController
from controllers.user_controller import UserController
from controllers.finance_controller import FinanceController
from controllers.atleta_controller import AtletaController
from controllers.coach_controller import CoachController

# Importar vistas (se importarán cuando estén listas)
# from views.login_view import LoginView
# from views.admin_view import AdminView
# from views.secretaria_view import SecretariaView
# from views.coach_view import CoachView


class MainView:
    def __init__(self):
        # Configuración inicial
        self.root = tk.Tk()
        self.configurar_ventana_principal()
        
        # Controladores
        self.auth_controller = AuthController()
        self.user_controller = UserController()
        self.finance_controller = FinanceController()
        self.atleta_controller = AtletaController()
        self.coach_controller = CoachController()
        
        # Variables de sesión
        self.usuario_actual = None
        self.token_sesion = None
        self.vista_actual = None
        
        # Configurar estilos
        self.configurar_estilos()
        
        # Iniciar con login
        self.mostrar_login()
        
    def configurar_ventana_principal(self):
        """Configura la ventana principal de la aplicación"""
        self.root.title("🏋️ Gimnasio Athenas - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Centrar ventana en pantalla
        self.centrar_ventana()
        
        # Configurar cierre de aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        # Configurar ícono (si existe)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass  # Si no existe el ícono, continuar sin él
        
        # Frame principal que contendrá todas las vistas
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def configurar_estilos(self):
        """Configura los estilos personalizados de ttk"""
        style = ttk.Style()
        
        # Tema moderno
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # Colores del gimnasio
        self.colores = {
            'primario': '#2E3440',      # Azul oscuro
            'secundario': '#5E81AC',     # Azul claro
            'acento': '#88C0D0',        # Azul agua
            'exito': '#A3BE8C',         # Verde
            'advertencia': '#EBCB8B',   # Amarillo
            'error': '#BF616A',         # Rojo
            'fondo': '#ECEFF4',         # Gris claro
            'texto': '#2E3440'          # Texto oscuro
        }
        
        # Configurar estilos personalizados
        
        # Botones principales
        style.configure(
            'Primary.TButton',
            background=self.colores['primario'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 8)
        )
        
        style.map(
            'Primary.TButton',
            background=[('active', self.colores['secundario'])]
        )
        
        # Botones de éxito
        style.configure(
            'Success.TButton',
            background=self.colores['exito'],
            foreground='white',
            font=('Segoe UI', 9, 'bold'),
            padding=(10, 5)
        )
        
        # Botones de advertencia
        style.configure(
            'Warning.TButton',
            background=self.colores['advertencia'],
            foreground=self.colores['texto'],
            font=('Segoe UI', 9, 'bold'),
            padding=(10, 5)
        )
        
        # Botones de error
        style.configure(
            'Danger.TButton',
            background=self.colores['error'],
            foreground='white',
            font=('Segoe UI', 9, 'bold'),
            padding=(10, 5)
        )
        
        # Labels de título
        style.configure(
            'Title.TLabel',
            font=('Segoe UI', 16, 'bold'),
            foreground=self.colores['primario'],
            background=self.colores['fondo']
        )
        
        # Labels de subtítulo
        style.configure(
            'Subtitle.TLabel',
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colores['secundario']
        )
        
        # Entries mejorados
        style.configure(
            'Custom.TEntry',
            font=('Segoe UI', 10),
            padding=5
        )
        
        # Treeview personalizado
        style.configure(
            'Custom.Treeview',
            font=('Segoe UI', 9),
            rowheight=25
        )
        
        style.configure(
            'Custom.Treeview.Heading',
            font=('Segoe UI', 10, 'bold'),
            background=self.colores['primario'],
            foreground='white'
        )
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    # ==================== GESTIÓN DE VISTAS ====================
    
    def limpiar_frame_principal(self):
        """Limpia el frame principal para mostrar nueva vista"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def mostrar_login(self):
        """Muestra la vista de login"""
        self.limpiar_frame_principal()
        self.vista_actual = "login"
        
        # Crear vista de login inline por ahora
        self.crear_vista_login()
    
    def mostrar_dashboard(self, rol_usuario):
        """Muestra el dashboard correspondiente según el rol"""
        dashboards = {
            'admin_principal': self.mostrar_admin_dashboard,
            'secretaria': self.mostrar_secretaria_dashboard,
            'coach': self.mostrar_coach_dashboard,
            'atleta': self.mostrar_atleta_dashboard
        }
        
        dashboard_func = dashboards.get(rol_usuario)
        if dashboard_func:
            dashboard_func()
        else:
            self.mostrar_error("Rol de usuario no reconocido")
    
    def mostrar_admin_dashboard(self):
        """Muestra el dashboard del administrador principal"""
        self.limpiar_frame_principal()
        self.vista_actual = "admin"
        
        # Por ahora crear inline, luego usar AdminView
        self.crear_dashboard_temporal("Administrador Principal", "admin")
    
    def mostrar_secretaria_dashboard(self):
        """Muestra el dashboard de secretaria"""
        self.limpiar_frame_principal()
        self.vista_actual = "secretaria"
        
        # Por ahora crear inline, luego usar SecretariaView
        self.crear_dashboard_temporal("Secretaria", "secretaria")
    
    def mostrar_coach_dashboard(self):
        """Muestra el dashboard de coach"""
        self.limpiar_frame_principal()
        self.vista_actual = "coach"
        
        # Por ahora crear inline, luego usar CoachView
        self.crear_dashboard_temporal("Coach", "coach")
    
    def mostrar_atleta_dashboard(self):
        """Muestra el dashboard de atleta"""
        self.limpiar_frame_principal()
        self.vista_actual = "atleta"
        
        # Dashboard básico para atletas
        self.crear_dashboard_temporal("Atleta", "atleta")
    
    # ==================== VISTAS TEMPORALES (inline) ====================
    
    def crear_vista_login(self):
        """Crea la vista de login temporalmente inline"""
        # Frame central para login
        login_frame = ttk.Frame(self.main_frame)
        login_frame.pack(expand=True)
        
        # Título
        titulo = ttk.Label(login_frame, text="🏋️ Gimnasio Athenas", style='Title.TLabel')
        titulo.pack(pady=(0, 10))
        
        subtitulo = ttk.Label(login_frame, text="Sistema de Gestión", style='Subtitle.TLabel')
        subtitulo.pack(pady=(0, 30))
        
        # Frame del formulario
        form_frame = ttk.LabelFrame(login_frame, text="Iniciar Sesión", padding=20)
        form_frame.pack(padx=50, pady=20)
        
        # Email
        ttk.Label(form_frame, text="Email:").pack(anchor='w', pady=(0, 5))
        self.email_entry = ttk.Entry(form_frame, style='Custom.TEntry', width=30)
        self.email_entry.pack(pady=(0, 15))
        
        # Contraseña
        ttk.Label(form_frame, text="Contraseña:").pack(anchor='w', pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, style='Custom.TEntry', show="*", width=30)
        self.password_entry.pack(pady=(0, 20))
        
        # Botón login
        login_btn = ttk.Button(
            form_frame, 
            text="Iniciar Sesión", 
            style='Primary.TButton',
            command=self.procesar_login
        )
        login_btn.pack(pady=10)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.procesar_login())
        
        # Focus en email
        self.email_entry.focus()
    
    def crear_dashboard_temporal(self, titulo_rol, rol):
        """Crea un dashboard temporal básico"""
        # Header con información del usuario
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título del dashboard
        titulo = ttk.Label(header_frame, text=f"Dashboard - {titulo_rol}", style='Title.TLabel')
        titulo.pack(side='left')
        
        # Información del usuario y logout
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side='right')
        
        if self.usuario_actual:
            user_info = ttk.Label(
                user_frame, 
                text=f"👤 {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}"
            )
            user_info.pack(side='left', padx=(0, 10))
        
        logout_btn = ttk.Button(
            user_frame, 
            text="Cerrar Sesión", 
            style='Warning.TButton',
            command=self.cerrar_sesion
        )
        logout_btn.pack(side='right')
        
        # Separador
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Contenido principal basado en rol
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill='both', expand=True)
        
        if rol == "admin":
            self.crear_contenido_admin(content_frame)
        elif rol == "secretaria":
            self.crear_contenido_secretaria(content_frame)
        elif rol == "coach":
            self.crear_contenido_coach(content_frame)
        elif rol == "atleta":
            self.crear_contenido_atleta(content_frame)
    
    def crear_contenido_admin(self, parent):
        """Contenido temporal para admin"""
        # Grid de estadísticas rápidas
        stats_frame = ttk.LabelFrame(parent, text="Resumen General", padding=15)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Estadísticas en grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        # Configurar columnas
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        
        # Estadísticas ejemplo (luego conectar con controladores)
        stats = [
            ("👥 Total Usuarios", "0"),
            ("🏃 Atletas Activos", "0"),
            ("💰 Ingresos del Mes", "$0"),
            ("📊 Balance", "$0")
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = ttk.Frame(stats_grid)
            stat_frame.grid(row=0, column=i, padx=10, pady=5, sticky='ew')
            
            ttk.Label(stat_frame, text=label, style='Subtitle.TLabel').pack()
            ttk.Label(stat_frame, text=value, font=('Segoe UI', 14, 'bold')).pack()
        
        # Menú de acciones principales
        actions_frame = ttk.LabelFrame(parent, text="Acciones Principales", padding=15)
        actions_frame.pack(fill='x', pady=(0, 20))
        
        # Botones de acción en grid
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack()
        
        actions = [
            ("👩‍💼 Gestionar Secretarias", lambda: self.mostrar_mensaje("Funcionalidad en desarrollo")),
            ("📊 Reportes Financieros", lambda: self.mostrar_mensaje("Funcionalidad en desarrollo")),
            ("⚙️ Configuración", lambda: self.mostrar_mensaje("Funcionalidad en desarrollo")),
            ("👥 Ver Sesiones Activas", lambda: self.mostrar_mensaje("Funcionalidad en desarrollo"))
        ]
        
        for i, (text, command) in enumerate(actions):
            row = i // 2
            col = i % 2
            btn = ttk.Button(actions_grid, text=text, command=command, style='Primary.TButton')
            btn.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
        
        # Configurar columnas del grid
        actions_grid.columnconfigure(0, weight=1)
        actions_grid.columnconfigure(1, weight=1)
    
    def crear_contenido_secretaria(self, parent):
        """Contenido temporal para secretaria"""
        # Panel de acciones principales
        actions_frame = ttk.LabelFrame(parent, text="Operaciones Diarias", padding=15)
        actions_frame.pack(fill='x', pady=(0, 20))
        
        # Grid de botones principales
        btn_grid = ttk.Frame(actions_frame)
        btn_grid.pack(fill='x')
        
        # Configurar grid
        for i in range(3):
            btn_grid.columnconfigure(i, weight=1)
        
        # Botones principales
        botones = [
            ("➕ Registrar Atleta", "Success.TButton", lambda: self.mostrar_mensaje("Abrir formulario de registro")),
            ("💰 Procesar Pago", "Primary.TButton", lambda: self.mostrar_mensaje("Abrir sistema de pagos")),
            ("👨‍🏫 Gestionar Coaches", "Primary.TButton", lambda: self.mostrar_mensaje("Abrir gestión de coaches")),
            ("📋 Ver Atletas", "Primary.TButton", lambda: self.mostrar_mensaje("Abrir lista de atletas")),
            ("💸 Registrar Gasto", "Warning.TButton", lambda: self.mostrar_mensaje("Abrir registro de gastos")),
            ("📊 Reportes", "Primary.TButton", lambda: self.mostrar_mensaje("Abrir reportes"))
        ]
        
        for i, (text, style, command) in enumerate(botones):
            row = i // 3
            col = i % 3
            btn = ttk.Button(btn_grid, text=text, style=style, command=command)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Alertas y notificaciones
        alerts_frame = ttk.LabelFrame(parent, text="⚠️ Alertas y Notificaciones", padding=15)
        alerts_frame.pack(fill='both', expand=True)
        
        # Lista de alertas ejemplo
        alerts_text = tk.Text(alerts_frame, height=10, font=('Segoe UI', 9))
        alerts_text.pack(fill='both', expand=True)
        
        # Scrollbar para las alertas
        scrollbar = ttk.Scrollbar(alerts_frame, orient='vertical', command=alerts_text.yview)
        scrollbar.pack(side='right', fill='y')
        alerts_text.config(yscrollcommand=scrollbar.set)
        
        # Insertar alertas ejemplo
        alerts_text.insert('end', "🔔 Sistema cargado correctamente\\n")
        alerts_text.insert('end', "ℹ️ No hay alertas de membresías vencidas\\n")
        alerts_text.insert('end', "✅ Todos los sistemas funcionando correctamente\\n")
        alerts_text.config(state='disabled')
    
    def crear_contenido_coach(self, parent):
        """Contenido temporal para coach"""
        # Mis atletas
        atletas_frame = ttk.LabelFrame(parent, text="Mis Atletas Asignados", padding=15)
        atletas_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Aquí iría la lista de atletas del coach
        info_label = ttk.Label(atletas_frame, text="📋 Lista de atletas asignados aparecerá aquí")
        info_label.pack(pady=20)
        
        # Acciones rápidas
        actions_frame = ttk.LabelFrame(parent, text="Acciones Rápidas", padding=15)
        actions_frame.pack(fill='x')
        
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="👥 Ver Mis Atletas", style='Primary.TButton',
                  command=lambda: self.mostrar_mensaje("Ver atletas asignados")).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="📝 Actualizar Perfil", style='Primary.TButton',
                  command=lambda: self.mostrar_mensaje("Actualizar perfil")).pack(side='left', padx=5)
    
    def crear_contenido_atleta(self, parent):
        """Contenido temporal para atleta"""
        # Info personal
        info_frame = ttk.LabelFrame(parent, text="Mi Información", padding=15)
        info_frame.pack(fill='x', pady=(0, 20))
        
        info_label = ttk.Label(info_frame, text="👤 Información personal y de membresía")
        info_label.pack(pady=10)
        
        # Estado de membresía
        membresia_frame = ttk.LabelFrame(parent, text="Estado de Membresía", padding=15)
        membresia_frame.pack(fill='x')
        
        status_label = ttk.Label(membresia_frame, text="✅ Membresía Activa", 
                               foreground=self.colores['exito'], font=('Segoe UI', 12, 'bold'))
        status_label.pack(pady=10)
    
    # ==================== LÓGICA DE AUTENTICACIÓN ====================
    
    def procesar_login(self):
        """Procesa el intento de login"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not email or not password:
            self.mostrar_error("Por favor ingresa email y contraseña")
            return
        
        # Intentar login
        try:
            # Obtener IP (para desktop será localhost)
            ip_cliente = "127.0.0.1"
            
            resultado = self.auth_controller.iniciar_sesion(email, password, ip_cliente)
            
            if resultado["success"]:
                # Guardar datos de sesión
                self.usuario_actual = resultado["usuario"]
                self.token_sesion = resultado["token_sesion"]
                
                # Mostrar mensaje de bienvenida
                self.mostrar_exito(resultado["message"])
                
                # Redirigir al dashboard correspondiente
                self.mostrar_dashboard(self.usuario_actual["rol"])
                
            else:
                self.mostrar_error(resultado["message"])
                # Limpiar campos
                self.password_entry.delete(0, 'end')
                
        except Exception as e:
            self.mostrar_error(f"Error de conexión: {str(e)}")
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        if self.token_sesion:
            try:
                resultado = self.auth_controller.cerrar_sesion(self.token_sesion)
                if resultado["success"]:
                    self.mostrar_exito(resultado["message"])
            except Exception as e:
                print(f"Error al cerrar sesión: {e}")
        
        # Limpiar datos de sesión
        self.usuario_actual = None
        self.token_sesion = None
        
        # Volver al login
        self.mostrar_login()
    
    # ==================== UTILIDADES ====================
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        messagebox.showerror("Error", mensaje)
    
    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito"""
        messagebox.showinfo("Éxito", mensaje)
    
    def mostrar_advertencia(self, mensaje):
        """Muestra un mensaje de advertencia"""
        messagebox.showwarning("Advertencia", mensaje)
    
    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo"""
        messagebox.showinfo("Información", mensaje)
    
    def confirmar_accion(self, mensaje):
        """Solicita confirmación para una acción"""
        return messagebox.askyesno("Confirmar", mensaje)
    
    def cerrar_aplicacion(self):
        """Cierra la aplicación"""
        if self.token_sesion:
            # Cerrar sesión antes de salir
            try:
                self.auth_controller.cerrar_sesion(self.token_sesion)
            except:
                pass
        
        if self.confirmar_accion("¿Estás seguro de que quieres cerrar la aplicación?"):
            self.root.destroy()
            sys.exit()
    
    def ejecutar(self):
        """Inicia la aplicación"""
        self.root.mainloop()


# ==================== EJECUCIÓN PRINCIPAL ====================

if __name__ == "__main__":
    try:
        app = MainView()
        app.ejecutar()
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)