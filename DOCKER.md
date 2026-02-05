# 🐳 Uso con Docker

## 🚀 Quick Start (3 pasos)

### 1. Construir imagen (primera vez)

```bash
cd /var/www/EC2/code/eugen
make install
```

### 2. Configurar API Key

```bash
nano .env
# Añadir: OPENAI_API_KEY=sk-tu-key-aqui
```

### 3. Ejecutar

```bash
# Opción A: Conectarse al contenedor
make shell
# Dentro del contenedor:
python3 -m src.infrastructure.cli.main --input /tests

# Opción B: Ejecución directa desde host
make run
```

---

## 📋 Comandos Make Disponibles

```bash
make help          # Ver todos los comandos

# Setup
make install       # Construir imagen Docker (primera vez)
make build         # Alias de install

# Gestión del contenedor
make up            # Levantar contenedor en background
make down          # Detener contenedor
make restart       # Reiniciar contenedor
make status        # Ver estado

# Uso
make shell         # Conectar al contenedor (shell bash)
make run           # Ejecutar programa (modo interactivo)
make run-all       # Ejecutar todos los tests (no interactivo)
make logs          # Ver logs del contenedor

# Desarrollo
make test          # Ejecutar tests (cuando estén)
make lint          # Linting con ruff
make format        # Formatear código con black
make typecheck     # Verificar tipos con mypy

# Limpieza
make clean         # Limpiar archivos generados y contenedor
```

---

## 💻 Flujo de Trabajo Típico

### Primera vez:

```bash
# 1. Clonar/navegar al proyecto
cd /var/www/EC2/code/eugen

# 2. Construir imagen
make install

# 3. Configurar API key
nano .env  # Añadir OPENAI_API_KEY

# 4. Levantar contenedor
make up

# 5. Conectarse
make shell
```

### Uso diario:

```bash
# Levantar (si no está corriendo)
make up

# Conectarse
make shell

# Dentro del contenedor:
python3 -m src.infrastructure.cli.main --input /tests

# O desde fuera:
make run
```

---

## 🔍 Dentro del Contenedor

Cuando ejecutas `make shell`, entras al contenedor con este entorno:

```
/app/
├── src/               # Código fuente (montado desde host)
├── output/            # Archivos generados (montado desde host)
├── /tests/            # Tests de entrada (read-only desde host)
├── .env               # Configuración
└── pyproject.toml     # Dependencias
```

### Comandos disponibles dentro:

```bash
# Ver tests disponibles
ls -la /tests/

# Ejecutar programa (interactivo)
python3 -m src.infrastructure.cli.main --input /tests

# Ejecutar todos los tests (no interactivo)
python3 -m src.infrastructure.cli.main --input /tests --non-interactive

# Ver archivos generados
ls -la output/
cat output/POM.md

# Salir del contenedor
exit  # o Ctrl+D
```

---

## 📂 Volúmenes Montados

Docker monta estos directorios del **host** dentro del **contenedor**:

```
Host                                          →  Contenedor
/var/www/EC2/code/eugen/src/                 →  /app/src/
/var/www/EC2/code/eugen/output/              →  /app/output/
/var/www/EC2/code/End2EndTests/.../generated →  /tests/
/var/www/EC2/code/eugen/.env                 →  /app/.env
```

**Ventajas:**
- Editas código en host, se ve en contenedor
- Archivos generados en contenedor aparecen en host
- No pierdes datos al reiniciar contenedor

---

## 🐛 Debugging en Docker

### Ver logs

```bash
make logs
```

### Verificar contenedor

```bash
docker-compose ps
docker-compose exec pom-ppia python3 --version
docker-compose exec pom-ppia pip list
```

### Probar componentes

```bash
make shell

# Dentro del contenedor:
python3
>>> from src.infrastructure.config.settings import settings
>>> print(settings.openai_api_key[:10])
>>> exit()
```

### Reconstruir imagen

```bash
make down
docker-compose build --no-cache
make up
```

---

## 🔧 Configuración Avanzada

### Cambiar directorio de tests

Edita `docker-compose.yml`:

```yaml
volumes:
  - /otro/directorio/tests:/tests:ro
```

### Cambiar modelo LLM

```bash
# En .env:
DEFAULT_MODEL=gpt-4o  # En lugar de gpt-4o-mini
```

### Usar otro directorio de output

```bash
# En .env:
OUTPUT_DIR=/app/mi-output

# Y en docker-compose.yml:
volumes:
  - ./mi-output:/app/mi-output
```

---

## 🚨 Troubleshooting

### Error: "Cannot connect to Docker daemon"

```bash
# Verificar que Docker está corriendo
sudo systemctl status docker
sudo systemctl start docker
```

### Error: "Port already in use"

```bash
# Ver qué contenedores están corriendo
docker ps

# Detener todos
docker stop $(docker ps -q)
```

### Error: "OPENAI_API_KEY not found"

```bash
# Verificar .env
cat .env | grep OPENAI_API_KEY

# Reiniciar contenedor para cargar nueva config
make restart
```

### Contenedor no arranca

```bash
# Ver logs
docker-compose logs pom-ppia

# Ver qué falló
docker-compose up  # Sin -d para ver output
```

---

## 🧹 Limpieza Completa

```bash
# Detener y eliminar contenedor
make down

# Limpiar archivos generados
make clean

# Eliminar imagen (para reconstruir desde cero)
docker rmi pom-ppia:latest
```

---

## ✅ Ventajas del Setup Docker

- ✅ **Aislamiento**: No contamina tu sistema
- ✅ **Reproducible**: Mismas dependencias siempre
- ✅ **Fácil setup**: `make install` y listo
- ✅ **Portable**: Funciona en cualquier máquina con Docker
- ✅ **Limpio**: `make clean` elimina todo
- ✅ **Profesional**: Setup estándar de la industria

---

¡Docker hace todo más fácil! 🐳🚀
