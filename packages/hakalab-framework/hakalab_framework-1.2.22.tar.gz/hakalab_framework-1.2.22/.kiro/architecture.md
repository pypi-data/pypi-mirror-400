# Arquitectura del Haka Framework

## Visión General de la Arquitectura

El Haka Framework sigue una arquitectura modular y extensible basada en los principios de separación de responsabilidades y bajo acoplamiento. La arquitectura está diseñada para facilitar el mantenimiento, la extensibilidad y la reutilización de componentes.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface                            │
│  haka-init | haka-run | haka-report | haka-steps | haka-validate │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Core Framework                              │
├─────────────────────────────────────────────────────────────┤
│  Step Suggester  │  Report Generator  │  Template Engine   │
│  Element Locator │  Variable Manager  │  Project Validator │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Integration Layer                            │
├─────────────────────────────────────────────────────────────┤
│     Behave BDD      │     Playwright      │     Allure      │
│   (Test Runner)     │   (Web Automation)  │   (Reporting)   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Data Layer                                  │
├─────────────────────────────────────────────────────────────┤
│  JSON Page Objects  │  Feature Files  │  Environment Config │
│  Test Data         │  Variables      │  Browser Settings   │
└─────────────────────────────────────────────────────────────┘
```

## Capas de la Arquitectura

### 1. CLI Interface Layer

**Responsabilidad**: Proporcionar una interfaz de línea de comandos intuitiva para interactuar con el framework.

**Componentes**:
- `cli.py`: Controlador principal de comandos
- Comandos disponibles:
  - `haka-init`: Inicialización de proyectos
  - `haka-run`: Ejecución de pruebas
  - `haka-report`: Generación de reportes
  - `haka-steps`: Exploración de pasos
  - `haka-validate`: Validación de configuración

**Tecnologías**: Click (Python CLI framework)

### 2. Core Framework Layer

**Responsabilidad**: Contiene la lógica de negocio principal y los servicios centrales del framework.

#### Step Suggester
- **Función**: Proporciona sugerencias inteligentes de pasos BDD
- **Características**:
  - Búsqueda por palabras clave
  - Filtrado por categorías
  - Soporte multiidioma
  - Generación de documentación

#### Report Generator
- **Función**: Genera reportes de pruebas en múltiples formatos
- **Características**:
  - Reportes Allure HTML
  - Reportes simples de fallback
  - Servidor integrado
  - Limpieza automática

#### Element Locator
- **Función**: Localiza elementos web usando diferentes estrategias
- **Características**:
  - Soporte para múltiples selectores (CSS, XPath, ID, etc.)
  - Integración con Page Object Models JSON
  - Manejo de timeouts y esperas

#### Variable Manager
- **Función**: Gestiona variables dinámicas durante la ejecución
- **Características**:
  - Variables de entorno
  - Variables de sesión
  - Generación de datos aleatorios
  - Interpolación de strings

#### Template Engine
- **Función**: Genera estructura de proyectos desde plantillas
- **Características**:
  - Plantillas básicas y avanzadas
  - Configuración por idioma
  - Archivos de ejemplo incluidos

### 3. Integration Layer

**Responsabilidad**: Integra las herramientas externas y proporciona abstracciones para su uso.

#### Behave Integration
- **Función**: Framework BDD para Python
- **Características**:
  - Sintaxis Gherkin
  - Hooks de ciclo de vida
  - Formatters personalizados
  - Ejecución paralela

#### Playwright Integration
- **Función**: Automatización web moderna
- **Características**:
  - Múltiples navegadores (Chromium, Firefox, WebKit)
  - Modo headless/headed
  - Capturas de pantalla
  - Manejo de elementos avanzados

#### Allure Integration
- **Función**: Sistema de reportes avanzado
- **Características**:
  - Reportes HTML interactivos
  - Métricas y gráficos
  - Historial de ejecuciones
  - Attachments automáticos

### 4. Data Layer

**Responsabilidad**: Maneja la persistencia y configuración de datos del framework.

#### JSON Page Objects
- **Estructura**: Archivos JSON con definiciones de elementos
- **Ventajas**:
  - Separación de lógica y datos
  - Fácil mantenimiento
  - Reutilización entre proyectos
  - Validación de esquemas

#### Feature Files
- **Formato**: Archivos .feature con sintaxis Gherkin
- **Organización**:
  - Scenarios individuales
  - Scenario Outlines
  - Tags para categorización
  - Documentación embebida

#### Configuration Management
- **Archivos**:
  - `.env`: Variables de entorno
  - `behave.ini`: Configuración de Behave
  - `pyproject.toml`: Configuración del proyecto

## Patrones de Diseño Implementados

### 1. Command Pattern
- **Implementación**: CLI commands
- **Beneficio**: Encapsula operaciones como objetos

### 2. Factory Pattern
- **Implementación**: Template creation
- **Beneficio**: Creación flexible de objetos

### 3. Strategy Pattern
- **Implementación**: Element locators
- **Beneficio**: Intercambio dinámico de algoritmos

### 4. Observer Pattern
- **Implementación**: Behave hooks
- **Beneficio**: Notificación de eventos

### 5. Page Object Pattern
- **Implementación**: JSON Page Objects
- **Beneficio**: Encapsulación de elementos UI

## Flujo de Ejecución

### 1. Inicialización del Proyecto
```
haka-init → Template Engine → Project Structure Creation
```

### 2. Ejecución de Pruebas
```
haka-run → Behave Runner → Playwright Actions → Results Collection
```

### 3. Generación de Reportes
```
haka-report → Report Generator → Allure Processing → HTML Output
```

### 4. Exploración de Pasos
```
haka-steps → Step Suggester → Pattern Matching → Documentation
```

## Extensibilidad

### Puntos de Extensión

1. **Custom Steps**: Agregar nuevos pasos BDD
2. **Custom Formatters**: Nuevos formatos de reporte
3. **Custom Locators**: Estrategias de localización personalizadas
4. **Custom Templates**: Plantillas de proyecto específicas
5. **Custom Hooks**: Lógica personalizada en ciclo de vida

### Plugin Architecture

El framework está diseñado para soportar plugins mediante:
- Entry points en `setup.py`
- Interfaces bien definidas
- Configuración dinámica
- Carga lazy de componentes

## Consideraciones de Rendimiento

### Optimizaciones Implementadas

1. **Lazy Loading**: Carga de módulos bajo demanda
2. **Caching**: Cache de elementos localizados
3. **Parallel Execution**: Soporte para ejecución paralela
4. **Resource Management**: Gestión eficiente de recursos del navegador

### Métricas de Rendimiento

- **Tiempo de inicio**: < 2 segundos
- **Memoria base**: < 50MB
- **Escalabilidad**: Hasta 10 procesos paralelos
- **Throughput**: 100+ acciones por minuto

## Seguridad

### Medidas de Seguridad

1. **Input Validation**: Validación de entradas de usuario
2. **Path Sanitization**: Sanitización de rutas de archivos
3. **Environment Isolation**: Aislamiento de variables de entorno
4. **Secure Defaults**: Configuraciones seguras por defecto

## Mantenibilidad

### Principios Aplicados

1. **Single Responsibility**: Cada clase tiene una responsabilidad
2. **Open/Closed**: Abierto para extensión, cerrado para modificación
3. **Dependency Inversion**: Dependencias hacia abstracciones
4. **DRY**: No repetir código
5. **KISS**: Mantener simplicidad

### Herramientas de Calidad

- **Black**: Formateo de código
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing unitario
- **Pre-commit**: Hooks de calidad