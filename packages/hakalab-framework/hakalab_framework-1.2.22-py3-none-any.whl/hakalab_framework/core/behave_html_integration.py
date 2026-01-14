#!/usr/bin/env python3
"""
Integración del HTML Reporter con Behave
Captura automáticamente datos durante la ejecución de pruebas
"""
import os
import re
from pathlib import Path
from datetime import datetime
from .html_reporter import html_reporter

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

def setup_html_reporting(context):
    """Configura el reporte HTML en el contexto de Behave"""
    # Obtener configuración del navegador
    browser = 'chromium'
    if hasattr(context, 'framework_config') and context.framework_config:
        browser = context.framework_config.config.get('browser', 'chromium')
    
    # Iniciar tracking de ejecución
    html_reporter.start_execution(browser=browser, environment='test')
    
    # Guardar referencia en el contexto
    context.html_reporter = html_reporter

def before_feature_html(context, feature):
    """Hook para inicio de feature"""
    if hasattr(context, 'html_reporter'):
        tags = [tag for tag in feature.tags] if hasattr(feature, 'tags') else []
        context.html_reporter.start_feature(
            feature_name=feature.name,
            feature_description=feature.description or "",
            tags=tags
        )

def after_feature_html(context, feature):
    """Hook para fin de feature"""
    if hasattr(context, 'html_reporter'):
        context.html_reporter.end_feature()

def before_scenario_html(context, scenario):
    """Hook para inicio de scenario"""
    if hasattr(context, 'html_reporter'):
        tags = [tag for tag in scenario.tags] if hasattr(scenario, 'tags') else []
        context.html_reporter.start_scenario(
            scenario_name=scenario.name,
            tags=tags
        )

def after_scenario_html(context, scenario):
    """Hook para fin de scenario"""
    if hasattr(context, 'html_reporter'):
        status = 'passed'
        error_message = None
        
        if scenario.status.name == 'failed':
            status = 'failed'
            if hasattr(scenario, 'exception') and scenario.exception:
                error_message = str(scenario.exception)
        elif scenario.status.name == 'skipped':
            status = 'skipped'
        
        # Capturar screenshot si el scenario falló
        if status == 'failed' and hasattr(context, 'page') and context.page:
            try:
                screenshot_dir = Path(os.getenv('SCREENSHOTS_DIR', 'screenshots'))
                screenshot_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                scenario_name = clean_filename(scenario.name, 50)
                screenshot_name = f"FAILED_{scenario_name}_{timestamp}.png"
                screenshot_path = screenshot_dir / screenshot_name
                
                full_page = os.getenv('SCREENSHOT_FULL_PAGE', 'true').lower() == 'true'
                context.page.screenshot(
                    path=str(screenshot_path),
                    full_page=full_page,  # Configurable: página completa o viewport
                    type='png'
                )
                
                # Debug: Verificar que el archivo se creó
                if os.path.exists(str(screenshot_path)):
                    print(f"📸 Screenshot de fallo capturado: {screenshot_path}")
                    context.html_reporter.add_screenshot(
                        str(screenshot_path), 
                        f"Screenshot del fallo: {scenario.name}"
                    )
                else:
                    print(f"❌ Error: Screenshot de fallo no se creó: {screenshot_path}")
                    
            except Exception as e:
                print(f"❌ Error capturando screenshot de fallo: {e}")
                import traceback
                traceback.print_exc()
        
        context.html_reporter.end_scenario(status=status, error_message=error_message)

def after_step_html(context, step):
    """Hook para después de cada step"""
    if hasattr(context, 'html_reporter'):
        status = 'passed'
        error_message = None
        screenshot_path = None
        
        if step.status.name == 'failed':
            status = 'failed'
            if hasattr(step, 'exception') and step.exception:
                error_message = str(step.exception)
        elif step.status.name == 'skipped':
            status = 'skipped'
        elif step.status.name == 'undefined':
            status = 'undefined'
        
        # Capturar screenshot para cada step (opcional, configurable)
        if hasattr(context, 'page') and context.page:
            try:
                # Solo capturar si está habilitado en configuración
                capture_all_steps = os.getenv('HTML_REPORT_CAPTURE_ALL_STEPS', 'false').lower() == 'true'
                
                if capture_all_steps or status == 'failed':
                    screenshot_dir = Path(os.getenv('SCREENSHOTS_DIR', 'screenshots'))
                    screenshot_dir.mkdir(exist_ok=True)
                    
                    step_name = clean_filename(step.name, 50)
                    timestamp = datetime.now().strftime("%H%M%S")
                    screenshot_name = f"step_{step.line}_{step_name}_{timestamp}.png"
                    screenshot_path = screenshot_dir / screenshot_name
                    
                    full_page = os.getenv('SCREENSHOT_FULL_PAGE', 'true').lower() == 'true'
                    context.page.screenshot(
                        path=str(screenshot_path),
                        full_page=full_page,  # Configurable: página completa o viewport
                        type='png'
                    )
                    screenshot_path = str(screenshot_path)
                    
                    # Debug: Verificar que el archivo se creó
                    if os.path.exists(screenshot_path):
                        print(f"📸 Screenshot capturado para step: {screenshot_path}")
                    else:
                        print(f"❌ Error: Screenshot no se creó: {screenshot_path}")
                        
            except Exception as e:
                print(f"❌ Error capturando screenshot del step: {e}")
                import traceback
                traceback.print_exc()
        
        context.html_reporter.add_step(
            step_name=step.name,
            status=status,
            error_message=error_message,
            screenshot_path=screenshot_path
        )

def generate_html_report(context, report_name: str = None):
    """Genera el reporte HTML final"""
    if hasattr(context, 'html_reporter'):
        if not report_name:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"test_report_{timestamp}.html"
        
        report_path = context.html_reporter.generate_report(report_name)
        print(f"📊 Reporte HTML generado: {report_path}")
        return report_path
    return None

def add_screenshot_to_report(context, screenshot_path: str, description: str = ""):
    """Agrega un screenshot manual al reporte"""
    if hasattr(context, 'html_reporter'):
        context.html_reporter.add_screenshot(screenshot_path, description)