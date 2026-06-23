import streamlit as st
import pandas as pd
import re

# Configuração da página e design do cabeçalho
st.set_page_config(page_title="Painel Faturamento Amil", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#0b2545; margin-bottom:5px; }
    .subtitle { font-size:16px; color:#555555; margin-bottom:25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">📊 Super Monitor de Imputação e Auditoria — Amil IW</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análise avançada cruzando relatórios de faturamento, pendências setoriais e segmentação ID/AD.</p>', unsafe_allow_html=True)

# --- ÁREA DE UPLOAD DAS DUAS PLANILHAS ---
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
            
            # Classificação Inteligente ID vs AD
            df['Tipo_Atendimento'] = df['Classific. Atendimento'].apply(
                lambda x: 'ID (Internação)' if x.startswith('ID') else ('AD (Atenção)' if x.startswith('AD') else 'Outros')
            )
            
            # --- PROCESSAMENTO DA SEGUNDA PLANILHA (SETORES), SE ENVIADA ---
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
                    
                    # Agrupa gerando a lista de setores pendentes por atendimento (PROCV)
                    setores_agrupados = df_s.groupby('Nº Atendimento')['Grupo Especialidade'].apply(
                        lambda x: ', '.join(sorted(set(x)))
                    ).reset_index()
                    setores_agrupados.columns = ['Nr. Atendimento', 'Especialidades Pendentes']
                except Exception as e_setor:
                    st.warning(f"⚠️ Não foi possível ler a planilha de setores. Prosseguindo sem o cruzamento. Erro: {e_setor}")

            # Cruzamento dos dados (Merge das Especialidades)
            if setores_agrupados is not None:
                df = pd.merge(df, setores_agrupados, on='Nr. Atendimento', how='left')
                df['Especialidades Pendentes'] = df['Especialidades Pendentes'].fillna('Não especificado na Planilha 2')
            else:
                df['Especialidades Pendentes'] = 'Carregue a Planilha 2 para ver as especialidades'

            # Métricas Básicas
            guia_valida_numerica = df['Nº Guia Solicitação (TISS)'].str.isnumeric()
            df['Inserido_Amil'] = (guia_valida_numerica) | (df['Senha Aprovação'] != '') | (df['Status Aut Orç'] == 'Autorizado')
            
            total_pacientes = len(df)
            inseridos = df['Inserido_Amil'].sum()
            faltam = total_pacientes - inseridos
            
            # Filtragem e Ordenação por Maior Valor (Regra Pedida!)
            df_prontuario = df[df['Status Aut Orç'] == 'Prontuário Pendente'].sort_values(by='Valor a Cobrar', ascending=False)
            df_ops = df[df['Status Aut Orç'] == 'OPS Pendente'].sort_values(by='Valor a Cobrar', ascending=False)
            
            # Auditoria de Erros de Cadastro
            tam_matriculas = df['Nr. Matricula'].str.len()
            erro_matricula = (tam_matriculas == 0) | (~tam_matriculas.isin([8, 9]))
            erro_vinculo = df['Nr. Atendimento'].isna() | df['ID Orçam.'].isna()
            df['Possui_Erro'] = erro_matricula | erro_vinculo
            pacientes_com_erro = df[df['Possui_Erro'] == True][['Nr. Atendimento', 'Nome do Paciente', 'Nr. Matricula', 'Pessoa Resp Aut']]
            pacientes_com_erro.columns = ['Nº Atendimento', 'Nome do Paciente', 'Matrícula Informada', 'Colaborador']

            # --- CRIAÇÃO DAS ABAS DO PAINEL ---
            aba1, aba2, aba3, aba4 = st.tabs(["📈 Geral & Produtividade", "🏥 Segmentação ID / AD", "📋 Listas de Pendências (Maiores Valores)", "🚨 Alertas de Erro"])
            
            with aba1:
                st.markdown("### 📌 Resumo Operacional")
                card1, card2, card3, card4 = st.columns(4)
                card1.metric("Total de Pacientes (IW)", f"{total_pacientes}")
                card2.metric("✅ Inseridos no Portal", f"{inseridos}")
                card3.metric("⏳ Pendentes (Faltam)", f"{faltam}")
                card4.metric("🚨 Erros de Cadastro", f"{len(pacientes_com_erro)}")
                
                st.markdown("---")
                st.markdown("### 🏆 Ranking de Produtividade dos Colaboradores")
                g_col1, g_col2 = st.columns([4, 6])
                with g_col1:
                    ranking = df['Pessoa Resp Aut'].value_counts().reset_index()
                    ranking.columns = ['Colaborador', 'Pacientes Atribuídos']
                    st.dataframe(ranking, use_container_width=True, hide_index=True)
                with g_col2:
                    st.bar_chart(ranking.set_index('Colaborador'), y='Pacientes Atribuídos', color='#2a9d8f')

            with aba2:
                st.markdown("### 🏥 Análise do Modelo de Atendimento (ID vs AD)")
                
                # Agrupando dados para os gráficos
                df_id_ad = df.groupby('Tipo_Atendimento').agg(
                    Quantidade=('Nome do Paciente', 'count'),
                    Valor_Total=('Valor a Cobrar', 'sum')
                ).reset_index()
                
                id_col1, id_col2 = st.columns(2)
                with id_col1:
                    st.write("**Quantidade de Pacientes por Tipo**")
                    st.bar_chart(df_id_ad.set_index('Tipo_Atendimento')[['Quantidade']], color='#134074')
                with id_col2:
                    st.write("**Volume Financeiro Represado (R$) por Tipo**")
                    st.bar_chart(df_id_ad.set_index('Tipo_Atendimento')[['Valor_Total']], color='#e76f51')
                
                st.markdown("#### 📋 Lista Resumida de Pacientes ID / AD")
                df_exibir_id_ad = df[['Nr. Atendimento', 'Nome do Paciente', 'Tipo_Atendimento', 'Pessoa Resp Aut', 'Valor a Cobrar']].copy()
                df_exibir_id_ad.columns = ['Nº Atendimento', 'Nome do Paciente', 'Tipo Atendimento', 'Responsável', 'Valor (R$)']
                st.dataframe(df_exibir_id_ad.style.format({'Valor (R$)': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

            with aba3:
                st.markdown("### 📋 Pendências Ordenadas pelos Maiores Valores")
                st.caption("Foque nas linhas do topo para liberar os maiores montantes financeiros primeiro.")
                
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

            with aba4:
                st.markdown("### 🚨 Cadastros Incompletos / Erros no IW")
                st.write("Corrija estes campos no IW para evitar glosas automáticas no portal:")
                st.dataframe(pacientes_com_erro, use_container_width=True, hide_index=True)
                
                if len(pacientes_com_erro) > 0:
                    csv_erros = pacientes_com_erro.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar Planilha de Erros para Ajuste",
                        data=csv_erros,
                        file_name="correcoes_iw.csv",
                        mime="text/csv",
                    )
                    
    except Exception as e:
        st.error(f"Erro ao processar os arquivos. Certifique-se de que usou os relatórios corretos. Detalhe: {e}")
else:
    st.info("💡 Tudo pronto! Aguardando o upload da planilha principal (1) do IW para ativar o painel...")
