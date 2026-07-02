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
st.markdown('<p class="subtitle">Módulo operacional integrado de auditoria Amil IW, monitoramento de prazos, volumetria ID/AD e controle de robô.</p>', unsafe_allow_html=True)

# --- ÁREA DE UPLOAD ---
col_up1, col_up2, col_up3 = st.columns(3)
with col_up1:
    arquivos_amil = st.file_uploader("1 - PRORROGAÇÃO (.csv/.xlsx)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up2:
    arquivos_setores = st.file_uploader("2 - RELATÓRIOS DAS ESPECIALIDADES (.csv/.xlsx)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up3:
    arquivos_to = st.file_uploader("3 - PACIENTES TO COM EVOLUÇÃO (.csv/.xlsx)", type=["csv", "xlsx"], accept_multiple_files=True)

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
        
        # Identificação de colunas secundárias e do Contrato
        col_justificativa = next((col for col in df.columns if 'justificativa' in col.lower() or 'pendencia' in col.lower()), None)
        col_status_rel = next((col for col in df.columns if 'status rel' in col.lower() or 'rel orç' in col.lower() or 'status_rel' in col.lower()), None)
        col_contrato = next((col for col in df.columns if str(col).strip().lower() == 'contrato'), None)
        
        # Mapeando e limpando campos principais
        campos_obrigatorios = ['Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Nr. Matricula', 'Pessoa Resp Aut', 'Classific. Atendimento', 'Nome do Paciente', 'ID Orçam.']
        if col_justificativa: campos_obrigatorios.append(col_justificativa)
        if col_status_rel: campos_obrigatorios.append(col_status_rel)
        if col_contrato: campos_obrigatorios.append(col_contrato)
            
        for c in campos_obrigatorios:
            if c in df.columns:
                df[c] = df[c].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            elif c == 'ID Orçam.':
                df['ID Orçam.'] = ''
        
        df['Nr. Atendimento'] = df['Nr. Atendimento'].fillna('').astype(str).str.strip()
        
        def converter_moeda_br(valor):
            valor_str = str(valor).strip()
            if not valor_str or valor_str.lower() == 'nan': return 0.0
            if re.search(r',\d{2}$', valor_str): valor_str = valor_str.replace('.', '').replace(',', '.')
            else: valor_str = valor_str.replace('.', '').replace(',', '.')
            try: return float(valor_str)
            except: return 0.0

        df['Valor a Cobrar'] = df['Valor a Cobrar'].apply(converter_moeda_br)
        
        # CLASSIFIC. ATENDIMENTO: Separação estrita de AD e ID
        df['Tipo_Atendimento'] = df['Classific. Atendimento'].apply(
            lambda x: 'ID (Internação Domiciliar)' if str(x).strip().upper().startswith('ID') else ('AD (Atenção Domiciliar)' if str(x).strip().upper().startswith('AD') else 'Outros')
        )

        # NOVO CRITÉRIO EXATO DOS INSERIDOS: Somente quem possui número na Guia TISS
        df['Inserido_Amil'] = df['Nº Guia Solicitação (TISS)'].str.isnumeric()

        # Input inteligente (Robô vs Manual)
        def analisar_tipo_input(linha):
            has_guia = str(linha['Nº Guia Solicitação (TISS)']).isnumeric()
            status_aut = str(linha['Status Aut Orç']).strip().lower()
            just_txt = str(linha[col_justificativa]).strip().lower() if col_justificativa else ""
            just_txt = re.sub(r'\s+', ' ', just_txt).replace('ê', 'e').replace('â', 'a')
            
            if has_guia and (status_aut == "em analise" or status_aut == "em análise"):
                if "operadora: robo em analise" in just_txt or "robo em analise" in just_txt:
                    return "Robô"
                elif "operadora: manual em analise" in just_txt or "manual em analise" in just_txt:
                    return "Manual"
            return "Outro"

        df['Origem_Input_Calculado'] = df.apply(analisar_tipo_input, axis=1)

        # FILA DO ROBÔ EXATA
        def verificar_flag_robo_exata(linha):
            just_txt = str(linha[col_justificativa]).strip() if col_justificativa else ""
            status_aut = str(linha['Status Aut Orç']).strip()
            
            cond_just = "Robô aguardando input" in just_txt or "Robo aguardando input" in just_txt
            cond_stat = "Lib. para o Robô input" in status_aut or "Lib. para o Robo input" in status_aut
            
            return cond_just and cond_stat

        df['É_Robo'] = df.apply(verificar_flag_robo_exata, axis=1)

        # Filtro de erro
        def avaliar_erros_arquivo_nao_encontrado(linha):
            if col_status_rel:
                valor_rel = str(linha[col_status_rel]).strip().lower()
                if "arquivo não encontrado" in valor_rel or "arquivo nao encontrado" in valor_rel:
                    return "Arquivo Não Encontrado"
            return "Sem Erros"

        df['Inconsistencia_Erro'] = df.apply(avaliar_erros_arquivo_nao_encontrado, axis=1)
        df['Possui_Erro_Critico'] = df['Inconsistencia_Erro'] == "Arquivo Não Encontrado"

        # --- 📑 LEITURA DA PLANILHA DE TO (PREVALÊNCIA) ---
        atendimentos_resolvidos_to = set()
        if arquivos_to:
            for arq_to in arquivos_to:
                if arq_to.name.endswith('.csv'):
                    try: df_to_temp = pd.read_csv(arq_to, sep=';', encoding='utf-8')
                    except: 
                        arq_to.seek(0)
                        df_to_temp = pd.read_csv(arq_to, sep=';', encoding='iso-8859-1')
                else:
                    df_to_temp = pd.read_excel(arq_to)
                
                df_to_temp.columns = df_to_temp.columns.str.strip()
                col_atend_to = next((col for col in df_to_temp.columns if 'atendimento' in col.lower() or 'nr.' in col.lower() or 'nº' in col.lower()), None)
                if col_atend_to:
                    atendimentos_resolvidos_to.update(df_to_temp[col_atend_to].dropna().astype(str).str.strip().unique())

        # --- ⚙️ PROCESSAMENTO DOS SETORES (RETIRANDO TO RESOLVIDO) ---
        atendimentos_pendentes_setores = set()
        df_s_consolidado = pd.DataFrame()
        setores_agrupados = None
        valor_total_pendencias_setores = 0.0
        
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
                
                col_valor_item = next((col for col in df_s_consolidado.columns if 'valor' in col.lower() or 'item' in col.lower() or 'cobrar' in col.lower()), None)
                if col_valor_item:
                    df_s_consolidado['Valor_Calculado_Setor'] = df_s_consolidado[col_valor_item].apply(converter_moeda_br)
                else:
                    df_s_consolidado['Valor_Calculado_Setor'] = 0.0
                
                def filtrar_prevalencia_to(linha):
                    if 'to' in str(linha['Grupo Especialidade']).lower() or 'terapia ocupacional' in str(linha['Grupo Especialidade']).lower():
                        if linha['Nº Atendimento'] in atendimentos_resolvidos_to:
                            return False
                    return True
                
                df_s_consolidado = df_s_consolidado[df_s_consolidado.apply(filtrar_prevalencia_to, axis=1)]
                atendimentos_pendentes_setores = set(df_s_consolidado['Nº Atendimento'].unique())
                
                valor_total_pendencias_setores = df_s_consolidado['Valor_Calculado_Setor'].sum()
                
                setores_agrupados = df_s_consolidado.groupby('Nº Atendimento')['Grupo Especialidade'].apply(
                    lambda x: ', '.join(sorted(set(x)))
                ).reset_index()
                setores_agrupados.columns = ['Nr. Atendimento', 'Especialidades Pendentes']

        if setores_agrupados is not None:
            df = pd.merge(df, setores_agrupados, on='Nr. Atendimento', how='left')
            df['Especialidades Pendentes'] = df['Especialidades Pendentes'].fillna('Nenhuma pendência técnica apontada')
        else:
            df['Especialidades Pendentes'] = 'Aguardando planilha de setores técnica...'

        df['Tem_Pendencia_Setor'] = df['Nr. Atendimento'].isin(atendimentos_pendentes_setores) & (~df['É_Robo'])

        # 🔥 CONSERTO SEGURO: Identificação do Contrato RioHome utilizando a coluna de Contrato mapeada
        if col_contrato:
            df['É_RioHome'] = df[col_contrato].str.lower().str.contains('riohome|rio home|rio_home', regex=True).fillna(False)
        else:
            df['É_RioHome'] = False

        # Separação das bases secundárias
        df_base_erros = df[df['Possui_Erro_Critico'] == True].copy()
        df_producao_limpa = df[df['Possui_Erro_Critico'] == False].copy()

        df_riohome = df_producao_limpa[df_producao_limpa['É_RioHome'] == True].copy()
        df_faturamento_geral = df_producao_limpa[df_producao_limpa['É_RioHome'] == False].copy()

        df_fila_robo = df_faturamento_geral[df_faturamento_geral['É_Robo'] == True].copy()
        df_faturamento_geral_sem_robo = df_faturamento_geral[df_faturamento_geral['É_Robo'] == False].copy()

        df_liberados = df_faturamento_geral_sem_robo[(df_faturamento_geral_sem_robo['Inserido_Amil'] == False) & (df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == False)].copy()
        df_liberados = df_liberados.sort_values(by='Valor a Cobrar', ascending=False)

        df_prontuario = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Status Aut Orç'] == 'Prontuário Pendente'].sort_values(by='Valor a Cobrar', ascending=False)
        df_ops = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Status Aut Orç'] == 'OPS Pendente'].sort_values(by='Valor a Cobrar', ascending=False)

        # Métricas globais
        total_pacientes_iw = len(df)
        inseridos_count = df_producao_limpa['Inserido_Amil'].sum()
        valor_total_todos_pacientes = df['Valor a Cobrar'].sum()

        # --- ABAS DO DASHBOARD ---
        aba1, aba2, aba3, aba4, aba5, aba_r, aba6, aba7 = st.tabs([
            "☀️ Resumo Geral", 
            "👤 Gestão de Equipe", 
            "🏥 Segmentação ID / AD", 
            "📋 Lista de Pendências",
            "🚀 Liberados para Input",
            "🤖 Liberados para o Robô",
            "🏠 Contrato RioHome (Manual)", 
            "🚨 Alertas de Erro"
        ])
        
        with aba1:
            st.markdown("### 📌 Indicadores Operacionais e Financeiros Estruturados")
            card1, card2, card3, card4, card5 = st.columns(5)
            
            card1.metric("Total Base Bruta IW", f"{total_pacientes_iw}")
            card2.metric("✅ Inseridos (Com Guia TISS)", f"{inseridos_count}")
            card3.metric("🤖 Fila do Robô (Filtro Exato)", f"{len(df_fila_robo)}")
            card4.metric("💰 Valor Total de Pacientes", f"R$ {valor_total_todos_pacientes:,.2f}")
            card5.metric("⚠️ Valor Total das Pendências", f"R$ {valor_total_pendencias_setores:,.2f}")
            
            if len(df_base_erros) > 0:
                st.warning(f"⚠️ Atenção: Detectamos {len(df_base_erros)} arquivos não encontrados cadastrados.")

        with aba2:
            st.markdown("### 👤 Carga Operacional e Rastreabilidade de Inputs (Robô vs Manual)")
            
            col_responsavel = 'Pessoa Resp Aut'
            
            df_producao_limpa['Qtd_ID'] = df_producao_limpa['Tipo_Atendimento'] == 'ID (Internação Domiciliar)'
            df_producao_limpa['Qtd_AD'] = df_producao_limpa['Tipo_Atendimento'] == 'AD (Atenção Domiciliar)'
            df_producao_limpa['Robo_Rodado'] = df_producao_limpa['Origem_Input_Calculado'] == "Robô"
            df_producao_limpa['Manual_Rodado'] = df_producao_limpa['Origem_Input_Calculado'] == "Manual"
            
            prod_colab = df_producao_limpa.groupby(col_responsavel).agg(
                Pacientes_ID=('Qtd_ID', 'sum'), 
                Pacientes_AD=('Qtd_AD', 'sum'),
                Inputs_pelo_Robo=('Robo_Rodado', 'sum'),
                Inputs_Manuais=('Manual_Rodado', 'sum'),
                Valor_Total_Analista=('Valor a Cobrar', 'sum'),
                Total_Geral_Pacientes=('Nome do Paciente', 'count')
            ).reset_index()
            
            prod_colab.columns = ['Colaborador (Responsável)', 'Nº Pacientes ID', 'Nº Pacientes AD', 'Inputs Concluídos p/ Robô', 'Inputs Concluídos Manuais', 'Soma de Valores (R$)', 'Quantitativo Total de Linhas']
            st.dataframe(prod_colab.style.format({'Soma de Valores (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba3:
            st.markdown("### 🏥 Análise do Modelo de Atendimento Solar (ID vs AD)")
            df_id_ad = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Inserido_Amil'] == False].groupby('Tipo_Atendimento').agg(Quantidade=('Nome do Paciente', 'count'), Valor_Total=('Valor a Cobrar', 'sum')).reset_index()
            st.dataframe(df_id_ad.style.format({'Valor_Total': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba4:
            st.markdown("### 📋 Lista de Pendências Ordenadas pelos Maiores Valores")
            
            if not df_s_consolidado.empty and 'Grupo Especialidade' in df_s_consolidado.columns:
                st.markdown("#### 📊 Distribuição de Pendências Técnicas (Quantidade)")
                contagem_setores = df_s_consolidado['Grupo Especialidade'].value_counts().reset_index()
                contagem_setores.columns = ['Setor/Especialidade', 'Volume de Pendências']
                fig_setores = px.bar(contagem_setores, x='Setor/Especialidade', y='Volume de Pendências', 
                                     color='Volume de Pendências', color_continuous_scale='Reds', text_auto=True)
                fig_setores.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_setores, use_container_width=True)
                
                st.markdown("#### 💰 Impacto Financeiro Represado por Setor (Valores)")
                financeiro_setores = df_s_consolidado.groupby('Grupo Especialidade')['Valor_Calculado_Setor'].sum().reset_index()
                financeiro_setores.columns = ['Setor/Especialidade', 'Valor Represado (R$)']
                financeiro_setores = financeiro_setores.sort_values(by='Valor Represado (R$)', ascending=False)
                
                fig_valores = px.bar(financeiro_setores, x='Setor/Especialidade', y='Valor Represado (R$)', 
                                     color='Valor Represado (R$)', color_continuous_scale='Oryel', text_auto='.2s')
                fig_valores.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_valores, use_container_width=True)
                
            tab_p, tab_o = st.tabs(["📄 Prontuário Pendente", "🏢 OPS Pendente (Operação)"])
            
            with tab_p:
                st.markdown(f"**Total de Processos: {len(df_prontuario)} | Montante: R$ {df_prontuario['Valor a Cobrar'].sum():,.2f}**")
                df_p_view = df_prontuario[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_p_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor a Cobrar (R$)']
                
                buffer_p = io.BytesIO()
                with pd.ExcelWriter(buffer_p, engine='xlsxwriter') as writer:
                    df_p_view.to_excel(writer, sheet_name='Prontuário Pendente', index=False)
                st.download_button(label="📥 Baixar Planilha Estruturada: Prontuário Pendente", data=buffer_p.getvalue(), file_name="prontuario_pendente_estruturado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                st.markdown("---")
                st.dataframe(df_p_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                
            with tab_o:
                st.markdown(f"**Total de Processos: {len(df_ops)} | Montante: R$ {df_ops['Valor a Cobrar'].sum():,.2f}**")
                df_o_view = df_ops[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_o_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor a Cobrar (R$)']
                
                buffer_o = io.BytesIO()
                with pd.ExcelWriter(buffer_o, engine='xlsxwriter') as writer:
                    df_o_view.to_excel(writer, sheet_name='OPS Pendente', index=False)
                st.download_button(label="📥 Baixar Planilha Estruturada: Pendências da Operação", data=buffer_o.getvalue(), file_name="ops_pendente_estruturado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                st.markdown("---")
                st.dataframe(df_o_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba5:
            st.markdown("### 🚀 Pacientes Liberados (Sem Pendências nos Setores)")
            if not arquivos_setores:
                st.warning("⚠️ Para ver quem está liberado, carregue a planilha de Setores no campo de upload.")
            else:
                st.markdown(f"**🔥 Total Prontos para Input: {len(df_liberados)} | Valor de Giro Rápido: R$ {df_liberados['Valor a Cobrar'].sum():,.2f}**")
                df_liberados_clean_excel = df_liberados[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Tipo_Atendimento', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_liberados_clean_excel.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo Atendimento', 'Responsável', 'Valor a Cobrar (R$)']
                st.dataframe(df_liberados_clean_excel.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba_r:
            st.markdown("### 🤖 Fila de Pacientes Encaminhados para Input Automatizado")
            st.markdown(f"**Volumetria Atual do Robô: {len(df_fila_robo)} pacientes na fila.**")
            if len(df_fila_robo) > 0:
                df_robo_view = df_fila_robo[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Tipo_Atendimento', 'Status Aut Orç', 'Valor a Cobrar']].copy()
                df_robo_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo', 'Status Atual', 'Valor a Cobrar (R$)']
                st.dataframe(df_robo_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
            else:
                st.info("💡 Nenhum paciente aguardando ou liberado para o robô detectado.")

        with aba6:
            st.markdown("### 🏠 Listagem Isolada — Contrato RioHome")
            df_riohome_view = df_riohome[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Tipo_Atendimento', 'Pessoa Resp Aut', 'Status Aut Orç', 'Valor a Cobrar']].copy()
            df_riohome_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo', 'Responsável', 'Status Atual IW', 'Valor a Cobrar (R$)']
            st.dataframe(df_riohome_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba7:
            st.markdown("### 🚨 Alertas de Erro: Arquivo Não Encontrado")
            if len(df_base_erros) > 0:
                colunas_erro = ['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Status Aut Orç', 'Pessoa Resp Aut']
                if col_status_rel: colunas_erro.insert(3, col_status_rel)
                
                df_erro_print = df_base_erros[colunas_erro].copy()
                colunas_visualizacao = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Status Aut Orç', 'Responsável']
                if col_status_rel: colunas_visualizacao.insert(3, 'Texto Capturado no Campo')
                
                df_erro_print.columns = colunas_visualizacao
                st.dataframe(df_erro_print, use_container_width=True, hide_index=True)
            else:
                st.success("✨ Excelente! Nenhum erro de 'Arquivo Não Encontrado' foi detectado.")
                    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Selecione os arquivos acima nos novos campos estruturados para carregar o cruzamento dinâmico.")
