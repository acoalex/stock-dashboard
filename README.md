# 📈 Stock Panel Dashboard

Dashboard financiero profesional e interactivo construido con **Python** y **Streamlit**. Permite el seguimiento de acciones en tiempo real, análisis técnico/fundamental y recomendaciones de inversión potenciadas por **Inteligencia Artificial**.

## 🚀 Características Principales

*   **🔐 Seguridad Robusta**: Autenticación integrada con Keycloak (OIDC/OAuth2) para gestión centralizada de usuarios.
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
*   **Seguridad**: python-dotenv, streamlit-oauth (Keycloak OIDC).

---

## ⚙️ Configuración (.env)

El proyecto utiliza variables de entorno para proteger la información sensible. **Antes de arrancar**, debes crear un archivo `.env` en la raíz del proyecto basado en el siguiente ejemplo:

```ini
# --- Keycloak Authentication (OIDC) ---
KEYCLOAK_URL=https://auth.example.com
KEYCLOAK_REALM=your-realm-name
KEYCLOAK_CLIENT_ID=stock-dashboard
KEYCLOAK_CLIENT_SECRET=your-client-secret-here

# --- Redirect URI (must match Keycloak client configuration) ---
# Local development:
REDIRECT_URI=http://localhost:8501
# Production:
# REDIRECT_URI=https://stock.example.com

# --- Role required to access the application ---
REQUIRED_ROLE=stock-user

# --- AI/LLM Configuration ---
LLM_API_KEY=tu_api_key_aqui
LLM_BASE_URL=https://modelhub.example.com/v1
LLM_MODEL=openai/gpt-oss-120b:free
```

### Keycloak Client Setup

1. Create a new client in your Keycloak realm with these settings:
   - **Client ID**: `stock-dashboard`
   - **Access Type**: `confidential`
   - **Standard Flow Enabled**: `ON`
   - **Root URL**: `https://stock.example.com`
   - **Valid Redirect URIs**: `https://stock.example.com/*`
   - **Valid Post Logout Redirect URIs**: `https://stock.example.com/*`
   - **Web Origins**: `https://stock.example.com`

2. Copy the **Client Secret** from the Credentials tab to your `.env` file.

3. Create a role for authorized users:
   - Go to your Client → **Roles** tab → **Create role**
   - **Role name**: `stock-user`
   - Save the role

4. Assign the role to users:
   - Go to **Users** → select a user → **Role Mappings** tab
   - In **Client Roles**, select your client (`stock-dashboard`)
   - Add the `stock-user` role to the user

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
