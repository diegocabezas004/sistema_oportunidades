# scripts/config.py
"""
Configuración del sistema con soporte multiplataforma
Detecta automáticamente el sistema operativo y maneja rutas correctamente
"""

import os
import json
import platform
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de OpenAI desde .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-...')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))

# Rutas del proyecto
BASE_DIR = Path(_file_).parent.parent.resolve()  #  .resolve() para path absoluto
CONFIG_FILE = BASE_DIR / "user_config.json"

def load_user_config():
    """Carga la configuración personalizada del usuario"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # ⭐ VALIDAR que las rutas existen y son accesibles
                validated_config = {}
                for key, value in config.items():
                    path = Path(value)
                    
                    # Si la ruta no existe o no es accesible, usar default
                    if not path.exists() or not os.access(path.parent, os.W_OK):
                        print(f"⚠ Ruta inaccesible en user_config.json: {value}")
                        print(f"   Usando ruta por defecto para {key}")
                        continue
                    
                    validated_config[key] = str(path)
                
                return validated_config
        except Exception as e:
            print(f"⚠ Error leyendo user_config.json: {e}")
            print("   Usando rutas por defecto")
            return {}
    return {}

def save_user_config(config):
    """Guarda la configuración personalizada del usuario"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False

def get_safe_path(path_str):
    """
    Convierte una ruta a Path de forma segura
    Maneja rutas de diferentes sistemas operativos
    """
    try:
        # Convertir a Path
        path = Path(path_str)
        
        # ⭐ Si la ruta no es absoluta o no existe, usar default
        if not path.is_absolute():
            return None
        
        # ⭐ Verificar que el directorio padre existe y es escribible
        if path.exists():
            if not os.access(str(path), os.W_OK):
                return None
        else:
            # Si no existe, verificar que podemos crear
            parent = path.parent
            if not parent.exists() or not os.access(str(parent), os.W_OK):
                return None
        
        return path
    except Exception:
        return None

# Cargar configuración del usuario
user_config = load_user_config()

# ⭐ RUTAS CON FALLBACK AUTOMÁTICO
def get_folder_path(key, default_name):
    """
    Obtiene la ruta de una carpeta con fallback automático
    Si la ruta en user_config no es válida, usa la por defecto
    """
    # Intentar usar la ruta del usuario
    if key in user_config:
        safe_path = get_safe_path(user_config[key])
        if safe_path:
            return safe_path
    
    # Fallback: usar ruta por defecto
    return BASE_DIR / default_name

# Definir rutas con fallback
PDFS_ENTRADA = get_folder_path('pdfs_entrada', 'pdfs_entrada')
PDFS_SALIDA = get_folder_path('pdfs_salida', 'pdfs_salida')
RESULTADOS = get_folder_path('resultados', 'resultados')

# ⭐ CREAR CARPETAS DE FORMA SEGURA
def create_folder_safe(folder_path):
    """Crea una carpeta de forma segura manejando errores"""
    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        print(f"❌ Sin permisos para crear: {folder_path}")
        print(f"   Por favor crea la carpeta manualmente o cambia permisos")
        return False
    except Exception as e:
        print(f"❌ Error creando carpeta {folder_path}: {e}")
        return False

# Intentar crear carpetas
for folder_name, folder_path in [
    ("PDFs Entrada", PDFS_ENTRADA),
    ("PDFs Salida", PDFS_SALIDA),
    ("Resultados", RESULTADOS)
]:
    if not folder_path.exists():
        print(f"📁 Creando carpeta: {folder_path}")
        if not create_folder_safe(folder_path):
            print(f"⚠ No se pudo crear {folder_name}")
            print(f"   El sistema intentará crearla cuando sea necesario")

# Configuración de exportación PDF
PDF_CONFIG = {
    "paper": "A4",
    "landscape": False,
    "print_background": True,
    "margin": {"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"},
    "scale": 1.0,
    "prefer_css_page_size": True,
    "timeout": 30000
}

# Configuración de procesamiento (desde .env o valores por defecto)
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '6000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '500'))
MAX_CHUNKS_PER_DOC = int(os.getenv('MAX_CHUNKS_PER_DOC', '10'))
KEEP_CLOSED = os.getenv('KEEP_CLOSED', 'False').lower() == 'true'
LANGUAGE_OUTPUT = os.getenv('LANGUAGE_OUTPUT', 'ES')

# Palabras clave para priorización
KEYWORDS = [
    "convocatoria", "grant", "funding", "beca", "premio", "award",
    "RFP", "request for proposal", "concurso", "subsidio", "financiamiento",
    "apoyo", "fondo", "call for proposals", "fellowship", "scholarship",
    "subvención", "ayuda", "dotación", "patrocinio", "call", "opportunity"
]

# Límites de procesamiento
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RATE_LIMIT_DELAY = int(os.getenv('RATE_LIMIT_DELAY', '1'))

def update_paths(entrada=None, salida=None, resultados=None):
    """
    Actualiza las rutas de las carpetas y las guarda
    Con validación de permisos
    """
    global PDFS_ENTRADA, PDFS_SALIDA, RESULTADOS
    
    config = load_user_config()
    updated = False
    
    if entrada:
        entrada_path = Path(entrada).resolve()
        # Validar que podemos escribir
        if create_folder_safe(entrada_path):
            PDFS_ENTRADA = entrada_path
            config['pdfs_entrada'] = str(entrada_path)
            updated = True
        else:
            print(f"⚠ No se pudo actualizar ruta de entrada")
            return False
    
    if salida:
        salida_path = Path(salida).resolve()
        if create_folder_safe(salida_path):
            PDFS_SALIDA = salida_path
            config['pdfs_salida'] = str(salida_path)
            updated = True
        else:
            print(f"⚠ No se pudo actualizar ruta de salida")
            return False
    
    if resultados:
        resultados_path = Path(resultados).resolve()
        if create_folder_safe(resultados_path):
            RESULTADOS = resultados_path
            config['resultados'] = str(resultados_path)
            updated = True
        else:
            print(f"⚠ No se pudo actualizar ruta de resultados")
            return False
    
    if updated:
        return save_user_config(config)
    
    return True

# Información del sistema (para debugging)
def print_system_info():
    """Imprime información del sistema para debugging"""
    print("\n" + "="*60)
    print("INFORMACIÓN DEL SISTEMA")
    print("="*60)
    print(f"Sistema Operativo: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Directorio base: {BASE_DIR}")
    print(f"PDFs Entrada: {PDFS_ENTRADA}")
    print(f"PDFs Salida: {PDFS_SALIDA}")
    print(f"Resultados: {RESULTADOS}")
    print(f"Config file: {CONFIG_FILE}")
    print("="*60 + "\n")

# Llamar automáticamente si se ejecuta directamente
if _name_ == "_main_":
    print_system_info()
