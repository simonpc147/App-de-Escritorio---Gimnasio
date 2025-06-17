# Vista de Coach - Dashboard para entrenadores
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import threading
from datetime import datetime, date, timedelta
from decimal import Decimal


class CoachView:
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
        self.coach_id = None
        
        # Configurar estilos específicos del coach
        self.configurar_estilos()
        
        # Obtener ID del coach actual
        self.obtener_coach_id()
        
        # Crear interfaz principal
        self.crear_interfaz()
        
        # Cargar datos iniciales
        self.cargar_datos_iniciales()
    
    def configurar_estilos(self):
        """Configura estilos específicos para la vista de coach"""
        self.style = ttk.Style()
        
        # Colores del tema coach (energético y motivacional)
        self.colores = {
            'primario': '#dc2626',        # Rojo energético
            'secundario': '#ea580c',      # Naranja vibrante
            'acento': '#f59e0b',          # Amarillo dorado
            'exito': '#16a34a',           # Verde activo
            'info': '#2563eb',            # Azul informativo
            'advertencia': '#ca8a04',     # Amarillo advertencia
            'error': '#dc2626',           # Rojo error
            'fondo': '#fef2f2',           # Fondo suave rojo
            'card': '#ffffff',            # Blanco puro
            'texto': '#1f2937',           # Texto oscuro
            'texto_claro': '#6b7280'      # Gris medio
        }
        
        # Estilo para cards de coach
        self.style.configure(
            'Coach.TFrame',
            background=self.colores['card'],
            relief='solid',
            borderwidth=2
        )
        
        # Estilo para headers de coach
        self.style.configure(
            'CoachHeader.TLabel',
            background=self.colores['card'],
            foreground=self.colores['primario'],
            font=('Segoe UI', 16, 'bold'),
            padding=(15, 15)
        )
        
        # Botones principales de coach
        self.style.configure(
            'CoachPrimary.TButton',
            background=self.colores['primario'],
            foreground='white',
            font=('Segoe UI', 11, 'bold'),
            padding=(15, 8)
        )
        
        # Botones de éxito para coach
        self.style.configure(
            'CoachSuccess.TButton',
            background=self.colores['exito'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(12, 7)
        )
        
        # Botones de acento para coach
        self.style.configure(
            'CoachAccent.TButton',
            background=self.colores['acento'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(12, 7)
        )
        
        # Treeviews de coach
        self.style.configure(
            'Coach.Treeview',
            font=('Segoe UI', 9),
            rowheight=26,
            background=self.colores['card']
        )
        
        self.style.configure(
            'Coach.Treeview.Heading',
            font=('Segoe UI', 10, 'bold'),
            background=self.colores['primario'],
            foreground='white'
        )
    
    def obtener_coach_id(self):
        """Obtiene el ID del coach actual"""
        try:
            # Buscar el coach correspondiente al usuario actual
            coaches_result = self.coach_controller.obtener_todos_coaches()
            if coaches_result['success']:
                for coach_info in coaches_result['coaches']:
                    usuario_data = coach_info['usuario_data']
                    if usuario_data[0] == self.usuario_actual['id']:  # ID de usuario
                        self.coach_id = coach_info['coach_data'][0]  # ID de coach
                        break
        except Exception as e:
            print(f"Error obteniendo coach ID: {e}")
    
    def crear_interfaz(self):
        """Crea la interfaz principal de coach"""
        # Frame principal con padding
        self.main_frame = ttk.Frame(self.parent_frame, padding=15)
        self.main_frame.pack(fill='both', expand=True)
        
        # Crear header de coach
        self.crear_header_coach()
        
        # Crear notebook principal
        self.crear_notebook_coach()
        
        # Crear status bar
        self.crear_status_bar_coach()
    
    def crear_header_coach(self):
        """Crea el header específico para coaches"""
        header_frame = ttk.Frame(self.main_frame, style='Coach.TFrame', padding=20)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Lado izquierdo - Información del coach
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        # Título principal
        title_label = ttk.Label(
            left_frame,
            text="💪 PANEL DE ENTRENADOR",
            font=('Segoe UI', 20, 'bold'),
            foreground=self.colores['primario']
        )
        title_label.pack(anchor='w')
        
        welcome_label = ttk.Label(
            left_frame,
            text=f"¡Hola Coach {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}!",
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colores['secundario']
        )
        welcome_label.pack(anchor='w', pady=(5, 0))
        
        # Información de turno
        turno_label = ttk.Label(
            left_frame,
            text=f"🕒 {datetime.now().strftime('%A, %d de %B %Y - %H:%M')}",
            font=('Segoe UI', 10),
            foreground=self.colores['texto_claro']
        )
        turno_label.pack(anchor='w', pady=(8, 0))
        
        # Lado derecho - Métricas rápidas del coach
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side='right')
        
        # Mini dashboard del coach
        self.crear_mini_dashboard_coach(right_frame)
    
    def crear_mini_dashboard_coach(self, parent):
        """Crea mini dashboard en el header"""
        mini_frame = ttk.Frame(parent)
        mini_frame.pack()
        
        # Grid de métricas
        metrics_frame = ttk.Frame(mini_frame)
        metrics_frame.pack(pady=(0, 15))
        
        # Métricas del coach
        self.mini_metrics = {}
        metrics_config = [
            ("mis_atletas", "🏃", "Mis Atletas", "0", self.colores['primario']),
            ("sesiones_hoy", "💪", "Sesiones Hoy", "0", self.colores['exito']),
            ("eficiencia", "📈", "Eficiencia", "0%", self.colores['acento'])
        ]
        
        for i, (key, icon, label, value, color) in enumerate(metrics_config):
            metric_card = self.crear_mini_metric_card(metrics_frame, icon, label, value, color)
            metric_card.grid(row=0, column=i, padx=8, pady=5)
            self.mini_metrics[key] = metric_card
        
        # Botones de acción
        buttons_frame = ttk.Frame(mini_frame)
        buttons_frame.pack()
        
        refresh_btn = ttk.Button(
            buttons_frame,
            text="🔄 Actualizar",
            command=self.actualizar_datos,
            style='CoachPrimary.TButton'
        )
        refresh_btn.pack(side='left', padx=(0, 10))
        
        profile_btn = ttk.Button(
            buttons_frame,
            text="👤 Mi Perfil",
            command=self.ver_mi_perfil,
            style='CoachAccent.TButton'
        )
        profile_btn.pack(side='left', padx=(0, 10))
        
        logout_btn = ttk.Button(
            buttons_frame,
            text="🚪 Cerrar Sesión",
            command=self.cerrar_sesion,
            style='CoachSuccess.TButton'
        )
        logout_btn.pack(side='right')
    
    def crear_mini_metric_card(self, parent, icon, label, value, color):
        """Crea una tarjeta de métrica mini"""
        card_frame = ttk.Frame(parent, style='Coach.TFrame', padding=12)
        
        # Layout vertical compacto
        icon_label = ttk.Label(
            card_frame,
            text=icon,
            font=('Segoe UI', 18),
            foreground=color
        )
        icon_label.pack()
        
        value_label = ttk.Label(
            card_frame,
            text=value,
            font=('Segoe UI', 14, 'bold'),
            foreground=color
        )
        value_label.pack()
        
        label_widget = ttk.Label(
            card_frame,
            text=label,
            font=('Segoe UI', 9),
            foreground=self.colores['texto_claro']
        )
        label_widget.pack()
        
        # Guardar referencia para actualizar
        card_frame.value_label = value_label
        
        return card_frame
    
    def crear_notebook_coach(self):
        """Crea el notebook con pestañas específicas para coaches"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 15))
        
        # Crear pestañas del coach
        self.crear_tab_mis_atletas()
        self.crear_tab_horarios()
        self.crear_tab_rendimiento()
        self.crear_tab_comunicacion()
        self.crear_tab_mi_perfil()
        
        # Bind para carga lazy
        self.notebook.bind('<<NotebookTabChanged>>', self.on_coach_tab_changed)
    
    def crear_tab_mis_atletas(self):
        """Crea la pestaña de gestión de atletas asignados"""
        atletas_frame = ttk.Frame(self.notebook)
        self.notebook.add(atletas_frame, text="🏃 Mis Atletas")
        
        # Panel de control
        control_frame = ttk.Frame(atletas_frame, padding=15)
        control_frame.pack(fill='x')
        
        # Botones de acción
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side='left')
        
        ttk.Button(
            btn_frame,
            text="👥 Ver Todos",
            style='CoachPrimary.TButton',
            command=self.cargar_mis_atletas
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="📊 Estadísticas",
            style='CoachAccent.TButton',
            command=self.ver_estadisticas_atletas
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="📝 Notas Rápidas",
            style='CoachSuccess.TButton',
            command=self.agregar_notas_rapidas
        ).pack(side='left')
        
        # Filtros
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Filtrar:").pack(side='left', padx=(0, 5))
        
        self.filtro_atletas_var = tk.StringVar(value="todos")
        filtro_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filtro_atletas_var,
            values=["todos", "activos", "nuevos", "veteranos"],
            state="readonly",
            width=12
        )
        filtro_combo.pack(side='left')
        filtro_combo.bind('<<ComboboxSelected>>', self.filtrar_mis_atletas)
        
        # Lista de atletas asignados
        self.crear_lista_mis_atletas(atletas_frame)
    
    def crear_lista_mis_atletas(self, parent):
        """Crea la lista de atletas asignados al coach"""
        list_frame = ttk.Frame(parent, padding=(15, 0, 15, 15))
        list_frame.pack(fill='both', expand=True)
        
        # Treeview para atletas
        columns = ('ID', 'Nombre', 'Email', 'Plan', 'Estado', 'Fecha Asignación', 'Progreso', 'Notas')
        self.mis_atletas_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            style='Coach.Treeview'
        )
        
        # Configurar columnas
        col_widths = {
            'ID': 50, 'Nombre': 150, 'Email': 180, 'Plan': 100,
            'Estado': 80, 'Fecha Asignación': 120, 'Progreso': 100, 'Notas': 200
        }
        
        for col in columns:
            self.mis_atletas_tree.heading(col, text=col)
            self.mis_atletas_tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.mis_atletas_tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.mis_atletas_tree.xview)
        self.mis_atletas_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.mis_atletas_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Menú contextual
        self.crear_menu_contextual_atletas()
        
        # Bind eventos
        self.mis_atletas_tree.bind('<Double-1>', self.ver_detalle_atleta)
    
    def crear_menu_contextual_atletas(self):
        """Crea menú contextual para atletas"""
        self.menu_atletas = tk.Menu(self.mis_atletas_tree, tearoff=0)
        self.menu_atletas.add_command(label="👤 Ver Perfil", command=self.ver_detalle_atleta)
        self.menu_atletas.add_command(label="📝 Agregar Nota", command=self.agregar_nota_atleta)
        self.menu_atletas.add_command(label="📊 Ver Progreso", command=self.ver_progreso_atleta)
        self.menu_atletas.add_separator()
        self.menu_atletas.add_command(label="🏋️ Asignar Rutina", command=self.asignar_rutina)
        self.menu_atletas.add_command(label="📅 Programar Sesión", command=self.programar_sesion)
        self.menu_atletas.add_separator()
        self.menu_atletas.add_command(label="📞 Contactar", command=self.contactar_atleta)
        
        # Bind del menú
        self.mis_atletas_tree.bind('<Button-3>', self.mostrar_menu_atletas)
    
    def crear_tab_horarios(self):
        """Crea la pestaña de gestión de horarios"""
        horarios_frame = ttk.Frame(self.notebook)
        self.notebook.add(horarios_frame, text="📅 Horarios")
        
        # Panel superior
        control_frame = ttk.Frame(horarios_frame, padding=15)
        control_frame.pack(fill='x')
        
        # Navegación de fechas
        date_frame = ttk.Frame(control_frame)
        date_frame.pack(side='left')
        
        ttk.Button(
            date_frame,
            text="◀ Anterior",
            command=self.dia_anterior
        ).pack(side='left', padx=(0, 10))
        
        self.fecha_actual_var = tk.StringVar(value=datetime.now().strftime("%A, %d de %B %Y"))
        fecha_label = ttk.Label(
            date_frame,
            textvariable=self.fecha_actual_var,
            font=('Segoe UI', 12, 'bold'),
            foreground=self.colores['primario']
        )
        fecha_label.pack(side='left', padx=(0, 10))
        
        ttk.Button(
            date_frame,
            text="Siguiente ▶",
            command=self.dia_siguiente
        ).pack(side='left')
        
        # Botones de acción
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side='right')
        
        ttk.Button(
            btn_frame,
            text="📅 Hoy",
            style='CoachPrimary.TButton',
            command=self.ir_a_hoy
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="➕ Nueva Sesión",
            style='CoachSuccess.TButton',
            command=self.nueva_sesion
        ).pack(side='left')
        
        # Calendario/Horarios del día
        self.crear_calendario_horarios(horarios_frame)
    
    def crear_calendario_horarios(self, parent):
        """Crea el calendario de horarios del coach"""
        calendar_frame = ttk.Frame(parent, padding=(15, 0, 15, 15))
        calendar_frame.pack(fill='both', expand=True)
        
        # Frame principal con dos columnas
        main_calendar_frame = ttk.Frame(calendar_frame)
        main_calendar_frame.pack(fill='both', expand=True)
        
        # Columna izquierda - Horarios del día
        left_frame = ttk.LabelFrame(main_calendar_frame, text="🕒 Horarios del Día", padding=15)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Lista de horarios
        self.horarios_tree = ttk.Treeview(
            left_frame,
            columns=('Hora', 'Atleta', 'Actividad', 'Estado'),
            show='headings',
            style='Coach.Treeview',
            height=15
        )
        
        for col in ['Hora', 'Atleta', 'Actividad', 'Estado']:
            self.horarios_tree.heading(col, text=col)
            self.horarios_tree.column(col, width=120)
        
        horarios_scroll = ttk.Scrollbar(left_frame, orient='vertical', command=self.horarios_tree.yview)
        self.horarios_tree.configure(yscrollcommand=horarios_scroll.set)
        
        self.horarios_tree.pack(side='left', fill='both', expand=True)
        horarios_scroll.pack(side='right', fill='y')
        
        # Columna derecha - Resumen y acciones rápidas
        right_frame = ttk.Frame(main_calendar_frame)
        right_frame.pack(side='right', fill='y')
        
        # Resumen del día
        self.crear_resumen_dia(right_frame)
        
        # Acciones rápidas
        self.crear_acciones_rapidas_horarios(right_frame)
    
    def crear_resumen_dia(self, parent):
        """Crea resumen del día"""
        resumen_frame = ttk.LabelFrame(parent, text="📊 Resumen del Día", padding=15)
        resumen_frame.pack(fill='x', pady=(0, 15))
        
        # Métricas del día
        self.resumen_widgets = {}
        
        resumen_data = [
            ("sesiones_programadas", "📅", "Sesiones Programadas", "0"),
            ("sesiones_completadas", "✅", "Completadas", "0"),
            ("atletas_atendidos", "👥", "Atletas Atendidos", "0"),
            ("horas_trabajadas", "🕒", "Horas de Trabajo", "0h")
        ]
        
        for i, (key, icon, label, value) in enumerate(resumen_data):
            metric_frame = ttk.Frame(resumen_frame)
            metric_frame.pack(fill='x', pady=5)
            
            ttk.Label(metric_frame, text=icon, font=('Segoe UI', 12)).pack(side='left')
            ttk.Label(metric_frame, text=label + ":", font=('Segoe UI', 9)).pack(side='left', padx=(5, 0))
            
            value_label = ttk.Label(metric_frame, text=value, font=('Segoe UI', 9, 'bold'), 
                                  foreground=self.colores['primario'])
            value_label.pack(side='right')
            
            self.resumen_widgets[key] = value_label
    
    def crear_acciones_rapidas_horarios(self, parent):
        """Crea acciones rápidas para horarios"""
        acciones_frame = ttk.LabelFrame(parent, text="⚡ Acciones Rápidas", padding=15)
        acciones_frame.pack(fill='x')
        
        acciones = [
            ("➕ Nueva Sesión", self.nueva_sesion),
            ("✏️ Editar Seleccionada", self.editar_sesion),
            ("✅ Marcar Completada", self.completar_sesion),
            ("❌ Cancelar Sesión", self.cancelar_sesion),
            ("📝 Agregar Notas", self.agregar_notas_sesion),
            ("📊 Ver Estadísticas", self.ver_estadisticas_horarios)
        ]
        
        for texto, comando in acciones:
            ttk.Button(
                acciones_frame,
                text=texto,
                command=comando,
                width=20
            ).pack(fill='x', pady=2)
    
    def crear_tab_rendimiento(self):
        """Crea la pestaña de análisis de rendimiento"""
        rendimiento_frame = ttk.Frame(self.notebook)
        self.notebook.add(rendimiento_frame, text="📈 Rendimiento")
        
        # Panel de control
        control_frame = ttk.Frame(rendimiento_frame, padding=15)
        control_frame.pack(fill='x')
        
        # Selector de período
        ttk.Label(control_frame, text="Período de análisis:").pack(side='left', padx=(0, 10))
        
        self.periodo_rendimiento_var = tk.StringVar(value="mes_actual")
        periodo_combo = ttk.Combobox(
            control_frame,
            textvariable=self.periodo_rendimiento_var,
            values=["ultima_semana", "mes_actual", "trimestre", "año_actual"],
            state="readonly",
            width=15
        )
        periodo_combo.pack(side='left', padx=(0, 20))
        periodo_combo.bind('<<ComboboxSelected>>', self.actualizar_rendimiento)
        
        ttk.Button(
            control_frame,
            text="📊 Generar Reporte",
            style='CoachPrimary.TButton',
            command=self.generar_reporte_rendimiento
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="📈 Ver Tendencias",
            style='CoachAccent.TButton',
            command=self.ver_tendencias_rendimiento
        ).pack(side='left')
        
        # Contenido del rendimiento
        self.crear_contenido_rendimiento(rendimiento_frame)
    
    def crear_contenido_rendimiento(self, parent):
        """Crea el contenido de análisis de rendimiento"""
        content_frame = ttk.Frame(parent, padding=(15, 0, 15, 15))
        content_frame.pack(fill='both', expand=True)
        
        # Notebook para diferentes análisis
        rendimiento_notebook = ttk.Notebook(content_frame)
        rendimiento_notebook.pack(fill='both', expand=True)
        
        # Pestaña de KPIs personales
        self.crear_kpis_personales(rendimiento_notebook)
        
        # Pestaña de evolución de atletas
        self.crear_evolucion_atletas(rendimiento_notebook)
        
        # Pestaña de comparativas
        self.crear_comparativas(rendimiento_notebook)
    
    def crear_kpis_personales(self, parent):
        """Crea KPIs personales del coach"""
        kpis_frame = ttk.Frame(parent)
        parent.add(kpis_frame, text="🎯 Mis KPIs")
        
        # Grid de KPIs
        kpis_grid_frame = ttk.Frame(kpis_frame, padding=20)
        kpis_grid_frame.pack(fill='x')
        
        # Configurar grid
        for i in range(3):
            kpis_grid_frame.columnconfigure(i, weight=1)
        
        # KPIs del coach
        self.kpis_personales = {}
        kpis_config = [
            ("atletas_asignados", "👥", "Atletas Asignados", "0", self.colores['primario']),
            ("sesiones_mes", "💪", "Sesiones Este Mes", "0", self.colores['exito']),
            ("eficiencia_general", "📈", "Eficiencia General", "0%", self.colores['acento']),
            ("satisfaccion_promedio", "⭐", "Satisfacción Promedio", "0/5", self.colores['secundario']),
            ("horas_mes", "🕒", "Horas Trabajadas", "0h", self.colores['info']),
            ("retension_atletas", "🎯", "Retención de Atletas", "0%", self.colores['exito'])
        ]
        
        for i, (key, icon, label, value, color) in enumerate(kpis_config):
            row = i // 3
            col = i % 3
            
            kpi_card = self.crear_kpi_card_coach(kpis_grid_frame, icon, label, value, color)
            kpi_card.grid(row=row, column=col, padx=15, pady=15, sticky='ew')
            self.kpis_personales[key] = kpi_card
        
        # Gráfico de evolución
        self.crear_grafico_evolucion_personal(kpis_frame)
    
    def crear_kpi_card_coach(self, parent, icon, label, value, color):
        """Crea una tarjeta KPI para coach"""
        card_frame = ttk.Frame(parent, style='Coach.TFrame', padding=20)
        
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
        value_label.pack(pady=(5, 0))
        
        # Label
        label_widget = ttk.Label(
            card_frame,
            text=label,
            font=('Segoe UI', 9),
            foreground=self.colores['texto_claro']
        )
        label_widget.pack()
        
        # Guardar referencia
        card_frame.value_label = value_label
        
        return card_frame
    
    def crear_grafico_evolucion_personal(self, parent):
        """Crea gráfico de evolución personal"""
        grafico_frame = ttk.LabelFrame(parent, text="📊 Mi Evolución", padding=15)
        grafico_frame.pack(fill='both', expand=True, padx=20, pady=(20, 0))
        
        # Placeholder para gráfico
        placeholder_label = ttk.Label(
            grafico_frame,
            text="📈 Gráfico de evolución personal\n🚧 Funcionalidad en desarrollo",
            font=('Segoe UI', 12),
            foreground=self.colores['texto_claro']
        )
        placeholder_label.pack(expand=True)
    
    def crear_evolucion_atletas(self, parent):
        """Crea pestaña de evolución de atletas"""
        evolucion_frame = ttk.Frame(parent)
        parent.add(evolucion_frame, text="📊 Evolución Atletas")
        
        # Selector de atleta
        selector_frame = ttk.Frame(evolucion_frame, padding=15)
        selector_frame.pack(fill='x')
        
        ttk.Label(selector_frame, text="Seleccionar Atleta:").pack(side='left', padx=(0, 10))
        
        self.atleta_evolucion_var = tk.StringVar()
        self.atleta_evolucion_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.atleta_evolucion_var,
            state="readonly",
            width=30
        )
        self.atleta_evolucion_combo.pack(side='left', padx=(0, 20))
        
        ttk.Button(
            selector_frame,
            text="📊 Ver Evolución",
            style='CoachPrimary.TButton',
            command=self.mostrar_evolucion_atleta
        ).pack(side='left')
        
        # Área de evolución
        evolucion_content = ttk.Frame(evolucion_frame, padding=15)
        evolucion_content.pack(fill='both', expand=True)
        
        placeholder = ttk.Label(
            evolucion_content,
            text="👥 Selecciona un atleta para ver su evolución\n📈 Aquí aparecerán gráficos de progreso",
            font=('Segoe UI', 12),
            foreground=self.colores['texto_claro']
        )
        placeholder.pack(expand=True)
    
    def crear_comparativas(self, parent):
        """Crea pestaña de comparativas"""
        comparativas_frame = ttk.Frame(parent)
        parent.add(comparativas_frame, text="⚖️ Comparativas")
        
        # Opciones de comparación
        options_frame = ttk.Frame(comparativas_frame, padding=15)
        options_frame.pack(fill='x')
        
        ttk.Label(options_frame, text="Tipo de Comparación:").pack(side='left', padx=(0, 10))
        
        self.tipo_comparacion_var = tk.StringVar(value="rendimiento_mensual")
        tipo_combo = ttk.Combobox(
            options_frame,
            textvariable=self.tipo_comparacion_var,
            values=["rendimiento_mensual", "atletas_vs_promedio", "mi_vs_otros_coaches"],
            state="readonly",
            width=20
        )
        tipo_combo.pack(side='left', padx=(0, 20))
        
        ttk.Button(
            options_frame,
            text="📊 Generar Comparativa",
            style='CoachPrimary.TButton',
            command=self.generar_comparativa
        ).pack(side='left')
        
        # Área de resultados
        resultados_frame = ttk.Frame(comparativas_frame, padding=15)
        resultados_frame.pack(fill='both', expand=True)
        
        placeholder = ttk.Label(
            resultados_frame,
            text="⚖️ Comparativas de rendimiento\n🚧 Funcionalidad en desarrollo",
            font=('Segoe UI', 12),
            foreground=self.colores['texto_claro']
        )
        placeholder.pack(expand=True)
    
    def crear_tab_comunicacion(self):
        """Crea la pestaña de comunicación con atletas"""
        comunicacion_frame = ttk.Frame(self.notebook)
        self.notebook.add(comunicacion_frame, text="💬 Comunicación")
        
        # Panel de control
        control_frame = ttk.Frame(comunicacion_frame, padding=15)
        control_frame.pack(fill='x')
        
        ttk.Button(
            control_frame,
            text="✉️ Nuevo Mensaje",
            style='CoachPrimary.TButton',
            command=self.nuevo_mensaje
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="📢 Anuncio Grupal",
            style='CoachAccent.TButton',
            command=self.nuevo_anuncio
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            control_frame,
            text="📋 Plantillas",
            style='CoachSuccess.TButton',
            command=self.ver_plantillas
        ).pack(side='left')
        
        # Contenido principal con dos paneles
        main_comunicacion = ttk.Frame(comunicacion_frame, padding=(15, 0, 15, 15))
        main_comunicacion.pack(fill='both', expand=True)
        
        # Panel izquierdo - Lista de conversaciones
        left_panel = ttk.LabelFrame(main_comunicacion, text="💬 Conversaciones", padding=15)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Lista de conversaciones
        self.conversaciones_tree = ttk.Treeview(
            left_panel,
            columns=('Atleta', 'Último Mensaje', 'Fecha'),
            show='headings',
            style='Coach.Treeview',
            height=20
        )
        
        for col in ['Atleta', 'Último Mensaje', 'Fecha']:
            self.conversaciones_tree.heading(col, text=col)
            self.conversaciones_tree.column(col, width=150)
        
        conv_scroll = ttk.Scrollbar(left_panel, orient='vertical', command=self.conversaciones_tree.yview)
        self.conversaciones_tree.configure(yscrollcommand=conv_scroll.set)
        
        self.conversaciones_tree.pack(side='left', fill='both', expand=True)
        conv_scroll.pack(side='right', fill='y')
        
        # Panel derecho - Acciones rápidas
        right_panel = ttk.Frame(main_comunicacion)
        right_panel.pack(side='right', fill='y')
        
        # Plantillas rápidas
        self.crear_plantillas_rapidas(right_panel)
        
        # Recordatorios
        self.crear_recordatorios_comunicacion(right_panel)
    
    def crear_plantillas_rapidas(self, parent):
        """Crea plantillas de mensajes rápidos"""
        plantillas_frame = ttk.LabelFrame(parent, text="📝 Plantillas Rápidas", padding=15)
        plantillas_frame.pack(fill='x', pady=(0, 15))
        
        plantillas = [
            ("👏 Felicitación", "¡Excelente trabajo en el entrenamiento de hoy! Sigue así."),
            ("💪 Motivación", "Recuerda que cada día es una oportunidad para mejorar."),
            ("📅 Recordatorio", "No olvides tu sesión de entrenamiento mañana."),
            ("🎯 Meta", "Estás muy cerca de alcanzar tu objetivo. ¡No te rindas!"),
            ("📋 Rutina", "He actualizado tu rutina de entrenamiento.")
        ]
        
        for titulo, mensaje in plantillas:
            btn = ttk.Button(
                plantillas_frame,
                text=titulo,
                command=lambda m=mensaje: self.usar_plantilla(m),
                width=25
            )
            btn.pack(fill='x', pady=2)
    
    def crear_recordatorios_comunicacion(self, parent):
        """Crea recordatorios de comunicación"""
        recordatorios_frame = ttk.LabelFrame(parent, text="🔔 Recordatorios", padding=15)
        recordatorios_frame.pack(fill='x')
        
        # Lista de recordatorios
        recordatorios_data = [
            "📞 Llamar a Juan sobre su progreso",
            "✉️ Enviar rutina nueva a María", 
            "📅 Confirmar cita con Pedro",
            "🎯 Revisar metas con Ana"
        ]
        
        for recordatorio in recordatorios_data:
            recordatorio_frame = ttk.Frame(recordatorios_frame)
            recordatorio_frame.pack(fill='x', pady=2)
            
            ttk.Label(recordatorio_frame, text=recordatorio, font=('Segoe UI', 9)).pack(side='left')
            ttk.Button(recordatorio_frame, text="✓", width=3).pack(side='right')
    
    def crear_tab_mi_perfil(self):
        """Crea la pestaña de perfil personal del coach"""
        perfil_frame = ttk.Frame(self.notebook)
        self.notebook.add(perfil_frame, text="👤 Mi Perfil")
        
        # Crear scrollable frame
        canvas = tk.Canvas(perfil_frame)
        scrollbar = ttk.Scrollbar(perfil_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Información personal
        self.crear_info_personal_coach(scrollable_frame)
        
        # Especialidades y horarios
        self.crear_especialidades_horarios(scrollable_frame)
        
        # Estadísticas personales
        self.crear_estadisticas_personales(scrollable_frame)
    
    def crear_info_personal_coach(self, parent):
        """Crea sección de información personal"""
        info_frame = ttk.LabelFrame(parent, text="📋 Información Personal", padding=20)
        info_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        # Grid para la información
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill='x')
        
        # Datos del coach (simulados por ahora)
        datos_coach = [
            ("Nombre Completo:", f"{self.usuario_actual['nombre']} {self.usuario_actual['apellido']}"),
            ("Email:", self.usuario_actual['email']),
            ("Rol:", "Entrenador Personal"),
            ("Fecha de Contratación:", "2024-01-15"),
            ("Especialidades:", "Fitness, Musculación, Cardio"),
            ("Horario Disponible:", "Lunes a Viernes 6:00-22:00")
        ]
        
        for i, (label, value) in enumerate(datos_coach):
            ttk.Label(info_grid, text=label, font=('Segoe UI', 10, 'bold')).grid(
                row=i, column=0, sticky='w', pady=5, padx=(0, 20)
            )
            ttk.Label(info_grid, text=value, font=('Segoe UI', 10)).grid(
                row=i, column=1, sticky='w', pady=5
            )
        
        # Botón editar
        ttk.Button(
            info_frame,
            text="✏️ Editar Perfil",
            style='CoachPrimary.TButton',
            command=self.editar_perfil
        ).pack(pady=(20, 0))
    
    def crear_especialidades_horarios(self, parent):
        """Crea sección de especialidades y horarios"""
        esp_frame = ttk.LabelFrame(parent, text="🎯 Especialidades y Disponibilidad", padding=20)
        esp_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        # Notebook para organizar
        esp_notebook = ttk.Notebook(esp_frame)
        esp_notebook.pack(fill='both', expand=True)
        
        # Especialidades
        especialidades_frame = ttk.Frame(esp_notebook)
        esp_notebook.add(especialidades_frame, text="🏋️ Especialidades")
        
        especialidades_text = tk.Text(especialidades_frame, height=8, width=50)
        especialidades_text.pack(fill='both', expand=True, pady=10)
        especialidades_text.insert('1.0', "• Entrenamiento de fuerza\n• Acondicionamiento físico\n• Rehabilitación\n• Entrenamiento funcional")
        
        # Horarios
        horarios_frame = ttk.Frame(esp_notebook)
        esp_notebook.add(horarios_frame, text="📅 Horarios")
        
        horarios_text = tk.Text(horarios_frame, height=8, width=50)
        horarios_text.pack(fill='both', expand=True, pady=10)
        horarios_text.insert('1.0', "Lunes a Viernes: 6:00 AM - 10:00 PM\nSábados: 8:00 AM - 6:00 PM\nDomingos: Descanso")
    
    def crear_estadisticas_personales(self, parent):
        """Crea estadísticas personales del coach"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Mis Estadísticas", padding=20)
        stats_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        # Grid de estadísticas
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        for i in range(2):
            stats_grid.columnconfigure(i, weight=1)
        
        # Estadísticas simuladas
        estadisticas = [
            ("📅 Días Trabajados:", "180 días"),
            ("👥 Total Atletas:", "25 atletas"),
            ("💪 Sesiones Impartidas:", "450 sesiones"),
            ("⭐ Valoración Promedio:", "4.8/5.0"),
            ("🎯 Objetivos Alcanzados:", "85%"),
            ("📈 Eficiencia:", "92%")
        ]
        
        for i, (label, value) in enumerate(estadisticas):
            row = i // 2
            col = i % 2
            
            stat_card = ttk.Frame(stats_grid, style='Coach.TFrame', padding=15)
            stat_card.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            
            ttk.Label(stat_card, text=label, font=('Segoe UI', 10, 'bold')).pack()
            ttk.Label(stat_card, text=value, font=('Segoe UI', 14, 'bold'), 
                     foreground=self.colores['primario']).pack(pady=(5, 0))
    
    def crear_status_bar_coach(self):
        """Crea la barra de estado para coach"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill='x', pady=(10, 0))
        
        # Separador
        ttk.Separator(self.status_frame, orient='horizontal').pack(fill='x', pady=(0, 8))
        
        # Status izquierdo
        self.status_label = ttk.Label(
            self.status_frame,
            text="💪 Panel de Entrenador Activo",
            font=('Segoe UI', 10, 'bold'),
            foreground=self.colores['primario']
        )
        self.status_label.pack(side='left')
        
        # Status derecho
        self.connection_label = ttk.Label(
            self.status_frame,
            text="🔗 Conectado | 🏃 Listo para entrenar",
            font=('Segoe UI', 9),
            foreground=self.colores['exito']
        )
        self.connection_label.pack(side='right')
    
    # ==================== CARGA DE DATOS ====================
    
    def cargar_datos_iniciales(self):
        """Carga datos iniciales del coach"""
        self.actualizar_status("🔄 Cargando datos del coach...")
        threading.Thread(target=self._cargar_datos_coach_background, daemon=True).start()
    
    def _cargar_datos_coach_background(self):
        """Carga datos en background"""
        try:
            # Cargar métricas del mini dashboard
            self.parent_frame.after(0, self.cargar_mini_metricas_coach)
            
            # Cargar atletas asignados
            self.parent_frame.after(100, self.cargar_mis_atletas)
            
            # Cargar horarios del día
            self.parent_frame.after(200, self.cargar_horarios_dia)
            
            # Status final
            self.parent_frame.after(500, lambda: self.actualizar_status("✅ Panel de coach listo"))
            
        except Exception as e:
            self.parent_frame.after(0, lambda: self.actualizar_status(f"❌ Error: {str(e)}"))
    
    def cargar_mini_metricas_coach(self):
        """Carga métricas del mini dashboard"""
        try:
            if self.coach_id:
                # Obtener atletas asignados
                atletas_result = self.coach_controller.obtener_atletas_por_coach(self.coach_id)
                if atletas_result['success']:
                    num_atletas = len(atletas_result['atletas'])
                    self.mini_metrics['mis_atletas']['value_label'].config(text=str(num_atletas))
                
                # Simular otras métricas
                self.mini_metrics['sesiones_hoy']['value_label'].config(text="3")
                self.mini_metrics['eficiencia']['value_label'].config(text="94%")
        except Exception as e:
            print(f"Error cargando métricas coach: {e}")
    
    def cargar_mis_atletas(self):
        """Carga lista de atletas asignados"""
        try:
            if not self.coach_id:
                return
            
            self.actualizar_status("🔄 Cargando mis atletas...")
            
            # Limpiar lista actual
            for item in self.mis_atletas_tree.get_children():
                self.mis_atletas_tree.delete(item)
            
            # Obtener atletas asignados al coach
            resultado = self.coach_controller.obtener_atletas_por_coach(self.coach_id)
            if resultado['success']:
                for atleta_info in resultado['atletas']:
                    atleta_data = atleta_info['atleta_data']
                    usuario_data = atleta_info['usuario_data']
                    asignacion_data = atleta_info['asignacion_data']
                    
                    values = (
                        atleta_data[0],  # ID
                        f"{usuario_data[1]} {usuario_data[2]}",  # Nombre
                        usuario_data[6],  # Email
                        "Plan Básico",  # Plan (placeholder)
                        "Activo",  # Estado
                        asignacion_data[3],  # Fecha asignación
                        "En progreso",  # Progreso
                        asignacion_data[6] or "Sin notas"  # Notas
                    )
                    
                    self.mis_atletas_tree.insert('', 'end', values=values)
                
                self.actualizar_status(f"✅ {len(resultado['atletas'])} atletas cargados")
            else:
                self.actualizar_status("ℹ️ No tienes atletas asignados")
                
        except Exception as e:
            self.actualizar_status(f"❌ Error cargando atletas: {str(e)}")
    
    def cargar_horarios_dia(self):
        """Carga horarios del día actual"""
        try:
            # Limpiar horarios actuales
            for item in self.horarios_tree.get_children():
                self.horarios_tree.delete(item)
            
            # Horarios simulados
            horarios_simulados = [
                ("08:00", "Juan Pérez", "Entrenamiento Personal", "Programada"),
                ("10:00", "María López", "Evaluación Física", "Completada"),
                ("14:00", "Carlos Ruiz", "Rutina de Fuerza", "Programada"),
                ("16:00", "Ana García", "Cardio + Tonificación", "Programada"),
                ("18:00", "Pedro Martín", "Rehabilitación", "Programada")
            ]
            
            for horario in horarios_simulados:
                self.horarios_tree.insert('', 'end', values=horario)
            
            # Actualizar resumen del día
            self.resumen_widgets['sesiones_programadas'].config(text="5")
            self.resumen_widgets['sesiones_completadas'].config(text="1")
            self.resumen_widgets['atletas_atendidos'].config(text="1")
            self.resumen_widgets['horas_trabajadas'].config(text="8h")
            
        except Exception as e:
            print(f"Error cargando horarios: {e}")
    
    # ==================== EVENTOS Y CALLBACKS ====================
    
    def on_coach_tab_changed(self, event):
        """Maneja cambio de pestañas del coach"""
        selected_tab = event.widget.tab('current')['text']
        
        if "🏃 Mis Atletas" in selected_tab and not hasattr(self, '_atletas_cargados'):
            self.cargar_mis_atletas()
            self._atletas_cargados = True
        elif "📅 Horarios" in selected_tab and not hasattr(self, '_horarios_cargados'):
            self.cargar_horarios_dia()
            self._horarios_cargados = True
    
    def filtrar_mis_atletas(self, event=None):
        """Filtra atletas por criterio"""
        filtro = self.filtro_atletas_var.get()
        self.actualizar_status(f"🔍 Filtrando atletas: {filtro}")
    
    def mostrar_menu_atletas(self, event):
        """Muestra menú contextual de atletas"""
        selection = self.mis_atletas_tree.selection()
        if selection:
            self.menu_atletas.post(event.x_root, event.y_root)
    
    # ==================== MÉTODOS DE ACCIÓN ====================
    
    def ver_detalle_atleta(self, event=None):
        """Ver detalles del atleta seleccionado"""
        selection = self.mis_atletas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un atleta")
            return
        
        item = self.mis_atletas_tree.item(selection[0])
        atleta_nombre = item['values'][1]
        
        messagebox.showinfo("Perfil de Atleta", f"👤 Perfil detallado de {atleta_nombre}\n🚧 En desarrollo")
    
    def agregar_nota_atleta(self):
        """Agregar nota al atleta seleccionado"""
        selection = self.mis_atletas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un atleta")
            return
        
        # Ventana de nota
        nota_window = tk.Toplevel(self.parent_frame)
        nota_window.title("📝 Agregar Nota")
        nota_window.geometry("400x300")
        nota_window.transient(self.parent_frame)
        nota_window.grab_set()
        
        main_frame = ttk.Frame(nota_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="📝 Nueva Nota", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 15))
        
        ttk.Label(main_frame, text="Nota:").pack(anchor='w')
        nota_text = tk.Text(main_frame, height=8, width=40)
        nota_text.pack(fill='both', expand=True, pady=(5, 15))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="❌ Cancelar", command=nota_window.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(btn_frame, text="✅ Guardar", style='CoachSuccess.TButton').pack(side='right')
    
    def ver_progreso_atleta(self):
        """Ver progreso del atleta"""
        messagebox.showinfo("Información", "📊 Progreso del atleta\n🚧 En desarrollo")
    
    def asignar_rutina(self):
        """Asignar rutina al atleta"""
        messagebox.showinfo("Información", "🏋️ Asignación de rutina\n🚧 En desarrollo")
    
    def programar_sesion(self):
        """Programar nueva sesión"""
        messagebox.showinfo("Información", "📅 Programar sesión\n🚧 En desarrollo")
    
    def contactar_atleta(self):
        """Contactar atleta"""
        messagebox.showinfo("Información", "📞 Contactar atleta\n🚧 En desarrollo")
    
    def ver_estadisticas_atletas(self):
        """Ver estadísticas de atletas"""
        messagebox.showinfo("Información", "📊 Estadísticas de atletas\n🚧 En desarrollo")
    
    def agregar_notas_rapidas(self):
        """Agregar notas rápidas"""
        messagebox.showinfo("Información", "📝 Notas rápidas\n🚧 En desarrollo")
    
    # ==================== MÉTODOS DE HORARIOS ====================
    
    def dia_anterior(self):
        """Navegar al día anterior"""
        self.actualizar_status("◀ Cargando día anterior...")
    
    def dia_siguiente(self):
        """Navegar al día siguiente"""
        self.actualizar_status("▶ Cargando día siguiente...")
    
    def ir_a_hoy(self):
        """Ir al día actual"""
        self.fecha_actual_var.set(datetime.now().strftime("%A, %d de %B %Y"))
        self.cargar_horarios_dia()
    
    def nueva_sesion(self):
        """Crear nueva sesión"""
        messagebox.showinfo("Información", "➕ Nueva sesión\n🚧 En desarrollo")
    
    def editar_sesion(self):
        """Editar sesión seleccionada"""
        messagebox.showinfo("Información", "✏️ Editar sesión\n🚧 En desarrollo")
    
    def completar_sesion(self):
        """Marcar sesión como completada"""
        messagebox.showinfo("Información", "✅ Sesión completada\n🚧 En desarrollo")
    
    def cancelar_sesion(self):
        """Cancelar sesión"""
        messagebox.showinfo("Información", "❌ Cancelar sesión\n🚧 En desarrollo")
    
    def agregar_notas_sesion(self):
        """Agregar notas a sesión"""
        messagebox.showinfo("Información", "📝 Notas de sesión\n🚧 En desarrollo")
    
    def ver_estadisticas_horarios(self):
        """Ver estadísticas de horarios"""
        messagebox.showinfo("Información", "📊 Estadísticas de horarios\n🚧 En desarrollo")
    
    # ==================== MÉTODOS DE RENDIMIENTO ====================
    
    def actualizar_rendimiento(self, event=None):
        """Actualizar análisis de rendimiento"""
        periodo = self.periodo_rendimiento_var.get()
        self.actualizar_status(f"📈 Actualizando rendimiento: {periodo}")
    
    def generar_reporte_rendimiento(self):
        """Generar reporte de rendimiento"""
        messagebox.showinfo("Información", "📊 Reporte de rendimiento\n🚧 En desarrollo")
    
    def ver_tendencias_rendimiento(self):
        """Ver tendencias de rendimiento"""
        messagebox.showinfo("Información", "📈 Tendencias de rendimiento\n🚧 En desarrollo")
    
    def mostrar_evolucion_atleta(self):
        """Mostrar evolución del atleta seleccionado"""
        messagebox.showinfo("Información", "📊 Evolución del atleta\n🚧 En desarrollo")
    
    def generar_comparativa(self):
        """Generar comparativa"""
        messagebox.showinfo("Información", "⚖️ Comparativa\n🚧 En desarrollo")
    
    # ==================== MÉTODOS DE COMUNICACIÓN ====================
    
    def nuevo_mensaje(self):
        """Crear nuevo mensaje"""
        messagebox.showinfo("Información", "✉️ Nuevo mensaje\n🚧 En desarrollo")
    
    def nuevo_anuncio(self):
        """Crear nuevo anuncio grupal"""
        messagebox.showinfo("Información", "📢 Nuevo anuncio\n🚧 En desarrollo")
    
    def ver_plantillas(self):
        """Ver plantillas de mensajes"""
        messagebox.showinfo("Información", "📋 Plantillas\n🚧 En desarrollo")
    
    def usar_plantilla(self, mensaje):
        """Usar plantilla de mensaje"""
        messagebox.showinfo("Plantilla", f"📝 Mensaje: {mensaje}\n🚧 En desarrollo")
    
    # ==================== MÉTODOS DE PERFIL ====================
    
    def ver_mi_perfil(self):
        """Ver perfil personal"""
        self.notebook.select(4)  # Seleccionar pestaña "Mi Perfil"
    
    def editar_perfil(self):
        """Editar perfil personal del coach"""
        # Ventana de edición de perfil
        perfil_window = tk.Toplevel(self.parent_frame)
        perfil_window.title("✏️ Editar Mi Perfil")
        perfil_window.geometry("600x500")
        perfil_window.transient(self.parent_frame)
        perfil_window.grab_set()
        
        # Centrar ventana
        x = (perfil_window.winfo_screenwidth() // 2) - 300
        y = (perfil_window.winfo_screenheight() // 2) - 250
        perfil_window.geometry(f"600x500+{x}+{y}")
        
        main_frame = ttk.Frame(perfil_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="✏️ Editar Mi Perfil de Coach", 
                 font=('Segoe UI', 16, 'bold'),
                 foreground=self.colores['primario']).pack(pady=(0, 20))
        
        # Notebook para organizar campos
        edit_notebook = ttk.Notebook(main_frame)
        edit_notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # Pestaña de datos personales
        personal_frame = ttk.Frame(edit_notebook, padding=15)
        edit_notebook.add(personal_frame, text="👤 Datos Personales")
        
        # Variables para los campos
        self.edit_vars = {
            'telefono': tk.StringVar(),
            'direccion': tk.StringVar(),
            'especialidades': tk.StringVar(),
            'horario_disponible': tk.StringVar()
        }
        
        # Campos editables
        ttk.Label(personal_frame, text="Teléfono:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(personal_frame, textvariable=self.edit_vars['telefono'], width=30).grid(
            row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(personal_frame, text="Dirección:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(personal_frame, textvariable=self.edit_vars['direccion'], width=30).grid(
            row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        personal_frame.columnconfigure(1, weight=1)
        
        # Pestaña profesional
        prof_frame = ttk.Frame(edit_notebook, padding=15)
        edit_notebook.add(prof_frame, text="🎯 Información Profesional")
        
        ttk.Label(prof_frame, text="Especialidades:").grid(row=0, column=0, sticky='nw', pady=5)
        esp_text = tk.Text(prof_frame, height=4, width=40)
        esp_text.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        esp_text.insert('1.0', "Entrenamiento de fuerza\nAcondicionamiento físico\nRehabilitación")
        
        ttk.Label(prof_frame, text="Horario Disponible:").grid(row=1, column=0, sticky='nw', pady=5)
        horario_text = tk.Text(prof_frame, height=4, width=40)
        horario_text.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        horario_text.insert('1.0', "Lunes a Viernes: 6:00-22:00\nSábados: 8:00-18:00")
        
        prof_frame.columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="❌ Cancelar", command=perfil_window.destroy).pack(side='right', padx=(10, 0))
        
        def guardar_perfil():
            # Aquí iría la lógica para guardar el perfil
            messagebox.showinfo("Éxito", "✅ Perfil actualizado correctamente")
            perfil_window.destroy()
        
        ttk.Button(btn_frame, text="✅ Guardar Cambios", 
                  style='CoachSuccess.TButton', command=guardar_perfil).pack(side='right')
    
    # ==================== UTILIDADES FINALES ====================
    
    def actualizar_datos(self):
        """Actualiza todos los datos del panel de coach"""
        self.actualizar_status("🔄 Actualizando datos del coach...")
        self.cargar_datos_iniciales()
        
        # Resetear flags de carga
        for attr in ['_atletas_cargados', '_horarios_cargados']:
            if hasattr(self, attr):
                delattr(self, attr)
    
    def actualizar_status(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=mensaje)
        
        # Auto-limpiar después de 5 segundos para mensajes de éxito
        if "✅" in mensaje:
            self.parent_frame.after(5000, lambda: self.status_label.config(text="💪 Panel de Entrenador Activo"))
    
    def cerrar_sesion(self):
        """Cierra la sesión del coach"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de cerrar sesión?\n\nTu turno se marcará como finalizado."):
            try:
                resultado = self.auth_controller.cerrar_sesion(self.token_sesion)
                if resultado['success']:
                    # Notificar al main view para volver al login
                    self.parent_frame.event_generate('<<Logout>>')
            except Exception as e:
                print(f"Error al cerrar sesión: {e}")
                # Forzar logout aunque falle
                self.parent_frame.event_generate('<<Logout>>')
    
    # ==================== MÉTODOS DE REPORTE ESPECÍFICOS ====================
    
    def generar_reporte_semanal(self):
        """Genera reporte semanal del coach"""
        # Ventana de reporte semanal
        reporte_window = tk.Toplevel(self.parent_frame)
        reporte_window.title("📊 Reporte Semanal")
        reporte_window.geometry("800x600")
        reporte_window.transient(self.parent_frame)
        
        main_frame = ttk.Frame(reporte_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="📊 Mi Reporte Semanal", 
                 font=('Segoe UI', 16, 'bold'),
                 foreground=self.colores['primario']).pack(pady=(0, 20))
        
        # Área de reporte
        reporte_frame = ttk.LabelFrame(main_frame, text="Resumen de la Semana", padding=15)
        reporte_frame.pack(fill='both', expand=True)
        
        reporte_text = tk.Text(reporte_frame, font=('Consolas', 10), state='disabled')
        reporte_scroll = ttk.Scrollbar(reporte_frame, orient='vertical', command=reporte_text.yview)
        reporte_text.configure(yscrollcommand=reporte_scroll.set)
        
        # Generar contenido del reporte
        reporte_content = f"""
💪 REPORTE SEMANAL DE ENTRENADOR
═══════════════════════════════════
👤 Coach: {self.usuario_actual['nombre']} {self.usuario_actual['apellido']}
📅 Semana del: {(datetime.now() - timedelta(days=7)).strftime('%d/%m/%Y')} al {datetime.now().strftime('%d/%m/%Y')}

📊 RESUMEN DE ACTIVIDADES
────────────────────────
• Sesiones Programadas: 25
• Sesiones Completadas: 23
• Sesiones Canceladas: 2
• Atletas Atendidos: 18
• Horas Trabajadas: 35h

👥 ATLETAS MÁS ACTIVOS
──────────────────────
1. Juan Pérez - 4 sesiones
2. María López - 3 sesiones  
3. Carlos Ruiz - 3 sesiones
4. Ana García - 2 sesiones
5. Pedro Martín - 2 sesiones

🎯 OBJETIVOS ALCANZADOS
───────────────────────
• Completar 20+ sesiones: ✅ LOGRADO (23)
• Mantener satisfacción >4.5: ✅ LOGRADO (4.8)
• Retener atletas activos: ✅ LOGRADO (95%)

📈 MÉTRICAS DE RENDIMIENTO
──────────────────────────
• Puntualidad: 98%
• Satisfacción Promedio: 4.8/5.0
• Tasa de Completado: 92%
• Eficiencia General: 94%

💡 OBSERVACIONES
────────────────
• Excelente semana en términos de rendimiento
• Alta satisfacción de los atletas
• Dos cancelaciones por motivos personales de atletas
• Mantener este nivel de calidad

🎯 OBJETIVOS PRÓXIMA SEMANA
───────────────────────────
• Programar 26 sesiones
• Implementar nueva rutina para 3 atletas
• Completar evaluaciones mensuales pendientes
• Realizar seguimiento de objetivos individuales

════════════════════════════════════
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        reporte_text.config(state='normal')
        reporte_text.insert('1.0', reporte_content)
        reporte_text.config(state='disabled')
        
        reporte_text.pack(side='left', fill='both', expand=True)
        reporte_scroll.pack(side='right', fill='y')
        
        # Botón para exportar
        ttk.Button(main_frame, text="📄 Exportar Reporte", 
                  style='CoachPrimary.TButton',
                  command=lambda: messagebox.showinfo("Exportar", "📄 Funcionalidad de exportación en desarrollo")).pack(pady=10)
    
    def programar_evaluacion_atleta(self):
        """Programar evaluación para un atleta"""
        # Ventana de programación
        eval_window = tk.Toplevel(self.parent_frame)
        eval_window.title("📋 Programar Evaluación")
        eval_window.geometry("500x400")
        eval_window.transient(self.parent_frame)
        eval_window.grab_set()
        
        main_frame = ttk.Frame(eval_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="📋 Programar Evaluación", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Seleccionar atleta
        ttk.Label(form_frame, text="Atleta:").grid(row=0, column=0, sticky='w', pady=5)
        atleta_combo = ttk.Combobox(form_frame, state="readonly", width=25)
        atleta_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Tipo de evaluación
        ttk.Label(form_frame, text="Tipo de Evaluación:").grid(row=1, column=0, sticky='w', pady=5)
        tipo_combo = ttk.Combobox(form_frame, 
                                 values=["Evaluación Inicial", "Seguimiento Mensual", "Evaluación Final"],
                                 state="readonly", width=25)
        tipo_combo.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # Fecha
        ttk.Label(form_frame, text="Fecha:").grid(row=2, column=0, sticky='w', pady=5)
        fecha_eval = DateEntry(form_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        fecha_eval.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Hora
        ttk.Label(form_frame, text="Hora:").grid(row=3, column=0, sticky='w', pady=5)
        hora_combo = ttk.Combobox(form_frame, 
                                 values=["08:00", "10:00", "14:00", "16:00", "18:00"],
                                 state="readonly", width=10)
        hora_combo.grid(row=3, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Notas
        ttk.Label(form_frame, text="Notas:").grid(row=4, column=0, sticky='nw', pady=5)
        notas_text = tk.Text(form_frame, height=4, width=30)
        notas_text.grid(row=4, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="❌ Cancelar", command=eval_window.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(btn_frame, text="✅ Programar", style='CoachSuccess.TButton').pack(side='right')
    
    def crear_rutina_personalizada(self):
        """Crear rutina personalizada para un atleta"""
        # Ventana de creación de rutina
        rutina_window = tk.Toplevel(self.parent_frame)
        rutina_window.title("🏋️ Crear Rutina Personalizada")
        rutina_window.geometry("700x600")
        rutina_window.transient(self.parent_frame)
        
        main_frame = ttk.Frame(rutina_window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="🏋️ Crear Rutina Personalizada", 
                 font=('Segoe UI', 16, 'bold'),
                 foreground=self.colores['primario']).pack(pady=(0, 20))
        
        # Notebook para organizar la rutina
        rutina_notebook = ttk.Notebook(main_frame)
        rutina_notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # Información general
        info_frame = ttk.Frame(rutina_notebook, padding=15)
        rutina_notebook.add(info_frame, text="📋 Información General")
        
        # Campos básicos
        ttk.Label(info_frame, text="Nombre de la Rutina:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(info_frame, width=40).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(info_frame, text="Atleta:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Combobox(info_frame, state="readonly", width=37).grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(info_frame, text="Objetivo:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Combobox(info_frame, 
                    values=["Pérdida de peso", "Ganancia muscular", "Resistencia", "Rehabilitación"],
                    state="readonly", width=37).grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        info_frame.columnconfigure(1, weight=1)
        
        # Ejercicios
        ejercicios_frame = ttk.Frame(rutina_notebook, padding=15)
        rutina_notebook.add(ejercicios_frame, text="💪 Ejercicios")
        
        ttk.Label(ejercicios_frame, text="Lista de Ejercicios:", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Treeview para ejercicios
        ejercicios_tree = ttk.Treeview(ejercicios_frame, 
                                      columns=('Ejercicio', 'Series', 'Repeticiones', 'Peso'),
                                      show='headings', height=10)
        
        for col in ['Ejercicio', 'Series', 'Repeticiones', 'Peso']:
            ejercicios_tree.heading(col, text=col)
            ejercicios_tree.column(col, width=120)
        
        ejercicios_tree.pack(fill='both', expand=True, pady=(0, 10))
        
        # Botones de ejercicios
        ej_btn_frame = ttk.Frame(ejercicios_frame)
        ej_btn_frame.pack(fill='x')
        
        ttk.Button(ej_btn_frame, text="➕ Agregar Ejercicio").pack(side='left', padx=(0, 10))
        ttk.Button(ej_btn_frame, text="✏️ Editar").pack(side='left', padx=(0, 10))
        ttk.Button(ej_btn_frame, text="🗑️ Eliminar").pack(side='left')
        
        # Botones principales
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="❌ Cancelar", command=rutina_window.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(btn_frame, text="✅ Guardar Rutina", style='CoachSuccess.TButton').pack(side='right')


# ==================== FUNCIONES DE UTILIDAD PARA COACH ====================

def validar_permisos_coach(usuario_rol):
    """Valida que el usuario tenga permisos de coach"""
    return usuario_rol == 'coach'


def formatear_tiempo_entrenamiento(minutos):
    """Formatea tiempo de entrenamiento"""
    if minutos < 60:
        return f"{minutos} min"
    else:
        horas = minutos // 60
        mins = minutos % 60
        return f"{horas}h {mins}min" if mins > 0 else f"{horas}h"


def calcular_eficiencia_coach(sesiones_completadas, sesiones_programadas):
    """Calcula eficiencia del coach"""
    if sesiones_programadas == 0:
        return 0
    return round((sesiones_completadas / sesiones_programadas) * 100, 1)


def generar_id_rutina():
    """Genera ID único para rutinas"""
    import secrets
    return f"RUT_{secrets.token_hex(4).upper()}"


def obtener_color_estado_sesion(estado):
    """Obtiene color según estado de sesión"""
    colores = {
        'programada': '#f59e0b',    # Amarillo
        'en_curso': '#2563eb',      # Azul
        'completada': '#16a34a',    # Verde
        'cancelada': '#dc2626',     # Rojo
        'perdida': '#6b7280'        # Gris
    }
    return colores.get(estado.lower(), '#6b7280')