import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import math

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="BVMAC Analyst Pro", layout="wide", page_icon="📈")

# --- GESTION DES IMPORTATIONS (SÉCURITÉ IA pour le Cloud) ---
AI_AVAILABLE = False
SKLEARN_AVAILABLE = False

try:
    from prophet import Prophet
    AI_AVAILABLE = True
except ImportError:
    try:
        from sklearn.linear_model import LinearRegression
        SKLEARN_AVAILABLE = True
    except ImportError:
        pass
        
# --- 1. CHARGEMENT ROBUSTE DES DONNÉES (EXCEL et CSV) ---
@st.cache_data
def load_data(file):
    """Essaie de lire le fichier en priorisant Excel, puis tente divers formats CSV."""
    df = None
    
    # Tentative 1: Lecture EXCEL (.xlsx)
    if hasattr(file, 'name') and file.name.endswith(('.xlsx', '.xls')):
        try:
            st.info("Tentative de lecture du fichier Excel...")
            df = pd.read_excel(file, engine='openpyxl')
        except Exception:
            pass
            
    # Tentative 2: Lecture CSV robuste
    if df is None:
        try:
            st.info("Tentative de lecture du fichier CSV (robuste)...")
            # Utilise 'engine=python' pour tolérer les lignes incohérentes
            df = pd.read_csv(file, sep=None, engine='python', dayfirst=True)
            if len(df.columns) < 2:
                 df = None
        except Exception:
            # Tentative 3: CSV standard point-virgule
            try:
                df = pd.read_csv(file, sep=';', dayfirst=True)
            except Exception:
                 df = None
    
    if df is not None:
        # Nettoyage
        df.columns = df.columns.str.strip()
        
        # Gestion des décimales (FCFA utilise la virgule)
        if 'Cours_rfrnc' in df.columns:
            df['Cours_rfrnc'] = df['Cours_rfrnc'].astype(str).str.replace(',', '.', regex=False)
            df['Cours_rfrnc'] = pd.to_numeric(df['Cours_rfrnc'], errors='coerce')
        
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        
        df = df.dropna(subset=['Date', 'Cours_rfrnc'])
            
        return df.sort_values(by='Date')
    
    return None

# --- 2. CALCUL DES INDICATEURS TECHNIQUES (RSI, MACD) ---
def add_indicators(df):
    
    # Moyennes Mobiles
    df['SMA_20'] = df['Cours_rfrnc'].rolling(window=20).mean()
    df['SMA_50'] = df['Cours_rfrnc'].rolling(window=50).mean()
    
    # Bandes de Bollinger
    df['STD_20'] = df['Cours_rfrnc'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA_20'] + (df['STD_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['STD_20'] * 2)
    
    # RSI (Relative Strength Index)
    delta = df['Cours_rfrnc'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp12 = df['Cours_rfrnc'].ewm(span=12, adjust=False).mean()
    exp26 = df['Cours_rfrnc'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    return df

# --- 3. FONCTIONS DE PRÉVISION (IA ou Linéaire) ---
def get_forecast(df, days):
    df_clean = df[['Date', 'Cours_rfrnc']].dropna()
    
    if AI_AVAILABLE:
        df_prophet = df_clean.rename(columns={'Date': 'ds', 'Cours_rfrnc': 'y'})
        m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True)
        m.fit(df_prophet)
        future = m.make_future_dataframe(periods=days)
        forecast = m.predict(future)
        return forecast, "AI"
        
    elif SKLEARN_AVAILABLE:
        df_reg = df_clean.copy()
        df_reg['Date_Ordinal'] = df_reg['Date'].map(pd.Timestamp.toordinal)
        
        X = df_reg[['Date_Ordinal']]
        y = df_reg['Cours_rfrnc']
        
        model = LinearRegression()
        model.fit(X, y)
        
        last_date = df_reg['Date'].max()
        future_dates = [last_date + pd.Timedelta(days=x) for x in range(1, days + 1)]
        future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        future_pred = model.predict(future_ordinals)
        
        return pd.DataFrame({'ds': future_dates, 'yhat': future_pred}), "Linear"
    
    return None, None

# --- 4. INTERFACE UTILISATEUR ET AFFICHAGE ---

# Le fichier par défaut n'est pas utilisé sur streamlit.io, l'utilisateur doit uploader son fichier.
st.title("📈 BVMAC Analyst Pro")
uploaded_file = st.sidebar.file_uploader("📂 Charger votre fichier (CSV ou XLSX)", type=['csv', 'xlsx', 'xls'])

# Seul le fichier uploadé sera chargé
df = load_data(uploaded_file)

if df is not None and 'Mnemo' in df.columns and len(df) > 0:
    try:
        st.sidebar.markdown("---")
        
        liste_actions = df['Mnemo'].unique()
        choix = st.sidebar.selectbox("🔎 Choisir l'action", liste_actions)
        
        # --- OPTIONS GRAPHIQUE ---
        st.sidebar.header("Options de visualisation")
        log_scale = st.sidebar.checkbox("Échelle Logarithmique (Axe Y)", value=False)
        show_bollinger = st.sidebar.checkbox("Afficher Bandes de Bollinger", value=True)
        show_rsi = st.sidebar.checkbox("Afficher RSI (14)", value=True)
        show_macd = st.sidebar.checkbox("Afficher MACD", value=True)
        
        data = df[df['Mnemo'] == choix].copy()
        
        if len(data) >= 20:
             data = add_indicators(data)
             
             # Détermine le nombre de sous-graphiques à afficher
             num_rows = 1 + show_rsi + show_macd
             
             # Poids des lignes
             row_heights_list = [0.6]
             if show_rsi:
                 row_heights_list.append(0.2)
             if show_macd:
                 row_heights_list.append(0.2)
                 
             # Titres des sous-graphiques
             titles_list = ["Cours & Bollinger"]
             if show_rsi:
                 titles_list.append("RSI (14)")
             if show_macd:
                 titles_list.append("MACD")
                 
             fig = make_subplots(rows=num_rows, cols=1, shared_xaxes=True, 
                                 vertical_spacing=0.03, row_heights=row_heights_list,
                                 subplot_titles=titles_list)
             
             # --- GRAPHIQUE PRIX / INDICATEURS ---
             st.subheader(f"Analyse Technique : {choix}")
             
             # 1. PRIX (LISSAGE MONOTONE)
             fig.add_trace(go.Scatter(x=data['Date'], y=data['Cours_rfrnc'], name="Prix", line=dict(color='blue'), line_shape='spline'), row=1, col=1)
             
             # Bandes de Bollinger (LISSAGE MONOTONE)
             if show_bollinger:
                 fig.add_trace(go.Scatter(x=data['Date'], y=data['Upper_Band'], name="Bande Sup.", line=dict(width=1, color='rgba(128,128,128,0.5)'), showlegend=False, line_shape='spline'), row=1, col=1)
                 fig.add_trace(go.Scatter(x=data['Date'], y=data['Lower_Band'], name="Bande Inf.", line=dict(width=1, color='rgba(128,128,128,0.5)'), fill='tonexty', fillcolor='rgba(128,128,128,0.2)', showlegend=False, line_shape='spline'), row=1, col=1)
             
             # Configuration de l'échelle Logarithmique
             if log_scale:
                 fig.update_yaxes(type="log", row=1, col=1)
                 
             row_index = 2
             
             # 2. RSI (LISSAGE MONOTONE)
             if show_rsi:
                 fig.add_trace(go.Scatter(x=data['Date'], y=data['RSI'], name="RSI", line=dict(color='purple'), line_shape='spline'), row=row_index, col=1)
                 fig.add_hline(y=70, line_dash="dot", line_color="red", row=row_index, col=1)
                 fig.add_hline(y=30, line_dash="dot", line_color="green", row=row_index, col=1)
                 row_index += 1
             
             # 3. MACD (LISSAGE MONOTONE)
             if show_macd:
                 fig.add_trace(go.Scatter(x=data['Date'], y=data['MACD'], name="MACD", line=dict(color='black'), line_shape='spline'), row=row_index, col=1)
                 fig.add_trace(go.Scatter(x=data['Date'], y=data['Signal_Line'], name="Signal", line=dict(color='red'), line_shape='spline'), row=row_index, col=1)
                 colors = np.where(data['MACD'] - data['Signal_Line'] > 0, 'green', 'red')
                 fig.add_trace(go.Bar(x=data['Date'], y=data['MACD'] - data['Signal_Line'], name="Hist", marker_color=colors), row=row_index, col=1)
             
             fig.update_layout(height=700, hovermode="x unified", template="plotly_white")
             st.plotly_chart(fig, use_container_width=True)
             
             # --- PRÉVISIONS ---
             st.markdown("---")
             if st.checkbox("Afficher les prévisions"):
                 days = st.slider("Horizon de prévision (jours)", 30, 180, 90)
                 forecast_df, method = get_forecast(data, days)
                 
                 if forecast_df is not None:
                     st.subheader(f"🔮 Projection sur {days} jours")
                     fig_pred = go.Figure()
                     
                     # Historique (Lissé)
                     fig_pred.add_trace(go.Scatter(x=data['Date'], y=data['Cours_rfrnc'], name="Historique", line_shape='spline'))
                     
                     # Prévision (Lissée)
                     future_only = forecast_df[forecast_df['ds'] > data['Date'].max()]
                     fig_pred.add_trace(go.Scatter(x=future_only['ds'], y=future_only['yhat'], name="Prévision", line=dict(dash='dash', color='orange'), line_shape='spline'))
                     
                     # Marge d'erreur (si IA)
                     if method == "AI" and 'yhat_upper' in forecast_df.columns:
                          fig_pred.add_trace(go.Scatter(
                             x=future_only['ds'].tolist() + future_only['ds'].tolist()[::-1],
                             y=future_only['yhat_upper'].tolist() + future_only['yhat_lower'].tolist()[::-1],
                             fill='toself', fillcolor='rgba(255,165,0,0.2)', line=dict(width=0), name="Marge d'erreur"
                         ))
                     
                     if log_scale:
                         fig_pred.update_yaxes(type="log")
                         
                     fig_pred.update_layout(title=f"Projection future : {choix}", yaxis_title="Prix (FCFA)")
                     st.plotly_chart(fig_pred, use_container_width=True)
                     
                     if method == "AI":
                         st.success("Modèle : Intelligence Artificielle (Prophet).")
                     else:
                         st.info("Modèle : Régression Linéaire (outil simple de tendance).")

                 else:
                     st.error("Aucune librairie de prévision n'est installée. Impossible de générer la projection.")
        else:
             st.warning(f"L'action {choix} n'a pas assez de données pour l'analyse technique (min 20 jours requis).")

    except Exception as e:
        st.error(f"Une erreur est survenue lors du traitement : {e}")
        # Optionnel: afficher les premières lignes pour aider l'utilisateur à débugger
        # st.dataframe(df.head())

else:
    st.info("Veuillez charger votre fichier de données pour commencer l'analyse.")
