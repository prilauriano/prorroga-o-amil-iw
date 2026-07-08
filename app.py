import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. Configuração de página
st.set_page_config(page_title="Dashboard Prorrogações | Solar Cuidados", page_icon="☀️", layout="wide")

# 2. Injeção da Paleta de Cores Exata (Bordô, Dourado e Off-White)
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
st.markdown('<p class="subtitle">Módulo operacional integrado de auditoria Amil IW, monitoramento de prazos, volumetria ID/AD e controle de pendências técnicas por paciente.</p>', unsafe_allow_html=True)

# --- ÁREA DE UPLOAD ---
col_up1, col_up2, col_up3 = st.columns(3)
with col_up1:
    arquivos_amil = st.file_uploader("1 - PRORROGAÇÃO (.csv/.xlsx)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up2:
    arquivos_setores = st.file_uploader("2 - RELATÓRIOS DAS ESPECIALIDADES (Todas as Pendências)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up3:
    arquivos_to = st.file_uploader("3 - PACIENTES TO COM EVOLUÇÃO (Liberações de TO)", type=["csv", "xlsx"], accept_multiple_files=True)

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
            
            df_temp.columns = df_temp.columns.str.strip().str.lower()
            lista_dfs_amil.append(df_temp)
        
        df = pd.concat(lista_dfs_amil, ignore_index=True)
        
        col_justificativa = next((col for col in df.columns if 'justificativa' in col or 'pendencia' in col), None)
        col_status_rel = next((col for col in df.columns if 'status rel' in col or 'rel orç' in col or 'status_rel' in col or 'rel orc' in col), None)
        col_contrato = next((col for col in df.columns if str(col).strip() == 'contrato'), None)
        col_valor = next((col for col in df.columns if 'valor a cobrar' in col or 'valor' in col), 'valor a cobrar')
        col_atendimento = next((col for col in df.columns if 'nr. atendimento' in col or 'nº atendimento' in col or 'nr.atendimento' in col), 'nr. atendimento')
        col_classificacao = next((col for col in df.columns if 'classific. atendimento' in col or 'classific.' in col or 'classificacao' in col), 'classific. atendimento')
        col_responsavel = next((col for col in df.columns if 'resp' in col or 'pessoa' in col or 'persona' in col), 'pessoa resp aut')
        
        campos_obrigatorios = ['nº guia solicitação (tiss)', 'senha aprovação', 'status aut orç', 'nr. matricula', col_responsavel, col_classificacao, 'nome do paciente', 'id orçam.']
        if col_justificativa: campos_obrigatorios.append(col_justificativa)
        if col_status_rel: campos_obrigatorios.append(col_status_rel)
        if col_contrato: campos_obrigatorios.append(col_contrato)
            
        for c in campos_obrigatorios:
            if c in df.columns:
                df[c] = df[c].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            elif c == 'id orçam.':
                df['id orçam.'] = ''
        
        if col_atendimento in df.columns:
            df[col_atendimento] = df[col_atendimento].fillna('').astype(str).str.strip()
        else:
            df[col_atendimento] = ''
            
        df['nome do paciente_limpo'] = df['nome do paciente'].str.lower().str.strip()
        
        # TRATAMENTO DE MOEDA
        def converter_moeda_br(valor):
            if pd.isna(valor): return 0.0
            if isinstance(valor, (int, float)):
                v_float = float(valor)
                if 0 < v_float < 10.0: return v_float * 1000.0
                return v_float
            valor_str = str(valor).strip().upper().replace('R$', '').strip()
            if not valor_str or valor_str in ['NAN', '']: return 0.0
            if ',' in valor_str and '.' in valor_str:
                if valor_str.find('.') < valor_str.find(','):
                    valor_str = valor_str.replace('.', '').replace(',', '.')
            elif ',' in valor_str: 
                valor_str = valor_str.replace(',', '.')
            elif '.' in valor_str:
                partes = valor_str.split('.')
                if len(partes[-1]) == 3: valor_str = valor_str.replace('.', '')
            try: 
                resultado = float(valor_str)
                if 0 < resultado < 10.0: return resultado * 1000.0
                return resultado
            except: return 0.0

        if col_valor in df.columns:
            df['valor_calculado'] = df[col_valor].apply(converter_moeda_br)
        else:
            df['valor_calculado'] = 0.0
        
        df['Is_ID'] = df[col_classificacao].str.upper().str.startswith('ID', na=False) if col_classificacao in df.columns else False
        df['Is_AD'] = df[col_classificacao].str.upper().str.startswith('AD', na=False) if col_classificacao in df.columns else False
        df['Tipo_Atendimento'] = df[col_classificacao].apply(
            lambda x: 'ID (Internação Domiciliar)' if str(x).strip().upper().startswith('ID') else ('AD (Atenção Domiciliar)' if str(x).strip().upper().startswith('AD') else 'Outros')
        ) if col_classificacao in df.columns else 'Outros'

        df['Inserido_Amil'] = df['nº guia solicitação (tiss)'].str.isnumeric() if 'nº guia solicitação (tiss)' in df.columns else False

        def verificar_origem_input(linha):
            just_txt = str(linha[col_justificativa]).lower().strip() if col_justificativa else ""
            status_aut = str(linha['status aut orç']).lower().strip() if 'status aut orç' in df.columns else ""
            if "operadora: robo" in just_txt or "operadora: robô" in just_txt or "lib. para o robô" in status_aut or "lib. para o robo" in status_aut: 
                return "Robô"
            elif "operadora: manual" in just_txt: 
                return "Manual"
            return "Outro"

        df['Origem_Input_Calculado'] = df.apply(verificar_origem_input, axis=1)

        def verificar_flag_robo_exata(linha):
            just_txt = str(linha[col_justificativa]).strip() if col_justificativa else ""
            status_aut = str(linha['status aut orç']).strip() if 'status aut orç' in df.columns else ""
            return ("Robô aguardando input" in just_txt or "Robo aguardando input" in just_txt) and ("Lib. para o Robô input" in status_aut or "Lib. para o Robo input" in status_aut)
        df['É_Robo'] = df.apply(verificar_flag_robo_exata, axis=1)

        df['Possui_Erro_Critico'] = df[col_status_rel].str.lower().str.contains("arquivo não encontrado|arquivo nao encontrado", na=False) if col_status_rel else False

        # --- 📑 LEITURA DA PLANILHA 3 (PACIENTES TO COM EVOLUÇÃO) ---
        nomes_entregues_planilha3 = set()
        if arquivos_to:
            for arq_to in arquivos_to:
                if arq_to.name.endswith('.csv'):
                    try: df_to_temp = pd.read_csv(arq_to, sep=';', encoding='utf-8')
                    except: 
                        arq_to.seek(0)
                        df_to_temp = pd.read_csv(arq_to, sep=';', encoding='iso-8859-1')
                else:
                    df_to_temp = pd.read_excel(arq_to)
                df_to_temp.columns = df_to_temp.columns.str.strip().str.lower()
                
                col_nome_to = next((col for col in df_to_temp.columns if 'nome' in col or 'paciente' in col), None)
                if col_nome_to:
                    nomes_entregues_planilha3.update(df_to_temp[col_nome_to].dropna().astype(str).str.lower().str.strip().unique())

        # --- ⚙️ PROCESSAMENTO DA PLANILHA 2 (SETORES TÉCNICOS) ---
        atendimentos_com_outras_pendencias = set()
        atendimentos_com_pendencia_to_estrita = set()
        df_s_visual = pd.DataFrame()
        
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
                df_s_temp.columns = df_s_temp.columns.str.strip().str.lower()
                lista_dfs_setores.append(df_s_temp)
            
            df_s_consolidado = pd.concat(lista_dfs_setores, ignore_index=True)
            col_s_atend = next((c for c in df_s_consolidado.columns if 'nº atendimento' in c or 'nr. atendimento' in c or 'atendimento' in c), None)
            col_s_esp = next((c for c in df_s_consolidado.columns if 'grupo especialidade' in c or 'especialidade' in c), None)
            col_s_nome = next((c for c in df_s_consolidado.columns if 'nome paciente' in c or 'nome do paciente' in c or 'paciente' in c or 'nome' in c), None)
            col_s_template = next((c for c in df_s_consolidado.columns if 'template' in c), None)
            
            if col_s_atend and col_s_nome and col_s_template:
                df_s_consolidado[col_s_atend] = df_s_consolidado[col_s_atend].astype(str).str.strip()
                df_s_consolidado['nome_paciente_p2'] = df_s_consolidado[col_s_nome].astype(str).str.lower().str.strip()
                df_s_consolidado['template_p2'] = df_s_consolidado[col_s_template].fillna('').astype(str).str.upper().str.strip()
                
                if col_s_esp:
                    df_s_consolidado['especialidade_limpa'] = df_s_consolidado[col_s_esp].fillna('Outros').astype(str).str.strip()
                else:
                    df_s_consolidado['especialidade_limpa'] = 'Outros'

                def normalizar_nome_setor(nome):
                    n = str(nome).strip().upper()
                    if "MEDIC" in n or "MEDIQ" in n: return "Médico"
                    if "FISIO" in n: return "Fisioterapia"
                    if "FONO" in n: return "Fonoaudiologia"
                    if "NUTRI" in n: return "Nutrição"
                    if "TERAPIA OCUPACIONAL" in n or "TO" == n: return "Terapia Ocupacional"
                    if "PSICO" in n: return "Psicologia"
                    return str(nome).strip().title()

                df_s_consolidado['setor_normalizado'] = df_s_consolidado['especialidade_limpa'].apply(normalizar_nome_setor)
                
                # Força a marcação como Terapia Ocupacional se o template contiver "TO"
                df_s_consolidado.loc[df_s_consolidado['template_p2'].str.contains('TO'), 'setor_normalizado'] = 'Terapia Ocupacional'

                def aplicar_nova_regra_validacao_to(linha):
                    nome_p2 = str(linha['nome_paciente_p2'])
                    setor = str(linha['setor_normalizado'])
                    
                    if setor == "Terapia Ocupacional":
                        if nome_p2 in nomes_entregues_planilha3:
                            return "RESOLVIDO_TO"
                        else:
                            return "TO (Pendência Ativa)"
                    return "OUTRO"

                df_s_consolidado['status_validacao_to'] = df_s_consolidado.apply(aplicar_nova_regra_validacao_to, axis=1)

                for _, text_linha in df_s_consolidado.iterrows():
                    atend = str(text_linha[col_s_atend])
                    status_to = str(text_linha['status_validacao_to'])
                    setor = str(text_linha['setor_normalizado'])
                    
                    if status_to == "TO (Pendência Ativa)":
                        atendimentos_com_pendencia_to_estrita.add(atend)
                    elif status_to == "OUTRO" and setor != "Terapia Ocupacional":
                        atendimentos_com_outras_pendencias.add(atend)

                df_s_visual = df_s_consolidado.copy()
                df_s_visual = df_s_visual[df_s_visual['status_validacao_to'] != "RESOLVIDO_TO"]

        # --- RE-ESTRUTURAÇÃO DAS REGRAS LOGICAS POR PACIENTE ---
        df['Tem_Outra_Pendencia_Setor'] = df[col_atendimento].isin(atendimentos_com_outras_pendencias)
        
        def checar_to_bloqueante_final(linha):
            atend = str(linha[col_atendimento])
            nome_amil = str(linha['nome do paciente_limpo'])
            if nome_amil in nomes_entregues_planilha3: 
                return False
            return atend in atendimentos_com_pendencia_to_estrita

        df['Tem_Pendencia_TO_Ativa'] = df.apply(checar_to_bloqueante_final, axis=1)
        df['Tem_Pendencia_Setor'] = (df['Tem_Outra_Pendencia_Setor'] | df['Tem_Pendencia_TO_Ativa']) & (~df['É_Robo'])

        df_setores_valores = pd.DataFrame()
        if not df_s_visual.empty:
            df_s_ativos_apenas = []
            for _, idx_row in df_s_visual.iterrows():
                atend_id = str(idx_row[col_s_atend])
                setor_nome = str(idx_row['setor_normalizado'])
                
                if setor_nome == "Terapia Ocupacional" and atend_id in atendimentos_com_pendencia_to_estrita:
                    df_s_ativos_apenas.append(idx_row)
                elif setor_nome != "Terapia Ocupacional" and atend_id in atendimentos_com_outras_pendencias:
                    df_s_ativos_apenas.append(idx_row)
            
            if df_s_ativos_apenas:
                df_s_visual_filtrado = pd.DataFrame(df_s_ativos_apenas)
                setores_agrupados = df_s_visual_filtrado.groupby(col_s_atend)['setor_normalizado'].apply(
                    lambda x: ', '.join(sorted(set(x)))
                ).reset_index()
                setores_agrupados.columns = [col_atendimento, 'Especialidades Pendentes']
                df = pd.merge(df, setores_agrupados, on=col_atendimento, how='left')
                
                df_setores_valores = pd.merge(df_s_visual_filtrado[[col_s_atend, 'setor_normalizado']], df[[col_atendimento, 'valor_calculado', 'Tem_Pendencia_Setor']], left_on=col_s_atend, right_on=col_atendimento, how='inner')
                df_setores_valores = df_setores_valores[df_setores_valores['Tem_Pendencia_Setor'] == True]

        df['Especialidades Pendentes'] = df['Especialidades Pendentes'].fillna('Nenhuma pendência técnica apontada')
        df.loc[df['Especialidades Pendentes'] == '', 'Especialidades Pendentes'] = 'Nenhuma pendência técnica apontada'

        df['É_RioHome'] = df[col_contrato].str.lower().str.contains('riohome|rio home|rio_home', regex=True).fillna(False) if col_contrato else False
        df_base_erros = df[df['Possui_Erro_Critico'] == True].copy()
        df_producao_limpa = df[df['Possui_Erro_Critico'] == False].copy()

        df_riohome = df_producao_limpa[df_producao_limpa['É_RioHome'] == True].copy()
        df_faturamento_geral = df_producao_limpa[df_producao_limpa['É_RioHome'] == False].copy()

        df_fila_robo = df_faturamento_geral[
            (df_faturamento_geral['É_Robo'] == True) & 
            (df_faturamento_geral['Inserido_Amil'] == False) &
            (df_faturamento_geral['nome do paciente'].str.strip() != "") & 
            (~df_faturamento_geral['status aut orç'].str.lower().str.contains('implantação|implantacao|operação|operacao', na=False))
        ].copy()
        
        df_faturamento_geral_sem_robo = df_faturamento_geral[df_faturamento_geral['É_Robo'] == False].copy()

        df_prontuario = df_faturamento_geral_sem_robo[
            (df_faturamento_geral_sem_robo['status aut orç'] == 'Prontuário Pendente') & 
            (df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == True)
        ].sort_values(by='valor_calculado', ascending=False) if 'status aut orç' in df_faturamento_geral_sem_robo.columns else pd.DataFrame()
        
        df_ops = df_faturamento_geral_sem_robo[
            (df_faturamento_geral_sem_robo['status aut orç'] == 'OPS Pendente') &
            (df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == True)
        ].sort_values(by='valor_calculado', ascending=False) if 'status aut orç' in df_faturamento_geral_sem_robo.columns else pd.DataFrame()

        df_liberados = df_faturamento_geral_sem_robo[
            (df_faturamento_geral_sem_robo['Inserido_Amil'] == False) & 
            (df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == False) &
            (~df_faturamento_geral_sem_robo['status aut orç'].str.lower().str.strip().isin(['em avaliação', '', 'implantação', 'implantacao', 'operação', 'operacao']))
        ].copy().sort_values(by='valor_calculado', ascending=False)

        # Métricas globais
        total_pacientes_iw = len(df)
        inseridos_count = df_producao_limpa['Inserido_Amil'].sum()
        valor_total_todos_pacientes = df['valor_calculado'].sum()
        valor_total_pendencias_setores = df[df['Tem_Pendencia_Setor'] == True]['valor_calculado'].sum()
        total_pendentes_input_real = (df['Inserido_Amil'] == False).sum()

        # --- ABAS DO DASHBOARD ---
        aba1, aba2, aba3, aba4, aba5, aba_r, aba6, aba7 = st.tabs([
            "☀️ Resumo Geral", "👤 Gestão de Equipe", "🏥 Segmentação ID / AD", 
            "📋 Lista de Pendências", "🚀 Liberados para Input", "🤖 Liberados para o Robô",
            "🏠 Contrato RioHome (Manual)", "🚨 Alertas de Erro"
        ])
        
        with aba1:
            st.markdown("### 📌 Indicadores Operacionais e Financeiros Estruturados")
            card1, card2, card3, card4, card5, card6 = st.columns(6)
            card1.metric("Total Base Bruta IW", f"{total_pacientes_iw}")
            card2.metric("✅ Inseridos (Com Guia TISS)", f"{inseridos_count}")
            card3.metric("🚀 Pendentes para Input", f"{total_pendentes_input_real}")
            card4.metric("🤖 Fila do Robô (Filtro Exato)", f"{len(df_fila_robo)}")
            card5.metric("VALOR TOTAL DE PACIENTES", f"R$ {valor_total_todos_pacientes:,.2f}")
            card6.metric("VALOR TOTAL EM PENDÊNCIA TÉCNICA", f"R$ {valor_total_pendencias_setores:,.2f}")

        with aba2:
            st.markdown("### 👤 Carga Operacional e Rastreabilidade de Inputs (Robô vs Manual)")
            if col_responsavel in df_producao_limpa.columns:
                df_producao_limpa['Valor_ID'] = df_producao_limpa.apply(lambda r: r['valor_calculado'] if r['Is_ID'] else 0.0, axis=1)
                df_producao_limpa['Valor_AD'] = df_producao_limpa.apply(lambda r: r['valor_calculado'] if r['Is_AD'] else 0.0, axis=1)
                df_producao_limpa['Robo_Contado'] = df_producao_limpa['Origem_Input_Calculado'] == "Robô"
                df_producao_limpa['Manual_Contado'] = df_producao_limpa['Origem_Input_Calculado'] == "Manual"
                
                prod_colab = df_producao_limpa.groupby(col_responsavel).agg(
                    Pacientes_ID=('Is_ID', 'sum'), Pacientes_AD=('Is_AD', 'sum'),
                    Soma_Valor_ID=('Valor_ID', 'sum'), Soma_Valor_AD=('Valor_AD', 'sum'),
                    Inputs_pelo_Robo=('Robo_Contado', 'sum'), Inputs_Manuais=('Manual_Contado', 'sum'),
                    Total_Geral_Pacientes=('nome do paciente', 'count')
                ).reset_index()
                prod_colab.columns = ['Colaborador (Responsável)', 'Nº Pacientes ID', 'Nº Pacientes AD', 'Valor Total de ID (R$)', 'Valor Total de AD (R$)', 'Inputs Concluídos p/ Robô', 'Inputs Concluídos Manuais', 'Quantitativo Total']
                st.dataframe(prod_colab.style.format({'Valor Total de ID (R$)': 'R$ {:,.2f}', 'Valor Total de AD (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba3:
            st.markdown("### Análise do Modelo de Atendimento Solar (ID vs AD)")
            df_id_ad = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Inserido_Amil'] == False].groupby('Tipo_Atendimento').agg(Quantidade=('nome do paciente', 'count'), Valor_Total=('valor_calculado', 'sum')).reset_index()
            st.dataframe(df_id_ad.style.format({'Valor_Total': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba4:
            st.markdown("### 📋 Lista de Pendências Ativas por Orçamento do Paciente")
            if arquivos_setores and 'df_setores_valores' in locals() and not df_setores_valores.empty:
                st.markdown("#### 📊 Distribuição Financeira Total Retida por Setor (Valor do Orçamento)")
                
                df_grafico = df_setores_valores.groupby('setor_normalizado')['valor_calculado'].sum().reset_index()
                df_grafico.columns = ['Setor Técnico', 'Valor Total Retido']
                df_grafico = df_grafico[df_grafico['Valor Total Retido'] > 0].sort_values(by="Valor Total Retido", ascending=False)
                
                if not df_grafico.empty:
                    fig_valores = px.bar(df_grafico, x='Setor Técnico', y='Valor Total Retido', color='Valor Total Retido', color_continuous_scale='Oryel', text_auto='R$ ,.2f')
                    fig_valores.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_valores, use_container_width=True)

            tab_p, tab_o = st.tabs(["📄 Prontuário Pendente (Filtro Unificado)", "🏢 OPS Pendente (Operação)"])
            with tab_p:
                if not df_prontuario.empty:
                    st.markdown(f"**Total de Processos: {len(df_prontuario)} | Montante: R$ {df_prontuario['valor_calculado'].sum():,.2f}**")
                    df_p_view = df_prontuario[[col_atendimento, 'id orçam.', 'nome do paciente', 'Tipo_Atendimento', 'Especialidades Pendentes', col_responsavel, 'valor_calculado']].copy()
                    df_p_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor do Paciente (R$)']
                    
                    buffer_p = io.BytesIO()
                    with pd.ExcelWriter(buffer_p, engine='xlsxwriter') as writer:
                        df_p_view.to_excel(writer, sheet_name='Prontuário Pendente', index=False)
                    st.download_button(label="📥 Baixar Planilha Estruturada: Prontuário Pendente", data=buffer_p.getvalue(), file_name="prontuario_pendente_priorizado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    st.dataframe(df_p_view.style.format({'Valor do Paciente (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                else: st.info("Nenhuma pendência de prontuário activa baseada no filtro unificado.")
                
            with tab_o:
                if not df_ops.empty:
                    st.markdown(f"**Total de Processos: {len(df_ops)} | Montante: R$ {df_ops['valor_calculado'].sum():,.2f}**")
                    df_o_view = df_ops[[col_atendimento, 'id orçam.', 'nome do paciente', 'Tipo_Atendimento', 'Especialidades Pendentes', col_responsavel, 'valor_calculado']].copy()
                    df_o_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo', 'Setores Pendentes', 'Responsável', 'Valor do Paciente (R$)']
                    
                    buffer_o = io.BytesIO()
                    with pd.ExcelWriter(buffer_o, engine='xlsxwriter') as writer:
                        df_o_excel = df_o_view.copy()
                    st.download_button(label="📥 Baixar Planilha Estruturada: Pendências da Operação", data=buffer_o.getvalue(), file_name="ops_pendente_estruturado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    st.dataframe(df_o_view.style.format({'Valor do Paciente (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                else: st.info("Nenhuma pendência de OPS activa.")

        with aba5:
            st.markdown("### 🚀 Pacientes Liberados (Sem Pendências nos Setores)")
            if not arquivos_setores:
                st.warning("⚠️ Para ver quem está liberado, carregue a planilha de Setores no campo de upload.")
            else:
                st.markdown(f"**🔥 Total Prontos para Input: {len(df_liberados)} | Valor de Giro Rápido: R$ {df_liberados['valor_calculado'].sum():,.2f}**")
                df_liberados_clean_excel = df_liberados[[col_atendimento, 'id orçam.', 'nome do paciente', 'Tipo_Atendimento', col_responsavel, 'valor_calculado']].copy()
                df_liberados_clean_excel.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo Atendimento', 'Responsável', 'Valor a Cobrar (R$)']
                
                buffer_liberados = io.BytesIO()
                with pd.ExcelWriter(buffer_liberados, engine='xlsxwriter') as writer:
                    df_liberados_clean_excel.to_excel(writer, sheet_name='Liberados Input', index=False)
                st.download_button(label="📥 Baixar Planilha Estruturada: Liberados para Input", data=buffer_liberados.getvalue(), file_name="liberados_para_input.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                st.dataframe(df_liberados_clean_excel.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba_r:
            st.markdown("### 🤖 Fila de Pacientes Encaminhados para Input Automatizado")
            st.markdown(f"**Volumetria Atual do Robô: {len(df_fila_robo)} pacientes na fila.**")
            if len(df_fila_robo) > 0:
                df_robo_view = df_fila_robo[[col_atendimento, 'id orçam.', 'nome do paciente', 'Tipo_Atendimento', 'status aut orç', 'valor_calculado']].copy()
                df_robo_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo', 'Status Atual', 'Valor a Cobrar (R$)']
                st.dataframe(df_robo_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
            else: st.info("💡 Nenhum paciente aguardando ou liberado para o robô detectado.")

        with aba6:
            st.markdown("### 🏠 Listagem Isolada — Contrato RioHome")
            df_riohome_view = df_riohome[[col_atendimento, 'id orçam.', 'nome do paciente', 'Tipo_Atendimento', col_responsavel, 'status aut orç', 'valor_calculado']].copy()
            df_riohome_view.columns = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo', 'Responsável', 'Status Atual IW', 'Valor a Cobrar (R$)']
            st.dataframe(df_riohome_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba7:
            st.markdown("### 🚨 Alertas de Erro: Arquivo Não Encontrado")
            if len(df_base_erros) > 0:
                colunas_erro = [col_atendimento, 'id orçam.', 'nome do paciente', 'status aut orç', col_responsavel]
                if col_status_rel: colunas_erro.insert(3, col_status_rel)
                df_erro_print = df_base_erros[colunas_erro].copy()
                colunas_visualizacao = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Status Aut Orç', 'Responsável']
                if col_status_rel: colunas_visualizacao.insert(3, 'Texto Capturado no Campo')
                df_erro_print.columns = colunas_visualizacao
                st.dataframe(df_erro_print, use_container_width=True, hide_index=True)
            else: st.success("✨ Excelente! Nenhum erro de 'Arquivo Não Encontrado' foi detectado.")
                    
    except Exception as e: st.error(f"Erro ao processar os arquivos. Detalhe técnico: {e}")
else: st.info("💡 Tudo pronto! Selecione os arquivos acima nos novos campos estruturados para carregar o cruzamento dinâmico.")
