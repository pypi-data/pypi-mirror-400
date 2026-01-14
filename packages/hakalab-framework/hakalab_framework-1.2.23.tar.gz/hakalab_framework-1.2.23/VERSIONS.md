# Versiones de Dependencias

## Versiones Actuales (v1.2.0)

### Dependencias Principales
- **Playwright**: `>=1.57.0` (Última versión estable)
- **Behave**: `>=1.3.3` (Última versión estable)
- **Python-dotenv**: `>=1.0.0` (Variables de entorno)

### Dependencias de Soporte
- **Python-dotenv**: `>=1.0.0`
- **JSONSchema**: `>=4.20.0`
- **Click**: `>=8.0.0`
- **Rich**: `>=13.0.0`
- **Jinja2**: `>=3.0.0`

## Compatibilidad de Python
- **Python**: `>=3.8`
- **Recomendado**: Python 3.11+

## Navegadores Soportados (Playwright 1.57.0)
- **Chromium**: 143.0.7499.4
- **Firefox**: 144.0.2
- **WebKit**: 26.0

## Instalación Automática

Al instalar `hakalab-framework`, todas las dependencias se instalan automáticamente con las versiones más recientes:

```bash
pip install hakalab-framework
```

## Actualización de Dependencias

Para actualizar a las últimas versiones:

```bash
pip install --upgrade hakalab-framework
```

## Notas de Compatibilidad

### Behave 1.3.3
- Mejoras en el manejo de cleanup
- Mejor soporte para Python 3.11+
- Correcciones de bugs menores

### Playwright 1.57.0
- Soporte para navegadores más recientes
- Mejoras en performance
- Nuevas funcionalidades de testing

### Allure-Behave 2.15.3
- Mejor integración con Behave 1.3.3
- Reportes más detallados
- Correcciones en el manejo de screenshots

## Problemas Conocidos

### cleanup_error
- **Afecta**: Todas las versiones de Behave + Playwright
- **Solución**: Usar `run_tests.py` wrapper
- **Estado**: Problema conocido de Behave core

## Historial de Versiones

### v1.1.19 (Enero 2025)
- ✅ Playwright 1.57.0
- ✅ Behave 1.3.3
- ✅ Allure-Behave 2.15.3
- ✅ Wrapper para cleanup_error

### v1.1.18 (Anterior)
- Playwright 1.40.0
- Behave 1.2.6
- Allure-Behave 2.13.2