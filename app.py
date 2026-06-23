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
arquivo_enviado = st.file_uploader("Clique no botão abaixo ou arraste o arquivo do IW aqui", type=["csv", "xlsx"])

if arquivo_enviado is not None:
    try:
        # Identificar se é CSV ou Excel e ler com o separador correto do IW (ponto e vírgula)
        if arquivo_enviado.name.endswith('.csv'):
            df = pd.read_csv(arquivo_enviado, sep=';', encoding='utf-8')
        else:
            df = pd.read_excel(arquivo_enviado)
        
        # --- REGRAS DE NEGÓCIO E MAPEAMENTO ---
        # Verificar se o paciente já foi inserido no Portal Amil
        df['Inserido_Amil'] = df['Nº Guia Solicitação (TISS)'].notna() | df['Senha Aprovação'].notna() | (df['Status Aut Orç'] == 'Autorizado')
        
        total_pacientes = len(df)
        inseridos = df['Inserido_Amil'].sum()
        faltam = total_pacientes - inseridos
        
        # Regras de Auditoria de Erros (Garantindo que calcula o tamanho da matrícula da forma correta)
        tam_matriculas = df['Nr. Matricula'].astype(str).str.strip().str.len()
        erro_matricula = ~tam_matriculas.isin([8, 9]) 
        
        erro_datas = df['Data Início'].isna() | df['Data Fim'].isna()
        erro_vinculo = df['Nr. Atendimento'].isna() | df['ID Orçam.'].isna()
        
        df['Possui_Erro'] = erro_matricula | erro_datas | erro_vinculo
        
        # Filtrar tabela contendo apenas os erros críticos
        pacientes_com_erro = df[df['Possui_Erro'] == True][['Nr. Atendimento', 'Nome do Paciente', 'Nr. Matricula', 'Pessoa Resp Aut']]
        pacientes_com_erro.columns = ['Nº Atendimento', 'Nome do Paciente', 'Matrícula Informada', 'Colaborador Responsável']
        
        # --- CARDS VISUAIS DE DADOS (KPIs) ---
        card1, card2, card3, card4 = st.columns(4)
        card1.metric("Total de Pacientes (IW)", f"{total_pacientes}")
        card2.metric("✅ Inseridos no Portal Amil", f"{inseridos}", delta=f"+{inseridos}")
        card3.metric("⏳ Pendentes (Faltam)", f"{faltam}", delta=f"-{inseridos}", delta_color="inverse")
        card4.metric("🚨 Cadastros com Inconsistência", f"{len(pacientes_com_erro)}")
        
        st.markdown("---")
        
        # --- DIVISÃO DA TELA EM COLUNAS ---
        col_esquerda, col_direita = st.columns([4, 6])
        
        with col_esquerda:
            st.markdown("### 🏆 Ranking de Produtividade")
            st.caption("Quantidade de processos sob a responsabilidade de cada colaborador:")
            if 'Pessoa Resp Aut' in df.columns:
                ranking = df['Pessoa Resp Aut'].value_counts().reset_index()
                ranking.columns = ['Colaborador', 'Pacientes Atribuídos']
                st.dataframe(ranking, use_column_width=True, hide_index=True)
            else:
                st.warning("Coluna 'Pessoa Resp Aut' não encontrada.")
                
        with col_direita:
            st.markdown("### 🚨 Lista de Erros para Correção Rápida")
            st.caption("Pacientes identificados com matrículas fora do padrão, falta de vigência ou sem ID de orçamento:")
            st.dataframe(pacientes_com_erro, use_column_width=True, hide_index=True)
            
            # Botão de clicar para baixar a lista de erros em Excel
            if len(pacientes_com_erro) > 0:
                csv_erros = pacientes_com_erro.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar Planilha de Erros para Cobrar a Equipe",
                    data=csv_erros,
                    file_name="erros_faturamento_amil.csv",
                    mime="text/csv",
                )
                
    except Exception as e:
        st.error(f"Erro ao processar o arquivo. Detalhe técnico: {e}")
else:
    st.info("💡 Tudo pronto! Aguardando você arrastar ou selecionar a planilha do IW acima para calcular...")
