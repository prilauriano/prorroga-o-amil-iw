import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Dashboard Solar", layout="wide")

st.markdown("## ☀️ Dashboard Solar Cuidados")

# Uploads
col1, col2 = st.columns(2)
with col1:
    arquivos_amil = st.file_uploader("1️⃣ Planilha Principal (IW)", type=["csv", "xlsx"])
with col2:
    arquivos_setores = st.file_uploader("2️⃣ Planilha de Setores", type=["csv", "xlsx"])

# Verificação de segurança: Só processa se houver arquivo
if arquivos_amil is not None:
    try:
        # Carregamento da Principal
        if arquivos_amil.name.endswith('.csv'):
            df = pd.read_csv(arquivos_amil, sep=';', encoding='iso-8859-1')
        else:
            df = pd.read_excel(arquivos_amil)
        
        df.columns = df.columns.str.strip()
        
        # Carregamento da de Setores (Opcional)
        df_s_consolidado = None
        if arquivos_setores is not None:
            if arquivos_setores.name.endswith('.csv'):
                df_s_consolidado = pd.read_csv(arquivos_setores, sep=';', encoding='iso-8859-1')
            else:
                df_s_consolidado = pd.read_excel(arquivos_setores)
            df_s_consolidado.columns = df_s_consolidado.columns.str.strip()
            st.success("Planilhas carregadas com sucesso!")
        
        # --- AQUI VAI O RESTO DO SEU CÓDIGO DE GRÁFICOS ---
        # Exemplo de teste para ver se os dados estão aí:
        st.write("Dados carregados:", df.head())
        
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("💡 Por favor, carregue a planilha no campo 1️⃣ para começar.")
