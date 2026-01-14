"""
Environment.py con integración Jira/Xray para Hakalab Framework
"""
from hakalab_framework.core.environment_config import (
    setup_framework_context,
    setup_scenario_context
)
from hakalab_framework.integrations.behave_hooks import (
    before_all_jira_xray,
    before_feature_jira_xray,
    after_scenario_jira_xray,
    after_feature_jira_xray
)


def before_all(context):
    """Configuración inicial antes de todas las features"""
    # Configurar el framework base
    setup_framework_context(context)
    
    # Configurar integración Jira/Xray
    before_all_jira_xray(context)


def before_feature(context, feature):
    """Configuración antes de cada feature"""
    # Hook para Jira/Xray
    before_feature_jira_xray(context, feature)


def before_scenario(context, scenario):
    """Configuración antes de cada escenario"""
    # Configurar contexto del escenario
    setup_scenario_context(context, scenario)


def after_scenario(context, scenario):
    """Limpieza después de cada escenario"""
    # Hook para Jira/Xray (recopilar resultados)
    after_scenario_jira_xray(context, scenario)
    
    # Capturar screenshot en caso de fallo
    if scenario.status == "failed" and hasattr(context, 'page'):
        try:
            screenshot_path = f"screenshots/failed_{scenario.name}_{context.timestamp}.png"
            context.page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot capturado: {screenshot_path}")
        except Exception as e:
            print(f"⚠️ Error al capturar screenshot: {e}")


def after_feature(context, feature):
    """Limpieza después de cada feature"""
    # Hook para Jira/Xray (procesar integración)
    after_feature_jira_xray(context, feature)


def after_all(context):
    """Limpieza final después de todas las features"""
    # Cerrar navegador si está abierto
    if hasattr(context, 'browser') and context.browser:
        try:
            context.browser.close()
            print("✅ Navegador cerrado correctamente")
        except Exception as e:
            print(f"⚠️ Error al cerrar navegador: {e}")
    
    print("🏁 Ejecución de pruebas completada")