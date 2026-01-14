#!/bin/bash
# Script para ejecutar pruebas en paralelo con Docker

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
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configuración por defecto
WORKERS=${WORKERS:-4}
BROWSER=${BROWSER:-chromium}
TAGS=${TAGS:-""}
FEATURE=${FEATURE:-""}
COMPOSE_SERVICE=${COMPOSE_SERVICE:-hakalab-tests}

# Mostrar ayuda
show_help() {
    cat << EOF
🚀 Script de Ejecución Paralela con Docker - Hakalab Framework

Uso: $0 [OPCIONES]

OPCIONES:
    -w, --workers NUM       Número de workers paralelos (default: 4)
    -b, --browser BROWSER   Navegador: chromium, firefox, webkit (default: chromium)
    -t, --tags TAGS         Tags para filtrar pruebas (ej: @smoke,@regression)
    -f, --feature FEATURE   Archivo feature específico
    -s, --service SERVICE   Servicio de docker-compose (default: hakalab-tests)
    --smoke                 Ejecutar solo pruebas smoke (8 workers)
    --multi-browser         Ejecutar en múltiples navegadores
    --build                 Reconstruir imagen Docker
    --clean                 Limpiar contenedores y volúmenes
    --reports               Generar y servir reportes
    -h, --help              Mostrar esta ayuda

EJEMPLOS:
    $0                                    # Ejecución básica con 4 workers
    $0 -w 8 --smoke                      # Smoke tests con 8 workers
    $0 -t "@regression" -w 6             # Tests de regresión con 6 workers
    $0 -f login.feature -w 2             # Feature específico con 2 workers
    $0 --multi-browser                   # Múltiples navegadores en paralelo
    $0 --build -w 8                      # Reconstruir y ejecutar con 8 workers
    $0 --reports                         # Solo generar reportes

VARIABLES DE ENTORNO:
    BASE_URL                 URL base de la aplicación
    TIMEOUT                  Timeout en milisegundos
    PARALLEL_WORKERS         Número de workers (sobrescrito por -w)
    BROWSER                  Navegador (sobrescrito por -b)

EOF
}

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -t|--tags)
            TAGS="$2"
            shift 2
            ;;
        -f|--feature)
            FEATURE="$2"
            shift 2
            ;;
        -s|--service)
            COMPOSE_SERVICE="$2"
            shift 2
            ;;
        --smoke)
            COMPOSE_SERVICE="hakalab-smoke"
            WORKERS=8
            shift
            ;;
        --multi-browser)
            COMPOSE_SERVICE="hakalab-multi-browser"
            shift
            ;;
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --clean)
            CLEAN_FLAG=true
            shift
            ;;
        --reports)
            REPORTS_ONLY=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Limpiar si se solicita
if [[ "$CLEAN_FLAG" == "true" ]]; then
    log "🧹 Limpiando contenedores y volúmenes..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    success "Limpieza completada"
    exit 0
fi

# Solo generar reportes
if [[ "$REPORTS_ONLY" == "true" ]]; then
    log "📊 Generando reportes..."
    docker-compose up hakalab-reports
    log "🌐 Sirviendo reportes en http://localhost:8080"
    docker-compose up -d hakalab-serve-reports
    success "Reportes disponibles en http://localhost:8080"
    exit 0
fi

# Verificar que docker-compose existe
if ! command -v docker-compose &> /dev/null; then
    error "docker-compose no está instalado"
    exit 1
fi

# Verificar que el archivo docker-compose.yml existe
if [[ ! -f "docker-compose.yml" ]]; then
    error "docker-compose.yml no encontrado en el directorio actual"
    exit 1
fi

# Crear directorios necesarios
log "📁 Creando directorios necesarios..."
mkdir -p allure-results screenshots logs downloads

# Configurar variables de entorno
export PARALLEL_WORKERS="$WORKERS"
export BROWSER="$BROWSER"

# Construir comando
DOCKER_CMD="docker-compose up"
if [[ -n "$BUILD_FLAG" ]]; then
    DOCKER_CMD="$DOCKER_CMD $BUILD_FLAG"
fi

# Configurar comando de behave
BEHAVE_CMD="behave --processes $WORKERS"

if [[ -n "$TAGS" ]]; then
    BEHAVE_CMD="$BEHAVE_CMD --tags $TAGS"
fi

if [[ -n "$FEATURE" ]]; then
    BEHAVE_CMD="$BEHAVE_CMD features/$FEATURE"
fi

# Mostrar configuración
log "🚀 Configuración de ejecución:"
log "   Workers: $WORKERS"
log "   Navegador: $BROWSER"
log "   Servicio: $COMPOSE_SERVICE"
if [[ -n "$TAGS" ]]; then
    log "   Tags: $TAGS"
fi
if [[ -n "$FEATURE" ]]; then
    log "   Feature: $FEATURE"
fi

# Ejecutar pruebas
log "▶️  Iniciando ejecución paralela..."

if [[ "$COMPOSE_SERVICE" == "hakalab-tests" ]]; then
    # Ejecución personalizada
    docker-compose run --rm $BUILD_FLAG \
        -e PARALLEL_WORKERS="$WORKERS" \
        -e BROWSER="$BROWSER" \
        "$COMPOSE_SERVICE" $BEHAVE_CMD
else
    # Usar servicio predefinido
    docker-compose up $BUILD_FLAG "$COMPOSE_SERVICE"
fi

EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
    success "✅ Ejecución completada exitosamente"
    
    # Preguntar si generar reportes
    read -p "¿Generar reportes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "📊 Generando reportes..."
        docker-compose up hakalab-reports
        
        read -p "¿Servir reportes en http://localhost:8080? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "🌐 Sirviendo reportes..."
            docker-compose up -d hakalab-serve-reports
            success "Reportes disponibles en http://localhost:8080"
            log "Para detener el servidor: docker-compose stop hakalab-serve-reports"
        fi
    fi
else
    error "❌ Ejecución falló con código: $EXIT_CODE"
    warning "Revisa los logs para más detalles"
fi

exit $EXIT_CODE