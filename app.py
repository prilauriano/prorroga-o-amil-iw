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
st.markdown('<p class="subtitle">Carregue o relatório do IW para atualizar o painel de faturamento e os gráficos instantaneamente.</p>', unsafe_allow_html=True)

# 1. Botão de fazer o upload do arquivo
arquivo_enviado = st.file_uploader("Clique no botão abaixo ou abra o arquivo do IW aqui", type=["csv", "xlsx"])

if arquivo_enviado is not None:
    try:
        # --- LEITURA BLINDADA DO ARQUIVO (COM TRATAMENTO DE ENCODING) ---
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
        colunas_obrigatorias = ['Nr. Matricula', 'Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Pessoa Resp Aut', 'Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.']
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"❌ O arquivo enviado está faltando as seguintes colunas essenciais: {colunas_faltantes}.")
        else:
            # Tratamento de valores nulos/vazios para evitar erros de leitura
            df['Nº Guia Solicitação (TISS)'] = df['Nº Guia Solicitação (TISS)'].fillna('').astype(str).str.strip()
            df['Senha Aprovação'] = df['Senha Aprovação'].fillna('').astype(str).str.strip()
            df['Status Aut Orç'] = df['Status Aut Orç'].fillna('').astype(str).str.strip()
            df['Nr. Matricula'] = df['Nr. Matricula'].fillna('').astype(str).str.strip()
            df['Pessoa Resp Aut'] = df['Pessoa Resp Aut'].fillna('Não Atribuído').astype(str).str.strip()
            
            # --- VALIDAÇÃO: SÓ ACEITA NÚMEROS NA GUIA TISS ---
            # .str.isnumeric() retorna True apenas se a célula contiver somente números
            guia_valida_numerica = df['Nº Guia Solicitação (TISS)'].str.isnumeric()
            
            # --- CRITÉRIO DE INSERÇÃO NO PORTAL AMIL ---
            # Considera inserido se a guia for estritamente numérica OU se tiver Senha de Aprovação OU se estiver Autorizado
            df['Inserido_Amil'] = (guia_valida_numerica) | (df['Senha Aprovação'] != '') | (df['Status Aut Orç'] == 'Autorizado')
            
            total_pacientes = len(df)
            inseridos = df['Inserido_Amil'].sum()
            faltam = total_pacientes - inseridos
            
            # --- AUDITORIA DE ERROS CRÍTICOS ---
            tam_matriculas = df['Nr. Matricula'].str.len()
            erro_matricula = (tam_matriculas == 0) | (~tam_matriculas.isin([8, 9]))
            
            # Checagem segura das colunas de data
            if 'Data Início' in df.columns and 'Data Fim' in df.columns:
                erro_datas = df['Data Início'].isna() | (df['Data Início'].astype(str).str.strip() == '') | df['Data Fim'].isna() | (df['Data Fim'].astype(str).str.strip() == '')
            else:
                erro_datas = False
                
            erro_vinculo = df['Nr. Atendimento'].isna() | df['ID Orçam.'].isna()
            df['Possui_Erro'] = erro_matricula | erro_datas | erro_vinculo
            
            # Tabela de erros filtrada
            pacientes_com_erro = df[df['Possui_Erro'] == True][['Nr. Atendimento', 'Nome do Paciente', 'Nr. Matricula', 'Pessoa Resp Aut']]
            pacientes_com_erro.columns = ['Nº Atendimento', 'Nome do Paciente', 'Matrícula Informada', 'Colaborador Responsável']
            
            # --- CARDS VISUAIS DE DADOS (KPIs) ---
            card1, card2, card3, card4 = st.columns(4)
            card1.metric("Total de Pacientes (IW)", f"{total_pacientes}")
            card2.metric("✅ Inseridos no Portal Amil", f"{inseridos}")
            card3.metric("⏳ Pendentes (Faltam)", f"{faltam}")
            card4.metric("🚨 Cadastros com Inconsistência", f"{len(pacientes_com_erro)}")
            
            st.markdown("---")
            
            # --- SEÇÃO DE GRÁFICOS INTERATIVOS ---
            st.markdown("### 📈 Análise Gráfica em Tempo Real")
            graf_col1, graf_col2 = st.columns(2)
            
            with graf_col1:
                st.write("**Progresso Geral da Operação**")
                dados_progresso = pd.DataFrame({
                    'Status': ['✅ Inseridos', '⏳ Pendentes'],
                    'Quantidade': [inseridos, faltam]
                })
                st.bar_chart(dados_progresso.set_index('Status'), y='Quantidade', color='#134074')
            
            with graf_col2:
                st.write("**Produtividade (Pacientes sob Responsabilidade)**")
                ranking_grafico = df['Pessoa Resp Aut'].value_counts().reset_index()
                ranking_grafico.columns = ['Colaborador', 'Pacientes']
                st.bar_chart(ranking_grafico.set_index('Colaborador'), y='Pacientes', color='#2a9d8f')
            
            st.markdown("---")
            
            # --- TABELAS DETALHADAS ---
            col_esquerda, col_direita = st.columns([4, 6])
            
            with col_esquerda:
                st.markdown("### 🏆 Ranking de Produtividade")
                ranking = df['Pessoa Resp Aut'].value_counts().reset_index()
                ranking.columns = ['Colaborador', 'Pacientes Atribuídos']
                st.dataframe(ranking, use_container_width=True, hide_index=True)
                    
            with col_direita:
                st.markdown("### 🚨 Detalhes dos Erros Detectados")
                st.dataframe(pacientes_com_erro, use_container_width=True, hide_index=True)
                
                if len(pacientes_com_erro) > 0:
                    csv_erros = pacientes_com_erro.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar Planilha de Erros para Cobrar a Equipe",
                        data=csv_erros,
                        file_name="erros_faturamento_amil.csv",
                        mime="text/csv",
                    )
                    
    except Exception as e:
        st.error(f"Erro inesperado ao processar o arquivo. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Aguardando você arrastar ou selecionar a planilha do IW acima para calcular...")
