# 1. Usar una imagen oficial de Python 3.13 ligera
FROM python:3.13-slim

# 2. Evitar que Python genere archivos temporales y forzar salida de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. AÑADIDO: Instalar la librería del sistema necesaria para LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 4. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 5. Instalar 'uv' para gestionar las dependencias
RUN pip install --no-cache-dir uv

# 6. Copiar SOLO los archivos de dependencias primero (Aprovecha la caché de Docker)
COPY pyproject.toml uv.lock ./

# 7. Instalar las dependencias exactas usando uv
RUN uv sync --frozen --no-install-project

# 8. Copiar el resto de tu código al contenedor
COPY . .

# 9. Exponer el puerto que usa Flask
EXPOSE 5000

# 10. Comando para arrancar la app como módulo
CMD ["uv", "run", "python", "-m", "web.app"]

### COMO UTILIZARLO
# Para construir la imagen ejecuta en la ruta del proyecto 'docker build -t boostmobility-app .'
# Para lanzar el contenedor una vez este construida la imagen ejecuta 'docker run -p 5000:5000 boostmobility-app'
# Una vez lanzado el contenedor abre tu navegador y entra en: http://localhost:5000