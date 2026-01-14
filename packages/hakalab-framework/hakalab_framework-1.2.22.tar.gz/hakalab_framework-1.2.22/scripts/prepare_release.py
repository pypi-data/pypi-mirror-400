#!/usr/bin/env python3
"""
Script para preparar una nueva release
"""
import re
import sys
from pathlib import Path
from datetime import datetime

def update_version(new_version):
    """Actualiza la versión en todos los archivos necesarios"""
    files_to_update = [
        ("setup.py", r'version="([^"]*)"', f'version="{new_version}"'),
        ("pyproject.toml", r'version = "([^"]*)"', f'version = "{new_version}"'),
        ("hakalab_framework/__init__.py", r'__version__ = "([^"]*)"', f'__version__ = "{new_version}"'),
        ("hakalab_framework/cli.py", r'@click.version_option\(version="([^"]*)"\)', f'@click.version_option(version="{new_version}")'),
    ]
    
    print(f"🔄 Actualizando versión a {new_version}...")
    
    for file_path, pattern, replacement in files_to_update:
        file_path = Path(file_path)
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            new_content = re.sub(pattern, replacement, content)
            
            if content != new_content:
                file_path.write_text(new_content, encoding='utf-8')
                print(f"✅ Actualizado: {file_path}")
            else:
                print(f"⚠️  No se encontró patrón en: {file_path}")
        else:
            print(f"❌ Archivo no encontrado: {file_path}")

def update_changelog(version, changes):
    """Actualiza el changelog"""
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        # Crear changelog si no existe
        changelog_content = "# Changelog\n\nTodos los cambios notables de este proyecto serán documentados en este archivo.\n\n"
    else:
        changelog_content = changelog_path.read_text(encoding='utf-8')
    
    # Agregar nueva entrada
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"## [{version}] - {date_str}\n\n"
    
    for change in changes:
        new_entry += f"- {change}\n"
    
    new_entry += "\n"
    
    # Insertar después del header
    lines = changelog_content.split('\n')
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith('## [') or line.startswith('### ['):
            header_end = i
            break
        elif i > 5:  # Si no encontramos una entrada existente, insertar después del header
            header_end = min(i, len(lines))
            break
    
    if header_end == 0:
        # No hay entradas previas, agregar después del header
        for i, line in enumerate(lines):
            if line.strip() == "" and i > 2:
                header_end = i + 1
                break
    
    lines.insert(header_end, new_entry.rstrip())
    
    changelog_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ Changelog actualizado: {changelog_path}")

def validate_version(version):
    """Valida que la versión tenga el formato correcto"""
    pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
    return re.match(pattern, version) is not None

def get_current_version():
    """Obtiene la versión actual del __init__.py"""
    init_file = Path("hakalab_framework/__init__.py")
    if init_file.exists():
        content = init_file.read_text()
        match = re.search(r'__version__ = "([^"]*)"', content)
        if match:
            return match.group(1)
    return "0.0.0"

def main():
    """Función principal"""
    print("🚀 Preparar Nueva Release - Playwright Behave Framework")
    print("=" * 60)
    
    current_version = get_current_version()
    print(f"📋 Versión actual: {current_version}")
    
    # Solicitar nueva versión
    new_version = input(f"🔢 Nueva versión (formato: x.y.z): ").strip()
    
    if not validate_version(new_version):
        print("❌ Formato de versión inválido. Use formato: x.y.z (ej: 1.2.0)")
        sys.exit(1)
    
    if new_version <= current_version:
        print("⚠️  La nueva versión debe ser mayor que la actual")
        if not input("¿Continuar de todos modos? (y/N): ").lower().startswith('y'):
            sys.exit(1)
    
    # Solicitar cambios
    print("\n📝 Describe los cambios en esta versión:")
    print("   (Presiona Enter en línea vacía para terminar)")
    
    changes = []
    while True:
        change = input("• ").strip()
        if not change:
            break
        changes.append(change)
    
    if not changes:
        print("❌ Debes agregar al menos un cambio")
        sys.exit(1)
    
    # Confirmar cambios
    print(f"\n📋 Resumen de la release {new_version}:")
    print("=" * 40)
    for change in changes:
        print(f"• {change}")
    
    if not input("\n¿Proceder con la actualización? (y/N): ").lower().startswith('y'):
        print("⏹️  Operación cancelada")
        sys.exit(0)
    
    # Actualizar archivos
    update_version(new_version)
    update_changelog(new_version, changes)
    
    print(f"\n✅ Release {new_version} preparada!")
    print("\n📋 Próximos pasos:")
    print("1. Revisa los cambios: git diff")
    print("2. Commit los cambios: git add . && git commit -m 'Release v{}'".format(new_version))
    print("3. Crea un tag: git tag v{}".format(new_version))
    print("4. Push los cambios: git push && git push --tags")
    print("5. Ejecuta el build: python scripts/build_and_publish.py")

if __name__ == "__main__":
    main()