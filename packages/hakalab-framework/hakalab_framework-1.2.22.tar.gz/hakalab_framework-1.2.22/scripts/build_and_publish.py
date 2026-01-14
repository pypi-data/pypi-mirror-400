#!/usr/bin/env python3
"""
Script para construir y publicar el paquete en PyPI
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(f"   Comando: {cmd}")
        print(f"   Error: {e.stderr}")
        return False

def check_requirements():
    """Verifica que las herramientas necesarias estén instaladas"""
    print("🔍 Verificando herramientas necesarias...")
    
    tools = [
        ("twine", "twine --version"),
        ("build", "python -m build --version"),
    ]
    
    missing_tools = []
    
    for tool, check_cmd in tools:
        try:
            subprocess.run(check_cmd, shell=True, check=True, capture_output=True)
            print(f"✅ {tool} instalado")
        except subprocess.CalledProcessError:
            missing_tools.append(tool)
            print(f"❌ {tool} no instalado")
    
    if missing_tools:
        print(f"\n💡 Instala las herramientas faltantes:")
        print(f"   pip install twine build")
        return False
    
    return True

def clean_build_dirs():
    """Limpia directorios de build anteriores"""
    print("🧹 Limpiando directorios de build...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    
    for dir_pattern in dirs_to_clean:
        if "*" in dir_pattern:
            # Usar glob para patrones
            import glob
            for path in glob.glob(dir_pattern):
                if os.path.exists(path):
                    import shutil
                    shutil.rmtree(path)
                    print(f"   Eliminado: {path}")
        else:
            if os.path.exists(dir_pattern):
                import shutil
                shutil.rmtree(dir_pattern)
                print(f"   Eliminado: {dir_pattern}")

def build_package():
    """Construye el paquete"""
    return run_command("python -m build", "Construyendo paquete")

def check_package():
    """Verifica el paquete construido"""
    return run_command("twine check dist/*", "Verificando paquete")

def upload_to_test_pypi():
    """Sube el paquete a Test PyPI"""
    print("\n🧪 ¿Subir a Test PyPI primero? (recomendado)")
    response = input("Presiona Enter para continuar o 'n' para saltar: ").strip().lower()
    
    if response != 'n':
        return run_command(
            "twine upload --repository testpypi dist/*",
            "Subiendo a Test PyPI"
        )
    return True

def upload_to_pypi():
    """Sube el paquete a PyPI"""
    print("\n🚀 ¿Subir a PyPI oficial?")
    response = input("Escribe 'yes' para confirmar: ").strip().lower()
    
    if response == 'yes':
        return run_command("twine upload dist/*", "Subiendo a PyPI")
    else:
        print("⏹️  Subida a PyPI cancelada")
        return True

def main():
    """Función principal"""
    print("📦 Script de Build y Publicación - Playwright Behave Framework")
    print("=" * 70)
    
    # Verificar que estamos en el directorio correcto
    if not Path("setup.py").exists() and not Path("pyproject.toml").exists():
        print("❌ No se encontró setup.py o pyproject.toml")
        print("💡 Ejecuta este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Verificar herramientas
    if not check_requirements():
        sys.exit(1)
    
    # Limpiar builds anteriores
    clean_build_dirs()
    
    # Construir paquete
    if not build_package():
        sys.exit(1)
    
    # Verificar paquete
    if not check_package():
        sys.exit(1)
    
    print("\n✅ Paquete construido y verificado exitosamente!")
    print("📁 Archivos generados en dist/:")
    
    # Listar archivos generados
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"   • {file.name}")
    
    # Subir a Test PyPI
    if not upload_to_test_pypi():
        print("⚠️  Error subiendo a Test PyPI, pero continuando...")
    
    # Subir a PyPI
    upload_to_pypi()
    
    print("\n🎉 Proceso completado!")
    print("\n📋 Próximos pasos:")
    print("1. Verifica que el paquete esté disponible en PyPI")
    print("2. Prueba la instalación: pip install playwright-behave-framework")
    print("3. Actualiza la documentación si es necesario")

if __name__ == "__main__":
    main()