import streamlit as st
import pandas as pd
import re

# Configuração padrão da página
st.set_page_config(page_title="Dashboard Prorrogações Amil", page_icon="☀️", layout="wide")

# CSS Avançado Dinâmico para Modo Claro/Escuro
st.markdown("""
    <style>
    @media (prefers-color-scheme: light) {
        .main-title { color: #4A148C !important; }
        .subtitle { color: #555555 !important; }
        div[data-testid="stMetric"] { background-color: #F8F9FA !important; border: 1px solid #EAEAEA !important; }
        div[data-testid="stMetricLabel"] { color: #4A148C !important; }
        div[data-testid="stMetricValue"] { color: #1A1A1A !important; }
    }
    @media (prefers-color-scheme: dark) {
        .main-title { color: #BA68C8 !important; }
        .subtitle { color: #B0BEC5 !important; }
        div[data-testid="stMetric"] { background-color: #1E1E1E !important; border: 1px solid #333333 !important; }
        div[data-testid="stMetricLabel"] { color: #BA68C8 !important; }
        div[data-testid="stMetricValue"] { color: #FFFFFF !important; }
    }
    .header-container { display: flex; align-items: center; gap: 15px; margin-bottom: 10px; }
    .logo-img { max-height: 60px; width: auto; }
    .main-title { font-size: 32px; font-weight: 800; font-family: sans-serif; margin: 0; }
    .solar-accent { color: #FFB300 !important; }
    .subtitle { font-size: 15px; margin-top: 5px; margin-bottom: 25px; }
    div[data-testid="stMetricLabel"] { font-weight: 700 !important; font-size: 13px !important; text-transform: uppercase !important; }
    div[data-testid="stMetricValue"] { font-weight: 700 !important; font-size: 28px !important; }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
LINK_DA_LOGO = "COLOQUE_O_LINK_DA_SUA_LOGO_AQUI" 

if LINK_DA_LOGO != "COLOQUE_O_LINK_DA_SUA_LOGO_AQUI":
    st.markdown(f"""
        <div class="header-container">
            <img src="{LINK_DA_LOGO}" class="logo-img">
            <p class="main-title">Dashboard Prorrogações <span class="solar-accent">Solar Cuidados</span></p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<p class="main-title">☀️ Dashboard Prorrogações <span class="solar-accent">Solar Cuidados</span></p>', unsafe_allow_html=True)

st.markdown('<p class="subtitle">Análise operacional consolidada de prorrogações Amil IW, pendências multidisciplinares e volumetria ID/AD.</p>', unsafe_allow_html=True)

# --- ÁREA DE UPLOAD (MÚLTIPLOS ARQUIVOS) ---
col_up1, col_up2 = st.columns(2)
with col_up1:
    arquivos_amil = st.file_uploader("1️⃣ Selecione uma ou mais planilhas PRINCIPAIS do IW (.csv)", type=["csv", "xlsx"], accept_multiple_files=True)
with col_up2:
    arquivos_setores = st.file_uploader("2️⃣ [Opcional] Selecione uma ou mais planilhas de PENDÊNCIAS POR SETOR (.csv)", type=["csv", "xlsx"], accept_multiple_files=True)

# Só executa se pelo menos um arquivo principal for enviado
if arquivos_amil:
    try:
        # --- LEITURA E CONSOLIDACÃO ---
        lista_dfs_amil = []
        for arq in arquivos_amil:
            if arq.name.endswith('.csv'):
                try:
                    df_temp = pd.read_csv(arq, sep=';', encoding='utf-8')
                except UnicodeDecodeError:
                    arq.seek(0)
                    df_temp = pd.read_csv(arq, sep=';', encoding='iso-8859-1')
                if df_temp.shape[1] <= 1:
                    arq.seek(0)
                    try:
                        df_temp = pd.read_csv(arq, sep=',', encoding='utf-8')
                    except UnicodeDecodeError:
                        arq.seek(0)
                        df_temp = pd.read_csv(arq, sep=',', encoding='iso-8859-1')
            else:
                df_temp = pd.read_excel(arq)
            
            df_temp.columns = df_temp.columns.str.strip()
            lista_dfs_amil.append(df_temp)
        
        df = pd.concat(lista_dfs_amil, ignore_index=True)
        
        # --- VERIFICAÇÃO DE COLUNAS ---
        colunas_obrigatorias = ['Nr. Matricula', 'Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Pessoa Resp Aut', 'Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Valor a Cobrar', 'Classific. Atendimento']
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"❌ O combo de planilhas 1 está faltando as colunas essenciais: {colunas_faltantes}.")
        else:
            for c in ['Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Nr. Matricula', 'Pessoa Resp Aut', 'Classific. Atendimento']:
                df[c] = df[c].fillna('').astype(str).str.strip()
            
            df['Nr. Atendimento'] = df['Nr. Atendimento'].astype(str).str.strip()
            
            def converter_moeda_br(valor):
                valor_str = str(valor).strip()
                if not valor_str or valor_str.lower() == 'nan': return 0.0
                if re.search(r',\d{2}$', valor_str):
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                else:
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                try: return float(valor_str)
                except: return 0.0

            df['Valor a Cobrar'] = df['Valor a Cobrar'].apply(converter_moeda_br)
            
            df['Tipo_Atendimento'] = df['Classific. Atendimento'].apply(
                lambda x: 'ID (Internação Domiciliar)' if x.startswith('ID') else ('AD (Atenção Domiciliar)' if x.startswith('AD') else 'Outros')
            )
            
            # --- CONSOLIDACÃO DAS PLANILHAS DE SETORES ---
            df_s_consolidado = None
            setores_agrupados = None
            
            if arquivos_setores:
                try:
                    lista_dfs_setores = []
                    for arq_s in arquivos_setores:
                        if arq_s.name.endswith('.csv'):
                            try:
                                df_s_temp = pd.read_csv(arq_s, sep=';', encoding='utf-8')
                            except UnicodeDecodeError:
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
                    st.warning(f"⚠️ Não foi possível processar os arquivos de setores. Erro: {e_setor}")

            if setores_agrupados is not None:
                df = pd.merge(df, setores_agrupados, on='Nr. Atendimento', how='left')
                df['Especialidades Pendentes'] = df['Especialidades Pendentes'].fillna('Nenhuma pendência técnica apontada')
            else:
                df['Especialidades Pendentes'] = 'Carregue a planilha 2 para abrir os setores'

            # Métricas
            guia_valida_numerica = df['Nº Guia Solicitação (TISS)'].str.isnumeric()
            df['Inserido_Amil'] = (guia_valida_numerica) | (df['Senha Aprovação'] != '') | (df['Status Aut Orç'] == 'Autorizado')
            
            total_pacientes = len(df)
            inseridos = df['Inserido_Amil'].sum()
            faltam = total_pacientes - inseridos
            
            df_prontuario = df[df['Status Aut Orç'] == 'Prontuário Pendente'].sort_values(by='Valor a Cobrar', ascending=False)
            df_ops = df[df['Status Aut Orç'] == 'OPS Pendente'].sort_values(by='Valor a Cobrar', ascending=False)
            
            tam_matriculas = df['Nr. Matricula'].str.len()
            erro_matricula = (tam_matriculas == 0) | (~tam_matriculas.isin([8, 9]))
            erro_vinculo = df['Nr. Atendimento'].isna() | df['ID Orçam.'].isna()
            df['Possui_Erro'] = erro_matricula | erro_vinculo
            pacientes_com_erro = df[df['Possui_Erro'] == True][['Nr. Atendimento', 'Nome do Paciente', 'Nr. Matricula', 'Pessoa Resp Aut']]
            pacientes_com_erro.columns = ['Nº Atendimento', 'Nome do Paciente', 'Matrícula Informada', 'Colaborador']

            # --- ABAS ---
            aba1, aba2, aba3, aba4, aba5 = st.tabs(["⭐ Resumo Geral", "👤 Gestão de Equipe", "🏥 Segmentação ID / AD", "📋 Listas de Prorrogação", "🚨 Alertas de Erro"])
            
            with aba1:
                st.subheader("📌 Indicadores Operacionais")
                card1, card2, card3, card4 = st.columns(4)
                card1.metric("Total de Pacientes (IW)", f"{total_pacientes}")
                card2.metric("✅ Inseridos no Portal", f"{inseridos}")
                card3.metric("⏳ Pendentes Total", f"{faltam}")
                card4.metric("🚨 Erros de Cadastro", f"{len(pacientes_com_erro)}")
                
                if df_s_consolidado is not None:
                    st.markdown("---")
                    st.subheader("🏢 Pendências de Relatório por Setor Multidisciplinar")
                    
                    df_amil_v = df[['Nr. Atendimento', 'Valor a Cobrar']].copy()
                    df_setores_valores = pd.merge(df_s_consolidado, df_amil_v, left_on='Nº Atendimento', right_on='Nr. Atendimento', how='left')
                    
                    analise_setores = df_setores_valores.groupby('Grupo Especialidade').agg(
                        Quantidade=('ID Pront.', 'count'),
                        Valor_Total=('Valor a Cobrar', 'sum')
                    ).reset_index()
                    
                    graf_setor_qtd = analise_setores[['Grupo Especialidade', 'Quantidade']].copy()
                    graf_setor_val = analise_setores[['Grupo Especialidade', 'Valor_Total']].copy()
                    
                    set_col1, set_col2 = st.columns(2)
                    with set_col1:
                        st.write("**Quantidade de Relatórios Pendentes por Setor**")
                        st.bar_chart(graf_setor_qtd, x='Grupo Especialidade', y='Quantidade')
                    with set_col2:
                        st.write("**Impacto Financeiro Bloqueado por Setor (R$)**")
                        st.bar_chart(graf_setor_val, x='Grupo Especialidade', y='Valor_Total')
                    
                    st.markdown("#### 📋 Detalhes Financeiros dos Setores")
                    df_setores_renomeado = analise_setores.rename(columns={'Grupo Especialidade': 'Setor / Especialidade', 'Quantidade': 'Qtd Pendências', 'Valor_Total': 'Valor Represado (R$)'})
                    st.dataframe(df_setores_renomeado.style.format({'Valor Represado (R$)' : 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

            with aba2:
                st.subheader("👤 Produtividade e Demandas por Colaborador")
                df_prod = df.groupby('Pessoa Resp Aut').agg(
                    Imputados=('Inserido_Amil', 'sum'),
                    Faltam=('Inserido_Amil', lambda x: len(x) - x.sum())
                ).reset_index()
                
                graf_colab = df_prod[['Pessoa Resp Aut', 'Imputados', 'Faltam']].copy()
                graf_colab.columns = ['Colaborador', 'Imputados (Concluídos)', 'Faltam Terminar']
                
                prod_graf_col, prod_tab_col = st.columns([6, 4])
                with prod_graf_col:
                    st.write("**Gráfico de Carga de Trabalho (Concluídos vs Faltam)**")
                    st.bar_chart(graf_colab, x='Colaborador', y=['Imputados (Concluídos)', 'Faltam Terminar'])
                with prod_tab_col:
                    st.write("**Dados Consolidados da Equipe**")
                    st.dataframe(graf_colab, use_container_width=True, hide_index=True)

            with aba3:
                st.subheader("🏥 Análise do Modelo de Atendimento (ID vs AD)")
                df_id_ad = df.groupby('Tipo_Atendimento').agg(
                    Quantidade=('Nome do Paciente', 'count'),
                    Valor_Total=('Valor a Cobrar', 'sum')
                ).reset_index()
                
                id_col1, id_col2 = st.columns(2)
                with id_col1:
                    st.write("**Quantidade de Pacientes por Tipo**")
                    st.bar_chart(df_id_ad, x='Tipo_Atendimento', y='Quantidade')
                with id_col2:
                    st.write("**Volume de Prorrogações Represado (R$) por Tipo**")
                    st.bar_chart(df_id_ad, x='Tipo_Atendimento', y='Valor_Total')

            with aba4:
                st.subheader("📋 Prorrogações Ordenadas pelos Maiores Valores")
                tab_p, tab_o = st.tabs(["📄 Prontuário Pendente", "🏢 OPS Pendente"])
                with tab_p:
                    st.markdown(f"**Total de Processos: {len(df_prontuario)} | Montante: R$ {df_prontuario['Valor a Cobrar'].sum():,.2f}**")
                    df_p_view = df_prontuario[['Nr. Atendimento', 'Nome do Paciente', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                    df_p_view.columns = ['Nº Atendimento', 'Nome do Paciente', 'Tipo', 'Especialidades Pendentes (Planilha 2)', 'Responsável', 'Valor a Cobrar (R$)']
                    st.dataframe(df_p_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                with tab_o:
                    st.markdown(f"**Total de Processos: {len(df_ops)} | Montante: R$ {df_ops['Valor a Cobrar'].sum():,.2f}**")
                    df_o_view = df_ops[['Nr. Atendimento', 'Nome do Paciente', 'Tipo_Atendimento', 'Especialidades Pendentes', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                    df_o_view.columns = ['Nº Atendimento', 'Nome do Paciente', 'Tipo', 'Especialidades Pendentes (Planilha 2)', 'Responsável', 'Valor a Cobrar (R$)']
                    st.dataframe(df_o_view.style.format({'Valor a Cobrar (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

            with aba5:
                st.subheader("🚨 Cadastros Incompletos / Erros no IW")
                st.dataframe(pacientes_com_erro, use_container_width=True, hide_index=True)
                
                if len(pacientes_com_erro) > 0:
                    csv_erros = pacientes_com_erro.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Baixar Planilha de Erros", data=csv_erros, file_name="correcoes_iw.csv", mime="text/csv")
                    
    except Exception as e:
        st.error(f"Erro ao processar o conjunto de arquivos. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Selecione um ou mais arquivos do IW acima para calcular o Dashboard...")
