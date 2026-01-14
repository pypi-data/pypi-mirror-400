# ==========================================
# DOCKERFILE OPTIMIZADO PARA HAKALAB FRAMEWORK v1.2.12
# Soporte para paralelización y CI/CD
# ==========================================

FROM python:3.11-slim

# Metadatos
LABEL maintainer="Hakalab Framework Team"
LABEL version="1.2.12"
LABEL description="Framework de pruebas automatizadas con soporte para paralelización"

# Variables de construcción
ARG DEBIAN_FRONTEND=noninteractive
ARG PARALLEL_WORKERS=4
ARG BROWSER=chromium

# Instalar dependencias del sistema optimizadas
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependencias básicas
    wget curl gnupg ca-certificates \
    # Fuentes y librerías gráficas
    fonts-liberation fonts-noto-color-emoji \
    # Dependencias de Playwright
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgtk-3-0 libnspr4 libnss3 \
    libwayland-client0 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxss1 libxtst6 \
    # Display virtual para modo no-headless
    xvfb \
    # Utilidades adicionales
    git zip unzip jq \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN groupadd -r testuser && useradd -r -g testuser -u 1000 testuser \
    && mkdir -p /home/testuser/app \
    && chown -R testuser:testuser /home/testuser

# Cambiar a usuario no-root
USER testuser
WORKDIR /home/testuser/app

# Configurar PATH para binarios de usuario
ENV PATH="/home/testuser/.local/bin:$PATH"

# Copiar y instalar dependencias Python
COPY --chown=testuser:testuser requirements.txt pyproject.toml ./
RUN pip install --user --no-cache-dir --upgrade pip \
    && pip install --user --no-cache-dir -r requirements.txt \
    && pip install --user --no-cache-dir hakalab-framework

# Instalar navegadores de Playwright
RUN python -m playwright install chromium firefox webkit \
    && python -m playwright install-deps

# Copiar código del proyecto
COPY --chown=testuser:testuser . .

# Variables de entorno optimizadas para contenedores
ENV PYTHONPATH=/home/testuser/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    BROWSER=${BROWSER} \
    HEADLESS=true \
    PARALLEL_WORKERS=${PARALLEL_WORKERS} \
    DISPLAY=:99 \
    NODE_OPTIONS=--max-old-space-size=4096

# Crear directorios necesarios con permisos correctos
RUN mkdir -p \
    html-reports \
    screenshots \
    logs \
    downloads \
    videos \
    test-results \
    && chmod -R 755 /home/testuser/app

# Copiar script de entrada mejorado
COPY --chown=testuser:testuser docker-entrypoint.sh /home/testuser/
RUN chmod +x /home/testuser/docker-entrypoint.sh

# Healthcheck para verificar que el contenedor está listo
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import playwright; print('OK')" || exit 1

# Exponer puerto para servidor de reportes (opcional)
EXPOSE 8080

ENTRYPOINT ["/home/testuser/docker-entrypoint.sh"]
CMD ["behave", "--processes", "4", "--format", "html", "--outdir", "html-reports"]