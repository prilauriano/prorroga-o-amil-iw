import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. Configuração de página
st.set_page_config(page_title="Dashboard Prorrogações | Solar Cuidados", page_icon="☀️", layout="wide")

# 2. Injeção da Paleta de Cores Exata do CSS do Site (Bordô, Dourado e Off-White)
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
        font-size: 30px !important;
        letter-spacing: -1px;
    }
    
    .stDataFrame {
        background-color: #FFFFFF !important;
        border: 1px solid #E2DDD6 !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Cabeçalho
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
        
        colunas_obrigatorias = ['Nr. Matricula', 'Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Pessoa Resp Aut', 'Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Valor a Cobrar', 'Classific. Atendimento']
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"❌ O combo de planilhas está faltando colunas essenciais: {colunas_faltantes}.")
        else:
            for c in ['Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Nr. Matricula', 'Pessoa Resp Aut', 'Classific. Atendimento']:
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
            
            # --- PROCESSAMENTO SETORES ---
            df_s_consolidado = None
            setores_agrupados = None
            
            if arquivos_setores:
                try:
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
                    df_s_consolidado['Nº Atendimento'] = df_s_consolidado['Nº Atendimento'].astype(str).str.strip()
                    df_s_consolidado['Grupo Especialidade'] = df_s_consolidado['Grupo Especialidade'].fillna('Outros').astype(str).str.strip()
                    
                    setores_agrupados = df_s_consolidado.groupby('Nº Atendimento')['Grupo Especialidade'].apply(
                        lambda x: ', '.join(sorted(set(x)))
                    ).reset_index()
                    setores_agrupados.columns = ['Nr. Atendimento', 'Especialidades Pendentes']
                except Exception as e_setor:
                    st.warning(f"⚠️ Erro ao cruzar arquivo de setores: {e_setor}")

            if setores_agrupados is not None:
                df = pd.merge(df, setores_agrupados, on='Nr. Atendimento', how='left')
                df['Especialidades Pendentes'] = df['Especialidades Pendentes'].fillna('Nenhuma pendência técnica apontada')
            else:
                df['Especialidades Pendentes'] = 'Aguardando planilha de setores técnica...'

            guia_valida_numerica = df['Nº Guia Solicitação (TISS)'].str.isnumeric()
            df['Inserido_Amil'] = (guia_valida_numerica) | (df['Senha Aprovação'] != '') | (df['Status Aut Orç'] == 'Autorizado')
            
            total_pacientes = len(df)
            inseridos = df['Inserido_Amil'].sum()
            faltam = total_pacientes - inseridos
            
            df_prontuario = df[df['Status Aut Orç'] == 'Prontuário Pendente'].sort_values(by='Valor a Cobrar', ascending=False)
            df_ops = df[df['Status Aut Orç'] == 'OPS Pendente'].sort_values(by='Valor a Cobrar', ascending=False)
            
            pacientes_com_erro = df[(df['Nr. Matricula'].str.len() == 0) | (df['Nr. Atendimento'].isna())]

            # --- RENDERIZAÇÃO DAS ABAS ---
            aba1, aba2, aba3, aba4, aba5 = st.tabs(["⭐ Resumo Geral", "👤 Gestão de Equipe", "🏥 Segmentação ID / AD", "📋 Listas de Prorrogação", "🚨 Alertas de Erro"])
            
            with aba1:
                st.markdown("### 📌 Indicadores Operacionais")
                card1, card2, card3, card4 = st.columns(4)
                card1.metric("Total de Processos (Linhas)", f"{total_pacientes}")
                card2.metric("✅ Inseridos no Portal", f"{inseridos}")
                card3.metric("⏳ Pendentes Total", f"{faltam}")
                card4.metric("🚨 Erros de Cadastro", f"{len(pacientes_com_erro)}")
                
                if df_s_consolidado is not None:
                    st.markdown("---")
                    st.markdown("### 🏢 Pendências de Relatório por Setor Multidisciplinar")
                    df_amil_v = df[['Nr. Atendimento', 'Valor a Cobrar']].copy()
                    df_setores_valores = pd.merge(df_s_consolidado, df_amil_v, left_on='Nº Atendimento', right_on='Nr. Atendimento', how='left')
                    
                    analise_setores = df_setores_valores.groupby('Grupo Especialidade').agg(
                        Quantidade=('ID Pront.', 'count'),
                        Valor_Total=('Valor a Cobrar', 'sum')
                    ).reset_index()
                    
                    set_col1, set_col2 = st.columns(2)
                    with set_col1:
                        st.write("**Quantidade de Relatórios Pendentes por Setor**")
                        st.bar_chart(analise_setores, x='Grupo Especialidade', y='Quantidade', color='#5C1220')
                    with set_col2:
                        st.write("**Impacto Financeiro Bloqueado por Setor (R$)**")
                        st.bar_chart(analise_setores, x='Grupo Especialidade', y='Valor_Total', color='#C07C20')

            # --- ABA 2: EQUIPE (CORRIGIDA) ---
            with aba2:
                st.markdown("### 👤 Produtividade e Carga Operacional")
                st.write("Análise puramente física do volume de pacientes **únicos** e inputs no portal.")
                
                col_responsavel = 'Pessoa Resp Aut'
                col_paciente = 'Nome do Paciente'
                
                # Conta total de inputs brutos por funcionário
                df_inputs = df.groupby(col_responsavel)['Inserido_Amil'].sum().reset_index()
                df_inputs.columns = [col_responsavel, 'Total de Inputs Realizados']
                
                # Remove pacientes repetidos para aquele colaborador
                df_unicos = df.drop_duplicates(subset=[col_responsavel, col_paciente]).copy()
                df_unicos['Qtd_ID'] = df_unicos['Tipo_Atendimento'] == 'ID (Internação Domiciliar)'
                df_unicos['Qtd_AD'] = df_unicos['Tipo_Atendimento'] == 'AD (Atenção Domiciliar)'
                
                prod_colab = df_unicos.groupby(col_responsavel).agg(
                    Pacientes_ID=('Qtd_ID', 'sum'),
                    Pacientes_AD=('Qtd_AD', 'sum'),
                    Total_Pacientes=(col_paciente, 'count')
                ).reset_index()
                prod_colab.columns = [col_responsavel, 'Nº Pacientes ID', 'Nº Pacientes AD', 'Quantitativo Total Pacientes']
                
                resumo_equipe = pd.merge(prod_colab, df_inputs, on=col_responsavel)
                
                st.dataframe(resumo_equipe.style.format({
                    'Nº Pacientes ID': '{:,.0f}',
                    'Nº Pacientes AD': '{:,.0f}',
                    'Quantitativo Total Pacientes': '{:,.0f}',
                    'Total de Inputs Realizados': '{:,.0f}'
                }), use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("#### 📊 Volume de Pacientes Únicos por Funcionário")
                
                df_graf_equipe = df_unicos[df_unicos['Tipo_Atendimento'].isin(['ID (Internação Domiciliar)', 'AD (Atenção Domiciliar)'])].groupby(
                    [col_responsavel, 'Tipo_Atendimento']
                ).size().reset_index(name='Qtd')
                
                df_graf_equipe['Tipo'] = df_graf_equipe['Tipo_Atendimento'].apply(lambda x: 'ID' if 'ID' in x else 'AD')
                
                fig_carga = px.bar(
                    df_graf_equipe,
                    x=col_responsavel,
                    y='Qtd',
                    color='Tipo',
                    labels={col_responsavel: 'Colaborador', 'Qtd': 'Nº de Pacientes Físicos', 'Tipo': 'Classificação'},
                    barmode='stack',
                    color_discrete_map={'ID': '#5C1220', 'AD': '#C07C20'}
                )
                st.plotly_chart(fig_carga, use_container_width=True)

            with aba3:
                st.markdown("### 🏥 Análise do Modelo de Atendimento Solar (ID vs AD)")
                df_id_ad = df.groupby('Tipo_Atendimento').agg(
                    Quantidade=('Nome do Paciente', 'count'),
                    Valor_Total=('Valor a Cobrar', 'sum')
                ).reset_index()
                
                id_col1, id_col2 = st.columns(2)
                with id_col1:
                    st.bar_chart(df_id_ad, x='Tipo_Atendimento', y='Quantidade', color='#5C1220')
                with id_col2:
                    st.bar_chart(df_id_ad, x='Tipo_Atendimento', y='Valor_Total', color='#C07C20')

            with aba4:
                st.markdown("### 📋 Prorrogações Ordenadas pelos Maiores Valores")
                tab_p, tab_o = st.tabs(["📄 Prontuário Pendente", "🏢 OPS Pendente"])
                with tab_p:
                    df_p_view = df_prontuario[['Nr. Atendimento', 'Nome do Paciente', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                    df_p_view.columns = ['Nº Atendimento', 'Nome do Paciente', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor a Cobrar (R$)']
                    st.dataframe(df_p_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                with tab_o:
                    df_o_view = df_ops[['Nr. Atendimento', 'Nome do Paciente', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                    df_o_view.columns = ['Nº Atendimento', 'Nome do Paciente', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor a Cobrar (R$)']
                    st.dataframe(df_o_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

            with aba5:
                st.markdown("### 🚨 Cadastros Incompletos / Erros no IW")
                st.dataframe(pacientes_com_erro[['Nr. Atendimento', 'Nome do Paciente', 'Nr. Matricula', 'Pessoa Resp Aut']], use_container_width=True, hide_index=True)
                    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Selecione um ou mais arquivos do IW acima para ativar o painel com o layout institucional...")
