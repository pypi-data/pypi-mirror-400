# Haka Framework - Documentación del Proyecto

## Resumen Ejecutivo

El **Haka Framework** es un framework completo de pruebas funcionales que combina **Playwright** para automatización web moderna con **Behave** para desarrollo dirigido por comportamiento (BDD). Está diseñado para facilitar la creación, ejecución y mantenimiento de pruebas automatizadas de aplicaciones web.

## Información del Proyecto

- **Nombre**: hakalab-framework
- **Versión**: 1.1.0
- **Autor**: Felipe Farias (felipe.farias@hakalab.com)
- **Licencia**: MIT
- **Repositorio**: https://github.com/pipefariashaka/hakalab-framework
- **Python**: >=3.8

## Características Principales

### 🎯 Tecnologías Core
- **Playwright**: Automatización web confiable y moderna
- **Behave**: Framework BDD para Python con sintaxis Gherkin
- **Allure**: Reportes HTML detallados y atractivos

### 🌍 Capacidades Avanzadas
- **Multiidioma**: Soporte para pasos en inglés, español o mixto
- **Page Object Model**: Elementos organizados en archivos JSON
- **Variables dinámicas**: Sistema completo de manejo de variables
- **Scenario Outlines**: Pruebas parametrizadas
- **Gestión de ventanas**: Manejo de múltiples ventanas y pestañas
- **Elementos avanzados**: Drag & drop, alerts, frames, cookies, storage
- **Ejecución paralela**: Soporte para pruebas concurrentes

## Arquitectura del Framework

### Estructura de Directorios

```
Haka-Framework/
├── hakalab_framework/    # Paquete principal
│   ├── core/                      # Módulos centrales
│   ├── steps/                     # Definiciones de pasos
│   ├── templates/                 # Plantillas de proyecto
│   └── cli.py                     # Interfaz de línea de comandos
├── features/                      # Features de ejemplo
│   ├── environment.py             # Configuración de Behave
│   ├── steps/                     # Pasos personalizados
│   ├── example_login.feature      # Ejemplo de login
│   └── example_forms.feature      # Ejemplo de formularios
├── json_poms/                     # Page Object Models en JSON
│   ├── LOGIN.json
│   ├── HOMEPAGE.json
│   └── FORMS.json
├── utils/                         # Utilidades del framework
├── test_files/                    # Archivos para pruebas de upload
├── scripts/                       # Scripts de construcción y publicación
├── requirements.txt               # Dependencias Python
├── behave.ini                     # Configuración de Behave
├── pyproject.toml                 # Configuración moderna del proyecto
└── setup.py                      # Configuración de instalación
```

### Componentes Clave

1. **CLI (Command Line Interface)**
   - `haka-init`: Inicializar nuevos proyectos
   - `haka-run`: Ejecutar pruebas
   - `haka-report`: Generar reportes
   - `haka-steps`: Explorar pasos disponibles
   - `haka-validate`: Validar configuración

2. **Core Modules**
   - Step Suggester: Sugerencias inteligentes de pasos
   - Report Generator: Generación de reportes Allure
   - Element Locator: Localización de elementos web
   - Variable Manager: Gestión de variables dinámicas

3. **Templates System**
   - Plantillas de proyecto básicas y avanzadas
   - Configuraciones predefinidas
   - Ejemplos de features y page objects

## Dependencias Principales

### Dependencias Core
- `playwright>=1.40.0`: Automatización web
- `behave>=1.2.6`: Framework BDD
- `allure-behave>=2.13.2`: Integración con Allure
- `python-dotenv>=1.0.0`: Manejo de variables de entorno
- `jsonschema>=4.20.0`: Validación de esquemas JSON
- `click>=8.0.0`: CLI framework
- `rich>=13.0.0`: Output enriquecido en terminal
- `jinja2>=3.0.0`: Motor de plantillas

### Dependencias Opcionales
- **dev**: pytest, black, flake8, mypy, pre-commit
- **allure**: allure-commandline

## Casos de Uso Principales

### 1. Pruebas de Aplicaciones Web
- Automatización de formularios
- Validación de flujos de usuario
- Pruebas de navegación
- Verificación de elementos UI

### 2. Pruebas de Regresión
- Ejecución automatizada en CI/CD
- Validación de releases
- Pruebas de smoke testing

### 3. Desarrollo BDD
- Colaboración entre equipos técnicos y de negocio
- Documentación ejecutable
- Especificaciones vivas

## Ventajas Competitivas

1. **Facilidad de Uso**: CLI intuitivo y documentación completa
2. **Flexibilidad**: Soporte multiidioma y configuración adaptable
3. **Escalabilidad**: Ejecución paralela y organización modular
4. **Reportes Avanzados**: Integración nativa con Allure
5. **Mantenibilidad**: Page Object Model en JSON
6. **Extensibilidad**: Arquitectura modular y pluggable

## Estado del Proyecto

- **Versión Actual**: 1.1.0 (Beta)
- **Estado**: Desarrollo activo
- **Compatibilidad**: Python 3.8+
- **Plataformas**: Multiplataforma (Windows, macOS, Linux)
- **Navegadores**: Chromium, Firefox, WebKit

## Próximos Pasos

1. **Documentación**: Completar guías de usuario avanzadas
2. **Testing**: Ampliar cobertura de pruebas unitarias
3. **CI/CD**: Configurar pipelines de integración continua
4. **Distribución**: Publicar en PyPI
5. **Comunidad**: Establecer canales de soporte y contribución