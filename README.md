# 📊 UCM GIDIA - Análisis y Predicción de Datos

Una aplicación web basada en **Flask** para análisis, visualización y predicción de datos con múltiples módulos especializados. El proyecto utiliza modelos de Machine Learning y proporciona una interfaz interactiva para explorar datos de demanda, transporte público, eventos, análisis económico y propinas.

## ✨ Características Principales

- 🚀 **Múltiples módulos de análisis**:
  - 📈 **Demanda**: Predicción de demanda con modelos entrenados
  - 🚇 **Metro/Subway**: Análisis de transporte público con mapas interactivos
  - 🎉 **Eventos**: Datos y análisis de eventos
  - 💰 **Económico**: Análisis económico y financiero
  - 💵 **Propinas**: Análisis de patrones de propinas

- 🤖 **Machine Learning**: Modelos LightGBM pre-entrenados para predicciones
- 🗺️ **Visualizaciones Interactivas**: Mapas con Folium y gráficos con Plotly
- 📦 **Almacenamiento en la Nube**: Integración con MinIO para gestión de datos
- 🐳 **Containerización**: Dockerfile incluido para fácil despliegue
- 🎨 **Interfaz moderna**: Interfaz web responsive con CSS personalizado

## 📋 Requisitos Previos

- **Python 3.13+**
- **Git**
- **pip** o **uv** (gestor de dependencias)
- **Docker** (opcional, para containerización)
- Acceso a **MinIO** (opcional, para datos en la nube)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/marioUCM/ucm-gidia-pd2-amcf-ws
cd ucm-gidia-pd2-amcf-ws
```

### 2. Instalar dependencias

**Usar uv**
```bash
pip install uv
uv sync
```

## 🏃 Ejecución

Existen 3 formas diferentes de ejecutar la aplicación según tus necesidades:

### Opción 1️⃣: Docker (Más Rápido - Recommended)

**Lo más rápido y fácil.** No requiere clonar el repositorio ni instalar dependencias.

```bash
docker run -p 5000:5000 mariogradocker/boostmobility-app
```

**Si el puerto 5000 está ocupado**, redirige a otro:
```bash
docker run -p 8080:5000 mariogradocker/boostmobility-app
```
*(La aplicación estará en `http://localhost:8080`)*

---

### Opción 2️⃣: Local con uv + MinIO (Recomendado para desarrollo)

**Clonas el repo y usas los datos directamente desde MinIO en la nube** (no necesitas descargar la carpeta de datos).

```bash
# 1. Clonar el repositorio
git clone https://github.com/marioUCM/ucm-gidia-pd2-amcf-ws
cd ucm-gidia-pd2-amcf-ws

# 2. Instalar dependencias con uv
pip install uv
uv sync

# 3. Configurar variables de entorno (ver sección 🔐 Abajo)
# Crear archivo .env con las credenciales de MinIO

# 4. Ejecutar la aplicación
uv run python -m web.app
```

**Ventajas:** Desarrollo ágil, cambios inmediatos, sin descargas pesadas.

---

### Opción 3️⃣: Local Completo (Sin Docker ni MinIO)

**Clonas el repo, usas uv y descargas todos los datos localmente desde [Google Drive](https://drive.google.com/drive/folders/1dVaG5wBnSt_7TkzQL_85iCKjOYrGUrpq?usp=drive_link).**

```bash
# 1. Clonar el repositorio
git clone https://github.com/marioUCM/ucm-gidia-pd2-amcf-ws
cd ucm-gidia-pd2-amcf-ws

# 2. Instalar dependencias con uv
pip install uv
uv sync

# 3. Descargar datos desde Google Drive
# Descarga la carpeta 'data/' desde el Drive y colócala en la raíz del proyecto
# (Tu carpeta de datos debe estar en ./data/)

# 4. Cambiar a la rama local
git switch local

# 5. Ejecutar la aplicación (sin necesidad de .env)
uv run python -m web.app
```

**Ventajas:** Independencia total, sin dependencias externas, funciona offline.
**Desventajas:** Descarga más pesada (~400 MB), requiere más espacio en disco.

---

## 📊 Comparativa de Opciones

| Criterio | Docker | uv + MinIO | Local Completo |
|----------|--------|-----------|----------------|
| 💾 **Espacio en disco** | Mínimo | ~665 MB | ~400 MB+ |
| 🌐 **Necesita conexión** | ✅ Sí | ✅ Sí (MinIO) | ❌ No |
| 🔧 **Para desarrollo** | ❌ No recomendado | ✅ Sí | ✅ Sí |
| 🚀 **Producción** | ✅ Recomendado | ❌ No | ❌ No |

La aplicación estará disponible en `http://localhost:5000` (o en el puerto que especifiques)

## 📁 Estructura del Proyecto

```
.
├── web/                          # Aplicación Flask principal
│   ├── app.py                    # Punto de entrada de la aplicación
│   ├── routes/                   # Rutas y endpoints
│   │   ├── main_routes.py        # Página principal
│   │   ├── demand_routes.py      # Rutas de demanda
│   │   ├── metro_routes.py       # Rutas de metro/subway
│   │   ├── event_routes.py       # Rutas de eventos
│   │   ├── money_routes.py       # Rutas de análisis económico
│   │   └── tips_routes.py        # Rutas de propinas
│   ├── services/                 # Lógica de negocio
│   │   ├── demand_service.py     # Servicio de predicción de demanda
│   │   ├── metro_service.py      # Servicio de metro
│   │   ├── event_service.py      # Servicio de eventos
│   │   ├── money_service.py      # Servicio económico
│   │   └── tips_service.py       # Servicio de propinas
│   ├── templates/                # Plantillas HTML
│   │   ├── base.html             # Plantilla base
│   │   ├── index.html            # Página de inicio
│   │   ├── demand.html
│   │   ├── metro.html
│   │   ├── event.html
│   │   ├── money.html
│   │   └── tips.html
│   └── static/                   # Archivos estáticos
│       ├── css/                  # Estilos CSS
│       ├── js/                   # Scripts JavaScript
│       ├── img/                  # Imágenes
│       └── generated/            # Mapas y visualizaciones generadas
├── data/                         # Datos del proyecto
│   ├── events/                   # Datos de eventos
│   ├── films/                    # Datos de películas
│   ├── money/                    # Datos económicos
│   ├── final_models/             # Modelos ML entrenados
│   │   ├── demanda/
│   │   ├── propinas/
│   │   └── subway/
│   └── utils/                    # Utilidades de datos
├── utils/                        # Funciones auxiliares globales
│   └── read_from_minio.py        # Lectura desde MinIO
├── Dockerfile                    # Configuración Docker
├── pyproject.toml               # Dependencias del proyecto
├── uv.lock                      # Lock file de uv
└── README.md                    # Este archivo
```

## 🔧 Dependencias Principales

| Dependencia | Versión | Propósito |
|------------|---------|----------|
| Flask | 3.1.3+ | Framework web |
| Pandas | 3.0.2+ | Análisis de datos |
| LightGBM | 4.6.0+ | Modelos de predicción |
| Plotly | 6.7.0+ | Visualizaciones interactivas |
| Folium | 0.20.0+ | Mapas interactivos |
| GeoPandas | 1.1.3+ | Análisis geoespacial |
| MinIO | 7.2.20+ | Almacenamiento en la nube |
| scikit-learn | 1.8.0+ | Machine Learning |
| PyArrow | 24.0.0+ | Serialización de datos |

Para la lista completa, consulta [pyproject.toml](pyproject.toml).

## 📡 API Endpoints

### Rutas Principales

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/` | GET | Página principal |
| `/demanda` | GET, POST | Predicción de demanda |
| `/metro` | GET, POST | Análisis de metro |
| `/eventos` | GET, POST | Análisis de eventos |
| `/economico` | GET, POST | Análisis económico |
| `/tips` | GET, POST | Análisis de propinas |


## 👥 Autores

- **Universidad Complutense de Madrid (UCM)**
- [Mario Granados Guerrero](https://github.com/marioUCM)
- [Francisco Pastor Ruiz](https://github.com/franpast)
- [Carlos Vallejo Ros](https://github.com/carlosvallejo23)
- [Alvaro Alonso Ortega](https://github.com/Alalonsoor)

## 🔐 Variables de Entorno

La aplicación requiere las siguientes variables de entorno para usar MinIO.

Crea un archivo '.env' en la raiz con el siguiente contenido:
```
# MinIO Configuration
ACCESS_KEY=TU_ACCESS_KEY
SECRET_KEY=TU_SECRET_KEY
```

**Última actualización:** Abril 2026
