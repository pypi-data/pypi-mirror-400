#!/usr/bin/env python3
"""
Sistema de reportes HTML personalizado para Hakalab Framework
Genera reportes con gráficos, screenshots y organización por features
Incluye logo de Haka Lab y configuración personalizable
"""
import json
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class HtmlReporter:
    """Generador de reportes HTML personalizados con branding de Haka Lab"""
    
    def __init__(self, output_dir: str = "html-reports", config_path: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Inicializar logger primero
        self.logger = logging.getLogger('hakalab_html_reporter')
        
        # Cargar configuración del reporte
        self.config = self._load_report_config(config_path)
        
        self.report_data = {
            'execution_info': {
                'start_time': None,
                'end_time': None,
                'duration': 0,
                'browser': 'chromium',
                'environment': 'test'
            },
            'summary': {
                'features': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0},
                'scenarios': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0},
                'steps': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'undefined': 0}
            },
            'features': []
        }
        
        self.current_feature = None
        self.current_scenario = None
    
    def _load_report_config(self, config_path: str = None) -> Dict[str, Any]:
        """Carga la configuración del reporte desde JSON"""
        default_config = {
            "report_info": {
                "title": "Reporte de Pruebas Haka Lab",
                "engineer": "Ingeniero QA",
                "execution_date": "auto",
                "product": "Nombre del Producto",
                "company": "Nombre de la Empresa",
                "version": "1.0.0",
                "environment": "Testing"
            },
            "logos": {
                "primary_logo": {
                    "enabled": True,
                    "path": self._get_haka_lab_logo(),
                    "alt": "Haka Lab Logo",
                    "width": "200px"
                },
                "secondary_logo": {
                    "enabled": False,
                    "path": "",
                    "alt": "Company Logo", 
                    "width": "200px"
                }
            },
            "styling": {
                "primary_color": "#2c3e50",
                "secondary_color": "#3498db",
                "accent_color": "#e74c3c",
                "success_color": "#27ae60",
                "warning_color": "#f39c12"
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge configs (user config overrides default)
                    self._deep_merge(default_config, user_config)
            except Exception as e:
                self.logger.warning(f"Error cargando configuración {config_path}: {e}")
        
        # Buscar archivo de configuración en ubicaciones comunes
        common_paths = [
            'report_config.json',
            'config/report_config.json',
            '.hakalab/report_config.json',
            os.path.expanduser('~/.hakalab/report_config.json')
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                        self._deep_merge(default_config, user_config)
                        self.logger.info(f"Configuración cargada desde: {path}")
                        break
                except Exception as e:
                    self.logger.warning(f"Error cargando configuración {path}: {e}")
        
        return default_config
    
    def _deep_merge(self, base_dict: dict, update_dict: dict):
        """Merge recursivo de diccionarios"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _get_haka_lab_logo(self) -> str:
        """Retorna el logo de Haka Lab en base64"""
        # Logo SVG de Haka Lab convertido a base64
        haka_lab_svg = """
        <svg width="200" height="80" viewBox="0 0 400 160" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="hakaGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#00bcd4;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#2196f3;stop-opacity:1" />
                </linearGradient>
            </defs>
            
            <!-- Haka Lab Logo -->
            <g fill="url(#hakaGradient)">
                <!-- H -->
                <rect x="20" y="30" width="12" height="60"/>
                <rect x="20" y="55" width="35" height="10"/>
                <rect x="43" y="30" width="12" height="60"/>
                
                <!-- a -->
                <circle cx="80" cy="70" r="15"/>
                <rect x="88" y="55" width="8" height="35"/>
                <rect x="72" y="75" width="16" height="8"/>
                
                <!-- k -->
                <rect x="120" y="30" width="12" height="60"/>
                <polygon points="132,55 145,42 155,42 142,55 155,68 145,68"/>
                <polygon points="132,65 145,78 155,78 142,65"/>
                
                <!-- a -->
                <circle cx="180" cy="70" r="15"/>
                <rect x="188" y="55" width="8" height="35"/>
                <rect x="172" y="75" width="16" height="8"/>
            </g>
            
            <!-- Lab -->
            <g fill="#34495e">
                <!-- L -->
                <rect x="240" y="30" width="12" height="60"/>
                <rect x="240" y="78" width="30" height="12"/>
                
                <!-- a -->
                <circle cx="290" cy="70" r="12"/>
                <rect x="296" y="58" width="6" height="32"/>
                <rect x="284" y="75" width="12" height="6"/>
                
                <!-- b -->
                <rect x="320" y="30" width="10" height="60"/>
                <ellipse cx="340" cy="55" rx="12" ry="10"/>
                <ellipse cx="340" cy="75" rx="12" ry="10"/>
            </g>
            
            <!-- Subtitle -->
            <text x="20" y="110" font-family="Arial, sans-serif" font-size="14" fill="#7f8c8d">
                CONTINUOUS VALUE DELIVERY
            </text>
        </svg>
        """
        
        # Convertir SVG a base64
        svg_bytes = haka_lab_svg.encode('utf-8')
        svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
        return f"data:image/svg+xml;base64,{svg_base64}"
    
    def configure_report_info(self, **kwargs):
        """Configura la información del reporte dinámicamente"""
        for key, value in kwargs.items():
            if key in self.config['report_info']:
                self.config['report_info'][key] = value
            elif key == 'secondary_logo_path':
                self.config['logos']['secondary_logo']['path'] = value
                self.config['logos']['secondary_logo']['enabled'] = bool(value)
            elif key == 'secondary_logo_alt':
                self.config['logos']['secondary_logo']['alt'] = value
    
    def set_secondary_logo(self, logo_path: str, alt_text: str = "Company Logo", width: str = "200px"):
        """Configura el logo secundario (empresa)"""
        if os.path.exists(logo_path):
            # Convertir imagen a base64
            with open(logo_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                file_ext = os.path.splitext(logo_path)[1].lower()
                mime_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml'
                }.get(file_ext, 'image/png')
                
                self.config['logos']['secondary_logo'] = {
                    'enabled': True,
                    'path': f"data:{mime_type};base64,{img_data}",
                    'alt': alt_text,
                    'width': width
                }
        else:
            self.logger.warning(f"Logo secundario no encontrado: {logo_path}")
    
    def create_config_template(self, output_path: str = "report_config.json"):
        """Crea un archivo de configuración template"""
        template_config = {
            "report_info": {
                "title": "Reporte de Pruebas Haka Lab",
                "engineer": "Tu Nombre Aquí",
                "execution_date": "auto",
                "product": "Nombre de tu Producto",
                "company": "Nombre de tu Empresa",
                "version": "1.0.0",
                "environment": "Testing"
            },
            "logos": {
                "primary_logo": {
                    "enabled": True,
                    "path": "auto",
                    "alt": "Haka Lab Logo",
                    "width": "150px"
                },
                "secondary_logo": {
                    "enabled": False,
                    "path": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                    "alt": "Logo de tu Empresa",
                    "width": "150px",
                    "note": "Reemplaza el path con tu logo en base64 o ruta de archivo. Para convertir a base64: https://www.base64-image.de/"
                }
            },
            "styling": {
                "primary_color": "#2c3e50",
                "secondary_color": "#3498db",
                "accent_color": "#e74c3c",
                "success_color": "#27ae60",
                "warning_color": "#f39c12"
            },
            "instructions": {
                "logos": "Para agregar tu logo empresarial:",
                "step1": "1. Convierte tu logo a base64 en: https://www.base64-image.de/",
                "step2": "2. Copia el resultado completo (data:image/png;base64,xxxxx)",
                "step3": "3. Pégalo en secondary_logo.path",
                "step4": "4. Cambia enabled a true",
                "alternative": "Alternativamente, puedes usar una ruta de archivo local"
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Template de configuración creado: {output_path}")
        print("📝 Edita este archivo para personalizar tu reporte")
        print("🎨 Para agregar tu logo empresarial:")
        print("   1. Convierte tu logo a base64 en: https://www.base64-image.de/")
        print("   2. Copia el resultado y pégalo en secondary_logo.path")
        print("   3. Cambia secondary_logo.enabled a true")
        return output_path
    
    def start_execution(self, browser: str = 'chromium', environment: str = 'test'):
        """Inicia el tracking de la ejecución"""
        self.report_data['execution_info']['start_time'] = datetime.now()
        self.report_data['execution_info']['browser'] = browser
        self.report_data['execution_info']['environment'] = environment
    
    def end_execution(self):
        """Finaliza el tracking de la ejecución"""
        end_time = datetime.now()
        self.report_data['execution_info']['end_time'] = end_time
        
        if self.report_data['execution_info']['start_time']:
            duration = end_time - self.report_data['execution_info']['start_time']
            self.report_data['execution_info']['duration'] = duration.total_seconds()
    
    def start_feature(self, feature_name: str, feature_description: str = "", tags: List[str] = None):
        """Inicia el tracking de un feature"""
        self.current_feature = {
            'name': feature_name,
            'description': feature_description,
            'tags': tags or [],
            'status': 'passed',  # Se actualizará según los escenarios
            'scenarios': [],
            'start_time': datetime.now(),
            'end_time': None,
            'duration': 0
        }
        
        self.report_data['features'].append(self.current_feature)
        self.report_data['summary']['features']['total'] += 1
    
    def end_feature(self):
        """Finaliza el tracking de un feature"""
        if self.current_feature:
            self.current_feature['end_time'] = datetime.now()
            if self.current_feature['start_time']:
                duration = self.current_feature['end_time'] - self.current_feature['start_time']
                self.current_feature['duration'] = duration.total_seconds()
            
            # Determinar estado del feature basado en escenarios
            failed_scenarios = [s for s in self.current_feature['scenarios'] if s['status'] == 'failed']
            skipped_scenarios = [s for s in self.current_feature['scenarios'] if s['status'] == 'skipped']
            
            if failed_scenarios:
                self.current_feature['status'] = 'failed'
                self.report_data['summary']['features']['failed'] += 1
            elif skipped_scenarios and len(skipped_scenarios) == len(self.current_feature['scenarios']):
                self.current_feature['status'] = 'skipped'
                self.report_data['summary']['features']['skipped'] += 1
            else:
                self.current_feature['status'] = 'passed'
                self.report_data['summary']['features']['passed'] += 1
    
    def start_scenario(self, scenario_name: str, tags: List[str] = None):
        """Inicia el tracking de un escenario"""
        self.current_scenario = {
            'name': scenario_name,
            'tags': tags or [],
            'status': 'passed',
            'steps': [],
            'screenshots': [],
            'start_time': datetime.now(),
            'end_time': None,
            'duration': 0,
            'error_message': None
        }
        
        if self.current_feature:
            self.current_feature['scenarios'].append(self.current_scenario)
        
        self.report_data['summary']['scenarios']['total'] += 1
    
    def end_scenario(self, status: str = 'passed', error_message: str = None):
        """Finaliza el tracking de un escenario"""
        if self.current_scenario:
            self.current_scenario['status'] = status
            self.current_scenario['error_message'] = error_message
            self.current_scenario['end_time'] = datetime.now()
            
            if self.current_scenario['start_time']:
                duration = self.current_scenario['end_time'] - self.current_scenario['start_time']
                self.current_scenario['duration'] = duration.total_seconds()
            
            # Actualizar contadores
            self.report_data['summary']['scenarios'][status] += 1
    
    def add_step(self, step_name: str, status: str = 'passed', error_message: str = None, 
                 screenshot_path: str = None):
        """Agrega un step al escenario actual"""
        step = {
            'name': step_name,
            'status': status,
            'error_message': error_message,
            'screenshot': None,
            'timestamp': datetime.now()
        }
        
        # Procesar screenshot si existe
        if screenshot_path and os.path.exists(screenshot_path):
            step['screenshot'] = self._encode_screenshot(screenshot_path)
        elif screenshot_path == 'fake_path':
            # Para el demo, usar screenshot de ejemplo
            step['screenshot'] = self._create_demo_screenshot(step_name, status)
        
        if self.current_scenario:
            self.current_scenario['steps'].append(step)
        
        # Actualizar contadores
        self.report_data['summary']['steps']['total'] += 1
        self.report_data['summary']['steps'][status] += 1
    
    def _create_demo_screenshot(self, step_name: str, status: str) -> str:
        """Crea un screenshot de demostración en SVG convertido a base64"""
        color = {
            'passed': '#27ae60',
            'failed': '#e74c3c',
            'skipped': '#f39c12'
        }.get(status, '#3498db')
        
        svg_content = f"""
        <svg width="300" height="200" viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{color};stop-opacity:0.1" />
                    <stop offset="100%" style="stop-color:{color};stop-opacity:0.3" />
                </linearGradient>
            </defs>
            <rect width="300" height="200" fill="url(#bg)" rx="8"/>
            <rect x="10" y="10" width="280" height="30" fill="{color}" rx="4"/>
            <text x="150" y="30" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle">
                Screenshot Demo - {status.upper()}
            </text>
            <text x="150" y="60" font-family="Arial, sans-serif" font-size="12" fill="#2c3e50" text-anchor="middle">
                Step: {step_name[:40]}...
            </text>
            <circle cx="150" cy="120" r="30" fill="{color}" opacity="0.3"/>
            <text x="150" y="125" font-family="Arial, sans-serif" font-size="20" fill="{color}" text-anchor="middle">
                📸
            </text>
            <text x="150" y="170" font-family="Arial, sans-serif" font-size="10" fill="#7f8c8d" text-anchor="middle">
                Demo Screenshot - {datetime.now().strftime('%H:%M:%S')}
            </text>
        </svg>
        """
        
        svg_bytes = svg_content.encode('utf-8')
        svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
        return svg_base64
    
    def add_screenshot(self, screenshot_path: str, description: str = ""):
        """Agrega un screenshot al escenario actual"""
        if self.current_scenario:
            screenshot_data = {
                'path': screenshot_path,
                'data': None,
                'description': description,
                'timestamp': datetime.now()
            }
            
            if os.path.exists(screenshot_path):
                screenshot_data['data'] = self._encode_screenshot(screenshot_path)
            elif screenshot_path == 'fake_path':
                # Para el demo, crear screenshot SVG
                screenshot_data['data'] = self._create_demo_scenario_screenshot(description)
            
            self.current_scenario['screenshots'].append(screenshot_data)
    
    def _create_demo_scenario_screenshot(self, description: str) -> str:
        """Crea un screenshot de scenario de demostración"""
        svg_content = f"""
        <svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="scenarioBg" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#3498db;stop-opacity:0.1" />
                    <stop offset="100%" style="stop-color:#2c3e50;stop-opacity:0.2" />
                </linearGradient>
            </defs>
            <rect width="400" height="300" fill="url(#scenarioBg)" rx="12"/>
            <rect x="15" y="15" width="370" height="40" fill="#3498db" rx="6"/>
            <text x="200" y="40" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">
                📸 Scenario Screenshot
            </text>
            <text x="200" y="80" font-family="Arial, sans-serif" font-size="14" fill="#2c3e50" text-anchor="middle">
                {description[:50]}
            </text>
            <rect x="50" y="100" width="300" height="150" fill="white" stroke="#ddd" stroke-width="2" rx="8"/>
            <rect x="60" y="110" width="280" height="20" fill="#ecf0f1" rx="4"/>
            <rect x="60" y="140" width="200" height="15" fill="#bdc3c7" rx="3"/>
            <rect x="60" y="165" width="250" height="15" fill="#bdc3c7" rx="3"/>
            <rect x="60" y="190" width="180" height="15" fill="#bdc3c7" rx="3"/>
            <circle cx="320" cy="180" r="25" fill="#27ae60" opacity="0.3"/>
            <text x="320" y="185" font-family="Arial, sans-serif" font-size="16" fill="#27ae60" text-anchor="middle">
                ✓
            </text>
            <text x="200" y="280" font-family="Arial, sans-serif" font-size="11" fill="#95a5a6" text-anchor="middle">
                Demo Screenshot - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            </text>
        </svg>
        """
        
        svg_bytes = svg_content.encode('utf-8')
        svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
        return svg_base64
    
    def _encode_screenshot(self, screenshot_path: str) -> str:
        """Codifica un screenshot en base64 para embebido en HTML"""
        try:
            with open(screenshot_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.warning(f"Error codificando screenshot {screenshot_path}: {e}")
            return None
    
    def generate_report(self, report_name: str = "test_report.html") -> str:
        """Genera el reporte HTML completo"""
        self.end_execution()
        
        html_content = self._generate_html()
        report_path = self.output_dir / report_name
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generar también JSON para debugging
        json_path = self.output_dir / f"{report_name.replace('.html', '.json')}"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, default=str)
        
        return str(report_path)
    
    def _generate_html(self) -> str:
        """Genera el contenido HTML del reporte"""
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hakalab Framework - Reporte de Pruebas</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_summary()}
        {self._generate_features_list()}
    </div>
    
    <script>
        {self._generate_javascript()}
    </script>
</body>
</html>
        """
    
    def _get_css_styles(self) -> str:
        """Retorna los estilos CSS del reporte con branding de Haka Lab"""
        colors = self.config['styling']
        
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, {colors['secondary_color']} 0%, {colors['primary_color']} 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: #1a1a1a;  /* Negro muy oscuro */
            color: white;
            padding: 20px 30px;
            position: relative;
            min-height: 200px;
        }}
        
        .logo-top-left {{
            position: absolute;
            top: 15px;
            left: 15px;
            z-index: 10;
            background: rgba(255, 255, 255, 0.1);
            padding: 8px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .logo-top-right {{
            position: absolute;
            top: 15px;
            right: 15px;
            z-index: 10;
            background: rgba(255, 255, 255, 0.1);
            padding: 8px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .logo-top-left img,
        .logo-top-right img {{
            max-height: 50px;
            max-width: 150px;
            object-fit: contain;
        }}
        
        .header-title {{
            text-align: center;
            margin: 40px 0 30px 0;
            padding: 0 180px; /* Espacio para los logos */
        }}
        
        .header-title h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
            background: linear-gradient(45deg, #00bcd4, #2196f3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header-title .subtitle {{
            font-size: 1.2em;
            opacity: 0.8;
        }}
        
        .report-info-section {{
            margin-top: 20px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .info-item {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .info-label {{
            font-size: 0.9em;
            opacity: 0.8;
            font-weight: 500;
        }}
        
        .info-value {{
            font-size: 1.1em;
            font-weight: 600;
            color: #ecf0f1;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
            transition: transform 0.3s ease;
            border-top: 4px solid {colors['secondary_color']};
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
        }}
        
        .summary-card h3 {{
            color: {colors['primary_color']};
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        
        .chart-and-stats {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }}
        
        .mini-chart {{
            flex-shrink: 0;
            width: 120px;
            height: 120px;
        }}
        
        .summary-stats {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            flex: 1;
        }}
        
        .stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        
        .stat-number {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
        }}
        
        .passed {{ color: {colors['success_color']}; }}
        .failed {{ color: {colors['accent_color']}; }}
        .skipped {{ color: {colors['warning_color']}; }}
        .undefined {{ color: #9b59b6; }}
        
        .features-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .features-section h2 {{
            color: {colors['primary_color']};
            margin-bottom: 20px;
            text-align: center;
            font-size: 2em;
        }}
        
        .feature {{
            background: white;
            margin-bottom: 20px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 5px solid {colors['secondary_color']};
        }}
        
        .feature-header {{
            padding: 20px;
            background: {colors['primary_color']};
            color: white;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.3s ease;
        }}
        
        .feature-header:hover {{
            background: #2c3e50;
        }}
        
        .feature-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .feature-status.passed {{ background: {colors['success_color']}; }}
        .feature-status.failed {{ background: {colors['accent_color']}; }}
        .feature-status.skipped {{ background: {colors['warning_color']}; }}
        
        .feature-content {{
            display: none;
            padding: 20px;
        }}
        
        .feature-content.active {{
            display: block;
        }}
        
        .scenario {{
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .scenario-header {{
            padding: 15px;
            background: #ecf0f1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }}
        
        .scenario-header:hover {{
            background: #d5dbdb;
        }}
        
        .scenario-info {{
            flex: 1;
        }}
        
        .scenario-meta {{
            display: flex;
            gap: 15px;
            margin-top: 8px;
            font-size: 0.85em;
            color: #666;
        }}
        
        .scenario-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            color: white;
        }}
        
        .scenario-status.passed {{ background: {colors['success_color']}; }}
        .scenario-status.failed {{ background: {colors['accent_color']}; }}
        .scenario-status.skipped {{ background: {colors['warning_color']}; }}
        
        .scenario-content {{
            display: none;
            padding: 15px;
        }}
        
        .scenario-content.active {{
            display: block;
        }}
        
        .scenario-error {{
            background: #fadbd8;
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9em;
            color: #c0392b;
            border-left: 4px solid {colors['accent_color']};
        }}
        
        .steps-list {{
            margin-bottom: 20px;
        }}
        
        .steps-list h4 {{
            color: {colors['primary_color']};
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .step {{
            margin-bottom: 10px;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .step.passed {{ 
            background: #d5f4e6; 
            border-left: 4px solid {colors['success_color']}; 
        }}
        .step.failed {{ 
            background: #fadbd8; 
            border-left: 4px solid {colors['accent_color']}; 
        }}
        .step.skipped {{ 
            background: #fef9e7; 
            border-left: 4px solid {colors['warning_color']}; 
        }}
        
        .step-content {{
            padding: 12px;
        }}
        
        .step-text {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .step-name {{
            flex: 1;
            font-weight: 500;
        }}
        
        .step-status-badge {{
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: bold;
            color: white;
        }}
        
        .step-status-badge.passed {{ background: {colors['success_color']}; }}
        .step-status-badge.failed {{ background: {colors['accent_color']}; }}
        .step-status-badge.skipped {{ background: {colors['warning_color']}; }}
        
        .step-screenshot {{
            margin-top: 10px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 6px;
            border-left: 3px solid {colors['secondary_color']};
        }}
        
        .step-screenshot-label {{
            font-size: 0.8em;
            color: #666;
            margin-bottom: 5px;
            font-weight: 500;
        }}
        
        .step-screenshot img {{
            max-width: 250px;
            max-height: 180px;
            border-radius: 6px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
            cursor: pointer;
            transition: all 0.3s ease;
            object-fit: cover;
            border: 2px solid #e9ecef;
        }}
        
        .step-screenshot img:hover {{
            transform: scale(1.02);
            box-shadow: 0 5px 20px rgba(0,0,0,0.25);
            border-color: {colors['secondary_color']};
        }}
        
        .step.failed .step-screenshot {{
            border-left-color: {colors['accent_color']};
        }}
        
        .step.failed .step-screenshot img {{
            border-color: {colors['accent_color']};
        }}
        
        .step.skipped .step-screenshot {{
            border-left-color: {colors['warning_color']};
        }}
        
        .step.skipped .step-screenshot img {{
            border-color: {colors['warning_color']};
        }}
        
        .step-error {{
            background: #fadbd8;
            padding: 10px;
            margin-top: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9em;
            color: #c0392b;
        }}
        
        .scenario-screenshots {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 2px solid #e9ecef;
        }}
        
        .scenario-screenshots h5 {{
            color: {colors['primary_color']};
            margin-bottom: 8px;
            font-size: 1em;
        }}
        
        .scenario-screenshots-note {{
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 4px;
            margin-bottom: 15px;
            border-left: 3px solid {colors['secondary_color']};
        }}
        
        .scenario-screenshots-note small {{
            color: #6c757d;
            font-style: italic;
        }}
        
        .screenshots {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
        }}
        
        .screenshot {{
            text-align: center;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .screenshot:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        
        .screenshot img {{
            max-width: 100%;
            height: 120px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.3s ease;
            object-fit: cover;
            border: 1px solid #dee2e6;
        }}
        
        .screenshot img:hover {{
            transform: scale(1.02);
            border-color: {colors['secondary_color']};
        }}
        
        .screenshot-caption {{
            margin-top: 8px;
            font-size: 0.8em;
            color: #666;
            line-height: 1.3;
        }}
        
        .screenshot-caption strong {{
            color: {colors['primary_color']};
        }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            overflow-y: auto; /* Scroll vertical cuando sea necesario */
            overflow-x: hidden; /* Sin scroll horizontal */
            padding: 0; /* Sin padding para evitar problemas de centrado */
            box-sizing: border-box;
        }}
        
        .modal-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start; /* Cambiar a flex-start para evitar cortes */
            min-height: 100vh; /* Usar viewport height */
            padding: 60px 20px 40px 20px; /* Más padding arriba para el botón cerrar */
            box-sizing: border-box;
        }}
        
        .modal-content {{
            max-width: 90%; /* Reducir un poco para mejor visualización */
            max-height: none; /* Permitir altura natural */
            width: auto; /* Mantener proporciones */
            height: auto; /* Mantener proporciones */
            object-fit: contain; /* Mantener aspecto sin distorsión */
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            cursor: zoom-out; /* Cambiar cursor para indicar que se puede cerrar */
            transition: transform 0.3s ease;
            margin: auto; /* Centrar automáticamente */
        }}
        
        .modal-content:hover {{
            transform: scale(1.02);
        }}
        
        .modal-info {{
            margin-top: 15px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            color: #f1f1f1;
            font-size: 14px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .close {{
            position: fixed; /* Fijo en la pantalla */
            top: 20px;
            right: 40px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            z-index: 1001;
            background: rgba(0,0,0,0.7);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }}
        
        .close:hover {{
            background: rgba(255,255,255,0.2);
            transform: scale(1.1);
        }}
        
        /* Responsive para móviles */
        @media (max-width: 768px) {{
            .modal {{
                padding: 0; /* Sin padding en móviles */
            }}
            
            .modal-container {{
                padding: 50px 10px 30px 10px; /* Menos padding en móviles */
            }}
            
            .modal-content {{
                max-width: 95%;
                border-radius: 4px; /* Bordes más pequeños en móviles */
            }}
            
            .modal-info {{
                font-size: 12px;
                padding: 8px 15px;
                margin-top: 15px;
            }}
            
            .close {{
                top: 10px;
                right: 15px;
                font-size: 30px;
                width: 40px;
                height: 40px;
            }}
        }}
        
        /* Para pantallas muy pequeñas */
        @media (max-width: 480px) {{
            .modal-container {{
                padding: 45px 5px 25px 5px;
            }}
            
            .modal-content {{
                max-width: 98%;
            }}
            
            .close {{
                top: 5px;
                right: 10px;
                font-size: 24px;
                width: 35px;
                height: 35px;
            }}
        }}
        
        .close:hover {{
            color: #bbb;
        }}
        
        .execution-info {{
            background: #ecf0f1;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 8px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .execution-info .info-item {{
            text-align: center;
        }}
        
        .execution-info .info-label {{
            font-weight: bold;
            color: {colors['primary_color']};
            margin-bottom: 5px;
        }}
        
        .execution-info .info-value {{
            color: #666;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .header {{
                padding: 15px;
                min-height: 180px;
            }}
            
            .logo-top-left,
            .logo-top-right {{
                position: static;
                display: inline-block;
                margin: 5px;
            }}
            
            .header-title {{
                padding: 0 20px;
                margin: 20px 0;
            }}
            
            .header-title h1 {{
                font-size: 2em;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .summary {{
                grid-template-columns: 1fr;
                padding: 20px;
            }}
            
            .chart-and-stats {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .mini-chart {{
                width: 100px;
                height: 100px;
            }}
            
            .scenario-meta {{
                flex-direction: column;
                gap: 5px;
            }}
            
            .step-text {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}
            
            .screenshots {{
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            }}
        }}
        
        @media (max-width: 480px) {{
            .header {{
                text-align: center;
                min-height: 160px;
            }}
            
            .logo-top-left,
            .logo-top-right {{
                position: relative;
                top: auto;
                left: auto;
                right: auto;
                display: block;
                margin: 10px auto;
                width: fit-content;
            }}
            
            .header-title {{
                padding: 0 10px;
            }}
            
            .summary {{
                padding: 15px;
            }}
            
            .summary-card {{
                padding: 20px;
            }}
            
            .step-screenshot img {{
                max-width: 150px;
                max-height: 100px;
            }}
        }}
        """
    
    def _generate_header(self) -> str:
        """Genera el header del reporte con logos en las esquinas superiores"""
        report_info = self.config['report_info']
        logos = self.config['logos']
        
        # Procesar fecha de ejecución
        execution_date = report_info['execution_date']
        if execution_date == 'auto':
            execution_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Logo primario (Haka Lab) - esquina superior izquierda
        primary_logo_html = ""
        if logos['primary_logo']['enabled'] and logos['primary_logo']['path']:
            primary_logo_html = f"""
            <div class="logo-top-left">
                <img src="{logos['primary_logo']['path']}" 
                     alt="{logos['primary_logo']['alt']}" 
                     style="max-width: {logos['primary_logo']['width']}; height: auto;">
            </div>
            """
        
        # Logo secundario (Empresa) - esquina superior derecha
        secondary_logo_html = ""
        if logos['secondary_logo']['enabled'] and logos['secondary_logo']['path']:
            secondary_logo_html = f"""
            <div class="logo-top-right">
                <img src="{logos['secondary_logo']['path']}" 
                     alt="{logos['secondary_logo']['alt']}" 
                     style="max-width: {logos['secondary_logo']['width']}; height: auto;">
            </div>
            """
        
        return f"""
        <div class="header">
            <!-- Logos en las esquinas superiores -->
            {primary_logo_html}
            {secondary_logo_html}
            
            <!-- Título Principal -->
            <div class="header-title">
                <h1>{report_info['title']}</h1>
                <div class="subtitle">Reporte de Pruebas Automatizadas</div>
            </div>
            
            <!-- Información del Proyecto -->
            <div class="report-info-section">
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">👨‍💻 Ingeniero:</span>
                        <span class="info-value">{report_info['engineer']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">📅 Fecha:</span>
                        <span class="info-value">{execution_date}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">📦 Producto:</span>
                        <span class="info-value">{report_info['product']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🏢 Empresa:</span>
                        <span class="info-value">{report_info['company']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🔖 Versión:</span>
                        <span class="info-value">{report_info['version']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">🌍 Ambiente:</span>
                        <span class="info-value">{report_info['environment']}</span>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_summary(self) -> str:
        """Genera la sección de resumen con gráficos integrados en las cards"""
        execution_info = self._generate_execution_info()
        
        features = self.report_data['summary']['features']
        scenarios = self.report_data['summary']['scenarios']
        steps = self.report_data['summary']['steps']
        
        return f"""
        <div class="summary">
            {execution_info}
            
            <div class="summary-card">
                <h3>📁 Features</h3>
                <div class="chart-and-stats">
                    <div class="mini-chart">
                        <canvas id="featuresChart" width="120" height="120"></canvas>
                    </div>
                    <div class="summary-stats">
                        <div class="stat">
                            <div class="stat-number passed">{features['passed']}</div>
                            <div class="stat-label">Passed</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number failed">{features['failed']}</div>
                            <div class="stat-label">Failed</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number skipped">{features['skipped']}</div>
                            <div class="stat-label">Skipped</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="summary-card">
                <h3>🎬 Scenarios</h3>
                <div class="chart-and-stats">
                    <div class="mini-chart">
                        <canvas id="scenariosChart" width="120" height="120"></canvas>
                    </div>
                    <div class="summary-stats">
                        <div class="stat">
                            <div class="stat-number passed">{scenarios['passed']}</div>
                            <div class="stat-label">Passed</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number failed">{scenarios['failed']}</div>
                            <div class="stat-label">Failed</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number skipped">{scenarios['skipped']}</div>
                            <div class="stat-label">Skipped</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="summary-card">
                <h3>👣 Steps</h3>
                <div class="chart-and-stats">
                    <div class="mini-chart">
                        <canvas id="stepsChart" width="120" height="120"></canvas>
                    </div>
                    <div class="summary-stats">
                        <div class="stat">
                            <div class="stat-number passed">{steps['passed']}</div>
                            <div class="stat-label">Passed</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number failed">{steps['failed']}</div>
                            <div class="stat-label">Failed</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number skipped">{steps['skipped']}</div>
                            <div class="stat-label">Skipped</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_execution_info(self) -> str:
        """Genera la información de ejecución"""
        info = self.report_data['execution_info']
        
        start_time = info['start_time'].strftime('%Y-%m-%d %H:%M:%S') if info['start_time'] else 'N/A'
        end_time = info['end_time'].strftime('%Y-%m-%d %H:%M:%S') if info['end_time'] else 'N/A'
        duration = f"{info['duration']:.2f}s" if info['duration'] else 'N/A'
        
        return f"""
        <div class="execution-info">
            <div class="info-item">
                <div class="info-label">🕐 Inicio</div>
                <div class="info-value">{start_time}</div>
            </div>
            <div class="info-item">
                <div class="info-label">🏁 Fin</div>
                <div class="info-value">{end_time}</div>
            </div>
            <div class="info-item">
                <div class="info-label">⏱️ Duración</div>
                <div class="info-value">{duration}</div>
            </div>
            <div class="info-item">
                <div class="info-label">🌐 Navegador</div>
                <div class="info-value">{info['browser'].title()}</div>
            </div>
        </div>
        """
    
    def _generate_charts(self) -> str:
        """Genera la sección de gráficos"""
        return f"""
        <div class="charts-section">
            <h2>📊 Estadísticas Visuales</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Features por Estado</h3>
                    <canvas id="featuresChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h3>Scenarios por Estado</h3>
                    <canvas id="scenariosChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h3>Steps por Estado</h3>
                    <canvas id="stepsChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h3>Distribución General</h3>
                    <canvas id="overallChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
        """
    
    def _generate_features_list(self) -> str:
        """Genera la lista de features con escenarios y screenshots en steps"""
        features_html = ""
        
        for i, feature in enumerate(self.report_data['features']):
            scenarios_html = ""
            
            for j, scenario in enumerate(feature['scenarios']):
                steps_html = ""
                
                for step in scenario['steps']:
                    error_html = ""
                    if step['error_message']:
                        error_html = f'<div class="step-error">{step["error_message"]}</div>'
                    
                    # Screenshot del step si existe
                    screenshot_html = ""
                    if step.get('screenshot'):
                        screenshot_html = f"""
                        <div class="step-screenshot">
                            <div class="step-screenshot-label">📸 Screenshot de este paso:</div>
                            <img src="data:image/png;base64,{step['screenshot']}" 
                                 alt="Screenshot del paso: {step['name']}" 
                                 onclick="openModal(this.src)"
                                 title="Click para ampliar - Paso: {step['name'][:50]}...">
                        </div>
                        """
                    
                    steps_html += f"""
                    <div class="step {step['status']}">
                        <div class="step-content">
                            <div class="step-text">
                                <span class="step-name">{step['name']}</span>
                                <span class="step-status-badge {step['status']}">{step['status'].upper()}</span>
                            </div>
                            {screenshot_html}
                        </div>
                        {error_html}
                    </div>
                    """
                
                # Screenshots adicionales del scenario (no asociados a steps específicos)
                scenario_screenshots_html = ""
                if scenario['screenshots']:
                    scenario_screenshots_html = f"""
                    <div class="scenario-screenshots">
                        <h5>📷 Screenshots Adicionales del Scenario:</h5>
                        <div class="scenario-screenshots-note">
                            <small>Estas capturas son generales del scenario, no están asociadas a steps específicos.</small>
                        </div>
                        <div class="screenshots">
                    """
                    for k, screenshot in enumerate(scenario['screenshots']):
                        if screenshot['data']:
                            scenario_screenshots_html += f"""
                            <div class="screenshot">
                                <img src="data:image/png;base64,{screenshot['data']}" 
                                     alt="Screenshot general del scenario" 
                                     onclick="openModal(this.src)"
                                     title="Screenshot general: {screenshot['description']}">
                                <div class="screenshot-caption">
                                    <strong>General #{k+1}</strong><br>
                                    {screenshot['description'] or f'Screenshot del scenario'}
                                </div>
                            </div>
                            """
                    scenario_screenshots_html += '</div></div>'
                
                duration = f"{scenario['duration']:.2f}s" if scenario['duration'] else 'N/A'
                error_message = f'<div class="scenario-error">{scenario["error_message"]}</div>' if scenario['error_message'] else ''
                
                # Contar screenshots totales: del scenario + de los steps
                scenario_screenshots = len(scenario['screenshots'])
                step_screenshots = sum(1 for step in scenario['steps'] if step.get('screenshot'))
                total_screenshots = scenario_screenshots + step_screenshots
                
                scenarios_html += f"""
                <div class="scenario">
                    <div class="scenario-header" onclick="toggleScenario({i}, {j})">
                        <div class="scenario-info">
                            <strong>{scenario['name']}</strong>
                            <div class="scenario-meta">
                                <span>⏱️ {duration}</span>
                                <span>👣 {len(scenario['steps'])} steps</span>
                                <span>📸 {total_screenshots} screenshots</span>
                                <span>🏷️ {', '.join(scenario.get('tags', []))}</span>
                            </div>
                        </div>
                        <span class="scenario-status {scenario['status']}">{scenario['status'].upper()}</span>
                    </div>
                    <div class="scenario-content" id="scenario-{i}-{j}">
                        {error_message}
                        <div class="steps-list">
                            <h4>📋 Steps:</h4>
                            {steps_html}
                        </div>
                        {scenario_screenshots_html}
                    </div>
                </div>
                """
            
            duration = f"{feature['duration']:.2f}s" if feature['duration'] else 'N/A'
            
            features_html += f"""
            <div class="feature">
                <div class="feature-header" onclick="toggleFeature({i})">
                    <div class="feature-info">
                        <h3>{feature['name']}</h3>
                        <div class="feature-meta">
                            <span>{feature['description']}</span>
                            <div class="feature-stats">
                                <span>⏱️ {duration}</span>
                                <span>🎬 {len(feature['scenarios'])} scenarios</span>
                                <span>🏷️ {', '.join(feature.get('tags', []))}</span>
                            </div>
                        </div>
                    </div>
                    <span class="feature-status {feature['status']}">{feature['status'].upper()}</span>
                </div>
                <div class="feature-content" id="feature-{i}">
                    {scenarios_html}
                </div>
            </div>
            """
        
        return f"""
        <div class="features-section">
            <h2>📁 Features y Scenarios</h2>
            {features_html}
        </div>
        
        <!-- Modal mejorado para screenshots -->
        <div id="imageModal" class="modal">
            <span class="close" onclick="closeModal()" title="Cerrar (ESC)">&times;</span>
            <div class="modal-container">
                <img class="modal-content" id="modalImage" alt="Screenshot ampliado">
                <div class="modal-info" id="modalInfo">
                    <p>💡 <strong>Tip:</strong> Presiona ESC para cerrar o haz clic fuera de la imagen</p>
                </div>
            </div>
        </div>
        """
    
    def _generate_javascript(self) -> str:
        """Genera el JavaScript para interactividad y mini gráficos"""
        features = self.report_data['summary']['features']
        scenarios = self.report_data['summary']['scenarios']
        steps = self.report_data['summary']['steps']
        
        return f"""
        // Datos para los gráficos
        const featuresData = {json.dumps(features)};
        const scenariosData = {json.dumps(scenarios)};
        const stepsData = {json.dumps(steps)};
        
        // Configuración de colores
        const colors = {{
            passed: '#27ae60',
            failed: '#e74c3c',
            skipped: '#f39c12',
            undefined: '#9b59b6'
        }};
        
        // Función para crear mini gráfico de dona
        function createMiniDoughnutChart(ctx, data, title) {{
            const labels = Object.keys(data).filter(key => key !== 'total' && data[key] > 0);
            const values = labels.map(label => data[label]);
            const backgroundColors = labels.map(label => colors[label]);
            
            return new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
                    datasets: [{{
                        data: values,
                        backgroundColor: backgroundColors,
                        borderWidth: 0,
                        cutout: '60%'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const label = context.label;
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{label}}: ${{value}} (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }},
                    animation: {{
                        animateRotate: true,
                        duration: 1000
                    }}
                }}
            }});
        }}
        
        // Inicializar gráficos cuando la página cargue
        document.addEventListener('DOMContentLoaded', function() {{
            // Mini gráficos en las cards
            createMiniDoughnutChart(
                document.getElementById('featuresChart').getContext('2d'),
                featuresData,
                'Features'
            );
            
            createMiniDoughnutChart(
                document.getElementById('scenariosChart').getContext('2d'),
                scenariosData,
                'Scenarios'
            );
            
            createMiniDoughnutChart(
                document.getElementById('stepsChart').getContext('2d'),
                stepsData,
                'Steps'
            );
        }});
        
        // Funciones de interactividad
        function toggleFeature(index) {{
            const content = document.getElementById(`feature-${{index}}`);
            content.classList.toggle('active');
        }}
        
        function toggleScenario(featureIndex, scenarioIndex) {{
            const content = document.getElementById(`scenario-${{featureIndex}}-${{scenarioIndex}}`);
            content.classList.toggle('active');
        }}
        
        function openModal(src) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const modalInfo = document.getElementById('modalInfo');
            
            // Mostrar modal
            modal.style.display = 'block';
            
            // Configurar imagen sin transformaciones problemáticas
            modalImg.src = src;
            modalImg.style.transform = 'none'; // Eliminar cualquier transformación previa
            
            // Actualizar información del modal
            modalInfo.innerHTML = '<p>💡 <strong>Tip:</strong> Presiona ESC para cerrar, haz clic fuera de la imagen, o haz clic en la X</p>';
            
            // Prevenir scroll del body cuando el modal está abierto
            document.body.style.overflow = 'hidden';
            
            // Agregar evento para cerrar con ESC
            document.addEventListener('keydown', handleEscKey);
            
            // Scroll al inicio del modal para asegurar que se vea completo
            modal.scrollTop = 0;
        }}
        
        function closeModal() {{
            const modal = document.getElementById('imageModal');
            modal.style.display = 'none';
            
            // Restaurar scroll del body
            document.body.style.overflow = 'auto';
            
            // Remover evento ESC
            document.removeEventListener('keydown', handleEscKey);
        }}
        
        function handleEscKey(event) {{
            if (event.key === 'Escape') {{
                closeModal();
            }}
        }}
        
        // Cerrar modal al hacer clic fuera de la imagen o en la imagen misma
        window.onclick = function(event) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            
            // Cerrar si se hace clic en el fondo del modal o en la imagen
            if (event.target === modal || event.target === modalImg) {{
                closeModal();
            }}
        }}
        
        // Expandir/contraer todos los features
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey && e.key === 'e') {{
                e.preventDefault();
                const features = document.querySelectorAll('.feature-content');
                const allExpanded = Array.from(features).every(f => f.classList.contains('active'));
                
                features.forEach(feature => {{
                    if (allExpanded) {{
                        feature.classList.remove('active');
                    }} else {{
                        feature.classList.add('active');
                    }}
                }});
            }}
        }});
        """

# Instancia global del reporter
html_reporter = HtmlReporter(output_dir=os.getenv('HTML_REPORTS_DIR', 'html-reports'))