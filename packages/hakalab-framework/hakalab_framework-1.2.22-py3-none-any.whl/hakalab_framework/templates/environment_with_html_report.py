"""
Template de environment.py para hakalab-framework v1.1.20+
CON REPORTE HTML PERSONALIZADO
Incluye gráficos, screenshots y organización por features
"""

from hakalab_framework import (
    setup_framework_context,
    setup_scenario_context
)
from hakalab_framework.core.screenshot_manager import take_screenshot_on_failure, take_screenshot
from hakalab_framework.core.behave_html_integration import (
    setup_html_reporting,
    before_feature_html,
    after_feature_html,
    before_scenario_html,
    after_scenario_html,
    after_step_html,
    generate_html_report
)

# Importar steps directamente para que Behave los reconozca
from hakalab_framework.steps import *

def before_all(context):
    """Configuración inicial - Framework + HTML Reporter"""
    try:
        # Limpiar archivos antiguos si está habilitado
        from hakalab_framework.core.screenshot_manager import cleanup_directories
        cleanup_directories()
        
        # Configurar framework base
        setup_framework_context(context)
        
        # Configurar reporte HTML
        setup_html_reporting(context)
        
        print("✅ Framework y HTML Reporter configurados correctamente")
    except Exception as e:
        print(f"❌ Error en before_all: {e}")
        raise

def before_feature(context, feature):
    """Configuración por feature"""
    try:
        # Hook para HTML reporter
        before_feature_html(context, feature)
    except Exception as e:
        print(f"⚠️ Error en before_feature: {e}")

def before_scenario(context, scenario):
    """Configuración por escenario - Framework + HTML Reporter"""
    try:
        # Configurar escenario en framework
        setup_scenario_context(context, scenario)
        
        # Hook para HTML reporter
        before_scenario_html(context, scenario)
        
        print(f"🚀 Iniciando escenario: {scenario.name}")
    except Exception as e:
        print(f"❌ Error en before_scenario: {e}")
        raise

def after_step(context, step):
    """Después de cada step - Capturar para HTML Reporter"""
    try:
        # Hook para HTML reporter (captura screenshots y datos)
        after_step_html(context, step)
        
        # Screenshot adicional usando framework (opcional)
        # Descomenta si quieres screenshots adicionales con el sistema del framework
        # if hasattr(context, 'page') and context.page:
        #     step_name = step.name.replace(' ', '_').replace('"', '').replace("'", '')
        #     screenshot_name = f"framework_step_{step.line}_{step_name[:50]}"
        #     take_screenshot(context, screenshot_name)
        
    except Exception as e:
        print(f"⚠️ Error en after_step: {e}")

def after_scenario(context, scenario):
    """Después de cada escenario - HTML Reporter + Framework"""
    try:
        # Hook para HTML reporter (captura estado y screenshots de fallo)
        after_scenario_html(context, scenario)
        
        # Screenshot de fallo usando framework (adicional)
        take_screenshot_on_failure(context, scenario)
        
    except Exception as e:
        print(f"⚠️ Error en after_scenario: {e}")
    
    # Cerrar página actual para liberar memoria
    try:
        if hasattr(context, 'page') and context.page:
            context.page.close()
            context.page = None
    except:
        pass

def after_feature(context, feature):
    """Después de cada feature"""
    try:
        # Hook para HTML reporter
        after_feature_html(context, feature)
    except Exception as e:
        print(f"⚠️ Error en after_feature: {e}")

def after_all(context):
    """Limpieza final - Generar reportes"""
    # Cerrar Playwright
    try:
        if hasattr(context, 'framework_config') and context.framework_config:
            context.framework_config.cleanup()
            print("✅ Playwright cerrado correctamente")
    except Exception as e:
        print(f"⚠️ Error cerrando Playwright: {e}")
    
    # Generar reporte HTML personalizado
    try:
        report_path = generate_html_report(context)
        if report_path:
            print(f"🎨 Reporte HTML personalizado: {report_path}")
            print("   📊 Incluye gráficos, screenshots y navegación interactiva")
    except Exception as e:
        print(f"⚠️ Error generando reporte HTML: {e}")
    
    # Mostrar resumen de screenshots
    try:
        from hakalab_framework.core.screenshot_manager import get_screenshots_summary
        summary = get_screenshots_summary()
        if summary["total"] > 0:
            print(f"📸 Screenshots generados: {summary['total']} total, {summary['failed']} fallos")
    except Exception as e:
        print(f"⚠️ Error obteniendo resumen de screenshots: {e}")