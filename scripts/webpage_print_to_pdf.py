# scripts/webpage_print_to_pdf.py
"""
Módulo para exportar páginas web a PDF usando Playwright
Versión mejorada con anti-detección
"""

import re
import asyncio
import random
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
import sys
sys.path.append(str(Path(__file__).parent))
from config import PDF_CONFIG, PDFS_SALIDA

def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    Limpia texto para usarlo como nombre de archivo seguro
    """
    # Eliminar caracteres no válidos
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    # Recortar y limpiar
    text = text.strip()[:max_length]
    return text or "documento"

def parse_margins(margin_str: str) -> Dict[str, str]:
    """
    Parsea string de márgenes a diccionario
    Ej: "1cm" -> {"top": "1cm", "bottom": "1cm", ...}
    """
    if isinstance(margin_str, dict):
        return margin_str
    return {
        "top": margin_str,
        "bottom": margin_str,
        "left": margin_str,
        "right": margin_str
    }

async def filename_from_title(page, index: int) -> str:
    """
    Genera nombre de archivo desde el título de la página
    """
    try:
        title = await page.title()
        filename = sanitize_filename(title)
        return f"{filename}_{index}"
    except:
        return f"documento_{index}"

async def print_urls_to_pdf(
    urls: List[str],
    output_dir: Path = PDFS_SALIDA,
    paper: str = PDF_CONFIG["paper"],
    landscape: bool = PDF_CONFIG["landscape"],
    print_background: bool = PDF_CONFIG["print_background"],
    margin: str = "1cm",
    scale: float = PDF_CONFIG["scale"],
    timeout: int = 60000,  # Aumentado a 60 segundos
    wait_after_load: int = 5000,  # Aumentado a 5 segundos
    handle_cookies: bool = True
) -> List[Dict]:
    """
    Exporta lista de URLs a PDFs con configuración anti-detección mejorada
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    margin_dict = parse_margins(margin)
    results = []
    
    # Sitios problemáticos conocidos con configuración especial
    PROBLEMATIC_SITES = {
        'undp.org': {'wait_time': 8000, 'needs_scroll': True},
        'unicef.org': {'wait_time': 8000, 'needs_scroll': True},
        'iom.int': {'wait_time': 7000, 'needs_scroll': True},
        'glasswing.org': {'wait_time': 6000, 'needs_scroll': True}
    }
    
    async with async_playwright() as p:
        # CAMBIO IMPORTANTE: headless=False para ver qué pasa
        # Cambia a True cuando funcione bien
        browser = await p.chromium.launch(
            headless=False,  # CAMBIADO: Navegador visible para debugging
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Contexto con configuración más realista
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            # User agent actualizado y realista para Mac
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='es-ES',
            timezone_id='America/El_Salvador',
            # Añadir permisos como navegador real
            permissions=['geolocation', 'notifications'],
            # Fingir que aceptamos idiomas
            extra_http_headers={
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
        )
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"\n📄 Procesando {i}/{len(urls)}: {url}")
                
                # Delay aleatorio entre páginas para parecer humano
                if i > 1:
                    delay = random.uniform(3, 7)
                    print(f"   ⏳ Esperando {delay:.1f}s antes de continuar...")
                    await asyncio.sleep(delay)
                
                page = await context.new_page()
                
                # Configurar la página antes de navegar
                await page.set_extra_http_headers({
                    'Accept-Language': 'es-ES,es;q=0.9',
                })
                
                # Verificar si es sitio problemático
                site_config = None
                for domain, config in PROBLEMATIC_SITES.items():
                    if domain in url:
                        site_config = config
                        print(f"   ⚠️ Sitio conocido como problemático, aplicando configuración especial...")
                        break
                
                # Navegar a la URL con estrategia más conservadora
                print(f"   ⏳ Cargando página...")
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                except:
                    # Si falla, intentar con networkidle
                    await page.goto(url, wait_until="networkidle", timeout=timeout)
                
                # Esperar tiempo específico según el sitio
                wait_time = site_config['wait_time'] if site_config else wait_after_load
                print(f"   ⏳ Esperando {wait_time/1000}s para carga completa...")
                await page.wait_for_timeout(wait_time)
                
                # Manejar cookies/banners
                if handle_cookies:
                    print(f"   🍪 Buscando banners de cookies...")
                    try:
                        cookie_selectors = [
                            'button:has-text("Accept")',
                            'button:has-text("Aceptar")',
                            'button:has-text("OK")',
                            'button:has-text("Agree")',
                            'button:has-text("Acepto")',
                            'button:has-text("Entendido")',
                            '[id*="accept"]',
                            '[class*="accept"]',
                            '[class*="cookie"] button',
                            '[class*="consent"] button'
                        ]
                        
                        for selector in cookie_selectors:
                            try:
                                if await page.locator(selector).first.is_visible(timeout=1000):
                                    await page.locator(selector).first.click()
                                    print(f"   ✅ Banner de cookies cerrado")
                                    await page.wait_for_timeout(1000)
                                    break
                            except:
                                continue
                    except:
                        pass
                
                # Simular comportamiento humano con scroll
                if not site_config or site_config.get('needs_scroll', False):
                    print(f"   🖱️ Simulando scroll humano...")
                    await page.evaluate('''
                        async () => {
                            const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
                            
                            // Scroll suave hacia abajo
                            const totalHeight = document.body.scrollHeight;
                            const viewportHeight = window.innerHeight;
                            let currentPosition = 0;
                            
                            while (currentPosition < totalHeight) {
                                const scrollStep = Math.min(viewportHeight * 0.8, totalHeight - currentPosition);
                                window.scrollTo({
                                    top: currentPosition + scrollStep,
                                    behavior: 'smooth'
                                });
                                currentPosition += scrollStep;
                                await delay(500 + Math.random() * 500);
                            }
                            
                            // Volver arriba
                            await delay(1000);
                            window.scrollTo({top: 0, behavior: 'smooth'});
                            await delay(1000);
                        }
                    ''')
                
                # Generar nombre de archivo
                filename = await filename_from_title(page, i)
                filepath = output_dir / f"{filename}.pdf"
                
                # Configurar para impresión
                await page.emulate_media(media="print")
                
                # Pequeña pausa antes de generar PDF
                await page.wait_for_timeout(2000)
                
                # Exportar a PDF
                print(f"   📝 Generando PDF...")
                await page.pdf(
                    path=str(filepath),
                    format=paper,
                    print_background=print_background,
                    landscape=landscape,
                    margin=margin_dict,
                    prefer_css_page_size=PDF_CONFIG["prefer_css_page_size"],
                    scale=scale
                )
                
                await page.close()
                
                results.append({
                    "url": url,
                    "filename": filepath.name,
                    "filepath": str(filepath),
                    "status": "success",
                    "message": f"PDF guardado: {filepath.name}"
                })
                
                print(f"   ✅ Guardado como: {filepath.name}")
                
            except Exception as e:
                error_msg = str(e)[:200]
                
                # Mensajes de error más informativos
                if "Access Denied" in error_msg:
                    error_msg = "Acceso denegado - El sitio tiene protección anti-bot"
                elif "timeout" in error_msg.lower():
                    error_msg = "Timeout - El sitio tardó demasiado en responder"
                
                results.append({
                    "url": url,
                    "filename": None,
                    "filepath": None,
                    "status": "error",
                    "message": error_msg
                })
                print(f"   ❌ Error: {error_msg}")
                
                # Si es error de acceso, sugerir alternativa
                if "Access Denied" in str(e) or "403" in str(e):
                    print(f"   💡 Sugerencia: Descarga este PDF manualmente y colócalo en pdfs_salida/")
        
        await browser.close()
    
    return results

def export_urls(urls: List[str], **kwargs) -> List[Dict]:
    """
    Función wrapper para ejecutar exportación desde código síncrono
    """
    return asyncio.run(print_urls_to_pdf(urls, **kwargs))

if __name__ == "__main__":
    # URLs de prueba
    urls_test = [
        "https://www.grants.gov",
        "https://www.gob.mx/conacyt",
        "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home"
    ]
    
    print("🚀 Iniciando exportación de prueba con configuración anti-detección...")
    print("📌 Nota: El navegador se abrirá visiblemente para debugging")
    print("   Puedes cambiar headless=False a True cuando funcione bien\n")
    
    resultados = export_urls(urls_test)
    
    print("\n📊 Resumen de resultados:")
    for r in resultados:
        status = "✅" if r["status"] == "success" else "❌"
        print(f"{status} {r['url'][:50]}... -> {r.get('filename', 'ERROR')}")
        if r["status"] == "error":
            print(f"   Razón: {r['message']}")