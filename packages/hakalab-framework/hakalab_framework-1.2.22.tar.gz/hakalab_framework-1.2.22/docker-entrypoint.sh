#!/bin/bash
# ==========================================
# DOCKER ENTRYPOINT MEJORADO PARA HAKALAB FRAMEWORK
# Soporte para paralelización y múltiples modos de ejecución
# ==========================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Banner de inicio
echo "
╔══════════════════════════════════════════════════════════════╗
║                    🚀 HAKALAB FRAMEWORK v1.2.12              ║
║                   Automatización de Pruebas Avanzada         ║
╚══════════════════════════════════════════════════════════════╝
"

# Verificar configuración
log "🔧 Verificando configuración del contenedor..."

# Configurar variables por defecto
export BROWSER=${BROWSER:-chromium}
export HEADLESS=${HEADLESS:-true}
export PARALLEL_WORKERS=${PARALLEL_WORKERS:-4}
export TIMEOUT=${TIMEOUT:-30000}
export DISPLAY=${DISPLAY:-:99}

log "📋 Configuración actual:"
log "   🌐 Navegador: $BROWSER"
log "   👻 Headless: $HEADLESS"
log "   ⚡ Workers paralelos: $PARALLEL_WORKERS"
log "   ⏱️  Timeout: $TIMEOUT ms"

# Iniciar Xvfb si no está en modo headless
if [ "$HEADLESS" != "true" ]; then
    log "🖥️  Iniciando Xvfb para modo con interfaz gráfica..."
    Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    XVFB_PID=$!
    export DISPLAY=:99
    sleep 3
    
    # Verificar que Xvfb está funcionando
    if ! pgrep -f "Xvfb :99" > /dev/null; then
        error "❌ Falló al iniciar Xvfb"
        exit 1
    fi
    success "✅ Xvfb iniciado correctamente"
fi

# Verificar que Playwright está instalado correctamente
log "🎭 Verificando instalación de Playwright..."
if ! python -c "import playwright; print('Playwright OK')" 2>/dev/null; then
    error "❌ Playwright no está instalado correctamente"
    exit 1
fi

# Verificar navegadores instalados
log "🌐 Verificando navegadores instalados..."
python -c "
import sys
from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        browsers = []
        try:
            p.chromium.launch(headless=True).close()
            browsers.append('✅ Chromium')
        except:
            browsers.append('❌ Chromium')
        
        try:
            p.firefox.launch(headless=True).close()
            browsers.append('✅ Firefox')
        except:
            browsers.append('❌ Firefox')
            
        try:
            p.webkit.launch(headless=True).close()
            browsers.append('✅ WebKit')
        except:
            browsers.append('❌ WebKit')
            
        for browser in browsers:
            print(f'   {browser}')
except Exception as e:
    print(f'❌ Error verificando navegadores: {e}')
    sys.exit(1)
"

# Crear directorios necesarios
log "📁 Creando directorios necesarios..."
mkdir -p html-reports screenshots logs downloads videos test-results

# Función para manejar señales de terminación
cleanup() {
    log "🧹 Limpiando procesos..."
    if [ ! -z "$XVFB_PID" ]; then
        kill $XVFB_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGTERM SIGINT

# Determinar modo de ejecución basado en argumentos
if [ $# -eq 0 ]; then
    # Modo por defecto: ejecutar todas las pruebas
    log "🚀 Modo por defecto: Ejecutando todas las pruebas con $PARALLEL_WORKERS workers..."
    
    # Comando optimizado para contenedores
    exec behave \
        --processes "$PARALLEL_WORKERS" \
        --format html \
        --outdir html-reports \
        --no-capture \
        --no-capture-stderr \
        --logging-level INFO
        
elif [ "$1" = "smoke" ]; then
    # Modo smoke tests
    log "💨 Modo Smoke Tests: Ejecutando pruebas críticas..."
    shift
    exec behave \
        --processes "$PARALLEL_WORKERS" \
        --tags @smoke \
        --format html \
        --outdir html-reports \
        --no-capture \
        "$@"
        
elif [ "$1" = "regression" ]; then
    # Modo regression
    log "🔄 Modo Regression: Ejecutando suite completa..."
    shift
    exec behave \
        --processes "$PARALLEL_WORKERS" \
        --tags @regression \
        --format html \
        --outdir html-reports \
        --no-capture \
        "$@"
        
elif [ "$1" = "parallel-browsers" ]; then
    # Modo múltiples navegadores en paralelo
    log "🌐 Modo Multi-Browser: Ejecutando en paralelo con diferentes navegadores..."
    
    # Ejecutar en background con diferentes navegadores
    BROWSER=chromium behave --processes 2 --tags @smoke --format html --outdir html-reports/chromium &
    BROWSER=firefox behave --processes 2 --tags @smoke --format html --outdir html-reports/firefox &
    BROWSER=webkit behave --processes 2 --tags @smoke --format html --outdir html-reports/webkit &
    
    # Esperar a que terminen todos
    wait
    success "✅ Ejecución multi-browser completada"
    
elif [ "$1" = "reports" ]; then
    # Modo generación de reportes
    log "📊 Generando reportes consolidados..."
    
    # Aquí puedes agregar lógica para consolidar reportes
    if [ -d "html-reports" ]; then
        success "✅ Reportes disponibles en html-reports/"
        ls -la html-reports/
    else
        warning "⚠️  No se encontraron reportes"
    fi
    
elif [ "$1" = "debug" ]; then
    # Modo debug
    log "🐛 Modo Debug: Información del sistema..."
    
    echo "📋 Información del sistema:"
    echo "   🐍 Python: $(python --version)"
    echo "   🎭 Playwright: $(python -c 'import playwright; print(playwright.__version__)')"
    echo "   🖥️  Display: $DISPLAY"
    echo "   💾 Memoria: $(free -h | grep '^Mem:' | awk '{print $2}')"
    echo "   💿 Disco: $(df -h / | tail -1 | awk '{print $4}')"
    
    # Ejecutar comando interactivo si se proporciona
    shift
    if [ $# -gt 0 ]; then
        log "🔧 Ejecutando comando debug: $*"
        exec "$@"
    else
        log "🐚 Iniciando shell interactivo..."
        exec /bin/bash
    fi
    
else
    # Modo personalizado: ejecutar comando proporcionado
    log "⚙️  Modo personalizado: Ejecutando comando: $*"
    exec "$@"
fi