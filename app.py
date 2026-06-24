import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. Configuração de página
st.set_page_config(page_title="Dashboard Prorrogações | Solar Cuidados", page_icon="☀️", layout="wide")

# CSS para o design (Vinho/Dourado)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FAFAF9 !important; 
        color: #1A1714 !important; 
        font-family: 'Inter', sans-serif !important;
    }
    .topbar-header {
        background-color: #3D0B16 !important; 
        padding: 12px 20px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .brand-mark {
        width: 38px; height: 38px;
        background: linear-gradient(135deg, #C07C20, #E09A30); 
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .brand-title { color: #FFFFFF !important; font-size: 22px !important; font-weight: 800 !important; margin: 0 !important; }
    .brand-title span { color: #E09A30 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Cabeçalho
st.markdown("""
    <div class="topbar-header">
        <div class="brand-mark">☀️</div>
        <h1 class="brand-title">Solar Cuidados — <span>Prorrogações</span></h1>
    </div>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO SEGURA ---
df_s_consolidado = None 

# --- ÁREA DE UPLOAD ---
col_up1, col_up2 = st.columns(2)
with col_up1:
    arquivos_amil = st.file_uploader("1️⃣ Selecione planilhas PRINCIPAIS do IW (.csv)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up2:
    arquivos_setores = st.file_uploader("2️⃣ [Opcional] Selecione planilhas de SETORES (.csv)", type=["csv", "xlsx"], accept_multiple_files=True)

if arquivos_amil:
    try:
        # --- PROCESSAMENTO PRINCIPAL ---
        lista_dfs_amil = []
        for arq in arquivos_amil:
            if arq.name.endswith('.csv'):
                try: df_temp = pd.read_csv(arq, sep=';', encoding='utf-8')
                except: 
                    arq.seek(0)
                    df_temp = pd.read_csv(arq, sep=';', encoding='iso-8859-1')
            else:
                df_temp = pd.read_excel(arq)
            df_temp.columns = df_temp.columns.str.strip()
            lista_dfs_amil.append(df_temp)
        
        df = pd.concat(lista_dfs_amil, ignore_index=True)
        
        # --- PROCESSAMENTO SETORES (PROTEGIDO) ---
        if arquivos_setores:
            lista_dfs_setores = []
            for arq_s in arquivos_setores:
                if arq_s.name.endswith('.csv'):
                    try: df_s_temp = pd.read_csv(arq_s, sep=';', encoding='utf-8')
                    except: 
                        arq_s.seek(0)
                        df_s_temp = pd.read_csv(arq_s, sep=';', encoding='iso-8859-1')
                else:
                    df_s_temp = pd.read_excel(arq_s)
                df_s_temp.columns = df_s_temp.columns.str.strip()
                lista_dfs_setores.append(df_s_temp)
            df_s_consolidado = pd.concat(lista_dfs_setores, ignore_index=True)

        # (CONTINUE AQUI O RESTO DA SUA LÓGICA DE PROCESSAMENTO E ABAS...)
        # ... seu código de processamento de colunas e cálculos continua aqui ...

        # --- EXEMPLO DE COMO USAR A VARIÁVEL AGORA ---
        if df_s_consolidado is not None:
             st.success("Setores carregados com sucesso!")
        
    except Exception as e:
        st.error(f"Erro: {e}")
