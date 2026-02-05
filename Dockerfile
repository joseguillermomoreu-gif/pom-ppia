# Dockerfile para POM-PPIA
FROM python:3.12-slim

# Metadata
LABEL maintainer="jgmoreu"
LABEL description="POM-PPIA Generator - Genera POM desde tests Playwright"

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (si se necesitan)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias primero (para aprovechar cache de Docker)
COPY pyproject.toml ./

# Instalar dependencias Python
RUN pip install --no-cache-dir \
    openai==1.50.0 \
    python-dotenv==1.0.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    pyyaml==6.0 \
    click==8.1.7 \
    rich==13.7.0

# Copiar el código fuente
COPY . .

# Crear directorio de output
RUN mkdir -p output

# Variables de entorno por defecto (se pueden sobrescribir)
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Comando por defecto (shell interactivo)
CMD ["/bin/bash"]
