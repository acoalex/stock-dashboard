# 📈 Stock Panel Dashboard

Dashboard financiero profesional e interactivo construido con **Python** y **Streamlit**. Permite el seguimiento de acciones en tiempo real, análisis técnico/fundamental y recomendaciones de inversión potenciadas por **Inteligencia Artificial**.

## 🚀 Características Principales

*   **🔐 Seguridad Robusta**: Sistema de login protegido con hash de contraseñas y gestión de sesiones.
*   **🤖 Análisis con IA**: Integración con LLMs (OpenAI/ModelHub) para analizar tendencias y noticias recientes, ofreciendo recomendaciones de compra/venta/mantenimiento.
*   **🔍 Búsqueda Inteligente**: Buscador predictivo en tiempo real conectado a la API de Yahoo Finance para añadir acciones instantáneamente.
*   **📊 Gráficos Avanzados**: Gráficos de velas (Candlestick) interactivos con detección automática de divisa (€/$) y tooltips detallados.
*   **⚡ Actualización Automática**: Configurable (1m, 5m, 15m) para mantener los precios siempre frescos.
*   **💼 Gestión de Cartera**: Añade y elimina activos de tu lista de seguimiento fácilmente desde la barra lateral.
*   **🐳 Docker Ready**: Despliegue sencillo y aislado mediante contenedores.

## 🛠️ Tecnologías

*   **Frontend**: Streamlit, Plotly.
*   **Datos**: yfinance (Yahoo Finance API).
*   **IA/LLM**: OpenAI Client (compatible con cualquier endpoint estándar).
*   **Seguridad**: python-dotenv, streamlit-authenticator.

---

## ⚙️ Configuración (.env)

El proyecto utiliza variables de entorno para proteger la información sensible. **Antes de arrancar**, debes crear un archivo `.env` en la raíz del proyecto basado en el siguiente ejemplo:

```ini
# --- Credenciales de Acceso al Dashboard ---
STOCK_USERNAME=admin
STOCK_NAME=Administrador
STOCK_EMAIL=admin@example.com
# Generar hash con: from streamlit_authenticator.utilities.hasher import Hasher; Hasher.hash('tu_password')
STOCK_PASSWORD_HASH=$2b$12$EjemploDeHashGenerado...

# --- Seguridad de Cookies ---
COOKIE_KEY=clave_secreta_larga_y_aleatoria
COOKIE_NAME=stock_dashboard_cookie

# --- Configuración de Inteligencia Artificial (LLM) ---
LLM_API_KEY=tu_api_key_aqui
LLM_BASE_URL=https://modelhub.example.com/v1
LLM_MODEL=openai/gpt-oss-120b:free
```

---

## 🐳 Instalación y Uso con Docker (Recomendado)

Es la forma más rápida y limpia de ejecutar la aplicación.

1.  **Clonar el repositorio y entrar en el directorio.**
2.  **Crear el archivo `.env`** con tu configuración (ver sección anterior).
3.  **Ejecutar:**

```bash
docker-compose up --build
```

4.  Acceder a **[http://localhost:8501](http://localhost:8501)**.

---

## 💻 Instalación Manual (Local)

Si prefieres ejecutarlo sin Docker:

1.  **Crear un entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar el `.env`** (ver sección de configuración).

4.  **Ejecutar la aplicación:**
    ```bash
    streamlit run app.py
    ```

## 📝 Notas de Uso

*   **Añadir Acciones:** Usa el buscador en la parte superior izquierda. Escribe el nombre (ej: "Tesla") y selecciona la coincidencia para añadirla a tu cartera.
*   **Eliminar Acciones:** En la lista "Tu Cartera", pulsa la **X** roja junto al valor que quieras quitar.
*   **Consultar IA:** En el panel de cada acción, haz clic en el botón **"🤖 Analizar con IA"** para obtener un reporte técnico y fundamental basado en los últimos 30 días y noticias recientes.

---
**Disclaimer:** Esta herramienta es solo para fines informativos y educativos. No constituye asesoramiento financiero profesional.
