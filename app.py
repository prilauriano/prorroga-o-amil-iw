import streamlit as st
import pandas as pd
import plotly.express as px
import io
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")

def agora_brasil():
    """Retorna o horário atual já convertido para o fuso de Brasília (America/Sao_Paulo)."""
    return datetime.now(FUSO_BRASILIA)


# 1. Configuração de página
st.set_page_config(page_title="Dashboard Prorrogações | Solar Cuidados", page_icon="☀️", layout="wide")


# Inicialização do Histórico em Sessão (Persistência em memória na navegação do Streamlit)
if 'historico_coletas_df' not in st.session_state:
    st.session_state.historico_coletas_df = pd.DataFrame(columns=[
        "Data", "Hora", "Ciclo", "Total da Base", "Pendentes", "Robô", "Manual", "Valor Pendente", "Percentual de Conclusão"
    ])


# Parâmetros Padrão de Configuração de Metas (Caso o usuário queira customizar na interface)
if 'meta_conclusao' not in st.session_state: st.session_state.meta_conclusao = 85.0
if 'meta_pendencias' not in st.session_state: st.session_state.meta_pendencias = 50
if 'meta_automacao' not in st.session_state: st.session_state.meta_automacao = 60.0
if 'meta_valor' not in st.session_state: st.session_state.meta_valor = 500000.0


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
        font-size: 24px !important;
        letter-spacing: -1px;
    }
    
    .stDataFrame {
        background-color: #FFFFFF !important;
        border: 1px solid #E2DDD6 !important;
        border-radius: 12px !important;
    }
    
    /* Box do Semáforo Inteligente */
    .semaforo-card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #E2DDD6;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Box de Insights */
    .insight-card {
        background-color: #FFFFFF;
        border-left: 5px solid #5C1220;
        padding: 15px 20px;
        border-radius: 4px 12px 12px 4px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
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
        
        col_justificativa = next((col for col in df.columns if 'justificativa' in col or 'pendencia' in col), 'justificativa pendência')
        col_status_rel = next((col for col in df.columns if 'status rel' in col or 'rel orç' in col or 'status_rel' in col or 'rel orc' in col), None)
        col_contrato = next((col for col in df.columns if str(col).strip() == 'contrato'), None)
        col_valor = next((col for col in df.columns if 'valor a cobrar' in col or 'valor' in col), 'valor a cobrar')
        col_atendimento = next((col for col in df.columns if 'nr. atendimento' in col or 'nº atendimento' in col or 'nr.atendimento' in col), 'nr. atendimento')
        col_classificacao = next((col for col in df.columns if 'classific. atendimento' in col or 'classific.' in col or 'classificacao' in col), 'classific. atendimento')
        
        # FIXAÇÃO EXATA DA COLUNA DE RESPONSÁVEL DO IW
        col_responsavel = 'persona resp aut' if 'persona resp aut' in df.columns else ('pessoa resp aut' if 'pessoa resp aut' in df.columns else 'responsavel')
        if col_responsavel not in df.columns and 'pessoa resp aut' in df.columns:
            col_responsavel = 'pessoa resp aut'
        elif col_responsavel not in df.columns:
            col_responsavel = 'pessoa resp aut'
            df[col_responsavel] = ''
        
        campos_obrigatorios = ['nº guia solicitação (tiss)', 'senha aprovação', 'status aut orç', 'nr. matricula', col_responsavel, col_classificacao, 'nome do paciente', 'id orçam.']
        if col_justificativa in df.columns: campos_obrigatorios.append(col_justificativa)
        if col_status_rel: campos_obrigatorios.append(col_status_rel)
        if col_contrato: campos_obrigatorios.append(col_contrato)
            
        for c in campos_obrigatorios:
            if c in df.columns:
                df[c] = df[c].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            elif c == 'id orçam.':
                df['id orçam.'] = ''
            elif c == col_responsavel:
                df[col_responsavel] = ''
        
        if col_atendimento in df.columns:
            df[col_atendimento] = df[col_atendimento].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
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
            just_txt = str(linha[col_justificativa]).lower().strip() if col_justificativa in df.columns else ""
            status_aut = str(linha['status aut orç']).lower().strip() if 'status aut orç' in df.columns else ""
            if "operadora: robo" in just_txt or "operadora: robô" in just_txt or "lib. para o robô" in status_aut or "lib. para o robo" in status_aut: 
                return "Robô"
            elif "operadora: manual" in just_txt: 
                return "Manual"
            return "Outro"

        df['Origem_Input_Calculado'] = df.apply(verificar_origem_input, axis=1)

        def verificar_flag_robo_exata(linha):
            just_txt = str(linha[col_justificativa]).strip() if col_justificativa in df.columns else ""
            status_aut = str(linha['status aut orç']).strip() if 'status aut orç' in df.columns else ""
            return ("Robô aguardando input" in just_txt or "Robo aguardando input" in just_txt) and ("Lib. para o Robô input" in status_aut or "Lib. para o Robo input" in status_aut)
        df['É_Robo'] = df.apply(verificar_flag_robo_exata, axis=1)

        df['Possui_Erro_Critico'] = df[col_status_rel].str.lower().str.contains("arquivo não encontrado|arquivo nao encontrado", na=False) if col_status_rel else False

        # --- 📑 LEITURA DA PLANILHA 3 (PACIENTES TO COM EVOLUÇÃO) - USANDO Nº ATENDIMENTO ---
        atendimentos_entregues_planilha3 = set()
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
                
                col_atend_to = next((col for col in df_to_temp.columns if 'nº atendimento' in col or 'nr. atendimento' in col or 'atendimento' in col), None)
                if col_atend_to:
                    atendimentos_entregues_planilha3.update(
                        df_to_temp[col_atend_to].dropna().astype(str).str.replace(r'\.0$', '', regex=True).str.strip().unique()
                    )

        # --- ⚙️ PROCESSAMENTO DA PLANILHA 2 (SETORES TÉCNICOS) ---
        atendimentos_com_outras_pendencias = set()
        atendimentos_com_pendencia_to_estrita = set()
        df_s_consolidado = pd.DataFrame()
        
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
                grid_cols = df_s_temp.columns.str.strip().str.lower()
                df_s_temp.columns = grid_cols
                lista_dfs_setores.append(df_s_temp)
            
            df_s_consolidado = pd.concat(lista_dfs_setores, ignore_index=True)
            col_s_atend = next((c for c in df_s_consolidado.columns if 'nº atendimento' in c or 'nr. atendimento' in c or 'atendimento' in c), None)
            col_s_esp = next((c for c in df_s_consolidado.columns if 'grupo especialidade' in c or 'especialidade' in c), None)
            col_s_template = next((c for c in df_s_consolidado.columns if 'template' in c), None)
            
            if col_s_atend and col_s_template:
                df_s_consolidado[col_s_atend] = df_s_consolidado[col_s_atend].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                df_s_consolidado['template_p2'] = df_s_consolidado[col_s_template].fillna('').astype(str).str.upper().str.strip()
                
                if col_s_esp:
                    df_s_consolidado['especialidade_limpa'] = df_s_consolidado[col_s_esp].fillna('Outros').astype(str).str.strip()
                else:
                    df_s_consolidado['especialidade_limpa'] = 'Outros'

                def normalizar_nome_setor(linha):
                    esp = str(linha['especialidade_limpa']).strip().upper()
                    tmpl = str(linha['template_p2'])
                    
                    if "MEDIC" in esp or "MEDIQ" in esp: return "Médico"
                    if "FISIO" in esp: return "Fisioterapia"
                    if "FONO" in esp: return "Fonoaudiologia"
                    if "NUTRI" in esp: return "Nutrição"
                    if "PSICO" in esp: return "Psicologia"
                    
                    if "TERAPIA OCUPACIONAL" in esp or esp == "TO" or "TERAPEUTA" in esp or tmpl == "TO" or " TO " in f" {tmpl} ": 
                        return "Terapia Ocupacional"
                    
                    return esp.title()

                df_s_consolidado['setor_normalizado'] = df_s_consolidado.apply(normalizar_nome_setor, axis=1)

                def aplicar_nova_regra_validacao_to_atend(linha):
                    atend_p2 = str(linha[col_s_atend])
                    setor = str(linha['setor_normalizado'])
                    if setor == "Terapia Ocupacional":
                        if atend_p2 in atendimentos_entregues_planilha3:
                            return "RESOLVIDO_TO"
                        else:
                            return "TO (Pendência Ativa)"
                    return "OUTRO"

                df_s_consolidado['status_validacao_to'] = df_s_consolidado.apply(aplicar_nova_regra_validacao_to_atend, axis=1)

                for _, text_linha in df_s_consolidado.iterrows():
                    atend = str(text_linha[col_s_atend])
                    status_to = str(text_linha['status_validacao_to'])
                    setor = str(text_linha['setor_normalizado'])
                    
                    if status_to == "TO (Pendência Ativa)":
                        atendimentos_com_pendencia_to_estrita.add(atend)
                    elif status_to == "OUTRO" and setor != "Terapia Ocupacional":
                        atendimentos_com_outras_pendencias.add(atend)

        # --- LOGICAS DE FILTRO POR PACIENTE ---
        df['Tem_Outra_Pendencia_Setor'] = df[col_atendimento].isin(atendimentos_com_outras_pendencias)
        
        def checar_to_bloqueante_final_atend(linha):
            atend = str(linha[col_atendimento])
            if atend in atendimentos_entregues_planilha3: 
                return False
            return atend in atendimentos_com_pendencia_to_estrita

        df['Tem_Pendencia_TO_Ativa'] = df.apply(checar_to_bloqueante_final_atend, axis=1)
        df['Tem_Pendencia_Setor'] = (df['Tem_Outra_Pendencia_Setor'] | df['Tem_Pendencia_TO_Ativa']) & (~df['É_Robo'])

        # --- CONSTRUÇÃO DAS ESPECIALIDADES PENDENTES ---
        if arquivos_setores and not df_s_consolidado.empty:
            df_s_ativos_reais = []
            for _, idx_row in df_s_consolidado.iterrows():
                atend_id = str(idx_row[col_s_atend])
                setor_nome = str(idx_row['setor_normalizado'])
                
                if setor_nome == "Terapia Ocupacional" and atend_id in atendimentos_com_pendencia_to_estrita:
                    df_s_ativos_reais.append(idx_row)
                elif setor_nome != "Terapia Ocupacional" and atend_id in atendimentos_com_outras_pendencias:
                    df_s_ativos_reais.append(idx_row)
            
            if df_s_ativos_reais:
                df_s_ativos_df = pd.DataFrame(df_s_ativos_reais)
                df_s_ativos_df = df_s_ativos_df[df_s_ativos_df['setor_normalizado'] != "Terapia Ocupacional"]
                
                setores_agrupados = df_s_ativos_df.groupby(col_s_atend)['setor_normalizado'].apply(
                    lambda x: ', '.join(sorted(set(x)))
                ).reset_index()
                setores_agrupados.columns = [col_atendimento, 'Especialidades Pendentes']
                
                df = pd.merge(df, setores_agrupados, on=col_atendimento, how='left')

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

        # Tabelas Filtradas
        df_prontuario = df_faturamento_geral_sem_robo[
            (df_faturamento_geral_sem_robo['status aut orç'] == 'Prontuário Pendente') & 
            (df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == True) &
            (df_faturamento_geral_sem_robo['Especialidades Pendentes'] != 'Nenhuma pendência técnica apontada')
        ].sort_values(by='valor_calculado', ascending=False) if 'status aut orç' in df_faturamento_geral_sem_robo.columns else pd.DataFrame()
        
        df_ops = df_faturamento_geral_sem_robo[
            (df_faturamento_geral_sem_robo['status aut orç'] == 'OPS Pendente') & 
            (df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == True) &
            (df_faturamento_geral_sem_robo['Especialidades Pendentes'] != 'Nenhuma pendência técnica apontada')
        ].sort_values(by='valor_calculado', ascending=False) if 'status aut orç' in df_faturamento_geral_sem_robo.columns else pd.DataFrame()

        # --- Normalização auxiliar (sem acento e minúscula) para comparações robustas de texto ---
        def normalizar_texto_sem_acento(texto):
            texto = str(texto) if not pd.isna(texto) else ''
            texto = texto.strip().lower()
            texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
            return texto

        def contem_termo_excluido_liberados(texto):
            texto_norm = normalizar_texto_sem_acento(texto)
            termos_excluidos = ['em avaliacao', 'implantacao', 'operacao', 'operadora pendente']
            return any(termo in texto_norm for termo in termos_excluidos)

        # Status vazio ou contendo um dos termos excluídos (comportamento original preservado)
        if 'status aut orç' in df_faturamento_geral_sem_robo.columns:
            status_vazio_ou_termo = df_faturamento_geral_sem_robo['status aut orç'].apply(
                lambda s: normalizar_texto_sem_acento(s) == '' or contem_termo_excluido_liberados(s)
            )
        else:
            status_vazio_ou_termo = False

        # Conteúdo do campo "Justificativa Pendência" (IW) também não pode indicar esses termos
        if col_justificativa in df_faturamento_geral_sem_robo.columns:
            justificativa_com_termo = df_faturamento_geral_sem_robo[col_justificativa].apply(contem_termo_excluido_liberados)
        else:
            justificativa_com_termo = False

        df_faturamento_geral_sem_robo['_status_excluido_liberados'] = status_vazio_ou_termo | justificativa_com_termo

        df_liberados = df_faturamento_geral_sem_robo[
            (df_faturamento_geral_sem_robo['Inserido_Amil'] == False) & 
            ((df_faturamento_geral_sem_robo['Tem_Pendencia_Setor'] == False) | (df_faturamento_geral_sem_robo['Especialidades Pendentes'] == 'Nenhuma pendência técnica apontada')) &
            (~df_faturamento_geral_sem_robo['_status_excluido_liberados'])
        ].copy().sort_values(by='valor_calculado', ascending=False)

        # Métricas globais
        total_pacientes_iw = len(df)
        inseridos_count = df_producao_limpa['Inserido_Amil'].sum()
        valor_total_todos_pacientes = df['valor_calculado'].sum()
        valor_total_pendencias_setores = df[df['Tem_Pendencia_Setor'] == True]['valor_calculado'].sum()
        total_pendentes_input_real = (df['Inserido_Amil'] == False).sum()
        
        # Volumetria do Robô baseada nas marcas internas do arquivo
        inputs_robo_total = 0
        inputs_manual_total = 0
        if col_justificativa in df.columns:
            inputs_robo_total = (df[col_justificativa].fillna('').str.strip() == "Operadora: Robô - Em analise").sum()
            inputs_manual_total = (df[col_justificativa].fillna('').str.strip() == "Operadora: Manual - Em analise").sum()
        total_inputs_calculados = inputs_robo_total + inputs_manual_total

        # --- CONFIGURAÇÃO LATERAL DE METAS (REQUISITO 14) ---
        with st.sidebar:
            st.markdown("### ⚙️ Configuração de Metas")
            st.session_state.meta_conclusao = st.number_input("Meta de Conclusão (%)", min_value=0.0, max_value=100.0, value=st.session_state.meta_conclusao)
            st.session_state.meta_pendencias = st.number_input("Meta Máxima de Pendências (Pacientes)", min_value=0, value=st.session_state.meta_pendencias)
            st.session_state.meta_automacao = st.number_input("Meta de Automação (%)", min_value=0.0, max_value=100.0, value=st.session_state.meta_automacao)
            st.session_state.meta_valor = st.number_input("Meta Máxima de Valor Pendente (R$)", min_value=0.0, value=st.session_state.meta_valor)
            horario_previsto = st.text_input("Horário previsto para conclusão", value="18:00")

        # --- IDENTIFICAÇÃO DO SETOR "VILÃO" (maior concentração financeira de pendência técnica) ---
        # Usa exatamente a MESMA base de atendimentos do gráfico "Distribuição Financeira Total Ativa"
        # da aba "Lista de Pendências" (Prontuário Pendente + OPS Pendente), para não divergir entre telas.
        lista_atendimentos_pendentes_globais = []
        if not df_prontuario.empty: lista_atendimentos_pendentes_globais.extend(df_prontuario[col_atendimento].tolist())
        if not df_ops.empty: lista_atendimentos_pendentes_globais.extend(df_ops[col_atendimento].tolist())

        setor_vilao = None
        valor_vilao = 0.0
        pct_vilao_do_total = 0.0
        if arquivos_setores and len(lista_atendimentos_pendentes_globais) > 0 and not df_s_consolidado.empty and 'setor_normalizado' in df_s_consolidado.columns:
            df_s_vilao = df_s_consolidado[df_s_consolidado[col_s_atend].isin(lista_atendimentos_pendentes_globais)].copy()
            df_s_vilao = df_s_vilao[
                (df_s_vilao['setor_normalizado'] != "Terapia Ocupacional") &
                (df_s_vilao[col_s_atend].isin(atendimentos_com_outras_pendencias))
            ]
            if not df_s_vilao.empty:
                df_valores_unicos_vilao = df[[col_atendimento, 'valor_calculado']].drop_duplicates()
                df_s_vilao_valores = pd.merge(df_s_vilao, df_valores_unicos_vilao, left_on=col_s_atend, right_on=col_atendimento, how='inner')
                df_s_vilao_valores = df_s_vilao_valores.drop_duplicates(subset=[col_s_atend, 'setor_normalizado'])
                df_ranking_setor_vilao = df_s_vilao_valores.groupby('setor_normalizado')['valor_calculado'].sum().reset_index().sort_values(by='valor_calculado', ascending=False)
                if not df_ranking_setor_vilao.empty:
                    linha_vilao = df_ranking_setor_vilao.iloc[0]
                    setor_vilao = linha_vilao['setor_normalizado']
                    valor_vilao = linha_vilao['valor_calculado']
                    # Percentual calculado sobre o mesmo total exibido no gráfico da Lista de Pendências
                    valor_total_grafico_pendencias = df_ranking_setor_vilao['valor_calculado'].sum()
                    pct_vilao_do_total = (valor_vilao / valor_total_grafico_pendencias * 100) if valor_total_grafico_pendencias > 0 else 0.0

        # --- RISCO DE NÃO CONCLUIR ATÉ O HORÁRIO ALVO (usa a mesma lógica de velocidade da Previsão Inteligente) ---
        risco_prazo = False
        mensagem_prazo = ""
        if len(st.session_state.historico_coletas_df) >= 2:
            try:
                h_df_semaforo = st.session_state.historico_coletas_df.copy()
                h_df_semaforo['timestamp'] = pd.to_datetime(h_df_semaforo['Data'] + ' ' + h_df_semaforo['Hora'], format='%d/%m/%Y %H:%M:%S')
                delta_tempo_sem = (h_df_semaforo['timestamp'].iloc[-1] - h_df_semaforo['timestamp'].iloc[0]).total_seconds() / 3600.0
                if delta_tempo_sem > 0:
                    pacientes_reduzidos_sem = h_df_semaforo['Pendentes'].iloc[0] - h_df_semaforo['Pendentes'].iloc[-1]
                    vel_pacientes_sem = pacientes_reduzidos_sem / delta_tempo_sem
                    if vel_pacientes_sem > 0:
                        horas_restantes_sem = total_pendentes_input_real / vel_pacientes_sem
                        horario_conclusao_estimado_sem = agora_brasil() + pd.Timedelta(hours=horas_restantes_sem)
                        try:
                            hora_alvo_sem, min_alvo_sem = map(int, horario_previsto.strip().split(":"))
                            horario_alvo_dt = agora_brasil().replace(hour=hora_alvo_sem, minute=min_alvo_sem, second=0, microsecond=0)
                            if horario_conclusao_estimado_sem > horario_alvo_dt:
                                risco_prazo = True
                                mensagem_prazo = f"⏱️ No ritmo atual, a conclusão está projetada para as {horario_conclusao_estimado_sem.strftime('%H:%M')} — depois do horário alvo ({horario_previsto})."
                            else:
                                mensagem_prazo = f"⏱️ No ritmo atual, a conclusão está projetada para as {horario_conclusao_estimado_sem.strftime('%H:%M')} — dentro do horário alvo ({horario_previsto})."
                        except Exception:
                            pass
                    else:
                        risco_prazo = True
                        mensagem_prazo = "⏱️ Ritmo de conclusão estagnado — nenhum avanço detectado entre as últimas coletas registradas."
            except Exception:
                pass

        # --- ABAS DO DASHBOARD ---
        aba1, aba2, aba3, aba4, aba5, aba_r, aba6, aba7 = st.tabs([
            "☀️ Histórico de Coletas & Produtividade", "👤 Gestão de Equipe", "🏥 Segmentação ID / AD", 
            "📋 Lista de Pendências", "🚀 Liberados para Input", "🤖 Liberados para o Robô",
            "🏠 Contrato RioHome (Manual)", "🚨 Alertas de Erro"
        ])
        
        with aba1:
            # --- 14. SEMÁFORO INTELIGENTE (RENDERIZADO NO TOPO) ---
            pct_conclusao_atual = (inseridos_count / total_pacientes_iw * 100) if total_pacientes_iw > 0 else 0.0
            pct_automacao_atual = (inputs_robo_total / total_inputs_calculados * 100) if total_inputs_calculados > 0 else 0.0
            
            # Lógica de Classificação das Cores do Alerta
            motivos_alerta = []
            if pct_conclusao_atual < st.session_state.meta_conclusao: motivos_alerta.append("Conclusão abaixo da meta")
            if total_pendentes_input_real > st.session_state.meta_pendencias: motivos_alerta.append("Volume de pendências acima do limite")
            if valor_total_pendencias_setores > st.session_state.meta_valor: motivos_alerta.append("Valor financeiro retido crítico")
            if risco_prazo: motivos_alerta.append(f"Risco de não concluir até o horário alvo ({horario_previsto})")
            
            if len(motivos_alerta) == 0:
                cor_semaforo = "#D4EDDA"
                borda_semaforo = "#28A745"
                texto_cor = "#155724"
                status_titulo = f"🟢 VERDE — {setor_vilao if setor_vilao else 'Sem pendências críticas'}"
                status_mensagem = "A prorrogação está evoluindo conforme o esperado."
            elif len(motivos_alerta) <= 2:
                cor_semaforo = "#FFF3CD"
                borda_semaforo = "#FFC107"
                texto_cor = "#856404"
                status_titulo = f"🟡 AMARELO — {setor_vilao if setor_vilao else 'Atenção necessária'}"
                status_mensagem = f"Alguns indicadores encontram-se abaixo da meta: {', '.join(motivos_alerta)}."
            else:
                cor_semaforo = "#F8D7DA"
                borda_semaforo = "#DC3545"
                texto_cor = "#721C24"
                status_titulo = f"🔴 VERMELHO — {setor_vilao if setor_vilao else 'Operação crítica'}"
                status_mensagem = "Recomenda-se atuação imediata da equipe! Multiplos gargalos de retenção técnica ativos."
                
            # Determinação da Tendência Baseada no Histórico de Sessão
            tendencia_txt = "➡️ Estável"
            if len(st.session_state.historico_coletas_df) >= 2:
                ultimo_p = st.session_state.historico_coletas_df.iloc[-1]["Pendentes"]
                penultimo_p = st.session_state.historico_coletas_df.iloc[-2]["Pendentes"]
                if ultimo_p < penultimo_p: tendencia_txt = "📈 Melhorando (Reduzindo bloqueos)"
                elif ultimo_p > penultimo_p: tendencia_txt = "📉 Piorando (Acúmulo de travas)"

            # Linha extra do card: identifica o setor "vilão" (maior concentração financeira de pendência)
            linha_vilao_html = ""
            if setor_vilao:
                linha_vilao_html = f"<br><small>🎯 <b>Principal gargalo:</b> {setor_vilao} — R$ {valor_vilao:,.2f} ({pct_vilao_do_total:.1f}% do valor total pendente)</small>"

            # Linha extra do card: projeção de conclusão frente ao horário alvo
            linha_prazo_html = ""
            if mensagem_prazo:
                linha_prazo_html = f"<br><small>{mensagem_prazo}</small>"

            st.markdown(f"""
                <div class="semaforo-card" style="background-color: {cor_semaforo}; border-left: 8px solid {borda_semaforo}; color: {texto_cor};">
                    <h4 style='margin:0 0 5px 0; font-weight:800;'>🚦 Situação das Pendências dos Setores: {status_titulo}</h4>
                    <p style='margin:0 0 8px 0; font-size:14px;'>{status_mensagem}</p>
                    <small><b>Tendência Geral Calculada:</b> {tendencia_txt} | <b>Horário Alvo:</b> {horario_previsto}</small>
                    {linha_vilao_html}
                    {linha_prazo_html}
                </div>
            """, unsafe_allow_html=True)
            
            # --- 1. CARDS DE INDICADORES ---
            st.markdown("### 📌 Indicadores Estruturados da Coleta Ativa")
            card1, card2, card3, card4, card5 = st.columns(5)
            card1.metric("Total de Pacientes", f"{total_pacientes_iw}")
            card2.metric("Quantidade de Pendentes", f"{total_pendentes_input_real}")
            card3.metric("Percentual de Conclusão", f"{pct_conclusao_atual:.2f}%", delta=f"{inseridos_count} imputados", delta_color="off")
            card4.metric("Valor Total Pendente", f"R$ {valor_total_pendencias_setores:,.2f}")
            
            # Contagem dinâmica de colaboradores qualificados
            cont_colaboradores_cards = 0
            if col_responsavel in df.columns:
                colab_filtrados_cards = [c for c in df[col_responsavel].unique() if str(c).strip() != '' and not any(exc in str(c).upper() for exc in ["IMPLANTAÇÃO", "IMPLANTACAO", "PRORROGAÇÃO", "PRORROGACAO", "OPERAÇÃO", "OPERACAO"])]
                cont_colaboradores_cards = len(colab_filtrados_cards)
            card5.metric("Quantidade de Colaboradores", f"{cont_colaboradores_cards}")
            
            card6, card7, card8, card9, card10 = st.columns(5)
            card6.metric("Total Pacientes AD", f"{df['Is_AD'].sum()}")
            card7.metric("Total Pacientes ID", f"{df['Is_ID'].sum()}")
            card8.metric("Imputs pelo Robô", f"{inputs_robo_total}")
            card9.metric("Imputs Manualmente", f"{inputs_manual_total}")
            card10.metric("Última Atualização", agora_brasil().strftime("%d/%m/%Y %H:%M"))
            
            # --- BOTÃO DE GERAÇÃO PARA O HISTÓRICO ---
            st.markdown("---")
            ciclo_opcao = st.selectbox("Selecione o Ciclo de Prorrogação para o Registro Histórico:", ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Extraordinário"], key="sel_ciclo_historico")
            
            if st.button("📊 Gerar Resumo para Histórico", key="btn_historico_avancado"):
                data_atual = datetime.now().strftime("%d/%m/%Y")
                hora_atual = datetime.now().strftime("%H:%M:%S")
                
                nova_linha = {
                    "Data": data_atual, "Hora": hora_atual, "Ciclo": ciclo_opcao,
                    "Total da Base": total_pacientes_iw, "Pendentes": total_pendentes_input_real,
                    "Robô": inputs_robo_total, "Manual": inputs_manual_total,
                    "Valor Pendente": round(valor_total_pendencias_setores, 2),
                    "Percentual de Conclusão": round(pct_conclusao_atual, 2)
                }
                st.session_state.historico_coletas_df = pd.concat([st.session_state.historico_coletas_df, pd.DataFrame([nova_linha])], ignore_index=True)
                st.success("✨ Nova linha registrada com sucesso no histórico da sessão!")

            # --- 15. PREVISÃO INTELIGENTE DE CONCLUSÃO ---
            if len(st.session_state.historico_coletas_df) >= 2:
                st.markdown("### ⏱️ Previsão Inteligente de Conclusão")
                try:
                    h_df = st.session_state.historico_coletas_df.copy()
                    # Mapeamento do tempo aproximado de delta entre coletas
                    h_df['timestamp'] = pd.to_datetime(h_df['Data'] + ' ' + h_df['Hora'], format='%d/%m/%Y %H:%M:%S')
                    delta_tempo = (h_df['timestamp'].iloc[-1] - h_df['timestamp'].iloc[0]).total_seconds() / 3600.0
                    
                    if delta_tempo > 0:
                        pacientes_reduzidos = h_df['Pendentes'].iloc[0] - h_df['Pendentes'].iloc[-1]
                        valor_reduzido = h_df['Valor Pendente'].iloc[0] - h_df['Valor Pendente'].iloc[-1]
                        
                        vel_pacientes = pacientes_reduzidos / delta_tempo
                        vel_financeira = valor_reduzido / delta_tempo
                        
                        restantes_p = h_df['Pendentes'].iloc[-1]
                        if vel_pacientes > 0:
                            horas_restantes = restantes_p / vel_pacientes
                            tempo_restante_str = f"{int(horas_restantes)}h {int((horas_restantes % 1) * 60)}min"
                            horario_conclusao_estimado = datetime.now() + pd.Timedelta(hours=horas_restantes)
                            horario_conclusao_str = horario_conclusao_estimado.strftime("%H:%M")
                        else:
                            vel_pacientes = 0
                            tempo_restante_str = "Indeterminado"
                            horario_conclusao_str = "Estagnado"
                        
                        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
                        col_p1.metric("Velocidade Atual", f"{int(vel_pacientes)} pac/hora")
                        col_p2.metric("Redução Financeira", f"R$ {vel_financeira:,.2f}/hora")
                        col_p3.metric("Horário Previsto de Conclusão", horario_conclusao_str)
                        col_p4.metric("Tempo Restante Estimado", tempo_restante_str)
                except Exception as e:
                    st.info("Aguardando mais variações cronológicas de registros de coletas para firmar velocidades.")

            # --- GRÁFICOS DE PRODUTIVIDADE OPERACIONAL (REQUISITOS 3, 4, 5, 6) ---
            st.markdown("---")
            st.markdown("### 📊 Gráficos de Produtividade e Carga de Trabalho")
            
            # Coleta de dados dos colaboradores para os rankings
            linhas_produtividade = []
            if col_responsavel in df.columns:
                colaboradores_unicos = df[df[col_responsavel].fillna('').str.strip() != ''][col_responsavel].unique()
                excecoes_setor = ["IMPLANTAÇÃO", "IMPLANTACAO", "PRORROGAÇÃO", "PRORROGACAO", "OPERAÇÃO", "OPERACAO"]
                for colab in colaboradores_unicos:
                    if any(exc in str(colab).upper() for exc in excecoes_setor): continue
                    df_c = df[df[col_responsavel] == colab]
                    linhas_produtividade.append({
                        "Colaborador": colab,
                        "Quantidade de Pacientes": len(df_c),
                        "Valor Total": df_c['valor_calculado'].sum()
                    })
            
            df_prod_graficos = pd.DataFrame(linhas_produtividade) if linhas_produtividade else pd.DataFrame(columns=["Colaborador", "Quantidade de Pacientes", "Valor Total"])
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("#### 👤 Carga de Trabalho: Ranking dos Colaboradores")
                if not df_prod_graficos.empty:
                    fig_rank_p = px.bar(df_prod_graficos.sort_values(by="Quantidade de Pacientes", ascending=True), y="Colaborador", x="Quantidade de Pacientes", orientation='h', color_discrete_sequence=['#C07C20'])
                    fig_rank_p.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_rank_p, use_container_width=True)
                else: st.info("Sem dados de colaboradores.")
                
            with col_g2:
                st.markdown("#### 💰 Concentração Financeira por Colaborador")
                if not df_prod_graficos.empty:
                    fig_rank_f = px.bar(df_prod_graficos.sort_values(by="Valor Total", ascending=True), y="Colaborador", x="Valor Total", orientation='h', color_discrete_sequence=['#5C1220'])
                    fig_rank_f.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_rank_f, use_container_width=True)
                else: st.info("Sem dados financeiros por colaborador.")
                
            col_g3, col_g4 = st.columns(2)
            with col_g3:
                st.markdown("#### 🤖 Comparativo Nível de Automação (Robô x Manual)")
                df_robo_man = pd.DataFrame({
                    "Método de Input": ["Robô", "Manual"],
                    "Quantidade de Imputs": [inputs_robo_total, inputs_manual_total]
                })
                fig_rm = px.bar(df_robo_man, x="Método de Input", y="Quantidade de Imputs", color="Método de Input", color_discrete_map={"Robô": "#C07C20", "Manual": "#5C1220"})
                fig_rm.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_rm, use_container_width=True)
                
            with col_g4:
                st.markdown("#### 🏥 Distribuição de Modelos (AD x ID)")
                df_ad_id_pizza = pd.DataFrame({
                    "Segmento": ["Pacientes AD", "Pacientes ID"],
                    "Total": [df['Is_AD'].sum(), df['Is_ID'].sum()]
                })
                fig_pizza = px.pie(df_ad_id_pizza, names="Segmento", values="Total", hole=0.4, color_discrete_sequence=['#5C1220', '#C07C20'])
                fig_pizza.update_layout(margin=dict(t=20, b=20, l=20, r=20))
                st.plotly_chart(fig_pizza, use_container_width=True)

            # --- RELATÓRIO ANALÍTICO DA EQUIPE COM PERCENTUAIS (REQUISITO 2) ---
            st.markdown("---")
            st.markdown("### 👤 Relatório Analítico Complementar da Equipe")
            if col_responsavel in df.columns and not df_prod_graficos.empty:
                df_analitico_completo = []
                for _, r_gc in df_prod_graficos.iterrows():
                    c_name = r_gc["Colaborador"]
                    df_c_filtro = df[df[col_responsavel] == c_name]
                    
                    p_id = df_c_filtro['Is_ID'].sum()
                    p_ad = df_c_filtro['Is_AD'].sum()
                    
                    imp_r = (df_c_filtro[col_justificativa].fillna('').str.strip() == "Operadora: Robô - Em analise").sum() if col_justificativa in df.columns else 0
                    imp_m = (df_c_filtro[col_justificativa].fillna('').str.strip() == "Operadora: Manual - Em analise").sum() if col_justificativa in df.columns else 0
                    soma_inputs = imp_r + imp_m
                    
                    pct_base = (r_gc["Quantidade de Pacientes"] / total_pacientes_iw * 100) if total_pacientes_iw > 0 else 0.0
                    pct_auto = (imp_r / soma_inputs * 100) if soma_inputs > 0 else 0.0
                    pct_manu = (imp_m / soma_inputs * 100) if soma_inputs > 0 else 0.0
                    
                    df_analitico_completo.append({
                        "Colaborador": c_name,
                        "Pacientes ID": p_id,
                        "Pacientes AD": p_ad,
                        "Imputs Robô": imp_r,
                        "Imputs Manuais": imp_m,
                        "Total Pacientes": r_gc["Quantidade de Pacientes"],
                        "Percentual da Base (%)": round(pct_base, 2),
                        "Percentual Automação (%)": round(pct_auto, 2),
                        "Percentual Manual (%)": round(pct_manu, 2),
                        "Valor Total": r_gc["Valor Total"]
                    })
                df_grid_re2 = pd.DataFrame(df_analitico_completo)
                st.dataframe(df_grid_re2.style.format({
                    'Valor Total': 'R$ {:,.2f}',
                    'Percentual da Base (%)': '{:.2f}%',
                    'Percentual Automação (%)': '{:.2f}%',
                    'Percentual Manual (%)': '{:.2f}%'
                }), use_container_width=True, hide_index=True)

            # --- 7. HISTÓRICO DAS COLETAS (TABELA ACUMULADA) ---
            st.markdown("---")
            st.markdown("### 📋 Histórico das Coletas Gravadas")
            
            # Filtros unificados do histórico (Requisito 11)
            if not st.session_state.historico_coletas_df.empty:
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1: f_ciclo = st.multiselect("Filtrar Ciclo:", options=st.session_state.historico_coletas_df["Ciclo"].unique(), default=st.session_state.historico_coletas_df["Ciclo"].unique())
                with col_f2: f_data = st.multiselect("Filtrar Data:", options=st.session_state.historico_coletas_df["Data"].unique(), default=st.session_state.historico_coletas_df["Data"].unique())
                with col_f3: f_hora = st.multiselect("Filtrar Hora da Coleta:", options=st.session_state.historico_coletas_df["Hora"].unique(), default=st.session_state.historico_coletas_df["Hora"].unique())
                
                df_historico_filtrado = st.session_state.historico_coletas_df[
                    (st.session_state.historico_coletas_df["Ciclo"].isin(f_ciclo)) &
                    (st.session_state.historico_coletas_df["Data"].isin(f_data)) &
                    (st.session_state.historico_coletas_df["Hora"].isin(f_hora))
                ]
                st.dataframe(df_historico_filtrado, use_container_width=True, hide_index=True)
                
                # --- GRÁFICOS HISTÓRICOS DE EVOLUÇÃO (REQUISITOS 8, 9, 10) ---
                df_historico_filtrado['Data_Hora_Eixo'] = df_historico_filtrado['Data'] + " " + df_historico_filtrado['Hora']
                
                st.markdown("#### 📈 Linhas de Tendência Histórica")
                col_lh1, col_lh2, col_lh3 = st.columns(3)
                with col_lh1:
                    st.markdown("**Evolução das Pendências**")
                    fig_lh1 = px.line(df_historico_filtrado, x="Data_Hora_Eixo", y="Pendentes", markers=True, color_discrete_sequence=['#5C1220'])
                    st.plotly_chart(fig_lh1, use_container_width=True)
                with col_lh2:
                    st.markdown("**Evolução do Valor Pendente**")
                    fig_lh2 = px.line(df_historico_filtrado, x="Data_Hora_Eixo", y="Valor Pendente", markers=True, color_discrete_sequence=['#C07C20'])
                    st.plotly_chart(fig_lh2, use_container_width=True)
                with col_lh3:
                    st.markdown("**Evolução da Conclusão (%)**")
                    fig_lh3 = px.line(df_historico_filtrado, x="Data_Hora_Eixo", y="Percentual de Conclusão", markers=True, color_discrete_sequence=['#28A745'])
                    st.plotly_chart(fig_lh3, use_container_width=True)
            else:
                st.info("Utilize o botão acima para registrar a primeira linha de coleta e disparar os gráficos evolutivos de linha.")

            # --- 13. INSIGHTS AUTOMÁTICOS DA COLETA & RECOMENDAÇÕES ---
            st.markdown("---")
            st.markdown("### 📊 Insights Automáticos da Coleta Ativa")
            
            # Análise automatizada com os dados reais
            total_ad_ins = df['Is_AD'].sum()
            total_id_ins = df['Is_ID'].sum()
            soma_ad_id = total_ad_ins + total_id_ins
            pct_ad_ins = (total_ad_ins / soma_ad_id * 100) if soma_ad_id > 0 else 0.0
            pct_id_ins = (total_id_ins / soma_ad_id * 100) if soma_ad_id > 0 else 0.0
            
            col_ins1, col_ins2 = st.columns(2)
            with col_ins1:
                st.markdown("""<div class="insight-card"><b>🤖 Automação de Carga:</b><br>"""
                            f"O Robô realizou {pct_automacao_atual:.1f}% dos inputs avaliados de forma ativa no cruzamento geral do banco de dados.</div>", unsafe_allow_html=True)
                
                st.markdown("""<div class="insight-card"><b>👨‍⚕️ Distribuição de Perfil Clínico (AD x ID):</b><br>"""
                            f"A base possui {pct_ad_ins:.1f}% de pacientes em Atenção Domiciliar (AD) e {pct_id_ins:.1f}% de pacientes em Internação Domiciliar (ID).</div>", unsafe_allow_html=True)
                
                st.markdown("""<div class="insight-card"><b>📊 Situação Atual de Faturamento:</b><br>"""
                            f"A base encontra-se {pct_conclusao_atual:.2f}% concluída, restando {total_pendentes_input_real} pacientes pendentes de digitação final.</div>", unsafe_allow_html=True)
            
            with col_ins2:
                if not df_prod_graficos.empty:
                    max_colab = df_prod_graficos.sort_values(by="Quantidade de Pacientes", ascending=False).iloc[0]
                    min_colab = df_prod_graficos.sort_values(by="Quantidade de Pacientes", ascending=True).iloc[0]
                    max_val_colab = df_prod_graficos.sort_values(by="Valor Total", ascending=False).iloc[0]
                    
                    pct_max_carga = (max_colab['Quantidade de Pacientes'] / total_pacientes_iw * 100) if total_pacientes_iw > 0 else 0.0
                    
                    st.markdown(f"""<div class="insight-card"><b>👥 Distribuição Operacional de Equipe:</b><br>
                                <b>{max_colab['Colaborador']}</b> possui a maior carga de faturamento da equipe, representando {pct_max_carga:.1f}% da base. 
                                Por outro lado, <b>{min_colab['Colaborador']}</b> concentra a menor carga atual de auditoria.</div>""", unsafe_allow_html=True)
                                
                    st.markdown(f"""<div class="insight-card"><b>💰 Concentração por Maior Valor Crítico:</b><br>
                                O colaborador <b>{max_val_colab['Colaborador']}</b> concentra a maior criticidade financeira absoluta, totalizando <b>R$ {max_val_colab['Valor Total']:,.2f}</b> sob sua responsabilidade direta no IW.</div>""", unsafe_allow_html=True)
                else:
                    st.info("Carregue uma base com auditores definidos no IW para extrair volumes individuais de liderança.")

            # Insights de Delta Comparativo Histórico
            if len(st.session_state.historico_coletas_df) >= 2:
                st.markdown("#### 📈 Variações em Relação à Coleta Anterior")
                ultimo_reg = st.session_state.historico_coletas_df.iloc[-1]
                penultimo_reg = st.session_state.historico_coletas_df.iloc[-2]
                
                dif_pacientes = int(penultimo_reg["Pendentes"] - ultimo_reg["Pendentes"])
                dif_valor = float(penultimo_reg["Valor Pendente"] - ultimo_reg["Valor Pendente"])
                
                col_h_ins1, col_h_ins2 = st.columns(2)
                with col_h_ins1:
                    if dif_pacientes >= 0: st.success(f"📈 Desde a última coleta registrada, foram concluídos ou liberados {dif_pacientes} pacientes.")
                    else: st.warning(f"⚠️ Houve um incremento de {abs(dif_pacientes)} novos pacientes travados na fila de conferência.")
                with col_h_ins2:
                    if dif_valor >= 0: st.success(f"💸 O valor pendente total foi reduzido em R$ {dif_valor:,.2f} em relação ao último ponto.")
                    else: st.warning(f"⚠️ O montante financeiro retido cresceu R$ {abs(dif_valor):,.2f} com novas pendências técnicas.")

            # --- RECOMENDAÇÕES AUTOMÁTICAS ---
            st.markdown("#### 💡 Diretrizes Operacionais Recomendadas")
            if not df_prod_graficos.empty:
                max_p = df_prod_graficos["Quantidade de Pacientes"].max()
                min_p = df_prod_graficos["Quantidade de Pacientes"].min()
                if (max_p - min_p) > 15:
                    st.warning("⚠️ **Equilíbrio de Carga:** Identificada alta disparidade na distribuição de pacientes. Recomenda-se redistribuir as pastas operacionais dos colaboradores mais sobrecarregados.")
            if pct_automacao_atual < 50.0:
                st.info("🤖 **Incentivo Tecnológico:** O nível de faturamento automatizado está abaixo do ideal. Monitore as travas do Robô e incentive a migração de lotes elegíveis.")
            if valor_total_pendencias_setores > st.session_state.meta_valor:
                st.error("🚨 **Força Tarefa Financeira:** O valor financeiro retido por pendência técnica estrapolou os limites de segurança. Priorize os pacientes de maior valor bruto com as coordenações das especialidades.")

        with aba2:
            st.markdown("### 👤 Relatório Analítico de Produtividade da Equipe")
            
            if col_responsavel in df.columns:
                colaboradores_unicos = df[df[col_responsavel].fillna('').str.strip() != ''][col_responsavel].unique()
                linhas_gestao = []
                excecoes_setor = ["IMPLANTAÇÃO", "IMPLANTACAO", "PRORROGAÇÃO", "PRORROGACAO", "OPERAÇÃO", "OPERACAO"]
                
                for colab in colaboradores_unicos:
                    colab_upper = str(colab).strip().upper()
                    if any(exc in colab_upper for exc in excecoes_setor) or colab_upper == "":
                        continue
                    
                    df_filtrado_colab = df[df[col_responsavel] == colab]
                    df_contagem_id_ad = df_filtrado_colab[
                        ~df_filtrado_colab[col_classificacao].fillna('').str.strip().str.upper().isin(excecoes_setor)
                    ]
                    
                    paci_id = df_contagem_id_ad['Is_ID'].sum()
                    paci_ad = df_contagem_id_ad['Is_AD'].sum()
                    
                    inputs_robo = 0
                    if col_justificativa in df_filtrado_colab.columns:
                        inputs_robo = (df_filtrado_colab[col_justificativa].fillna('').str.strip() == "Operadora: Robô - Em analise").sum()
                        
                    inputs_manuais = 0
                    if col_justificativa in df_filtrado_colab.columns:
                        inputs_manuais = (df_filtrado_colab[col_justificativa].fillna('').str.strip() == "Operadora: Manual - Em analise").sum()
                    
                    total_paci = len(df_filtrado_colab)
                    valor_total = df_filtrado_colab['valor_calculado'].sum()
                    
                    linhas_gestao.append({
                        "Colaborador": colab,
                        "Pacientes ID": paci_id,
                        "Pacientes AD": paci_ad,
                        "Imputs feitos pelo Robô": inputs_robo,
                        "Imputs Manuais": inputs_manuais,
                        "Quantitativo Total de Pacientes": total_paci,
                        "Valor Total dos Pacientes": valor_total
                    })
                
                if linhas_gestao:
                    df_gestao_final = pd.DataFrame(linhas_gestao)
                    df_gestao_final = df_gestao_final[[
                        "Colaborador", "Pacientes ID", "Pacientes AD", 
                        "Imputs feitos pelo Robô", "Imputs Manuais", 
                        "Quantitativo Total de Pacientes", "Valor Total dos Pacientes"
                    ]]
                    st.dataframe(df_gestao_final.style.format({'Valor Total dos Pacientes': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum colaborador elegível localizado com os parâmetros aplicados.")

        with aba3:
            st.markdown("### Análise do Modelo de Atendimento Solar (ID vs AD)")
            df_id_ad = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Inserido_Amil'] == False].groupby('Tipo_Atendimento').agg(Quantidade=('nome do paciente', 'count'), Valor_Total=('valor_calculado', 'sum')).reset_index()
            st.dataframe(df_id_ad.style.format({'Valor_Total': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### 📄 Detalhamento dos Pacientes Pendentes por Tipo de Atendimento")

            df_id_ad_detalhe_base = df_faturamento_geral_sem_robo[df_faturamento_geral_sem_robo['Inserido_Amil'] == False].copy()

            tab_seg_ad, tab_seg_id = st.tabs(["🏠 AD (Atenção Domiciliar)", "🏥 ID (Internação Domiciliar)"])

            with tab_seg_ad:
                df_ad_detalhe = df_id_ad_detalhe_base[df_id_ad_detalhe_base['Is_AD'] == True].copy()
                if not df_ad_detalhe.empty:
                    df_ad_view = df_ad_detalhe[[col_atendimento, 'nome do paciente', col_responsavel, 'valor_calculado']].copy()
                    df_ad_view.columns = ['Nº Atendimento', 'Paciente', 'Responsável', 'Valor a Cobrar (R$)']
                    df_ad_view = df_ad_view.sort_values(by='Valor a Cobrar (R$)', ascending=False)
                    st.markdown(f"**Total: {len(df_ad_view)} pacientes | Valor: R$ {df_ad_view['Valor a Cobrar (R$)'].sum():,.2f}**")
                    st.dataframe(df_ad_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum paciente AD pendente encontrado.")

            with tab_seg_id:
                df_id_detalhe = df_id_ad_detalhe_base[df_id_ad_detalhe_base['Is_ID'] == True].copy()
                if not df_id_detalhe.empty:
                    df_id_view = df_id_detalhe[[col_atendimento, 'nome do paciente', col_responsavel, 'valor_calculado']].copy()
                    df_id_view.columns = ['Nº Atendimento', 'Paciente', 'Responsável', 'Valor a Cobrar (R$)']
                    df_id_view = df_id_view.sort_values(by='Valor a Cobrar (R$)', ascending=False)
                    st.markdown(f"**Total: {len(df_id_view)} pacientes | Valor: R$ {df_id_view['Valor a Cobrar (R$)'].sum():,.2f}**")
                    st.dataframe(df_id_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum paciente ID pendente encontrado.")

        with aba4:
            st.markdown("### 📋 Lista de Pendências Ativas por Orçamento do Paciente")
            
            lista_atendimentos_visiveis = []
            if not df_prontuario.empty: lista_atendimentos_visiveis.extend(df_prontuario[col_atendimento].tolist())
            if not df_ops.empty: lista_atendimentos_visiveis.extend(df_ops[col_atendimento].tolist())
                
            if arquivos_setores and len(lista_atendimentos_visiveis) > 0 and not df_s_consolidado.empty:
                df_s_filtrado_grafico = df_s_consolidado[df_s_consolidado[col_s_atend].isin(lista_atendimentos_visiveis)].copy()
                df_s_filtrado_grafico = df_s_filtrado_grafico[(df_s_filtrado_grafico['setor_normalizado'] != "Terapia Ocupacional") & (df_s_filtrado_grafico[col_s_atend].isin(atendimentos_com_outras_pendencias))]
                
                df_valores_unicos = df[[col_atendimento, 'valor_calculado']].drop_duplicates()
                df_grafico_final = pd.merge(df_s_filtrado_grafico, df_valores_unicos, left_on=col_s_atend, right_on=col_atendimento, how='inner')
                df_grafico_final = df_grafico_final.drop_duplicates(subset=[col_s_atend, 'setor_normalizado'])
                
                df_grafico_pizza = df_grafico_final.groupby('setor_normalizado')['valor_calculado'].sum().reset_index()
                df_grafico_pizza.columns = ['Setor Técnico', 'Valor Total Retido']
                df_grafico_pizza = df_grafico_pizza[df_grafico_pizza['Valor Total Retido'] > 0].sort_values(by="Valor Total Retido", ascending=False)
                
                if not df_grafico_pizza.empty:
                    st.markdown("#### 📊 Distribuição Financeira Total Ativa")
                    fig_valores = px.bar(df_grafico_pizza, x='Setor Técnico', y='Valor Total Retido', color='Valor Total Retido', color_continuous_scale='Oryel', labels={'Valor Total Retido': 'Valor Retido (R$)'})
                    fig_valores.update_traces(texttemplate='R$ %{y:,.2f}', textposition='outside')
                    fig_valores.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=10, l=10, r=10), yaxis=dict(tickprefix="R$ ", tickformat=",.2f"))
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
                        df_o_view.to_excel(writer, sheet_name='OPS Pendente', index=False)
                    st.download_button(label="📥 Baixar Planilha Estruturada: Pendências da Operação", data=buffer_o.getvalue(), file_name="ops_pendente_estruturado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    st.dataframe(df_o_view.style.format({'Valor do Paciente (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                else: st.info("Nenhuma pendência de OPS activa.")

        with aba5:
            st.markdown("### 🚀 Pacientes Liberados (Sem Pendências nos Setores)")
            if not arquivos_setores:
                st.warning("⚠️ Para ver quem está liberado, carregue a planilha de Setores no campo de upload.")
            else:
                st.markdown(f"**🔥 Total Prontos para Input: {len(df_liberados)} | Valor de Giro Rápido: R$ {df_liberados['valor_calculado'].sum():,.2f}**")

                # Campo "Justificativa Pendência": exibição informativa exclusiva desta planilha,
                # copiado integralmente da coluna do IW, sem alterações, resumos ou interpretações.
                colunas_liberados = [col_atendimento, 'id orçam.', 'nome do paciente', 'Tipo_Atendimento']
                nomes_colunas_liberados = ['Nº Atendimento', 'ID Orçamento', 'Paciente', 'Tipo Atendimento']

                if col_justificativa in df_liberados.columns:
                    colunas_liberados.append(col_justificativa)
                    nomes_colunas_liberados.append('Justificativa Pendência')

                colunas_liberados.extend([col_responsavel, 'valor_calculado'])
                nomes_colunas_liberados.extend(['Responsável', 'Valor a Cobrar (R$)'])

                df_liberados_clean_excel = df_liberados[colunas_liberados].copy()
                df_liberados_clean_excel.columns = nomes_colunas_liberados
                
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
