#!/usr/bin/env python3
"""
Generador de reportes para el framework de pruebas
"""
import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional
import shutil

class ReportGenerator:
    """Clase para generar diferentes tipos de reportes"""
    
    def __init__(self, results_dir: str = "html-reports", output_dir: str = "html-reports"):
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
    
    def clean_previous_results(self):
        """Limpia los resultados anteriores"""
        if self.results_dir.exists():
            shutil.rmtree(self.results_dir)
            print(f"🧹 Resultados anteriores limpiados: {self.results_dir}")
    
    def clean_previous_reports(self):
        """Limpia los reportes anteriores"""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            print(f"🧹 Reportes anteriores limpiados: {self.output_dir}")
    
    def check_allure_installation(self) -> bool:
        """Verifica si Allure está instalado"""
        try:
            subprocess.run(["allure", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_allure_suggestions(self):
        """Muestra sugerencias para instalar Allure"""
        print("💡 Para instalar Allure, usa uno de estos métodos:")
        print("   • Homebrew (macOS/Linux): brew install allure")
        print("   • Scoop (Windows): scoop install allure")
        print("   • NPM: npm install -g allure-commandline")
        print("   • Manual: https://docs.qameta.io/allure/")
    
    def generate_allure_report(self, single_file: bool = True, open_browser: bool = True) -> bool:
        """
        Genera el reporte de Allure en formato HTML
        
        Args:
            single_file: Si generar un archivo HTML único
            open_browser: Si abrir automáticamente en el navegador
            
        Returns:
            True si el reporte se generó exitosamente, False en caso contrario
        """
        if not self.check_allure_installation():
            print("❌ Allure no está instalado")
            self.install_allure_suggestions()
            return False
        
        if not self.results_dir.exists() or not any(self.results_dir.iterdir()):
            print(f"❌ No se encontraron resultados en: {self.results_dir}")
            print("💡 Ejecuta las pruebas primero para generar resultados")
            return False
        
        try:
            # Construir comando de Allure
            cmd = [
                "allure", "generate", str(self.results_dir),
                "--output", str(self.output_dir),
                "--clean"
            ]
            
            if single_file:
                cmd.append("--single-file")
            
            print(f"📊 Generando reporte de Allure...")
            subprocess.run(cmd, check=True)
            
            print(f"✅ Reporte de Allure generado exitosamente en: {self.output_dir}/")
            
            # Abrir en el navegador si se solicita
            if open_browser:
                self.open_report_in_browser()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error generando reporte de Allure: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return False
    
    def open_report_in_browser(self):
        """Abre el reporte en el navegador por defecto"""
        report_path = self.output_dir / "index.html"
        
        if report_path.exists():
            report_url = f"file://{report_path.absolute()}"
            print(f"🌐 Abriendo reporte en el navegador: {report_url}")
            
            try:
                webbrowser.open(report_url)
            except Exception as e:
                print(f"⚠️  No se pudo abrir automáticamente el navegador: {e}")
                print(f"📋 Abre manualmente: {report_url}")
        else:
            print(f"❌ Archivo de reporte no encontrado: {report_path}")
    
    def serve_allure_report(self, port: int = 8080):
        """
        Sirve el reporte de Allure usando el servidor integrado
        
        Args:
            port: Puerto para servir el reporte
        """
        if not self.check_allure_installation():
            print("❌ Allure no está instalado")
            self.install_allure_suggestions()
            return False
        
        if not self.results_dir.exists() or not any(self.results_dir.iterdir()):
            print(f"❌ No se encontraron resultados en: {self.results_dir}")
            return False
        
        try:
            print(f"🚀 Sirviendo reporte de Allure en puerto {port}...")
            print(f"🌐 Abre tu navegador en: http://localhost:{port}")
            print("⏹️  Presiona Ctrl+C para detener el servidor")
            
            subprocess.run([
                "allure", "serve", str(self.results_dir),
                "--port", str(port)
            ], check=True)
            
        except KeyboardInterrupt:
            print("\n⏹️  Servidor detenido")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error sirviendo reporte: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    def generate_simple_html_report(self) -> bool:
        """
        Genera un reporte HTML simple sin Allure (fallback)
        
        Returns:
            True si el reporte se generó exitosamente
        """
        try:
            # Crear directorio de salida
            self.output_dir.mkdir(exist_ok=True)
            
            # Generar HTML básico
            html_content = self._generate_simple_html_content()
            
            report_file = self.output_dir / "simple_report.html"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Reporte simple generado: {report_file}")
            
            # Abrir en navegador
            webbrowser.open(f"file://{report_file.absolute()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generando reporte simple: {e}")
            return False
    
    def _generate_simple_html_content(self) -> str:
        """Genera contenido HTML básico para el reporte simple"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Pruebas - Framework</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .info-box { background: #e7f3ff; border: 1px solid #007bff; border-radius: 4px; padding: 15px; margin: 20px 0; }
        .warning { background: #fff3cd; border: 1px solid #ffc107; color: #856404; }
        .success { background: #d4edda; border: 1px solid #28a745; color: #155724; }
        .code { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 10px; font-family: monospace; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Reporte de Pruebas Funcionales</h1>
            <p>Framework con Playwright y Behave</p>
        </div>
        
        <div class="info-box warning">
            <h3>⚠️ Reporte Básico</h3>
            <p>Este es un reporte básico generado porque Allure no está disponible.</p>
            <p>Para reportes más detallados, instala Allure:</p>
            <div class="code">
                # Homebrew (macOS/Linux)<br>
                brew install allure<br><br>
                # NPM<br>
                npm install -g allure-commandline
            </div>
        </div>
        
        <div class="info-box">
            <h3>📊 Información de la Ejecución</h3>
            <p><strong>Fecha:</strong> """ + str(__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + """</p>
            <p><strong>Framework:</strong> Playwright + Behave</p>
            <p><strong>Resultados:</strong> Revisa la consola para detalles de la ejecución</p>
        </div>
        
        <div class="info-box success">
            <h3>🚀 Próximos Pasos</h3>
            <ul>
                <li>Instala Allure para reportes detallados</li>
                <li>Ejecuta: <code>haka-report</code></li>
                <li>O usa: <code>haka-report --serve</code></li>
            </ul>
        </div>
    </div>
</body>
</html>
        """