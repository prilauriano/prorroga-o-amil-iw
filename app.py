import streamlit as st
import pandas as pd
import re

# Configuração da página institucional da Solar Cuidados
st.set_page_config(page_title="Dashboard Prorrogações | Solar Cuidados", page_icon="☀️", layout="wide")

# Estilização Personalizada com a Identidade Visual da Solar Cuidados (Laranja e Azul Noturno)
st.markdown("""
    <style>
    .main-title { font-size:34px; font-weight:bold; color:#0b2545; margin-bottom:2px; }
    .solar-accent { color: #f37021; }
    .subtitle { font-size:16px; color:#555555; margin-bottom:25px; }
    div[data-testid="stMetricValue"] { color: #0b2545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">☀️ Dashboard Prorrogações <span class="solar-accent">Solar Cuidados</span></p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Gestão estratégica de prorrogações Amil, pendências multidisciplinares e segmentação de internações (ID/AD).</p>', unsafe_allow_html=True)

# --- ÁREA DE UPLOAD DAS PLANILHAS ---
col_up1, col_up2 = st.columns(2)
with col_up1:
    arquivo_amil = st.file_uploader("1️⃣ Arrasta a planilha PRINCIPAL do IW aqui (.csv)", type=["csv", "xlsx"])
with col_up2:
    arquivo_setores = st.file_uploader("2️⃣ [Opcional] Arrasta a planilha de PENDÊNCIAS POR SETORES aqui (.csv)", type=["csv", "xlsx"])

if arquivo_amil is not None:
    try:
        # --- LEITURA DA PLANILHA PRINCIPAL ---
        if arquivo_amil.name.endswith('.csv'):
            try:
                df = pd.read_csv(arquivo_amil, sep=';', encoding='utf-8')
            except UnicodeDecodeError:
                arquivo_amil.seek(0)
                df = pd.read_csv(arquivo_amil, sep=';', encoding='iso-8859-1')
            if df.shape[1] <= 1:
                arquivo_amil.seek(0)
                try:
                    df = pd.read_csv(arquivo_amil, sep=',', encoding='utf-8')
                except UnicodeDecodeError:
                    arquivo_amil.seek(0)
                    df = pd.read_csv(arquivo_amil, sep=',', encoding='iso-8859-1')
        else:
            df = pd.read_excel(arquivo_amil)
            
        df.columns = df.columns.str.strip()
        
        # --- VERIFICAÇÃO DE COLUNAS CRÍTICAS ---
        colunas_obrigatorias = ['Nr. Matricula', 'Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Pessoa Resp Aut', 'Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Valor a Cobrar', 'Classific. Atendimento']
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"❌ A planilha 1 está faltando as colunas essenciais: {colunas_faltantes}.")
        else:
            # Tratamento inicial de texto e nulos
            for c in ['Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Nr. Matricula', 'Pessoa Resp Aut', 'Classific. Atendimento']:
                df[c] = df[c].fillna('').astype(str).str.strip()
            
            df['Nr. Atendimento'] = df['Nr. Atendimento'].astype(str).str.strip()
            
            # Conversão correta de dinheiro
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
            
            # Classificação Inteligente ID vs AD - Padrão de Cuidados Solar
            df['Tipo_Atendimento'] = df['Classific. Atendimento'].apply(
                lambda x: 'ID (Internação Domiciliar)' if x.startswith('ID') else ('AD (Atenção Domiciliar)' if x.startswith('AD') else 'Outros')
            )
            
            # --- PROCESSAMENTO DA SEGUNDA PLANILHA (SETORES) ---
            df_s = None
            setores_agrupados = None
            if arquivo_setores is not None:
                try:
                    if arquivo_setores.name.endswith('.csv'):
                        try: df_s = pd.read_csv(arquivo_setores, sep=';', encoding='utf-8')
                        except UnicodeDecodeError:
                            arquivo_setores.seek(0)
                            df_s = pd.read_csv(arquivo_setores, sep=';', encoding='iso-8859-1')
                    else:
                        df_s = pd.read_excel(arquivo_setores)
                    
                    df_s.columns = df_s.columns.str.strip()
                    df_s['Nº Atendimento'] = df_s['Nº Atendimento'].astype(str).str.strip()
                    df_s['Grupo Especialidade'] = df_s['Grupo Especialidade'].fillna('Outros').astype(str).str.strip()
                    
                    setores_agrupados = df_s.groupby('Nº Atendimento')['Grupo Especialidade'].apply(
                        lambda x: ', '.join(sorted(set(x)))
                    ).reset_index()
                    setores_agrupados.columns = ['Nr. Atendimento', 'Especialidades Pendentes']
                except Exception as e_setor:
                    st.warning(f"⚠️ Não foi possível ler a planilha de setores. Erro: {e_setor}")

            if setores_agrupados is not None:
                df = pd.merge(df, setores_agrupados, on='Nr. Atendimento', how='left')
                df['Especialidades Pendentes'] = df['Especialidades Pendentes'].fillna('Nenhuma pendência técnica apontada')
            else:
                df['Especialidades Pendentes'] = 'Carregue a planilha 2 para abrir os setores'

            # Métricas Gerais
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

            # --- ABAS INTEGRADAS COM DESIGN SOLAR ---
            aba1, aba2, aba3, aba4, aba5 = st.tabs(["🧡 Resumo Geral Solar", "👤 Gestão de Equipe", "🏥 Segmentação ID / AD", "📋 Listas de Prorrogação", "🚨 Alertas de Erro"])
            
            with aba1:
                st.markdown("### 📌 Resumo Operacional da Operação")
                card1, card2, card3, card4 = st.columns(4)
                card1.metric("Total de Pacientes (IW)", f"{total_pacientes}")
                card2.metric("✅ Inseridos no Portal", f"{inseridos}")
                card3.metric("⏳ Pendentes Total", f"{faltam}")
                card4.metric("🚨 Erros de Cadastro", f"{len(pacientes_com_erro)}")
                
                if df_s is not None:
                    st.markdown("---")
                    st.markdown("### 🏢 Pendências de Relatório por Setor Multidisciplinar")
                    
                    df_amil_v = df[['Nr. Atendimento', 'Valor a Cobrar']].copy()
                    df_setores_valores = pd.merge(df_s, df_amil_v, left_on='Nº Atendimento', right_on='Nr. Atendimento', how='left')
                    analise_setores = df_setores_valores.groupby('Grupo Especialidade').agg(
                        Quantidade=('ID Pront.', 'count'),
                        Valor_Total=('Valor a Cobrar', 'sum')
                    ).reset_index()
                    
                    set_col1, set_col2 = st.columns(2)
                    with set_col1:
                        st.write("**Quantidade de Relatórios Pendentes por Setor**")
                        st.bar_chart(analise_setores.set_index('Grupo Especialidade')[['Quantidade']], color='#0b2545')
                    with set_col2:
                        st.write("**Impacto Financeiro Bloqueado por Setor (R$)**")
                        st.bar_chart(analise_setores.set_index('Grupo Especialidade')[['Valor_Total']], color='#f37021')
                    
                    st.markdown("#### 📋 Detalhamento dos Setores")
                    st.dataframe(analise_setores.rename(columns={'Grupo Especialidade': 'Setor / Especialidade', 'Quantidade': 'Qtd Pendências', 'Valor_Total': 'Valor Represado (R$)'}).style.format({'Valor Represado (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

            with aba2:
                st.markdown("### 👤 Produtividade e Demandas por Colaborador")
                
                df_prod = df.groupby('Pessoa Resp Aut').agg(
                    Imputados=('Inserido_Amil', 'sum'),
                    Faltam=('Inserido_Amil', lambda x: len(x) - x.sum()),
                    Total=('Inserido_Amil', 'count')
                ).reset_index()
                df_prod.columns = ['Colaborador', 'Imputados (Concluídos)', 'Faltam Terminar', 'Total sob Custódia']
                
                prod_graf_col, prod_tab_col = st.columns([6, 4])
                with prod_graf_col:
                    st.write("**Gráfico de Carga de Trabalho Solar (Faltam vs Concluídos)**")
                    # Cores customizadas da Solar para o gráfico empilhado
                    st.bar_chart(df_prod.set_index('Colaborador')[['Imputados (Concluídos)', 'Faltam Terminar']], color=['#f37021', '#0b2545'])
                with prod_tab_col:
                    st.write("**Dados Consolidados**")
                    st.dataframe(df_prod, use_container_width=True, hide_index=True)

            with aba3:
                st.markdown("### 🏥 Análise do Modelo de Atendimento Solar (ID vs AD)")
                df_id_ad = df.groupby('Tipo_Atendimento').agg(
                    Quantidade=('Nome do Paciente', 'count'),
                    Valor_Total=('Valor a Cobrar', 'sum')
                ).reset_index()
                
                id_col1, id_col2 = st.columns(2)
                with id_col1:
                    st.write("**Quantidade de Pacientes por Tipo**")
                    st.bar_chart(df_id_ad.set_index('Tipo_Atendimento')[['Quantidade']], color='#0b2545')
                with id_col2:
                    st.write("**Volume de Prorrogas Represado (R$) por Tipo**")
                    st.bar_chart(df_id_ad.set_index('Tipo_Atendimento')[['Valor_Total']], color='#f37021')

            with aba4:
                st.markdown("### 📋 Prorrogações Ordenadas pelos Maiores Valores")
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
                st.markdown("### 🚨 Cadastros Incompletos / Erros no IW")
                st.dataframe(pacientes_com_erro, use_container_width=True, hide_index=True)
                
                if len(pacientes_com_erro) > 0:
                    csv_erros = pacientes_com_erro.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Baixar Planilha de Erros", data=csv_erros, file_name="correcoes_iw.csv", mime="text/csv")
                    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Aguardando o upload da planilha do IW para ativar o Dashboard Prorrogações Solar Cuidados...")

