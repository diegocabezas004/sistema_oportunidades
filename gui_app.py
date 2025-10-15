"""
Sistema de Búsqueda de Oportunidades de Financiamiento
Interfaz Gráfica Responsive con Configuración Dinámica
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import sys
import json
from pathlib import Path
from datetime import datetime
import webbrowser

# Importar módulos del sistema
sys.path.append(str(Path(__file__).parent / "scripts"))
from webpage_print_to_pdf import export_urls
from funding_pdf_extractor import process_pdf_folder
import config

class FundingOpportunitiesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Sistema de Oportunidades de Financiamiento")
        
        # Configurar ventana responsive
        self.setup_responsive_window()
        
        # Variables
        self.urls_list = []
        self.is_processing = False
        
        # Configurar estilo
        self.setup_style()
        
        # Crear interfaz
        self.create_widgets()
        
        # Verificar API Key
        self.check_api_key()
        
        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)
    
    def setup_responsive_window(self):
        """Configura la ventana para ser responsive"""
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcular tamaño inicial (80% de la pantalla)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Tamaño mínimo
        min_width = 900
        min_height = 650
        
        # Establecer tamaño
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(min_width, min_height)
        
        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configurar grid weights para responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def on_window_resize(self, event):
        """Maneja el evento de redimensionamiento de ventana"""
        # Aquí puedes agregar lógica adicional si necesitas
        pass
    
    def setup_style(self):
        """Configura el estilo visual de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores corporativos
        self.colors = {
            'primary': '#2C3E50',
            'secondary': '#3498DB',
            'success': '#27AE60',
            'warning': '#F39C12',
            'danger': '#E74C3C',
            'light': "#5C6769",
            'dark': '#34495E',
            'white': "#7B7272"
        }
        
        # Configurar estilos
        style.configure('Title.TLabel', 
                       font=('Arial', 20, 'bold'),
                       foreground=self.colors['primary'])
        
        style.configure('Subtitle.TLabel',
                       font=('Arial', 11),
                       foreground=self.colors['dark'])
        
        style.configure('Header.TLabel',
                       font=('Arial', 13, 'bold'),
                       foreground=self.colors['primary'])
        
        style.configure('Primary.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=8)
        
        style.configure('Success.TButton',
                       font=('Arial', 10, 'bold'),
                       padding=8)
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Pestañas
        self.tab_export = ttk.Frame(notebook)
        notebook.add(self.tab_export, text="📄 Exportar URLs")
        self.create_export_tab()
        
        self.tab_process = ttk.Frame(notebook)
        notebook.add(self.tab_process, text="🤖 Analizar PDFs")
        self.create_process_tab()
        
        self.tab_pipeline = ttk.Frame(notebook)
        notebook.add(self.tab_pipeline, text="🔄 Pipeline")
        self.create_pipeline_tab()
        
        self.tab_results = ttk.Frame(notebook)
        notebook.add(self.tab_results, text="📊 Resultados")
        self.create_results_tab()
        
        self.tab_config = ttk.Frame(notebook)
        notebook.add(self.tab_config, text="⚙️ Configuración")
        self.create_config_tab()
        
        # Console output
        self.create_console(main_frame)
    
    def create_header(self, parent):
        """Crea el encabezado de la aplicación"""
        header_frame = tk.Frame(parent, bg=self.colors['primary'], height=100)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="🔍 Sistema de Oportunidades de Financiamiento",
            font=('Arial', 18, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['white']
        )
        title_label.grid(row=0, column=0, pady=(15, 5))
        
        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="Análisis automatizado con Inteligencia Artificial | Versión 1.0",
            font=('Arial', 10),
            bg=self.colors['primary'],
            fg=self.colors['light']
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 15))
    
    def create_export_tab(self):
        """Pestaña para exportar URLs a PDF - Responsive"""
        # Configurar grid
        self.tab_export.grid_rowconfigure(1, weight=1)
        self.tab_export.grid_columnconfigure(0, weight=1)
        
        # Frame contenedor
        frame = ttk.Frame(self.tab_export, padding=15)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Instrucciones
        ttk.Label(
            frame,
            text="Ingresa las URLs que deseas convertir a PDF",
            style='Header.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Frame para entrada de URLs
        input_frame = ttk.LabelFrame(frame, text="URLs (una por línea)", padding=10)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.urls_text = scrolledtext.ScrolledText(
            input_frame,
            font=('Courier', 9),
            wrap=tk.WORD
        )
        self.urls_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URLs de ejemplo
        ejemplo_urls = """https://www.grants.gov/search-grants
https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home"""
        self.urls_text.insert(1.0, ejemplo_urls)
        
        # Frame de botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            button_frame,
            text="🗑️ Limpiar",
            command=self.clear_urls,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📥 Cargar archivo",
            command=self.load_urls_from_file,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🚀 Exportar a PDF",
            command=self.start_export,
            style='Success.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        # Barra de progreso
        self.export_progress = ttk.Progressbar(frame, mode='indeterminate')
        self.export_progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
    
    def create_process_tab(self):
        """Pestaña para procesar PDFs - Responsive"""
        # Configurar grid
        self.tab_process.grid_rowconfigure(2, weight=1)
        self.tab_process.grid_columnconfigure(0, weight=1)
        
        frame = ttk.Frame(self.tab_process, padding=15)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Instrucciones
        ttk.Label(
            frame,
            text="Analiza PDFs con Inteligencia Artificial",
            style='Header.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Info frame
        info_frame = ttk.LabelFrame(frame, text="Información", padding=10)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.pdf_count_label = ttk.Label(
            info_frame,
            text="PDFs disponibles: Calculando...",
            font=('Arial', 10)
        )
        self.pdf_count_label.pack(anchor=tk.W, pady=5)
        
        ttk.Label(
            info_frame,
            text=f"📁 Carpeta: {config.PDFS_SALIDA}",
            font=('Arial', 9)
        ).pack(anchor=tk.W, pady=5)
        
        ttk.Button(
            info_frame,
            text="🔄 Actualizar conteo",
            command=self.update_pdf_count
        ).pack(anchor=tk.W, pady=5)
        
        # Lista de PDFs
        list_frame = ttk.LabelFrame(frame, text="PDFs detectados", padding=10)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.pdf_listbox = tk.Listbox(list_frame, font=('Courier', 9))
        self.pdf_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, command=self.pdf_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.pdf_listbox.config(yscrollcommand=scrollbar.set)
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            button_frame,
            text="📂 Abrir carpeta",
            command=self.open_pdf_folder,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🤖 Analizar con IA",
            command=self.start_processing,
            style='Success.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        # Barra de progreso
        self.process_progress = ttk.Progressbar(frame, mode='indeterminate')
        self.process_progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Actualizar conteo inicial
        self.update_pdf_count()
    
    def create_pipeline_tab(self):
        """Pestaña pipeline - Responsive"""
        self.tab_pipeline.grid_rowconfigure(2, weight=1)
        self.tab_pipeline.grid_columnconfigure(0, weight=1)
        
        frame = ttk.Frame(self.tab_pipeline, padding=15)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Título
        ttk.Label(
            frame,
            text="Pipeline Completo: URLs → PDFs → Análisis",
            style='Header.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Diagrama
        flow_frame = tk.Frame(frame, bg=self.colors['light'], relief=tk.RIDGE, bd=2)
        flow_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=15, padx=10)
        
        steps = ["📝 URLs", "📄 PDFs", "🤖 IA", "📊 Reportes"]
        
        for i, step in enumerate(steps):
            step_label = tk.Label(
                flow_frame,
                text=step,
                font=('Arial', 11, 'bold'),
                bg=self.colors['light'],
                fg=self.colors['primary']
            )
            step_label.pack(side=tk.LEFT, expand=True, padx=10, pady=10)
            
            if i < len(steps) - 1:
                arrow_label = tk.Label(
                    flow_frame,
                    text="→",
                    font=('Arial', 14),
                    bg=self.colors['light']
                )
                arrow_label.pack(side=tk.LEFT)
        
        # Input URLs
        input_frame = ttk.LabelFrame(frame, text="URLs para el Pipeline", padding=10)
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=15)
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.pipeline_urls_text = scrolledtext.ScrolledText(
            input_frame,
            font=('Courier', 9),
            wrap=tk.WORD
        )
        self.pipeline_urls_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            button_frame,
            text="🗑️ Limpiar",
            command=lambda: self.pipeline_urls_text.delete(1.0, tk.END),
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🚀 Ejecutar Pipeline",
            command=self.start_pipeline,
            style='Success.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        # Barra de progreso
        self.pipeline_progress = ttk.Progressbar(frame, mode='indeterminate')
        self.pipeline_progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
    
    def create_results_tab(self):
        """Pestaña resultados - Responsive"""
        self.tab_results.grid_rowconfigure(2, weight=1)
        self.tab_results.grid_columnconfigure(0, weight=1)
        
        frame = ttk.Frame(self.tab_results, padding=15)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Título
        ttk.Label(
            frame,
            text="Resultados del Análisis",
            style='Header.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Resumen
        summary_frame = ttk.LabelFrame(frame, text="Resumen", padding=10)
        summary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        summary_frame.grid_columnconfigure(0, weight=1)
        
        self.summary_text = tk.Text(
            summary_frame,
            height=6,
            font=('Arial', 9),
            wrap=tk.WORD,
            bg=self.colors['light']
        )
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.summary_text.config(state=tk.DISABLED)
        
        # Oportunidades
        opps_frame = ttk.LabelFrame(frame, text="Oportunidades", padding=10)
        opps_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        opps_frame.grid_rowconfigure(0, weight=1)
        opps_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview
        tree_frame = ttk.Frame(opps_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.results_tree = ttk.Treeview(
            tree_frame,
            columns=('Título', 'Deadline', 'Sponsor', 'Status'),
            show='tree headings'
        )
        
        self.results_tree.heading('#0', text='#')
        self.results_tree.heading('Título', text='Título')
        self.results_tree.heading('Deadline', text='Fecha Límite')
        self.results_tree.heading('Sponsor', text='Patrocinador')
        self.results_tree.heading('Status', text='Estado')
        
        self.results_tree.column('#0', width=40, minwidth=40)
        self.results_tree.column('Título', width=300, minwidth=200)
        self.results_tree.column('Deadline', width=120, minwidth=100)
        self.results_tree.column('Sponsor', width=150, minwidth=100)
        self.results_tree.column('Status', width=80, minwidth=80)
        
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            button_frame,
            text="🔄 Cargar",
            command=self.load_results,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📂 Carpeta",
            command=self.open_results_folder,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📄 JSON",
            command=self.open_json_results,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📝 DOCX",
            command=self.open_docx_results,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
    
    def create_config_tab(self):
        """Pestaña de configuración - CON CAMBIO DE RUTAS"""
        self.tab_config.grid_rowconfigure(0, weight=1)
        self.tab_config.grid_columnconfigure(0, weight=1)
        
        # Frame con scroll
        canvas = tk.Canvas(self.tab_config)
        scrollbar = ttk.Scrollbar(self.tab_config, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        frame = ttk.Frame(scrollable_frame, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            frame,
            text="Configuración del Sistema",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # OpenAI Config
        openai_frame = ttk.LabelFrame(frame, text="Configuración OpenAI", padding=12)
        openai_frame.pack(fill=tk.X, pady=10)
        
        grid_row = 0
        configs_openai = [
            ("API Key:", "✅ Configurada" if config.OPENAI_API_KEY != "sk-..." else "❌ No configurada"),
            ("Modelo:", config.OPENAI_MODEL),
            ("Temperatura:", str(config.OPENAI_TEMPERATURE))
        ]
        
        for label, value in configs_openai:
            ttk.Label(openai_frame, text=label, font=('Arial', 10, 'bold')).grid(row=grid_row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            ttk.Label(openai_frame, text=value, font=('Arial', 10)).grid(row=grid_row, column=1, sticky=tk.W, pady=5)
            grid_row += 1
        
        # Processing Config
        process_frame = ttk.LabelFrame(frame, text="Configuración de Procesamiento", padding=12)
        process_frame.pack(fill=tk.X, pady=10)
        
        grid_row = 0
        configs_process = [
            ("Idioma:", config.LANGUAGE_OUTPUT),
            ("Tamaño chunk:", f"{config.CHUNK_SIZE} tokens"),
            ("Overlap chunk:", f"{config.CHUNK_OVERLAP} tokens"),
            ("Max chunks/doc:", str(config.MAX_CHUNKS_PER_DOC)),
            ("Mantener cerradas:", "Sí" if config.KEEP_CLOSED else "No"),
            ("Max reintentos:", str(config.MAX_RETRIES)),
            ("Delay (segs):", f"{config.RATE_LIMIT_DELAY}s")
        ]
        
        for label, value in configs_process:
            ttk.Label(process_frame, text=label, font=('Arial', 10, 'bold')).grid(row=grid_row, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            ttk.Label(process_frame, text=value, font=('Arial', 10)).grid(row=grid_row, column=1, sticky=tk.W, pady=5)
            grid_row += 1
        
        # ⭐ RUTAS DEL SISTEMA - CON BOTONES PARA CAMBIAR
        paths_frame = ttk.LabelFrame(frame, text="📁 Rutas del Sistema", padding=12)
        paths_frame.pack(fill=tk.X, pady=10)
        
        # PDFs Entrada
        ttk.Label(paths_frame, text="PDFs Entrada:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.path_entrada_label = ttk.Label(paths_frame, text=str(config.PDFS_ENTRADA), font=('Courier', 9))
        self.path_entrada_label.grid(row=0, column=1, sticky=tk.W, pady=8, padx=(10, 10))
        ttk.Button(
            paths_frame,
            text="📂 Cambiar",
            command=lambda: self.change_folder('entrada'),
            width=10
        ).grid(row=0, column=2, sticky=tk.E, pady=8)
        
        # PDFs Salida
        ttk.Label(paths_frame, text="PDFs Salida:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.path_salida_label = ttk.Label(paths_frame, text=str(config.PDFS_SALIDA), font=('Courier', 9))
        self.path_salida_label.grid(row=1, column=1, sticky=tk.W, pady=8, padx=(10, 10))
        ttk.Button(
            paths_frame,
            text="📂 Cambiar",
            command=lambda: self.change_folder('salida'),
            width=10
        ).grid(row=1, column=2, sticky=tk.E, pady=8)
        
        # Resultados
        ttk.Label(paths_frame, text="Resultados:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.path_resultados_label = ttk.Label(paths_frame, text=str(config.RESULTADOS), font=('Courier', 9))
        self.path_resultados_label.grid(row=2, column=1, sticky=tk.W, pady=8, padx=(10, 10))
        ttk.Button(
            paths_frame,
            text="📂 Cambiar",
            command=lambda: self.change_folder('resultados'),
            width=10
        ).grid(row=2, column=2, sticky=tk.E, pady=8)
        
        paths_frame.grid_columnconfigure(1, weight=1)
        
        # Botón para restaurar rutas por defecto
        ttk.Button(
            paths_frame,
            text="🔄 Restaurar rutas por defecto",
            command=self.restore_default_paths,
            style='Primary.TButton'
        ).grid(row=3, column=0, columnspan=3, pady=(15, 5), sticky=(tk.W, tk.E))
        
        # Botón para editar config
        ttk.Button(
            frame,
            text="📝 Editar configuración avanzada (config.py)",
            command=self.open_config_file,
            style='Primary.TButton'
        ).pack(pady=15, fill=tk.X)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_console(self, parent):
        """Crea la consola de salida - Responsive"""
        console_frame = ttk.LabelFrame(parent, text="📟 Consola", padding=8)
        console_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(5, 10))
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar altura mínima
        parent.grid_rowconfigure(2, minsize=150)
        
        self.console_text = scrolledtext.ScrolledText(
            console_frame,
            height=8,
            font=('Courier', 9),
            bg='#1E1E1E',
            fg='#00FF00',
            wrap=tk.WORD
        )
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Button(
            console_frame,
            text="🗑️ Limpiar",
            command=lambda: self.console_text.delete(1.0, tk.END)
        ).grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
    
    # ⭐ NUEVOS MÉTODOS PARA CAMBIAR RUTAS
    
    def change_folder(self, folder_type):
        """Permite cambiar la ruta de una carpeta"""
        titles = {
            'entrada': "Seleccionar carpeta para PDFs de Entrada",
            'salida': "Seleccionar carpeta para PDFs de Salida",
            'resultados': "Seleccionar carpeta para Resultados"
        }
        
        current_paths = {
            'entrada': config.PDFS_ENTRADA,
            'salida': config.PDFS_SALIDA,
            'resultados': config.RESULTADOS
        }
        
        # Abrir diálogo para seleccionar carpeta
        new_path = filedialog.askdirectory(
            title=titles[folder_type],
            initialdir=str(current_paths[folder_type])
        )
        
        if new_path:
            # Confirmar cambio
            response = messagebox.askyesno(
                "Confirmar cambio",
                f"¿Cambiar la ruta de {folder_type} a:\n\n{new_path}\n\n"
                "Este cambio se guardará permanentemente."
            )
            
            if response:
                # Actualizar configuración
                if folder_type == 'entrada':
                    config.update_paths(entrada=new_path)
                    self.path_entrada_label.config(text=new_path)
                elif folder_type == 'salida':
                    config.update_paths(salida=new_path)
                    self.path_salida_label.config(text=new_path)
                elif folder_type == 'resultados':
                    config.update_paths(resultados=new_path)
                    self.path_resultados_label.config(text=new_path)
                
                self.log(f"✅ Ruta de {folder_type} actualizada: {new_path}")
                
                # Recargar módulos que usan las rutas
                self.reload_paths()
                
                messagebox.showinfo(
                    "Ruta actualizada",
                    f"La ruta de {folder_type} ha sido actualizada correctamente.\n\n"
                    "Los cambios están activos."
                )
    
    def restore_default_paths(self):
        """Restaura las rutas a sus valores por defecto"""
        response = messagebox.askyesno(
            "Restaurar rutas",
            "¿Restaurar todas las rutas a sus valores por defecto?\n\n"
            "Esto sobrescribirá las rutas personalizadas."
        )
        
        if response:
            base_dir = Path(__file__).parent
            
            config.update_paths(
                entrada=str(base_dir / "pdfs_entrada"),
                salida=str(base_dir / "pdfs_salida"),
                resultados=str(base_dir / "resultados")
            )
            
            # Actualizar labels
            self.path_entrada_label.config(text=str(config.PDFS_ENTRADA))
            self.path_salida_label.config(text=str(config.PDFS_SALIDA))
            self.path_resultados_label.config(text=str(config.RESULTADOS))
            
            self.reload_paths()
            
            self.log("✅ Rutas restauradas a valores por defecto")
            messagebox.showinfo("Rutas restauradas", "Las rutas han sido restauradas correctamente.")
    
    def reload_paths(self):
        """Recarga las rutas en TODOS los módulos - VERSIÓN MEJORADA"""
        import sys
        import importlib
        
        self.log("🔄 Recargando configuración...")
        
        # Paso 1: Limpiar cache de módulos
        modules_to_reload = ['config', 'webpage_print_to_pdf', 'funding_pdf_extractor']
        for module_name in modules_to_reload:
            if module_name in sys.modules:
                del sys.modules[module_name]
                self.log(f"   🗑️ Cache limpiado: {module_name}")
        
        # Paso 2: Forzar reimportación de config
        global config
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        config = importlib.import_module('config')
        
        # Paso 3: Verificar que las rutas se actualizaron
        self.log("✅ Configuración recargada:")
        self.log(f"   📥 PDFs Entrada: {config.PDFS_ENTRADA}")
        self.log(f"   📤 PDFs Salida: {config.PDFS_SALIDA}")
        self.log(f"   📊 Resultados: {config.RESULTADOS}")
        
        # Paso 4: Actualizar interfaz
        self.update_pdf_count()
        
        # Paso 5: Confirmar que las carpetas existen
        for folder_name, folder_path in [
            ("Entrada", config.PDFS_ENTRADA),
            ("Salida", config.PDFS_SALIDA),
            ("Resultados", config.RESULTADOS)
        ]:
            if folder_path.exists():
                self.log(f"   ✅ {folder_name}: carpeta verificada")
            else:
                folder_path.mkdir(parents=True, exist_ok=True)
                self.log(f"   📁 {folder_name}: carpeta creada")
    
    def change_folder(self, folder_type):
        """Permite cambiar la ruta de una carpeta - VERSIÓN MEJORADA"""
        titles = {
            'entrada': "Seleccionar carpeta para PDFs de Entrada",
            'salida': "Seleccionar carpeta para PDFs de Salida",
            'resultados': "Seleccionar carpeta para Resultados"
        }
        
        current_paths = {
            'entrada': config.PDFS_ENTRADA,
            'salida': config.PDFS_SALIDA,
            'resultados': config.RESULTADOS
        }
        
        # Abrir diálogo
        new_path = filedialog.askdirectory(
            title=titles[folder_type],
            initialdir=str(current_paths[folder_type])
        )
        
        if new_path:
            # Confirmar
            response = messagebox.askyesno(
                "Confirmar cambio",
                f"¿Cambiar la ruta de {folder_type} a:\n\n{new_path}\n\n"
                "Los archivos se guardarán en esta nueva ubicación."
            )
            
            if response:
                self.log(f"🔄 Cambiando ruta de {folder_type}...")
                
                # Actualizar configuración
                if folder_type == 'entrada':
                    config.update_paths(entrada=new_path)
                    self.path_entrada_label.config(text=new_path)
                elif folder_type == 'salida':
                    config.update_paths(salida=new_path)
                    self.path_salida_label.config(text=new_path)
                elif folder_type == 'resultados':
                    config.update_paths(resultados=new_path)
                    self.path_resultados_label.config(text=new_path)
                
                # IMPORTANTE: Recargar módulos con la nueva configuración
                self.reload_paths()
                
                self.log(f"✅ Ruta actualizada exitosamente")
                
                messagebox.showinfo(
                    "Ruta actualizada",
                    f"La ruta de {folder_type} ha sido actualizada.\n\n"
                    f"Nueva ubicación:\n{new_path}\n\n"
                    "Los próximos archivos se guardarán aquí."
                )
    
    def restore_default_paths(self):
        """Restaura las rutas a sus valores por defecto - VERSIÓN MEJORADA"""
        response = messagebox.askyesno(
            "Restaurar rutas",
            "¿Restaurar todas las rutas a sus valores por defecto?\n\n"
            "Las rutas volverán a:\n"
            "• pdfs_entrada/\n"
            "• pdfs_salida/\n"
            "• resultados/"
        )
        
        if response:
            self.log("🔄 Restaurando rutas por defecto...")
            
            base_dir = Path(__file__).parent
            
            # Actualizar todas las rutas
            config.update_paths(
                entrada=str(base_dir / "pdfs_entrada"),
                salida=str(base_dir / "pdfs_salida"),
                resultados=str(base_dir / "resultados")
            )
            
            # Actualizar labels en la interfaz
            self.path_entrada_label.config(text=str(config.PDFS_ENTRADA))
            self.path_salida_label.config(text=str(config.PDFS_SALIDA))
            self.path_resultados_label.config(text=str(config.RESULTADOS))
            
            # Recargar módulos
            self.reload_paths()
            
            self.log("✅ Rutas restauradas correctamente")
            messagebox.showinfo(
                "Rutas restauradas",
                "Las rutas han sido restauradas a sus valores por defecto."
            )
    
    # MÉTODOS DE FUNCIONALIDAD (continuación del código anterior)
    
    def log(self, message, level='info'):
        """Imprime mensaje en la consola"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)
        self.root.update()
    
    def check_api_key(self):
        """Verifica si la API key está configurada"""
        if config.OPENAI_API_KEY == "sk-..." or len(config.OPENAI_API_KEY) < 20:
            messagebox.showwarning(
                "API Key no configurada",
                "⚠️ No has configurado tu API Key de OpenAI.\n\n"
                "Edita el archivo .env y añade tu clave.\n"
                "Puedes obtenerla en: https://platform.openai.com/api-keys"
            )
    
    def clear_urls(self):
        """Limpia el campo de URLs"""
        self.urls_text.delete(1.0, tk.END)
    
    def load_urls_from_file(self):
        """Carga URLs desde un archivo de texto"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de URLs",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    urls = f.read()
                    self.urls_text.delete(1.0, tk.END)
                    self.urls_text.insert(1.0, urls)
                self.log(f"✅ URLs cargadas desde {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")
    
    def update_pdf_count(self):
        """Actualiza el conteo de PDFs"""
        pdfs = list(config.PDFS_SALIDA.glob("*.pdf"))
        self.pdf_count_label.config(text=f"PDFs disponibles: {len(pdfs)}")
        
        self.pdf_listbox.delete(0, tk.END)
        for pdf in pdfs:
            self.pdf_listbox.insert(tk.END, pdf.name)
    
    def open_pdf_folder(self):
        """Abre la carpeta de PDFs"""
        import subprocess
        import platform
        
        path = str(config.PDFS_SALIDA)
        
        if platform.system() == 'Darwin':
            subprocess.run(['open', path])
        elif platform.system() == 'Windows':
            subprocess.run(['explorer', path])
        else:
            subprocess.run(['xdg-open', path])
    
    def open_results_folder(self):
        """Abre la carpeta de resultados"""
        import subprocess
        import platform
        
        path = str(config.RESULTADOS)
        
        if platform.system() == 'Darwin':
            subprocess.run(['open', path])
        elif platform.system() == 'Windows':
            subprocess.run(['explorer', path])
        else:
            subprocess.run(['xdg-open', path])
    
    def open_json_results(self):
        """Abre el archivo JSON de resultados"""
        json_path = config.RESULTADOS / "oportunidades_resultados.json"
        if json_path.exists():
            webbrowser.open(str(json_path))
        else:
            messagebox.showinfo("Info", "Aún no hay resultados generados")
    
    def open_docx_results(self):
        """Abre el documento DOCX de resultados"""
        docx_path = config.RESULTADOS / "resumen_oportunidades.docx"
        if docx_path.exists():
            import subprocess
            import platform
            
            if platform.system() == 'Darwin':
                subprocess.run(['open', str(docx_path)])
            elif platform.system() == 'Windows':
                subprocess.run(['start', str(docx_path)], shell=True)
            else:
                subprocess.run(['xdg-open', str(docx_path)])
        else:
            messagebox.showinfo("Info", "Aún no hay resultados generados")
    
    def open_config_file(self):
        """Abre el archivo de configuración"""
        config_path = Path(__file__).parent / "scripts" / "config.py"
        webbrowser.open(str(config_path))
    
    def start_export(self):
        """Inicia la exportación de URLs"""
        if self.is_processing:
            messagebox.showwarning("Procesando", "Ya hay un proceso en ejecución")
            return
        
        urls_text = self.urls_text.get(1.0, tk.END).strip()
        urls = [u.strip() for u in urls_text.split('\n') if u.strip() and u.strip().startswith('http')]
        
        if not urls:
            messagebox.showwarning("URLs vacías", "Por favor ingresa al menos una URL válida")
            return
        
        response = messagebox.askyesno(
            "Confirmar exportación",
            f"¿Exportar {len(urls)} URLs a PDF?\n\nEsto puede tomar varios minutos."
        )
        
        if not response:
            return
        
        self.is_processing = True
        self.export_progress.start()
        
        thread = threading.Thread(target=self.export_thread, args=(urls,))
        thread.daemon = True
        thread.start()
    
    def export_thread(self, urls):
        try:
            self.log(f"🚀 Iniciando exportación de {len(urls)} URLs...")
        
            resultados = export_urls(urls)
        
            exitosos = sum(1 for r in resultados if r['status'] == 'success')
            errores = len(urls) - exitosos
        
            self.log(f"✅ Exportación completada: {exitosos} exitosos, {errores} errores")
        
            for r in resultados:
                if r['status'] == 'success':
                    self.log(f"✅ {r['filename']}")
                else:
                    self.log(f"❌ Error: {r['message'][:100]}", 'error')
        
            self.root.after(0, self.update_pdf_count)
        
            # ✅ CORRECCIÓN APLICADA
            success_msg = f"✅ {exitosos} PDFs creados\n❌ {errores} errores"
            self.root.after(0, lambda msg=success_msg: messagebox.showinfo(
                "Exportación completada", msg
            ))
        
        except Exception as e:
            # ✅ CORRECCIÓN APLICADA
            error_msg = str(e)
            self.log(f"❌ Error: {error_msg}", 'error')
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))
    
        finally:
            self.is_processing = False
            self.root.after(0, self.export_progress.stop)
    
    def start_processing(self):
        """Inicia el procesamiento de PDFs"""
        if self.is_processing:
            messagebox.showwarning("Procesando", "Ya hay un proceso en ejecución")
            return
        
        pdfs = list(config.PDFS_SALIDA.glob("*.pdf"))
        
        if not pdfs:
            messagebox.showwarning(
                "No hay PDFs",
                f"No se encontraron PDFs en {config.PDFS_SALIDA}"
            )
            return
        
        response = messagebox.askyesno(
            "Confirmar análisis",
            f"¿Analizar {len(pdfs)} PDFs con IA?\n\n"
            f"Modelo: {config.OPENAI_MODEL}"
        )
        
        if not response:
            return
        
        self.is_processing = True
        self.process_progress.start()
        
        thread = threading.Thread(target=self.process_thread)
        thread.daemon = True
        thread.start()
    
    def process_thread(self):
        try:
            self.log("🤖 Iniciando análisis con IA...")
        
            resultado = process_pdf_folder()
        
            total_opps = resultado.get('total_opportunities', 0)
            total_pdfs = resultado.get('total_pdfs', 0)
        
            self.log(f"✅ Completado: {total_pdfs} PDFs, {total_opps} oportunidades")
        
            self.root.after(0, self.load_results)
        
            # ✅ CORRECCIÓN APLICADA
            success_msg = f"✅ {total_pdfs} PDFs procesados\n💰 {total_opps} oportunidades"
            self.root.after(0, lambda msg=success_msg: messagebox.showinfo(
                "Análisis completado", msg
            ))
        
        except Exception as e:
            # ✅ CORRECCIÓN APLICADA
            error_msg = str(e)
            self.log(f"❌ Error: {error_msg}", 'error')
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))
    
        finally:
            self.is_processing = False
            self.root.after(0, self.process_progress.stop)
    
    def start_pipeline(self):
        """Inicia el pipeline completo"""
        if self.is_processing:
            messagebox.showwarning("Procesando", "Ya hay un proceso en ejecución")
            return
        
        urls_text = self.pipeline_urls_text.get(1.0, tk.END).strip()
        urls = [u.strip() for u in urls_text.split('\n') if u.strip() and u.strip().startswith('http')]
        
        if not urls:
            messagebox.showwarning("URLs vacías", "Por favor ingresa al menos una URL válida")
            return
        
        response = messagebox.askyesno(
            "Confirmar pipeline",
            f"¿Ejecutar pipeline completo con {len(urls)} URLs?"
        )
        
        if not response:
            return
        
        self.is_processing = True
        self.pipeline_progress.start()
        
        thread = threading.Thread(target=self.pipeline_thread, args=(urls,))
        thread.daemon = True
        thread.start()
    
    def pipeline_thread(self, urls):
        try:
            self.log("🔄 PIPELINE INICIADO")
        
            # Exportar
            self.log(f"[1/2] Exportando {len(urls)} URLs...")
            resultados_export = export_urls(urls)
        
            exitosos = sum(1 for r in resultados_export if r['status'] == 'success')
        
            if exitosos == 0:
                self.log("❌ No se pudo exportar ningún PDF", 'error')
                return
        
            self.log(f"✅ {exitosos} PDFs creados")
        
            # Procesar
            import time
            time.sleep(2)
        
            self.log("[2/2] Analizando con IA...")
            resultado = process_pdf_folder()
        
            total_opps = resultado.get('total_opportunities', 0)
        
            self.log(f"🎉 PIPELINE COMPLETADO: {total_opps} oportunidades")
        
            self.root.after(0, self.load_results)
            self.root.after(0, self.update_pdf_count)
        
            # ✅ CORRECCIÓN APLICADA
            success_msg = f"🎉 Proceso finalizado\n\n💰 {total_opps} oportunidades encontradas"
            self.root.after(0, lambda msg=success_msg: messagebox.showinfo(
                "Pipeline completado", msg
            ))
        
        except Exception as e:
            # ✅ CORRECCIÓN APLICADA
            error_msg = str(e)
            self.log(f"❌ Error: {error_msg}", 'error')
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))
    
        finally:
            self.is_processing = False
            self.root.after(0, self.pipeline_progress.stop)
    
    def load_results(self):
        """Carga los resultados del JSON"""
        json_path = config.RESULTADOS / "oportunidades_resultados.json"
        
        if not json_path.exists():
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, "Aún no hay resultados.\nEjecuta el análisis primero.")
            self.summary_text.config(state=tk.DISABLED)
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Resumen
            summary = f"""📅 Fecha: {data.get('processing_date', 'N/A')[:10]}
📄 PDFs: {data.get('total_pdfs', 0)}
💰 Oportunidades: {data.get('total_opportunities', 0)}
🌍 Idioma: {data.get('language', 'ES')}

✅ Resultados cargados"""
            
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary)
            self.summary_text.config(state=tk.DISABLED)
            
            # Limpiar TreeView
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Cargar oportunidades
            all_opportunities = []
            for result in data.get('results', []):
                all_opportunities.extend(result.get('opportunities', []))
            
            for i, opp in enumerate(all_opportunities, 1):
                self.results_tree.insert(
                    '',
                    'end',
                    text=str(i),
                    values=(
                        opp.get('title', 'Sin título')[:50],
                        opp.get('deadline', 'N/A'),
                        opp.get('sponsor', 'N/A')[:25],
                        opp.get('status', 'unknown')
                    )
                )
            
            self.log(f"✅ {len(all_opportunities)} oportunidades cargadas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando resultados:\n{str(e)}")

def main():
    """Función principal"""
    root = tk.Tk()
    app = FundingOpportunitiesApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()