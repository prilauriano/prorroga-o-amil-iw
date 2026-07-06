import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. Configuração de página
st.set_page_config(page_title="Dashboard Prorrogações | Solar Cuidados", page_icon="☀️", layout="wide")

# 2. Paleta de Cores (Bordô, Dourado e Off-White)
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
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="topbar-header">
        <div class="brand-mark">☀️</div>
        <h1 class="brand-title">Solar Cuidados — <span>Prorrogações</span></h1>
    </div>
""", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Módulo operacional de auditoria Amil IW, controle de volumetria e alocação por paciente.</p>', unsafe_allow_html=True)

# --- ÁREA DE UPLOAD ---
col_up1, col_up2, col_up3 = st.columns(3)
with col_up1:
    arquivos_amil = st.file_uploader("1 - PLANILHA PRORROGAÇÃO (.csv/.xlsx)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up2:
    arquivos_setores = st.file_uploader("2 - RELATÓRIOS DAS ESPECILIDADES (Todas as Pendências)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up3:
    arquivos_to = st.file_uploader("3 - PACIENTES TO COM EVOLUÇÃO (Liberações de TO)", type=["csv", "xlsx"], accept_multiple_files=True)

if arquivos_amil:
    try:
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
        
        col_justificativa = next((col for col in df.columns if 'justificativa' in col.lower() or 'pendencia' in col.lower()), None)
        col_status_rel = next((col for col in df.columns if 'status rel' in col.lower() or 'rel orç' in col.lower() or 'status_rel' in col.lower()), None)
        col_contrato = next((col for col in df.columns if str(col).strip().lower() == 'contrato'), None)
        
        campos_obrigatorios = ['Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Nr. Matricula', 'Pessoa Resp Aut', 'Classific. Atendimento', 'Nome do Paciente', 'ID Orçam.']
        if col_justificativa: campos_obrigatorios.append(col_justificativa)
        if col_status_rel: campos_obrigatorios.append(col_status_rel)
        if col_contrato: campos_obrigatorios.append(col_contrato)
            
        for c in campos_obrigatorios:
            if c in df.columns:
                df[c] = df[c].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        df['Nr. Atendimento'] = df['Nr. Atendimento'].fillna('').astype(str).str.strip()
        
        # Tratamento de Moeda Robusto (Garante conversão limpa para Real)
        def converter_moeda_br(valor):
            if pd.isna(valor): return 0.0
            valor_str = str(valor).strip().upper().replace('R$', '').replace(' ', '')
            if not valor_str or valor_str in ['NAN', 'NULL', '']: return 0.0
            
            # Se tiver pontos e vírgula no padrão BR (ex: 1.650,00)
            if ',' in valor_str and '.' in valor_str:
                if valor_str.find('.') < valor_str.find(','):
                    valor_str = valor_str.replace('.', '').replace(',', '.')
            elif ',' in valor_str: 
                valor_str = valor_str.replace(',', '.')
                
            try: return float(valor_str)
            except: return 0.0

        df['Valor a Cobrar'] = df['Valor a Cobrar'].apply(converter_moeda_br)
        
        df['Is_ID'] = df['Classific. Atendimento'].str.upper().str.startswith('ID', na=False)
        df['Is_AD'] = df['Classific. Atendimento'].str.upper().str.startswith('AD', na=False)
        df['Tipo_Atendimento'] = df['Classific. Atendimento'].apply(
            lambda x: 'ID (Internação Domiciliar)' if str(x).strip().upper().startswith('ID') else ('AD (Atenção Domiciliar)' if str(x).strip().upper().startswith('AD') else 'Outros')
        )

        df['Inserido_Amil'] = df['Nº Guia Solicitação (TISS)'].str.isnumeric()

        # Correção do Robô na Gestão de Equipe (Busca Inteligente e Ampla)
        def verificar_origem_input(linha):
            just_txt = str(linha[col_justificativa]).strip().lower() if col_justificativa else ""
            if "operadora: robo" in just_txt or "operadora: robô" in just_txt or "robo - em analise" in just_txt:
                return "Robô"
            elif "operadora: manual" in just_txt:
                return "Manual"
            return "Outro"

        df['Origem_Input_Calculado'] = df.apply(verificar_origem_input, axis=1)

        def verificar_flag_robo_exata(linha):
            just_txt = str(linha[col_justificativa]).strip().lower() if col_justificativa else ""
            status_aut = str(linha['Status Aut Orç']).strip().lower()
            cond_just = "robô aguardando" in just_txt or "robo aguardando" in just_txt
            cond_stat = "lib. para o robô" in status_aut or "lib. para o robo" in status_aut
            return cond_just or cond_stat

        df['É_Robo'] = df.apply(verificar_flag_robo_exata, axis=1)

        def avaliar_erros_arquivo_nao_encontrado(linha):
            if col_status_rel:
                valor_rel = str(linha[col_status_rel]).strip().lower()
                if "arquivo não encontrado" in valor_rel or "arquivo nao encontrado" in valor_rel:
                    return "Arquivo Não Encontrado"
            return "Sem Erros"

        df['Inconsistencia_Erro'] = df.apply(avaliar_erros_arquivo_nao_encontrado, axis=1)
        df['Possui_Erro_Critico'] = df['Inconsistencia_Erro'] == "Arquivo Não Encontrado"

        # --- PLANILHA TO ---
        atendimentos_resolvidos_to = set()
        if arquivos_to:
            for arq_to in arquivos_to:
                df_to_temp = pd.read_csv(arq_to, sep=';', encoding='utf-8') if arq_to.name.endswith('.csv') else pd.read_excel(arq_to)
                df_to_temp.columns = df_to_temp.columns.str.strip()
                col_atend_to = next((col for col in df_to_temp.columns if 'atendimento' in col.lower() or 'nr.' in col.lower()), None)
                if col_atend_to:
                    atendimentos_resolvidos_to.update(df_to_temp[col_atend_to].dropna().astype(str).str.strip().unique())

        # --- PLANILHA 2 (SETORES) ---
        atendimentos_pendentes_setores = set()
        setores_agrupados = None
        df_s_consolidado = pd.DataFrame()
        
        if arquivos_setores:
            lista_dfs_setores = []
            for arq_s in arquivos_setores:
                df_s_temp = pd.read_csv(arq_s, sep=';', encoding='utf-8') if arq_s.name.endswith('.csv') else pd.read_excel(arq_s)
                df_s_temp.columns = df_s_temp.columns.str.strip()
                lista_dfs_setores.append(df_s_temp)
            
            df_s_consolidado = pd.concat(lista_dfs_setores, ignore_index=True)
            
            if 'Nº Atendimento' in df_s_consolidado.columns:
                df_s_consolidado['Nº Atendimento'] = df_s_consolidado['Nº Atendimento'].astype(str).str.strip()
                df_s_consolidado['Grupo Especialidade'] = df_s_consolidado['Grupo Especialidade'].fillna('Outros').astype(str).str.strip()
                
                # Nova coluna de status do setor para limpeza
                col_status_setor = next((c for c in df_s_consolidado.columns if 'status' in c.lower() or 'situação' in c.lower()), None)
                if col_status_setor:
                    df_s_consolidado[col_status_setor] = df_s_consolidado[col_status_setor].fillna('').astype(str).str.strip()
                
                # Filtro de Prevalência e Exclusão de "Implantação" / "Operação"
                def filtrar_setores_validos(linha):
                    esp = str(linha['Grupo Especialidade']).lower()
                    status_txt = str(linha[col_status_setor]).lower() if col_status_setor else ""
                    
                    # 3. Correção: Remove implantação e operação do fluxo
                    if "implantação" in status_txt or "implantacao" in status_txt or "operação" in status_txt or "operacao" in status_txt:
                        return False
                    if 'to' in esp or 'terapia ocupacional' in esp:
                        if linha['Nº Atendimento'] in atendimentos_resolvidos_to:
                            return False
                    return True
                
                df_s_consolidado = df_s_consolidado[df_s_consolidado.apply(filtrar_setores_validos, axis=1)]
                atendimentos_pendentes_setores = set(df_s_consolidado['Nº Atendimento'].unique())
                
                setores_agrupados = df_s_consolidado.groupby('Nº Atendimento')['Grupo Especialidade'].apply(
                    lambda x: ', '.join(sorted(set(x)))
                ).reset_index()
                setores_agrupados.columns = ['Nr. Atendimento', 'Especialidades Pendentes']

        if setores_agrupados is not None:
            df = pd.merge(df, setores_agrupados, on='Nr. Atendimento', how='left')
            df['Especialidades Pendentes'] = df['Especialidades Pendentes'].fillna('Nenhuma pendência técnica apontada')
        else:
            df['Especialidades Pendentes'] = 'Nenhuma pendência técnica apontada'

        df['Tem_Pendencia_Setor'] = df['Nr. Atendimento'].isin(atendimentos_pendentes_setores) & (~df['É_Robo'])

        if col_contrato:
            df['É_RioHome'] = df[col_contrato].str.lower().str.contains('riohome|rio home', regex=True).fillna(False)
        else:
            df['É_RioHome'] = False

        df_producao_limpa = df[df['Possui_Erro_Critico'] == False].copy()
        df_riohome = df_producao_limpa[df_producao_limpa['É_RioHome'] == True].copy()
        df_faturamento_geral = df_producao_limpa[df_producao_limpa['É_RioHome'] == False].copy()
        df_fila_robo = df_faturamento_geral[df_faturamento_geral['É_Robo'] == True].copy()
        df_faturamento_geral_sem_robo = df_faturamento_geral[df_faturamento_geral['É_Robo'] == False].copy()

        # Filtro estrito para Liberados Input
        df_liberados = df_faturamento_geral_sem_robo[(df_faturamento_geral_sem_robo['Inserido_Amil'] == False) & (df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == False)].copy()
        df_liberados = df_liberados.sort_values(by='Valor a Cobrar', ascending=False)

        df_prontuario = df_faturamento_geral_sem_robo[(df_faturamento_geral_sem_robo['Status Aut Orç'] == 'Prontuário Pendente') & (df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == True)].sort_values(by='Valor a Cobrar', ascending=False)
        df_ops = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Status Aut Orç'] == 'OPS Pendente'].sort_values(by='Valor a Cobrar', ascending=False)

        # --- ABAS ---
        aba1, aba2, aba3, aba4, aba5, aba_r, aba6 = st.tabs([
            "☀️ Resumo Geral", "👤 Gestão de Equipe", "🏥 Segmentação ID / AD", 
            "📋 Lista de Pendências", "🚀 Liberados para Input", "🤖 Liberados para o Robô", "🏠 RioHome"
        ])
        
        with aba1:
            st.markdown("### 📌 Indicadores Estruturados")
            card1, card2, card3 = st.columns(3)
            card1.metric("Total Base IW", f"{len(df)}")
            card2.metric("VALOR TOTAL BLOQUEADO", f"R$ {df['Valor a Cobrar'].sum():,.2f}")
            card3.metric("VALOR PENDÊNCIA TÉCNICA", f"R$ {df[df['Tem_Pendencia_Setor'] == True]['Valor a Cobrar'].sum():,.2f}")

        with aba2:
            st.markdown("### 👤 Gestão de Equipe (Métricas de Produção)")
            col_responsavel = 'Pessoa Resp Aut'
            df_producao_limpa['Robo_Contado'] = df_producao_limpa['Origem_Input_Calculado'] == "Robô"
            df_producao_limpa['Manual_Contado'] = df_producao_limpa['Origem_Input_Calculado'] == "Manual"
            
            prod_colab = df_producao_limpa.groupby(col_responsavel).agg(
                Inputs_pelo_Robo=('Robo_Contado', 'sum'),
                Inputs_Manuais=('Manual_Contado', 'sum'),
                Total_Geral=('Nome do Paciente', 'count')
            ).reset_index()
            st.dataframe(prod_colab, use_container_width=True, hide_index=True)

        with aba4:
            st.markdown("### 📋 Lista de Pendências")
            tab_p, tab_o = st.tabs(["📄 Prontuário Pendente", "🏢 OPS Pendente"])
            
            with tab_p:
                df_p_view = df_prontuario[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_p_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Setores Pendentes', 'Responsável', 'Valor do Paciente (R$)']
                st.dataframe(df_p_view.style.format({'Valor do Paciente (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                
            with tab_o:
                df_o_view = df_ops[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_o_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Setores Pendentes', 'Responsável', 'Valor do Paciente (R$)']
                st.dataframe(df_o_view.style.format({'Valor do Paciente (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba5:
            st.markdown("### 🚀 Pacientes Liberados para Input (Sem Implantação / Sem Operação)")
            df_liberados_view = df_liberados[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Tipo_Atendimento', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
            df_liberados_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo Atendimento', 'Responsável', 'Valor do Paciente (R$)']
            st.dataframe(df_liberados_view.style.format({'Valor do Paciente (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba_r:
            st.markdown("### 🤖 Fila do Robô")
            df_robo_view = df_fila_robo[['Nr. Atendimento', 'ID Orçam.', 'Nome do Paciente', 'Valor a Cobrar']].copy()
            df_robo_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Valor do Paciente (R$)']
            st.dataframe(df_robo_view.style.format({'Valor do Paciente (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba6:
            st.markdown("### 🏠 Contrato RioHome")
            df_rh_view = df_riohome[['Nr. Atendimento', 'Nome do Paciente', 'Valor a Cobrar']].copy()
            df_rh_view.columns = ['Nº Atendimento', 'Paciente', 'Valor do Paciente (R$)']
            st.dataframe(df_rh_view.style.format({'Valor do Paciente (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao processar arquivos: {e}")
else:
    st.info("💡 Aguardando o upload das planilhas para consolidação...")
