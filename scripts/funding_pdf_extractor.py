# scripts/funding_pdf_extractor.py
"""
Módulo principal de extracción de oportunidades de financiamiento
Implementación completa según documento técnico
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
from config import *

# Inicializar cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# PROMPT MAESTRO PARA OPORTUNIDADES (del documento original)
OPP_SYSTEM_PROMPT = """Eres un experto en análisis de documentos para identificar OPORTUNIDADES DE FINANCIAMIENTO reales.
Devuelve EXCLUSIVAMENTE un JSON con el campo "opportunities": lista de objetos. Cada objeto debe tener:
- title (string, claro y breve)
- summary (string, 2-4 líneas con lo esencial)
- sponsor (string o null)
- amount (string o null) y currency (string o null) si corresponde
- deadline (string ISO-8601 o "rolling" o null). Si solo hay mes/año, devuelve esa precisión.
- region (string o null), country (string o null)
- eligibility (string o null) - quién puede postular
- link (string o null) - si hay URL específica de la convocatoria
- contact (string o null)
- status ("open" | "closed" | "unknown")
- source_file (string o null) - el nombre del archivo que analizas
- notes (string o null) - aclaraciones importantes (ej. cofinanciamiento, etapa, etc.)

REGLAS:
1) Incluye solo oportunidades "para aplicar" (convocatorias, becas, grants, RFP, premios). Excluye noticias, reseñas o proyectos ya adjudicados.
2) No inventes datos. Si un campo no existe, usa null.
3) Si hay múltiples oportunidades en un mismo PDF, devuélvelas todas.
4) Si no hay oportunidades, devuelve "opportunities": [].
5) Sé muy estricto con el JSON (sin texto adicional)."""

def read_pdf_text(filepath: Path) -> str:
    """
    Lee y extrae texto de un PDF con normalización
    """
    try:
        text = pdf_extract_text(str(filepath))
        if text:
            # Normalizar saltos de página
            text = text.replace('\x0c', '\n')
            # Eliminar espacios excesivos
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' {2,}', ' ', text)
            return text.strip()
        return ""
    except Exception as e:
        print(f"   ⚠️ Error leyendo PDF: {e}")
        return ""

def keyword_focus(text: str, keywords: List[str] = KEYWORDS) -> str:
    """
    Prioriza párrafos con palabras clave de oportunidades
    """
    if not text:
        return ""
    
    # Dividir en párrafos
    paragraphs = re.split(r'\n{2,}', text)
    
    # Buscar párrafos con keywords
    relevant_paras = []
    other_paras = []
    
    for para in paragraphs:
        para_lower = para.lower()
        if any(kw.lower() in para_lower for kw in keywords):
            relevant_paras.append(para)
        else:
            other_paras.append(para)
    
    # Combinar: primero relevantes, luego contexto
    if relevant_paras:
        focused_text = '\n\n'.join(relevant_paras)
        # Añadir algo de contexto si hay espacio
        if len(focused_text) < CHUNK_SIZE * 3:
            focused_text += '\n\n' + '\n\n'.join(other_paras[:5])
        return focused_text
    
    return text

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, 
               overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Divide texto en chunks con solapamiento
    """
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
    
    return chunks[:MAX_CHUNKS_PER_DOC]

def call_summary(text: str, filename: str = "documento.pdf") -> str:
    """
    Genera resumen conciso del documento (120-180 palabras)
    """
    if not text:
        return "No se pudo extraer texto del documento."
    
    # Limitar texto para resumen
    words = text.split()[:2000]
    text_limited = ' '.join(words)
    
    prompt = f"""Resume este documento en 120-180 palabras en {LANGUAGE_OUTPUT}.
Destaca: tema principal, propósito, y si contiene oportunidades de financiamiento.
Sé conciso y directo.

Archivo: {filename}

Texto:
{text_limited}"""
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": "Eres un experto en análisis y resumen de documentos."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generando resumen: {str(e)}"

def call_json_extract(text_chunk: str, filename: str = "documento.pdf") -> Dict:
    """
    Extrae oportunidades en formato JSON estructurado
    """
    if not text_chunk:
        return {"opportunities": []}
    
    # Construir prompt de usuario según plantilla del documento
    user_prompt = f"""Idioma de salida: {LANGUAGE_OUTPUT}
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

TEXTO (puede venir por bloques):
{text_chunk}"""
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": OPP_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validar estructura
            if "opportunities" in result and isinstance(result["opportunities"], list):
                return result
            else:
                return {"opportunities": []}
                
        except json.JSONDecodeError:
            if attempt == MAX_RETRIES - 1:
                print(f"   ⚠️ Error parseando JSON después de {MAX_RETRIES} intentos")
                return {"opportunities": []}
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                print(f"   ⚠️ Error en API: {str(e)}")
                return {"opportunities": []}
        
        time.sleep(RATE_LIMIT_DELAY)
    
    return {"opportunities": []}

def dedupe_opportunities(items: List[Dict]) -> List[Dict]:
    """
    Elimina duplicados basándose en title|deadline
    """
    seen: Set[str] = set()
    deduped = []
    
    for item in items:
        title = item.get("title", "").strip().lower()
        deadline = str(item.get("deadline", "")).strip()
        
        # Crear clave única
        key = f"{title}|{deadline}"
        
        if key not in seen and title:
            seen.add(key)
            deduped.append(item)
    
    return deduped

def extract_opportunities_from_text(text: str, filename: str) -> Tuple[List[Dict], str]:
    """
    Procesa texto completo: resumen + extracción de oportunidades
    """
    if not text:
        return [], "Documento vacío o no se pudo extraer texto."
    
    print(f"   📝 Texto extraído: {len(text)} caracteres")
    
    # Generar resumen
    print(f"   🤖 Generando resumen...")
    summary = call_summary(text, filename)
    
    # Aplicar keyword focus
    print(f"   🔍 Aplicando filtro de palabras clave...")
    focused_text = keyword_focus(text)
    
    # Dividir en chunks
    chunks = chunk_text(focused_text)
    print(f"   📦 Dividido en {len(chunks)} bloques para análisis")
    
    # Extraer oportunidades de cada chunk
    all_opportunities = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"   🔄 Analizando bloque {i}/{len(chunks)}...")
        
        result = call_json_extract(chunk, filename)
        opportunities = result.get("opportunities", [])
        
        # Añadir source_file a cada oportunidad
        for opp in opportunities:
            opp["source_file"] = filename
        
        all_opportunities.extend(opportunities)
        
        # Rate limiting
        if i < len(chunks):
            time.sleep(RATE_LIMIT_DELAY)
    
    # Deduplicar
    all_opportunities = dedupe_opportunities(all_opportunities)
    
    # Filtrar cerradas si está configurado
    if not KEEP_CLOSED:
        all_opportunities = [
            opp for opp in all_opportunities
            if opp.get("status", "unknown").lower() != "closed"
        ]
    
    print(f"   ✅ Encontradas {len(all_opportunities)} oportunidades únicas")
    
    return all_opportunities, summary

def process_pdf_folder(
    input_folder: Path = PDFS_SALIDA,
    output_folder: Path = RESULTADOS
) -> Dict:
    """
    Procesa todos los PDFs en una carpeta
    """
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Buscar PDFs
    pdf_files = list(input_folder.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No se encontraron PDFs en la carpeta")
        return {"error": "No PDFs found"}
    
    print(f"\n{'='*70}")
    print(f"📚 PROCESANDO {len(pdf_files)} PDFs")
    print(f"{'='*70}")
    
    all_results = []
    all_opportunities = []
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 [{idx}/{len(pdf_files)}] Procesando: {pdf_path.name}")
        print(f"   {'-'*60}")
        
        # Leer PDF
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
        
        # Extraer oportunidades y resumen
        opportunities, summary = extract_opportunities_from_text(text, pdf_path.name)
        
        # Guardar resultado
        result = {
            "filename": pdf_path.name,
            "summary": summary,
            "opportunities_count": len(opportunities),
            "opportunities": opportunities
        }
        
        all_results.append(result)
        all_opportunities.extend(opportunities)
        
        # Mostrar resumen en consola
        print(f"\n   📋 RESUMEN:")
        for line in summary.split('\n'):
            print(f"   {line}")
        
        if opportunities:
            print(f"\n   💰 OPORTUNIDADES ENCONTRADAS: {len(opportunities)}")
            for i, opp in enumerate(opportunities[:3], 1):  # Mostrar máx 3
                print(f"   {i}. {opp.get('title', 'Sin título')}")
                if opp.get('deadline'):
                    print(f"      Deadline: {opp['deadline']}")
    
    # Guardar JSON consolidado
    json_output = {
        "processing_date": datetime.now().isoformat(),
        "total_pdfs": len(pdf_files),
        "total_opportunities": len(all_opportunities),
        "language": LANGUAGE_OUTPUT,
        "keep_closed": KEEP_CLOSED,
        "results": all_results
    }
    
    json_path = output_folder / "oportunidades_resultados.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    
    # Crear DOCX
    docx_path = create_opportunities_docx(all_results, all_opportunities, output_folder)
    
    print(f"\n{'='*70}")
    print(f"✅ PROCESO COMPLETADO")
    print(f"{'='*70}")
    print(f"📊 Resumen final:")
    print(f"   • PDFs procesados: {len(pdf_files)}")
    print(f"   • Oportunidades encontradas: {len(all_opportunities)}")
    print(f"   • JSON guardado en: {json_path}")
    print(f"   • DOCX guardado en: {docx_path}")
    
    return json_output

def create_opportunities_docx(
    results: List[Dict],
    all_opportunities: List[Dict],
    output_folder: Path
) -> Path:
    """
    Crea documento Word profesional con los resultados
    """
    doc = Document()
    
    # Configurar estilos del documento
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    
    # Título principal
    title = doc.add_heading('REPORTE DE OPORTUNIDADES DE FINANCIAMIENTO', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Metadata
    doc.add_paragraph(f'Fecha de generación: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    doc.add_paragraph(f'Idioma: {"Español" if LANGUAGE_OUTPUT == "ES" else "English"}')
    doc.add_paragraph()
    
    # Resumen ejecutivo
    doc.add_heading('RESUMEN EJECUTIVO', 1)
    
    # Tabla de resumen
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Headers
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Métrica'
    hdr_cells[1].text = 'Valor'
    
    # Datos
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
    
    # Listado consolidado de oportunidades
    if all_opportunities:
        doc.add_heading('TODAS LAS OPORTUNIDADES', 1)
        
        for i, opp in enumerate(all_opportunities, 1):
            # Título de la oportunidad
            p = doc.add_paragraph()
            runner = p.add_run(f"{i}. {opp.get('title', 'Sin título')}")
            runner.bold = True
            runner.font.size = Pt(12)
            
            # Crear tabla para detalles
            detail_table = doc.add_table(rows=0, cols=2)
            detail_table.style = 'Table Grid'
            
            # Añadir campos si existen
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
                ('Archivo fuente', opp.get('source_file')),
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
            
            doc.add_paragraph()  # Espacio entre oportunidades
        
        doc.add_page_break()
    
    # Análisis por documento
    doc.add_heading('ANÁLISIS POR DOCUMENTO', 1)
    
    for result in results:
        # Título del documento
        doc.add_heading(f"📄 {result['filename']}", 2)
        
        # Resumen
        doc.add_heading('Resumen del contenido:', 3)
        doc.add_paragraph(result['summary'])
        
        # Oportunidades del documento
        if result['opportunities_count'] > 0:
            doc.add_heading(f"Oportunidades encontradas ({result['opportunities_count']})", 3)
            
            for opp in result['opportunities']:
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(opp.get('title', 'Sin título')).bold = True
                if opp.get('deadline'):
                    p.add_run(f" - Deadline: {opp['deadline']}")
        else:
            doc.add_paragraph("No se encontraron oportunidades en este documento.", style='Intense Quote')
        
        doc.add_paragraph()  # Espacio entre documentos
    
    # Guardar documento
    docx_path = output_folder / "resumen_oportunidades.docx"
    doc.save(str(docx_path))
    
    return docx_path

if __name__ == "__main__":
    # Ejecutar procesamiento
    process_pdf_folder()