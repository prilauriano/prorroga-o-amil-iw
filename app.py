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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700;800&display=swap');
    
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
    
    .stDataFrame {
        background-color: #FFFFFF !important;
        border: 1px solid #E2DDD6 !important;
        border-radius: 12px !important;
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
        
        # Mapeando e limpando o campo 'ID Orçam.' correto da Amil
        for c in ['Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Nr. Matricula', 'Pessoa Resp Aut', 'Classific. Atendimento', 'Nome do Paciente', 'ID Orçam.']:
            if c in df.columns:
                df[c] = df[c].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            elif c == 'ID Orçam.':
                df['ID Orçam.'] = ''
        
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

        # --- PROCESSAMENTO DOS SETORES ---
        atendimentos_pendentes_setores = set()
        df_s_consolidado = None
        setores_agrupados = None
        
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
                df_s_consolidado['Grupo Especialidade'] = df_s_consolidado['Grupo Especialidade'].fillna('Outros').astype(str).str.strip()
                atendimentos_pendentes_setores = set(df_s_consolidado['Nº Atendimento'].unique())
                
                setores_agrupados = df_s_consolidado.groupby('Nº Atendimento')['Grupo Especialidade'].apply(
                    lambda x: ', '.join(sorted(set(x)))
                ).reset_index()
                setores_agrupados.columns = ['Nr. Atendimento', 'Especialidades Pendentes']

        if setores_agrupados is not None:
            df = pd.merge(df, setores_agrupados, on='Nr. Atendimento', how='left')
            df['Especialidades Pendentes'] = df['Especialidades Pendentes'].fillna('Nenhuma pendência técnica apontada')
        else:
            df['Especialidades Pendentes'] = 'Aguardando planilha de setores técnica...'

        df['Tem_Pendencia_Setor'] = df['Nr. Atendimento'].isin(atendimentos_pendentes_setores)

        # Filtros das Tabelas Visuais
        df_liberados = df[(df['Inserido_Amil'] == False) & (df['Tem_Pendencia_Setor'] == False)].copy()
        df_liberados = df_liberados.sort_values(by='Valor a Cobrar', ascending=False)

        df_prontuario = df[df['Status Aut Orç'] == 'Prontuário Pendente'].sort_values(by='Valor a Cobrar', ascending=False)
        df_ops = df[df['Status Aut Orç'] == 'OPS Pendente'].sort_values(by='Valor a Cobrar', ascending=False)

        # Indicadores globais
        total_pacientes = len(df)
        inseridos = df['Inserido_Amil'].sum()
        faltam = total_pacientes - inseridos
        valor_total_pendente = df[df['Inserido_Amil'] == False]['Valor a Cobrar'].sum()
        pacientes_com_erro = df[(df['Nr. Matricula'].str.len() == 0) | (df['Nr. Atendimento'].isna())]

        # --- ABAS DO DASHBOARD ---
        aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
            "⭐ Resumo Geral", 
            "👤 Gestão de Equipe", 
            "🏥 Segmentação ID / AD", 
            "📋 Listas de Prorrogação", 
            "🚀 Liberados para Input",
            "🚨 Alertas de Erro"
        ])
        
        with aba1:
            st.markdown("### 📌 Indicadores Operacionais e Financeiros")
            card1, card2, card3, card4, card5 = st.columns(5)
            card1.metric("Total Linhas (IW)", f"{total_pacientes}")
            card2.metric("✅ Inseridos", f"{inseridos}")
            card3.metric("⏳ Pendentes", f"{faltam}")
            card4.metric("🚀 Liberados p/ Input", f"{len(df_liberados)}")
            card5.metric("💰 Represado Total", f"R$ {valor_total_pendente:,.2f}")
            
            # --- NOVO SEGUNDO BOTÃO: DOWNLOAD DA PLANILHA COMPLETA TOTALMENTE LIMPA ---
            st.markdown("### 📥 Exportação de Dados Limpos")
            buffer_completo = io.BytesIO()
            with pd.ExcelWriter(buffer_completo, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Base Consolidada IW', index=False)
            
            st.download_button(
                label="🟢 Baixar Planilha Consolidada COMPLETA (Excel Limpo)",
                data=buffer_completo.getvalue(),
                file_name="base_consolidada_iw_limpa.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Clique aqui para baixar todas as linhas originais do IW já devidamente separadas em colunas limpas no Excel."
            )
            st.markdown("---")
            
            coluna_setor = next((col for col in df.columns if 'Setor' in col or 'Região' in col or 'SAD' in col), None)
            if not coluna_setor and 'Setor' in df.columns:
                coluna_setor = 'Setor'
            if coluna_setor:
                st.markdown("### 🗺️ Gráfico por Setor Regional (SAD)")
                df_graf_setor = df[coluna_setor].value_counts().reset_index()
                df_graf_setor.columns = ['Setor', 'Quantidade de Pacientes']
                fig_setor = px.bar(df_graf_setor, x='Setor', y='Quantidade de Pacientes', color='Setor', text_auto=True, color_discrete_sequence=px.colors.sequential.RdBu)
                fig_setor.update_traces(textposition='outside')
                fig_setor.update_layout(showlegend=False)
                st.plotly_chart(fig_setor, use_container_width=True)

            if df_s_consolidado is not None:
                st.markdown("---")
                st.markdown("### 🏢 Pendências de Relatório por Setor Multidisciplinar")
                df_amil_v = df[['Nr. Atendimento', 'Valor a Cobrar']].copy()
                df_setores_valores = pd.merge(df_s_consolidado, df_amil_v, left_on='Nº Atendimento', right_on='Nr. Atendimento', how='left')
                
                analise_setores = df_setores_valores.groupby('Grupo Especialidade').agg(
                    Quantidade=('ID Pront.', 'count'),
                    Valor_Total=('Valor a Cobrar', 'sum')
                ).reset_index().sort_values(by='Quantidade', ascending=False)
                
                set_col1, set_col2 = st.columns(2)
                with set_col1:
                    fig_qtd = px.bar(analise_setores, x='Grupo Especialidade', y='Quantidade', title="<b>Quantidade de Relatórios Pendentes por Setor</b>", text_auto=True)
                    fig_qtd.update_traces(marker_color='#5C1220', textposition='outside')
                    fig_qtd.update_layout(xaxis_title="Setor Técnico", yaxis_title="Nº de Pendências", plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#E2DDD6'))
                    st.plotly_chart(fig_qtd, use_container_width=True)
                    
                with set_col2:
                    fig_val = px.bar(analise_setores, x='Grupo Especialidade', y='Valor_Total', title="<b>Impacto Financeiro Bloqueado por Setor (R$)</b>", text_auto='.2f')
                    fig_val.update_traces(marker_color='#C07C20', textposition='outside')
                    fig_val.update_layout(xaxis_title="Setor Técnico", yaxis_title="Valor Represado (R$)", plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#E2DDD6'))
                    st.plotly_chart(fig_val, use_container_width=True)

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

        with aba4:
            st.markdown("### 📋 Prorrogações Ordenadas pelos Maiores Valores")
            tab_p, tab_o = st.tabs(["📄 Prontuário Pendente", "🏢 OPS Pendente"])
            with tab_p:
                st.markdown(f"**Total de Processos: {len(df_prontuario)} | Montante: R$ {df_prontuario['Valor a Cobrar'].sum():,.2f}**")
                df_p_view = df_prontuario[['Nr. Atendimento', 'Nome do Paciente', 'ID Orçam.', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_p_view.columns = ['Nº Atendimento', 'Paciente', 'ID Orçamento', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor a Cobrar (R$)']
                st.dataframe(df_p_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
            with tab_o:
                st.markdown(f"**Total de Processos: {len(df_ops)} | Montante: R$ {df_ops['Valor a Cobrar'].sum():,.2f}**")
                df_o_view = df_ops[['Nr. Atendimento', 'Nome do Paciente', 'ID Orçam.', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_o_view.columns = ['Nº Atendimento', 'Paciente', 'ID Orçamento', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor a Cobrar (R$)']
                st.dataframe(df_o_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba5:
            st.markdown("### 🚀 Pacientes Liberados (Sem Pendências nos Setores)")
            if not arquivos_setores:
                st.warning("⚠️ Para ver quem está liberado, carregue a planilha de Setores no campo de upload.")
            else:
                st.markdown(f"**🔥 Total Prontos para Input: {len(df_liberados)} | Valor de Giro Rápido: R$ {df_liberados['Valor a Cobrar'].sum():,.2f}**")
                
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
                df_liberados_view = df_liberados[['Nr. Atendimento', 'Nome do Paciente', 'ID Orçam.', 'Tipo_Atendimento', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_liberados_view.columns = ['Nº Atendimento', 'Paciente', 'ID Orçamento', 'Tipo Atendimento', 'Responsável', 'Valor a Cobrar (R$)']
                st.dataframe(df_liberados_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba6:
            st.markdown("### 🚨 Cadastros Incompletos / Erros no IW")
            df_erro_view = pacientes_com_erro[['Nr. Atendimento', 'Nome do Paciente', 'ID Orçam.', 'Nr. Matricula', 'Pessoa Resp Aut']].copy()
            df_erro_view.columns = ['Nº Atendimento', 'Paciente', 'ID Orçamento', 'Matrícula', 'Responsável']
            st.dataframe(df_erro_view, use_container_width=True, hide_index=True)
                    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Selecione os arquivos acima para carregar o cruzamento dinâmico.")
