#!/usr/bin/env python3
"""
Configurador de environment MINIMO para Playwright + Behave
Solo lo ultra esencial
"""
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

# Imports mínimos necesarios para que funcionen los steps
from .element_locator import ElementLocator
from .variable_manager import VariableManager
# from .allure_config import setup_allure_environment, validate_allure_setup


class FrameworkConfig:
    """Configurador MINIMO del framework"""
    
    def __init__(self, env_file: Optional[str] = None):
        """Inicializa la configuración MINIMA del framework"""
        # Cargar variables de entorno básicas
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        self.config = self._load_config()
        self.playwright = None
        self.browser = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde variables de entorno"""
        return {
            # Configuración de navegador
            'browser': os.getenv('BROWSER', 'chromium').lower(),
            'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
            'timeout': int(os.getenv('TIMEOUT', '30000')),
            'viewport_width': int(os.getenv('VIEWPORT_WIDTH', '1920')),
            'viewport_height': int(os.getenv('VIEWPORT_HEIGHT', '1080')),
            'device_scale_factor': float(os.getenv('DEVICE_SCALE_FACTOR', '1')),
            'slow_mo': int(os.getenv('SLOW_MO', '0')),
            
            # Configuración de video
            'record_video': os.getenv('RECORD_VIDEO', 'false').lower() == 'true',
            'video_dir': os.getenv('VIDEO_DIR', 'videos'),
            'video_size': os.getenv('VIDEO_SIZE', '1280x720'),
            'video_mode': os.getenv('VIDEO_MODE', 'retain-on-failure'),  # on, off, retain-on-failure
            'cleanup_old_videos': os.getenv('CLEANUP_OLD_VIDEOS', 'true').lower() == 'true',
            'video_max_age_hours': int(os.getenv('VIDEO_MAX_AGE_HOURS', '168')),  # 7 días
            
            # URLs y rutas
            'base_url': os.getenv('BASE_URL', ''),
            'json_poms_path': os.getenv('JSON_POMS_PATH', 'json_poms'),
            
            # Reportes y archivos
            'allure_results_dir': os.getenv('ALLURE_RESULTS_DIR', 'allure-results'),
            'html_reports_dir': os.getenv('HTML_REPORTS_DIR', 'html-reports'),
            'screenshots_dir': os.getenv('SCREENSHOTS_DIR', 'screenshots'),
            'downloads_dir': os.getenv('DOWNLOADS_DIR', 'downloads'),
            
            # Configuración de logging
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', ''),
            
            # Configuración de red
            'ignore_https_errors': os.getenv('IGNORE_HTTPS_ERRORS', 'false').lower() == 'true',
            'user_agent': os.getenv('USER_AGENT', ''),
            
            # Configuración de pruebas
            'auto_screenshot_on_failure': os.getenv('AUTO_SCREENSHOT_ON_FAILURE', 'true').lower() == 'true',
            'auto_wait_for_load': os.getenv('AUTO_WAIT_FOR_LOAD', 'true').lower() == 'true',
            'retry_failed_steps': int(os.getenv('RETRY_FAILED_STEPS', '0')),
            
            # Configuración de paralelismo
            'parallel_workers': int(os.getenv('PARALLEL_WORKERS', '4')),
            'max_browser_instances': int(os.getenv('MAX_BROWSER_INSTANCES', '10')),
            'browser_pool_size': int(os.getenv('BROWSER_POOL_SIZE', '5')),
            'worker_timeout': int(os.getenv('WORKER_TIMEOUT', '300')),
            
            # Variables de datos de prueba (las más comunes)
            'test_email': os.getenv('TEST_EMAIL', ''),
            'test_password': os.getenv('TEST_PASSWORD', ''),
            'test_user_name': os.getenv('TEST_USER_NAME', ''),
            'api_base_url': os.getenv('API_BASE_URL', ''),
        }
    
    def setup_playwright(self) -> Browser:
        """Configura e inicializa Playwright con soporte para concurrencia"""
        self.playwright = sync_playwright().start()
        
        browser_options = {
            'headless': self.config['headless'],
            'slow_mo': self.config['slow_mo'],
        }
        
        if self.config['downloads_dir']:
            browser_options['downloads_path'] = self.config['downloads_dir']
        
        # Configuraciones adicionales para paralelismo
        if self.config['headless']:
            # En modo headless, optimizar para paralelismo
            browser_options['args'] = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--max_old_space_size=4096'
            ]
        
        # Seleccionar navegador
        if self.config['browser'] == 'firefox':
            self.browser = self.playwright.firefox.launch(**browser_options)
        elif self.config['browser'] == 'webkit':
            self.browser = self.playwright.webkit.launch(**browser_options)
        else:  # chromium por defecto
            self.browser = self.playwright.chromium.launch(**browser_options)
        
        return self.browser
    
    def create_context(self) -> BrowserContext:
        """Crea un nuevo contexto de navegador con la configuración"""
        if not self.browser:
            raise RuntimeError("Browser not initialized. Call setup_playwright() first.")
        
        context_options = {
            'viewport': {
                'width': self.config['viewport_width'],
                'height': self.config['viewport_height']
            },
            'device_scale_factor': self.config['device_scale_factor'],
            'ignore_https_errors': self.config['ignore_https_errors'],
        }
        
        # Configuración de video automática
        if self.config['record_video']:
            video_dir = self.config['video_dir']
            
            # Crear directorio de videos si no existe
            os.makedirs(video_dir, exist_ok=True)
            
            # Limpiar videos antiguos si está habilitado
            if self.config['cleanup_old_videos']:
                self._cleanup_old_videos(video_dir)
            
            # Configurar grabación de video con la sintaxis correcta de Playwright
            video_size = self.config['video_size']
            width, height = map(int, video_size.split('x'))
            
            context_options['record_video_dir'] = video_dir
            context_options['record_video_size'] = {'width': width, 'height': height}
        
        if self.config['base_url']:
            context_options['base_url'] = self.config['base_url']
        
        if self.config['user_agent']:
            context_options['user_agent'] = self.config['user_agent']
        
        return self.browser.new_context(**context_options)
    
    def create_page(self, context: Optional[BrowserContext] = None) -> Page:
        """Crea página MINIMA"""
        if context is None:
            context = self.create_context()
        
        page = context.new_page()
        page.set_default_timeout(self.config['timeout'])
        
        return page
    
    def setup_logging(self) -> logging.Logger:
        """Configura el sistema de logging"""
        logger = logging.getLogger('hakalab_framework')
        logger.setLevel(logging.INFO)  # Hardcoded para simplicidad
        
        # Evitar duplicar handlers
        if not logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def get_test_data(self) -> Dict[str, str]:
        """Retorna los datos de prueba configurados"""
        return {
            'email': self.config.get('test_email', ''),
            'password': self.config.get('test_password', ''),
            'user_name': self.config.get('test_user_name', ''),
            'api_base_url': self.config.get('api_base_url', ''),
            'base_url': self.config.get('base_url', ''),
        }
    
    def _cleanup_old_videos(self, video_dir: str):
        """Limpia videos antiguos según la configuración"""
        try:
            import time
            from pathlib import Path
            
            max_age_hours = self.config['video_max_age_hours']
            max_age_seconds = max_age_hours * 3600
            current_time = time.time()
            
            video_path = Path(video_dir)
            if not video_path.exists():
                return
            
            deleted_count = 0
            for video_file in video_path.glob('*.webm'):
                file_age = current_time - video_file.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        video_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"⚠️ No se pudo eliminar video antiguo {video_file}: {e}")
            
            if deleted_count > 0:
                print(f"🧹 Videos antiguos eliminados: {deleted_count} archivos")
                
        except Exception as e:
            print(f"⚠️ Error limpiando videos antiguos: {e}")
    
    def cleanup(self):
        """Cleanup ULTRA MINIMO"""
        # Cerrar browser básico
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
            self.browser = None
        
        # Detener playwright básico
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass
            self.playwright = None


def setup_framework_context(context, env_file: Optional[str] = None):
    """Setup completo del framework SIN cleanup_error"""
    
    # Inicializar configuración
    context.framework_config = FrameworkConfig(env_file)
    
    # Configurar logging
    context.logger = context.framework_config.setup_logging()
    
    # Configurar Playwright
    context.browser = context.framework_config.setup_playwright()
    
    # Inicializar utilidades del framework
    from .element_locator import ElementLocator
    from .variable_manager import VariableManager
    context.element_locator = ElementLocator()
    context.variable_manager = VariableManager()
    
    # Configurar test data (SIN context.config para evitar cleanup_error)
    try:
        context.test_data = context.framework_config.get_test_data()
        # NO asignar context.config - causa cleanup_error
    except Exception as e:
        context.logger.warning(f"Error configurando datos de prueba: {e}")
        context.test_data = {}
    
    context.logger.info("Framework configurado correctamente")


def setup_scenario_context(context, scenario):
    """Setup completo de escenario"""
    
    # Crear nueva página para el escenario
    context.page = context.framework_config.create_page()
    
    # Configurar funciones helper simplificadas
    from .context_helpers import setup_context_helpers, add_bulk_operations, setup_advanced_helpers
    setup_context_helpers(context)
    add_bulk_operations(context)
    setup_advanced_helpers(context)
    
    # Configurar tags si es necesario
    try:
        if hasattr(scenario, 'tags') and scenario.tags:
            if 'mobile' in [tag.lower() for tag in scenario.tags]:
                # Configurar viewport móvil
                context.page.set_viewport_size({"width": 375, "height": 667})
    except Exception as e:
        context.logger.warning(f"Error configurando tags: {e}")
    
    context.logger.info(f"Iniciando escenario: {scenario.name}")

