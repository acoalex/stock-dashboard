import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import streamlit_authenticator as stauth
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="Dashboard Financiero", layout="wide")

# --- Configuración Dinámica desde .env ---
config = {
    'credentials': {
        'usernames': {
            os.getenv('STOCK_USERNAME', 'admin'): {
                'email': os.getenv('STOCK_EMAIL', 'admin@example.com'),
                'name': os.getenv('STOCK_NAME', 'Admin'),
                'password': os.getenv('STOCK_PASSWORD_HASH') 
            }
        }
    },
    'cookie': {
        'name': os.getenv('COOKIE_NAME', 'stock_dashboard_cookie'),
        'key': os.getenv('COOKIE_KEY', 'default_secret_key'),
        'expiry_days': 30
    }
}

# --- Autenticación ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state.get('authentication_status'):
    # --- UI Principal (Solo visible si logueado) ---
    
    # Botón de Logout
    with st.sidebar:
        st.write(f"Bienvenido, *{st.session_state['name']}*")
        authenticator.logout('Cerrar Sesión', 'sidebar')
        st.divider()

    st.title("📈 Dashboard de Acciones Interactivo")

    # --- Barra Lateral ---
    st.sidebar.header("Configuración")
    
    # Configuración de Auto-Refresco
    refresh_options = {
        "Apagado": 0,
        "1 minuto": 60 * 1000,
        "5 minutos": 5 * 60 * 1000,
        "15 minutos": 15 * 60 * 1000
    }
    refresh_selection = st.sidebar.selectbox("Actualización automática:", list(refresh_options.keys()), index=0)
    
    if refresh_options[refresh_selection] > 0:
        st_autorefresh(interval=refresh_options[refresh_selection], key="data_refresh")

    st.sidebar.markdown("---")

    # --- Gestión de Tickers (Estado y Búsqueda) ---
    
    if 'tickers' not in st.session_state:
        st.session_state['tickers'] = ["GOOGL", "NVDA", "TSM", "ORCL", "ACMR", "RNMBF", "BAYN.DE", "EOAN.DE"]

    # Función de búsqueda nativa
    def search_symbols_realtime(search_query: str):
        if not search_query or len(search_query) < 2:
            return []
            
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        headers = {'User-Agent': 'Mozilla/5.0'}
        params = {'q': search_query, 'quotesCount': 8, 'newsCount': 0}
        try:
            r = requests.get(url, headers=headers, params=params)
            data = r.json()
            if 'quotes' in data:
                return [(f"{q['symbol']} - {q.get('shortname', q.get('longname', ''))}", q['symbol']) for q in data['quotes']]
        except:
            pass
        return []

    # 1. Sección: Añadir Nueva Acción (Nativo y Estable)
    st.sidebar.subheader("🔍 Añadir Acción")
    st.sidebar.caption("Escribe y pulsa Enter para buscar:")
    
    search_query = st.sidebar.text_input("Buscar...", key="native_search_input", placeholder="Ej: Apple")

    if search_query and len(search_query) >= 2:
        results = search_symbols_realtime(search_query)
        
        if not results:
            st.sidebar.caption("No se encontraron resultados.")
        else:
            st.sidebar.markdown("**Resultados:**")
            for label, symbol in results[:5]:
                # Usamos use_container_width para que los botones se vean mejor
                if st.sidebar.button(f"➕ {label}", key=f"add_{symbol}", use_container_width=True):
                    if symbol not in st.session_state['tickers']:
                        st.session_state['tickers'].append(symbol)
                        st.success(f"Añadido: {symbol}")
                        st.rerun()
                    else:
                        st.sidebar.warning("Ya está en tu lista.")

    st.sidebar.markdown("---")

    # 2. Sección: Cartera Actual
    st.sidebar.subheader("💼 Tu Cartera")
    for ticker in st.session_state['tickers'][:]:
        col1, col2 = st.sidebar.columns([0.8, 0.2])
        col1.code(ticker)
        if col2.button("❌", key=f"del_{ticker}"):
            st.session_state['tickers'].remove(ticker)
            st.rerun()
    
    st.sidebar.markdown("---")
    
    tickers = st.session_state['tickers']

    if not tickers:
        st.warning("Tu cartera está vacía. Añade acciones desde la barra lateral.")
        st.stop()
        
    st.sidebar.write(f"Monitorizando **{len(tickers)}** activos.")

    # --- Lógica Principal ---
    
    period_options = {
        "1 Mes": "1mo",
        "3 Meses": "3mo",
        "6 Meses": "6mo",
        "1 Año": "1y",
        "2 Años": "2y",
        "5 Años": "5y",
        "Todo el historial": "max"
    }
    
    col_header, col_period = st.columns([3, 1])
    with col_period:
        selected_period_label = st.selectbox("Rango de tiempo:", list(period_options.keys()), index=3)
        selected_period = period_options[selected_period_label]


    # Cacheamos los datos por 5 minutos (300 segundos) para evitar recargas lentas
    @st.cache_data(ttl=300, show_spinner=False)
    def get_stock_data(ticker_symbol, period):
        """Descarga datos de yahoo finance con caché"""
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period=period)
        info = stock.info
        news = stock.news
        return hist, info, news

    def analyze_stock_with_ai(ticker, hist_data, news_data):
        try:
            api_key = os.getenv('LLM_API_KEY')
            base_url = os.getenv('LLM_BASE_URL')
            model_name = os.getenv('LLM_MODEL')
            
            if not api_key:
                return "Error: No se ha configurado la API Key del LLM en el archivo .env"

            client = OpenAI(api_key=api_key, base_url=base_url)
            
            recent_data = hist_data.tail(30).copy()
            recent_data['Change'] = recent_data['Close'].pct_change() * 100
            data_summary = recent_data[['Close', 'Change']].to_string()

            news_summary = ""
            if news_data:
                for n in news_data[:3]:
                    title = n.get('title', 'Sin título')
                    link = n.get('link', '#')
                    news_summary += f"- {title} ({link})\n"
            else:
                news_summary = "No hay noticias recientes disponibles."

            prompt = f"""
            Actúa como un analista financiero experto. Analiza la situación de la acción {ticker}.
            
            --- DATOS TÉCNICOS (Últimos 30 días) ---
            {data_summary}
            
            --- NOTICIAS RECIENTES (Contexto Fundamental) ---
            {news_summary}
            
            Tu respuesta debe ser estricta y directa. Comienza INMEDIATAMENTE con la decisión final. 
            
            Sigue este formato exacto: 
            
            ### 🎯 RECOMENDACIÓN: [COMPRAR | VENDER | MANTENER]
            
            **📈 Análisis Técnico:**
            (Breve resumen)
            
            **📰 Contexto Fundamental:**
            (Impacto noticias)
            
            **⚖️ Justificación:**
            (Explicación)
            """

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "Eres un asistente financiero útil, conciso y analítico."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al consultar la IA: {str(e)}"

    with st.spinner('Cargando datos del mercado...'):
        st.subheader(f"Resumen de Mercado ({selected_period_label})")
        
        valid_tickers = []
        columns_per_row = 4
        current_cols = st.columns(columns_per_row)
        
        for i, ticker in enumerate(tickers):
            if i > 0 and i % columns_per_row == 0:
                current_cols = st.columns(columns_per_row)
            
            col_index = i % columns_per_row
            
            with current_cols[col_index]:
                try:
                    hist, info, _ = get_stock_data(ticker, "5d")
                    if hist.empty:
                        st.error(f"{ticker}: Sin datos")
                        continue
                        
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    delta = current_price - prev_price
                    delta_percent = (delta / prev_price) * 100
                    
                    short_name = info.get('shortName', ticker)
                    currency = info.get('currency', 'USD')
                    symbol = "€" if currency == "EUR" else "$"
                    
                    st.metric(
                        label=f"{short_name} ({ticker})",
                        value=f"{symbol}{current_price:.2f}",
                        delta=f"{delta:.2f} ({delta_percent:.2f}%)"
                    )
                    valid_tickers.append(ticker)
                except Exception as e:
                    st.error(f"Error {ticker}")

        st.markdown("---")
        st.subheader("📊 Análisis Individual y Progresión")
        
        st.markdown("""
        <div style="background-color: #262730; padding: 10px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #444;">
            <h5 style="margin:0; margin-bottom:5px;">ℹ️ Leyenda del Gráfico</h5>
            <span style="color: #00C805; font-weight: bold;">🟢 Vela Verde (Alcista):</span> El precio de <b>Cierre</b> fue mayor que el de Apertura.<br>
            <span style="color: #FF3B30; font-weight: bold;">🔴 Vela Roja (Bajista):</span> El precio de <b>Cierre</b> fue menor que el de Apertura.
        </div>
        """, unsafe_allow_html=True)
        
        for ticker in valid_tickers:
            hist, info, news = get_stock_data(ticker, selected_period)
            if hist.empty:
                continue
            
            short_name = info.get('shortName', ticker)
            currency = info.get('currency', 'USD')
            symbol = "€" if currency == "EUR" else "$"
            
            with st.expander(f"Detalles de {ticker} - {short_name}", expanded=True):
                hist['Daily_Change_Pct'] = hist['Close'].pct_change() * 100
                hist['Daily_Change_Pct'] = hist['Daily_Change_Pct'].fillna(0)

                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='Precio',
                    customdata=hist['Daily_Change_Pct'],
                    hovertemplate=(
                        "<b>Fecha:</b> %{x|%Y-%m-%d}<br>" +
                        f"<b>Apertura:</b> {symbol}%{{open:.2f}}<br>" +
                        f"<b>Alto:</b> {symbol}%{{high:.2f}}<br>" +
                        f"<b>Bajo:</b> {symbol}%{{low:.2f}}<br>" +
                        f"<b>Cierre:</b> {symbol}%{{close:.2f}}<br>" +
                        "<b>Cambio:</b> %{customdata:.2f}%<extra></extra>"
                    )
                ))
                
                fig.update_layout(
                    title=f"Evolución de Precio: {ticker} ({currency})",
                    yaxis_title=f"Precio ({currency})",
                    xaxis_title="Fecha",
                    height=500,
                    template="plotly_dark",
                    xaxis_rangeslider_visible=False 
                )
                st.plotly_chart(fig, use_container_width=True)
                
                col_table, col_ai = st.columns([1, 1])
                with col_table:
                    if st.checkbox(f"Ver datos de tabla para {ticker}", key=f"check_{ticker}"):
                        st.dataframe(hist.sort_index(ascending=False).head(10))
                with col_ai:
                    st.markdown("#### 🧠 Inteligencia Artificial")
                    st.caption("Analiza tendencias de precio y noticias recientes.")
                    if st.button(f"🤖 Analizar {ticker} con IA", key=f"btn_{ticker}"):
                        with st.spinner(f"Leyendo noticias y consultando a {os.getenv('LLM_MODEL')}:"):
                            analysis = analyze_stock_with_ai(ticker, hist, news)
                            with st.expander("📝 Ver Análisis de la IA", expanded=True):
                                st.info(analysis)
    st.success("Actualización completada.")

elif st.session_state.get('authentication_status') is False:
    st.error('Usuario o contraseña incorrectos')
elif st.session_state.get('authentication_status') is None:
    st.warning('Por favor ingresa tu usuario y contraseña')
