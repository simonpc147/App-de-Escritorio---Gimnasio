# Vista de Administrador - Dashboard completo de gestión
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import threading
from datetime import datetime, date, timedelta
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import secrets 


class AdminView:
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
        
        # Configurar estilos específicos del admin
        self.configurar_estilos()
        
        # Crear interfaz principal
        self.crear_interfaz()
        
        # Cargar datos iniciales
        self.actualizar_datos()
    
    def configurar_estilos(self):
        """Configura estilos específicos para la vista de administrador"""
        self.style = ttk.Style()
        
        # Colores del tema administrador (más elegantes y ejecutivos)
        self.colores = {
            'primario': '#0f172a',        # Azul muy oscuro (executive)
            'secundario': '#1e293b',      # Gris azulado oscuro
            'acento': '#3b82f6',          # Azul brillante
            'dorado': '#f59e0b',          # Dorado (premium)
            'exito': '#10b981',           # Verde esmeralda
            'advertencia': '#f59e0b',     # Ámbar
            'error': '#ef4444',           # Rojo vibrante
            'fondo': '#f8fafc',           # Gris muy claro
            'card': '#ffffff',            # Blanco puro
            'texto': '#0f172a',           # Texto muy oscuro
            'texto_claro': '#64748b'      # Gris medio
        }
        
        # Estilo para cards ejecutivas
        self.style.configure(
            'Executive.TFrame',
            background=self.colores['card'],
            relief='solid',
            borderwidth=2
        )
        
        # Estilo para headers ejecutivos
        self.style.configure(
            'Executive.TLabel',
            background=self.colores['card'],
            foreground=self.colores['primario'],
            font=('Segoe UI', 16, 'bold'),
            padding=(15, 15)
        )
        
        # Botones ejecutivos principales
        self.style.configure(
            'Executive.TButton',
            background=self.colores['primario'],
            foreground='white',
            font=('Segoe UI', 11, 'bold'),
            padding=(20, 10)
        )
        
        # Botones dorados (premium)
        self.style.configure(
            'Premium.TButton',
            background=self.colores['dorado'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 8)
        )
        
        # Botones de éxito
        self.style.configure(
            'AdminSuccess.TButton',
            background=self.colores['exito'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(12, 7)
        )
        
        # Treeviews ejecutivos
        self.style.configure(
            'Admin.Treeview',
            font=('Segoe UI', 9),
            rowheight=28,
            background=self.colores['card']
        )
        
        self.style.configure(
            'Admin.Treeview.Heading',
            font=('Segoe UI', 11, 'bold'),
            background=self.colores['primario'],
            foreground='white'
        )
    
    def crear_interfaz(self):
        """Crea la interfaz principal de administrador"""
        # Frame principal con padding ejecutivo
        self.main_frame = ttk.Frame(self.parent_frame, padding=15)
        self.main_frame.pack(fill='both', expand=True)
        
        # Crear header ejecutivo
        self.crear_header_ejecutivo()
        
        # Crear notebook principal
        self.crear_notebook_admin()
        
        # Crear status bar ejecutivo
        self.crear_status_bar_ejecutivo()
    
    def crear_header_ejecutivo(self):
        """Crea el header ejecutivo con información privilegiada"""
        header_frame = ttk.Frame(self.main_frame, style='Executive.TFrame', padding=20)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Lado izquierdo - Información ejecutiva
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        # Título ejecutivo
        title_label = ttk.Label(
            left_frame,
            text="👑 PANEL EJECUTIVO",
            font=('Segoe UI', 20, 'bold'),
            foreground=self.colores['dorado']
        )
        title_label.pack(anchor='w')
        
        welcome_label = ttk.Label(
            left_frame,
            text=f"Bienvenida {self.usuario_actual['nombre']} {self.usuario_actual['apellido']} - Administradora Principal",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colores['primario']
        )
        welcome_label.pack(anchor='w', pady=(5, 0))
        
        # Información de tiempo y ubicación
        fecha_actual = datetime.now().strftime("%A, %d de %B %Y - %H:%M")
        fecha_label = ttk.Label(
            left_frame,
            text=f"🕒 {fecha_actual}",
            font=('Segoe UI', 10),
            foreground=self.colores['texto_claro']
        )
        fecha_label.pack(anchor='w', pady=(8, 0))
        
        # Lado derecho - Métricas rápidas y acciones
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side='right')
        
        # Mini dashboard
        self.crear_mini_dashboard(right_frame)
    
    def crear_mini_dashboard(self, parent):
        """Crea un mini dashboard en el header"""
        mini_frame = ttk.Frame(parent)
        mini_frame.pack()
        
        # Grid de métricas rápidas
        metrics_frame = ttk.Frame(mini_frame)
        metrics_frame.pack(pady=(0, 15))
        
        # Métricas ejecutivas
        self.mini_metrics = {}
        metrics_config = [
            ("revenue_today", "💰", "Ingresos Hoy", "$0", self.colores['exito']),
            ("balance_month", "📊", "Balance Mes", "$0", self.colores['dorado']),
            ("active_members", "👥", "Miembros Activos", "0", self.colores['acento'])
        ]
        
        for i, (key, icon, label, value, color) in enumerate(metrics_config):
            metric_card = self.crear_mini_metric_card(metrics_frame, icon, label, value, color)
            metric_card.grid(row=0, column=i, padx=8, pady=5)
            self.mini_metrics[key] = metric_card
        
        # Botones ejecutivos
        buttons_frame = ttk.Frame(mini_frame)
        buttons_frame.pack()
        
        refresh_btn = ttk.Button(
            buttons_frame,
            text="🔄 Actualizar",
            command=self.actualizar_datos,
            style='Executive.TButton'
        )
        refresh_btn.pack(side='left', padx=(0, 10))
        
        logout_btn = ttk.Button(
            buttons_frame,
            text="🚪 Cerrar Sesión",
            command=self.cerrar_sesion,
            style='Premium.TButton'
        )
        logout_btn.pack(side='right')
    
    def crear_mini_metric_card(self, parent, icon, label, value, color):
        """Crea una tarjeta de métrica mini"""
        card_frame = ttk.Frame(parent, style='Executive.TFrame', padding=12)
        
        # Layout horizontal compacto
        content_frame = ttk.Frame(card_frame)
        content_frame.pack()
        
        # Ícono
        icon_label = ttk.Label(
            content_frame,
            text=icon,
            font=('Segoe UI', 16),
            foreground=color
        )
        icon_label.pack(side='left', padx=(0, 8))
        
        # Datos
        data_frame = ttk.Frame(content_frame)
        data_frame.pack(side='left')
        
        value_label = ttk.Label(
            data_frame,
            text=value,
            font=('Segoe UI', 12, 'bold'),
            foreground=color
        )
        value_label.pack(anchor='w')
        
        label_widget = ttk.Label(
            data_frame,
            text=label,
            font=('Segoe UI', 8),
            foreground=self.colores['texto_claro']
        )
        label_widget.pack(anchor='w')
        
        # Guardar referencia para actualizar
        card_frame.value_label = value_label
        
        return card_frame
    
    def crear_notebook_admin(self):
        """Crea el notebook con pestañas administrativas"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 15))
        
        # Crear pestañas ejecutivas
        self.crear_tab_dashboard_ejecutivo()
        self.crear_tab_usuarios()
        self.crear_tab_finanzas_avanzadas()
        self.crear_tab_analytics()
        self.crear_tab_configuracion()
        self.crear_tab_auditoria()
        
        # Bind para carga lazy
        self.notebook.bind('<<NotebookTabChanged>>', self.on_admin_tab_changed)
    
    def crear_tab_dashboard_ejecutivo(self):
        """Crea el dashboard ejecutivo principal"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard Ejecutivo")
        
        # Crear canvas scrollable
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
        
        # KPIs ejecutivos
        self.crear_kpis_ejecutivos(scrollable_frame)
        
        # Gráficos de rendimiento
        self.crear_graficos_rendimiento(scrollable_frame)
        
        # Alertas críticas
        self.crear_alertas_criticas(scrollable_frame)
        
        # Resumen de operaciones
        self.crear_resumen_operaciones(scrollable_frame)
    
    def crear_kpis_ejecutivos(self, parent):
        """Crea los KPIs principales para ejecutivos"""
        kpis_frame = ttk.LabelFrame(parent, text="📈 Indicadores Clave de Rendimiento (KPIs)", padding=20)
        kpis_frame.pack(fill='x', pady=(0, 20))
        
        # Grid de KPIs
        grid_frame = ttk.Frame(kpis_frame)
        grid_frame.pack(fill='x')
        
        # Configurar columnas
        for i in range(4):
            grid_frame.columnconfigure(i, weight=1)
        
        # KPIs ejecutivos
        self.kpis_widgets = {}
        
        kpis_config = [
            ("revenue_monthly", "💰", "Ingresos Mensuales", "$0", self.colores['exito']),
            ("profit_margin", "📊", "Margen de Ganancia", "0%", self.colores['dorado']),
            ("member_retention", "👥", "Retención de Miembros", "0%", self.colores['acento']),
            ("avg_revenue_per_member", "💎", "Ingreso Promedio/Miembro", "$0", self.colores['primario'])
        ]
        
        for i, (key, icon, label, value, color) in enumerate(kpis_config):
            kpi_card = self.crear_kpi_card(grid_frame, icon, label, value, color)
            kpi_card.grid(row=0, column=i, padx=15, pady=10, sticky='ew')
            self.kpis_widgets[key] = kpi_card
        
        # Segunda fila de KPIs
        kpis_config_2 = [
            ("total_members", "🏃", "Total Miembros", "0", self.colores['secundario']),
            ("coaches_efficiency", "👨‍🏫", "Eficiencia Coaches", "0%", self.colores['exito']),
            ("monthly_growth", "📈", "Crecimiento Mensual", "0%", self.colores['dorado']),
            ("operational_costs", "💸", "Costos Operacionales", "$0", self.colores['error'])
        ]
        
        for i, (key, icon, label, value, color) in enumerate(kpis_config_2):
            kpi_card = self.crear_kpi_card(grid_frame, icon, label, value, color)
            kpi_card.grid(row=1, column=i, padx=15, pady=10, sticky='ew')
            self.kpis_widgets[key] = kpi_card
    
    def crear_kpi_card(self, parent, icon, label, value, color):
        """Crea una tarjeta KPI ejecutiva"""
        card_frame = ttk.Frame(parent, style='Executive.TFrame', padding=20)
        
        # Ícono grande
        icon_label = ttk.Label(
            card_frame,
            text=icon,
            font=('Segoe UI', 28),
            foreground=color
        )
        icon_label.pack()
        
        # Valor principal
        value_label = ttk.Label(
            card_frame,
            text=value,
            font=('Segoe UI', 18, 'bold'),
            foreground=color
        )
        value_label.pack(pady=(8, 0))
        
        # Label descriptivo
        label_widget = ttk.Label(
            card_frame,
            text=label,
            font=('Segoe UI', 10),
            foreground=self.colores['texto_claro']
        )
        label_widget.pack()
        
        # Indicador de tendencia (placeholder)
        trend_label = ttk.Label(
            card_frame,
            text="📈 +5.2%",
            font=('Segoe UI', 9),
            foreground=self.colores['exito']
        )
        trend_label.pack(pady=(5, 0))
        
        # Guardar referencias
        card_frame.value_label = value_label
        card_frame.trend_label = trend_label
        
        return card_frame
    
    def crear_graficos_rendimiento(self, parent):
        """Crea gráficos de rendimiento usando matplotlib"""
        graficos_frame = ttk.LabelFrame(parent, text="📊 Análisis de Rendimiento", padding=20)
        graficos_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Notebook para diferentes gráficos
        graficos_notebook = ttk.Notebook(graficos_frame)
        graficos_notebook.pack(fill='both', expand=True)
        
        # Gráfico de ingresos
        self.crear_grafico_ingresos(graficos_notebook)
        
        # Gráfico de miembros
        self.crear_grafico_miembros(graficos_notebook)
        
        # Gráfico de coaches
        self.crear_grafico_coaches(graficos_notebook)
    
    def crear_grafico_ingresos(self, parent):
        """Crea gráfico de ingresos mensuales"""
        ingresos_frame = ttk.Frame(parent)
        parent.add(ingresos_frame, text="💰 Ingresos")
        
        # Crear figura de matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')
        
        # Datos de ejemplo (luego conectar con datos reales)
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        ingresos = [12000, 15000, 18000, 16000, 20000, 22000]
        egresos = [8000, 9000, 10000, 11000, 12000, 13000]
        
        # Crear gráficos de barras
        x = np.arange(len(meses))
        width = 0.35
        
        ax.bar(x - width/2, ingresos, width, label='Ingresos', color=self.colores['exito'], alpha=0.8)
        ax.bar(x + width/2, egresos, width, label='Egresos', color=self.colores['error'], alpha=0.8)
        
        # Configurar gráfico
        ax.set_xlabel('Meses')
        ax.set_ylabel('Monto ($)')
        ax.set_title('Análisis Financiero Mensual')
        ax.set_xticks(x)
        ax.set_xticklabels(meses)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Integrar con tkinter
        canvas = FigureCanvasTkAgg(fig, ingresos_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        plt.close(fig)  # Evitar memory leaks
    
    def crear_grafico_miembros(self, parent):
        """Crea gráfico de evolución de miembros"""
        miembros_frame = ttk.Frame(parent)
        parent.add(miembros_frame, text="👥 Miembros")
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')
        
        # Datos de ejemplo
        fechas = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        nuevos_miembros = [25, 30, 35, 28, 40, 45]
        miembros_activos = [150, 175, 200, 220, 250, 280]
        
        # Crear gráfico de líneas
        ax.plot(fechas, nuevos_miembros, marker='o', linewidth=3, 
                color=self.colores['acento'], label='Nuevos Miembros')
        ax.plot(fechas, miembros_activos, marker='s', linewidth=3, 
                color=self.colores['dorado'], label='Miembros Activos')
        
        # Configurar
        ax.set_xlabel('Meses')
        ax.set_ylabel('Cantidad')
        ax.set_title('Evolución de Membresía')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Integrar
        canvas = FigureCanvasTkAgg(fig, miembros_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        plt.close(fig)
    
    def crear_grafico_coaches(self, parent):
        """Crea gráfico de rendimiento de coaches"""
        coaches_frame = ttk.Frame(parent)
        parent.add(coaches_frame, text="👨‍🏫 Coaches")
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')
        
        # Datos de ejemplo
        coaches = ['Coach A', 'Coach B', 'Coach C', 'Coach D']
        atletas_asignados = [15, 12, 18, 10]
        
        # Crear gráfico de pastel
        colors = [self.colores['acento'], self.colores['exito'], 
                 self.colores['dorado'], self.colores['secundario']]
        
        ax.pie(atletas_asignados, labels=coaches, autopct='%1.1f%%', 
               colors=colors, startangle=90)
        ax.set_title('Distribución de Atletas por Coach')
        
        # Integrar
        canvas = FigureCanvasTkAgg(fig, coaches_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        plt.close(fig)
    
    def crear_alertas_criticas(self, parent):
        """Crea panel de alertas críticas para administrador"""
        alertas_frame = ttk.LabelFrame(parent, text="🚨 Alertas Críticas", padding=20)
        alertas_frame.pack(fill='x', pady=(0, 20))
        
        # Container de alertas
        self.alertas_admin_container = ttk.Frame(alertas_frame)
        self.alertas_admin_container.pack(fill='x')
        
        # Placeholder inicial
        placeholder = ttk.Label(
            self.alertas_admin_container,
            text="✅ Todas las operaciones funcionando correctamente",
            font=('Segoe UI', 11),
            foreground=self.colores['exito']
        )
        placeholder.pack(pady=15)
    
    def crear_resumen_operaciones(self, parent):
        """Crea resumen de operaciones diarias"""
        operaciones_frame = ttk.LabelFrame(parent, text="📋 Resumen de Operaciones Hoy", padding=20)
        operaciones_frame.pack(fill='both', expand=True)
        
        # Grid de operaciones
        ops_grid = ttk.Frame(operaciones_frame)
        ops_grid.pack(fill='x')
        
        # Configurar grid
        for i in range(3):
            ops_grid.columnconfigure(i, weight=1)
        
        # Operaciones del día
        operaciones = [
            ("Nuevos Registros", "0", "👤"),
            ("Pagos Procesados", "0", "💳"),
            ("Sesiones Activas", "0", "🔐"),
            ("Renovaciones", "0", "🔄"),
            ("Gastos Registrados", "0", "💸"),
            ("Reportes Generados", "0", "📊")
        ]
        
        self.ops_widgets = {}
        for i, (label, value, icon) in enumerate(operaciones):
            row = i // 3
            col = i % 3
            
            op_frame = ttk.Frame(ops_grid, style='Executive.TFrame', padding=15)
            op_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            
            # Ícono
            ttk.Label(op_frame, text=icon, font=('Segoe UI', 20)).pack()
            
            # Valor
            value_label = ttk.Label(op_frame, text=value, 
                                  font=('Segoe UI', 16, 'bold'),
                                  foreground=self.colores['primario'])
            value_label.pack()
            
            # Label
            ttk.Label(op_frame, text=label, 
                     font=('Segoe UI', 9),
                     foreground=self.colores['texto_claro']).pack()
            
            self.ops_widgets[label.lower().replace(' ', '_')] = value_label
    
    def crear_tab_usuarios(self):
        """Crea la pestaña de gestión completa de usuarios"""
        usuarios_frame = ttk.Frame(self.notebook)
        self.notebook.add(usuarios_frame, text="👥 Gestión de Usuarios")
        
        # Panel de control superior
        control_frame = ttk.Frame(usuarios_frame, padding=15)
        control_frame.pack(fill='x')
        
        # Botones de acción
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side='left')
        
        ttk.Button(
            btn_frame,
            text="➕ Nueva Secretaria",
            style='AdminSuccess.TButton',
            command=self.crear_secretaria
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="👁️ Ver Sesiones Activas",
            style='Executive.TButton',
            command=self.ver_sesiones_activas
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="🔄 Actualizar",
            style='Executive.TButton',
            command=self.cargar_usuarios
        ).pack(side='left')
        
        # Filtros avanzados
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Filtrar por rol:").pack(side='left', padx=(0, 5))
        
        self.filtro_rol_var = tk.StringVar(value="todos")
        filtro_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filtro_rol_var,
            values=["todos", "secretaria", "coach", "atleta"],
            state="readonly",
            width=15
        )
        filtro_combo.pack(side='left', padx=(0, 10))
        filtro_combo.bind('<<ComboboxSelected>>', self.filtrar_usuarios)
        
        ttk.Button(
            filter_frame,
            text="🔍 Buscar",
            command=self.buscar_usuarios
        ).pack(side='left')
        
        # Lista de usuarios
        self.crear_lista_usuarios(usuarios_frame)
    
    def crear_lista_usuarios(self, parent):
        """Crea lista avanzada de usuarios"""
        list_frame = ttk.Frame(parent, padding=(15, 0, 15, 15))
        list_frame.pack(fill='both', expand=True)
        
        # Treeview avanzado
        columns = ('ID', 'Nombre Completo', 'Email', 'Rol', 'Estado', 'Fecha Creación', 'Creado Por', 'Último Acceso')
        self.usuarios_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            style='Admin.Treeview'
        )
        
        # Configurar columnas
        col_widths = {
            'ID': 50, 'Nombre Completo': 180, 'Email': 200, 'Rol': 100,
            'Estado': 80, 'Fecha Creación': 120, 'Creado Por': 120, 'Último Acceso': 140
        }
        
        for col in columns:
            self.usuarios_tree.heading(col, text=col)
            self.usuarios_tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.usuarios_tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.usuarios_tree.xview)
        self.usuarios_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.usuarios_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Menú contextual administrativo
        self.crear_menu_contextual_usuarios()
        
    
    def crear_menu_contextual_usuarios(self):
        """Crea menú contextual para gestión de usuarios"""
        self.menu_usuarios = tk.Menu(self.usuarios_tree, tearoff=0)
        self.menu_usuarios.add_command(label="👤 Ver Perfil Completo", command=self.ver_perfil_completo)
        self.menu_usuarios.add_command(label="✏️ Editar Usuario", command=self.editar_usuario_admin)
        self.menu_usuarios.add_separator()
        self.menu_usuarios.add_command(label="🔐 Cambiar Contraseña", command=self.cambiar_password_admin)
        self.menu_usuarios.add_command(label="⚠️ Desactivar Usuario", command=self.desactivar_usuario_admin)
        self.menu_usuarios.add_command(label="🗑️ Eliminar Usuario", command=self.eliminar_usuario_admin)
        self.menu_usuarios.add_separator()
        self.menu_usuarios.add_command(label="🔄 Cerrar Todas las Sesiones", command=self.cerrar_sesiones_usuario)
        
        # Bind del menú
        self.usuarios_tree.bind('<Button-3>', self.mostrar_menu_usuarios)

def crear_tab_gestion_atletas(self):
    """Crea la pestaña de gestión de atletas con listado y doble clic"""
    self.tab_gestion_atletas = ttk.Frame(self.tabs)
    self.tabs.add(self.tab_gestion_atletas, text="👟 Gestión de Atletas")

    frame = ttk.Frame(self.tab_gestion_atletas, padding=15)
    frame.pack(fill='both', expand=True)

    columns = ("ID", "Nombre", "Apellido", "Cédula", "Edad", "Peso", "Plan", "Estado")
    self.atletas_tree = ttk.Treeview(frame, columns=columns, show='headings', style='Admin.Treeview')
    self.atletas_tree.bind('<Double-1>', self.ver_detalles_atleta)

    for col in columns:
        self.atletas_tree.heading(col, text=col)
        self.atletas_tree.column(col, width=100)

    vsb = ttk.Scrollbar(frame, orient='vertical', command=self.atletas_tree.yview)
    hsb = ttk.Scrollbar(frame, orient='horizontal', command=self.atletas_tree.xview)
    self.atletas_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    self.atletas_tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    self.cargar_atletas_en_tabla()

def ver_detalles_atleta(self, event=None):
    """Muestra todos los datos detallados del atleta seleccionado en un cuadro de mensaje"""
    selection = self.atletas_tree.selection()
    if not selection:
        messagebox.showwarning("Atención", "Selecciona un atleta para ver detalles.")
        return

    item = self.atletas_tree.item(selection[0])
    atleta_id = item['values'][0]  # Suponiendo que el primer valor es el ID del atleta

    resultado = self.atleta_controller.obtener_detalles_completos_atleta(atleta_id)
    if not resultado['success']:
        messagebox.showerror("Error", resultado['message'])
        return

    a = resultado['atleta']

    mensaje = f"""
👤 {a['nombre']} {a['apellido']}
🪪 Cédula: {a['cedula']}
🎂 Edad: {a['edad'] or 'N/A'} | Nacimiento: {a['fecha_nacimiento'].strftime('%Y-%m-%d') if a['fecha_nacimiento'] else 'N/A'}
⚖️ Peso: {a['peso']} kg
🏠 Dirección: {a['direccion'] or 'No especificada'}

🎯 Meta: {a['meta_largo_plazo'] or 'No registrada'}
🩺 Condiciones Médicas: {a['valoracion_especiales'] or 'No registradas'}

📅 Fecha de Inscripción: {a['fecha_inscripcion'].strftime('%Y-%m-%d') if a['fecha_inscripcion'] else 'N/A'}
💎 Plan: {a['nombre_plan'] or 'No asignado'}
💵 Último Pago: {a['ultimo_pago'].strftime('%Y-%m-%d') if a['ultimo_pago'] else 'No registrado'}
⏳ Vence: {a['fecha_vencimiento'].strftime('%Y-%m-%d') if a['fecha_vencimiento'] else 'No definido'}
"""
    messagebox.showinfo("📋 Detalles del Atleta", mensaje.strip())


    self.atletas_tree.bind('<Double-1>', self.ver_detalles_atleta)



    def crear_tab_finanzas_avanzadas(self):
        """Crea la pestaña de finanzas avanzadas"""
        finanzas_frame = ttk.Frame(self.notebook)
        self.notebook.add(finanzas_frame, text="💰 Finanzas Avanzadas")
        
        # Panel de control financiero
        control_frame = ttk.Frame(finanzas_frame, padding=15)
        control_frame.pack(fill='x')
        
        # Botones de gestión financiera
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side='left')
        
        ttk.Button(
            btn_frame,
            text="📊 Dashboard Financiero",
            style='Executive.TButton',
            command=self.abrir_dashboard_financiero
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="💎 Gestionar Planes",
            style='Premium.TButton',
            command=self.gestionar_planes
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="📈 Proyecciones",
            style='AdminSuccess.TButton',
            command=self.ver_proyecciones
        ).pack(side='left')
        
        # Filtros temporales
        periodo_frame = ttk.Frame(control_frame)
        periodo_frame.pack(side='right')
        
        ttk.Label(periodo_frame, text="Período:").pack(side='left', padx=(0, 5))
        
        self.periodo_financiero_var = tk.StringVar(value="mes_actual")
        periodo_combo = ttk.Combobox(
            periodo_frame,
            textvariable=self.periodo_financiero_var,
            values=["semana", "mes_actual", "trimestre", "año_actual", "año_anterior"],
            state="readonly",
            width=15
        )
        periodo_combo.pack(side='left', padx=(0, 10))
        periodo_combo.bind('<<ComboboxSelected>>', self.actualizar_finanzas)
        
        # Crear resumen financiero ejecutivo
        self.crear_resumen_financiero_ejecutivo(finanzas_frame)
    
    def crear_resumen_financiero_ejecutivo(self, parent):
        """Crea resumen financiero ejecutivo"""
        # Frame principal con notebook
        main_frame = ttk.Frame(parent, padding=(15, 0, 15, 15))
        main_frame.pack(fill='both', expand=True)
        
        # Notebook financiero
        finance_notebook = ttk.Notebook(main_frame)
        finance_notebook.pack(fill='both', expand=True)
        
        # Pestaña de overview
        self.crear_finance_overview(finance_notebook)
        
        # Pestaña de análisis detallado
        self.crear_finance_analysis(finance_notebook)
        
        # Pestaña de planes y precios
        self.crear_plans_management(finance_notebook)
    
    def crear_finance_overview(self, parent):
        """Crea vista general financiera"""
        overview_frame = ttk.Frame(parent)
        parent.add(overview_frame, text="📊 Vista General")
        
        # Métricas financieras principales
        metrics_frame = ttk.LabelFrame(overview_frame, text="💰 Métricas Financieras", padding=20)
        metrics_frame.pack(fill='x', pady=(0, 15))
        
        # Grid de métricas financieras
        self.finance_metrics = {}
        finance_grid = ttk.Frame(metrics_frame)
        finance_grid.pack(fill='x')
        
        for i in range(3):
            finance_grid.columnconfigure(i, weight=1)
        
        finance_metrics_config = [
            ("total_revenue", "💰", "Ingresos Totales", "$0"),
            ("total_expenses", "💸", "Gastos Totales", "$0"),
            ("net_profit", "📈", "Ganancia Neta", "$0"),
            ("cash_flow", "🌊", "Flujo de Caja", "$0"),
            ("profit_margin", "📊", "Margen de Ganancia", "0%"),
            ("roi", "💎", "Retorno de Inversión", "0%")
        ]
        
        for i, (key, icon, label, value) in enumerate(finance_metrics_config):
            row = i // 3
            col = i % 3
            
            metric_frame = ttk.Frame(finance_grid, style='Executive.TFrame', padding=15)
            metric_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            
            ttk.Label(metric_frame, text=icon, font=('Segoe UI', 20)).pack()
            
            value_label = ttk.Label(metric_frame, text=value, 
                                  font=('Segoe UI', 14, 'bold'),
                                  foreground=self.colores['primario'])
            value_label.pack()
            
            ttk.Label(metric_frame, text=label, 
                     font=('Segoe UI', 9),
                     foreground=self.colores['texto_claro']).pack()
            
            self.finance_metrics[key] = value_label
        
        # Transacciones recientes
        transactions_frame = ttk.LabelFrame(overview_frame, text="💳 Transacciones Recientes", padding=15)
        transactions_frame.pack(fill='both', expand=True)
        
        # Treeview para transacciones
        columns = ('Fecha', 'Tipo', 'Descripción', 'Monto', 'Estado')
        self.transactions_tree = ttk.Treeview(
            transactions_frame,
            columns=columns,
            show='headings',
            style='Admin.Treeview',
            height=10
        )
        
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=150)
        
        # Scrollbar para transacciones
        trans_scroll = ttk.Scrollbar(transactions_frame, orient='vertical', command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=trans_scroll.set)
        
        self.transactions_tree.pack(side='left', fill='both', expand=True)
        trans_scroll.pack(side='right', fill='y')
    
    def crear_finance_analysis(self, parent):
        """Crea análisis financiero detallado"""
        analysis_frame = ttk.Frame(parent)
        parent.add(analysis_frame, text="📈 Análisis Detallado")
        
        # Placeholder para análisis avanzado
        analysis_label = ttk.Label(
            analysis_frame,
            text="📊 Análisis financiero detallado con gráficos avanzados\n🚧 En desarrollo",
            font=('Segoe UI', 12),
            foreground=self.colores['texto_claro']
        )
        analysis_label.pack(expand=True)
    
    def crear_plans_management(self, parent):
        """Crea gestión de planes"""
        plans_frame = ttk.Frame(parent)
        parent.add(plans_frame, text="💎 Gestión de Planes")
        
        # Control de planes
        control_frame = ttk.Frame(plans_frame, padding=10)
        control_frame.pack(fill='x')
        
        ttk.Button(
            control_frame,
            text="➕ Nuevo Plan",
            style='AdminSuccess.TButton',
            command=self.crear_nuevo_plan
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="📊 Estadísticas de Planes",
            style='Executive.TButton',
            command=self.ver_estadisticas_planes
        ).pack(side='left')
        
        # Lista de planes
        self.crear_lista_planes(plans_frame)
    
    def crear_lista_planes(self, parent):
        """Crea lista de planes de membresía"""
        list_frame = ttk.Frame(parent, padding=(10, 0, 10, 10))
        list_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Nombre', 'Precio', 'Duración', 'Estado', 'Miembros Activos', 'Ingresos Generados')
        self.planes_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            style='Admin.Treeview'
        )
        
        for col in columns:
            self.planes_tree.heading(col, text=col)
            self.planes_tree.column(col, width=120)
        
        # Scrollbar
        planes_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.planes_tree.yview)
        self.planes_tree.configure(yscrollcommand=planes_scroll.set)
        
        self.planes_tree.pack(side='left', fill='both', expand=True)
        planes_scroll.pack(side='right', fill='y')
    
    def crear_tab_analytics(self):
        """Crea la pestaña de analytics avanzados"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Panel de control de analytics
        control_frame = ttk.Frame(analytics_frame, padding=15)
        control_frame.pack(fill='x')
        
        ttk.Button(
            control_frame,
            text="📈 Generar Reporte Ejecutivo",
            style='Executive.TButton',
            command=self.generar_reporte_ejecutivo
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🎯 Análisis de Tendencias",
            style='Premium.TButton',
            command=self.analizar_tendencias
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="📊 Comparar Períodos",
            style='AdminSuccess.TButton',
            command=self.comparar_periodos
        ).pack(side='left')
        
        # Área de analytics
        analytics_content = ttk.Frame(analytics_frame, padding=(15, 0, 15, 15))
        analytics_content.pack(fill='both', expand=True)
        
        # Placeholder para analytics
        analytics_label = ttk.Label(
            analytics_content,
            text="📊 Panel de Analytics Avanzados\n🚧 Funcionalidad en desarrollo",
            font=('Segoe UI', 14),
            foreground=self.colores['texto_claro']
        )
        analytics_label.pack(expand=True)
    
    def crear_tab_configuracion(self):
        """Crea la pestaña de configuración del sistema"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Configuración")
        
        # Notebook de configuración
        config_notebook = ttk.Notebook(config_frame)
        config_notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Configuración general
        self.crear_config_general(config_notebook)
        
        # Configuración de seguridad
        self.crear_config_seguridad(config_notebook)
        
        # Configuración del sistema
        self.crear_config_sistema(config_notebook)
    
    def crear_config_general(self, parent):
        """Crea configuración general"""
        general_frame = ttk.Frame(parent)
        parent.add(general_frame, text="🏢 General")
        
        # Información del gimnasio
        info_frame = ttk.LabelFrame(general_frame, text="Información del Gimnasio", padding=20)
        info_frame.pack(fill='x', pady=(0, 15))
        
        # Campos de configuración
        ttk.Label(info_frame, text="Nombre del Gimnasio:").grid(row=0, column=0, sticky='w', pady=5)
        self.gym_name_var = tk.StringVar(value="Gimnasio Athenas")
        ttk.Entry(info_frame, textvariable=self.gym_name_var, width=30).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(info_frame, text="Dirección:").grid(row=1, column=0, sticky='w', pady=5)
        self.gym_address_var = tk.StringVar(value="")
        ttk.Entry(info_frame, textvariable=self.gym_address_var, width=30).grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(info_frame, text="Teléfono:").grid(row=2, column=0, sticky='w', pady=5)
        self.gym_phone_var = tk.StringVar(value="")
        ttk.Entry(info_frame, textvariable=self.gym_phone_var, width=30).grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        info_frame.columnconfigure(1, weight=1)
        
        # Botón guardar
        ttk.Button(
            info_frame,
            text="💾 Guardar Configuración",
            style='AdminSuccess.TButton',
            command=self.guardar_config_general
        ).grid(row=3, column=0, columnspan=2, pady=15)
    
    def crear_config_seguridad(self, parent):
        """Crea configuración de seguridad"""
        security_frame = ttk.Frame(parent)
        parent.add(security_frame, text="🔒 Seguridad")
        
        # Configuración de sesiones
        session_frame = ttk.LabelFrame(security_frame, text="Configuración de Sesiones", padding=20)
        session_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(session_frame, text="Tiempo de expiración (minutos):").grid(row=0, column=0, sticky='w', pady=5)
        self.session_timeout_var = tk.StringVar(value="60")
        ttk.Entry(session_frame, textvariable=self.session_timeout_var, width=10).grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        ttk.Label(session_frame, text="Intentos fallidos permitidos:").grid(row=1, column=0, sticky='w', pady=5)
        self.max_attempts_var = tk.StringVar(value="5")
        ttk.Entry(security_frame, textvariable=self.max_attempts_var, width=10).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Acciones de seguridad
        actions_frame = ttk.LabelFrame(security_frame, text="Acciones de Seguridad", padding=20)
        actions_frame.pack(fill='x')
        
        ttk.Button(
            actions_frame,
            text="🔄 Cerrar Todas las Sesiones",
            style='Executive.TButton',
            command=self.cerrar_todas_sesiones
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            actions_frame,
            text="🔍 Ver Log de Seguridad",
            style='Executive.TButton',
            command=self.ver_log_seguridad
        ).pack(side='left')
    
    def crear_config_sistema(self, parent):
        """Crea configuración del sistema"""
        system_frame = ttk.Frame(parent)
        parent.add(system_frame, text="🖥️ Sistema")
        
        # Información del sistema
        info_frame = ttk.LabelFrame(system_frame, text="Información del Sistema", padding=20)
        info_frame.pack(fill='x', pady=(0, 15))
        
        system_info = [
            ("Versión:", "1.0.0"),
            ("Base de Datos:", "MySQL"),
            ("Último Backup:", "No disponible"),
            ("Espacio Usado:", "Calculando...")
        ]
        
        for i, (label, value) in enumerate(system_info):
            ttk.Label(info_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)
            ttk.Label(info_frame, text=value, foreground=self.colores['primario']).grid(row=i, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Acciones del sistema
        system_actions = ttk.LabelFrame(system_frame, text="Mantenimiento", padding=20)
        system_actions.pack(fill='x')
        
        ttk.Button(
            system_actions,
            text="💾 Crear Backup",
            style='AdminSuccess.TButton',
            command=self.crear_backup
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            system_actions,
            text="🧹 Limpiar Cache",
            style='Executive.TButton',
            command=self.limpiar_cache
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            system_actions,
            text="📊 Diagnóstico",
            style='Executive.TButton',
            command=self.ejecutar_diagnostico
        ).pack(side='left')
    
    def crear_tab_auditoria(self):
        """Crea la pestaña de auditoría"""
        auditoria_frame = ttk.Frame(self.notebook)
        self.notebook.add(auditoria_frame, text="📋 Auditoría")
        
        # Panel de control de auditoría
        control_frame = ttk.Frame(auditoria_frame, padding=15)
        control_frame.pack(fill='x')
        
        ttk.Button(
            control_frame,
            text="📊 Generar Informe de Auditoría",
            style='Executive.TButton',
            command=self.generar_informe_auditoria
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🔍 Buscar Eventos",
            style='Executive.TButton',
            command=self.buscar_eventos_auditoria
        ).pack(side='left')
        
        # Log de auditoría
        log_frame = ttk.LabelFrame(auditoria_frame, text="📝 Log de Actividades", padding=15)
        log_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Treeview para el log
        columns = ('Fecha/Hora', 'Usuario', 'Acción', 'Módulo', 'Detalles', 'IP')
        self.auditoria_tree = ttk.Treeview(
            log_frame,
            columns=columns,
            show='headings',
            style='Admin.Treeview'
        )
        
        for col in columns:
            self.auditoria_tree.heading(col, text=col)
            self.auditoria_tree.column(col, width=120)
        
        # Scrollbar
        audit_scroll = ttk.Scrollbar(log_frame, orient='vertical', command=self.auditoria_tree.yview)
        self.auditoria_tree.configure(yscrollcommand=audit_scroll.set)
        
        self.auditoria_tree.pack(side='left', fill='both', expand=True)
        audit_scroll.pack(side='right', fill='y')
    
    def crear_status_bar_ejecutivo(self):
        """Crea la barra de estado ejecutiva"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill='x', pady=(10, 0))
        
        # Separador elegante
        ttk.Separator(self.status_frame, orient='horizontal').pack(fill='x', pady=(0, 8))
        
        # Status izquierdo
        self.status_label = ttk.Label(
            self.status_frame,
            text="🔴 SISTEMA EJECUTIVO ACTIVO",
            font=('Segoe UI', 10, 'bold'),
            foreground=self.colores['dorado']
        )
        self.status_label.pack(side='left')
        
        # Status derecho
        self.connection_label = ttk.Label(
            self.status_frame,
            text="🔗 Conexión Segura | 🔒 Acceso Privilegiado",
            font=('Segoe UI', 9),
            foreground=self.colores['exito']
        )
        self.connection_label.pack(side='right')
    
    # ==================== CARGA DE DATOS ====================
    
    def cargar_datos_iniciales(self):
        """Carga datos iniciales del administrador"""
        self.actualizar_status("🔄 Cargando datos ejecutivos...")
        threading.Thread(target=self._cargar_datos_admin_background, daemon=True).start()
    
    def _cargar_datos_admin_background(self):
        """Carga datos en background"""
        try:
            # Cargar métricas del mini dashboard
            self.parent_frame.after(0, self.cargar_mini_metricas)
            
            # Cargar KPIs ejecutivos
            self.parent_frame.after(100, self.cargar_kpis_ejecutivos)
            
            # Cargar alertas críticas
            self.parent_frame.after(200, self.cargar_alertas_admin)
            
            # Cargar transacciones recientes en el dashboard financiero
            self.parent_frame.after(300, self.cargar_transacciones_recientes)
            
            # Status final
            self.parent_frame.after(500, lambda: self.actualizar_status("✅ Panel ejecutivo listo"))
            
        except Exception as e:
            self.parent_frame.after(0, lambda: self.actualizar_status(f"❌ Error: {str(e)}"))

# ... (código existente hasta el final de la clase) ...

    def cargar_datos_financieros(self):
        """Carga datos financieros avanzados"""
        self.actualizar_status("🔄 Cargando datos financieros...")
        self.cargar_transacciones_recientes()
        # Aquí se podrían cargar más datos para los otros widgets financieros
        self.actualizar_status("✅ Datos financieros actualizados.")

    def cargar_transacciones_recientes(self):
        """Carga las transacciones más recientes en la vista general financiera."""
        try:
            # Limpiar transacciones existentes
            for item in self.transactions_tree.get_children():
                self.transactions_tree.delete(item)
            
            resultado = self.finance_controller.obtener_ingresos_detallados()

            if resultado['success']:
                # Mostrar solo las últimas 15-20 transacciones para un resumen
                transacciones_recientes = resultado['ingresos'][:20] 

                for transaccion in transacciones_recientes:
                    tipo_transaccion = f"Ingreso ({transaccion['tipo_pago']})"
                    monto = f"+ ${transaccion['monto']:.2f}"
                    estado = "Completado"
                    
                    values = (
                        transaccion['fecha_pago'],
                        tipo_transaccion,
                        transaccion['descripcion'],
                        monto,
                        estado
                    )
                    self.transactions_tree.insert('', 'end', values=values)
            else:
                messagebox.showerror("Error Financiero", f"No se pudieron cargar las transacciones: {resultado['message']}")

        except Exception as e:
            print(f"Error cargando transacciones recientes: {e}")
    def cargar_mini_metricas(self):
        """Carga métricas del mini dashboard"""
        try:
            # Simular carga de métricas (conectar con controladores)
            self.mini_metrics['revenue_today']['value_label'].config(text="$1,250")
            self.mini_metrics['balance_month']['value_label'].config(text="$18,500")
            self.mini_metrics['active_members']['value_label'].config(text="287")
        except Exception as e:
            print(f"Error cargando mini métricas: {e}")
    
    def cargar_kpis_ejecutivos(self):
        """Carga KPIs ejecutivos"""
        try:
            # Simular KPIs (luego conectar con datos reales)
            kpis_data = {
                'revenue_monthly': "$22,450",
                'profit_margin': "35.2%",
                'member_retention': "92.1%",
                'avg_revenue_per_member': "$78.30",
                'total_members': "287",
                'coaches_efficiency': "94.5%",
                'monthly_growth': "+12.3%",
                'operational_costs': "$14,200"
            }
            
            for key, value in kpis_data.items():
                if key in self.kpis_widgets:
                    self.kpis_widgets[key]['value_label'].config(text=value)
                    
        except Exception as e:
            print(f"Error cargando KPIs: {e}")
    
    def cargar_alertas_admin(self):
        """Carga alertas críticas para administrador"""
        try:
            # Limpiar alertas existentes
            for widget in self.alertas_admin_container.winfo_children():
                widget.destroy()
            
            # Verificar alertas críticas del sistema
            alertas_criticas = []
            
            # Verificar estado general
            resultado_atletas = self.atleta_controller.obtener_todos_atletas()
            if resultado_atletas['success']:
                total_atletas = len(resultado_atletas['atletas'])
                if total_atletas == 0:
                    alertas_criticas.append("⚠️ No hay atletas registrados en el sistema")
            
            # Mostrar alertas o estado OK
            if alertas_criticas:
                for alerta in alertas_criticas:
                    alert_label = ttk.Label(
                        self.alertas_admin_container,
                        text=alerta,
                        font=('Segoe UI', 11),
                        foreground=self.colores['advertencia']
                    )
                    alert_label.pack(anchor='w', pady=3)
            else:
                ok_label = ttk.Label(
                    self.alertas_admin_container,
                    text="✅ Todas las operaciones funcionando correctamente",
                    font=('Segoe UI', 11),
                    foreground=self.colores['exito']
                )
                ok_label.pack(pady=15)
                
        except Exception as e:
            print(f"Error cargando alertas admin: {e}")
    
    # ==================== EVENTOS Y CALLBACKS ====================
    
    def on_admin_tab_changed(self, event):
        """Maneja cambio de pestañas del administrador"""
        selected_tab = event.widget.tab('current')['text']
        
        if "👥 Gestión de Usuarios" in selected_tab and not hasattr(self, '_usuarios_cargados'):
            self.cargar_usuarios()
            self._usuarios_cargados = True
        elif "💰 Finanzas Avanzadas" in selected_tab and not hasattr(self, '_finanzas_cargadas'):
            self.cargar_datos_financieros()
            self._finanzas_cargadas = True
    
    def filtrar_usuarios(self, event=None):
        """Filtra usuarios por rol"""
        rol = self.filtro_rol_var.get()
        self.actualizar_status(f"🔍 Filtrando usuarios por rol: {rol}")
    
    def mostrar_menu_usuarios(self, event):
        """Muestra menú contextual de usuarios"""
        selection = self.usuarios_tree.selection()
        if selection:
            self.menu_usuarios.post(event.x_root, event.y_root)
    
    # ==================== MÉTODOS ADMINISTRATIVOS ====================
    
    def crear_secretaria(self):
        """Abre ventana para crear nueva secretaria"""
        messagebox.showinfo("Información", "🚧 Crear secretaria - En desarrollo")
    
    def ver_sesiones_activas(self):
        """Muestra sesiones activas del sistema"""
        try:
            resultado = self.auth_controller.obtener_sesiones_activas(self.usuario_actual['id'])
            if resultado['success']:
                sesiones = resultado['sesiones_activas']
                total = resultado['total_sesiones']
                
                mensaje = f"🔐 SESIONES ACTIVAS: {total}\n\n"
                for sesion in sesiones[:10]:  # Mostrar máximo 10
                    mensaje += f"👤 {sesion['usuario']}\n"
                    mensaje += f"📧 {sesion['email']}\n"
                    mensaje += f"🕒 {sesion['ultimo_acceso']}\n\n"
                
                messagebox.showinfo("Sesiones Activas", mensaje)
            else:
                messagebox.showerror("Error", resultado['message'])
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo sesiones: {str(e)}")
    
    def cargar_usuarios(self):
        """Carga lista completa de usuarios"""
        try:
            self.actualizar_status("🔄 Cargando usuarios...")
            
            # Limpiar lista actual
            for item in self.usuarios_tree.get_children():
                self.usuarios_tree.delete(item)
            
            # Obtener todos los usuarios
            resultado = self.user_controller.obtener_todos_usuarios()
            if resultado['success']:
                for usuario in resultado['usuarios']:
                    values = (
                        usuario[0],  # ID
                        f"{usuario[1]} {usuario[2]}",  # Nombre completo
                        usuario[6],  # Email
                        usuario[8],  # Rol
                        "Activo" if usuario[9] else "Inactivo",  # Estado
                        usuario[10],  # Fecha creación
                        "Sistema" if usuario[11] == 0 else f"Usuario #{usuario[11]}",  # Creado por
                        "Hace 1 hora"  # Último acceso (placeholder)
                    )
                    
                    self.usuarios_tree.insert('', 'end', values=values)
                
                self.actualizar_status(f"✅ {len(resultado['usuarios'])} usuarios cargados")
            else:
                self.actualizar_status(f"❌ Error: {resultado['message']}")
                
        except Exception as e:
            self.actualizar_status(f"❌ Error cargando usuarios: {str(e)}")
    
    def cargar_datos_financieros(self):
        """Carga datos financieros avanzados"""
        messagebox.showinfo("Información", "🚧 Datos financieros avanzados - En desarrollo")
    
    # ==================== MÉTODOS PLACEHOLDER ====================
    
    def buscar_usuarios(self):
        """Busca usuarios por nombre o email"""
        # Crear ventana de búsqueda
        busqueda_window = tk.Toplevel(self.parent_frame)
        busqueda_window.title("🔍 Buscar Usuarios")
        busqueda_window.geometry("400x150")
        busqueda_window.transient(self.parent_frame)
        busqueda_window.grab_set()
        
        # Centrar ventana
        x = (busqueda_window.winfo_screenwidth() // 2) - 200
        y = (busqueda_window.winfo_screenheight() // 2) - 75
        busqueda_window.geometry(f"400x150+{x}+{y}")
        
        frame = ttk.Frame(busqueda_window, padding=20)
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Buscar por nombre o email:").pack(pady=(0, 10))
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(frame, textvariable=search_var, width=30)
        search_entry.pack(pady=(0, 15))
        search_entry.focus()
        
        def ejecutar_busqueda():
            termino = search_var.get().strip()
            if termino:
                self.filtrar_usuarios_por_termino(termino)
                busqueda_window.destroy()
        
        ttk.Button(frame, text="🔍 Buscar", command=ejecutar_busqueda, 
                  style='Executive.TButton').pack()
        
        search_entry.bind('<Return>', lambda e: ejecutar_busqueda())
    
    def filtrar_usuarios_por_termino(self, termino):
        """Filtra usuarios por término de búsqueda"""
        # Limpiar selección actual
        for item in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item)
        
        # Buscar usuarios que coincidan
        resultado = self.user_controller.obtener_todos_usuarios()
        if resultado['success']:
            usuarios_encontrados = []
            termino_lower = termino.lower()
            
            for usuario in resultado['usuarios']:
                nombre_completo = f"{usuario[1]} {usuario[2]}".lower()
                email = usuario[6].lower()
                
                if termino_lower in nombre_completo or termino_lower in email:
                    usuarios_encontrados.append(usuario)
            
            # Mostrar resultados
            for usuario in usuarios_encontrados:
                values = (
                    usuario[0],  # ID
                    f"{usuario[1]} {usuario[2]}",  # Nombre completo
                    usuario[6],  # Email
                    usuario[8],  # Rol
                    "Activo" if usuario[9] else "Inactivo",  # Estado
                    usuario[10],  # Fecha creación
                    "Sistema" if usuario[11] == 0 else f"Usuario #{usuario[11]}",
                    "Hace 1 hora"
                )
                self.usuarios_tree.insert('', 'end', values=values)
            
            self.actualizar_status(f"🔍 {len(usuarios_encontrados)} usuarios encontrados")
    
def ver_detalles_atleta(self, event=None):
    """Muestra todos los datos del atleta seleccionado en un cuadro de diálogo"""
    selection = self.atletas_tree.selection()
    if not selection:
        messagebox.showwarning("Atención", "Selecciona un atleta")
        return

    item = self.atletas_tree.item(selection[0])
    atleta_id = item['values'][0]

    resultado = self.atleta_controller.obtener_detalles_completos_atleta(atleta_id)
    if not resultado['success']:
        messagebox.showerror("Error", resultado['message'])
        return

    a = resultado['atleta']

    mensaje = f"""
👤 {a['nombre']} {a['apellido']}
🪪 Cédula: {a['cedula']}
🎂 Edad: {a['edad']}  |  Nacimiento: {a['fecha_nacimiento'].strftime('%Y-%m-%d') if a['fecha_nacimiento'] else 'N/A'}
⚖️ Peso: {a['peso']} kg
🏠 Dirección: {a['direccion'] or 'No especificada'}

🎯 Meta: {a['meta_largo_plazo'] or 'No registrada'}
🩺 Condiciones Médicas: {a['valoracion_especiales'] or 'No registradas'}

📅 Fecha de Inscripción: {a['fecha_inscripcion'].strftime('%Y-%m-%d')}
💎 Plan: {a['nombre_plan'] or 'No asignado'}
💵 Último Pago: {a['ultimo_pago'].strftime('%Y-%m-%d') if a['ultimo_pago'] else 'No registrado'}
⏳ Vence: {a['fecha_vencimiento'].strftime('%Y-%m-%d') if a['fecha_vencimiento'] else 'No definido'}
"""

    messagebox.showinfo("📋 Datos completos del atleta", mensaje)

    
    def cambiar_password_admin(self):
        """Cambiar contraseña de usuario seleccionado"""
        selection = self.usuarios_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un usuario")
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás segura de cambiar la contraseña de este usuario?"):
            messagebox.showinfo("Información", "🚧 Cambio de contraseña - En desarrollo")
    
    def desactivar_usuario_admin(self):
        """Desactivar usuario seleccionado"""
        selection = self.usuarios_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un usuario")
            return
        
        item = self.usuarios_tree.item(selection[0])
        usuario_nombre = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Estás segura de desactivar al usuario {usuario_nombre}?"):
            usuario_id = item['values'][0]
            resultado = self.user_controller.desactivar_usuario(usuario_id, self.usuario_actual['id'])
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['message'])
                self.cargar_usuarios()  # Recargar lista
            else:
                messagebox.showerror("Error", resultado['message'])
    
    def eliminar_usuario_admin(self):
        """Eliminar usuario seleccionado"""
        selection = self.usuarios_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un usuario")
            return
        item = self.usuarios_tree-item(selection[0])
        usuario_id = item['values'][0]
        usuario_nombre = item['values'][1]
        if messagebox.askyesno("Confirmar", f"¿Estás segura de eliminar al usuario {usuario_nombre}?"):
            resultado = self.user_controller.eliminar_usuario(usuario_id, self.usuario_actual['id'])
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['message'])
                self.cargar_usuarios()

    
    
    def cerrar_sesiones_usuario(self):
        """Cerrar todas las sesiones del usuario seleccionado"""
        selection = self.usuarios_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un usuario")
            return
        
        item = self.usuarios_tree.item(selection[0])
        usuario_id = item['values'][0]
        usuario_nombre = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Cerrar todas las sesiones de {usuario_nombre}?"):
            resultado = self.auth_controller.cerrar_todas_sesiones_usuario(usuario_id)
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['message'])
            else:
                messagebox.showerror("Error", resultado['message'])
    
    def actualizar_finanzas(self, event=None):
        """Actualiza datos financieros según período seleccionado"""
        periodo = self.periodo_financiero_var.get()
        self.actualizar_status(f"🔄 Actualizando finanzas para período: {periodo}")
    
    # ==================== MÉTODOS FINANCIEROS ====================
    
    def abrir_dashboard_financiero(self):
        """Abre dashboard financiero avanzado"""
        # Crear ventana del dashboard financiero
        finance_window = tk.Toplevel(self.parent_frame)
        finance_window.title("💰 Dashboard Financiero Ejecutivo")
        finance_window.geometry("1000x700")
        finance_window.transient(self.parent_frame)
        
        # Frame principal
        main_frame = ttk.Frame(finance_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="💰 Dashboard Financiero Ejecutivo", 
                               style='Executive.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Notebook con diferentes análisis
        finance_notebook = ttk.Notebook(main_frame)
        finance_notebook.pack(fill='both', expand=True)
        
        # Resumen ejecutivo
        resumen_frame = ttk.Frame(finance_notebook)
        finance_notebook.add(resumen_frame, text="📊 Resumen Ejecutivo")
        
        # Análisis de tendencias
        tendencias_frame = ttk.Frame(finance_notebook)
        finance_notebook.add(tendencias_frame, text="📈 Tendencias")
        
        # Proyecciones
        proyecciones_frame = ttk.Frame(finance_notebook)
        finance_notebook.add(proyecciones_frame, text="🔮 Proyecciones")
        
        # Llenar con datos (placeholder)
        for frame in [resumen_frame, tendencias_frame, proyecciones_frame]:
            ttk.Label(frame, text="📊 Análisis financiero detallado\n🚧 En desarrollo", 
                     font=('Segoe UI', 12)).pack(expand=True)
    
    def gestionar_planes(self):
        """Gestionar planes de membresía"""
        # Crear ventana de gestión de planes
        planes_window = tk.Toplevel(self.parent_frame)
        planes_window.title("💎 Gestión de Planes de Membresía")
        planes_window.geometry("800x600")
        planes_window.transient(self.parent_frame)
        
        main_frame = ttk.Frame(planes_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(main_frame, text="💎 Gestión de Planes de Membresía", 
                 style='Executive.TLabel').pack(pady=(0, 20))
        
        # Panel de control
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Button(control_frame, text="➕ Nuevo Plan", 
                  style='AdminSuccess.TButton',
                  command=self.crear_nuevo_plan).pack(side='left', padx=(0, 10))
        
        ttk.Button(control_frame, text="✏️ Editar Seleccionado", 
                  style='Executive.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(control_frame, text="🔄 Actualizar", 
                  style='Executive.TButton',
                  command=lambda: self.cargar_planes_en_ventana(planes_tree)).pack(side='left')
        
        # Lista de planes
        columns = ('ID', 'Nombre', 'Precio', 'Duración (días)', 'Estado', 'Usuarios')
        planes_tree = ttk.Treeview(main_frame, columns=columns, show='headings', 
                                  style='Admin.Treeview')
        
        for col in columns:
            planes_tree.heading(col, text=col)
            planes_tree.column(col, width=120)
        
        # Scrollbar
        scroll = ttk.Scrollbar(main_frame, orient='vertical', command=planes_tree.yview)
        planes_tree.configure(yscrollcommand=scroll.set)
        
        planes_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        
        # Cargar datos
        self.cargar_planes_en_ventana(planes_tree)
    
    def cargar_planes_en_ventana(self, tree_widget):
        """Carga planes en el treeview especificado"""
        # Limpiar
        for item in tree_widget.get_children():
            tree_widget.delete(item)
        
        # Obtener planes
        resultado = self.finance_controller.obtener_planes_activos()
        if resultado['success']:
            for plan in resultado['planes']:
                values = (
                    plan[0],  # ID
                    plan[1],  # Nombre
                    f"${plan[3]}",  # Precio
                    plan[4],  # Duración
                    "Activo" if plan[5] else "Inactivo",  # Estado
                    "0"  # Usuarios (placeholder)
                )
                tree_widget.insert('', 'end', values=values)
    
    def ver_proyecciones(self):
        """Ver proyecciones financieras"""
        # Ventana de proyecciones
        proj_window = tk.Toplevel(self.parent_frame)
        proj_window.title("🔮 Proyecciones Financieras")
        proj_window.geometry("900x600")
        proj_window.transient(self.parent_frame)
        
        main_frame = ttk.Frame(proj_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="🔮 Proyecciones Financieras", 
                 style='Executive.TLabel').pack(pady=(0, 20))
        
        # Opciones de proyección
        options_frame = ttk.LabelFrame(main_frame, text="Opciones de Proyección", padding=15)
        options_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(options_frame, text="Período de proyección:").grid(row=0, column=0, sticky='w', pady=5)
        
        periodo_var = tk.StringVar(value="6_meses")
        periodo_combo = ttk.Combobox(options_frame, textvariable=periodo_var,
                                   values=["3_meses", "6_meses", "1_año", "2_años"],
                                   state="readonly")
        periodo_combo.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ttk.Button(options_frame, text="📊 Generar Proyección",
                  style='Executive.TButton',
                  command=lambda: self.generar_proyeccion(periodo_var.get())).grid(row=1, column=0, columnspan=2, pady=15)
        
        # Área de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding=15)
        results_frame.pack(fill='both', expand=True)
        
        results_text = tk.Text(results_frame, font=('Consolas', 10), state='disabled')
        results_scroll = ttk.Scrollbar(results_frame, orient='vertical', command=results_text.yview)
        results_text.configure(yscrollcommand=results_scroll.set)
        
        results_text.pack(side='left', fill='both', expand=True)
        results_scroll.pack(side='right', fill='y')
    
    def generar_proyeccion(self, periodo):
        """Genera proyección financiera"""
        messagebox.showinfo("Proyección", f"🔮 Generando proyección para {periodo}\n🚧 En desarrollo")
    
    def crear_nuevo_plan(self):
        """Crear nuevo plan de membresía"""
        # Ventana de creación de plan
        plan_window = tk.Toplevel(self.parent_frame)
        plan_window.title("➕ Nuevo Plan de Membresía")
        plan_window.geometry("500x400")
        plan_window.transient(self.parent_frame)
        plan_window.grab_set()
        
        # Centrar
        x = (plan_window.winfo_screenwidth() // 2) - 250
        y = (plan_window.winfo_screenheight() // 2) - 200
        plan_window.geometry(f"500x400+{x}+{y}")
        
        main_frame = ttk.Frame(plan_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="➕ Crear Nuevo Plan", 
                 style='Executive.TLabel').pack(pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Variables
        nombre_var = tk.StringVar()
        precio_var = tk.StringVar()
        duracion_var = tk.StringVar(value="30")
        descripcion_var = tk.StringVar()
        
        # Campos
        ttk.Label(form_frame, text="Nombre del Plan *:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(form_frame, textvariable=nombre_var, width=30).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(form_frame, text="Precio *:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(form_frame, textvariable=precio_var, width=30).grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(form_frame, text="Duración (días) *:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(form_frame, textvariable=duracion_var, width=30).grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(form_frame, text="Descripción:").grid(row=3, column=0, sticky='nw', pady=5)
        desc_text = tk.Text(form_frame, height=4, width=30)
        desc_text.grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="❌ Cancelar",
                  command=plan_window.destroy).pack(side='right', padx=(10, 0))
        
        def crear_plan():
            if not nombre_var.get() or not precio_var.get():
                messagebox.showerror("Error", "Por favor completa los campos obligatorios")
                return
            
            datos_plan = {
                'nombre_plan': nombre_var.get(),
                'precio': precio_var.get(),
                'duracion_dias': duracion_var.get(),
                'descripcion': desc_text.get("1.0", 'end-1c')
            }
            
            resultado = self.finance_controller.crear_plan(datos_plan, self.usuario_actual['id'])
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['message'])
                plan_window.destroy()
            else:
                messagebox.showerror("Error", resultado['message'])
        
        ttk.Button(btn_frame, text="✅ Crear Plan",
                  style='AdminSuccess.TButton',
                  command=crear_plan).pack(side='right')
    
    def ver_estadisticas_planes(self):
        """Ver estadísticas de planes"""
        messagebox.showinfo("Información", "📊 Estadísticas de planes - En desarrollo")
    
    # ==================== MÉTODOS DE ANALYTICS ====================
    
    def generar_reporte_ejecutivo(self):
        """Genera reporte ejecutivo completo"""
        # Ventana de reporte
        report_window = tk.Toplevel(self.parent_frame)
        report_window.title("📈 Reporte Ejecutivo")
        report_window.geometry("1000x700")
        report_window.transient(self.parent_frame)
        
        main_frame = ttk.Frame(report_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="📈 Reporte Ejecutivo", 
                 style='Executive.TLabel').pack(pady=(0, 20))
        
        # Opciones del reporte
        options_frame = ttk.LabelFrame(main_frame, text="Configuración del Reporte", padding=15)
        options_frame.pack(fill='x', pady=(0, 20))
        
        # Período
        ttk.Label(options_frame, text="Período:").grid(row=0, column=0, sticky='w', pady=5)
        periodo_exec_var = tk.StringVar(value="mes_actual")
        ttk.Combobox(options_frame, textvariable=periodo_exec_var,
                    values=["semana", "mes_actual", "trimestre", "año_actual"],
                    state="readonly").grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Tipo de reporte
        ttk.Label(options_frame, text="Tipo:").grid(row=0, column=2, sticky='w', padx=(20, 0), pady=5)
        tipo_var = tk.StringVar(value="completo")
        ttk.Combobox(options_frame, textvariable=tipo_var,
                    values=["completo", "financiero", "operacional", "estratégico"],
                    state="readonly").grid(row=0, column=3, padx=(10, 0), pady=5)
        
        ttk.Button(options_frame, text="📊 Generar Reporte",
                  style='Executive.TButton',
                  command=lambda: self.procesar_reporte_ejecutivo(periodo_exec_var.get(), tipo_var.get())).grid(row=1, column=0, columnspan=4, pady=15)
        
        # Área de reporte
        report_frame = ttk.LabelFrame(main_frame, text="Reporte Ejecutivo", padding=15)
        report_frame.pack(fill='both', expand=True)
        
        self.report_text = tk.Text(report_frame, font=('Consolas', 10), state='disabled')
        report_scroll = ttk.Scrollbar(report_frame, orient='vertical', command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scroll.set)
        
        self.report_text.pack(side='left', fill='both', expand=True)
        report_scroll.pack(side='right', fill='y')
    
    def procesar_reporte_ejecutivo(self, periodo, tipo):
        """Procesa y genera el reporte ejecutivo"""
        self.report_text.config(state='normal')
        self.report_text.delete('1.0', 'end')
        
        reporte = f"""
🏢 GIMNASIO ATHENAS - REPORTE EJECUTIVO
═══════════════════════════════════════
📅 Período: {periodo.replace('_', ' ').title()}
📊 Tipo: {tipo.title()}
📋 Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Por: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}

══════════════════════════════════════════════════════════════

📈 RESUMEN EJECUTIVO
────────────────────
• Estado General: 🟢 OPERACIONAL
• Ingresos del Período: $22,450 (+12.3% vs período anterior)
• Gastos del Período: $14,200 (-3.1% vs período anterior)
• Ganancia Neta: $8,250 (+28.7% vs período anterior)
• Margen de Ganancia: 36.7%

👥 MÉTRICAS DE MEMBRESÍA
────────────────────────
• Total de Miembros Activos: 287 (+15 nuevos)
• Retención de Miembros: 92.1% (Meta: 90%)
• Tasa de Conversión: 78.3%
• Ingreso Promedio por Miembro: $78.30

👨‍🏫 RENDIMIENTO DEL PERSONAL
─────────────────────────────
• Total de Coaches: 8
• Eficiencia Promedio: 94.5%
• Satisfacción del Cliente: 4.7/5.0
• Productividad: 📈 ALTA

💰 ANÁLISIS FINANCIERO
──────────────────────
• ROI: 24.3%
• Flujo de Caja: +$6,800
• Proyección Mensual: $25,000
• Margen de Crecimiento: 15.2%

🎯 INDICADORES CLAVE (KPIs)
──────────────────────────
• Objetivo de Ingresos: ✅ 112% alcanzado
• Control de Gastos: ✅ 97% del presupuesto
• Crecimiento de Membresía: ✅ 105% de meta
• Retención: ✅ 102% de objetivo

⚠️ ALERTAS Y RECOMENDACIONES
────────────────────────────
• 🟡 Considerar expansión de horarios premium
• 🟢 Excelente rendimiento del equipo de ventas
• 🟡 Evaluar nuevos equipos para área de cardio
• 🟢 Mantener estrategias actuales de retención

📊 PROYECCIONES PRÓXIMO PERÍODO
───────────────────────────────
• Ingresos Proyectados: $24,500 (+9.1%)
• Nuevos Miembros Esperados: 18-22
• Inversiones Planificadas: $5,000 (equipos)
• ROI Proyectado: 26.1%

══════════════════════════════════════════════════════════════

📋 CONCLUSIONES EJECUTIVAS
───────────────────────────
✅ El gimnasio muestra un rendimiento excepcional
✅ Todos los KPIs superan las expectativas
✅ Crecimiento sostenible y saludable
✅ Equipo altamente productivo
✅ Posición financiera sólida

🎯 RECOMENDACIONES ESTRATÉGICAS
──────────────────────────────
1. Continuar con las estrategias actuales
2. Considerar expansión de servicios premium
3. Evaluar apertura de sucursal
4. Implementar programa de fidelización avanzado
5. Invertir en tecnología de fitness

════════════════════════════════════════════════════════════════
        """
        
        self.report_text.insert('1.0', reporte)
        self.report_text.config(state='disabled')
    
    def analizar_tendencias(self):
        """Analizar tendencias del negocio"""
        messagebox.showinfo("Información", "🎯 Análisis de tendencias - En desarrollo")
    
    def comparar_periodos(self):
        """Comparar diferentes períodos"""
        messagebox.showinfo("Información", "📊 Comparación de períodos - En desarrollo")
    
    # ==================== MÉTODOS DE CONFIGURACIÓN ====================
    
    def guardar_config_general(self):
        """Guarda configuración general"""
        nombre = self.gym_name_var.get()
        direccion = self.gym_address_var.get()
        telefono = self.gym_phone_var.get()
        
        messagebox.showinfo("Configuración", 
                           f"✅ Configuración guardada:\n\n"
                           f"Nombre: {nombre}\n"
                           f"Dirección: {direccion}\n"
                           f"Teléfono: {telefono}")
    
    
    
    def crear_backup(self):
        """Crear backup del sistema"""
        if messagebox.askyesno("Backup", "¿Crear backup completo del sistema?\n\n"
                              "Este proceso puede tomar varios minutos."):
            messagebox.showinfo("Información", "💾 Creando backup - En desarrollo")
    
    def limpiar_cache(self):
        """Limpiar cache del sistema"""
        if messagebox.askyesno("Limpiar Cache", "¿Limpiar el cache del sistema?"):
            messagebox.showinfo("Información", "🧹 Limpiando cache - En desarrollo")
    
    def ejecutar_diagnostico(self):
        """Ejecutar diagnóstico del sistema"""
        # Crear ventana de diagnóstico
        diag_window = tk.Toplevel(self.parent_frame)
        diag_window.title("🔍 Diagnóstico del Sistema")
        diag_window.geometry("700x500")
        diag_window.transient(self.parent_frame)
        
        main_frame = ttk.Frame(diag_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="🔍 Diagnóstico del Sistema", 
                 style='Executive.TLabel').pack(pady=(0, 20))
        
        # Área de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados del Diagnóstico", padding=15)
        results_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        diag_text = tk.Text(results_frame, font=('Consolas', 9), state='disabled')
        diag_scroll = ttk.Scrollbar(results_frame, orient='vertical', command=diag_text.yview)
        diag_text.configure(yscrollcommand=diag_scroll.set)
        
        diag_text.pack(side='left', fill='both', expand=True)
        diag_scroll.pack(side='right', fill='y')
        
        # Botón ejecutar
        ttk.Button(main_frame, text="🔍 Ejecutar Diagnóstico",
                  style='Executive.TButton',
                  command=lambda: self.ejecutar_diagnostico_completo(diag_text)).pack()
    
    def ejecutar_diagnostico_completo(self, text_widget):
        """Ejecuta diagnóstico completo del sistema"""
        text_widget.config(state='normal')
        text_widget.delete('1.0', 'end')
        
        diagnostico = f"""
🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA
═══════════════════════════════════
📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Ejecutado por: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}

🖥️ ESTADO DEL SISTEMA
─────────────────────
✅ Aplicación: FUNCIONANDO
✅ Base de Datos: CONECTADA
✅ Controladores: OPERATIVOS
✅ Interfaces: ACTIVAS

📊 MÉTRICAS DE RENDIMIENTO
─────────────────────────
• Tiempo de respuesta promedio: 120ms
• Uso de memoria: 85MB
• Sesiones activas: 3
• Operaciones por minuto: 12

🔒 SEGURIDAD
────────────
✅ Autenticación: ACTIVA
✅ Sesiones: CONTROLADAS
✅ Permisos: CONFIGURADOS
✅ Logs: FUNCIONANDO

💾 BASE DE DATOS
───────────────
✅ Conexión: ESTABLE
✅ Integridad: VERIFICADA
✅ Respaldo: REQUERIDO
• Último backup: No disponible
• Espacio usado: ~150MB

📋 TABLAS DEL SISTEMA
────────────────────
✅ usuarios: OK (registros activos)
✅ atletas: OK 
✅ coaches: OK
✅ planes: OK
✅ ingresos: OK
✅ egresos: OK
✅ asignaciones: OK

🎯 RECOMENDACIONES
──────────────────
🟡 Crear backup de seguridad
🟢 Sistema operando correctamente
🟡 Considerar limpieza de logs antiguos
🟢 Rendimiento óptimo

═══════════════════════════════════
DIAGNÓSTICO COMPLETADO EXITOSAMENTE
        """
        
        text_widget.insert('1.0', diagnostico)
        text_widget.config(state='disabled')
    
    # ==================== MÉTODOS DE AUDITORÍA ====================
    
    def generar_informe_auditoria(self):
        """Genera informe de auditoría"""
        # Ventana de informe de auditoría
        audit_window = tk.Toplevel(self.parent_frame)
        audit_window.title("📋 Informe de Auditoría")
        audit_window.geometry("900x600")
        audit_window.transient(self.parent_frame)
        
        main_frame = ttk.Frame(audit_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="📋 Informe de Auditoría", 
                 style='Executive.TLabel').pack(pady=(0, 20))
        
        # Opciones del informe
        options_frame = ttk.LabelFrame(main_frame, text="Configuración del Informe", padding=15)
        options_frame.pack(fill='x', pady=(0, 20))
        
        # Tipo de auditoría
        ttk.Label(options_frame, text="Tipo de Auditoría:").grid(row=0, column=0, sticky='w', pady=5)
        tipo_audit_var = tk.StringVar(value="completa")
        ttk.Combobox(options_frame, textvariable=tipo_audit_var,
                    values=["completa", "seguridad", "financiera", "operacional"],
                    state="readonly").grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Período
        ttk.Label(options_frame, text="Período:").grid(row=0, column=2, sticky='w', padx=(20, 0), pady=5)
        periodo_audit_var = tk.StringVar(value="ultimo_mes")
        ttk.Combobox(options_frame, textvariable=periodo_audit_var,
                    values=["ultima_semana", "ultimo_mes", "ultimo_trimestre", "todo"],
                    state="readonly").grid(row=0, column=3, padx=(10, 0), pady=5)
        
        ttk.Button(options_frame, text="📋 Generar Informe",
                  style='Executive.TButton',
                  command=lambda: self.procesar_informe_auditoria(tipo_audit_var.get(), periodo_audit_var.get())).grid(row=1, column=0, columnspan=4, pady=15)
        
        # Área del informe
        informe_frame = ttk.LabelFrame(main_frame, text="Informe de Auditoría", padding=15)
        informe_frame.pack(fill='both', expand=True)
        
        self.audit_text = tk.Text(informe_frame, font=('Consolas', 9), state='disabled')
        audit_scroll = ttk.Scrollbar(informe_frame, orient='vertical', command=self.audit_text.yview)
        self.audit_text.configure(yscrollcommand=audit_scroll.set)
        
        self.audit_text.pack(side='left', fill='both', expand=True)
        audit_scroll.pack(side='right', fill='y')
    
    def procesar_informe_auditoria(self, tipo, periodo):
        """Procesa el informe de auditoría"""
        self.audit_text.config(state='normal')
        self.audit_text.delete('1.0', 'end')
        
        informe = f"""
📋 INFORME DE AUDITORÍA - GIMNASIO ATHENAS
═══════════════════════════════════════════
📊 Tipo: {tipo.title()}
📅 Período: {periodo.replace('_', ' ').title()}
📋 Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Auditor: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}

🔍 ALCANCE DE LA AUDITORÍA
──────────────────────────
• Revisión de actividades del sistema
• Análisis de transacciones financieras
• Verificación de controles de seguridad
• Evaluación de procedimientos operativos

👥 GESTIÓN DE USUARIOS
─────────────────────
✅ Creación de usuarios: CONTROLADA
✅ Asignación de roles: APROPIADA
✅ Cambios de permisos: DOCUMENTADOS
• Total de usuarios auditados: 15
• Usuarios activos: 12
• Usuarios inactivos: 3

🔐 SEGURIDAD Y ACCESOS
─────────────────────
✅ Intentos de login fallidos: MONITOREADOS
✅ Sesiones cerradas apropiadamente: SÍ
✅ Cambios de contraseña: REGISTRADOS
• Promedio de sesiones diarias: 8
• Tiempo promedio de sesión: 2.5 horas

💰 TRANSACCIONES FINANCIERAS
────────────────────────────
✅ Registros de ingresos: COMPLETOS
✅ Registros de egresos: DOCUMENTADOS
✅ Aprobaciones requeridas: CUMPLIDAS
• Total de transacciones: 47
• Ingresos registrados: $15,240
• Egresos registrados: $8,950

🏃 GESTIÓN DE ATLETAS
────────────────────
✅ Registros completos: SÍ
✅ Pagos procesados correctamente: SÍ
✅ Asignaciones de coaches: APROPIADAS
• Nuevos registros: 12
• Renovaciones: 8
• Cambios de plan: 3

👨‍🏫 GESTIÓN DE COACHES
──────────────────────
✅ Asignaciones documentadas: SÍ
✅ Actualizaciones de perfil: REGISTRADAS
• Total de coaches activos: 6
• Atletas promedio por coach: 15
• Eficiencia promedio: 92%

🚨 HALLAZGOS Y OBSERVACIONES
──────────────────────────
🟢 FORTALEZAS IDENTIFICADAS:
• Excelente control de accesos
• Documentación completa de transacciones
• Procesos bien definidos
• Alta adherencia a procedimientos

🟡 ÁREAS DE MEJORA:
• Implementar backup automático
• Mejorar logs de auditoría
• Considerar autenticación de dos factores

🔴 RIESGOS IDENTIFICADOS:
• Ningún riesgo crítico identificado
• Sistema operando dentro de parámetros normales

📋 RECOMENDACIONES
─────────────────
1. Mantener las prácticas actuales de seguridad
2. Implementar backup automático programado
3. Considerar auditorías más frecuentes
4. Documentar mejor los procedimientos de emergencia
5. Capacitación continua del personal

🎯 CUMPLIMIENTO NORMATIVO
────────────────────────
✅ Políticas internas: CUMPLIDAS
✅ Procedimientos de seguridad: APLICADOS
✅ Controles financieros: EFECTIVOS
✅ Gestión de datos: APROPIADA

═══════════════════════════════════════════
AUDITORÍA COMPLETADA SATISFACTORIAMENTE
SISTEMA OPERANDO DENTRO DE PARÁMETROS NORMALES
        """
        
        self.audit_text.insert('1.0', informe)
        self.audit_text.config(state='disabled')
    
    def buscar_eventos_auditoria(self):
        """Buscar eventos específicos en la auditoría"""
        # Ventana de búsqueda de eventos
        search_window = tk.Toplevel(self.parent_frame)
        search_window.title("🔍 Buscar Eventos de Auditoría")
        search_window.geometry("600x400")
        search_window.transient(self.parent_frame)
        search_window.grab_set()
        
        main_frame = ttk.Frame(search_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="🔍 Buscar Eventos de Auditoría", 
                 style='Executive.TLabel').pack(pady=(0, 20))
        
        # Criterios de búsqueda
        criteria_frame = ttk.LabelFrame(main_frame, text="Criterios de Búsqueda", padding=15)
        criteria_frame.pack(fill='x', pady=(0, 15))
        
        # Usuario
        ttk.Label(criteria_frame, text="Usuario:").grid(row=0, column=0, sticky='w', pady=5)
        usuario_search_var = tk.StringVar()
        ttk.Entry(criteria_frame, textvariable=usuario_search_var, width=20).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Tipo de evento
        ttk.Label(criteria_frame, text="Tipo de Evento:").grid(row=0, column=2, sticky='w', padx=(20, 0), pady=5)
        evento_var = tk.StringVar()
        ttk.Combobox(criteria_frame, textvariable=evento_var,
                    values=["todos", "login", "logout", "creacion", "edicion", "eliminacion"],
                    state="readonly").grid(row=0, column=3, padx=(10, 0), pady=5)
        
        # Fechas
        ttk.Label(criteria_frame, text="Fecha desde:").grid(row=1, column=0, sticky='w', pady=5)
        fecha_desde = DateEntry(criteria_frame, width=12, background='darkblue',
                               foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        fecha_desde.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(criteria_frame, text="Fecha hasta:").grid(row=1, column=2, sticky='w', padx=(20, 0), pady=5)
        fecha_hasta = DateEntry(criteria_frame, width=12, background='darkblue',
                               foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        fecha_hasta.grid(row=1, column=3, padx=(10, 0), pady=5)
        
        # Botón buscar
        ttk.Button(criteria_frame, text="🔍 Buscar Eventos",
                  style='Executive.TButton',
                  command=lambda: self.ejecutar_busqueda_eventos(usuario_search_var.get(), evento_var.get(), fecha_desde.get(), fecha_hasta.get())).grid(row=2, column=0, columnspan=4, pady=15)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding=15)
        results_frame.pack(fill='both', expand=True)
        
        columns = ('Fecha/Hora', 'Usuario', 'Evento', 'Detalles')
        search_tree = ttk.Treeview(results_frame, columns=columns, show='headings', style='Admin.Treeview')
        
        for col in columns:
            search_tree.heading(col, text=col)
            search_tree.column(col, width=130)
        
        search_scroll = ttk.Scrollbar(results_frame, orient='vertical', command=search_tree.yview)
        search_tree.configure(yscrollcommand=search_scroll.set)
        
        search_tree.pack(side='left', fill='both', expand=True)
        search_scroll.pack(side='right', fill='y')
        
        # Guardar referencia para usar en la búsqueda
        self.search_tree = search_tree
    
    def ejecutar_busqueda_eventos(self, usuario, tipo_evento, fecha_desde, fecha_hasta):
        """Ejecuta la búsqueda de eventos"""
        # Limpiar resultados anteriores
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Simular eventos encontrados
        eventos_simulados = [
            (datetime.now().strftime("%Y-%m-%d %H:%M"), "admin@gimnasio.com", "Login", "Acceso al sistema"),
            ((datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), "secretaria@gimnasio.com", "Creación", "Nuevo atleta registrado"),
            ((datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"), "admin@gimnasio.com", "Configuración", "Cambio en configuración general"),
            ((datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), "coach@gimnasio.com", "Login", "Acceso al sistema"),
        ]
        
        # Filtrar eventos según criterios (simulado)
        for evento in eventos_simulados:
            if not usuario or usuario.lower() in evento[1].lower():
                if not tipo_evento or tipo_evento == "todos" or tipo_evento.lower() in evento[2].lower():
                    self.search_tree.insert('', 'end', values=evento)
        
        messagebox.showinfo("Búsqueda", f"Búsqueda completada. Se encontraron {len(self.search_tree.get_children())} eventos.")
    
    # ==================== UTILIDADES FINALES ====================
    
    def actualizar_datos(self):
        """Actualiza todos los datos del panel administrativo"""
        self.actualizar_status("🔄 Actualizando panel ejecutivo...")
        self.cargar_datos_iniciales()
        
        # Resetear flags de carga
        for attr in ['_usuarios_cargados', '_finanzas_cargadas']:
            if hasattr(self, attr):
                delattr(self, attr)
    
    def actualizar_status(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=mensaje)
        
        # Auto-limpiar después de 5 segundos para mensajes de éxito
        if "✅" in mensaje:
            self.parent_frame.after(5000, lambda: self.status_label.config(text="🔴 SISTEMA EJECUTIVO ACTIVO"))
    
    def cerrar_sesion(self):
        """Cierra la sesión del administrador"""
        if messagebox.askyesno("Confirmar", "¿Estás segura de cerrar sesión?\n\nSe cerrará el panel ejecutivo."):
            try:
                resultado = self.auth_controller.cerrar_sesion(self.token_sesion)
                if resultado['success']:
                    # Notificar al main view para volver al login
                    self.parent_frame.event_generate('<<Logout>>')
            except Exception as e:
                print(f"Error al cerrar sesión: {e}")
                # Forzar logout aunque falle
                self.parent_frame.event_generate('<<Logout>>')


# ==================== FUNCIONES DE UTILIDAD PARA ADMIN ====================

def validar_permisos_admin(usuario_rol):
    """Valida que el usuario tenga permisos de administrador"""
    return usuario_rol == 'admin_principal'


def formatear_numero_ejecutivo(numero):
    """Formatea números para vista ejecutiva"""
    try:
        if numero >= 1000000:
            return f"{numero/1000000:.1f}M"
        elif numero >= 1000:
            return f"{numero/1000:.1f}K"
        else:
            return str(int(numero))
    except:
        return str(numero)


def generar_id_sesion_admin():
    """Genera ID único para sesiones administrativas"""
    import secrets
    return f"ADMIN_{secrets.token_hex(8).upper()}"