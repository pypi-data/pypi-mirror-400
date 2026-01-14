#!/usr/bin/env python3
"""
CLI para generar reportes HTML personalizados
"""
import click
import os
import json
from pathlib import Path
from datetime import datetime
from .core.html_reporter import HtmlReporter

@click.group()
def html_cli():
    """Comandos para reportes HTML personalizados de Haka Lab"""
    pass

@html_cli.command()
@click.option('--output', '-o', default='report_config.json', 
              help='Nombre del archivo de configuración')
def create_config(output):
    """Crea un archivo de configuración template para reportes HTML"""
    click.echo("📝 Creando template de configuración...")
    
    reporter = HtmlReporter()
    config_path = reporter.create_config_template(output)
    
    click.echo(f"✅ Template creado: {config_path}")
    click.echo("📋 Personaliza los siguientes campos:")
    click.echo("   • engineer: Tu nombre")
    click.echo("   • product: Nombre del producto a probar")
    click.echo("   • company: Nombre de tu empresa")
    click.echo("   • secondary_logo.path: Ruta a tu logo empresarial")
    click.echo("   • styling: Colores personalizados")

@html_cli.command()
@click.option('--input-dir', '-i', default='allure-results', 
              help='Directorio con resultados de pruebas')
@click.option('--output-dir', '-o', default='html-reports',
              help='Directorio de salida para reportes HTML')
@click.option('--report-name', '-n', default=None,
              help='Nombre del archivo de reporte')
@click.option('--config', '-c', default=None,
              help='Archivo de configuración personalizado')
@click.option('--screenshots-dir', '-s', default=lambda: os.getenv('SCREENSHOTS_DIR', 'screenshots'),
              help='Directorio de screenshots')
@click.option('--open-browser', '-b', is_flag=True,
              help='Abrir reporte en navegador automáticamente')
@click.option('--engineer', default=None, help='Nombre del ingeniero')
@click.option('--product', default=None, help='Nombre del producto')
@click.option('--company', default=None, help='Nombre de la empresa')
@click.option('--version', default=None, help='Versión del producto')
def generate(input_dir, output_dir, report_name, config, screenshots_dir, 
             open_browser, engineer, product, company, version):
    """Genera un reporte HTML personalizado desde resultados de pruebas"""
    
    click.echo("🎨 Generando reporte HTML personalizado de Haka Lab...")
    
    # Crear reporter con configuración
    reporter = HtmlReporter(output_dir, config_path=config)
    
    # Configurar información desde parámetros CLI
    config_updates = {}
    if engineer:
        config_updates['engineer'] = engineer
    if product:
        config_updates['product'] = product
    if company:
        config_updates['company'] = company
    if version:
        config_updates['version'] = version
    
    if config_updates:
        reporter.configure_report_info(**config_updates)
    
    # Generar nombre si no se proporciona
    if not report_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"hakalab_report_{timestamp}.html"
    
    # Buscar datos de entrada
    input_path = Path(input_dir)
    screenshots_path = Path(screenshots_dir)
    
    if not input_path.exists():
        click.echo(f"❌ Directorio de entrada no encontrado: {input_dir}")
        click.echo("💡 Tip: Ejecuta primero tus pruebas con Behave para generar resultados")
        return
    
    # Procesar datos (simulado - en una implementación real parsearías Allure JSON)
    reporter.start_execution(browser='chromium', environment='test')
    
    # Ejemplo de datos simulados
    _add_sample_data(reporter, screenshots_path)
    
    # Generar reporte
    try:
        report_path = reporter.generate_report(report_name)
        click.echo(f"✅ Reporte generado: {report_path}")
        click.echo(f"📊 Incluye gráficos interactivos y navegación por features")
        
        # Abrir en navegador si se solicita
        if open_browser:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
            click.echo("🌐 Reporte abierto en navegador")
            
    except Exception as e:
        click.echo(f"❌ Error generando reporte: {e}")

@html_cli.command()
@click.option('--port', '-p', default=8080, help='Puerto para servidor local')
@click.option('--reports-dir', '-d', default='html-reports', help='Directorio de reportes')
def serve(port, reports_dir):
    """Inicia un servidor local para ver reportes HTML"""
    
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        click.echo(f"❌ Directorio de reportes no encontrado: {reports_dir}")
        click.echo("💡 Tip: Genera primero un reporte con 'haka-html generate'")
        return
    
    click.echo(f"🌐 Iniciando servidor Haka Lab en puerto {port}...")
    click.echo(f"📁 Sirviendo reportes desde: {reports_path.absolute()}")
    click.echo(f"🔗 URL: http://localhost:{port}")
    click.echo("📊 Navega a los archivos .html para ver los reportes")
    
    try:
        import http.server
        import socketserver
        import os
        
        os.chdir(reports_path)
        
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            click.echo("✅ Servidor iniciado. Presiona Ctrl+C para detener.")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        click.echo("\n🛑 Servidor detenido")
    except Exception as e:
        click.echo(f"❌ Error iniciando servidor: {e}")

@html_cli.command()
def demo():
    """Genera un reporte de demostración con datos de ejemplo"""
    click.echo("🎭 Generando reporte de demostración...")
    
    reporter = HtmlReporter(output_dir="demo-reports")
    
    # Configurar datos de demo
    reporter.configure_report_info(
        engineer="Demo Engineer",
        product="Sistema Demo",
        company="Haka Lab Demo",
        version="1.0.0-demo",
        environment="Demo"
    )
    
    # Generar datos de ejemplo más completos
    reporter.start_execution(browser='chromium', environment='demo')
    
    # Feature 1: Login
    reporter.start_feature("Autenticación de Usuarios", "Sistema de login y registro", ["@auth", "@critical"])
    
    reporter.start_scenario("Login exitoso con credenciales válidas", ["@smoke", "@positive"])
    reporter.add_step("Navegar a la página de login", "passed")
    reporter.add_step("Ingresar email válido", "passed")
    reporter.add_step("Ingresar contraseña válida", "passed")
    reporter.add_step("Hacer clic en botón 'Iniciar Sesión'", "passed")
    reporter.add_step("Verificar redirección al dashboard", "passed")
    reporter.end_scenario("passed")
    
    reporter.start_scenario("Login fallido con credenciales inválidas", ["@negative"])
    reporter.add_step("Navegar a la página de login", "passed")
    reporter.add_step("Ingresar email inválido", "passed")
    reporter.add_step("Ingresar contraseña incorrecta", "passed")
    reporter.add_step("Hacer clic en botón 'Iniciar Sesión'", "passed")
    reporter.add_step("Verificar mensaje de error", "failed", "Mensaje de error esperado no encontrado")
    reporter.end_scenario("failed", "Validación de credenciales falló")
    
    reporter.end_feature()
    
    # Feature 2: Navegación
    reporter.start_feature("Navegación del Sistema", "Pruebas de navegación y menús", ["@navigation"])
    
    reporter.start_scenario("Navegación por menú principal", ["@smoke"])
    reporter.add_step("Verificar menú principal visible", "passed")
    reporter.add_step("Hacer clic en 'Productos'", "passed")
    reporter.add_step("Verificar carga de página de productos", "passed")
    reporter.end_scenario("passed")
    
    reporter.start_scenario("Navegación con breadcrumbs", ["@ui"])
    reporter.add_step("Navegar a página de detalle", "passed")
    reporter.add_step("Verificar breadcrumbs visibles", "skipped")
    reporter.end_scenario("skipped")
    
    reporter.end_feature()
    
    # Feature 3: Formularios
    reporter.start_feature("Formularios y Validaciones", "Pruebas de formularios", ["@forms"])
    
    reporter.start_scenario("Envío de formulario de contacto", ["@forms", "@positive"])
    reporter.add_step("Navegar a página de contacto", "passed")
    reporter.add_step("Completar campo nombre", "passed")
    reporter.add_step("Completar campo email", "passed")
    reporter.add_step("Completar campo mensaje", "passed")
    reporter.add_step("Enviar formulario", "passed")
    reporter.add_step("Verificar mensaje de confirmación", "passed")
    reporter.end_scenario("passed")
    
    reporter.end_feature()
    
    # Generar reporte
    report_path = reporter.generate_report("demo_hakalab_report.html")
    click.echo(f"✅ Reporte de demostración generado: {report_path}")
    click.echo("🎨 Incluye:")
    click.echo("   • Logo de Haka Lab")
    click.echo("   • Gráficos interactivos")
    click.echo("   • Navegación por features y scenarios")
    click.echo("   • Diseño responsive")
    click.echo("🌐 Abre el archivo en tu navegador para verlo")

def _add_sample_data(reporter, screenshots_path):
    """Agrega datos de ejemplo (en implementación real, parsearía resultados reales)"""
    
    # Feature 1: Login Tests
    reporter.start_feature("Login Tests", "Pruebas de autenticación de usuarios", ["@login", "@smoke"])
    
    # Scenario 1: Login exitoso
    reporter.start_scenario("Login exitoso con credenciales válidas", ["@smoke"])
    reporter.add_step("Given I navigate to login page", "passed")
    reporter.add_step("When I enter valid credentials", "passed")
    reporter.add_step("And I click login button", "passed")
    reporter.add_step("Then I should see dashboard", "passed")
    reporter.end_scenario("passed")
    
    # Scenario 2: Login fallido
    reporter.start_scenario("Login fallido con credenciales inválidas", ["@negative"])
    reporter.add_step("Given I navigate to login page", "passed")
    reporter.add_step("When I enter invalid credentials", "passed")
    reporter.add_step("And I click login button", "passed")
    reporter.add_step("Then I should see error message", "failed", "Expected error message not found")
    reporter.end_scenario("failed", "Login validation failed")
    
    reporter.end_feature()
    
    # Feature 2: Navigation Tests
    reporter.start_feature("Navigation Tests", "Pruebas de navegación del sitio", ["@navigation"])
    
    # Scenario 1: Menu navigation
    reporter.start_scenario("Navegación por menú principal", ["@smoke"])
    reporter.add_step("Given I am on homepage", "passed")
    reporter.add_step("When I click on Products menu", "passed")
    reporter.add_step("Then I should see products page", "passed")
    reporter.end_scenario("passed")
    
    # Scenario 2: Breadcrumb navigation
    reporter.start_scenario("Navegación por breadcrumbs", [])
    reporter.add_step("Given I am on product detail page", "passed")
    reporter.add_step("When I click on category breadcrumb", "passed")
    reporter.add_step("Then I should see category page", "skipped")
    reporter.end_scenario("skipped")
    
    reporter.end_feature()
    
    # Feature 3: Form Tests
    reporter.start_feature("Form Tests", "Pruebas de formularios", ["@forms"])
    
    # Scenario 1: Contact form
    reporter.start_scenario("Envío de formulario de contacto", ["@forms"])
    reporter.add_step("Given I navigate to contact page", "passed")
    reporter.add_step("When I fill contact form", "passed")
    reporter.add_step("And I submit the form", "passed")
    reporter.add_step("Then I should see success message", "passed")
    reporter.end_scenario("passed")
    
    reporter.end_feature()

if __name__ == '__main__':
    html_cli()