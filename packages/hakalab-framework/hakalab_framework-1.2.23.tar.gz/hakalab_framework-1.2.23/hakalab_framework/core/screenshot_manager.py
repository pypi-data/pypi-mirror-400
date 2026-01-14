#!/usr/bin/env python3
"""
Gestor de screenshots para el framework Hakalab
Reemplaza la funcionalidad de Allure con un sistema independiente
"""
import os
import re
from pathlib import Path
from datetime import datetime

def clean_filename(filename: str, max_length: int = 50) -> str:
    """
    Limpia un nombre de archivo removiendo caracteres inválidos para Windows
    """
    # Caracteres inválidos en Windows: < > : " | ? * \ /
    invalid_chars = r'[<>:"|?*\\/]'
    
    # Reemplazar caracteres inválidos con guión bajo
    clean_name = re.sub(invalid_chars, '_', filename)
    
    # Reemplazar espacios con guión bajo
    clean_name = clean_name.replace(' ', '_')
    
    # Remover múltiples guiones bajos consecutivos
    clean_name = re.sub(r'_+', '_', clean_name)
    
    # Remover guiones bajos al inicio y final
    clean_name = clean_name.strip('_')
    
    # Limitar longitud
    if len(clean_name) > max_length:
        clean_name = clean_name[:max_length].rstrip('_')
    
    return clean_name

def take_screenshot(context, screenshot_name="screenshot"):
    """
    Toma screenshot con nombre personalizado y alta calidad
    """
    if hasattr(context, 'page') and context.page:
        try:
            # Obtener directorio de screenshots desde variables de entorno
            screenshots_dir_name = os.getenv('SCREENSHOTS_DIR', 'screenshots')
            screenshots_dir = Path(screenshots_dir_name)
            screenshots_dir.mkdir(exist_ok=True)
            
            # Limpiar nombre del archivo
            clean_name = screenshot_name.replace(' ', '_').replace(':', '_').replace('/', '_')
            timestamp = datetime.now().strftime("%H%M%S")
            screenshot_path = screenshots_dir / f"{clean_name}_{timestamp}.png"
            
            # Opciones para screenshot de alta calidad
            full_page = os.getenv('SCREENSHOT_FULL_PAGE', 'true').lower() == 'true'
            screenshot_options = {
                'path': str(screenshot_path),
                'full_page': full_page,  # Configurable: página completa o solo viewport
                'type': 'png',
                'quality': None  # PNG no usa quality, pero está disponible para JPEG
            }
            
            context.page.screenshot(**screenshot_options)
            print(f"📸 Screenshot guardado: {screenshot_path}")
            
            return str(screenshot_path)
            
        except Exception as e:
            print(f"❌ Error tomando screenshot: {e}")
            return None

def take_screenshot_on_failure(context, scenario):
    """
    Toma screenshot solo si el escenario falla con alta calidad
    """
    if scenario.status == "failed" and hasattr(context, 'page') and context.page:
        try:
            # Obtener directorio de screenshots desde variables de entorno
            screenshots_dir_name = os.getenv('SCREENSHOTS_DIR', 'screenshots')
            screenshots_dir = Path(screenshots_dir_name)
            screenshots_dir.mkdir(exist_ok=True)
            
            scenario_name = scenario.name.replace(' ', '_').replace(':', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = screenshots_dir / f"FAILED_{scenario_name}_{timestamp}.png"
            
            # Opciones para screenshot de alta calidad
            full_page = os.getenv('SCREENSHOT_FULL_PAGE', 'true').lower() == 'true'
            screenshot_options = {
                'path': str(screenshot_path),
                'full_page': full_page,  # Configurable: página completa o solo viewport
                'type': 'png'
            }
            
            context.page.screenshot(**screenshot_options)
            print(f"📸 Screenshot de fallo guardado: {screenshot_path}")
            
            return str(screenshot_path)
            
        except Exception as e:
            print(f"❌ Error tomando screenshot de fallo: {e}")
            return None

def take_step_screenshot(context, step):
    """
    Toma screenshot de un step específico
    """
    if hasattr(context, 'page') and context.page:
        try:
            # Obtener directorio de screenshots desde variables de entorno
            screenshots_dir_name = os.getenv('SCREENSHOTS_DIR', 'screenshots')
            screenshots_dir = Path(screenshots_dir_name)
            screenshots_dir.mkdir(exist_ok=True)
            
            step_name = step.name.replace(' ', '_').replace('"', '').replace("'", '')[:50]
            timestamp = datetime.now().strftime("%H%M%S")
            screenshot_path = screenshots_dir / f"step_{step.line}_{step_name}_{timestamp}.png"
            
            context.page.screenshot(path=str(screenshot_path))
            print(f"📸 Screenshot de step guardado: {screenshot_path}")
            
            return str(screenshot_path)
            
        except Exception as e:
            print(f"❌ Error tomando screenshot de step: {e}")
            return None

def cleanup_directories():
    """
    Limpia los directorios de screenshots, reportes HTML y JSON si está habilitado
    """
    try:
        cleanup_enabled = os.getenv('CLEANUP_OLD_FILES', 'false').lower() == 'true'
        
        if not cleanup_enabled:
            return
        
        # Configuración de limpieza
        cleanup_mode = os.getenv('CLEANUP_MODE', 'all').lower()
        max_age_hours = int(os.getenv('CLEANUP_MAX_AGE_HOURS', '24'))
        
        # Directorios a limpiar
        screenshots_dir = Path(os.getenv('SCREENSHOTS_DIR', 'screenshots'))
        html_reports_dir = Path(os.getenv('HTML_REPORTS_DIR', 'html-reports'))
        
        cleaned_files = 0
        
        # Calcular tiempo límite para archivos antiguos
        if cleanup_mode == 'old':
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cutoff_timestamp = cutoff_time.timestamp()
        
        # Limpiar screenshots (PNG)
        if screenshots_dir.exists():
            for file in screenshots_dir.glob("*.png"):
                try:
                    should_delete = False
                    
                    if cleanup_mode == 'all':
                        should_delete = True
                    elif cleanup_mode == 'old':
                        should_delete = file.stat().st_mtime < cutoff_timestamp
                    
                    if should_delete:
                        file.unlink()
                        cleaned_files += 1
                        
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar {file}: {e}")
        
        # Limpiar reportes HTML
        if html_reports_dir.exists():
            for file in html_reports_dir.glob("*.html"):
                try:
                    should_delete = False
                    
                    if cleanup_mode == 'all':
                        should_delete = True
                    elif cleanup_mode == 'old':
                        should_delete = file.stat().st_mtime < cutoff_timestamp
                    
                    if should_delete:
                        file.unlink()
                        cleaned_files += 1
                        
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar {file}: {e}")
        
        # Limpiar reportes JSON
        if html_reports_dir.exists():
            for file in html_reports_dir.glob("*.json"):
                try:
                    should_delete = False
                    
                    if cleanup_mode == 'all':
                        should_delete = True
                    elif cleanup_mode == 'old':
                        should_delete = file.stat().st_mtime < cutoff_timestamp
                    
                    if should_delete:
                        file.unlink()
                        cleaned_files += 1
                        
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar {file}: {e}")
        
        if cleaned_files > 0:
            mode_text = "todos los archivos" if cleanup_mode == 'all' else f"archivos antiguos (>{max_age_hours}h)"
            print(f"🧹 Limpiados {cleaned_files} {mode_text} (screenshots, reportes HTML y JSON)")
        
    except Exception as e:
        print(f"⚠️ Error durante limpieza automática: {e}")

def cleanup_old_screenshots(max_age_hours=24):
    """
    Limpia screenshots antiguos para evitar acumulación
    """
    try:
        # Obtener directorio de screenshots desde variables de entorno
        screenshots_dir_name = os.getenv('SCREENSHOTS_DIR', 'screenshots')
        screenshots_dir = Path(screenshots_dir_name)
        if not screenshots_dir.exists():
            return
        
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        deleted_count = 0
        for screenshot_file in screenshots_dir.glob("*.png"):
            if screenshot_file.stat().st_mtime < cutoff_time.timestamp():
                screenshot_file.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"🧹 Limpiados {deleted_count} screenshots antiguos")
            
    except Exception as e:
        print(f"⚠️ Error limpiando screenshots: {e}")

def get_screenshots_summary():
    """
    Obtiene un resumen de los screenshots disponibles
    """
    try:
        # Obtener directorio de screenshots desde variables de entorno
        screenshots_dir_name = os.getenv('SCREENSHOTS_DIR', 'screenshots')
        screenshots_dir = Path(screenshots_dir_name)
        if not screenshots_dir.exists():
            return {"total": 0, "failed": 0, "steps": 0}
        
        screenshots = list(screenshots_dir.glob("*.png"))
        failed_screenshots = [s for s in screenshots if "FAILED_" in s.name]
        step_screenshots = [s for s in screenshots if "step_" in s.name]
        
        return {
            "total": len(screenshots),
            "failed": len(failed_screenshots),
            "steps": len(step_screenshots),
            "other": len(screenshots) - len(failed_screenshots) - len(step_screenshots)
        }
        
    except Exception as e:
        print(f"⚠️ Error obteniendo resumen de screenshots: {e}")
        return {"total": 0, "failed": 0, "steps": 0}