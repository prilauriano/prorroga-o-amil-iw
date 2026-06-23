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
st.markdown('<p class="subtitle">Carregue o relatório do IW para atualizar o painel de faturamento instantaneamente.</p>', unsafe_allow_html=True)

# 1. Botão de fazer o upload do arquivo
arquivo_enviado = st.file_uploader("Clique no botão abaixo ou abra o arquivo do IW aqui", type=["csv", "xlsx"])

if arquivo_enviado is not None:
    try:
        # --- LEITURA BLINDADA DO ARQUIVO ---
        if arquivo_enviado.name.endswith('.csv'):
            df = pd.read_csv(arquivo_enviado, sep=';', encoding='utf-8')
            if df.shape[1] <= 1:
                arquivo_enviado.seek(0)
                df = pd.read_csv(arquivo_enviado, sep=',', encoding='utf-8')
        else:
            df = pd.read_excel(arquivo_enviado)
        
        # Limpa espaços invisíveis nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # --- VERIFICAÇÃO DE COLUNAS CRÍTICAS ---
        colunas_obrigatorias = ['Nr. Matricula', 'Nº Guia Solicitação (TISS)', 'Senha Aprovação', 'Status Aut Orç', 'Pessoa Resp Aut', 'Nome do Paciente', 'Nr. Atendimento', 'ID Orçam.']
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltantes:
            st.error(f"❌ O arquivo enviado está faltando as seguintes colunas essenciais: {colunas_faltantes}. Verifique se exportou o relatório correto do IW.")
        else:
            # Tratamento de valores nulos/vazios para evitar erros de leitura
            df['Nº Guia Solicitação (TISS)'] = df['Nº Guia Solicitação (TISS)'].fillna('').astype(str).str.strip()
            df['Senha Aprovação'] = df['Senha Aprovação'].fillna('').astype(str).str.strip()
            df['Status Aut Orç'] = df['Status Aut Orç'].fillna('').astype(str).str.strip()
            df['Nr. Matricula'] = df['Nr. Matricula'].fillna('').astype(str).str.strip()
            df['Pessoa Resp Aut'] = df['Pessoa Resp Aut'].fillna('Não Atribuído').astype(str).str.strip()
            
            # --- CRITÉRIO DE INSERÇÃO NO PORTAL AMIL ---
            df['Inserido_Amil'] = (df['Nº Guia Solicitação (TISS)'] != '') | (df['Senha Aprovação'] != '') | (df['Status Aut Orç'] == 'Autorizado')
            
            total_pacientes = len(df)
            inseridos = df['Inserido_Amil'].sum()
            faltam = total_pacientes - inseridos
            
            # --- AUDITORIA DE ERROS ---
            tam_matriculas = df['Nr. Matricula'].str.len()
            # Considera erro se estiver zerado ou fora do padrão de 8 ou 9 dígitos da Amil
            erro_matricula = (tam_matriculas == 0) | (~tam_matriculas.isin([8, 9]))
            
            # Checagem segura das colunas de data (só valida se as colunas existirem com esses nomes exatos)
            if 'Data Início' in df.columns and 'Data Fim' in df.columns:
                erro_datas = df['Data Início'].isna() | df['Data Fim'].isna()
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
            
            # --- DIVISÃO DA TELA EM COLUNAS ---
            col_esquerda, col_direita = st.columns([4, 6])
            
            with col_esquerda:
                st.markdown("### 🏆 Ranking de Produtividade")
                st.caption("Quantidade de processos sob a responsabilidade de cada colaborador:")
                ranking = df['Pessoa Resp Aut'].value_counts().reset_index()
                ranking.columns = ['Colaborador', 'Pacientes Atribuídos']
                st.dataframe(ranking, use_column_width=True, hide_index=True)
                    
            with col_direita:
                st.markdown("### 🚨 Lista de Erros para Correção Rápida")
                st.caption("Pacientes com inconformidades detectadas no relatório:")
                st.dataframe(pacientes_com_erro, use_column_width=True, hide_index=True)
                
                # Botão para baixar planilha de erros
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
