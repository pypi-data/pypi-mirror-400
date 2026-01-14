"""
Todos los pasos del framework Hakalab
Importación automática de todos los steps disponibles
"""
import os

# Steps básicos existentes
from .navigation_steps import *
from .interaction_steps import *
from .assertion_steps import *
from .scroll_steps import *
from .wait_steps import *
from .data_extraction_steps import *
from .variable_steps import *
from .window_steps import *
from .advanced_steps import *

# Nuevos steps avanzados
from .drag_drop_steps import *
from .combobox_steps import *
from .iframe_steps import *
from .modal_steps import *
from .file_steps import *
from .table_steps import *
from .keyboard_mouse_steps import *

# Steps específicos para Salesforce
from .salesforce_steps import *

# Steps para variables de entorno
from .environment_steps import *

# Nuevos steps avanzados v1.2.12
from .csv_file_steps import *
from .timing_steps import *
from .advanced_input_steps import *

# Solo mostrar mensajes si está habilitado explícitamente
if os.getenv('HAKALAB_SHOW_STEPS') == 'true':
    print("✅ Hakalab Framework Steps cargados:")
    print("   📍 Navigation Steps - Navegación y URLs")
    print("   🖱️ Interaction Steps - Clicks, hover, fill")
    print("   ✅ Assertion Steps - Verificaciones y validaciones")
    print("   📜 Scroll Steps - Desplazamiento de página")
    print("   ⏱️ Wait Steps - Esperas y timeouts")
    print("   📊 Data Extraction Steps - Extracción de datos")
    print("   🔤 Variable Steps - Manejo de variables")
    print("   🪟 Window Steps - Manejo de ventanas y tabs")
    print("   🔧 Advanced Steps - JavaScript y screenshots")
    print("   🎯 Drag & Drop Steps - Arrastrar y soltar")
    print("   📋 Combobox Steps - Selects y dropdowns avanzados")
    print("   🖼️ iFrame Steps - Interacción con iframes")
    print("   💬 Modal Steps - Modales y diálogos")
    print("   📁 File Steps - Upload, download y verificación")
    print("   📊 Table Steps - Tablas avanzadas")
    print("   ⌨️ Keyboard/Mouse Steps - Interacciones avanzadas")
    print("   ☁️ Salesforce Steps - Automatización específica de Salesforce")
    print("   🌍 Environment Steps - Manejo de variables de entorno")
    print("   📊 CSV File Steps - Manejo y análisis de archivos CSV")
    print("   ⏱️ Timing Steps - Control de tiempos y esperas avanzadas")
    print("   ⌨️ Advanced Input Steps - Interacción avanzada con campos de entrada")
    print("   🔤 Enhanced Variable Steps - Manejo dinámico de variables")