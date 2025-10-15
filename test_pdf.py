# test_pdf.py
from pdfminer.high_level import extract_text
from pathlib import Path
import json

# Leer la ruta real desde user_config.json
with open('user_config.json', 'r') as f:
    config = json.load(f)

pdfs_salida = Path(config['pdfs_salida'])

# Listar PDFs disponibles
print("📁 PDFs disponibles:")
pdfs = list(pdfs_salida.glob("*.pdf"))
for i, pdf in enumerate(pdfs, 1):
    print(f"   {i}. {pdf.name}")

if not pdfs:
    print("❌ No hay PDFs en la carpeta configurada")
    print(f"   Carpeta: {pdfs_salida}")
    exit(1)

# Usar el primer PDF
pdf_path = pdfs[0]

print(f"\n{'='*70}")
print(f"ANALIZANDO: {pdf_path.name}")
print('='*70)

text = extract_text(str(pdf_path))

print(f"\n📊 Caracteres: {len(text)}")
print(f"\n📄 PRIMEROS 3000 CARACTERES:\n")
print(text[:3000])

# Buscar info clave
print(f"\n{'='*70}")
print("🔍 BUSCANDO INFO CRÍTICA:")
print('='*70)

keywords = {
    "DEADLINE": ["deadline", "17-oct", "01:59"],
    "CONTACT": ["adquisiciones", "@undp.org", "email"],
    "REFERENCE": ["UNDP-SLV-00470", "reference number"],
    "SPONSOR": ["UNDP", "united nations"],
    "COUNTRY": ["el salvador", "salvador"]
}

for category, terms in keywords.items():
    print(f"\n{category}:")
    for term in terms:
        count = text.lower().count(term.lower())
        if count > 0:
            print(f"   ✅ '{term}': {count} veces")
            # Mostrar contexto
            idx = text.lower().find(term.lower())
            if idx >= 0:
                context = text[max(0, idx-50):min(len(text), idx+100)]
                print(f"      Contexto: ...{context}...")
        else:
            print(f"   ❌ '{term}': NO ENCONTRADO")

# Buscar emails
import re
emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
if emails:
    print(f"\n📧 EMAILS ENCONTRADOS ({len(emails)}):")
    for email in emails:
        print(f"   • {email}")
else:
    print(f"\n📧 NO SE ENCONTRARON EMAILS")

# Buscar fechas
dates = re.findall(r'\d{1,2}[-/]\w{3}[-/]\d{2,4}', text)
if dates:
    print(f"\n📅 FECHAS ENCONTRADAS ({len(dates)}):")
    for date in dates[:5]:
        print(f"   • {date}")
else:
    print(f"\n📅 NO SE ENCONTRARON FECHAS")

print(f"\n{'='*70}")
print("DIAGNÓSTICO COMPLETO")
print('='*70)

if len(text) < 100:
    print("❌ PROBLEMA CRÍTICO: Texto muy corto")
    print("   El PDF puede ser imagen o estar corrupto")
elif len(emails) == 0:
    print("⚠️ ADVERTENCIA: No se encontraron emails")
    print("   El PDF puede tener formato complejo")
elif "deadline" not in text.lower():
    print("⚠️ ADVERTENCIA: No se encontró la palabra 'deadline'")
    print("   Puede estar en imagen o formato especial")
else:
    print("✅ El texto parece extraerse correctamente")
    print(f"   {len(emails)} emails encontrados")
    print(f"   {len(dates)} fechas encontradas")