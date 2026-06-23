import streamlit as st
import pandas as pd

# Configuração da página e design do cabeçalho
st.set_page_config(page_title="Painel Faturamento Amil", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#0b2545; margin-bottom:5px; }
    .subtitle { font-size:16px; color:#555555; margin-bottom:25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">📊 Monitor de Imputação e Auditoria — Portal Amil</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análise avançada de pendências operacionais e valores represados do sistema IW.</p>', unsafe_allow_html=True)

# 1. Botão de fazer o upload do arquivo
arquivo_enviado = st.file_uploader("Clique no botão abaixo ou abra o arquivo do IW aqui", type=["csv", "xlsx"])

if arquivo_enviado is not None:
    try:
        # --- LEITURA BLINDADA DO ARQUIVO ---
        if arquivo_enviado.name.endswith('.csv'):
            try:
                df = pd.read_csv(arquivo_enviado, sep=';', encoding='utf-8')
            except UnicodeDecodeError:
                arquivo_enviado.seek(0)
                df = pd.read_csv(arquivo_enviado, sep=';', encoding='iso-8859-1')
            
            if df.shape[1] <= 1:
                arquivo_enviado.seek(0)
                try:
                    df = pd.read_csv(arquivo_enviado, sep=',', encoding='utf-8')
                except UnicodeDecodeError:
                    arquivo_enviado.seek(0)
                    df = pd.read_csv(arquivo_enviado, sep=',', encoding='iso-8859-1')
        else:
            df = pd.read_excel(arquivo_enviado)
        
        # Limpa espaços invisíveis nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # --- VERIFICAÇÃO DE COLUNAS CRÍTICAS ---
        colunas_obrigatorias = ['Nr. Matricula', 'Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Pessoa Resp Aut', 'Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.', 'Valor a Cobrar']
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"❌ O arquivo enviado está faltando as seguintes colunas essenciais: {colunas_faltantes}.")
        else:
            # Tratamento de valores nulos/vazios
            df['Nº Guia Solicitação (TISS)'] = df['Nº Guia Solicitação (TISS)'].fillna('').astype(str).str.strip()
            df['Senha Aprovação'] = df['Senha Aprovação'].fillna('').astype(str).str.strip()
            df['Status Aut Orç'] = df['Status Aut Orç'].fillna('').astype(str).str.strip()
            df['Nr. Matricula'] = df['Nr. Matricula'].fillna('').astype(str).str.strip()
            df['Pessoa Resp Aut'] = df['Pessoa Resp Aut'].fillna('Não Atribuído').astype(str).str.strip()
            
            # Garante que a coluna de Valor a Cobrar está tratada como número numérico puro
            if df['Valor a Cobrar'].dtype == 'object':
                df['Valor a Cobrar'] = df['Valor a Cobrar'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df['Valor a Cobrar'] = pd.to_numeric(df['Valor a Cobrar'], errors='coerce').fillna(0.0)
            
            # --- CRITÉRIO DE INSERÇÃO NO PORTAL AMIL ---
            guia_valida_numerica = df['Nº Guia Solicitação (TISS)'].str.isnumeric()
            df['Inserido_Amil'] = (guia_valida_numerica) | (df['Senha Aprovação'] != '') | (df['Status Aut Orç'] == 'Autorizado')
            
            total_pacientes = len(df)
            inseridos = df['Inserido_Amil'].sum()
            faltam = total_pacientes - inseridos
            
            # --- MAPEAMENTO ESPECÍFICO DE PENDÊNCIAS PEDIDAS ---
            df_prontuario = df[df['Status Aut Orç'] == 'Prontuário Pendente']
            df_ops = df[df['Status Aut Orç'] == 'OPS Pendente']
            
            qtd_prontuario = len(df_prontuario)
            valor_prontuario = df_prontuario['Valor a Cobrar'].sum()
            
            qtd_ops = len(df_ops)
            valor_ops = df_ops['Valor a Cobrar'].sum()
            
            # --- AUDITORIA GERAL DE ERROS DE CADASTRO ---
            tam_matriculas = df['Nr. Matricula'].str.len()
            erro_matricula = (tam_matriculas == 0) | (~tam_matriculas.isin([8, 9]))
            if 'Data Início' in df.columns and 'Data Fim' in df.columns:
                erro_datas = df['Data Início'].isna() | (df['Data Início'].astype(str).str.strip() == '') | df['Data Fim'].isna() | (df['Data Fim'].astype(str).str.strip() == '')
            else:
                erro_datas = False
            erro_vinculo = df['Nr. Atendimento'].isna() | df['ID Orçam.'].isna()
            df['Possui_Erro'] = erro_matricula | erro_datas | erro_vinculo
            
            pacientes_com_erro = df[df['Possui_Erro'] == True][['Nr. Atendimento', 'Nome do Paciente', 'Nr. Matricula', 'Pessoa Resp Aut']]
            pacientes_com_erro.columns = ['Nº Atendimento', 'Nome do Paciente', 'Matrícula Informada', 'Colaborador Responsável']

            # --- LINHA 1 DE METRICAS (GERAL) ---
            st.markdown("### 📌 Visão Geral do Faturamento")
            card1, card2, card3, card4 = st.columns(4)
            card1.metric("Total de Pacientes (IW)", f"{total_pacientes}")
            card2.metric("✅ Inseridos no Portal Amil", f"{inseridos}")
            card3.metric("⏳ Pendentes (Faltam)", f"{faltam}")
            card4.metric("🚨 Erros Críticos de Cadastro", f"{len(pacientes_com_erro)}")
            
            st.markdown("---")
            
            # --- LINHA 2 DE METRICAS (FINANCEIRO DAS PENDÊNCIAS EXCLUSIVAS) ---
            st.markdown("### 💸 Impacto Financeiro Represado por Status")
            fin1, fin2, fin3, fin4 = st.columns(4)
            fin1.metric("📄 Prontuário Pendente (Qtd)", f"{qtd_prontuario} pac.")
            fin2.metric("💰 Prontuário Pendente (R$)", f"R$ {valor_prontuario:,.2f}")
            fin3.metric("🏢 OPS Pendente (Qtd)", f"{qtd_ops} pac.")
            fin4.metric("💰 OPS Pendente (R$)", f"R$ {valor_ops:,.2f}")
            
            st.markdown("---")
            
            # --- GRÁFICOS SOLICITADOS ---
            st.markdown("### 📈 Painel Gráfico de Pendências")
            graf_col1, graf_col2 = st.columns(2)
            
            with graf_col1:
                st.write("**Comparativo de Pacientes Travados (Quantidade)**")
                dados_qtd = pd.DataFrame({
                    'Status de Pendência': ['Prontuário Pendente', 'OPS Pendente'],
                    'Pacientes': [qtd_prontuario, qtd_ops]
                })
                st.bar_chart(dados_qtd.set_index('Status de Pendência'), y='Pacientes', color='#f4a261')
            
            with graf_col2:
                st.write("**Volume Financeiro Represado (Em Reais - R$)**
