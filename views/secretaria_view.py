# Vista de Secretaria - Dashboard principal de operaciones
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import threading
from datetime import datetime, date, timedelta
from decimal import Decimal


class SecretariaView:
    def __init__(self, parent_frame, controllers, usuario_actual, token_sesion):
        self.parent_frame = parent_frame
        self.controllers = controllers
        self.usuario_actual = usuario_actual
        self.token_sesion = token_sesion
        
        # Referencias rápidas a controladores
        self.auth_controller = controllers['auth']
        self.user_controller = controllers['user']
        self.finance_controller = controllers['finance']
        self.atleta_controller = controllers['atleta']
        self.coach_controller = controllers['coach']
        
        # Variables de control
        self.vista_actual = "dashboard"
        self.datos_cache = {}
        
        # Configurar estilos específicos
        self.configurar_estilos()
        
        # Crear interfaz principal
        self.crear_interfaz()
        
        # Cargar datos iniciales
        self.cargar_datos_iniciales()
    
    def configurar_estilos(self):
        """Configura estilos específicos para la vista de secretaria"""
        self.style = ttk.Style()
        
        # Colores del tema secretaria
        self.colores = {
            'primario': '#1e40af',        # Azul profesional
            'secundario': '#3b82f6',      # Azul medio
            'acento': '#60a5fa',          # Azul claro
            'exito': '#059669',           # Verde
            'advertencia': '#d97706',     # Naranja
            'error': '#dc2626',           # Rojo
            'fondo': '#f8fafc',           # Gris muy claro
            'card': '#ffffff',            # Blanco
            'texto': '#1f2937',           # Gris oscuro
            'texto_claro': '#6b7280'      # Gris medio
        }
        
        # Estilo para cards/paneles
        self.style.configure(
            'Card.TFrame',
            background=self.colores['card'],
            relief='solid',
            borderwidth=1
        )
        
        # Estilo para headers de secciones
        self.style.configure(
            'SectionHeader.TLabel',
            background=self.colores['card'],
            foreground=self.colores['primario'],
            font=('Segoe UI', 14, 'bold'),
            padding=(10, 10)
        )
        
        # Estilo para botones de acción principales
        self.style.configure(
            'ActionButton.TButton',
            background=self.colores['primario'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 8)
        )
        
        # Estilo para botones de éxito
        self.style.configure(
            'SuccessButton.TButton',
            background=self.colores['exito'],
            foreground='white',
            font=('Segoe UI', 9, 'bold'),
            padding=(10, 6)
        )
        
        # Estilo para botones de advertencia
        self.style.configure(
            'WarningButton.TButton',
            background=self.colores['advertencia'],
            foreground='white',
            font=('Segoe UI', 9, 'bold'),
            padding=(10, 6)
        )
        
        # Estilo para treeviews
        self.style.configure(
            'Secretaria.Treeview',
            font=('Segoe UI', 9),
            rowheight=25,
            background=self.colores['card']
        )
        
        self.style.configure(
            'Secretaria.Treeview.Heading',
            font=('Segoe UI', 10, 'bold'),
            background=self.colores['primario'],
            foreground='white'
        )
    
    def crear_interfaz(self):
        """Crea la interfaz principal de secretaria"""
        # Frame principal con padding
        self.main_frame = ttk.Frame(self.parent_frame, padding=10)
        self.main_frame.pack(fill='both', expand=True)
        
        # Crear header
        self.crear_header()
        
        # Crear notebook (pestañas)
        self.crear_notebook()
        
        # Crear status bar
        self.crear_status_bar()
    
    def crear_header(self):
        """Crea el header con información del usuario"""
        header_frame = ttk.Frame(self.main_frame, style='Card.TFrame', padding=15)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Lado izquierdo - Información
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        # Título y saludo
        title_label = ttk.Label(
            left_frame,
            text=f"🏢 Dashboard Secretaria",
            font=('Segoe UI', 18, 'bold'),
            foreground=self.colores['primario']
        )
        title_label.pack(anchor='w')
        
        welcome_label = ttk.Label(
            left_frame,
            text=f"Bienvenida {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}",
            font=('Segoe UI', 11),
            foreground=self.colores['texto_claro']
        )
        welcome_label.pack(anchor='w', pady=(2, 0))
        
        # Fecha y hora actual
        fecha_actual = datetime.now().strftime("%A, %d de %B %Y")
        fecha_label = ttk.Label(
            left_frame,
            text=f"📅 {fecha_actual}",
            font=('Segoe UI', 9),
            foreground=self.colores['texto_claro']
        )
        fecha_label.pack(anchor='w', pady=(5, 0))
        
        # Lado derecho - Acciones rápidas
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side='right')
        
        # Botones de acción rápida
        quick_frame = ttk.Frame(right_frame)
        quick_frame.pack()
        
        refresh_btn = ttk.Button(
            quick_frame,
            text="🔄 Actualizar",
            command=self.actualizar_datos,
            style='ActionButton.TButton'
        )
        refresh_btn.pack(side='left', padx=(0, 10))
        
        logout_btn = ttk.Button(
            quick_frame,
            text="🚪 Cerrar Sesión",
            command=self.cerrar_sesion,
            style='WarningButton.TButton'
        )
        logout_btn.pack(side='right')
    
    def crear_notebook(self):
        """Crea el notebook con todas las pestañas"""
        # Crear notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Crear pestañas
        self.crear_tab_dashboard()
        self.crear_tab_atletas()
        self.crear_tab_coaches()
        self.crear_tab_pagos()
        self.crear_tab_gastos()
        self.crear_tab_reportes()
        
        # Bind para actualizar datos cuando cambie de pestaña
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def crear_tab_dashboard(self):
        """Crea la pestaña del dashboard principal"""
        # Frame de la pestaña
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🏠 Dashboard")
        
        # Crear scrollable frame
        canvas = tk.Canvas(dashboard_frame)
        scrollbar = ttk.Scrollbar(dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Grid de estadísticas
        self.crear_estadisticas_grid(scrollable_frame)
        
        # Alertas y notificaciones
        self.crear_panel_alertas(scrollable_frame)
        
        # Acciones rápidas mejoradas
        self.crear_acciones_rapidas(scrollable_frame)
        
        # Actividad reciente
        self.crear_actividad_reciente(scrollable_frame)
    
    def crear_estadisticas_grid(self, parent):
        """Crea el grid de estadísticas principales"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Estadísticas del Día", padding=15)
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Grid container
        grid_frame = ttk.Frame(stats_frame)
        grid_frame.pack(fill='x')
        
        # Configurar columnas del grid
        for i in range(4):
            grid_frame.columnconfigure(i, weight=1)
        
        # Crear widgets de estadísticas
        self.stats_widgets = {}
        
        stats_config = [
            ("atletas_hoy", "👥", "Registros Hoy", "0", self.colores['exito']),
            ("pagos_hoy", "💰", "Pagos Hoy", "$0", self.colores['primario']),
            ("vencimientos", "⚠️", "Próximos a Vencer", "0", self.colores['advertencia']),
            ("atletas_total", "🏃", "Total Atletas", "0", self.colores['secundario'])
        ]
        
        for i, (key, icon, label, value, color) in enumerate(stats_config):
            stat_card = self.crear_stat_card(grid_frame, icon, label, value, color)
            stat_card.grid(row=0, column=i, padx=10, pady=5, sticky='ew')
            self.stats_widgets[key] = stat_card
    
    def crear_stat_card(self, parent, icon, label, value, color):
        """Crea una tarjeta de estadística"""
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding=15)
        
        # Ícono
        icon_label = ttk.Label(
            card_frame,
            text=icon,
            font=('Segoe UI', 24),
            foreground=color
        )
        icon_label.pack()
        
        # Valor
        value_label = ttk.Label(
            card_frame,
            text=value,
            font=('Segoe UI', 16, 'bold'),
            foreground=color
        )
        value_label.pack()
        
        # Label
        label_widget = ttk.Label(
            card_frame,
            text=label,
            font=('Segoe UI', 9),
            foreground=self.colores['texto_claro']
        )
        label_widget.pack()
        
        # Guardar referencias para actualizar
        card_frame.value_label = value_label
        card_frame.icon_label = icon_label
        
        return card_frame
    
    def crear_panel_alertas(self, parent):
        """Crea el panel de alertas y notificaciones"""
        alerts_frame = ttk.LabelFrame(parent, text="🔔 Alertas y Notificaciones", padding=15)
        alerts_frame.pack(fill='x', pady=(0, 15))
        
        # Frame para las alertas
        self.alerts_container = ttk.Frame(alerts_frame)
        self.alerts_container.pack(fill='x')
        
        # Inicialmente mostrar placeholder
        placeholder = ttk.Label(
            self.alerts_container,
            text="✅ No hay alertas pendientes",
            font=('Segoe UI', 10),
            foreground=self.colores['exito']
        )
        placeholder.pack(pady=10)
    
    def crear_acciones_rapidas(self, parent):
        """Crea el panel de acciones rápidas"""
        actions_frame = ttk.LabelFrame(parent, text="⚡ Acciones Rápidas", padding=15)
        actions_frame.pack(fill='x', pady=(0, 15))
        
        # Grid de botones
        buttons_grid = ttk.Frame(actions_frame)
        buttons_grid.pack(fill='x')
        
        # Configurar grid
        for i in range(3):
            buttons_grid.columnconfigure(i, weight=1)
        
        # Botones de acción
        acciones = [
            ("➕ Registrar Atleta", "SuccessButton.TButton", self.abrir_registro_atleta),
            ("💰 Procesar Pago", "ActionButton.TButton", self.abrir_procesar_pago),
            ("👨‍🏫 Nuevo Coach", "ActionButton.TButton", self.abrir_registro_coach),
            ("📋 Ver Atletas", "ActionButton.TButton", lambda: self.notebook.select(1)),
            ("💸 Registrar Gasto", "WarningButton.TButton", self.abrir_registro_gasto),
            ("📊 Generar Reporte", "ActionButton.TButton", lambda: self.notebook.select(5))
        ]
        
        for i, (text, style, command) in enumerate(acciones):
            row = i // 3
            col = i % 3
            btn = ttk.Button(buttons_grid, text=text, style=style, command=command)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
    
    def crear_actividad_reciente(self, parent):
        """Crea el panel de actividad reciente"""
        activity_frame = ttk.LabelFrame(parent, text="📈 Actividad Reciente", padding=15)
        activity_frame.pack(fill='both', expand=True)
        
        # Crear treeview para mostrar actividades
        columns = ('Hora', 'Tipo', 'Descripción', 'Usuario')
        self.activity_tree = ttk.Treeview(
            activity_frame,
            columns=columns,
            show='headings',
            height=8,
            style='Secretaria.Treeview'
        )
        
        # Configurar columnas
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=100)
        
        # Scrollbar para el treeview
        activity_scroll = ttk.Scrollbar(activity_frame, orient='vertical', command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scroll.set)
        
        # Empaquetar
        self.activity_tree.pack(side='left', fill='both', expand=True)
        activity_scroll.pack(side='right', fill='y')
    
    def crear_tab_atletas(self):
        """Crea la pestaña de gestión de atletas"""
        atletas_frame = ttk.Frame(self.notebook)
        self.notebook.add(atletas_frame, text="🏃 Atletas")
        
        # Panel superior con controles
        control_frame = ttk.Frame(atletas_frame, padding=10)
        control_frame.pack(fill='x')
        
        # Botones de acción
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side='left')
        
        ttk.Button(
            btn_frame,
            text="➕ Nuevo Atleta",
            style='SuccessButton.TButton',
            command=self.abrir_registro_atleta
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="🔄 Actualizar Lista",
            style='ActionButton.TButton',
            command=self.cargar_atletas
        ).pack(side='left', padx=(0, 10))
        
        # Filtros
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Filtrar por estado:").pack(side='left', padx=(0, 5))
        
        self.filtro_estado_var = tk.StringVar(value="todos")
        filtro_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filtro_estado_var,
            values=["todos", "solvente", "vencido", "suspendido"],
            state="readonly",
            width=12
        )
        filtro_combo.pack(side='left')
        filtro_combo.bind('<<ComboboxSelected>>', self.filtrar_atletas)
        
        # Lista de atletas
        self.crear_lista_atletas(atletas_frame)
    
    def crear_lista_atletas(self, parent):
        """Crea la lista de atletas con treeview"""
        # Frame contenedor
        list_frame = ttk.Frame(parent, padding=(10, 0, 10, 10))
        list_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('ID', 'Nombre', 'Email', 'Plan', 'Estado', 'Vencimiento', 'Coach')
        self.atletas_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            style='Secretaria.Treeview'
        )
        
        # Configurar columnas
        col_widths = {'ID': 60, 'Nombre': 150, 'Email': 180, 'Plan': 120, 'Estado': 80, 'Vencimiento': 100, 'Coach': 150}
        for col in columns:
            self.atletas_tree.heading(col, text=col)
            self.atletas_tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.atletas_tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.atletas_tree.xview)
        self.atletas_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout para scrollbars
        self.atletas_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Menú contextual
        self.crear_menu_contextual_atletas()
        
        # Bind doble click
        self.atletas_tree.bind('<Double-1>', self.on_atleta_double_click)
    
    def crear_menu_contextual_atletas(self):
        """Crea menú contextual para la lista de atletas"""
        self.menu_atletas = tk.Menu(self.atletas_tree, tearoff=0)
        self.menu_atletas.add_command(label="👤 Ver Perfil", command=self.ver_perfil_atleta)
        self.menu_atletas.add_command(label="💰 Procesar Pago", command=self.procesar_pago_atleta)
        self.menu_atletas.add_command(label="👨‍🏫 Asignar Coach", command=self.asignar_coach_atleta)
        self.menu_atletas.add_separator()
        self.menu_atletas.add_command(label="✏️ Editar", command=self.editar_atleta)
        self.menu_atletas.add_command(label="⚠️ Suspender", command=self.suspender_atleta)
        
        # Bind del menú
        self.atletas_tree.bind('<Button-3>', self.mostrar_menu_atletas)
    
    def crear_tab_coaches(self):
        """Crea la pestaña de gestión de coaches"""
        coaches_frame = ttk.Frame(self.notebook)
        self.notebook.add(coaches_frame, text="👨‍🏫 Coaches")
        
        # Panel de control
        control_frame = ttk.Frame(coaches_frame, padding=10)
        control_frame.pack(fill='x')
        
        ttk.Button(
            control_frame,
            text="➕ Nuevo Coach",
            style='SuccessButton.TButton',
            command=self.abrir_registro_coach
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🔄 Actualizar",
            style='ActionButton.TButton',
            command=self.cargar_coaches
        ).pack(side='left')
        
        # Lista de coaches
        self.crear_lista_coaches(coaches_frame)
    
    def crear_lista_coaches(self, parent):
        """Crea la lista de coaches"""
        list_frame = ttk.Frame(parent, padding=(10, 0, 10, 10))
        list_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Nombre', 'Email', 'Especialidades', 'Atletas Asignados', 'Salario')
        self.coaches_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            style='Secretaria.Treeview'
        )
        
        # Configurar columnas
        col_widths = {'ID': 60, 'Nombre': 150, 'Email': 180, 'Especialidades': 200, 'Atletas Asignados': 120, 'Salario': 100}
        for col in columns:
            self.coaches_tree.heading(col, text=col)
            self.coaches_tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbar
        coaches_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.coaches_tree.yview)
        self.coaches_tree.configure(yscrollcommand=coaches_scroll.set)
        
        self.coaches_tree.pack(side='left', fill='both', expand=True)
        coaches_scroll.pack(side='right', fill='y')
    
    def crear_tab_pagos(self):
        """Crea la pestaña de gestión de pagos"""
        pagos_frame = ttk.Frame(self.notebook)
        self.notebook.add(pagos_frame, text="💰 Pagos")
        
        # Panel superior
        control_frame = ttk.Frame(pagos_frame, padding=10)
        control_frame.pack(fill='x')
        
        ttk.Button(
            control_frame,
            text="💰 Procesar Pago",
            style='SuccessButton.TButton',
            command=self.abrir_procesar_pago
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🔄 Actualizar",
            style='ActionButton.TButton',
            command=self.cargar_pagos
        ).pack(side='left')
        
        # Filtros de fecha
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Desde:").pack(side='left', padx=(0, 5))
        self.fecha_desde = DateEntry(filter_frame, width=10, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.fecha_desde.pack(side='left', padx=(0, 10))
        
        ttk.Label(filter_frame, text="Hasta:").pack(side='left', padx=(0, 5))
        self.fecha_hasta = DateEntry(filter_frame, width=10, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.fecha_hasta.pack(side='left', padx=(0, 10))
        
        ttk.Button(
            filter_frame,
            text="🔍 Filtrar",
            command=self.filtrar_pagos
        ).pack(side='left')
        
        # Lista de pagos
        self.crear_lista_pagos(pagos_frame)
    
    def crear_lista_pagos(self, parent):
        """Crea la lista de pagos/ingresos"""
        list_frame = ttk.Frame(parent, padding=(10, 0, 10, 10))
        list_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Fecha', 'Atleta', 'Plan', 'Monto', 'Tipo', 'Método', 'Procesado Por')
        self.pagos_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            style='Secretaria.Treeview'
        )
        
        # Configurar columnas
        for col in columns:
            self.pagos_tree.heading(col, text=col)
            self.pagos_tree.column(col, width=100)
        
        # Scrollbar
        pagos_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.pagos_tree.yview)
        self.pagos_tree.configure(yscrollcommand=pagos_scroll.set)
        
        self.pagos_tree.pack(side='left', fill='both', expand=True)
        pagos_scroll.pack(side='right', fill='y')
    
    def crear_tab_gastos(self):
        """Crea la pestaña de gestión de gastos"""
        gastos_frame = ttk.Frame(self.notebook)
        self.notebook.add(gastos_frame, text="💸 Gastos")
        
        # Panel de control
        control_frame = ttk.Frame(gastos_frame, padding=10)
        control_frame.pack(fill='x')
        
        ttk.Button(
            control_frame,
            text="💸 Registrar Gasto",
            style='WarningButton.TButton',
            command=self.abrir_registro_gasto
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🔄 Actualizar",
            style='ActionButton.TButton',
            command=self.cargar_gastos
        ).pack(side='left')
        
        # Lista de gastos
        self.crear_lista_gastos(gastos_frame)
    
    def crear_lista_gastos(self, parent):
        """Crea la lista de gastos/egresos"""
        list_frame = ttk.Frame(parent, padding=(10, 0, 10, 10))
        list_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Fecha', 'Tipo', 'Descripción', 'Beneficiario', 'Monto', 'Método', 'Registrado Por')
        self.gastos_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            style='Secretaria.Treeview'
        )
        
        # Configurar columnas
        for col in columns:
            self.gastos_tree.heading(col, text=col)
            self.gastos_tree.column(col, width=120)
        
        # Scrollbar
        gastos_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.gastos_tree.yview)
        self.gastos_tree.configure(yscrollcommand=gastos_scroll.set)
        
        self.gastos_tree.pack(side='left', fill='both', expand=True)
        gastos_scroll.pack(side='right', fill='y')
    
    def crear_tab_reportes(self):
        """Crea la pestaña de reportes"""
        reportes_frame = ttk.Frame(self.notebook)
        self.notebook.add(reportes_frame, text="📊 Reportes")
        
        # Panel de opciones de reporte
        options_frame = ttk.LabelFrame(reportes_frame, text="Opciones de Reporte", padding=15)
        options_frame.pack(fill='x', padx=10, pady=10)
        
        # Tipo de reporte
        ttk.Label(options_frame, text="Tipo de Reporte:").grid(row=0, column=0, sticky='w', pady=5)
        self.tipo_reporte_var = tk.StringVar(value="financiero")
        tipo_combo = ttk.Combobox(
            options_frame,
            textvariable=self.tipo_reporte_var,
            values=["financiero", "atletas", "coaches", "membresías"],
            state="readonly"
        )
        tipo_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Período
        ttk.Label(options_frame, text="Período:").grid(row=1, column=0, sticky='w', pady=5)
        self.periodo_var = tk.StringVar(value="mes_actual")
        periodo_combo = ttk.Combobox(
            options_frame,
            textvariable=self.periodo_var,
            values=["hoy", "semana", "mes_actual", "mes_anterior", "personalizado"],
            state="readonly"
        )

        periodo_combo.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Botón generar
        ttk.Button(
            options_frame,
            text="📊 Generar Reporte",
            style='ActionButton.TButton',
            command=self.generar_reporte
        ).grid(row=2, column=0, columnspan=2, pady=15)
        
        options_frame.columnconfigure(1, weight=1)
        
        # Área de resultados
        self.crear_area_resultados_reporte(reportes_frame)
    
    def crear_area_resultados_reporte(self, parent):
        """Crea el área para mostrar resultados de reportes"""
        results_frame = ttk.LabelFrame(parent, text="Resultados", padding=15)
        results_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Text widget para mostrar reportes
        self.reporte_text = tk.Text(
            results_frame,
            font=('Consolas', 10),
            wrap='word',
            state='disabled'
        )
        
        # Scrollbar para el text widget
        reporte_scroll = ttk.Scrollbar(results_frame, orient='vertical', command=self.reporte_text.yview)
        self.reporte_text.configure(yscrollcommand=reporte_scroll.set)
        
        self.reporte_text.pack(side='left', fill='both', expand=True)
        reporte_scroll.pack(side='right', fill='y')
    
    def crear_status_bar(self):
        """Crea la barra de estado en la parte inferior"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill='x', pady=(5, 0))
        
        # Separador
        ttk.Separator(self.status_frame, orient='horizontal').pack(fill='x', pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(
            self.status_frame,
            text="✅ Sistema listo",
            font=('Segoe UI', 9),
            foreground=self.colores['exito']
        )
        self.status_label.pack(side='left')
        
        # Información de conexión
        self.connection_label = ttk.Label(
            self.status_frame,
            text="🔗 Conectado",
            font=('Segoe UI', 9),
            foreground=self.colores['exito']
        )
        self.connection_label.pack(side='right')
    
    # ==================== CARGA DE DATOS ====================
    
    def cargar_datos_iniciales(self):
        """Carga todos los datos iniciales en un hilo separado"""
        self.actualizar_status("🔄 Cargando datos iniciales...")
        threading.Thread(target=self._cargar_datos_background, daemon=True).start()
    
    def _cargar_datos_background(self):
        """Carga datos en background"""
        try:
            # Cargar estadísticas
            self.parent_frame.after(0, self.cargar_estadisticas)
            
            # Cargar alertas
            self.parent_frame.after(100, self.cargar_alertas)
            
            # Cargar actividad reciente
            self.parent_frame.after(200, self.cargar_actividad_reciente)
            
            # Status final
            self.parent_frame.after(500, lambda: self.actualizar_status("✅ Datos cargados correctamente"))
            
        except Exception as e:
            self.parent_frame.after(0, lambda: self.actualizar_status(f"❌ Error al cargar datos: {str(e)}"))
    
    def cargar_estadisticas(self):
        """Carga las estadísticas del dashboard"""
        try:
            # Obtener estadísticas de atletas
            atletas_result = self.atleta_controller.obtener_todos_atletas()
            total_atletas = len(atletas_result.get('atletas', [])) if atletas_result['success'] else 0
            
            # Próximos a vencer (7 días)
            vencimientos_result = self.atleta_controller.obtener_atletas_proximos_vencer(7)
            proximos_vencer = len(vencimientos_result.get('atletas', [])) if vencimientos_result['success'] else 0
            
            # Actualizar widgets
            self.stats_widgets['atletas_total']['value_label'].config(text=str(total_atletas))
            self.stats_widgets['vencimientos']['value_label'].config(text=str(proximos_vencer))
            
            # Cambiar color si hay vencimientos
            if proximos_vencer > 0:
                self.stats_widgets['vencimientos']['icon_label'].config(foreground=self.colores['error'])
            
        except Exception as e:
            print(f"Error cargando estadísticas: {e}")
    
    def cargar_alertas(self):
        """Carga alertas y notificaciones"""
        try:
            # Limpiar alertas existentes
            for widget in self.alerts_container.winfo_children():
                widget.destroy()
            
            alertas = []
            
            # Verificar membresías próximas a vencer
            vencimientos = self.atleta_controller.obtener_atletas_proximos_vencer(7)
            if vencimientos['success'] and vencimientos['atletas']:
                count = len(vencimientos['atletas'])
                alertas.append(f"⚠️ {count} membresías vencen en los próximos 7 días")
            
            # Verificar membresías ya vencidas
            vencidos = self.atleta_controller.obtener_atletas_por_estado_solvencia('vencido')
            if vencidos['success'] and vencidos['atletas']:
                count = len(vencidos['atletas'])
                alertas.append(f"🔴 {count} atletas con membresía vencida")
            
            # Mostrar alertas o mensaje de no hay alertas
            if alertas:
                for i, alerta in enumerate(alertas):
                    color = self.colores['error'] if '🔴' in alerta else self.colores['advertencia']
                    alert_label = ttk.Label(
                        self.alerts_container,
                        text=alerta,
                        font=('Segoe UI', 10),
                        foreground=color
                    )
                    alert_label.pack(anchor='w', pady=2)
            else:
                no_alerts = ttk.Label(
                    self.alerts_container,
                    text="✅ No hay alertas pendientes",
                    font=('Segoe UI', 10),
                    foreground=self.colores['exito']
                )
                no_alerts.pack(pady=10)
                
        except Exception as e:
            print(f"Error cargando alertas: {e}")
    
    def cargar_actividad_reciente(self):
        """Carga la actividad reciente del sistema"""
        try:
            # Limpiar actividad existente
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # Actividades simuladas por ahora
            actividades = [
                (datetime.now().strftime("%H:%M"), "Login", "Inicio de sesión", self.usuario_actual['nombre']),
                ((datetime.now() - timedelta(minutes=30)).strftime("%H:%M"), "Sistema", "Carga de datos", "Sistema"),
                ((datetime.now() - timedelta(hours=1)).strftime("%H:%M"), "Pago", "Renovación de membresía", "Secretaria"),
            ]
            
            for actividad in actividades:
                self.activity_tree.insert('', 'end', values=actividad)
                
        except Exception as e:
            print(f"Error cargando actividad: {e}")
    
    def cargar_atletas(self):
        """Carga la lista de atletas"""
        try:
            self.actualizar_status("🔄 Cargando atletas...")
            
            # Limpiar lista actual
            for item in self.atletas_tree.get_children():
                self.atletas_tree.delete(item)
            
            # Obtener atletas
            resultado = self.atleta_controller.obtener_todos_atletas()
            if resultado['success']:
                for atleta_info in resultado['atletas']:
                    atleta_data = atleta_info['atleta_data']
                    usuario_data = atleta_info['usuario_data']
                    
                    # Obtener información del plan
                    plan_info = self.finance_controller.obtener_plan_por_id(atleta_data[5])
                    plan_nombre = plan_info['plan'][1] if plan_info['success'] else "N/A"
                    
                    # Insertar en treeview
                    values = (
                        atleta_data[0],  # ID
                        f"{usuario_data[1]} {usuario_data[2]}",  # Nombre
                        usuario_data[6],  # Email
                        plan_nombre,  # Plan
                        atleta_data[9] or "N/A",  # Estado
                        atleta_data[7] or "N/A",  # Vencimiento
                        "Coach asignado" if atleta_data[6] else "Sin coach"  # Coach
                    )
                    
                    self.atletas_tree.insert('', 'end', values=values)
                
                self.actualizar_status(f"✅ {len(resultado['atletas'])} atletas cargados")
            else:
                self.actualizar_status(f"❌ Error: {resultado['message']}")
                
        except Exception as e:
            self.actualizar_status(f"❌ Error cargando atletas: {str(e)}")
    
    def cargar_coaches(self):
        """Carga la lista de coaches"""
        try:
            self.actualizar_status("🔄 Cargando coaches...")
            
            # Limpiar lista actual
            for item in self.coaches_tree.get_children():
                self.coaches_tree.delete(item)
            
            # Obtener coaches
            resultado = self.coach_controller.obtener_todos_coaches()
            if resultado['success']:
                for coach_info in resultado['coaches']:
                    coach_data = coach_info['coach_data']
                    usuario_data = coach_info['usuario_data']
                    
                    # Contar atletas asignados
                    atletas_count = self.coach_controller.contar_atletas_asignados(coach_data[0])
                    
                    values = (
                        coach_data[0],  # ID
                        f"{usuario_data[1]} {usuario_data[2]}",  # Nombre
                        usuario_data[6],  # Email
                        coach_data[2] or "N/A",  # Especialidades
                        atletas_count,  # Atletas asignados
                        f"${coach_data[5]}" if coach_data[5] else "N/A"  # Salario
                    )
                    
                    self.coaches_tree.insert('', 'end', values=values)
                
                self.actualizar_status(f"✅ {len(resultado['coaches'])} coaches cargados")
            else:
                self.actualizar_status(f"❌ Error: {resultado['message']}")
                
        except Exception as e:
            self.actualizar_status(f"❌ Error cargando coaches: {str(e)}")
    
    def cargar_pagos(self):
        """Carga la lista de pagos/ingresos"""
        try:
            self.actualizar_status("🔄 Cargando historial de pagos...")
            
            # Limpiar lista actual
            for item in self.pagos_tree.get_children():
                self.pagos_tree.delete(item)
            
            # Obtener ingresos detallados del controlador
            resultado = self.finance_controller.obtener_ingresos_detallados()
            
            if resultado['success']:
                self.datos_cache['pagos'] = resultado['ingresos']
                for pago in resultado['ingresos']:
                    monto_formateado = f"${pago['monto']:.2f}"
                    values = (
                        pago['id_pago'],
                        pago['fecha_pago'],
                        pago['nombre_atleta'],
                        pago['nombre_plan'],
                        monto_formateado,
                        pago['tipo_pago'],
                        pago['metodo_pago'],
                        pago['nombre_procesador']
                    )
                    self.pagos_tree.insert('', 'end', values=values)
                
                self.actualizar_status(f"✅ {len(resultado['ingresos'])} pagos cargados.")
            else:
                self.actualizar_status(f"❌ Error al cargar pagos: {resultado['message']}")
                messagebox.showerror("Error", resultado['message'])
            
        except Exception as e:
            self.actualizar_status(f"❌ Error crítico cargando pagos: {str(e)}")

    def cargar_gastos(self):
# ... (resto del código de secretaria_view.py) ...

     def filtrar_pagos(self):
        """Filtra pagos por rango de fechas"""
        try:
            fecha_desde = self.fecha_desde.get_date()
            fecha_hasta = self.fecha_hasta.get_date()
            self.actualizar_status(f"🔍 Filtrando pagos desde {fecha_desde} hasta {fecha_hasta}...")

            resultado = self.finance_controller.obtener_ingresos_por_fecha(fecha_desde, fecha_hasta)

            if resultado['success']:
                # Limpiar la tabla
                for item in self.pagos_tree.get_children():
                    self.pagos_tree.delete(item)
                
                # Llenar la tabla con los resultados filtrados
                for pago in resultado['ingresos']:
                    monto_formateado = f"${pago['monto']:.2f}"
                    values = (
                        pago['id_pago'],
                        pago['fecha_pago'],
                        pago['nombre_atleta'],
                        pago['nombre_plan'],
                        monto_formateado,
                        pago['tipo_pago'],
                        pago['metodo_pago'],
                        pago['nombre_procesador']
                    )
                    self.pagos_tree.insert('', 'end', values=values)
                
                self.actualizar_status(f"✅ {len(resultado['ingresos'])} pagos encontrados en el período.")
            else:
                messagebox.showerror("Error", f"Error al filtrar pagos: {resultado['message']}")
                self.actualizar_status(f"❌ Error al filtrar pagos.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el filtro de fechas: {str(e)}")
            self.actualizar_status(f"❌ Error en filtro.")
    
    # ==================== EVENTOS Y CALLBACKS ====================
    
    def on_tab_changed(self, event):
        """Maneja el cambio de pestañas"""
        selected_tab = event.widget.tab('current')['text']
        
        if "🏃 Atletas" in selected_tab and not hasattr(self, '_atletas_cargados'):
            self.cargar_atletas()
            self._atletas_cargados = True
        elif "👨‍🏫 Coaches" in selected_tab and not hasattr(self, '_coaches_cargados'):
            self.cargar_coaches()
            self._coaches_cargados = True
        elif "💰 Pagos" in selected_tab and not hasattr(self, '_pagos_cargados'):
            self.cargar_pagos()
            self._pagos_cargados = True
        elif "💸 Gastos" in selected_tab and not hasattr(self, '_gastos_cargados'):
            self.cargar_gastos()
            self._gastos_cargados = True
    
    def filtrar_atletas(self, event=None):
        """Filtra atletas por estado"""
        estado = self.filtro_estado_var.get()
        # TODO: Implementar filtrado real
        self.actualizar_status(f"🔍 Filtrando atletas por estado: {estado}")
    
    def filtrar_pagos(self):
        """Filtra pagos por rango de fechas"""
        fecha_desde = self.fecha_desde.get_date()
        fecha_hasta = self.fecha_hasta.get_date()
        self.actualizar_status(f"🔍 Filtrando pagos desde {fecha_desde} hasta {fecha_hasta}")
    
    def mostrar_menu_atletas(self, event):
        """Muestra el menú contextual de atletas"""
        selection = self.atletas_tree.selection()
        if selection:
            self.menu_atletas.post(event.x_root, event.y_root)
    
    def on_atleta_double_click(self, event):
        """Maneja doble click en atleta"""
        self.ver_perfil_atleta()
    
    # ==================== VENTANAS MODALES ====================
    
    def abrir_registro_atleta(self):
        """Abre ventana de registro de atleta"""
        self.crear_ventana_registro_atleta()
    
    def crear_ventana_registro_atleta(self):
        """Crea ventana modal para registrar atleta"""
        # Ventana modal
        ventana = tk.Toplevel(self.parent_frame)
        ventana.title("➕ Registrar Nuevo Atleta")
        ventana.geometry("600x700")
        ventana.resizable(False, False)
        ventana.transient(self.parent_frame)
        ventana.grab_set()
        
        # Centrar ventana
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (600 // 2)
        y = (ventana.winfo_screenheight() // 2) - (700 // 2)
        ventana.geometry(f"600x700+{x}+{y}")
        
        # Frame principal con scroll
        main_frame = ttk.Frame(ventana, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Registro de Nuevo Atleta", style='SectionHeader.TLabel')
        titulo.pack(pady=(0, 20))
        
        # Notebook para organizar campos
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # Pestaña de datos personales
        personal_frame = ttk.Frame(notebook, padding=15)
        notebook.add(personal_frame, text="👤 Datos Personales")
        
        # Variables para los campos
        self.atleta_vars = {
            'nombre': tk.StringVar(),
            'apellido': tk.StringVar(),
            'email': tk.StringVar(),
            'contraseña': tk.StringVar(),
            'cedula': tk.StringVar(),
            'peso': tk.StringVar(),
            'fecha_nacimiento': tk.StringVar(),
            'direccion': tk.StringVar(),
            'telefono': tk.StringVar(),
            'meta_largo_plazo': tk.StringVar(),
            'valoracion_especiales': tk.StringVar()
        }
        
        # Crear campos de datos personales
        self.crear_campos_datos_personales(personal_frame)
        
        # Pestaña de membresía
        membresia_frame = ttk.Frame(notebook, padding=15)
        notebook.add(membresia_frame, text="💳 Membresía")
        
        self.crear_campos_membresia(membresia_frame)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(
            buttons_frame,
            text="❌ Cancelar",
            command=ventana.destroy
        ).pack(side='right', padx=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="✅ Registrar Atleta",
            style='SuccessButton.TButton',
            command=lambda: self.procesar_registro_atleta(ventana)
        ).pack(side='right')
    
    def crear_campos_datos_personales(self, parent):
        """Crea campos de datos personales"""
        # Grid para organizar campos
        row = 0
        
        # Nombre
        ttk.Label(parent, text="Nombre *:").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.atleta_vars['nombre'], width=25).grid(row=row, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Apellido
        ttk.Label(parent, text="Apellido *:").grid(row=row, column=2, sticky='w', padx=(20, 0), pady=5)
        ttk.Entry(parent, textvariable=self.atleta_vars['apellido'], width=25).grid(row=row, column=3, sticky='ew', padx=(10, 0), pady=5)
        
        row += 1
        
        # Email
        ttk.Label(parent, text="Email *:").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.atleta_vars['email'], width=40).grid(row=row, column=1, columnspan=3, sticky='ew', padx=(10, 0), pady=5)
        
        row += 1
        
        # Contraseña
        ttk.Label(parent, text="Contraseña *:").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.atleta_vars['contraseña'], show="*", width=25).grid(row=row, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Cédula
        ttk.Label(parent, text="Cédula *:").grid(row=row, column=2, sticky='w', padx=(20, 0), pady=5)
        ttk.Entry(parent, textvariable=self.atleta_vars['cedula'], width=25).grid(row=row, column=3, sticky='ew', padx=(10, 0), pady=5)
        
        row += 1
        
        # Peso
        ttk.Label(parent, text="Peso (kg):").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.atleta_vars['peso'], width=25).grid(row=row, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Fecha de nacimiento
        ttk.Label(parent, text="Fecha de Nacimiento:").grid(row=row, column=2, sticky='w', padx=(20, 0), pady=5)
        self.fecha_nacimiento_entry = DateEntry(parent, width=12, background='darkblue',
                                               foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.fecha_nacimiento_entry.grid(row=row, column=3, sticky='w', padx=(10, 0), pady=5)
        
        row += 1
        
        # Dirección
        ttk.Label(parent, text="Dirección:").grid(row=row, column=0, sticky='nw', pady=5)
        direccion_text = tk.Text(parent, height=3, width=50)
        direccion_text.grid(row=row, column=1, columnspan=3, sticky='ew', padx=(10, 0), pady=5)
        self.direccion_text = direccion_text
        
        row += 1
        
        # Teléfono
        ttk.Label(parent, text="Teléfono:").grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.atleta_vars['telefono'], width=25).grid(row=row, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Configurar columnas
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)
    
    def crear_campos_membresia(self, parent):
        """Crea campos de membresía"""
        # Plan de membresía
        ttk.Label(parent, text="Plan de Membresía *:").grid(row=0, column=0, sticky='w', pady=5)
        
        # Cargar planes disponibles
        self.plan_var = tk.StringVar()
        self.plan_combo = ttk.Combobox(parent, textvariable=self.plan_var, state="readonly", width=30)
        self.plan_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Cargar planes
        self.cargar_planes_combo()
        
        # Método de pago
        ttk.Label(parent, text="Método de Pago *:").grid(row=1, column=0, sticky='w', pady=5)
        self.metodo_pago_var = tk.StringVar(value="efectivo")
        metodo_combo = ttk.Combobox(
            parent,
            textvariable=self.metodo_pago_var,
            values=["efectivo", "tarjeta", "transferencia"],
            state="readonly",
            width=30
        )
        metodo_combo.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Coach asignado (opcional)
        ttk.Label(parent, text="Coach Asignado:").grid(row=2, column=0, sticky='w', pady=5)
        self.coach_var = tk.StringVar()
        self.coach_combo = ttk.Combobox(parent, textvariable=self.coach_var, state="readonly", width=30)
        self.coach_combo.grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Cargar coaches
        self.cargar_coaches_combo()
        
        # Meta a largo plazo
        ttk.Label(parent, text="Meta a Largo Plazo:").grid(row=3, column=0, sticky='nw', pady=5)
        meta_text = tk.Text(parent, height=4, width=50)
        meta_text.grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=5)
        self.meta_text = meta_text
        
        # Valoraciones especiales
        ttk.Label(parent, text="Valoraciones Especiales:").grid(row=4, column=0, sticky='nw', pady=5)
        valoracion_text = tk.Text(parent, height=4, width=50)
        valoracion_text.grid(row=4, column=1, sticky='ew', padx=(10, 0), pady=5)
        self.valoracion_text = valoracion_text
        
        # Configurar columna
        parent.columnconfigure(1, weight=1)
    
    def cargar_planes_combo(self):
        """Carga planes en el combobox"""
        try:
            resultado = self.finance_controller.obtener_planes_activos()
            if resultado['success']:
                planes_text = []
                self.planes_data = {}
                
                for plan in resultado['planes']:
                    plan_id = plan[0]
                    nombre = plan[1]
                    precio = plan[3]
                    duracion = plan[4]
                    
                    texto = f"{nombre} - ${precio} ({duracion} días)"
                    planes_text.append(texto)
                    self.planes_data[texto] = plan_id
                
                self.plan_combo['values'] = planes_text
                if planes_text:
                    self.plan_combo.current(0)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando planes: {str(e)}")
    
    def cargar_coaches_combo(self):
        """Carga coaches en el combobox"""
        try:
            resultado = self.coach_controller.obtener_coaches_disponibles()
            if resultado['success']:
                coaches_text = ["Sin asignar"]
                self.coaches_data = {"Sin asignar": None}
                
                for coach_info in resultado['coaches']:
                    coach_data = coach_info['coach_data']
                    usuario_data = coach_info['usuario_data']
                    
                    coach_id = coach_data[0]
                    nombre = f"{usuario_data[1]} {usuario_data[2]}"
                    especialidades = coach_data[2] or "General"
                    
                    texto = f"{nombre} ({especialidades})"
                    coaches_text.append(texto)
                    self.coaches_data[texto] = coach_id
                
                self.coach_combo['values'] = coaches_text
                self.coach_combo.current(0)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando coaches: {str(e)}")
    
    def procesar_registro_atleta(self, ventana):
        """Procesa el registro del atleta"""
        try:
            # Recopilar datos del usuario
            datos_usuario = {
                'nombre': self.atleta_vars['nombre'].get().strip(),
                'apellido': self.atleta_vars['apellido'].get().strip(),
                'email': self.atleta_vars['email'].get().strip(),
                'contraseña': self.atleta_vars['contraseña'].get(),
                'direccion': self.direccion_text.get("1.0", 'end-1c').strip(),
                'telefono': self.atleta_vars['telefono'].get().strip()
            }
            
            # Recopilar datos del atleta
            plan_seleccionado = self.plan_var.get()
            coach_seleccionado = self.coach_var.get()
            
            datos_atleta = {
                'cedula': self.atleta_vars['cedula'].get().strip(),
                'peso': float(self.atleta_vars['peso'].get()) if self.atleta_vars['peso'].get() else None,
                'fecha_nacimiento': self.fecha_nacimiento_entry.get_date(),
                'id_plan': self.planes_data.get(plan_seleccionado),
                'id_coach': self.coaches_data.get(coach_seleccionado),
                'meta_largo_plazo': self.meta_text.get("1.0", 'end-1c').strip(),
                'valoracion_especiales': self.valoracion_text.get("1.0", 'end-1c').strip()
            }
            
            # Método de pago
            metodo_pago = self.metodo_pago_var.get()
            
            # Validaciones básicas
            if not all([datos_usuario['nombre'], datos_usuario['apellido'], 
                       datos_usuario['email'], datos_usuario['contraseña'], 
                       datos_atleta['cedula'], datos_atleta['id_plan']]):
                messagebox.showerror("Error", "Por favor completa todos los campos obligatorios (*)")
                return
            
            # Procesar registro
            self.actualizar_status("🔄 Registrando atleta...")
            
            resultado = self.atleta_controller.registrar_atleta_completo(
                datos_atleta,
                datos_usuario,
                metodo_pago,
                self.usuario_actual['id']
            )
            
            if resultado['success']:
                messagebox.showinfo("Éxito", 
                    f"✅ {resultado['message']}\n\n"
                    f"💰 Monto pagado: ${resultado['monto_pagado']}\n"
                    f"📅 Vencimiento: {resultado['fecha_vencimiento']}")
                
                # Actualizar listas
                self.cargar_atletas()
                self.cargar_estadisticas()
                
                # Cerrar ventana
                ventana.destroy()
                
                self.actualizar_status("✅ Atleta registrado exitosamente")
                
            else:
                messagebox.showerror("Error", resultado['message'])
                self.actualizar_status("❌ Error en el registro")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando registro: {str(e)}")
            self.actualizar_status("❌ Error interno")
    
    # ==================== OTRAS VENTANAS MODALES ====================
    
    def abrir_procesar_pago(self):
        """Abre ventana para procesar pagos"""
        messagebox.showinfo("Información", "🚧 Funcionalidad en desarrollo")
    
    def abrir_registro_coach(self):
        """Abre ventana para registrar coach"""
        messagebox.showinfo("Información", "🚧 Funcionalidad en desarrollo")
    
    def abrir_registro_gasto(self):
        """Abre ventana para registrar gastos"""
        messagebox.showinfo("Información", "🚧 Funcionalidad en desarrollo")
    
    def ver_perfil_atleta(self):
        """Ver perfil detallado del atleta seleccionado"""
        selection = self.atletas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un atleta")
            return
        
        # Obtener datos del atleta seleccionado
        item = self.atletas_tree.item(selection[0])
        atleta_id = item['values'][0]
        
        messagebox.showinfo("Información", f"🚧 Ver perfil del atleta ID: {atleta_id}")
    
    def procesar_pago_atleta(self):
        """Procesar pago del atleta seleccionado"""
        selection = self.atletas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un atleta")
            return
        
        self.abrir_procesar_pago()
    
    def asignar_coach_atleta(self):
        """Asignar coach al atleta seleccionado"""
        selection = self.atletas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un atleta")
            return
        
        messagebox.showinfo("Información", "🚧 Asignar coach en desarrollo")
    
    def editar_atleta(self):
        """Editar datos del atleta seleccionado"""
        selection = self.atletas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un atleta")
            return
        
        messagebox.showinfo("Información", "🚧 Editar atleta en desarrollo")
    
    def suspender_atleta(self):
        """Suspender atleta seleccionado"""
        selection = self.atletas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un atleta")
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás segura de suspender este atleta?"):
            messagebox.showinfo("Información", "🚧 Suspender atleta en desarrollo")
    
    def generar_reporte(self):
        """Genera el reporte seleccionado"""
        tipo = self.tipo_reporte_var.get()
        periodo = self.periodo_var.get()
        
        # Limpiar área de resultados
        self.reporte_text.config(state='normal')
        self.reporte_text.delete('1.0', 'end')
        
        # Generar reporte según tipo
        if tipo == "financiero":
            reporte = self.generar_reporte_financiero(periodo)
        elif tipo == "atletas":
            reporte = self.generar_reporte_atletas(periodo)
        elif tipo == "coaches":
            reporte = self.generar_reporte_coaches()
        else:
            reporte = "🚧 Tipo de reporte en desarrollo"
        
        # Mostrar reporte
        self.reporte_text.insert('1.0', reporte)
        self.reporte_text.config(state='disabled')
        
        self.actualizar_status(f"✅ Reporte {tipo} generado")
    
    def generar_reporte_financiero(self, periodo):
        """Genera reporte financiero"""
        try:
            # Calcular fechas según período
            hoy = date.today()
            if periodo == "hoy":
                fecha_inicio = fecha_fin = hoy
            elif periodo == "semana":
                fecha_inicio = hoy - timedelta(days=7)
                fecha_fin = hoy
            elif periodo == "mes_actual":
                fecha_inicio = hoy.replace(day=1)
                fecha_fin = hoy
            elif periodo == "mes_anterior":
                primer_dia_mes_actual = hoy.replace(day=1)
                fecha_fin = primer_dia_mes_actual - timedelta(days=1)
                fecha_inicio = fecha_fin.replace(day=1)
            else:
                fecha_inicio = fecha_fin = hoy
            
            # Generar reporte usando el controlador
            resultado = self.finance_controller.generar_reporte_financiero(fecha_inicio, fecha_fin)
            
            if resultado['success']:
                reporte_data = resultado['reporte']
                
                reporte = f"""
📊 REPORTE FINANCIERO
========================
📅 Período: {fecha_inicio} a {fecha_fin}

💰 RESUMEN GENERAL
------------------
Total Ingresos:    ${reporte_data['resumen']['total_ingresos']}
Total Egresos:     ${reporte_data['resumen']['total_egresos']}
Balance:           ${reporte_data['resumen']['balance']}

Cantidad Ingresos: {reporte_data['resumen']['cantidad_ingresos']}
Cantidad Egresos:  {reporte_data['resumen']['cantidad_egresos']}

💵 DESGLOSE DE INGRESOS
-----------------------
"""
                for tipo, monto in reporte_data['desglose_ingresos'].items():
                    reporte += f"{tipo.replace('_', ' ').title()}: ${monto}\n"
                
                reporte += "\n💸 DESGLOSE DE EGRESOS\n"
                reporte += "-----------------------\n"
                for tipo, monto in reporte_data['desglose_egresos'].items():
                    reporte += f"{tipo.replace('_', ' ').title()}: ${monto}\n"
                
                return reporte
            else:
                return f"❌ Error generando reporte: {resultado['message']}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def generar_reporte_atletas(self, periodo):
        """Genera reporte de atletas"""
        try:
            resultado = self.atleta_controller.obtener_todos_atletas()
            if resultado['success']:
                atletas = resultado['atletas']
                total = len(atletas)
                
                # Contar por estado
                estados = {}
                for atleta_info in atletas:
                    estado = atleta_info['atleta_data'][9] or 'N/A'
                    estados[estado] = estados.get(estado, 0) + 1
                
                reporte = f"""
👥 REPORTE DE ATLETAS
=====================
📅 Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 RESUMEN GENERAL
------------------
Total de Atletas: {total}

📈 POR ESTADO DE SOLVENCIA
--------------------------
"""
                for estado, cantidad in estados.items():
                    porcentaje = (cantidad / total * 100) if total > 0 else 0
                    reporte += f"{estado.title()}: {cantidad} ({porcentaje:.1f}%)\n"
                
                return reporte
            else:
                return f"❌ Error: {resultado['message']}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def generar_reporte_coaches(self):
        """Genera reporte de coaches"""
        try:
            resultado = self.coach_controller.obtener_resumen_coaches()
            if resultado['success']:
                resumen = resultado['resumen']
                
                reporte = f"""
👨‍🏫 REPORTE DE COACHES
======================
📅 Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 RESUMEN GENERAL
------------------
Total Coaches:           {resumen['total_coaches']}
Coaches con Atletas:     {resumen['coaches_con_atletas']}
Total Atletas Asignados: {resumen['total_atletas_asignados']}
Salario Promedio:        ${resumen['salario_promedio']}

🎯 POR ESPECIALIDAD
-------------------
"""
                for especialidad, cantidad in resumen['coaches_por_especialidad'].items():
                    reporte += f"{especialidad}: {cantidad}\n"
                
                return reporte
            else:
                return f"❌ Error: {resultado['message']}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==================== UTILIDADES ====================
    
    def actualizar_datos(self):
        """Actualiza todos los datos de la interfaz"""
        self.actualizar_status("🔄 Actualizando datos...")
        self.cargar_datos_iniciales()
        
        # Resetear flags de carga de pestañas
        if hasattr(self, '_atletas_cargados'):
            delattr(self, '_atletas_cargados')
        if hasattr(self, '_coaches_cargados'):
            delattr(self, '_coaches_cargados')
        if hasattr(self, '_pagos_cargados'):
            delattr(self, '_pagos_cargados')
        if hasattr(self, '_gastos_cargados'):
            delattr(self, '_gastos_cargados')
    
    def actualizar_status(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=mensaje)
        
        # Auto-limpiar después de 5 segundos para mensajes de éxito
        if "✅" in mensaje:
            self.parent_frame.after(5000, lambda: self.status_label.config(text="✅ Sistema listo"))
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        if messagebox.askyesno("Confirmar", "¿Estás segura de cerrar sesión?"):
            try:
                resultado = self.auth_controller.cerrar_sesion(self.token_sesion)
                if resultado['success']:
                    # Notificar al main view para volver al login
                    self.parent_frame.event_generate('<<Logout>>')
            except Exception as e:
                print(f"Error al cerrar sesión: {e}")
                # Forzar logout aunque falle
                self.parent_frame.event_generate('<<Logout>>')


# ==================== FUNCIONES DE UTILIDAD ====================

def mostrar_mensaje_desarrollo(titulo="Información"):
    """Muestra mensaje de funcionalidad en desarrollo"""
    messagebox.showinfo(titulo, "🚧 Esta funcionalidad está en desarrollo y estará disponible pronto.")


def validar_email(email):
    """Valida formato básico de email"""
    import re
    patron = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(patron, email) is not None


def formatear_fecha(fecha):
    """Formatea fecha para mostrar"""
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except:
            return fecha
    
    if isinstance(fecha, date):
        return fecha.strftime('%d/%m/%Y')
    
    return str(fecha)


def formatear_moneda(monto):
    """Formatea monto como moneda"""
    try:
        return f"${float(monto):,.2f}"
    except:
        return str(monto)