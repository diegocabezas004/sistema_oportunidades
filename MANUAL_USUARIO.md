# 📖 MANUAL DE USUARIO
## Sistema de Búsqueda de Oportunidades de Financiamiento

---

## 📑 ÍNDICE

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Guía de Uso por Pestaña](#guía-de-uso-por-pestaña)
4. [Flujos de Trabajo Comunes](#flujos-de-trabajo-comunes)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Solución de Problemas](#solución-de-problemas)
7. [Consejos y Mejores Prácticas](#consejos-y-mejores-prácticas)

---

## 🎯 INTRODUCCIÓN

### ¿Qué hace este sistema?

El Sistema de Búsqueda de Oportunidades de Financiamiento es una herramienta automatizada que:

- ✅ **Convierte páginas web a PDF** preservando su formato
- ✅ **Analiza documentos** usando Inteligencia Artificial (GPT-4)
- ✅ **Extrae información estructurada** de convocatorias, grants, becas y RFPs
- ✅ **Genera reportes profesionales** en JSON y Word
- ✅ **Filtra oportunidades** según criterios configurables

### ¿Para quién es este sistema?

- 🎓 Organizaciones que buscan financiamiento
- 💼 Equipos de desarrollo institucional
- 🔍 Profesionales de fundraising
- 📊 Investigadores que necesitan rastrear oportunidades

---

## 🚀 PRIMEROS PASOS

### Requisitos Previos

Antes de usar el sistema, asegúrate de tener:

1. ✅ Python 3.8 o superior instalado
2. ✅ API Key de OpenAI configurada
3. ✅ Ambiente virtual activado

### Configuración Inicial

#### 1. Activar el ambiente virtual

**macOS/Linux:**
```bash
cd sistema-oportunidades
source venv/bin/activate
```

**Windows:**
```bash
cd sistema-oportunidades
venv\Scripts\activate
```

#### 2. Verificar configuración

Antes de usar el sistema, verifica tu archivo `.env`:

```bash
cat .env
```

Debe contener:
```env
OPENAI_API_KEY=tu-api-key-real
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.3
LANGUAGE_OUTPUT=ES
CHUNK_SIZE=10000
CHUNK_OVERLAP=1500
MAX_CHUNKS_PER_DOC=15
```

⚠️ **IMPORTANTE**: Si tu `OPENAI_API_KEY` comienza con `sk-...` y tiene menos de 20 caracteres, NO es válida.

#### 3. Iniciar la aplicación

```bash
python gui_app.py
```

La interfaz gráfica se abrirá automáticamente.

---

## 🎨 GUÍA DE USO POR PESTAÑA

### 📄 PESTAÑA 1: Exportar URLs a PDF

**Propósito**: Convertir páginas web de convocatorias a documentos PDF.

#### Paso a paso:

1. **Ingresar URLs**
   - Pega las URLs en el área de texto (una por línea)
   - Ejemplo:
     ```
     https://www.grants.gov/search-grants
     https://procurement-notices.undp.org/view_notice.cfm?notice_id=12345
     https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home
     ```

2. **Opciones disponibles**
   - 🗑️ **Limpiar**: Borra todas las URLs ingresadas
   - 📥 **Cargar desde archivo**: Importa URLs desde un archivo `.txt`
   - 🚀 **Exportar a PDF**: Inicia la conversión

3. **Durante la exportación**
   - Verás una barra de progreso animada
   - La consola mostrará el progreso en tiempo real
   - Ejemplo de output:
     ```
     [10:30:15] 🚀 Iniciando exportación de 3 URLs...
     [10:30:16] 📄 Procesando 1/3: https://www.grants.gov/...
     [10:30:20] ✅ Guardado como: grants_gov_1.pdf
     ```

4. **Resultados**
   - Los PDFs se guardan en la carpeta configurada (ver pestaña Configuración)
   - Recibirás una notificación con el resumen
   - Ejemplo: "✅ 3 PDFs creados exitosamente, ❌ 0 errores"

#### ⚠️ Problemas comunes:

**Sitio con protección anti-bot:**
```
❌ Error: Acceso denegado - Protección anti-bot
💡 Solución: Descarga el PDF manualmente y colócalo en la carpeta pdfs_salida/
```

---

### 🤖 PESTAÑA 2: Analizar PDFs

**Propósito**: Extraer información estructurada de PDFs usando IA.

#### Paso a paso:

1. **Verificar PDFs disponibles**
   - El sistema muestra automáticamente cuántos PDFs detectó
   - Click en "🔄 Actualizar conteo" para refrescar
   - Click en "📂 Abrir carpeta" para ver los archivos

2. **Iniciar análisis**
   - Click en "🤖 Analizar con IA"
   - Confirma en el diálogo que aparece
   - La información mostrada incluye:
     - Número de PDFs a procesar
     - Modelo de IA que se usará
     - Advertencia sobre consumo de créditos

3. **Durante el análisis**
   - Observa la consola para ver el progreso detallado
   - Ejemplo de output:
     ```
     [10:45:00] 📄 [1/3] Procesando: convocatoria_undp.pdf
     [10:45:01]    📝 Texto extraído: 3606 caracteres
     [10:45:02]    🧹 Limpiando y estructurando...
     [10:45:03]    🔍 Extrayendo con regex...
     [10:45:03]    ✅ Regex encontró: ['deadline', 'contact', 'sponsor']
     [10:45:03]       🎯 Deadline regex: 2025-10-17
     [10:45:03]       🎯 Contact regex: email@undp.org
     [10:45:05]    🤖 Generando resumen...
     [10:45:08]    📦 Texto dividido en 1 bloques
     [10:45:10]       ✨ 'deadline' FORZADO desde regex: 2025-10-17
     [10:45:10]       ✨ 'contact' FORZADO desde regex: email@undp.org
     [10:45:10]    ✅ 1 oportunidades encontradas
     [10:45:10]       📊 Especialista Finanzas: 12/14 campos (85%)
     [10:45:10]          💰 Amount: A determinar
     [10:45:10]          📅 Deadline: 2025-10-17
     [10:45:10]          📧 Contact: email@undp.org
     ```

4. **Resultados**
   - Se generan dos archivos:
     - 📄 `oportunidades_resultados.json` - Datos estructurados
     - 📝 `resumen_oportunidades.docx` - Reporte formateado
   - Ubicación: carpeta de resultados configurada

#### 💡 Entendiendo el análisis:

**Extracción híbrida:**
El sistema usa dos métodos complementarios:

1. **Regex (Expresiones regulares)**
   - Busca patrones específicos: emails, fechas, números de referencia
   - Es rápido y preciso para datos estructurados
   - Ejemplo: `17-Oct-25 @ 01:59 AM` → `2025-10-17`

2. **GPT-4 (Inteligencia Artificial)**
   - Entiende contexto y semántica
   - Extrae información narrativa (elegibilidad, resumen, etc.)
   - Completa campos que regex no puede encontrar

**Indicadores de calidad:**
```
📊 Título de oportunidad: 12/14 campos (85%)
```
- `12/14`: 12 de 14 campos tienen información
- `85%`: Porcentaje de completitud
- ✅ Bueno: >70%
- ⚠️ Regular: 50-70%
- ❌ Pobre: <50%

---

### 🔄 PESTAÑA 3: Pipeline Completo

**Propósito**: Ejecutar todo el proceso automáticamente (URLs → PDFs → Análisis).

#### Cuándo usar esta pestaña:

- ✅ Tienes URLs nuevas que analizar
- ✅ Quieres automatizar todo el flujo
- ✅ No tienes PDFs existentes

#### Paso a paso:

1. **Ingresar URLs**
   - Igual que en la pestaña "Exportar URLs"
   - Puedes mezclar diferentes fuentes

2. **Ejecutar pipeline**
   - Click en "🚀 Ejecutar Pipeline Completo"
   - El sistema hará automáticamente:
     1. Exportar URLs → PDFs
     2. Analizar PDFs → Extraer información
     3. Generar reportes → JSON + DOCX

3. **Monitorear progreso**
   - El diagrama de flujo muestra la etapa actual
   - La consola muestra detalles en tiempo real
   - Ejemplo:
     ```
     [11:00:00] 🔄 PIPELINE INICIADO
     [11:00:01] [1/2] Exportando 2 URLs...
     [11:00:15] ✅ 2 PDFs creados
     [11:00:17] [2/2] Analizando con IA...
     [11:02:30] 🎉 PIPELINE COMPLETADO: 3 oportunidades
     ```

4. **Tiempo estimado**
   - Exportación: ~5-10 segundos por URL
   - Análisis: ~30-60 segundos por PDF
   - Total para 5 URLs: ~5-8 minutos

---

### 📊 PESTAÑA 4: Ver Resultados

**Propósito**: Visualizar y acceder a las oportunidades encontradas.

#### Componentes:

**1. Resumen Ejecutivo**
- Fecha de procesamiento
- Total de PDFs analizados
- Total de oportunidades encontradas
- Idioma utilizado
- Configuración de filtros

**2. Tabla de Oportunidades**
- Vista en árbol con todas las oportunidades
- Columnas:
  - `#`: Número secuencial
  - `Título`: Nombre de la convocatoria
  - `Fecha Límite`: Deadline en formato ISO
  - `Patrocinador`: Organización que financia
  - `Estado`: open/closed/unknown

**3. Botones de acción**
- 🔄 **Cargar**: Recarga resultados desde el JSON
- 📂 **Carpeta**: Abre la carpeta de resultados
- 📄 **JSON**: Abre el archivo JSON en tu navegador
- 📝 **DOCX**: Abre el documento Word

#### Interpretando los resultados:

**Archivo JSON** (`oportunidades_resultados.json`):
```json
{
  "processing_date": "2025-10-15T17:02:01",
  "total_pdfs": 3,
  "total_opportunities": 5,
  "language": "ES",
  "results": [
    {
      "filename": "convocatoria_undp.pdf",
      "opportunities": [
        {
          "title": "Especialista en Finanzas",
          "deadline": "2025-10-17",
          "contact": "email@undp.org",
          "amount": "A determinar",
          "status": "open"
        }
      ]
    }
  ]
}
```

**Documento Word** (`resumen_oportunidades.docx`):
- Resumen ejecutivo con métricas
- Listado completo de oportunidades con todos los detalles
- Análisis por documento procesado
- Formato profesional listo para compartir

---

### ⚙️ PESTAÑA 5: Configuración

**Propósito**: Ver y modificar la configuración del sistema.

#### Secciones:

**1. Configuración OpenAI**
- **API Key**: Estado (✅ Configurada / ❌ No configurada)
- **Modelo**: `gpt-4-turbo-preview` (recomendado) o `gpt-3.5-turbo`
- **Temperatura**: `0.3` (nivel de creatividad)

**2. Configuración de Procesamiento**
- **Idioma**: ES (Español) o EN (Inglés)
- **Tamaño chunk**: 10000 tokens (bloques de texto)
- **Overlap chunk**: 1500 tokens (solapamiento)
- **Max chunks/doc**: 15 (límite de bloques)
- **Mantener cerradas**: No (filtra convocatorias cerradas)
- **Max reintentos**: 3 (intentos ante errores)
- **Delay**: 1s (pausa entre llamadas API)

**3. 📁 Rutas del Sistema** (¡NUEVA FUNCIONALIDAD!)

Esta sección permite cambiar dónde se guardan los archivos:

#### Carpetas configurables:

1. **PDFs Entrada**
   - Carpeta para PDFs que quieras procesar
   - Por defecto: `pdfs_entrada/`
   
2. **PDFs Salida**
   - Carpeta donde se guardan PDFs exportados
   - Por defecto: `pdfs_salida/`
   
3. **Resultados**
   - Carpeta donde se guardan JSON y DOCX
   - Por defecto: `resultados/`

#### Cómo cambiar una carpeta:

1. Click en "📂 Cambiar" junto a la ruta deseada
2. Selecciona la nueva carpeta en el diálogo
3. Confirma el cambio
4. El sistema:
   - Guarda la nueva ruta en `user_config.json`
   - Actualiza todos los módulos
   - Crea la carpeta si no existe
   - Muestra confirmación en la consola

**Ejemplo de uso:**

Quieres guardar los resultados en tu Google Drive:

1. Click en "📂 Cambiar" en Resultados
2. Navega a: `/Users/tu-usuario/Google Drive/Oportunidades/`
3. Click "Seleccionar"
4. Confirma: "¿Cambiar la ruta de resultados a..."
5. ✅ Listo - próximos resultados irán ahí

#### Restaurar rutas por defecto:

Si quieres volver a la configuración original:

1. Click en "🔄 Restaurar rutas por defecto"
2. Confirma
3. Las rutas vuelven a:
   - `pdfs_entrada/`
   - `pdfs_salida/`
   - `resultados/`

**4. Botón de configuración avanzada**
- "📝 Editar configuración avanzada" abre `scripts/config.py`
- ⚠️ Solo para usuarios avanzados

---

## 🔄 FLUJOS DE TRABAJO COMUNES

### Flujo 1: Analizar URLs nuevas (más común)

```
1. Ir a pestaña "🔄 Pipeline"
2. Pegar URLs de convocatorias
3. Click "Ejecutar Pipeline"
4. Esperar 5-10 minutos
5. Ir a pestaña "📊 Resultados"
6. Click "Cargar" y revisar
```

**Tiempo total**: 5-10 minutos para 5 URLs

---

### Flujo 2: Analizar PDFs existentes

```
1. Colocar PDFs en carpeta pdfs_salida/
2. Ir a pestaña "🤖 Analizar PDFs"
3. Click "Actualizar conteo"
4. Click "Analizar con IA"
5. Esperar procesamiento
6. Ir a "📊 Resultados"
```

**Tiempo total**: 1-2 minutos por PDF

---

### Flujo 3: Solo descargar páginas web

```
1. Ir a pestaña "📄 Exportar URLs"
2. Pegar URLs
3. Click "Exportar a PDF"
4. Abrir carpeta para ver PDFs
```

**Tiempo total**: 30 segundos a 2 minutos

---

### Flujo 4: Cambiar ubicación de archivos

```
1. Ir a pestaña "⚙️ Configuración"
2. En "Rutas del Sistema"
3. Click "Cambiar" en la ruta deseada
4. Seleccionar nueva carpeta
5. Confirmar
```

**Ejemplo práctico**: Guardar en Google Drive para acceso desde cualquier dispositivo

---

## 📊 INTERPRETACIÓN DE RESULTADOS

### Campos extraídos

Cada oportunidad tiene hasta 14 campos:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `title` | Nombre de la convocatoria | "Especialista en Finanzas" |
| `summary` | Resumen de 2-4 líneas | "Convocatoria para especialista..." |
| `sponsor` | Organización financiadora | "UNDP", "World Bank" |
| `amount` | Monto disponible | "$50,000", "A determinar" |
| `currency` | Moneda | "USD", "EUR" |
| `deadline` | Fecha límite | "2025-10-17", "rolling" |
| `region` | Región geográfica | "América Latina", "Global" |
| `country` | País específico | "El Salvador", "Guatemala" |
| `eligibility` | Quién puede aplicar | "ONGs", "Universidades" |
| `link` | URL de la convocatoria | "http://..." |
| `contact` | Email de contacto | "email@undp.org" |
| `status` | Estado | "open", "closed", "unknown" |
| `source_file` | PDF de origen | "convocatoria.pdf" |
| `notes` | Notas adicionales | "Requiere cofinanciamiento" |

### Valores especiales

- `"A determinar"`: No se encontró monto específico
- `"unknown"`: No se pudo determinar el valor
- `"rolling"`: Sin fecha límite fija
- `"Global"`: Aplica a todos los países
- `null`: Campo sin información

### Indicadores de calidad

**Completitud por campo:**
```
📊 Título: 12/14 campos (85%)
   💰 Amount: A determinar
   📅 Deadline: 2025-10-17
   📧 Contact: email@undp.org
```

**Interpretación:**
- ✅ **85-100%**: Excelente - casi toda la info disponible
- ⚠️ **70-84%**: Bueno - info suficiente para evaluar
- ⚠️ **50-69%**: Regular - puede faltar info importante
- ❌ **<50%**: Pobre - considerar revisar PDF manualmente

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Problema 1: "API Key no configurada"

**Síntoma**: Mensaje de advertencia al abrir la app

**Solución**:
1. Abre el archivo `.env`
2. Reemplaza `OPENAI_API_KEY=sk-...` con tu clave real
3. La clave debe empezar con `sk-proj-` o `sk-`
4. Cierra y reabre la aplicación

**Cómo obtener una API Key**:
1. Ve a https://platform.openai.com/api-keys
2. Inicia sesión
3. Click "Create new secret key"
4. Copia la clave (empieza con `sk-`)
5. Pégala en `.env`

---

### Problema 2: Muchos campos en `null`

**Síntoma**: JSON con mayoría de campos vacíos

**Causas posibles**:
1. ❌ Usando `gpt-3.5-turbo` (modelo básico)
2. ❌ CHUNK_SIZE muy pequeño (< 6000)
3. ❌ PDF es imagen escaneada sin texto

**Soluciones**:

**Opción 1: Cambiar a GPT-4** (recomendado)
```env
# En .env
OPENAI_MODEL=gpt-4-turbo-preview
```

**Opción 2: Aumentar chunk size**
```env
# En .env
CHUNK_SIZE=15000
CHUNK_OVERLAP=2000
```

**Opción 3: Verificar PDF**
```bash
# Ejecutar diagnóstico
python test_pdf.py
```

Si el PDF tiene < 100 caracteres, es una imagen y necesitas OCR.

---

### Problema 3: "Access Denied" al exportar

**Síntoma**: Error al intentar exportar ciertas URLs

**Causa**: El sitio web tiene protección anti-bot

**Solución**:
1. Intenta con `headless=False` en el código
2. O descarga el PDF manualmente:
   - Abre la URL en tu navegador
   - Imprime → Guardar como PDF
   - Coloca el PDF en `pdfs_salida/`
   - Usa la pestaña "Analizar PDFs"

---

### Problema 4: "FileNotFoundError"

**Síntoma**: Error diciendo que no encuentra archivos

**Causa**: Las rutas de carpetas cambiaron

**Solución**:
1. Ve a "⚙️ Configuración"
2. Revisa las rutas mostradas
3. Click "Restaurar rutas por defecto"
4. O configura las rutas correctas con "Cambiar"

---

### Problema 5: Aplicación no abre

**Síntoma**: Al ejecutar `python gui_app.py` no pasa nada

**Soluciones**:

1. Verifica que el ambiente virtual esté activo:
```bash
which python  # macOS/Linux
where python  # Windows
```
Debe mostrar una ruta dentro de `venv/`

2. Reinstala dependencias:
```bash
pip install -r requirements.txt
```

3. Verifica errores:
```bash
python gui_app.py 2>&1 | tee error.log
```

---

## 💡 CONSEJOS Y MEJORES PRÁCTICAS

### Para obtener mejores resultados

**1. Calidad de las URLs**
- ✅ Usa URLs directas a la convocatoria
- ✅ Evita páginas de listado general
- ✅ URLs de UNDP, World Bank, EU suelen funcionar mejor
- ❌ Evita URLs con login requerido

**2. Configuración óptima**
```env
OPENAI_MODEL=gpt-4-turbo-preview  # Mejor calidad
CHUNK_SIZE=10000                   # Balance óptimo
CHUNK_OVERLAP=1500                 # Buen contexto
```

**3. Organización de archivos**
- Usa nombres descriptivos para PDFs
- Organiza por fecha o tema
- Ejemplo: `2025-10_UNDP_El-Salvador.pdf`

**4. Revisión de resultados**
- Siempre revisa el porcentaje de completitud
- Si < 70%, considera revisar el PDF manualmente
- Verifica especialmente deadline y contact

---

### Optimización de costos

**Costo por PDF:**
- GPT-3.5-turbo: $0.01-0.02 por PDF
- GPT-4-turbo: $0.10-0.20 por PDF

**Recomendaciones:**
1. Usa GPT-3.5 para pruebas iniciales
2. Cambia a GPT-4 para producción
3. Procesa en lotes para eficiencia
4. Revisa `CHUNK_SIZE` - más grande = menos llamadas

**Estimación de costos:**
- 10 PDFs con GPT-4: ~$1-2 USD
- 100 PDFs con GPT-4: ~$10-20 USD
- Presupuesto recomendado: $10-20 USD/mes

---

### Seguridad y privacidad

**Datos sensibles:**
- ✅ Tu API Key nunca se comparte
- ✅ PDFs se procesan localmente
- ✅ Solo el texto se envía a OpenAI
- ✅ OpenAI no almacena tu contenido (por política)

**Backups:**
- Haz backup de `user_config.json`
- Guarda tus resultados importantes
- Considera usar Google Drive para carpetas

---

### Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `Cmd+Q` / `Alt+F4` | Cerrar aplicación |
| `Cmd+W` | Cerrar ventana |
| `Tab` | Navegar entre campos |
| `Enter` | Confirmar diálogos |

---

## 📞 SOPORTE

### Recursos adicionales

- 📖 README.md - Información técnica
- 🐛 GitHub Issues - Reportar problemas
- 📧 Email: diegocabezas72@gmail.com

### Antes de reportar un problema

1. ✅ Revisa esta documentación
2. ✅ Verifica tu configuración (.env)
3. ✅ Ejecuta test_pdf.py para diagnóstico
4. ✅ Revisa la consola para errores
5. ✅ Intenta con un PDF diferente

---

## 📈 ACTUALIZACIONES

**Versión actual**: 1.0

**Changelog**:
- ✅ Interfaz gráfica completa
- ✅ Extracción híbrida (Regex + GPT)
- ✅ Configuración de rutas desde GUI
- ✅ Soporte para múltiples idiomas
- ✅ Mejora en detección de deadlines
- ✅ Valores por defecto inteligentes

---

**¿Listo para empezar?** 🚀

1. Verifica tu `.env`
2. Ejecuta `python gui_app.py`
3. Ve a "Pipeline" y pega tus URLs
4. ¡Deja que la IA haga el trabajo!