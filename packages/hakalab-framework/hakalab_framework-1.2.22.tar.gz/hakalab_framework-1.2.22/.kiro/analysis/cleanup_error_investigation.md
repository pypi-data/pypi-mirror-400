# Investigación Profunda: cleanup_error

## Problema Reportado
El usuario reporta que el `cleanup_error` sigue ocurriendo en su proyecto real, a pesar de que en nuestro entorno de prueba parece funcionar.

## Análisis 1: Diferencias entre Entorno de Prueba vs Proyecto Real

### Entorno de Prueba (Nuestro)
- Framework instalado localmente desde código fuente
- Escenario simple con 2 steps
- Ejecución directa desde el directorio del framework
- Variables de entorno cargadas correctamente

### Proyecto Real (Usuario)
- Framework instalado desde PyPI (hakalab-framework==1.1.11)
- Escenarios más complejos (3+ steps)
- Ejecución desde directorio diferente
- Posibles diferencias en configuración de entorno

## Análisis 2: Causas Potenciales del cleanup_error

### Causa 1: Timing Issues con Allure
```
USING RUNNER: behave.runner:Runner
```
El usuario muestra que está usando `behave.runner:Runner`, lo que indica que behave está manejando el cleanup internamente, no nuestras funciones.

### Causa 2: Diferencias en Versión Instalada
El usuario tiene instalado desde PyPI, que puede tener diferencias con nuestro código local actual.

### Causa 3: Configuración de Allure
El cleanup_error aparece específicamente cuando se usa Allure formatter, sugiriendo un conflicto entre:
- Allure formatter intentando escribir archivos
- Nuestras funciones de cleanup cerrando recursos
- Behave intentando hacer su propio cleanup

## Hipótesis Principal
El problema NO está en nuestras funciones de cleanup, sino en la **interacción entre Allure formatter y behave** cuando se ejecuta desde un proyecto externo.

## Próximos Pasos de Investigación
1. Reproducir el problema en un proyecto separado
2. Analizar logs detallados de Allure
3. Investigar timing de cleanup entre Allure y Playwright
4. Crear solución específica para proyectos externos