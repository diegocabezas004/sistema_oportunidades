# 🔍 Sistema de Búsqueda de Oportunidades de Financiamiento

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/diegocabezas004/sistema_oportunidades)

Sistema automatizado con **Interfaz Gráfica** para capturar, analizar y extraer oportunidades de financiamiento (convocatorias, grants, becas, RFPs) desde páginas web utilizando **Inteligencia Artificial**.

<img src="https://via.placeholder.com/800x400.png?text=Sistema+de+Oportunidades+Screenshot" alt="Screenshot">

---

## ✨ Características Principales

### 🎨 Interfaz Gráfica Profesional
- ✅ **5 pestañas organizadas** para cada funcionalidad
- ✅ **Responsive** - se adapta a cualquier tamaño de pantalla
- ✅ **Configuración visual** de rutas de carpetas
- ✅ **Consola integrada** con logs en tiempo real
- ✅ **Barras de progreso** para procesos largos

### 🤖 Extracción Inteligente con IA
- ✅ **Híbrido Regex + GPT-4** para máxima precisión
- ✅ **14 campos estructurados** por oportunidad
- ✅ **Extracción agresiva** de deadline y contact
- ✅ **Valores por defecto inteligentes** (no más nulls)
- ✅ **80-90% de completitud** de campos

### 📄 Procesamiento de Documentos
- ✅ **Exportación automática** de URLs a PDF
- ✅ **Anti-detección** para sitios protegidos
- ✅ **Extracción mejorada** con LAParams
- ✅ **Soporte multi-idioma** (ES/EN)

### 📊 Reportes Profesionales
- ✅ **JSON estructurado** con toda la data
- ✅ **Documento Word** formateado y listo para compartir
- ✅ **Métricas de completitud** por oportunidad
- ✅ **Deduplicación automática**

### 🎯 Configuración Flexible
- ✅ **Cambio de carpetas** desde la interfaz
- ✅ **Persistencia** de rutas personalizadas
- ✅ **Restauración rápida** a valores por defecto
- ✅ **Filtrado automático** de convocatorias cerradas

---

## 📋 Tabla de Contenidos

- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso Rápido](#-uso-rápido)
- [Documentación](#-documentación)
- [Arquitectura](#-arquitectura)
- [Campos Extraídos](#-campos-extraídos)
- [Costos](#-costos)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribuciones](#-contribuciones)
- [Licencia](#-licencia)

---

## 🚀 Instalación

### Prerequisitos

- **Python 3.8 o superior** ([Descargar](https://www.python.org/downloads/))
- **Cuenta de OpenAI** con créditos API ([Registrarse](https://platform.openai.com/signup))
- **Sistema operativo**: macOS, Linux o Windows

### Instalación Paso a Paso

#### 1. Clonar el repositorio

```bash
git clone https://github.com/diegocabezas004/sistema_oportunidades.git
cd sistema_oportunidades
```

#### 2. Crear ambiente virtual

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
playwright install chromium
```

#### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y agrega tu API key de OpenAI:

```env
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.3
LANGUAGE_OUTPUT=ES
CHUNK_SIZE=10000
CHUNK_OVERLAP=1500
MAX_CHUNKS_PER_DOC=15
```

**Obtener API Key:**
1. Ve a https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copia la clave (comienza con `sk-`)
4. Pégala en el archivo `.env`

---

## ⚙️ Configuración

### Configuración Recomendada

Para mejores resultados, usa esta configuración en tu `.env`:

```env
# API de OpenAI
OPENAI_API_KEY=sk-tu-api-key-real
OPENAI_MODEL=gpt-4-turbo-preview  # Mejor calidad (recomendado)
OPENAI_TEMPERATURE=0.3              # Balance creatividad/precisión

# Idioma
LANGUAGE_OUTPUT=ES                  # ES (Español) o EN (Inglés)

# Procesamiento
CHUNK_SIZE=10000                    # Bloques de texto grandes
CHUNK_OVERLAP=1500                  # Solapamiento entre bloques
MAX_CHUNKS_PER_DOC=15              # Máximo de bloques por PDF

# Filtros
KEEP_CLOSED=False                   # Filtrar convocatorias cerradas

# Límites
MAX_RETRIES=3                       # Reintentos ante errores
RATE_LIMIT_DELAY=1                  # Pausa entre llamadas (segundos)
PDF_TIMEOUT=60000                   # Timeout para PDFs (ms)
```

### Modelos Disponibles

| Modelo | Calidad | Velocidad | Costo/PDF | Recomendado para |
|--------|---------|-----------|-----------|------------------|
| `gpt-3.5-turbo` | ⭐⭐⭐ | Rápido | $0.01-0.02 | Pruebas |
| `gpt-4-turbo-preview` | ⭐⭐⭐⭐⭐ | Normal | $0.10-0.20 | Producción |

**Recomendación**: Usa `gpt-4-turbo-preview` para obtener 80-90% de completitud en los campos.

---

## 🎯 Uso Rápido

### Opción 1: Interfaz Gráfica (Recomendado)

```bash
python gui_app.py
```

La interfaz se abrirá automáticamente con 5 pestañas:

1. **📄 Exportar URLs** - Convierte páginas web a PDF
2. **🤖 Analizar PDFs** - Extrae información con IA
3. **🔄 Pipeline** - Proceso completo automatizado
4. **📊 Resultados** - Visualiza oportunidades encontradas
5. **⚙️ Configuración** - Ajusta rutas y parámetros

### Opción 2: Línea de Comandos

```bash
python main.py --console
```

Menú interactivo en terminal para usuarios avanzados.

### Ejemplo Básico - 3 Pasos

#### Paso 1: Pegar URLs

```
https://procurement-notices.undp.org/view_notice.cfm?notice_id=12345
https://www.grants.gov/web/grants/search-grants.html
https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home
```

#### Paso 2: Ejecutar Pipeline

Click en "🚀 Ejecutar Pipeline Completo"

#### Paso 3: Ver Resultados

Abre `resultados/oportunidades_resultados.json` o el `.docx`

**Tiempo total**: ~5-10 minutos para 5 URLs

---

## 📖 Documentación

### Documentación Completa

Para una guía detallada paso a paso, consulta:

📘 **[MANUAL_USUARIO.md](MANUAL_USUARIO.md)** - Guía completa de uso

Incluye:
- ✅ Tutorial paso a paso de cada pestaña
- ✅ Solución de problemas comunes
- ✅ Interpretación de resultados
- ✅ Consejos y mejores prácticas
- ✅ Ejemplos de uso real

### Guías Rápidas

**Analizar URLs nuevas:**
```
1. Ir a "Pipeline"
2. Pegar URLs
3. Click "Ejecutar Pipeline"
4. Ver resultados en "Resultados"
```

**Analizar PDFs existentes:**
```
1. Colocar PDFs en pdfs_salida/
2. Ir a "Analizar PDFs"
3. Click "Analizar con IA"
4. Ver resultados
```

**Cambiar ubicación de archivos:**
```
1. Ir a "Configuración"
2. En "Rutas del Sistema"
3. Click "Cambiar" en la ruta deseada
4. Seleccionar nueva carpeta
```

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
sistema-oportunidades/
├── 🎨 gui_app.py                    # Interfaz gráfica principal
├── 📟 main.py                       # CLI alternativa
├── 📁 scripts/
│   ├── config.py                    # Configuración dinámica
│   ├── webpage_print_to_pdf.py      # Exportador de URLs a PDF
│   └── funding_pdf_extractor.py     # Extractor con IA (híbrido)
├── 📂 pdfs_entrada/                 # PDFs para procesar (configurable)
├── 📂 pdfs_salida/                  # PDFs exportados (configurable)
├── 📂 resultados/                   # JSON y DOCX (configurable)
├── 🔧 .env                          # Variables de entorno
├── 📝 .env.example                  # Plantilla de configuración
├── 📦 requirements.txt              # Dependencias
├── 🔒 user_config.json              # Rutas personalizadas (auto-generado)
└── 📖 MANUAL_USUARIO.md             # Documentación completa

```

### Flujo de Datos

```
URLs → [Playwright] → PDFs → [PDFMiner] → Texto → 
[Regex] → Info estructurada → [GPT-4] → JSON → 
[python-docx] → DOCX
```

### Componentes Principales

#### 1. **Exportador de URLs** (`webpage_print_to_pdf.py`)
- Usa Playwright con navegador real
- Anti-detección para sitios protegidos
- Simula comportamiento humano (scroll, delays)
- Maneja cookies y banners automáticamente

#### 2. **Extractor Híbrido** (`funding_pdf_extractor.py`)
- **Fase 1 - Regex**: Extrae patrones obvios (emails, fechas, URLs)
- **Fase 2 - GPT-4**: Entiende contexto y semántica
- **Fase 3 - Fusión**: Combina resultados y fuerza valores críticos
- **Fase 4 - Validación**: Deduplicación y filtrado

#### 3. **Interfaz Gráfica** (`gui_app.py`)
- Framework: Tkinter (incluido en Python)
- Responsive design con grid system
- Multithreading para no bloquear UI
- Gestión dinámica de rutas
- Logs en tiempo real

---

## 📊 Campos Extraídos

Cada oportunidad contiene hasta **14 campos estructurados**:

### Campos Principales

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `title` | string | Título de la convocatoria | "Especialista en Finanzas Internacionales" |
| `summary` | string | Resumen de 2-4 líneas | "Convocatoria para especialista en finanzas..." |
| `sponsor` | string | Organización financiadora | "UNDP", "World Bank", "European Union" |
| `amount` | string | Monto disponible | "$50,000", "€100,000", "A determinar" |
| `currency` | string | Moneda | "USD", "EUR", "GBP" |
| `deadline` | string | Fecha límite (ISO 8601) | "2025-10-17", "rolling", "unknown" |

### Campos Geográficos

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `region` | string | Región geográfica | "América Latina", "Global", "África" |
| `country` | string | País específico | "El Salvador", "Guatemala" |

### Campos de Contacto

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `eligibility` | string | Quién puede aplicar | "ONGs", "Universidades", "Individuos" |
| `link` | string | URL de la convocatoria | "https://..." |
| `contact` | string | Email de contacto | "procurement@undp.org" |

### Campos Administrativos

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `status` | string | Estado de la convocatoria | "open", "closed", "unknown" |
| `source_file` | string | PDF de origen | "convocatoria_undp.pdf" |
| `notes` | string | Información adicional | "Requiere cofinanciamiento del 20%" |

### Valores Especiales

- `"A determinar"`: Monto no especificado en el documento
- `"unknown"`: No se pudo determinar el valor
- `"rolling"`: Convocatoria sin fecha límite fija
- `"Global"`: Aplicable a todos los países
- `null`: Sin información disponible (se minimiza con la versión actual)

---

## 💰 Costos

### Estimación de Costos por Modelo

#### GPT-3.5-turbo (Económico)
- **Por PDF**: $0.01 - $0.02 USD
- **100 PDFs**: ~$1 - $2 USD
- **Completitud**: 50-60% de campos

#### GPT-4-turbo-preview (Recomendado)
- **Por PDF**: $0.10 - $0.20 USD
- **100 PDFs**: ~$10 - $20 USD
- **Completitud**: 80-90% de campos

### Optimización de Costos

**1. Ajustar CHUNK_SIZE**
```env
CHUNK_SIZE=15000  # Más grande = menos llamadas API
```

**2. Usar caché**
- Los resultados se guardan en JSON
- No necesitas reprocesar PDFs

**3. Filtrar antes de procesar**
```env
KEEP_CLOSED=False  # Filtra convocatorias cerradas
```

**4. Batch processing**
- Procesa múltiples PDFs en una sesión
- Reduce overhead

### Presupuesto Recomendado

| Uso | PDFs/mes | Modelo | Costo estimado |
|-----|----------|--------|----------------|
| Pruebas | 10-20 | GPT-3.5 | $0.20 - $0.40 |
| Uso ligero | 50-100 | GPT-4 | $5 - $20 |
| Uso regular | 200-500 | GPT-4 | $20 - $100 |
| Uso intensivo | 1000+ | GPT-4 | $100+ |

---

## 🔧 Solución de Problemas

### Problema 1: Campos en `null`

**Síntomas**:
```json
{
  "deadline": null,
  "contact": null,
  "amount": null
}
```

**Diagnóstico**:
```bash
python test_pdf.py
```

**Soluciones**:

1. **Cambiar a GPT-4**:
```env
OPENAI_MODEL=gpt-4-turbo-preview
```

2. **Aumentar chunk size**:
```env
CHUNK_SIZE=15000
CHUNK_OVERLAP=2000
```

3. **Verificar que usas la versión correcta de `funding_pdf_extractor.py`**:
- Debe tener las funciones `extract_deadline_aggressive()` y `extract_contact_aggressive()`
- Debe incluir extracción híbrida (Regex + GPT)

---

### Problema 2: "Access Denied" al exportar URLs

**Causa**: El sitio web tiene protección anti-bot

**Solución Rápida**:
1. Descarga el PDF manualmente desde tu navegador
2. Guárdalo en la carpeta `pdfs_salida/`
3. Usa la pestaña "Analizar PDFs"

**Solución Técnica**:
Edita `webpage_print_to_pdf.py` línea 93:
```python
headless=False  # Cambia a True si quieres modo invisible
```

---

### Problema 3: "insufficient_quota" (Sin créditos)

**Causa**: No tienes créditos en tu cuenta de OpenAI

**Solución**:
1. Ve a https://platform.openai.com/account/billing
2. Añade un método de pago
3. Compra créditos ($5 mínimo recomendado)

---

### Problema 4: PDF es imagen (no se extrae texto)

**Diagnóstico**:
```bash
python test_pdf.py
# Si muestra < 100 caracteres, es una imagen
```

**Solución**:
Este sistema **NO incluye OCR**. Opciones:
1. Buscar una versión del PDF con texto
2. Usar herramientas OCR externas (Adobe Acrobat, Google Drive)
3. Solicitar el documento en formato editable

---

### Problema 5: Aplicación no abre

**Verificar ambiente virtual**:
```bash
which python  # macOS/Linux
where python  # Windows
# Debe mostrar ruta dentro de venv/
```

**Reinstalar dependencias**:
```bash
pip install --upgrade -r requirements.txt
playwright install chromium
```

**Ver errores detallados**:
```bash
python gui_app.py 2>&1 | tee error.log
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! 

### Cómo Contribuir

1. **Fork** el proyecto
2. Crea tu **feature branch**: `git checkout -b feature/NuevaCaracteristica`
3. **Commit** tus cambios: `git commit -m 'Añade nueva característica'`
4. **Push** al branch: `git push origin feature/NuevaCaracteristica`
5. Abre un **Pull Request**

### Áreas donde puedes contribuir

- 🐛 Reportar bugs
- 💡 Proponer nuevas funcionalidades
- 📝 Mejorar documentación
- 🌍 Traducciones
- 🧪 Casos de prueba
- 🎨 Mejoras de UI/UX

### Guidelines

- Sigue el estilo de código existente
- Documenta funciones nuevas
- Añade tests cuando sea posible
- Actualiza el README si es necesario

---

## 👥 Colaboradores

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/diegocabezas004">
        <img src="https://github.com/diegocabezas004.png" width="100px;" alt="Diego Cabezas"/><br />
        <sub><b>Diego Cabezas</b></sub>
      </a><br />
      💻 🎨 📖
    </td>
    <td align="center">
      <a href="https://github.com/alexitoc31">
        <img src="https://github.com/alexitoc31.png" width="100px;" alt="Colaborador"/><br />
        <sub><b>Alexito</b></sub>
      </a><br />
      💻 🤔
    </td>
  </tr>
</table>

---

## 📞 Soporte y Contacto

### Canales de Soporte

- 📧 **Email**: diegocabezas72@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/diegocabezas004/sistema_oportunidades/issues)
- 📖 **Documentación**: [MANUAL_USUARIO.md](MANUAL_USUARIO.md)

### Antes de Contactar

1. ✅ Revisa el [Manual de Usuario](MANUAL_USUARIO.md)
2. ✅ Busca en [Issues existentes](https://github.com/diegocabezas004/sistema_oportunidades/issues)
3. ✅ Ejecuta `test_pdf.py` para diagnóstico
4. ✅ Verifica tu configuración en `.env`

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 Diego Cabezas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Agradecimientos

Este proyecto no sería posible sin:

- **OpenAI** - Por la API de GPT-4
- **Playwright** - Automatización de navegadores
- **PDFMiner** - Extracción de texto de PDFs
- **python-docx** - Generación de documentos Word
- **Tkinter** - Framework de interfaz gráfica
- **La comunidad de desarrolladores** - Por sus contribuciones y feedback

---

## 🌟 Reconocimientos Especiales

- **FES (Fundación para la Educación Superior)** - Por el apoyo al proyecto
- **ESEN (Escuela Superior de Economía y Negocios)** - Por facilitar el desarrollo
- **Usuarios beta** - Por su retroalimentación invaluable

---

## 📈 Estadísticas del Proyecto

![GitHub stars](https://img.shields.io/github/stars/diegocabezas004/sistema_oportunidades?style=social)
![GitHub forks](https://img.shields.io/github/forks/diegocabezas004/sistema_oportunidades?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/diegocabezas004/sistema_oportunidades?style=social)

---

## 🚀 Roadmap

### Versión 1.1 (Próximamente)

- [ ] OCR integrado para PDFs escaneados
- [ ] Soporte para más idiomas (PT, FR)
- [ ] Exportación a Excel
- [ ] Base de datos SQLite
- [ ] API REST

### Versión 2.0 (Futuro)

- [ ] Dashboard web con Flask/Django
- [ ] Notificaciones automáticas
- [ ] Sistema de alertas por email
- [ ] Integración con calendarios
- [ ] Machine Learning para categorización

---

## 🎓 Casos de Uso

### Organizaciones sin fines de lucro
- Búsqueda automatizada de grants
- Seguimiento de convocatorias internacionales
- Base de datos de oportunidades

### Universidades
- Convocatorias de investigación
- Becas para estudiantes
- Programas de movilidad

### Empresas
- RFPs gubernamentales
- Licitaciones internacionales
- Oportunidades de financiamiento

### Consultores
- Servicio de búsqueda para clientes
- Análisis de mercado de financiamiento
- Reportes profesionales automatizados

---

## 📚 Recursos Adicionales

### Documentación Relacionada

- [Documentación OpenAI](https://platform.openai.com/docs)
- [Playwright Python](https://playwright.dev/python/)
- [PDFMiner Docs](https://pdfminersix.readthedocs.io/)

### Tutoriales

- [Video Tutorial: Instalación](enlace-pendiente)
- [Video Tutorial: Primer Uso](enlace-pendiente)
- [Webinar: Casos de Uso Avanzados](enlace-pendiente)

---

## 💡 FAQ

**P: ¿Funciona con cualquier PDF?**  
R: Sí, siempre que el PDF contenga texto extraíble. No funciona con PDFs escaneados sin OCR.

**P: ¿Puedo procesar 1000 PDFs de una vez?**  
R: Técnicamente sí, pero considera el costo (~$100-200 con GPT-4) y el tiempo (~8-16 horas).

**P: ¿Los datos son privados?**  
R: Sí. El procesamiento es local y solo el texto se envía a OpenAI (que no lo almacena por política).

**P: ¿Funciona sin internet?**  
R: No. Requiere conexión para la API de OpenAI y para exportar URLs.

**P: ¿Puedo usar otro modelo de IA?**  
R: Actualmente solo OpenAI. Estamos considerando añadir Claude y LLaMA en futuras versiones.

---

<div align="center">

**¿Listo para automatizar tu búsqueda de oportunidades?** 🚀

[⬇️ Descargar](https://github.com/diegocabezas004/sistema_oportunidades/archive/refs/heads/main.zip) | [📖 Documentación](MANUAL_USUARIO.md) | [🐛 Reportar Issue](https://github.com/diegocabezas004/sistema_oportunidades/issues)

---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub

Hecho con ❤️ para la comunidad de fundraising

</div>