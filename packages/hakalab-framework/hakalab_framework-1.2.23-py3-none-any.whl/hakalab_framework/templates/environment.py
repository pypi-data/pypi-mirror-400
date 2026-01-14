"""
Template de environment.py para hakalab-framework v1.1.20+
Enfoque simple y limpio - Sistema de screenshots independiente
SOLUCION: Allure eliminado completamente
Versiones soportadas:
- Playwright >= 1.57.0
- Behave >= 1.3.3  
"""

from hakalab_framework import (
    setup_framework_context,
    setup_scenario_context
)
from hakalab_framework.core.screenshot_manager import take_screenshot_on_failure, take_screenshot

# Importar steps directamente para que Behave los reconozca
from hakalab_framework.steps import *

def before_all(context):
    """Configuración inicial - El framework hace todo el trabajo"""
    try:
        # Limpiar archivos antiguos si está habilitado
        from hakalab_framework.core.screenshot_manager import cleanup_directories
        cleanup_directories()
        
        setup_framework_context(context)
    except Exception as e:
        print(f"Error en before_all: {e}")
        raise

def before_scenario(context, scenario):
    """Configuración por escenario - El framework maneja todo"""
    try:
        setup_scenario_context(context, scenario)
    except Exception as e:
        print(f"Error en before_scenario: {e}")
        raise

def after_step(context, step):
    """Capturar screenshot después de cada paso"""
    try:
        if hasattr(context, 'page') and context.page:
            # Generar nombre del screenshot basado en el paso
            step_name = step.name.replace(' ', '_').replace('"', '').replace("'", '')
            screenshot_name = f"step_{step.line}_{step_name[:50]}"
            
            # Capturar screenshot usando el framework
            take_screenshot(context, screenshot_name)
    except Exception as e:
        print(f"Error capturando screenshot en step: {e}")

def after_scenario(context, scenario):
    """Solo screenshot si falla - Enfoque simple"""
    try:
        take_screenshot_on_failure(context, scenario)
    except:
        pass
    
    # Cerrar página actual para liberar memoria
    try:
        if hasattr(context, 'page') and context.page:
            context.page.close()
            context.page = None
    except:
        pass

def after_all(context):
    """Cerrar Playwright y mostrar resumen"""
    # Cerrar Playwright
    try:
        if hasattr(context, 'framework_config') and context.framework_config:
            context.framework_config.cleanup()
            print("✅ Playwright cerrado correctamente")
    except Exception as e:
        print(f"❌ Error cerrando Playwright: {e}")
    
    # Mostrar resumen de screenshots
    try:
        from hakalab_framework.core.screenshot_manager import get_screenshots_summary
        summary = get_screenshots_summary()
        if summary["total"] > 0:
            print(f"📸 Screenshots generados: {summary['total']} total, {summary['failed']} fallos")
    except:
        pass