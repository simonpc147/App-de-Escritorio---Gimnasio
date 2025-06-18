# Vista de Login - Pantalla de autenticación ATHENA GYM & BOX
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
        """Configura estilos específicos para ATHENA GYM & BOX"""
        self.style = ttk.Style()
        
        # Colores oficiales de ATHENA GYM & BOX
        self.colores = {
            'verde_lima': '#CCFF00',               # Verde lima principal
            'morado': '#660066',                   # Morado oficial
            'gris_oscuro': '#333333',              # Gris del logo
            'blanco': '#FFFFFF',                   # Blanco
            'negro': '#000000',                    # Negro
            'gris_claro': '#F5F5F5',              # Gris muy claro para fondos
            'verde_hover': '#B8E600',              # Verde más oscuro para hover
            'morado_claro': '#8A1A8A',            # Morado más claro
            'success': '#4CAF50',                  # Verde éxito
            'warning': '#FF9800',                  # Naranja advertencia
            'error': '#F44336',                    # Rojo error
            'fondo_principal': '#1A1A1A'           # Fondo oscuro elegante
        }
        
        # Estilo para el frame principal del login
        self.style.configure(
            'Login.TFrame',
            background=self.colores['fondo_principal']
        )
        
        # Estilo para la tarjeta de login
        self.style.configure(
            'LoginCard.TFrame',
            background=self.colores['gris_claro'],
            relief='flat',
            borderwidth=0
        )
        
        # Título principal - ATHENA
        self.style.configure(
            'AthenaTitle.TLabel',
            background=self.colores['gris_claro'],
            foreground=self.colores['gris_oscuro'],
            font=('Arial Black', 28, 'bold')  # Similar a Dalek Pinpoint Bold
        )
        
        # Subtítulo - GYM & BOX
        self.style.configure(
            'GymBoxSubtitle.TLabel',
            background=self.colores['gris_claro'],
            foreground=self.colores['morado'],
            font=('Arial', 14, 'bold')  # Similar a Century Gothic
        )
        
        # Título del formulario
        self.style.configure(
            'LoginFormTitle.TLabel',
            background=self.colores['gris_claro'],
            foreground=self.colores['gris_oscuro'],
            font=('Arial', 20, 'bold')
        )
        
        # Labels de campos
        self.style.configure(
            'LoginLabel.TLabel',
            background=self.colores['gris_claro'],
            foreground=self.colores['gris_oscuro'],
            font=('Arial', 11, 'bold')
        )
        
        # Entries del login
        self.style.configure(
            'Login.TEntry',
            font=('Arial', 12),
            padding=(12, 10),
            relief='solid',
            borderwidth=2,
            focuscolor=self.colores['verde_lima']
        )
        
        # Botón principal de login
        self.style.configure(
            'AthenaButton.TButton',
            background=self.colores['verde_lima'],
            foreground=self.colores['gris_oscuro'],
            font=('Arial', 12, 'bold'),
            padding=(25, 12),
            relief='flat',
            borderwidth=0
        )
        
        self.style.map(
            'AthenaButton.TButton',
            background=[
                ('active', self.colores['verde_hover']),
                ('disabled', '#CCCCCC')
            ],
            foreground=[
                ('active', self.colores['gris_oscuro']),
                ('disabled', '#999999')
            ]
        )
        
        # Botón secundario
        self.style.configure(
            'SecondaryButton.TButton',
            background=self.colores['morado'],
            foreground=self.colores['blanco'],
            font=('Arial', 10, 'bold'),
            padding=(15, 8),
            relief='flat'
        )
        
        self.style.map(
            'SecondaryButton.TButton',
            background=[('active', self.colores['morado_claro'])]
        )
        
        # Checkbutton personalizado
        self.style.configure(
            'Login.TCheckbutton',
            background=self.colores['gris_claro'],
            foreground=self.colores['gris_oscuro'],
            font=('Arial', 10),
            focuscolor=self.colores['verde_lima']
        )
    
    def crear_interfaz(self):
        """Crea la interfaz completa de login"""
        # Frame principal con fondo oscuro
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
        """Crea el header con logo y título de ATHENA"""
        # Frame del header
        header_frame = ttk.Frame(self.center_container, style='Login.TFrame')
        header_frame.pack(pady=(40, 30))
        
        # Crear logo de ATHENA (versión simplificada)
        self.crear_logo_athena(header_frame)
        
        # Título principal - ATHENA
        title_label = ttk.Label(
            header_frame,
            text="ATHENA",
            style='AthenaTitle.TLabel'
        )
        title_label.pack(pady=(15, 0))
        
        # Subtítulo - GYM & BOX
        subtitle_label = ttk.Label(
            header_frame,
            text="GYM & BOX",
            style='GymBoxSubtitle.TLabel'
        )
        subtitle_label.pack()
        
        # Línea decorativa
        separator_frame = ttk.Frame(header_frame, style='Login.TFrame')
        separator_frame.pack(pady=(10, 0))
        
        separator_canvas = tk.Canvas(
            separator_frame,
            width=200,
            height=3,
            bg=self.colores['verde_lima'],
            highlightthickness=0
        )
        separator_canvas.pack()
    
    def crear_logo_athena(self, parent):
        """Crea una versión simplificada del logo de ATHENA"""
        logo_frame = ttk.Frame(parent, style='Login.TFrame')
        logo_frame.pack(pady=(0, 10))
        
        # Canvas para el logo
        logo_canvas = tk.Canvas(
            logo_frame,
            width=120,
            height=80,
            bg=self.colores['fondo_principal'],
            highlightthickness=0
        )
        logo_canvas.pack()
        
        # Centro del canvas
        cx, cy = 60, 40
        
        # Dibujar las "alas" decorativas (versión simplificada)
        # Alas verdes superiores
        logo_canvas.create_polygon(
            [25, 25, 45, 20, 50, 30, 30, 35],
            fill=self.colores['verde_lima'],
            outline=''
        )
        logo_canvas.create_polygon(
            [95, 25, 75, 20, 70, 30, 90, 35],
            fill=self.colores['verde_lima'],
            outline=''
        )
        
        # Alas moradas inferiores
        logo_canvas.create_polygon(
            [25, 45, 45, 50, 50, 60, 30, 55],
            fill=self.colores['morado'],
            outline=''
        )
        logo_canvas.create_polygon(
            [95, 45, 75, 50, 70, 60, 90, 55],
            fill=self.colores['morado'],
            outline=''
        )
        
        # Círculo central (cabeza de lechuza simplificada)
        logo_canvas.create_oval(
            cx-15, cy-15, cx+15, cy+15,
            fill=self.colores['gris_oscuro'],
            outline=self.colores['verde_lima'],
            width=2
        )
        
        # "Ojos" de la lechuza
        logo_canvas.create_oval(
            cx-8, cy-5, cx-2, cy+1,
            fill=self.colores['blanco'],
            outline=''
        )
        logo_canvas.create_oval(
            cx+2, cy-5, cx+8, cy+1,
            fill=self.colores['blanco'],
            outline=''
        )
        
        # Detalle verde inferior
        logo_canvas.create_polygon(
            [cx-3, cy+8, cx, cy+15, cx+3, cy+8],
            fill=self.colores['verde_lima'],
            outline=''
        )
    
    def crear_formulario_login(self):
        """Crea el formulario de login"""
        # Tarjeta principal del formulario
        self.card_frame = ttk.Frame(self.center_container, style='LoginCard.TFrame', padding=50)
        self.card_frame.pack(pady=20, padx=40)
        
        # Sombra de la tarjeta (efecto visual)
        shadow_frame = tk.Frame(
            self.center_container,
            bg='#00000020',
            height=4
        )
        shadow_frame.place(in_=self.card_frame, x=4, y=4, relwidth=1, relheight=1)
        self.card_frame.lift()
        
        # Título del formulario
        form_title = ttk.Label(
            self.card_frame,
            text="INICIAR SESIÓN",
            style='LoginFormTitle.TLabel'
        )
        form_title.pack(pady=(0, 35))
        
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
        email_frame.pack(fill='x', pady=(0, 25))
        
        # Label
        email_label = ttk.Label(
            email_frame,
            text="📧 CORREO ELECTRÓNICO",
            style='LoginLabel.TLabel'
        )
        email_label.pack(anchor='w', pady=(0, 8))
        
        # Entry
        self.email_entry = ttk.Entry(
            email_frame,
            textvariable=self.email_var,
            style='Login.TEntry',
            width=35
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
        password_frame.pack(fill='x', pady=(0, 25))
        
        # Label con opción de mostrar/ocultar
        label_frame = ttk.Frame(password_frame, style='LoginCard.TFrame')
        label_frame.pack(fill='x', pady=(0, 8))
        
        password_label = ttk.Label(
            label_frame,
            text="🔐 CONTRASEÑA",
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
            width=35
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
            foreground=self.colores['morado'],
            background=self.colores['gris_claro'],
            font=('Arial', 9, 'underline'),
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
            style='AthenaButton.TButton',
            command=self.procesar_login,
            state='disabled'
        )
        self.login_button.pack(fill='x', pady=(0, 15))
        
        # Frame para botones secundarios
        secondary_buttons = ttk.Frame(buttons_frame, style='LoginCard.TFrame')
        secondary_buttons.pack(fill='x')
        
        # Botón de prueba rápida (para desarrollo)
        test_button = ttk.Button(
            secondary_buttons,
            text="🧪 Login de Prueba",
            style='SecondaryButton.TButton',
            command=self.login_prueba
        )
        test_button.pack(side='left', padx=(0, 10))
        
        # Botón de información del sistema
        info_button = ttk.Button(
            secondary_buttons,
            text="ℹ️ INFO SISTEMA",
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
            background=self.colores['gris_claro'],
            font=('Arial', 10),
            wraplength=400
        )
        self.status_label.pack()
        
        # Barra de progreso (para cargas) - colores de ATHENA
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=400
        )
        # Personalizar colores de la barra de progreso
        self.style.configure(
            'TProgressbar',
            background=self.colores['verde_lima'],
            troughcolor=self.colores['gris_oscuro']
        )
    
    def crear_footer(self):
        """Crea el footer con información de ATHENA"""
        footer_frame = ttk.Frame(self.center_container, style='Login.TFrame')
        footer_frame.pack(side='bottom', pady=30)
        
        # Información del sistema
        info_text = "🔒 SISTEMA SEGURO | 📱 VERSIÓN 1.0 | 🏋️ ATHENA GYM & BOX 2024"
        footer_label = ttk.Label(
            footer_frame,
            text=info_text,
            font=('Arial', 9),
            foreground=self.colores['verde_lima'],
            background=self.colores['fondo_principal']
        )
        footer_label.pack()
        
        # Línea decorativa inferior
        line_canvas = tk.Canvas(
            footer_frame,
            width=400,
            height=2,
            bg=self.colores['morado'],
            highlightthickness=0
        )
        line_canvas.pack(pady=(10, 0))
    
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
            self.mostrar_estado_exito("✅ ¡Bienvenido a ATHENA! Cargando sistema...")
            
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
    
   def login_prueba(self):
        """Login de prueba temporal"""
        resultado = self.auth_controller.login_bypass_temporal("duena@gimnasio.com", "admin123")
        if resultado["success"]:
            self.manejar_resultado_login(resultado)
    
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
        self.status_label.config(text=mensaje, foreground=self.colores['morado'])
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
            "Recuperar Contraseña - ATHENA GYM & BOX",
            "Para recuperar tu contraseña, contacta al administrador del gimnasio.\n\n"
            "📧 Email: admin@athena.gym\n"
            "📞 Teléfono: (555) 123-4567\n"
            "🏋️ ATHENA GYM & BOX - Sistema de Gestión"
        )
    
    def mostrar_info_sistema(self):
        """Muestra información del sistema"""
        info = """
🏋️ ATHENA GYM & BOX
Sistema de Gestión Integral

📋 Versión: 1.0.0
🏗️ Desarrollado con: Python + Tkinter
💾 Base de datos: MySQL
🔐 Autenticación: Token-based

👥 ROLES DISPONIBLES:
• Administrador Principal
• Secretaria/Recepción
• Coach/Entrenador
• Atleta/Miembro

🔧 FUNCIONALIDADES PRINCIPALES:
• Gestión completa de miembros
• Control de pagos y suscripciones
• Asignación de coaches y rutinas
• Reportes financieros y estadísticas
• Control de acceso al gimnasio
• Gestión de clases y horarios

💪 ESPECIALIDADES:
• Entrenamiento funcional
• CrossFit y BOX
• Gimnasio tradicional
• Clases grupales
• Entrenamiento personalizado

© 2024 ATHENA GYM & BOX
Todos los derechos reservados
        """
        messagebox.showinfo("ATHENA GYM & BOX - Información del Sistema", info)
    
    # ==================== PERSISTENCIA DE CREDENCIALES ====================
    
    def guardar_credenciales(self):
        """Guarda credenciales de forma segura (simplificado)"""
        try:
            # En un sistema real, usar keyring o similar
            with open('.athena_login_cache', 'w') as f:
                f.write(f"{self.email_var.get()}")
        except Exception:
            pass
    
    def cargar_credenciales_guardadas(self):
        """Carga credenciales guardadas"""
        try:
            with open('.athena_login_cache', 'r') as f:
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
            if os.path.exists('.athena_login_cache'):
                os.remove('.athena_login_cache')
        except Exception:
            pass