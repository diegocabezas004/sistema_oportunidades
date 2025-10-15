# scripts/funding_pdf_extractor.py
"""
Módulo principal de extracción de oportunidades de financiamiento
CON SOPORTE PARA RUTAS DINÁMICAS
"""

import os
import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from openai import OpenAI
import sys
sys.path.append(str(Path(__file__).parent))

def get_config():
    """Obtiene la configuración actualizada"""
    import config
    import importlib
    importlib.reload(config)
    return config

# Inicializar cliente OpenAI al momento de uso
def get_openai_client():
    """Obtiene cliente OpenAI con config actualizada"""
    cfg = get_config()
    return OpenAI(api_key=cfg.OPENAI_API_KEY)

# PROMPT MAESTRO (sin cambios)
OPP_SYSTEM_PROMPT = """Eres un experto en análisis de documentos de OPORTUNIDADES DE FINANCIAMIENTO.

Tu tarea es extraer TODA la información disponible de convocatorias, grants, becas, RFPs, premios, etc.

IMPORTANTE - REGLAS DE EXTRACCIÓN:
1. **Busca activamente** información en TODO el texto, incluso si está separada o mal formateada
2. **Infiere información** del contexto cuando sea posible
3. **NO dejes campos en null** si hay alguna pista en el texto
4. Si encuentras información parcial, úsala (ejemplo: "Monto: variable" es mejor que null)

CAMPOS A EXTRAER (devuelve JSON):
{
  "opportunities": [
    {
      "title": "Título claro y descriptivo de la oportunidad",
      "summary": "Resumen de 2-4 líneas explicando QUÉ es y PARA QUÉ sirve",
      "sponsor": "Organización que patrocina (UNDP, World Bank, etc.) - busca nombres de organizaciones",
      "amount": "Cantidad de dinero (busca números con $ o USD o EUR) - si no hay monto específico pon 'Variable' o 'A determinar'",
      "currency": "USD, EUR, etc. - infiere del contexto si no está explícito",
      "deadline": "Fecha en formato ISO (YYYY-MM-DD) o 'rolling' o mes/año. Busca: 'fecha límite', 'deadline', 'closing date', 'hasta'",
      "region": "Región geográfica (América Latina, Global, África, etc.) - infiere del contexto",
      "country": "País específico si aplica - busca nombres de países",
      "eligibility": "Quiénes pueden aplicar (ONGs, universidades, individuos, etc.) - busca 'elegible', 'pueden participar', 'dirigido a'",
      "link": "URL si aparece en el texto - busca patrones http:// o www.",
      "contact": "Email o contacto - busca @ o 'contacto:' o 'email:'",
      "status": "Determina si está 'open' (abierta), 'closed' (cerrada) o 'unknown'. Busca palabras como 'abierta', 'cerrada', 'vigente', 'expirada'",
      "source_file": "Nombre del PDF (se llena automáticamente)",
      "notes": "Información adicional importante: cofinanciamiento requerido, etapas, restricciones especiales, etc."
    }
  ]
}

ESTRATEGIAS DE BÚSQUEDA:
- **Sponsor/Patrocinador**: Busca siglas (UNDP, USAID, EU, BID) o nombres de organizaciones en mayúsculas
- **Amount/Monto**: Busca números seguidos de: $, USD, EUR, dólares, euros, millones, mil
- **Deadline**: Busca fechas en cualquier formato: DD/MM/YYYY, Month Day Year, "30 de junio", "June 30"
- **Eligibility**: Busca frases como: "pueden aplicar", "dirigido a", "elegibles", "podrán participar"
- **Region**: Si menciona países de LATAM → "América Latina". Si dice "all countries" → "Global"
- **Contact**: Busca direcciones de email (palabra@dominio.com) o "para más información contactar"

CASOS ESPECIALES:
- Si el texto dice "monto variable" o "según propuesta" → amount: "Variable", NO null
- Si no hay fecha límite explícita pero dice "permanente" → deadline: "rolling"
- Si menciona varios países de la misma región → region: nombre de la región
- Si el documento es una lista de oportunidades → extrae CADA UNA por separado

CALIDAD > PERFECCIÓN:
- Es mejor tener "amount: Variable" que "amount: null"
- Es mejor "deadline: 2025" que "deadline: null"
- Es mejor "eligibility: Organizaciones sin fines de lucro" que "eligibility: null"

EXCLUYE:
- Noticias de proyectos ya finalizados
- Reseñas o reportes de resultados
- Convocatorias explícitamente cerradas (a menos que la configuración indique mantenerlas)

FORMATO DE SALIDA:
Devuelve SOLO el JSON, sin explicaciones adicionales. Si no hay oportunidades, devuelve {"opportunities": []}"""

def read_pdf_text(filepath: Path) -> str:
    """Lee y extrae texto de un PDF"""
    try:
        text = pdf_extract_text(str(filepath))
        if text:
            text = text.replace('\x0c', '\n')
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' {2,}', ' ', text)
            return text.strip()
        return ""
    except Exception as e:
        print(f"   ⚠️ Error leyendo PDF: {e}")
        return ""

def clean_and_structure_text(text: str) -> str:
    """
    Limpia y estructura mejor el texto para facilitar la extracción
    """
    if not text:
        return ""
    
    # Normalizar espacios y saltos de línea
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Identificar y marcar secciones importantes
    # Esto ayuda al modelo a entender la estructura
    
    # Marcar encabezados (palabras en mayúsculas)
    text = re.sub(r'\n([A-ZÁÉÍÓÚÑ\s]{5,})\n', r'\n\n=== \1 ===\n\n', text)
    
    # Marcar información de contacto
    text = re.sub(r'(contact[o]?[\s:])', r'\n📧 CONTACTO: ', text, flags=re.IGNORECASE)
    text = re.sub(r'(e-?mail[\s:])', r'\n📧 EMAIL: ', text, flags=re.IGNORECASE)
    
    # Marcar fechas límite
    text = re.sub(r'(deadline|fecha[\s]l[ií]mite|closing[\s]date)[\s:]*', r'\n📅 DEADLINE: ', text, flags=re.IGNORECASE)
    
    # Marcar montos
    text = re.sub(r'(\$\s*[\d,]+|\d+\s*(USD|EUR|dollars|dólares))', r'\n💰 MONTO: \1', text, flags=re.IGNORECASE)
    
    # Marcar elegibilidad
    text = re.sub(r'(eligib[lei]|pueden\s+aplicar|dirigido\s+a|podr[áa]n\s+participar)[\s:]*', r'\n👥 ELEGIBILIDAD: ', text, flags=re.IGNORECASE)
    
    # Marcar URLs
    text = re.sub(r'(https?://[^\s]+)', r'\n🔗 LINK: \1', text)
    
    return text

def extract_structured_info(text: str) -> Dict[str, str]:
    """
    Extrae información estructurada usando regex antes de enviar a GPT
    Esto ayuda a llenar campos que el modelo podría perder
    """
    info = {}
    
    # Extraer emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if emails:
        info['contact'] = emails[0]
    
    # Extraer URLs
    urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
    if urls:
        info['link'] = urls[0]
    
    # Extraer montos (con $, USD, EUR)
    amounts = re.findall(r'\$\s*[\d,]+(?:\.\d{2})?|[\d,]+\s*(?:USD|EUR|dollars|dólares|euros)', text, re.IGNORECASE)
    if amounts:
        info['amount'] = amounts[0].strip()
    
    # Extraer fechas en diferentes formatos
    dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{1,2},?\s+\d{4}', text, re.IGNORECASE)
    if dates:
        info['deadline'] = dates[0]
    
    # Extraer organizaciones conocidas
    orgs = re.findall(r'\b(UNDP|UNICEF|World Bank|IDB|BID|USAID|EU|European Union|ONU|UNESCO|FAO|WHO|OMS|IOM|OIM)\b', text, re.IGNORECASE)
    if orgs:
        info['sponsor'] = orgs[0].upper()
    
    return info

# MODIFICAR la función extract_opportunities_from_text
# Reemplazar con esta versión mejorada:

def extract_opportunities_from_text(text: str, filename: str) -> Tuple[List[Dict], str]:
    """
    Procesa texto completo - VERSIÓN MEJORADA
    """
    if not text:
        return [], "Documento vacío."
    
    cfg = get_config()
    client = get_openai_client()
    
    print(f"   📝 Texto original: {len(text)} caracteres")
    
    # NUEVO: Limpiar y estructurar el texto
    print(f"   🧹 Limpiando y estructurando texto...")
    text = clean_and_structure_text(text)
    
    # NUEVO: Extraer información estructurada con regex
    print(f"   🔍 Extrayendo información estructurada...")
    structured_info = extract_structured_info(text)
    if structured_info:
        print(f"   ✅ Info encontrada por regex: {list(structured_info.keys())}")
    
    print(f"   🤖 Generando resumen...")
    summary = call_summary(text, filename, client, cfg)
    
    print(f"   🔍 Aplicando filtro de keywords...")
    focused_text = keyword_focus(text, cfg.KEYWORDS)
    
    chunks = chunk_text(focused_text, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP, cfg.MAX_CHUNKS_PER_DOC)
    print(f"   📦 {len(chunks)} bloques para análisis")
    
    all_opportunities = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"   🔄 Analizando bloque {i}/{len(chunks)}...")
        
        result = call_json_extract(chunk, filename, client, cfg)
        opportunities = result.get("opportunities", [])
        
        # NUEVO: Completar campos vacíos con info extraída por regex
        for opp in opportunities:
            opp["source_file"] = filename
            
            # Si GPT no encontró el campo pero regex sí, úsalo
            for key, value in structured_info.items():
                if not opp.get(key) or opp.get(key) == "null":
                    opp[key] = value
                    print(f"      ✨ Campo '{key}' completado con regex: {value[:50]}")
        
        all_opportunities.extend(opportunities)
        
        if i < len(chunks):
            time.sleep(cfg.RATE_LIMIT_DELAY)
    
    all_opportunities = dedupe_opportunities(all_opportunities)
    
    if not cfg.KEEP_CLOSED:
        all_opportunities = [
            opp for opp in all_opportunities
            if opp.get("status", "unknown").lower() != "closed"
        ]
    
    print(f"   ✅ {len(all_opportunities)} oportunidades únicas encontradas")
    
    # Mostrar resumen de campos completados
    for opp in all_opportunities:
        filled_fields = sum(1 for v in opp.values() if v and v != "null")
        total_fields = len(opp)
        print(f"      📊 {opp.get('title', 'Sin título')[:40]}: {filled_fields}/{total_fields} campos llenos")
    
    return all_opportunities, summary

def keyword_focus(text: str, keywords: List[str]) -> str:
    """Prioriza párrafos con palabras clave"""
    if not text:
        return ""
    
    paragraphs = re.split(r'\n{2,}', text)
    relevant_paras = []
    other_paras = []
    
    for para in paragraphs:
        para_lower = para.lower()
        if any(kw.lower() in para_lower for kw in keywords):
            relevant_paras.append(para)
        else:
            other_paras.append(para)
    
    if relevant_paras:
        focused_text = '\n\n'.join(relevant_paras)
        cfg = get_config()
        if len(focused_text) < cfg.CHUNK_SIZE * 3:
            focused_text += '\n\n' + '\n\n'.join(other_paras[:5])
        return focused_text
    
    return text

def chunk_text(text: str, chunk_size: int, overlap: int, max_chunks: int) -> List[str]:
    """Divide texto en chunks"""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    if len(words) <= chunk_size:
        return [text]
    
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        
        if end >= len(words):
            break
            
        start = end - overlap
    
    return chunks[:max_chunks]

def call_summary(text: str, filename: str, client: OpenAI, cfg) -> str:
    """Genera resumen del documento"""
    if not text:
        return "No se pudo extraer texto del documento."
    
    words = text.split()[:2000]
    text_limited = ' '.join(words)
    
    prompt = f"""Resume este documento en 120-180 palabras en {cfg.LANGUAGE_OUTPUT}.
Destaca: tema principal, propósito, y si contiene oportunidades de financiamiento.

Archivo: {filename}

Texto:
{text_limited}"""
    
    try:
        response = client.chat.completions.create(
            model=cfg.OPENAI_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de documentos."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generando resumen: {str(e)}"

def call_json_extract(text_chunk: str, filename: str, client: OpenAI, cfg) -> Dict:
    """Extrae oportunidades en JSON"""
    if not text_chunk:
        return {"opportunities": []}
    
    user_prompt = f"""Idioma de salida: {cfg.LANGUAGE_OUTPUT}
Archivo: {filename}

Esquema JSON esperado:
{{
  "opportunities": [
    {{
      "title": "string",
      "summary": "string",
      "sponsor": "string|null",
      "amount": "string|null",
      "currency": "string|null",
      "deadline": "string|null",
      "region": "string|null",
      "country": "string|null",
      "eligibility": "string|null",
      "link": "string|null",
      "contact": "string|null",
      "status": "open"|"closed"|"unknown",
      "source_file": "string|null",
      "notes": "string|null"
    }}
  ]
}}

TEXTO:
{text_chunk}"""
    
    for attempt in range(cfg.MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=cfg.OPENAI_MODEL,
                temperature=cfg.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": OPP_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if "opportunities" in result and isinstance(result["opportunities"], list):
                return result
            else:
                return {"opportunities": []}
                
        except json.JSONDecodeError:
            if attempt == cfg.MAX_RETRIES - 1:
                print(f"   ⚠️ Error parseando JSON")
                return {"opportunities": []}
        except Exception as e:
            if attempt == cfg.MAX_RETRIES - 1:
                print(f"   ⚠️ Error en API: {str(e)}")
                return {"opportunities": []}
        
        time.sleep(cfg.RATE_LIMIT_DELAY)
    
    return {"opportunities": []}

def dedupe_opportunities(items: List[Dict]) -> List[Dict]:
    """Elimina duplicados"""
    seen: Set[str] = set()
    deduped = []
    
    for item in items:
        title = item.get("title", "").strip().lower()
        deadline = str(item.get("deadline", "")).strip()
        
        key = f"{title}|{deadline}"
        
        if key not in seen and title:
            seen.add(key)
            deduped.append(item)
    
    return deduped

def extract_opportunities_from_text(text: str, filename: str) -> Tuple[List[Dict], str]:
    """Procesa texto completo"""
    if not text:
        return [], "Documento vacío."
    
    cfg = get_config()
    client = get_openai_client()
    
    print(f"   📝 Texto: {len(text)} caracteres")
    
    print(f"   🤖 Generando resumen...")
    summary = call_summary(text, filename, client, cfg)
    
    print(f"   🔍 Aplicando filtro...")
    focused_text = keyword_focus(text, cfg.KEYWORDS)
    
    chunks = chunk_text(focused_text, cfg.CHUNK_SIZE, cfg.CHUNK_OVERLAP, cfg.MAX_CHUNKS_PER_DOC)
    print(f"   📦 {len(chunks)} bloques")
    
    all_opportunities = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"   🔄 Analizando bloque {i}/{len(chunks)}...")
        
        result = call_json_extract(chunk, filename, client, cfg)
        opportunities = result.get("opportunities", [])
        
        for opp in opportunities:
            opp["source_file"] = filename
        
        all_opportunities.extend(opportunities)
        
        if i < len(chunks):
            time.sleep(cfg.RATE_LIMIT_DELAY)
    
    all_opportunities = dedupe_opportunities(all_opportunities)
    
    if not cfg.KEEP_CLOSED:
        all_opportunities = [
            opp for opp in all_opportunities
            if opp.get("status", "unknown").lower() != "closed"
        ]
    
    print(f"   ✅ {len(all_opportunities)} oportunidades únicas")
    
    return all_opportunities, summary

def process_pdf_folder(
    input_folder: Path = None,
    output_folder: Path = None
) -> Dict:
    """
    Procesa todos los PDFs - AHORA CON RUTAS DINÁMICAS
    """
    # Obtener rutas actualizadas
    cfg = get_config()
    
    if input_folder is None:
        input_folder = cfg.PDFS_SALIDA
    if output_folder is None:
        output_folder = cfg.RESULTADOS
    
    print(f"\n📁 Carpeta de PDFs: {input_folder}")
    print(f"📁 Carpeta de resultados: {output_folder}")
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(input_folder.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No se encontraron PDFs")
        return {"error": "No PDFs found"}
    
    print(f"\n{'='*70}")
    print(f"📚 PROCESANDO {len(pdf_files)} PDFs")
    print(f"{'='*70}")
    
    all_results = []
    all_opportunities = []
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 [{idx}/{len(pdf_files)}] {pdf_path.name}")
        print(f"   {'-'*60}")
        
        text = read_pdf_text(pdf_path)
        
        if not text:
            print(f"   ⚠️ No se pudo extraer texto")
            all_results.append({
                "filename": pdf_path.name,
                "summary": "No se pudo extraer texto del PDF",
                "opportunities_count": 0,
                "opportunities": []
            })
            continue
        
        opportunities, summary = extract_opportunities_from_text(text, pdf_path.name)
        
        result = {
            "filename": pdf_path.name,
            "summary": summary,
            "opportunities_count": len(opportunities),
            "opportunities": opportunities
        }
        
        all_results.append(result)
        all_opportunities.extend(opportunities)
        
        print(f"\n   📋 RESUMEN:")
        for line in summary.split('\n'):
            print(f"   {line}")
        
        if opportunities:
            print(f"\n   💰 OPORTUNIDADES: {len(opportunities)}")
            for i, opp in enumerate(opportunities[:3], 1):
                print(f"   {i}. {opp.get('title', 'Sin título')}")
                if opp.get('deadline'):
                    print(f"      Deadline: {opp['deadline']}")
    
    # Guardar JSON
    json_output = {
        "processing_date": datetime.now().isoformat(),
        "total_pdfs": len(pdf_files),
        "total_opportunities": len(all_opportunities),
        "language": cfg.LANGUAGE_OUTPUT,
        "keep_closed": cfg.KEEP_CLOSED,
        "results": all_results
    }
    
    json_path = output_folder / "oportunidades_resultados.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    
    # Crear DOCX
    docx_path = create_opportunities_docx(all_results, all_opportunities, output_folder)
    
    print(f"\n{'='*70}")
    print(f"✅ COMPLETADO")
    print(f"{'='*70}")
    print(f"   • PDFs: {len(pdf_files)}")
    print(f"   • Oportunidades: {len(all_opportunities)}")
    print(f"   • JSON: {json_path}")
    print(f"   • DOCX: {docx_path}")
    
    return json_output

def create_opportunities_docx(
    results: List[Dict],
    all_opportunities: List[Dict],
    output_folder: Path
) -> Path:
    """Crea documento Word (sin cambios en la lógica)"""
    doc = Document()
    
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    
    title = doc.add_heading('REPORTE DE OPORTUNIDADES DE FINANCIAMIENTO', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph(f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    cfg = get_config()
    doc.add_paragraph(f'Idioma: {"Español" if cfg.LANGUAGE_OUTPUT == "ES" else "English"}')
    doc.add_paragraph()
    
    doc.add_heading('RESUMEN EJECUTIVO', 1)
    
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Métrica'
    hdr_cells[1].text = 'Valor'
    
    metrics = [
        ('Documentos analizados', str(len(results))),
        ('Oportunidades identificadas', str(len(all_opportunities))),
        ('Oportunidades abiertas', str(sum(1 for o in all_opportunities if o.get('status') == 'open'))),
        ('Oportunidades con deadline', str(sum(1 for o in all_opportunities if o.get('deadline'))))
    ]
    
    for metric, value in metrics:
        row = table.add_row()
        row.cells[0].text = metric
        row.cells[1].text = value
    
    doc.add_page_break()
    
    if all_opportunities:
        doc.add_heading('TODAS LAS OPORTUNIDADES', 1)
        
        for i, opp in enumerate(all_opportunities, 1):
            p = doc.add_paragraph()
            runner = p.add_run(f"{i}. {opp.get('title', 'Sin título')}")
            runner.bold = True
            runner.font.size = Pt(12)
            
            detail_table = doc.add_table(rows=0, cols=2)
            detail_table.style = 'Table Grid'
            
            fields = [
                ('Resumen', opp.get('summary')),
                ('Patrocinador', opp.get('sponsor')),
                ('Monto', f"{opp.get('amount', '')} {opp.get('currency', '')}".strip() if opp.get('amount') else None),
                ('Fecha límite', opp.get('deadline')),
                ('Región', opp.get('region')),
                ('País', opp.get('country')),
                ('Elegibilidad', opp.get('eligibility')),
                ('Enlace', opp.get('link')),
                ('Contacto', opp.get('contact')),
                ('Estado', opp.get('status')),
                ('Archivo', opp.get('source_file')),
                ('Notas', opp.get('notes'))
            ]
            
            for label, value in fields:
                if value and str(value).strip():
                    row = detail_table.add_row()
                    row.cells[0].text = label
                    row.cells[0].paragraphs[0].runs[0].bold = True
                    row.cells[0].width = Inches(2)
                    row.cells[1].text = str(value)
                    row.cells[1].width = Inches(4.5)
            
            doc.add_paragraph()
        
        doc.add_page_break()
    
    doc.add_heading('ANÁLISIS POR DOCUMENTO', 1)
    
    for result in results:
        doc.add_heading(f"📄 {result['filename']}", 2)
        
        doc.add_heading('Resumen:', 3)
        doc.add_paragraph(result['summary'])
        
        if result['opportunities_count'] > 0:
            doc.add_heading(f"Oportunidades ({result['opportunities_count']})", 3)
            
            for opp in result['opportunities']:
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(opp.get('title', 'Sin título')).bold = True
                if opp.get('deadline'):
                    p.add_run(f" - Deadline: {opp['deadline']}")
        else:
            doc.add_paragraph("No se encontraron oportunidades.", style='Intense Quote')
        
        doc.add_paragraph()
    
    docx_path = output_folder / "resumen_oportunidades.docx"
    doc.save(str(docx_path))
    
    return docx_path

if __name__ == "__main__":
    process_pdf_folder()