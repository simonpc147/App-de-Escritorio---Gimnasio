# Vista de Login - Pantalla de autenticación
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time


class LoginView:
    def __init__(self, parent_frame, auth_controller, main_view_callback):
        self.parent_frame = parent_frame
        self.auth_controller = auth_controller
        self.main_view_callback = main_view_callback
        
        # Variables de control
        self.intentos_login = 0
        self.max_intentos = 5
        self.tiempo_bloqueo = 300  # 5 minutos
        self.bloqueado_hasta = None
        
        # Variables de UI
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar()
        self.show_password_var = tk.BooleanVar()
        
        # Configurar estilos específicos del login
        self.configurar_estilos()
        
        # Crear la interfaz
        self.crear_interfaz()
        
        # Cargar credenciales guardadas si existen
        self.cargar_credenciales_guardadas()
        
        # Configurar eventos
        self.configurar_eventos()
    
    def configurar_estilos(self):
        """Configura estilos específicos para la vista de login"""
        self.style = ttk.Style()
        
        # Colores específicos del login
        self.colores = {
            'fondo_principal': '#1e3a8a',      # Azul profundo
            'fondo_secundario': '#3b82f6',     # Azul medio
            'acento': '#60a5fa',               # Azul claro
            'texto_claro': '#ffffff',          # Blanco
            'texto_oscuro': '#1f2937',         # Gris oscuro
            'success': '#10b981',              # Verde
            'warning': '#f59e0b',              # Naranja
            'error': '#ef4444',                # Rojo
            'card_bg': '#f8fafc'               # Fondo de tarjeta
        }
        
        # Estilo para el frame principal del login
        self.style.configure(
            'Login.TFrame',
            background=self.colores['fondo_principal']
        )
        
        # Estilo para la tarjeta de login
        self.style.configure(
            'LoginCard.TFrame',
            background=self.colores['card_bg'],
            relief='solid',
            borderwidth=1
        )
        
        # Título principal
        self.style.configure(
            'LoginTitle.TLabel',
            background=self.colores['card_bg'],
            foreground=self.colores['fondo_principal'],
            font=('Segoe UI', 24, 'bold')
        )
        
        # Subtítulo
        self.style.configure(
            'LoginSubtitle.TLabel',
            background=self.colores['card_bg'],
            foreground=self.colores['fondo_secundario'],
            font=('Segoe UI', 12)
        )
        
        # Labels de campos
        self.style.configure(
            'LoginLabel.TLabel',
            background=self.colores['card_bg'],
            foreground=self.colores['texto_oscuro'],
            font=('Segoe UI', 10, 'bold')
        )
        
        # Entries del login
        self.style.configure(
            'Login.TEntry',
            font=('Segoe UI', 11),
            padding=(10, 8),
            relief='solid',
            borderwidth=1
        )
        
        # Botón principal de login
        self.style.configure(
            'LoginButton.TButton',
            background=self.colores['fondo_principal'],
            foreground=self.colores['texto_claro'],
            font=('Segoe UI', 11, 'bold'),
            padding=(20, 10),
            relief='flat'
        )
        
        self.style.map(
            'LoginButton.TButton',
            background=[
                ('active', self.colores['fondo_secundario']),
                ('disabled', '#94a3b8')
            ]
        )
        
        # Botón secundario
        self.style.configure(
            'SecondaryButton.TButton',
            background=self.colores['card_bg'],
            foreground=self.colores['fondo_principal'],
            font=('Segoe UI', 9),
            padding=(10, 5),
            relief='solid',
            borderwidth=1
        )
        
        # Checkbutton personalizado
        self.style.configure(
            'Login.TCheckbutton',
            background=self.colores['card_bg'],
            foreground=self.colores['texto_oscuro'],
            font=('Segoe UI', 9)
        )
    
    def crear_interfaz(self):
        """Crea la interfaz completa de login"""
        # Frame principal con fondo azul
        self.main_frame = ttk.Frame(self.parent_frame, style='Login.TFrame')
        self.main_frame.pack(fill='both', expand=True)
        
        # Contenedor central
        self.center_container = ttk.Frame(self.main_frame, style='Login.TFrame')
        self.center_container.pack(expand=True)
        
        # Crear elementos de la interfaz
        self.crear_header()
        self.crear_formulario_login()
        self.crear_footer()
    
    def crear_header(self):
        """Crea el header con logo y título"""
        # Frame del header
        header_frame = ttk.Frame(self.center_container, style='Login.TFrame')
        header_frame.pack(pady=(50, 30))
        
        # Logo del gimnasio (emoji por ahora, luego imagen)
        logo_frame = ttk.Frame(header_frame, style='Login.TFrame')
        logo_frame.pack(pady=(0, 20))
        
        # Crear logo circular con emoji
        logo_canvas = tk.Canvas(
            logo_frame, 
            width=100, 
            height=100, 
            bg=self.colores['acento'],
            highlightthickness=0
        )
        logo_canvas.pack()
        
        # Dibujar círculo
        logo_canvas.create_oval(10, 10, 90, 90, fill=self.colores['card_bg'], outline=self.colores['fondo_principal'], width=3)
        logo_canvas.create_text(50, 50, text="🏋️", font=('Segoe UI', 30))
        
        # Título principal
        title_label = ttk.Label(
            header_frame,
            text="GIMNASIO ATHENAS",
            style='LoginTitle.TLabel'
        )
        title_label.pack()
        
        # Subtítulo
        subtitle_label = ttk.Label(
            header_frame,
            text="Sistema de Gestión Integral",
            style='LoginSubtitle.TLabel'
        )
        subtitle_label.pack(pady=(5, 0))
    
    def crear_formulario_login(self):
        """Crea el formulario de login"""
        # Tarjeta principal del formulario
        self.card_frame = ttk.Frame(self.center_container, style='LoginCard.TFrame', padding=40)
        self.card_frame.pack(pady=20)
        
        # Título del formulario
        form_title = ttk.Label(
            self.card_frame,
            text="Iniciar Sesión",
            style='LoginTitle.TLabel'
        )
        form_title.pack(pady=(0, 30))
        
        # Campo de email
        self.crear_campo_email()
        
        # Campo de contraseña
        self.crear_campo_password()
        
        # Opciones adicionales
        self.crear_opciones_adicionales()
        
        # Botones
        self.crear_botones()
        
        # Información de estado
        self.crear_info_estado()
    
    def crear_campo_email(self):
        """Crea el campo de email"""
        email_frame = ttk.Frame(self.card_frame, style='LoginCard.TFrame')
        email_frame.pack(fill='x', pady=(0, 20))
        
        # Label
        email_label = ttk.Label(
            email_frame,
            text="📧 Correo Electrónico",
            style='LoginLabel.TLabel'
        )
        email_label.pack(anchor='w', pady=(0, 8))
        
        # Entry
        self.email_entry = ttk.Entry(
            email_frame,
            textvariable=self.email_var,
            style='Login.TEntry',
            width=30
        )
        self.email_entry.pack(fill='x')
        
        # Placeholder behavior
        self.email_entry.bind('<FocusIn>', self.on_email_focus_in)
        self.email_entry.bind('<FocusOut>', self.on_email_focus_out)
        
        # Validación en tiempo real
        self.email_var.trace('w', self.validar_campos)
    
    def crear_campo_password(self):
        """Crea el campo de contraseña"""
        password_frame = ttk.Frame(self.card_frame, style='LoginCard.TFrame')
        password_frame.pack(fill='x', pady=(0, 20))
        
        # Label con opción de mostrar/ocultar
        label_frame = ttk.Frame(password_frame, style='LoginCard.TFrame')
        label_frame.pack(fill='x', pady=(0, 8))
        
        password_label = ttk.Label(
            label_frame,
            text="🔐 Contraseña",
            style='LoginLabel.TLabel'
        )
        password_label.pack(side='left')
        
        # Checkbox para mostrar contraseña
        show_password_check = ttk.Checkbutton(
            label_frame,
            text="Mostrar",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            style='Login.TCheckbutton'
        )
        show_password_check.pack(side='right')
        
        # Entry de contraseña
        self.password_entry = ttk.Entry(
            password_frame,
            textvariable=self.password_var,
            style='Login.TEntry',
            show="●",
            width=30
        )
        self.password_entry.pack(fill='x')
        
        # Validación en tiempo real
        self.password_var.trace('w', self.validar_campos)
    
    def crear_opciones_adicionales(self):
        """Crea opciones adicionales como recordar credenciales"""
        options_frame = ttk.Frame(self.card_frame, style='LoginCard.TFrame')
        options_frame.pack(fill='x', pady=(0, 30))
        
        # Recordar credenciales
        remember_check = ttk.Checkbutton(
            options_frame,
            text="🔄 Recordar mis credenciales",
            variable=self.remember_var,
            style='Login.TCheckbutton'
        )
        remember_check.pack(side='left')
        
        # Link de ayuda (simulado)
        help_label = ttk.Label(
            options_frame,
            text="¿Olvidaste tu contraseña?",
            style='LoginSubtitle.TLabel',
            cursor='hand2'
        )
        help_label.pack(side='right')
        help_label.bind('<Button-1>', self.mostrar_ayuda_password)
    
    def crear_botones(self):
        """Crea los botones del formulario"""
        buttons_frame = ttk.Frame(self.card_frame, style='LoginCard.TFrame')
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        # Botón principal de login
        self.login_button = ttk.Button(
            buttons_frame,
            text="🚀 INICIAR SESIÓN",
            style='LoginButton.TButton',
            command=self.procesar_login,
            state='disabled'
        )
        self.login_button.pack(fill='x', pady=(0, 15))
        
        # Frame para botones secundarios
        secondary_buttons = ttk.Frame(buttons_frame, style='LoginCard.TFrame')
        secondary_buttons.pack(fill='x')
        
       
        
        # Botón de información del sistema
        info_button = ttk.Button(
            secondary_buttons,
            text="ℹ️ Información",
            style='SecondaryButton.TButton',
            command=self.mostrar_info_sistema
        )
        info_button.pack(side='right')
    
    def crear_info_estado(self):
        """Crea la sección de información de estado"""
        # Frame para información de estado
        self.status_frame = ttk.Frame(self.card_frame, style='LoginCard.TFrame')
        self.status_frame.pack(fill='x')
        
        # Label de estado (inicialmente oculto)
        self.status_label = ttk.Label(
            self.status_frame,
            text="",
            style='LoginSubtitle.TLabel',
            wraplength=300
        )
        self.status_label.pack()
        
        # Barra de progreso (para cargas)
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=300
        )
        # No se empaqueta inicialmente
    
    def crear_footer(self):
        """Crea el footer con información adicional"""
        footer_frame = ttk.Frame(self.center_container, style='Login.TFrame')
        footer_frame.pack(side='bottom', pady=30)
        
        # Información del sistema
        info_text = "🔒 Sistema Seguro | 📱 Versión 1.0 | 🏢 Gimnasio Athenas 2024"
        footer_label = ttk.Label(
            footer_frame,
            text=info_text,
            font=('Segoe UI', 8),
            foreground=self.colores['acento'],
            background=self.colores['fondo_principal']
        )
        footer_label.pack()
    
    def configurar_eventos(self):
        """Configura eventos de teclado y otros"""
        # Enter en cualquier campo ejecuta login
        self.email_entry.bind('<Return>', lambda e: self.procesar_login())
        self.password_entry.bind('<Return>', lambda e: self.procesar_login())
        
        # Tab navigation
        self.email_entry.bind('<Tab>', lambda e: self.password_entry.focus())
        
        # Focus inicial
        self.parent_frame.after(100, lambda: self.email_entry.focus())
    
    # ==================== LÓGICA DE AUTENTICACIÓN ====================
    
    def procesar_login(self):
        """Procesa el intento de login"""
        if not self.validar_formulario():
            return
        
        # Verificar si está bloqueado
        if self.esta_bloqueado():
            tiempo_restante = self.tiempo_restante_bloqueo()
            self.mostrar_estado_error(f"⏰ Acceso bloqueado. Intenta en {tiempo_restante} minutos")
            return
        
        # Mostrar estado de carga
        self.mostrar_estado_carga("🔐 Verificando credenciales...")
        
        # Deshabilitar botón durante el proceso
        self.login_button.config(state='disabled')
        
        # Ejecutar login en hilo separado para no bloquear UI
        threading.Thread(target=self.ejecutar_login, daemon=True).start()
    
    def ejecutar_login(self):
        """Ejecuta el login en un hilo separado"""
        try:
            email = self.email_var.get().strip()
            password = self.password_var.get()
            
            # Simular delay de red (opcional)
            time.sleep(0.5)
            
            # Intentar autenticación
            resultado = self.auth_controller.iniciar_sesion(email, password, "127.0.0.1")
            
            # Volver al hilo principal para actualizar UI
            self.parent_frame.after(0, lambda: self.manejar_resultado_login(resultado))
            
        except Exception as e:
            self.parent_frame.after(0, lambda: self.manejar_error_login(str(e)))
    
    def manejar_resultado_login(self, resultado):
        """Maneja el resultado del login en el hilo principal"""
        # Ocultar estado de carga
        self.ocultar_estado_carga()
        
        if resultado["success"]:
            # Login exitoso
            self.mostrar_estado_exito("✅ ¡Bienvenido! Cargando dashboard...")
            
            # Guardar credenciales si está marcado
            if self.remember_var.get():
                self.guardar_credenciales()
            
            # Reset intentos
            self.intentos_login = 0
            
            # Callback al main view con delay para mostrar mensaje
            self.parent_frame.after(1500, lambda: self.main_view_callback(resultado))
            
        else:
            # Login fallido
            self.intentos_login += 1
            self.mostrar_estado_error(f"❌ {resultado['message']}")
            
            # Verificar si debe bloquear
            if self.intentos_login >= self.max_intentos:
                self.bloquear_acceso()
            
            # Limpiar contraseña
            self.password_var.set("")
            
            # Reactivar botón
            self.login_button.config(state='normal')
            
            # Focus en contraseña
            self.password_entry.focus()
    
    def manejar_error_login(self, error):
        """Maneja errores de conexión"""
        self.ocultar_estado_carga()
        self.mostrar_estado_error(f"🔌 Error de conexión: {error}")
        self.login_button.config(state='normal')
    
   
    
    # ==================== VALIDACIONES ====================
    
    def validar_formulario(self):
        """Valida el formulario antes del login"""
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        if not email:
            self.mostrar_estado_error("📧 Por favor ingresa tu email")
            self.email_entry.focus()
            return False
        
        if "@" not in email:
            self.mostrar_estado_error("📧 Email inválido")
            self.email_entry.focus()
            return False
        
        if not password:
            self.mostrar_estado_error("🔐 Por favor ingresa tu contraseña")
            self.password_entry.focus()
            return False
        
        if len(password) < 3:
            self.mostrar_estado_error("🔐 Contraseña muy corta")
            self.password_entry.focus()
            return False
        
        return True
    
    def validar_campos(self, *args):
        """Valida campos en tiempo real y habilita/deshabilita botón"""
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        # Habilitar botón solo si ambos campos tienen contenido válido
        if email and "@" in email and password and len(password) >= 3:
            self.login_button.config(state='normal')
        else:
            self.login_button.config(state='disabled')
    
    # ==================== CONTROL DE BLOQUEO ====================
    
    def esta_bloqueado(self):
        """Verifica si el acceso está bloqueado"""
        if self.bloqueado_hasta is None:
            return False
        return time.time() < self.bloqueado_hasta
    
    def bloquear_acceso(self):
        """Bloquea el acceso por tiempo determinado"""
        self.bloqueado_hasta = time.time() + self.tiempo_bloqueo
        tiempo_mins = self.tiempo_bloqueo // 60
        self.mostrar_estado_error(f"🔒 Demasiados intentos fallidos. Acceso bloqueado por {tiempo_mins} minutos")
        
        # Deshabilitar campos
        self.email_entry.config(state='disabled')
        self.password_entry.config(state='disabled')
        self.login_button.config(state='disabled')
        
        # Programar desbloqueo
        self.parent_frame.after(self.tiempo_bloqueo * 1000, self.desbloquear_acceso)
    
    def desbloquear_acceso(self):
        """Desbloquea el acceso"""
        self.bloqueado_hasta = None
        self.intentos_login = 0
        
        # Rehabilitar campos
        self.email_entry.config(state='normal')
        self.password_entry.config(state='normal')
        
        self.mostrar_estado_exito("🔓 Acceso desbloqueado. Puedes intentar nuevamente")
        
        # Revalidar campos
        self.validar_campos()
    
    def tiempo_restante_bloqueo(self):
        """Calcula tiempo restante de bloqueo en minutos"""
        if self.bloqueado_hasta is None:
            return 0
        restante = max(0, self.bloqueado_hasta - time.time())
        return int(restante // 60) + 1
    
    # ==================== MANEJO DE ESTADOS VISUALES ====================
    
    def mostrar_estado_carga(self, mensaje):
        """Muestra estado de carga"""
        self.status_label.config(text=mensaje, foreground=self.colores['fondo_secundario'])
        self.progress_bar.pack(pady=(10, 0))
        self.progress_bar.start(10)
    
    def ocultar_estado_carga(self):
        """Oculta estado de carga"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
    
    def mostrar_estado_error(self, mensaje):
        """Muestra mensaje de error"""
        self.status_label.config(text=mensaje, foreground=self.colores['error'])
        # Auto-limpiar después de 5 segundos
        self.parent_frame.after(5000, self.limpiar_estado)
    
    def mostrar_estado_exito(self, mensaje):
        """Muestra mensaje de éxito"""
        self.status_label.config(text=mensaje, foreground=self.colores['success'])
    
    def limpiar_estado(self):
        """Limpia el mensaje de estado"""
        self.status_label.config(text="")
    
    # ==================== UTILIDADES ====================
    
    def toggle_password_visibility(self):
        """Alterna visibilidad de la contraseña"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="●")
    
    def on_email_focus_in(self, event):
        """Maneja focus en campo email"""
        self.limpiar_estado()
    
    def on_email_focus_out(self, event):
        """Maneja pérdida de focus en email"""
        pass
    
    def mostrar_ayuda_password(self, event):
        """Muestra ayuda para contraseña olvidada"""
        messagebox.showinfo(
            "Ayuda",
            "Para recuperar tu contraseña, contacta al administrador del sistema.\n\n"
            "📧 Email: admin@gimnasio.com\n"
            "📞 Teléfono: (555) 123-4567"
        )
    
    def mostrar_info_sistema(self):
        """Muestra información del sistema"""
        info = """
🏋️ GIMNASIO ATHENAS
Sistema de Gestión Integral

📋 Versión: 1.0.0
🏗️ Desarrollado con: Python + Tkinter
💾 Base de datos: MySQL
🔐 Autenticación: Token-based

👥 Roles disponibles:
• Administrador Principal
• Secretaria
• Coach
• Atleta

🔧 Funcionalidades:
• Gestión de usuarios
• Registro de atletas
• Control de pagos
• Asignación de coaches
• Reportes financieros

© 2024 Gimnasio Athenas
        """
        messagebox.showinfo("Información del Sistema", info)
    
    # ==================== PERSISTENCIA DE CREDENCIALES ====================
    
    def guardar_credenciales(self):
        """Guarda credenciales de forma segura (simplificado)"""
        try:
            # En un sistema real, usar keyring o similar
            with open('.login_cache', 'w') as f:
                f.write(f"{self.email_var.get()}")
        except Exception:
            pass
    
    def cargar_credenciales_guardadas(self):
        """Carga credenciales guardadas"""
        try:
            with open('.login_cache', 'r') as f:
                email = f.read().strip()
                if email:
                    self.email_var.set(email)
                    self.remember_var.set(True)
                    # Focus en contraseña si email está cargado
                    self.parent_frame.after(200, lambda: self.password_entry.focus())
        except FileNotFoundError:
            pass
        except Exception:
            pass
    
    def limpiar_credenciales_guardadas(self):
        """Limpia credenciales guardadas"""
        try:
            import os
            if os.path.exists('.login_cache'):
                os.remove('.login_cache')
        except Exception:
            pass