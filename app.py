import streamlit as st
import pandas as pd
import re

# Configuração padrão da página
st.set_page_config(page_title="Dashboard Prorrogações Amil", page_icon="☀️", layout="wide")

# CSS Avançado Dinâmico para Modo Claro/Escuro
st.markdown("""
    <style>
    @media (prefers-color-scheme: light) {
        .main-title { color: #4A148C !important; }
        .subtitle { color: #555555 !important; }
        div[data-testid="stMetric"] { background-color: #F8F9FA !important; border: 1px solid #EAEAEA !important; }
        div[data-testid="stMetricLabel"] { color: #4A148C !important; }
        div[data-testid="stMetricValue"] { color: #1A1A1A !important; }
    }
    @media (prefers-color-scheme: dark) {
        .main-title { color: #BA68C8 !important; }
        .subtitle { color: #B0BEC5 !important; }
        div[data-testid="stMetric"] { background-color: #1E1E1E !important; border: 1px solid #333333 !important; }
        div[data-testid="stMetricLabel"] { color: #BA68C8 !important; }
        div[data-testid="stMetricValue"] { color: #FFFFFF !important; }
    }
    .header-container { display: flex; align-items: center; gap: 15px; margin-bottom: 10px; }
    .logo-img { max-height: 60px; width: auto; }
    .main-title { font-size: 32px; font-weight: 800; font-family: sans-serif; margin: 0; }
    .solar-accent { color: #FFB300 !important; }
    .subtitle { font-size: 15px; margin-top: 5px; margin-bottom: 25px; }
    div[data-testid="stMetricLabel"] { font-weight: 700 !important; font-size: 13px !important; text-transform: uppercase !important; }
    div[data-testid="stMetricValue"] { font-weight: 700 !important; font-size: 28px !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
LINK_DA_LOGO = "COLOQUE_O_LINK_DA_SUA_LOGO_AQUI" 

if LINK_DA_LOGO != "COLOQUE_O_LINK_DA_SUA_LOGO_AQUI":
    st.markdown(f"""
        <div class="header-container">
            <img src="{LINK_DA_LOGO}" class="logo-img">
            <p class="main-title">Dashboard Prorrogações <span class="solar-accent">Solar Cuidados</span></p
