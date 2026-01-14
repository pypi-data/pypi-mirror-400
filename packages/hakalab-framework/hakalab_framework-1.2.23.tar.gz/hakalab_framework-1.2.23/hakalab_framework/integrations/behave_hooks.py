"""
Hooks de Behave para integración con Jira y Xray
"""
import os
from typing import List, Dict, Any
from behave.model import Feature, Scenario
from behave.runner import Context
from .jira_integration import JiraIntegration
from .xray_integration import XrayIntegration


class JiraXrayHooks:
    """Clase para manejar los hooks de integración con Jira y Xray"""
    
    def __init__(self):
        """Inicializar las integraciones"""
        self.jira = JiraIntegration()
        self.xray = XrayIntegration(self.jira) if self.jira.is_configured else None
        self.scenario_results = []
    
    def before_all(self, context: Context):
        """Hook ejecutado antes de todas las features"""
        if self.jira.is_configured:
            print("🔗 Iniciando integración con Jira")
            if self.jira.test_connection():
                print("✅ Conexión con Jira establecida")
            else:
                print("❌ Error de conexión con Jira")
        
        if self.xray and self.xray.is_configured:
            print("🔗 Xray habilitado")
    
    def before_feature(self, context: Context, feature: Feature):
        """Hook ejecutado antes de cada feature"""
        # Limpiar resultados de escenarios anteriores
        self.scenario_results = []
        
        # Guardar información del feature en el contexto
        context.current_feature = feature
        context.jira_xray_hooks = self
    
    def after_scenario(self, context: Context, scenario: Scenario):
        """Hook ejecutado después de cada escenario"""
        # Extraer test key de los tags del escenario
        test_key = None
        if self.xray and self.xray.is_configured:
            test_key = self.xray.extract_test_key_from_tags(scenario.tags)
        
        # Recopilar información del resultado
        scenario_result = {
            'name': scenario.name,
            'status': scenario.status.name,
            'test_key': test_key,
            'tags': scenario.tags,
            'error_message': None
        }
        
        # Capturar mensaje de error si el escenario falló
        if scenario.status.name == 'failed' and hasattr(scenario, 'exception'):
            scenario_result['error_message'] = str(scenario.exception)
        
        self.scenario_results.append(scenario_result)
    
    def after_feature(self, context: Context, feature: Feature):
        """Hook ejecutado después de cada feature"""
        if not (self.jira.is_configured or (self.xray and self.xray.is_configured)):
            return
        
        print(f"\n🔗 Procesando integración para feature: {feature.name}")
        
        # Obtener ruta del reporte HTML
        report_path = self._get_html_report_path(context)
        
        if not report_path or not os.path.exists(report_path):
            print("⚠️ Reporte HTML no encontrado, saltando integración")
            return
        
        # Procesar integración con Jira (regla 3 y 4)
        if self.jira.is_configured:
            self._process_jira_integration(feature, report_path)
        
        # Procesar integración con Xray (regla 5)
        if self.xray and self.xray.is_configured:
            self._process_xray_integration(feature)
    
    def _get_html_report_path(self, context: Context) -> str:
        """Obtener la ruta del reporte HTML generado"""
        # Intentar obtener la ruta del contexto si está disponible
        if hasattr(context, 'html_report_path'):
            return context.html_report_path
        
        # Buscar en ubicaciones comunes
        possible_paths = [
            'reports/report.html',
            'html-reports/report.html',
            'report.html',
            'reports/behave-report.html'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _process_jira_integration(self, feature: Feature, report_path: str):
        """Procesar integración con Jira (reglas 3 y 4)"""
        print("📋 Procesando integración con Jira...")
        
        # Extraer tags del feature
        feature_tags = [tag for tag in feature.tags]
        
        if not feature_tags:
            print("⚠️ Feature sin tags, saltando integración con Jira")
            return
        
        # Procesar cada tag del feature
        results = self.jira.process_feature_tags(feature_tags, report_path)
        
        if results:
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            print(f"📊 Jira: {successful}/{total} reportes adjuntados exitosamente")
        else:
            print("ℹ️ Ningún tag del feature corresponde a issues válidas de Jira")
    
    def _process_xray_integration(self, feature: Feature):
        """Procesar integración con Xray (regla 5)"""
        print("🧪 Procesando integración con Xray...")
        
        # Filtrar escenarios que tienen test keys válidos
        valid_scenarios = [
            result for result in self.scenario_results 
            if result.get('test_key')
        ]
        
        if not valid_scenarios:
            print("⚠️ No se encontraron escenarios con test keys válidos para Xray")
            return
        
        # Crear Test Execution y actualizar estados
        execution_key = self.xray.create_execution_from_feature(feature.name, valid_scenarios)
        
        if execution_key:
            print(f"✅ Test Execution creado y actualizado: {execution_key}")
        else:
            print("❌ Error al crear Test Execution en Xray")


# Instancia global para usar en environment.py
jira_xray_hooks = JiraXrayHooks()


def setup_jira_xray_hooks(context: Context):
    """Configurar los hooks de Jira/Xray en el contexto de Behave"""
    context.jira_xray_hooks = jira_xray_hooks
    
    # Registrar hooks
    context.add_cleanup(jira_xray_hooks.before_all, context)


# Funciones de hook para usar directamente en environment.py
def before_all_jira_xray(context: Context):
    """Hook before_all para Jira/Xray"""
    jira_xray_hooks.before_all(context)


def before_feature_jira_xray(context: Context, feature: Feature):
    """Hook before_feature para Jira/Xray"""
    jira_xray_hooks.before_feature(context, feature)


def after_scenario_jira_xray(context: Context, scenario: Scenario):
    """Hook after_scenario para Jira/Xray"""
    jira_xray_hooks.after_scenario(context, scenario)


def after_feature_jira_xray(context: Context, feature: Feature):
    """Hook after_feature para Jira/Xray"""
    jira_xray_hooks.after_feature(context, feature)