#!/usr/bin/env python3
"""
CLI para el framework Hakalab
"""
import click
import os
import sys
import shutil
from pathlib import Path
from typing import Optional

from .core.step_suggester import StepSuggester
from .core.report_generator import ReportGenerator
from .core.allure_config import get_safe_behave_command, diagnose_allure_issue
from .templates import create_project_structure

@click.group()
@click.version_option(version="1.1.2")
def cli():
    """Hakalab Framework - CLI para pruebas funcionales"""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--template', default='basic', help='Plantilla de proyecto (basic, advanced)')
@click.option('--language', default='mixed', help='Idioma por defecto (en, es, mixed)')
def init(project_name: str, template: str, language: str):
    """Inicializa un nuevo proyecto de pruebas"""
    click.echo(f"🚀 Creando proyecto: {project_name}")
    
    project_path = Path(project_name)
    
    if project_path.exists():
        if not click.confirm(f"El directorio {project_name} ya existe. ¿Continuar?"):
            return
    
    try:
        create_project_structure(project_path, template, language)
        click.echo(f"✅ Proyecto {project_name} creado exitosamente!")
        click.echo(f"\n📋 Próximos pasos:")
        click.echo(f"1. cd {project_name}")
        click.echo(f"2. pip install hakalab-framework")
        click.echo(f"3. haka-run --list-features")
        click.echo(f"4. haka-run --feature example_login.feature")
        
    except Exception as e:
        click.echo(f"❌ Error creando proyecto: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--tags', multiple=True, help='Tags para filtrar pruebas')
@click.option('--feature', help='Archivo feature específico')
@click.option('--parallel', is_flag=True, help='Ejecutar en paralelo')
@click.option('--workers', default=4, help='Número de workers paralelos (default: 4)')
@click.option('--list-features', is_flag=True, help='Listar features disponibles')
@click.option('--browser', default='chromium', help='Navegador a usar')
@click.option('--headless', is_flag=True, help='Ejecutar en modo headless')
@click.option('--docker', is_flag=True, help='Optimizar para ejecución en Docker')
def run(tags, feature, parallel, workers, list_features, browser, headless, docker):
    """Ejecuta las pruebas del proyecto"""
    
    if list_features:
        _list_features()
        return
    
    # Configurar variables de entorno
    os.environ['BROWSER'] = browser
    if headless:
        os.environ['HEADLESS'] = 'true'
    if docker:
        os.environ['HEADLESS'] = 'true'  # Forzar headless en Docker
        os.environ['AUTO_SCREENSHOT_ON_FAILURE'] = 'true'
        os.environ['LOG_LEVEL'] = 'INFO'
    
    # Usar configuración segura de Allure
    cmd = get_safe_behave_command(tags=tags[0] if tags else None, use_allure=True)
    
    # Agregar configuraciones adicionales
    if feature:
        if not feature.endswith('.feature'):
            feature += '.feature'
        feature_path = Path("features") / feature
        if feature_path.exists():
            cmd.append(str(feature_path))
        else:
            click.echo(f"❌ Feature no encontrado: {feature_path}", err=True)
            return
    
    if parallel:
        cmd.extend(["--processes", str(workers)])
        click.echo(f"🔄 Ejecutando con {workers} workers en paralelo")
    
    click.echo(f"🚀 Ejecutando: behave {' '.join(cmd)}")
    
    import subprocess
    try:
        result = subprocess.run(["behave"] + cmd, check=False)
        if result.returncode == 0:
            click.echo("✅ Todas las pruebas pasaron!")
        else:
            click.echo(f"⚠️  Algunas pruebas fallaron (código: {result.returncode})")
            sys.exit(result.returncode)
    except Exception as e:
        click.echo(f"❌ Error ejecutando pruebas: {e}", err=True)
        
        # Diagnosticar problema de Allure si es necesario
        if "allure" in str(e).lower():
            click.echo("\n🔍 Diagnosticando problema de Allure...")
            diagnose_allure_issue()
        
        sys.exit(1)

@cli.command()
@click.option('--serve', is_flag=True, help='Servir reporte con servidor integrado')
@click.option('--port', default=8080, help='Puerto para servidor')
@click.option('--simple', is_flag=True, help='Generar reporte HTML simple')
@click.option('--clean', is_flag=True, help='Limpiar reportes anteriores')
@click.option('--no-browser', is_flag=True, help='No abrir navegador')
def report(serve, port, simple, clean, no_browser):
    """Genera reportes de las pruebas"""
    
    generator = ReportGenerator()
    
    if clean:
        generator.clean_previous_reports()
        generator.clean_previous_results()
        click.echo("✅ Reportes limpiados")
        return
    
    if simple:
        if generator.generate_simple_html_report():
            click.echo("✅ Reporte simple generado")
        else:
            click.echo("❌ Error generando reporte simple", err=True)
        return
    
    if serve:
        generator.serve_allure_report(port)
        return
    
    # Generar reporte normal
    success = generator.generate_allure_report(
        single_file=True,
        open_browser=not no_browser
    )
    
    if success:
        click.echo("✅ Reporte de Allure generado")
    else:
        click.echo("⚠️  Generando reporte simple como alternativa...")
        generator.generate_simple_html_report()

@cli.command()
@click.option('--search', help='Buscar pasos por palabra clave')
@click.option('--category', help='Filtrar por categoría')
@click.option('--language', default='mixed', help='Idioma (en, es, mixed)')
@click.option('--suggest', help='Sugerir pasos para texto parcial')
@click.option('--generate-docs', is_flag=True, help='Generar documentación completa')
def steps(search, category, language, suggest, generate_docs):
    """Explora y sugiere pasos disponibles"""
    
    suggester = StepSuggester()
    
    if generate_docs:
        suggester.generate_step_documentation()
        return
    
    if suggest:
        suggestions = suggester.suggest_steps(suggest, language)
        click.echo(f"💡 Sugerencias para: '{suggest}'")
        click.echo("=" * 50)
        
        for i, step in enumerate(suggestions, 1):
            click.echo(f"\n{i}. {step.description}")
            click.echo(f"   Patrón: {step.pattern}")
            click.echo(f"   Ejemplo: {step.example}")
            click.echo(f"   Categoría: {step.category}")
        
        if not suggestions:
            click.echo("No se encontraron sugerencias")
        return
    
    if search:
        results = suggester.search_steps(search, language)
        click.echo(f"🔍 Resultados para: '{search}'")
        click.echo("=" * 50)
        
        for step in results:
            click.echo(f"\n• {step.description}")
            click.echo(f"  {step.example}")
        
        if not results:
            click.echo("No se encontraron resultados")
        return
    
    if category:
        steps_in_category = suggester.get_steps_by_category(category, language)
        click.echo(f"📂 Pasos en categoría: {category}")
        click.echo("=" * 50)
        
        for step in steps_in_category:
            click.echo(f"\n• {step.description}")
            click.echo(f"  {step.example}")
        return
    
    # Mostrar resumen por defecto
    categories = suggester.get_all_categories()
    click.echo("📚 Categorías de pasos disponibles:")
    click.echo("=" * 40)
    
    for cat in sorted(categories):
        count = len(suggester.get_steps_by_category(cat, language))
        click.echo(f"• {cat}: {count} pasos")
    
    click.echo(f"\n💡 Usa --help para ver más opciones")
    click.echo(f"   haka-steps --search 'click'")
    click.echo(f"   haka-steps --suggest 'I want to'")
    click.echo(f"   haka-steps --category 'Navegación'")

@cli.command()
def validate():
    """Valida la configuración del proyecto"""
    
    checks = [
        ("features/", "Directorio features"),
        ("json_poms/", "Directorio json_poms"),
        ("behave.ini", "Configuración de Behave"),
        (".env", "Variables de entorno"),
    ]
    
    click.echo("🔍 Validando proyecto...")
    click.echo("=" * 30)
    
    all_good = True
    
    for path, description in checks:
        if Path(path).exists():
            click.echo(f"✅ {description}")
        else:
            click.echo(f"❌ {description} no encontrado: {path}")
            all_good = False
    
    # Verificar dependencias
    try:
        import playwright
        click.echo("✅ Playwright instalado")
    except ImportError:
        click.echo("❌ Playwright no instalado")
        all_good = False
    
    try:
        import behave
        click.echo("✅ Behave instalado")
    except ImportError:
        click.echo("❌ Behave no instalado")
        all_good = False
    
    if all_good:
        click.echo("\n🎉 Proyecto configurado correctamente!")
    else:
        click.echo("\n🚨 Se encontraron problemas. Ejecuta 'haka-init' para crear un proyecto nuevo.")
        sys.exit(1)

def _list_features():
    """Lista archivos feature disponibles"""
    features_dir = Path("features")
    
    if not features_dir.exists():
        click.echo("❌ Directorio features no encontrado")
        return
    
    feature_files = list(features_dir.glob("*.feature"))
    
    if feature_files:
        click.echo("📁 Features disponibles:")
        for feature_file in sorted(feature_files):
            click.echo(f"  • {feature_file.name}")
    else:
        click.echo("❌ No se encontraron archivos .feature")

# Funciones de entrada para setup.py
def init_project():
    """Punto de entrada para haka-init"""
    cli(['init'] + sys.argv[1:])

def run_tests():
    """Punto de entrada para haka-run"""
    cli(['run'] + sys.argv[1:])

def generate_report():
    """Punto de entrada para haka-report"""
    cli(['report'] + sys.argv[1:])

def list_steps():
    """Punto de entrada para haka-steps"""
    cli(['steps'] + sys.argv[1:])

def validate_project():
    """Punto de entrada para haka-validate"""
    cli(['validate'] + sys.argv[1:])

if __name__ == '__main__':
    cli()