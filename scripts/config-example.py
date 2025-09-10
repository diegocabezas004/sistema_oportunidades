# scripts/config.py
import os
from pathlib import Path

# Configuración de OpenAI
OPEN_API_KEY = 'your api key'
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.0

# Rutas del proyecto
BASE_DIR = Path(__file__).parent.parent
PDFS_ENTRADA = BASE_DIR / "pdfs_entrada"
PDFS_SALIDA = BASE_DIR / "pdfs_salida"
RESULTADOS = BASE_DIR / "resultados"

# Crear carpetas si no existen
for folder in [PDFS_ENTRADA, PDFS_SALIDA, RESULTADOS]:
    folder.mkdir(parents=True, exist_ok=True)

# Configuración de exportación PDF
PDF_CONFIG = {
    "paper": "A4",
    "landscape": False,
    "print_background": True,
    "margin": {"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"},
    "scale": 1.0,
    "prefer_css_page_size": True,
    "timeout": 30000  # milisegundos
}

# Configuración de procesamiento
CHUNK_SIZE = 6000  # tokens aproximados
CHUNK_OVERLAP = 500  # tokens de solapamiento
MAX_CHUNKS_PER_DOC = 10  # límite de chunks por documento

# Palabras clave para priorización
KEYWORDS = [
    "convocatoria", "grant", "funding", "beca", "premio", "award",
    "RFP", "request for proposal", "concurso", "subsidio", "financiamiento",
    "apoyo", "fondo", "call for proposals", "fellowship", "scholarship",
    "subvención", "ayuda", "dotación", "patrocinio", "call", "opportunity"
]

# Configuración de filtrado
KEEP_CLOSED = False  # Si False, filtra convocatorias cerradas
LANGUAGE_OUTPUT = "ES"  # ES o EN

# Límites de procesamiento
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1  # segundos entre llamadas API