#!/usr/bin/env python3
"""
Ejemplo de uso del HTML Reporter personalizado de Haka Lab
Muestra cómo configurar y generar reportes HTML con logos y datos personalizados
"""

from hakalab_framework.core.html_reporter import HtmlReporter
import os

def example_basic_usage():
    """Ejemplo básico de uso del HTML Reporter"""
    print("🎨 Ejemplo básico del HTML Reporter")
    
    # Crear reporter
    reporter = HtmlReporter(output_dir="example-reports")
    
    # Configurar información del reporte
    reporter.configure_report_info(
        engineer="Juan Pérez",
        product="Sistema de Ventas Online",
        company="Mi Empresa S.A.",
        version="2.1.0",
        environment="Staging"
    )
    
    # Simular ejecución de pruebas
    reporter.start_execution(browser='chromium', environment='staging')
    
    # Feature 1
    reporter.start_feature("Login y Autenticación", "Pruebas del sistema de login", ["@login", "@critical"])
    
    reporter.start_scenario("Login exitoso", ["@smoke"])
    reporter.add_step("Navegar a página de login", "passed")
    reporter.add_step("Ingresar credenciales válidas", "passed")
    reporter.add_step("Hacer clic en botón login", "passed")
    reporter.add_step("Verificar redirección al dashboard", "passed")
    reporter.end_scenario("passed")
    
    reporter.start_scenario("Login con credenciales inválidas", ["@negative"])
    reporter.add_step("Navegar a página de login", "passed")
    reporter.add_step("Ingresar credenciales inválidas", "passed")
    reporter.add_step("Hacer clic en botón login", "passed")
    reporter.add_step("Verificar mensaje de error", "failed", "Mensaje de error no encontrado")
    reporter.end_scenario("failed", "Validación de credenciales falló")
    
    reporter.end_feature()
    
    # Feature 2
    reporter.start_feature("Carrito de Compras", "Funcionalidad del carrito", ["@cart", "@ecommerce"])
    
    reporter.start_scenario("Agregar producto al carrito", ["@smoke"])
    reporter.add_step("Navegar a página de productos", "passed")
    reporter.add_step("Seleccionar un producto", "passed")
    reporter.add_step("Hacer clic en 'Agregar al carrito'", "passed")
    reporter.add_step("Verificar producto en carrito", "passed")
    reporter.end_scenario("passed")
    
    reporter.end_feature()
    
    # Generar reporte
    report_path = reporter.generate_report("ejemplo_basico.html")
    print(f"✅ Reporte generado: {report_path}")
    
    return report_path

def example_with_custom_logo():
    """Ejemplo con logo personalizado"""
    print("🎨 Ejemplo con logo personalizado")
    
    # Crear reporter
    reporter = HtmlReporter(output_dir="example-reports")
    
    # Configurar información del reporte
    reporter.configure_report_info(
        title="Reporte QA - Mi Empresa",
        engineer="María García",
        product="App Mobile Banking",
        company="Banco Digital S.A.",
        version="3.2.1",
        environment="Production"
    )
    
    # Agregar logo secundario (si existe)
    # reporter.set_secondary_logo("path/to/company_logo.png", "Logo Banco Digital")
    
    # Simular datos de prueba más complejos
    reporter.start_execution(browser='firefox', environment='production')
    
    # Múltiples features con diferentes estados
    for i in range(3):
        feature_name = f"Feature {i+1}"
        reporter.start_feature(feature_name, f"Descripción del {feature_name}", [f"@feature{i+1}"])
        
        for j in range(2):
            scenario_name = f"Scenario {j+1} del {feature_name}"
            status = "passed" if (i + j) % 3 != 0 else "failed"
            
            reporter.start_scenario(scenario_name, [f"@scenario{j+1}"])
            
            for k in range(4):
                step_status = "passed" if k < 3 or status == "passed" else "failed"
                error_msg = f"Error en step {k+1}" if step_status == "failed" else None
                
                reporter.add_step(f"Step {k+1} - Acción de prueba", step_status, error_msg)
            
            reporter.end_scenario(status, "Error en validación" if status == "failed" else None)
        
        reporter.end_feature()
    
    # Generar reporte
    report_path = reporter.generate_report("ejemplo_con_logo.html")
    print(f"✅ Reporte con logo generado: {report_path}")
    
    return report_path

def example_create_config_template():
    """Ejemplo de creación de template de configuración"""
    print("📝 Creando template de configuración")
    
    reporter = HtmlReporter()
    config_path = reporter.create_config_template("mi_config_personalizado.json")
    
    print(f"📄 Archivo de configuración creado: {config_path}")
    print("✏️  Edita este archivo para personalizar:")
    print("   - Información del ingeniero y empresa")
    print("   - Logos personalizados")
    print("   - Colores del tema")
    
    return config_path

def example_with_config_file():
    """Ejemplo usando archivo de configuración"""
    print("⚙️  Ejemplo con archivo de configuración")
    
    # Primero crear el config si no existe
    config_path = "example_config.json"
    if not os.path.exists(config_path):
        example_create_config_template()
        os.rename("mi_config_personalizado.json", config_path)
    
    # Crear reporter con configuración personalizada
    reporter = HtmlReporter(output_dir="example-reports", config_path=config_path)
    
    # El resto de la lógica es igual
    reporter.start_execution(browser='webkit', environment='test')
    
    reporter.start_feature("Feature con Config", "Usando configuración personalizada", ["@config"])
    reporter.start_scenario("Scenario de ejemplo", ["@example"])
    reporter.add_step("Step con configuración personalizada", "passed")
    reporter.end_scenario("passed")
    reporter.end_feature()
    
    report_path = reporter.generate_report("ejemplo_con_config.html")
    print(f"✅ Reporte con configuración personalizada: {report_path}")
    
    return report_path

if __name__ == "__main__":
    print("🚀 Ejemplos del HTML Reporter de Haka Lab")
    print("=" * 50)
    
    # Ejecutar ejemplos
    example_basic_usage()
    print()
    
    example_with_custom_logo()
    print()
    
    example_create_config_template()
    print()
    
    example_with_config_file()
    print()
    
    print("🎉 Todos los ejemplos completados!")
    print("📁 Revisa la carpeta 'example-reports' para ver los reportes generados")
    print("🌐 Abre los archivos .html en tu navegador para ver los resultados")