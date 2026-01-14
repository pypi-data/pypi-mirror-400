#!/usr/bin/env python3
"""
Script para publicar el framework Hakalab en PyPI
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(f"   Comando: {cmd}")
        print(f"   Error: {e.stderr}")
        return None

def clean_build_artifacts():
    """Limpia artefactos de construcción anteriores"""
    print("🧹 Limpiando artefactos anteriores...")
    
    dirs_to_clean = ['dist', 'build', 'hakalab_framework.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Eliminado: {dir_name}")

def verify_version():
    """Verifica que la versión esté actualizada en todos los archivos"""
    print("🔍 Verificando versión...")
    
    # Leer versión del __init__.py
    init_file = Path("hakalab_framework/__init__.py")
    if not init_file.exists():
        print("❌ No se encontró hakalab_framework/__init__.py")
        return None
    
    content = init_file.read_text()
    for line in content.split('\n'):
        if line.startswith('__version__'):
            version = line.split('"')[1]
            print(f"   Versión encontrada: {version}")
            return version
    
    print("❌ No se encontró __version__ en __init__.py")
    return None

def build_package():
    """Construye el paquete"""
    print("📦 Construyendo paquete...")
    
    # Usar build en lugar de setup.py (recomendado)
    cmd = "python -m build"
    result = run_command(cmd, "Construcción del paquete")
    
    if result is None:
        # Fallback a setup.py si build no está disponible
        print("   Intentando con setup.py...")
        cmd = "python setup.py sdist bdist_wheel"
        result = run_command(cmd, "Construcción con setup.py")
    
    return result is not None

def verify_package():
    """Verifica el paquete construido"""
    print("🔍 Verificando paquete...")
    
    if not os.path.exists("dist"):
        print("❌ Directorio dist no encontrado")
        return False
    
    dist_files = list(Path("dist").glob("*"))
    if not dist_files:
        print("❌ No se encontraron archivos en dist/")
        return False
    
    print(f"   Archivos encontrados:")
    for file in dist_files:
        print(f"     - {file.name}")
    
    # Verificar con twine
    cmd = "python -m twine check dist/*"
    result = run_command(cmd, "Verificación con twine")
    
    return result is not None

def show_upload_instructions(version):
    """Muestra instrucciones para subir manualmente"""
    print("\n" + "="*60)
    print("📋 INSTRUCCIONES PARA PUBLICAR EN PyPI")
    print("="*60)
    
    print(f"\n🎯 Versión a publicar: {version}")
    
    print("\n1️⃣ Configurar token de PyPI:")
    print("   - Ve a https://pypi.org/manage/account/token/")
    print("   - Crea un token para el proyecto 'hakalab-framework'")
    print("   - Configura el token:")
    print("     python -m twine configure")
    print("     # O edita ~/.pypirc manualmente")
    
    print("\n2️⃣ Publicar en PyPI:")
    print("   python -m twine upload dist/*")
    
    print("\n3️⃣ Verificar publicación:")
    print("   https://pypi.org/project/hakalab-framework/")
    
    print("\n4️⃣ Probar instalación:")
    print("   pip install hakalab-framework==1.1.1")
    print("   haka-init test-project")
    
    print("\n5️⃣ Contenido del archivo ~/.pypirc:")
    print("""   [distutils]
   index-servers = pypi
   
   [pypi]
   username = __token__
   password = pypi-TU_TOKEN_AQUI""")
    
    print("\n" + "="*60)

def main():
    """Función principal"""
    print("🚀 Script de Publicación - Hakalab Framework")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("hakalab_framework"):
        print("❌ No se encontró el directorio hakalab_framework")
        print("   Ejecuta este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Verificar versión
    version = verify_version()
    if not version:
        sys.exit(1)
    
    # Limpiar artefactos anteriores
    clean_build_artifacts()
    
    # Construir paquete
    if not build_package():
        print("❌ Error construyendo el paquete")
        sys.exit(1)
    
    # Verificar paquete
    if not verify_package():
        print("❌ Error verificando el paquete")
        sys.exit(1)
    
    print("\n✅ Paquete construido y verificado exitosamente!")
    
    # Mostrar instrucciones
    show_upload_instructions(version)
    
    # Preguntar si intentar subir automáticamente
    try:
        response = input("\n¿Intentar subir automáticamente? (y/N): ").strip().lower()
        if response in ['y', 'yes', 'sí', 'si']:
            print("\n🚀 Intentando subir a PyPI...")
            cmd = "python -m twine upload dist/*"
            result = run_command(cmd, "Subida a PyPI")
            
            if result:
                print(f"\n🎉 ¡Framework hakalab-framework v{version} publicado exitosamente!")
                print(f"   Disponible en: https://pypi.org/project/hakalab-framework/{version}/")
                print(f"\n📦 Para instalar:")
                print(f"   pip install hakalab-framework=={version}")
            else:
                print("\n⚠️  Error en la subida automática.")
                print("   Sigue las instrucciones manuales mostradas arriba.")
        else:
            print("\n📋 Sigue las instrucciones manuales mostradas arriba.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Proceso cancelado por el usuario")
        sys.exit(0)

if __name__ == "__main__":
    main()