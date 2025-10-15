import sys
import time
from pathlib import Path
from typing import List, Optional

# Si no se pasan argumentos de línea de comandos, abrir GUI
if len(sys.argv) == 1:
    from gui_app import main as gui_main
    gui_main()
    sys.exit()

# El resto del código main.py original continúa...

# Añadir scripts al path
sys.path.append(str(Path(__file__).parent / "scripts"))

from webpage_print_to_pdf import export_urls
from funding_pdf_extractor import process_pdf_folder
from config import *

def print_banner():
    """Imprime banner del sistema"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║     SISTEMA DE BÚSQUEDA DE OPORTUNIDADES DE FINANCIAMIENTO      ║
║                    Versión 1.0 - Documento Técnico              ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def menu_principal():
    """Menú interactivo principal"""
    print("\n🎯 MENÚ PRINCIPAL")
    print("="*50)
    print("1. Exportar URLs a PDF")
    print("2. Procesar PDFs existentes")
    print("3. Pipeline completo (URLs → PDFs → Análisis)")
    print("4. Configuración")
    print("5. Salir")
    print("="*50)
    
    return input("\nSelecciona una opción (1-5): ").strip()

def obtener_urls() -> List[str]:
    """Obtiene URLs del usuario"""
    print("\n📝 INGRESO DE URLs")
    print("Ingresa las URLs (una por línea).")
    print("Escribe 'FIN' cuando termines:\n")
    
    urls = []
    while True:
        url = input("URL> ").strip()
        if url.upper() == 'FIN':
            break
        if url and (url.startswith('http://') or url.startswith('https://')):
            urls.append(url)
            print(f"   ✅ Añadida: {url[:50]}...")
        elif url:
            print("   ⚠️ URL inválida (debe empezar con http:// o https://)")
    
    return urls

def ejecutar_exportacion_urls():
    """Ejecuta módulo de exportación de URLs"""
    urls = obtener_urls()
    
    if not urls:
        print("\n❌ No se ingresaron URLs válidas")
        return
    
    print(f"\n🚀 Exportando {len(urls)} URLs a PDF...")
    print(f"📁 Carpeta de destino: {PDFS_SALIDA}\n")
    
    resultados = export_urls(urls)
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE EXPORTACIÓN:")
    print("="*50)
    exitosos = sum(1 for r in resultados if r['status'] == 'success')
    print(f"✅ Exitosos: {exitosos}/{len(urls)}")
    
    for r in resultados:
        if r['status'] == 'error':
            print(f"❌ Error en {r['url'][:30]}...: {r['message'][:50]}")

def ejecutar_procesamiento_pdfs():
    """Ejecuta módulo de procesamiento de PDFs"""
    # Verificar PDFs disponibles
    pdfs = list(PDFS_SALIDA.glob("*.pdf"))
    
    if not pdfs:
        print(f"\n❌ No hay PDFs en {PDFS_SALIDA}")
        print("   Primero debes exportar algunas URLs o colocar PDFs en la carpeta")
        return
    
    print(f"\n📚 Encontrados {len(pdfs)} PDFs para procesar")
    print("PDFs a analizar:")
    for i, pdf in enumerate(pdfs[:10], 1):  # Mostrar máximo 10
        print(f"   {i}. {pdf.name}")
    if len(pdfs) > 10:
        print(f"   ... y {len(pdfs)-10} más")
    
    confirmar = input("\n¿Proceder con el análisis? (s/n): ").strip().lower()
    
    if confirmar != 's':
        print("Análisis cancelado")
        return
    
    print(f"\n🤖 Iniciando análisis con OpenAI...")
    print(f"⚙️ Modelo: {OPENAI_MODEL}")
    print(f"🌍 Idioma de salida: {LANGUAGE_OUTPUT}")
    print(f"🔧 Filtrar cerradas: {'Sí' if not KEEP_CLOSED else 'No'}\n")
    
    # Ejecutar procesamiento
    resultado = process_pdf_folder()
    
    print("\n✨ ¡Análisis completado!")
    print(f"📂 Revisa los resultados en: {RESULTADOS}")

def pipeline_completo():
    """Ejecuta el pipeline completo"""
    print("\n🔄 PIPELINE COMPLETO")
    print("="*50)
    
    # Paso 1: Obtener URLs
    urls = obtener_urls()
    
    if not urls:
        print("\n❌ Pipeline cancelado: no se ingresaron URLs")
        return
    
    # Paso 2: Exportar a PDF
    print(f"\n[1/2] Exportando {len(urls)} URLs a PDF...")
    resultados_export = export_urls(urls)
    
    exitosos = sum(1 for r in resultados_export if r['status'] == 'success')
    if exitosos == 0:
        print("\n❌ Pipeline cancelado: no se pudo exportar ningún PDF")
        return
    
    print(f"✅ {exitosos} PDFs creados exitosamente")
    
    # Pequeña pausa
    time.sleep(2)
    
    # Paso 3: Procesar PDFs
    print(f"\n[2/2] Analizando PDFs con IA...")
    resultado = process_pdf_folder()
    
    print("\n🎉 ¡PIPELINE COMPLETADO!")
    print(f"📊 Total de oportunidades encontradas: {resultado.get('total_opportunities', 0)}")

def mostrar_configuracion():
    """Muestra la configuración actual"""
    print("\n⚙️ CONFIGURACIÓN ACTUAL")
    print("="*50)
    print(f"OpenAI API Key: {'✅ Configurada' if OPENAI_API_KEY != 'sk-...' else '❌ No configurada'}")
    print(f"Modelo: {OPENAI_MODEL}")
    print(f"Idioma de salida: {LANGUAGE_OUTPUT}")
    print(f"Mantener cerradas: {KEEP_CLOSED}")
    print(f"Chunk size: {CHUNK_SIZE} tokens")
    print(f"Chunk overlap: {CHUNK_OVERLAP} tokens")
    print(f"\nCarpetas:")
    print(f"  PDFs entrada: {PDFS_ENTRADA}")
    print(f"  PDFs salida: {PDFS_SALIDA}")
    print(f"  Resultados: {RESULTADOS}")
    
    input("\nPresiona Enter para continuar...")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar API Key
    if OPENAI_API_KEY == "sk-..." or len(OPENAI_API_KEY) < 20:
        print("⚠️ ADVERTENCIA: No has configurado tu API Key de OpenAI")
        print("   Edita scripts/config.py y añade tu clave")
        print("   Obtenla en: https://platform.openai.com/api-keys")
        return
    
    while True:
        opcion = menu_principal()
        
        if opcion == '1':
            ejecutar_exportacion_urls()
        elif opcion == '2':
            ejecutar_procesamiento_pdfs()
        elif opcion == '3':
            pipeline_completo()
        elif opcion == '4':
            mostrar_configuracion()
        elif opcion == '5':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción no válida")
        
        if opcion in ['1', '2', '3']:
            input("\nPresiona Enter para volver al menú...")

if __name__ == "__main__":
    main()