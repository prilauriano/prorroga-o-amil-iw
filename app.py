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

# --- ÁREA DE UPLOAD (NOMES ATUALIZADOS) ---
col_up1, col_up2, col_up3 = st.columns(3)
with col_up1:
    arquivos_amil = st.file_uploader("1 - PLANILHA PRORROGAÇÃO (.csv/.xlsx)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up2:
    arquivos_setores = st.file_uploader("2 - RELATÓRIOS DAS ESPECILIDADES (.csv/.xlsx)", type=["csv", "xlsx"], accept_multiple_files=True)
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
        
        # Identificação dinâmica das colunas secundárias
        col_justificativa = next((col for col in df.columns if 'justificativa' in col.lower() or 'pendencia' in col.lower()), None)
        col_status_rel = next((col for col in df.columns if 'status rel' in col.lower() or 'rel orç' in col.lower() or 'status_rel' in col.lower()), None)
        
        # Mapeando e limpando campos principais
        campos_obrigatorios = ['Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Nr. Matricula', 'Pessoa Resp Aut', 'Classific. Atendimento', 'Nome do Paciente', 'ID Orçam.']
        if col_justificativa: campos_obrigatorios.append(col_justificativa)
        if col_status_rel: campos_obrigatorios.append(col_status_rel)
            
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
        df['Tipo_Atendimento'] = df['Classific. Atendimento'].apply(
            lambda x: 'ID (Internação Domiciliar)' if x.startswith('ID') else ('AD (Atenção Domiciliar)' if x.startswith('AD') else 'Outros')
        )

        guia_valida_numerica = df['Nº Guia Solicitação (TISS)'].str.isnumeric()
        df['Inserido_Amil'] = (guia_valida_numerica) | (df['Senha Aprovação'] != '') | (df['Status Aut Orç'] == 'Autorizado')

        # --- NOVA REGRA COMPLETA DE ENTENDIMENTO DE IMPUTS DO ROBÔ E MANUAL ---
        def analisar_tipo_input(linha):
            has_guia = str(linha['Nº Guia Solicitação (TISS)']).isnumeric()
            status_aut = str(linha['Status Aut Orç']).strip().lower()
            
            just_txt = ""
            if col_justificativa:
                just_txt = str(linha[col_justificativa]).strip().lower()
            
            # Condição 1: Inputado por Robô
            if has_guia and status_aut == "em análise" and "operadora: robô em analise" in just_txt:
                return "Robô"
            # Condição 2: Inputado Manualmente
            elif has_guia and status_aut == "em análise" and "operadora: manual em analise" in just_txt:
                return "Manual"
            return "Outro"

        df['Origem_Input_Calculado'] = df.apply(analisar_tipo_input, axis=1)

        # Regra retroativa para o Robo Tradicional da Fila Técnica (Caso existam flags antigas)
        def verificar_flag_robo_geral(linha):
            if linha['Origem_Input_Calculado'] == "Robô":
                return True
            status_aut = str(linha['Status Aut Orç']).lower()
            condicao_status = ('lib.' in status_aut and 'robô' in status_aut) or ('robô' in status_aut or 'robo' in status_aut)
            condicao_resp = any(r in str(linha['Pessoa Resp Aut']).lower() for r in ['robô', 'robo', 'robot'])
            return condicao_status or condicao_resp

        df['É_Robo'] = df.apply(verificar_flag_robo_geral, axis=1)

        # --- FILTRO EXATO DE ERRO: ARQUIVO NÃO ENCONTRADO ---
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
                df_s_consolidado['Valor do Item'] = df_s_consolidado.get('Valor do Item', 0.0)
                if df_s_consolidado['Valor do Item'].dtype == object:
                    df_s_consolidado['Valor do Item'] = df_s_consolidado['Valor do Item'].apply(converter_moeda_br)
                
                # Regra de exclusão da TO ativa
                def filtrar_prevalencia_to(linha):
                    if 'to' in str(linha['Grupo Especialidade']).lower() or 'terapia ocupacional' in str(linha['Grupo Especialidade']).lower():
                        if linha['Nº Atendimento'] in atendimentos_resolvidos_to:
                            return False
                    return True
                
                df_s_consolidado = df_s_consolidado[df_s_consolidado.apply(filtrar_prevalencia_to, axis=1)]
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

        df['Tem_Pendencia_Setor'] = df['Nr. Atendimento'].isin(atendimentos_pendentes_setores) & (~df['É_Robo'])

        # IDENTIFICAÇÃO DO CONTRATO RIOHOME
        df['É_RioHome'] = df.astype(str).apply(
            lambda row: row.str.lower().str.contains('riohome|rio home|rio_home', regex=True).any(), 
            axis=1
        )

        # Divisão estruturada das tabelas
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

        # Indicadores globais (Valor Represado Mantido!)
        total_pacientes_iw = len(df)
        inseridos = df_producao_limpa['Inserido_Amil'].sum()
        valor_total_pendente = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Inserido_Amil'] == False]['Valor a Cobrar'].sum()

        # --- ABAS DO DASHBOARD ---
        aba1, aba2, aba3, aba4, aba5, aba_r, aba6, aba7 = st.tabs([
            "⭐ Resumo Geral", 
            "👤 Gestão de Equipe", 
            "🏥 Segmentação ID / AD", 
            "📋 Lista de Pendências",
            "🚀 Liberados para Input",
            "🤖 Liberados para o Robô",
            "🏠 Contrato RioHome (Manual)", 
            "🚨 Alertas de Erro"
        ])
        
        with aba1:
            st.markdown("### 📌 Indicadores Operacionais e Financeiros (Exceto RioHome)")
            card1, card2, card3, card4, card5 = st.columns(5)
            card1.metric("Total Base Bruta IW", f"{total_pacientes_iw}")
            card2.metric("✅ Inseridos", f"{inseridos}")
            card3.metric("⏳ Pendentes Operação", f"{len(df_prontuario) + len(df_ops)}")
            card4.metric("🤖 Fila do Robô", f"{len(df_fila_robo)}")
            card5.metric("💰 Represado Total", f"R$ {valor_total_pendente:,.2f}")
            
            if len(df_base_erros) > 0:
                st.warning(f"⚠️ Atenção: Detectamos {len(df_base_erros)} arquivos não encontrados cadastrados.")

        with aba2:
            st.markdown("### 👤 Carga Operacional e Rastreabilidade de Inputs (Robô vs Manual)")
            
            col_responsavel = 'Pessoa Resp Aut'
            col_paciente = 'Nome do Paciente'
            
            # Criando métricas agrupadas por Pessoa Responsável (Contabilizando a ação do robô para quem programou)
            df_unicos = df_producao_limpa.drop_duplicates(subset=[col_responsavel, col_paciente]).copy()
            df_unicos['Qtd_ID'] = df_unicos['Tipo_Atendimento'] == 'ID (Internação Domiciliar)'
            df_unicos['Qtd_AD'] = df_unicos['Tipo_Atendimento'] == 'AD (Atenção Domiciliar)'
            
            # Quantificações por método de input associado ao analista
            df_unicos['Robo_Rodado'] = df_unicos['Origem_Input_Calculado'] == "Robô"
            df_unicos['Manual_Rodado'] = df_unicos['Origem_Input_Calculado'] == "Manual"
            
            prod_colab = df_unicos.groupby(col_responsavel).agg(
                Pacientes_ID=('Qtd_ID', 'sum'), 
                Pacientes_AD=('Qtd_AD', 'sum'),
                Inputs_pelo_Robo=('Robo_Rodado', 'sum'),
                Inputs_Manuais=('Manual_Rodado', 'sum'),
                Total_Geral_Pacientes=(col_paciente, 'count')
            ).reset_index()
            
            prod_colab.columns = ['Colaborador (Responsável)', 'Nº Pacientes ID', 'Nº Pacientes AD', 'Inputs Concluídos p/ Robô', 'Inputs Concluídos Manuais', 'Quantitativo Total de Pacientes']
            st.dataframe(prod_colab, use_container_width=True, hide_index=True)

        with aba3:
            st.markdown("### 🏥 Análise do Modelo de Atendimento Solar (ID vs AD)")
            df_id_ad = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Inserido_Amil'] == False].groupby('Tipo_Atendimento').agg(Quantidade=('Nome do Paciente', 'count'), Valor_Total=('Valor a Cobrar', 'sum')).reset_index()
            st.dataframe(df_id_ad.style.format({'Valor_Total': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba4:
            st.markdown("### 📋 Lista de Pendências Ordenadas pelos Maiores Valores")
            
            # 🔥 EXIBIÇÃO LADO A LADO DOS DOIS GRÁFICOS (QUANTIDADE VS VALOR FINANCEIRO)
            if not df_s_consolidado.empty and 'Grupo Especialidade' in df_s_consolidado.columns:
                g_col1, g_col2 = st.columns(2)
                
                with g_col1:
                    st.markdown("#### 📊 Distribuição de Pendências Técnicas (Quantidade)")
                    contagem_setores = df_s_consolidado['Grupo Especialidade'].value_counts().reset_index()
                    contagem_setores.columns = ['Setor/Especialidade', 'Volume de Pendências']
                    fig_setores = px.bar(contagem_setores, x='Setor/Especialidade', y='Volume de Pendências', 
                                         color='Volume de Pendências', color_continuous_scale='Reds', text_auto=True)
                    fig_setores.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_setores, use_container_width=True)
                
                with g_col2:
                    st.markdown("#### 💰 Impacto Financeiro Represado por Setor (Valores)")
                    financeiro_setores = df_s_consolidado.groupby('Grupo Especialidade')['Valor do Item'].sum().reset_index()
                    financeiro_setores.columns = ['Setor/Especialidade', 'Valor Represado (R$)']
                    financeiro_setores = financeiro_setores.sort_values(by='Valor Represado (R$)', ascending=False)
                    fig_valores = px.bar(financeiro_setores, x='Setor/Especialidade', y='Valor Represado (R$)', 
                                         color='Valor Represado (R$)', color_continuous_scale='Oryel', text_auto='.2s')
                    fig_valores.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_valores, use_container_width=True)
                
            tab_p, tab_o = st.tabs(["📄 Prontuário Pendente", "🏢 OPS Pendente (Operação)"])
            
            with tab_p:
                st.markdown(f"**Total de Processos: {len(df_prontuario)} | Montante: R$ {df_prontuario['Valor a Cobrar'].sum():,.2f}**")
                
                # 🔥 MODIFICAÇÃO: Nº ATENDIMENTO DO LADO DO ID ORÇAM.
                df_p_view = df_prontuario[['Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_p_view.columns = ['Paciente', 'Nº Atendimento', 'ID Orçamento', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor a Cobrar (R$)']
                
                buffer_p = io.BytesIO()
                with pd.ExcelWriter(buffer_p, engine='xlsxwriter') as writer:
                    df_p_view.to_excel(writer, sheet_name='Prontuário Pendente', index=False)
                    workbook  = writer.book
                    worksheet = writer.sheets['Prontuário Pendente']
                    format_money = workbook.add_format({'num_format': 'R$ #,##0.00'})
                    worksheet.set_column('G:G', 18, format_money)
                    worksheet.set_column('A:F', 22)
                
                st.download_button(
                    label="📥 Baixar Planilha Estruturada: Prontuário Pendente",
                    data=buffer_p.getvalue(),
                    file_name="prontuario_pendente_estruturado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.markdown("---")
                st.dataframe(df_p_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                
            with tab_o:
                st.markdown(f"**Total de Processos: {len(df_ops)} | Montante: R$ {df_ops['Valor a Cobrar'].sum():,.2f}**")
                
                # 🔥 MODIFICAÇÃO: Nº ATENDIMENTO DO LADO DO ID ORÇAM.
                df_o_view = df_ops[['Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_o_view.columns = ['Paciente', 'Nº Atendimento', 'ID Orçamento', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor a Cobrar (R$)']
                
                buffer_o = io.BytesIO()
                with pd.ExcelWriter(buffer_o, engine='xlsxwriter') as writer:
                    df_o_view.to_excel(writer, sheet_name='OPS Pendente', index=False)
                    workbook  = writer.book
                    worksheet = writer.sheets['OPS Pendente']
                    format_money = workbook.add_format({'num_format': 'R$ #,##0.00'})
                    worksheet.set_column('G:G', 18, format_money)
                    worksheet.set_column('A:F', 22)
                
                st.download_button(
                    label="📥 Baixar Planilha Estruturada: Pendências da Operação",
                    data=buffer_o.getvalue(),
                    file_name="ops_pendente_estruturado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.markdown("---")
                st.dataframe(df_o_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba5:
            st.markdown("### 🚀 Pacientes Liberados (Sem Pendências nos Setores)")
            if not arquivos_setores:
                st.warning("⚠️ Para ver quem está liberado, carregue a planilha de Setores no campo de upload.")
            else:
                st.markdown(f"**🔥 Total Prontos para Input: {len(df_liberados)} | Valor de Giro Rápido: R$ {df_liberados['Valor a Cobrar'].sum():,.2f}**")
                
                # 🔥 MODIFICAÇÃO: Nº ATENDIMENTO DO LADO DO ID ORÇAM.
                df_liberados_clean_excel = df_liberados[['Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Tipo_Atendimento', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_liberados_clean_excel.columns = ['Paciente', 'Nº Atendimento', 'ID Orçamento', 'Tipo Atendimento', 'Responsável', 'Valor a Cobrar (R$)']
                st.dataframe(df_liberados_clean_excel.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba_r:
            st.markdown("### 🤖 Fila de Pacientes Encaminhados para Input Automatizado")
            st.markdown(f"**Volumetria Atual do Robô: {len(df_fila_robo)} pacientes na fila.**")
            if len(df_fila_robo) > 0:
                
                # 🔥 MODIFICAÇÃO: Nº ATENDIMENTO DO LADO DO ID ORÇAM.
                df_robo_view = df_fila_robo[['Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Tipo_Atendimento', 'Status Aut Orç', 'Valor a Cobrar']].copy()
                df_robo_view.columns = ['Paciente', 'Nº Atendimento', 'ID Orçamento', 'Tipo', 'Status Atual', 'Valor a Cobrar (R$)']
                st.dataframe(df_robo_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
            else:
                st.info("💡 Nenhum paciente aguardando ou liberado para o robô detectado.")

        with aba6:
            st.markdown("### 🏠 Listagem Isolada — Contrato RioHome")
            
            # 🔥 MODIFICAÇÃO: Nº ATENDIMENTO DO LADO DO ID ORÇAM.
            df_riohome_view = df_riohome[['Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Tipo_Atendimento', 'Pessoa Resp Aut', 'Status Aut Orç', 'Valor a Cobrar']].copy()
            df_riohome_view.columns = ['Paciente', 'Nº Atendimento', 'ID Orçamento', 'Tipo', 'Responsável', 'Status Atual IW', 'Valor a Cobrar (R$)']
            st.dataframe(df_riohome_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba7:
            st.markdown("### 🚨 Alertas de Erro: Arquivo Não Encontrado")
            st.markdown("Registros mapeados cujo preenchimento no campo de status de relatório acusa impossibilidade de leitura.")
            
            if len(df_base_erros) > 0:
                # 🔥 MODIFICAÇÃO: Nº ATENDIMENTO DO LADO DO ID ORÇAM.
                colunas_erro = ['Nome do Paciente', 'Nr. Atendimento', 'Status Aut Orç', 'Pessoa Resp Aut']
                if col_status_rel: colunas_erro.insert(2, col_status_rel)
                
                df_erro_print = df_base_erros[colunas_erro].copy()
                colunas_visualizacao = ['Paciente', 'Nº Atendimento', 'Status Aut Orç', 'Responsável']
                if col_status_rel: colunas_visualizacao.insert(2, 'Texto Capturado no Campo')
                
                df_erro_print.columns = colunas_visualizacao
                st.dataframe(df_erro_print, use_container_width=True, hide_index=True)
            else:
                st.success("✨ Excelente! Nenhum erro de 'Arquivo Não Encontrado' foi detectado.")
                    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Selecione os arquivos acima nos novos campos estruturados para carregar o cruzamento dinâmico.")
