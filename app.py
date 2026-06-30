import streamlit as st
import pandas as pd
import plotly.express as px
import re
import io

# 1. Configuração de página
st.set_page_config(page_title="Dashboard Prorrogações | Solar Cuidados", page_icon="☀️", layout="wide")

# 2. Injeção da Paleta de Cores Exata do Site (Bordô, Dourado e Off-White)
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
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #C07C20, #E09A30); 
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .brand-title {
        color: #FFFFFF !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -.2px;
    }
    .brand-title span {
        color: #E09A30 !important;
    }
    .subtitle {
        font-size: 13px;
        color: #8A7D72 !important;
        margin-top: 5px;
        margin-bottom: 25px;
        font-weight: 500;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F3F0EC !important; 
        border: 1px solid #E2DDD6 !important; 
        color: #52473E !important; 
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 11px !important;
        letter-spacing: .2px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #5C1220 !important; 
        color: #FFFFFF !important;
        border-color: #5C1220 !important;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2DDD6 !important;
        border-radius: 12px !important; 
        padding: 14px 18px !important;
        box-shadow: 0 2px 8px rgba(28,14,10,.08) !important; 
        border-left: 4px solid #C07C20 !important; 
    }
    div[data-testid="stMetricLabel"] {
        color: #5C1220 !important; 
        font-weight: 700 !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: .5px;
    }
    div[data-testid="stMetricValue"] {
        color: #1A1714 !important;
        font-weight: 800 !important;
        font-size: 26px !important;
        letter-spacing: -1px;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho Oficial
st.markdown("""
    <div class="topbar-header">
        <div class="brand-mark">☀️</div>
        <h1 class="brand-title">Solar Cuidados — <span>Prorrogações</span></h1>
    </div>
""", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Módulo operacional integrado de auditoria Amil IW, monitoramento de prazos e volumetria ID/AD.</p>', unsafe_allow_html=True)

# Máscaras de Proteção Visual para LGPD
def ocultar_nome_paciente(nome):
    if not nome or pd.isna(nome): return "Paciente Protegido"
    partes = str(nome).strip().split()
    return " ".join([p[0] + "*" * (len(p) - 1) if len(p) > 1 else p for p in partes])

def ocultar_matricula(mat):
    mat_str = str(mat).strip()
    if not mat_str or mat_str.lower() == 'nan': return "******"
    return mat_str[:2] + "****" + mat_str[-2:] if len(mat_str) > 4 else "****"

# --- ÁREA DE UPLOAD ---
col_up1, col_up2 = st.columns(2)
with col_up1:
    arquivos_amil = st.file_uploader("1️⃣ Selecione planilhas PRINCIPAIS do IW (.csv)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up2:
    arquivos_setores = st.file_uploader("2️⃣ Selecione planilha de PENDÊNCIAS DOS SETORES (.csv)", type=["csv", "xlsx"], accept_multiple_files=True)

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
        
        for c in ['Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Nr. Matricula', 'Pessoa Resp Aut', 'Classific. Atendimento', 'Nome do Paciente']:
            if c in df.columns:
                df[c] = df[c].fillna('').astype(str).str.strip()
        
        df['Nr. Atendimento'] = df['Nr. Atendimento'].astype(str).str.strip()
        
        def converter_moeda_br(valor):
            valor_str = str(valor).strip()
            if not valor_str or valor_str.lower() == 'nan': return 0.0
            if re.search(r',\d{2}$', valor_str): valor_str = valor_str.replace('.', '').replace(',', '.')
            else: valor_str = valor_str.replace('.', '').replace(',', '.')
            try: return float(valor_str)
            except: return 0.0

        df['Valor a Cobrar'] = df['Valor a Cobrar'].apply(converter_moeda_br)
        df['Tipo_Atendimento'] = df['Classific. Atendimento'].apply(
            lambda x: 'ID (Internação Domiciliar)' if x.startswith('ID') else ('AD (Atenção Domiciliar)' if x.startswith('AD') else 'Outros')
        )

        guia_valida_numerica = df['Nº Guia Solicitação (TISS)'].str.isnumeric()
        df['Inserido_Amil'] = (guia_valida_numerica) | (df['Senha Aprovação'] != '') | (df['Status Aut Orç'] == 'Autorizado')

        # --- PROCESSAMENTO EXCLUSIVO DE SETORES (CRUZAMENTO ANTI-PENDÊNCIA) ---
        atendimentos_pendentes_setores = set()
        df_s_consolidado = None
        
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
            if 'Nº Atendimento' in df_s_consolidado.columns:
                df_s_consolidado['Nº Atendimento'] = df_s_consolidado['Nº Atendimento'].astype(str).str.strip()
                atendimentos_pendentes_setores = set(df_s_consolidado['Nº Atendimento'].unique())

        # Identificação de quem tem pendência técnica no dataframe principal
        df['Tem_Pendencia_Setor'] = df['Nr. Atendimento'].isin(atendimentos_pendentes_setores)

        # --- FILTRO DO CAMINHO LIVRE (Liberados para Input) ---
        # Regra: Não pode ter sido inserido no portal AINDA E não pode estar na planilha de pendência dos setores
        df_liberados = df[(df['Inserido_Amil'] == False) & (df['Tem_Pendencia_Setor'] == False)].copy()
        df_liberados = df_liberados.sort_values(by='Valor a Cobrar', ascending=False)

        # Totais para os Cards
        total_pacientes = len(df)
        inseridos = df['Inserido_Amil'].sum()
        faltam = total_pacientes - inseridos
        valor_total_pendente = df[df['Inserido_Amil'] == False]['Valor a Cobrar'].sum()

        # --- ABAS DO DASHBOARD ---
        aba1, aba2, aba3, aba4, aba5 = st.tabs([
            "⭐ Resumo Geral", 
            "👤 Gestão de Equipe", 
            "🏥 Segmentação ID / AD", 
            "🚀 Liberados para Input", # ABA REESTRUTURADA
            "🚨 Alertas de Erro"
        ])
        
        with aba1:
            st.markdown("### 📌 Indicadores Operacionais e Financeiros")
            card1, card2, card3, card4, card5 = st.columns(5)
            card1.metric("Total Linhas (IW)", f"{total_pacientes}")
            card2.metric("✅ Inseridos", f"{inseridos}")
            card3.metric("⏳ Pendentes", f"{faltam}")
            card4.metric("🚀 Liberados p/ Input", f"{len(df_liberados)}")
            card5.metric("💰 Represado Total (R$)", f"R$ {valor_total_pendente:,.2f}")
            
            coluna_setor = next((col for col in df.columns if 'Setor' in col or 'Região' in col or 'SAD' in col), None)
            if coluna_setor:
                st.markdown("### 🗺️ Gráfico por Setor Regional (SAD)")
                df_graf_setor = df[coluna_setor].value_counts().reset_index()
                df_graf_setor.columns = ['Setor', 'Quantidade de Pacientes']
                fig_setor = px.bar(df_graf_setor, x='Setor', y='Quantidade de Pacientes', color='Setor', text_auto=True, color_discrete_sequence=px.colors.sequential.RdBu)
                fig_setor.update_layout(showlegend=False)
                st.plotly_chart(fig_setor, use_container_width=True)

        with aba2:
            st.markdown("### 👤 Produtividade e Carga Operacional")
            col_responsavel = 'Pessoa Resp Aut'
            col_paciente = 'Nome do Paciente'
            df_inputs = df.groupby(col_responsavel)['Inserido_Amil'].sum().reset_index()
            df_inputs.columns = [col_responsavel, 'Total de Inputs Realizados']
            df_unicos = df.drop_duplicates(subset=[col_responsavel, col_paciente]).copy()
            df_unicos['Qtd_ID'] = df_unicos['Tipo_Atendimento'] == 'ID (Internação Domiciliar)'
            df_unicos['Qtd_AD'] = df_unicos['Tipo_Atendimento'] == 'AD (Atenção Domiciliar)'
            
            prod_colab = df_unicos.groupby(col_responsavel).agg(Pacientes_ID=('Qtd_ID', 'sum'), Pacientes_AD=('Qtd_AD', 'sum'), Total_Pacientes=(col_paciente, 'count')).reset_index()
            prod_colab.columns = [col_responsavel, 'Nº Pacientes ID', 'Nº Pacientes AD', 'Quantitativo Total Pacientes']
            resumo_equipe = pd.merge(prod_colab, df_inputs, on=col_responsavel)
            st.dataframe(resumo_equipe, use_container_width=True, hide_index=True)

        with aba3:
            st.markdown("### 🏥 Análise do Modelo de Atendimento Solar (ID vs AD)")
            df_id_ad = df[df['Inserido_Amil'] == False].groupby('Tipo_Atendimento').agg(Quantidade=('Nome do Paciente', 'count'), Valor_Total=('Valor a Cobrar', 'sum')).reset_index()
            st.dataframe(df_id_ad.style.format({'Valor_Total': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        # --- 🚀 REESTRUTURAÇÃO COMPLETA DA ABA 4: LIBERADOS PARA INPUT ---
        with aba4:
            st.markdown("### 🚀 Pacientes com Sinal Verde (Sem Pendências nos Setores)")
            st.markdown("Esta lista mostra exclusivamente os pacientes que estão **represados**, mas que **não possuem nenhuma pendência** na planilha dos setores multidisciplinares. Estão prontos para digitação!")
            
            if not arquivos_setores:
                st.warning("⚠️ Para filtrar quem está liberado, você precisa carregar a Planilha de Setores técnica no campo de upload acima.")
            else:
                st.markdown(f"**🔥 Total de Processos Prontos para Input: {len(df_liberados)} | Carga Financeira de Giro Rápido: R$ {df_liberados['Valor a Cobrar'].sum():,.2f}**")
                
                # Criando arquivo de download em Excel REAL com dados COMPLETOS (sem máscara para você poder trabalhar)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_liberados.to_excel(writer, sheet_name='Liberados Para Input', index=False)
                
                st.download_button(
                    label="📥 Baixar Planilha de Liberados (Excel)",
                    data=buffer.getvalue(),
                    file_name="pacientes_liberados_input_solar.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.markdown("---")
                st.write("**📋 Lista de Execução Visual (Nomes mascarados na tela por segurança):**")
                
                # Exibição segura em tela
                df_liberados_view = df_liberados[['Nr. Atendimento', 'Nome do Paciente', 'Tipo_Atendimento', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_liberados_view['Nome do Paciente'] = df_liberados_view['Nome do Paciente'].apply(ocultar_nome_paciente)
                df_liberados_view.columns = ['Nº Atendimento', 'Paciente', 'Tipo Atendimento', 'Responsável Aut.', 'Valor a Cobrar (R$)']
                
                st.dataframe(df_liberados_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba5:
            st.markdown("### 🚨 Cadastros Incompletos / Erros no IW")
            pacientes_com_erro = df[(df['Nr. Matricula'].str.len() == 0) | (df['Nr. Atendimento'].isna())]
            st.dataframe(pacientes_com_erro[['Nr. Atendimento', 'Nome do Paciente', 'Nr. Matricula', 'Pessoa Resp Aut']], use_container_width=True, hide_index=True)
                    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Selecione os arquivos acima para carregar o cruzamento dinâmico.")
