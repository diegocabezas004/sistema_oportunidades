```markdown
# 🔍 Sistema de Búsqueda de Oportunidades de Financiamiento

Sistema automatizado para capturar, analizar y extraer oportunidades de financiamiento (convocatorias, grants, becas, RFPs) desde páginas web utilizando IA.

## 📋 Características

- **Exportación automática de URLs a PDF**: Convierte páginas web a PDF preservando formato
- **Análisis inteligente con IA**: Usa OpenAI GPT para identificar y extraer oportunidades
- **Extracción estructurada**: Genera JSON con datos estructurados y documento Word formateado
- **Filtrado inteligente**: Prioriza contenido relevante y elimina duplicados
- **Pipeline completo**: Desde URL hasta reporte final en un solo proceso

## 🚀 Instalación

### Prerequisitos
- Python 3.8 o superior
- Cuenta de OpenAI con créditos ($5-10 USD recomendado)
- macOS, Linux o Windows

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/diegocabezas004/sistema_oportunidades
cd sistema-oportunidades
```

2. **Crear ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env y agregar tu API key de OpenAI
```

Tu archivo `.env` debe verse así:
```env
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-4-turbo-preview
LANGUAGE_OUTPUT=ES
CHUNK_SIZE=8000
CHUNK_OVERLAP=1000
```

## 💻 Uso

### Ejecutar el sistema
```bash
python main.py
```

### Opciones del menú

1. **Exportar URLs a PDF**: Convierte páginas web a PDF
2. **Procesar PDFs existentes**: Analiza PDFs en la carpeta
3. **Pipeline completo**: Ejecuta todo el proceso automáticamente
4. **Configuración**: Ver configuración actual
5. **Salir**

### Ejemplo de uso

```python
# URLs de ejemplo para El Salvador
urls = [
    "https://www.fomilenioii.gob.sv/convocatorias",
    "https://www.fusades.org/programas",
    "https://www.grants.gov/search-grants"
]
```

## 📁 Estructura del proyecto

```
sistema-oportunidades/
├── main.py                    # Script principal con menú interactivo
├── scripts/
│   ├── config.py             # Configuración (NO subir a git)
│   ├── webpage_print_to_pdf.py  # Módulo de exportación a PDF
│   └── funding_pdf_extractor.py # Módulo de análisis con IA
├── pdfs_entrada/             # PDFs para procesar
├── pdfs_salida/              # PDFs generados
├── resultados/               # JSON y DOCX de salida
├── .env                      # Variables de entorno (NO subir)
├── .env.example              # Plantilla de variables
├── requirements.txt          # Dependencias Python
└── README.md                 # Este archivo
```

## 🔧 Configuración

### Variables de entorno principales

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `OPENAI_API_KEY` | Tu API key de OpenAI | Requerido |
| `OPENAI_MODEL` | Modelo a usar | gpt-4-turbo-preview |
| `LANGUAGE_OUTPUT` | Idioma de salida | ES |
| `CHUNK_SIZE` | Tamaño de bloques de texto | 8000 |
| `KEEP_CLOSED` | Mantener convocatorias cerradas | False |

### Modelos disponibles
- `gpt-3.5-turbo`: Rápido y económico ($0.01-0.02 por PDF)
- `gpt-4-turbo-preview`: Más preciso ($0.10-0.20 por PDF)

## 📊 Salidas

El sistema genera dos archivos principales:

### 1. JSON estructurado (`oportunidades_resultados.json`)
```json
{
  "processing_date": "2024-01-15T10:30:00",
  "total_pdfs": 3,
  "total_opportunities": 5,
  "results": [...]
}
```

### 2. Documento Word (`resumen_oportunidades.docx`)
- Resumen ejecutivo
- Listado consolidado de oportunidades
- Análisis por documento
- Tablas formateadas

## 🐛 Solución de problemas

### Error: "Access Denied" al exportar PDFs
Algunos sitios tienen protección anti-bot. Soluciones:
- Usar `headless=False` en `webpage_print_to_pdf.py`
- Descargar manualmente y colocar en `pdfs_salida/`

### Error: "insufficient_quota"
No tienes créditos en OpenAI. Ve a https://platform.openai.com/account/billing

### Campos en null en el JSON
- Aumentar `CHUNK_SIZE` a 10000
- Cambiar a `gpt-4-turbo-preview` para mejor extracción
- Verificar que el PDF tenga texto (no sea imagen escaneada)

## 📝 Licencia

MIT License - Ver archivo LICENSE

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Diego Cabezas - diegocabezas72@gmail.com.com

## 👥 Colaboradores

- **Diego Cabezas** - [@diegocabezas004](https://github.com/diegocabezas004)
- **Nombre Colaborador** - [@alexitoc31](https://github.com/alexitoc31)

Link del proyecto: [https://github.com/diegocabezas004/sistema_oportunidades](https://github.com/diegocabezas004/sistema_oportunidades)

## 🙏 Agradecimientos

- OpenAI por la API de GPT
- Playwright por la automatización del navegador
- PDFMiner por la extracción de texto
- python-docx por la generación de documentos Word

---

**Nota**: Este sistema está diseñado para facilitar la búsqueda de oportunidades de financiamiento para la organización FES dentro de la ESEN.
```