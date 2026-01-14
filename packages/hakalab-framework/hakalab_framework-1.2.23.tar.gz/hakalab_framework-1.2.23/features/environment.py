"""
Environment.py para hakalab-framework v1.1.20+
CON REPORTE HTML PERSONALIZADO
SIN ALLURE - Screenshots integrados con HTML Reporter
CON GRABACIÓN DE VIDEO AUTOMÁTICA
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

# Importar manejo de videos
from hakalab_framework.core.video_manager import (
    setup_video_name_for_scenario,
    save_video_on_scenario_end,
    get_video_summary,
    is_video_recording_enabled
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
        
        # Configurar información del reporte y logo secundario
        if hasattr(context, 'html_reporter'):
            context.html_reporter.configure_report_info(
                title="Reporte de Pruebas - Mi Empresa",
                engineer="Tu Nombre",
                product="Mi Producto",
                company="Mi Empresa",
                version="1.0.0"
            )
            
            # Habilitar logo secundario con un ejemplo
            context.html_reporter.config['logos']['secondary_logo']['enabled'] = True
            context.html_reporter.config['logos']['secondary_logo']['path'] = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjYwIiB2aWV3Qm94PSIwIDAgMTUwIDYwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iNjAiIGZpbGw9IiMzNDQ5NWUiIHJ4PSI4Ii8+PHRleHQgeD0iNzUiIHk9IjM1IiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5NSSBFTVBSRVNBPC90ZXh0Pjwvc3ZnPg=="
            context.html_reporter.config['logos']['secondary_logo']['alt'] = "Logo de Mi Empresa"
        
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
    """Configuración por escenario - Framework + HTML Reporter + Video"""
    try:
        # Configurar escenario en framework
        setup_scenario_context(context, scenario)
        
        # Hook para HTML reporter
        before_scenario_html(context, scenario)
        
        # Configurar nombre de video para el escenario
        setup_video_name_for_scenario(context, scenario)
        
        print(f"🚀 Iniciando escenario: {scenario.name}")
    except Exception as e:
        print(f"❌ Error en before_scenario: {e}")
        raise

def after_step(context, step):
    """Después de cada step - HTML Reporter + Screenshots"""
    try:
        # Hook para HTML reporter (captura screenshots automáticamente)
        after_step_html(context, step)
        
        # Screenshot adicional del framework (opcional)
        import os
        capture_framework_steps = os.getenv('CAPTURE_FRAMEWORK_STEPS', 'false').lower() == 'true'
        
        if capture_framework_steps and hasattr(context, 'page') and context.page:
            step_name = step.name.replace(' ', '_').replace('"', '').replace("'", '')
            screenshot_name = f"framework_step_{step.line}_{step_name[:50]}"
            take_screenshot(context, screenshot_name)
        
    except Exception as e:
        print(f"⚠️ Error en after_step: {e}")

def after_scenario(context, scenario):
    """Después de cada escenario - HTML Reporter + Framework + Video"""
    try:
        # Hook para HTML reporter (captura estado y screenshots de fallo)
        after_scenario_html(context, scenario)
        
        # Manejo de video según resultado del escenario
        save_video_on_scenario_end(context, scenario)
        
        # Screenshot de fallo usando framework (adicional al HTML reporter)
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
    """Limpieza final - Generar reportes + Resumen de videos"""
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
    
    # Mostrar resumen de videos
    try:
        if is_video_recording_enabled():
            video_summary = get_video_summary(context)
            if video_summary['total_videos'] > 0:
                print(f"📹 Videos generados: {video_summary['total_videos']} total")
                print(f"   ✅ Exitosos: {video_summary['passed_videos']}")
                print(f"   ❌ Fallidos: {video_summary['failed_videos']}")
                print(f"   📁 Directorio: {video_summary['video_directory']}")
            else:
                print("📹 No se generaron videos en esta ejecución")
    except Exception as e:
        print(f"⚠️ Error obteniendo resumen de videos: {e}")