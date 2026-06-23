import streamlit as st
import pandas as pd

# Configuração da página e design do Dashboard
st.set_page_config(page_title="Gestão de Faturamento Amil", page_icon="📊", layout="wide")

# Estilização customizada para deixar o visual profissional
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #0b2545; margin-bottom: 5px; }
    .subtitle { font-size: 14px; color: #555555; margin-bottom: 25px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #134074; }
    </style>
""", unsafe_type=True)

st.markdown('<p class="main-title">📊 Painel de Controle e Auditoria — Portal Amil</p>', unsafe_type=True)
st.markdown('<p class="subtitle">Faça o upload do relatório bruto extraído do sistema IW para consolidar a produção e auditar inconsistências instantaneamente.</p>', unsafe_type=True)

# Área Interativa de Upload de Arquivo
arquivo_iw = st.file_uploader("Arraste ou clique para anexar a sua planilha do IW (.csv)", type=["csv"])

if arquivo_iw is not None:
    try:
        # Lendo o arquivo do IW configurado com separador ponto e vírgula
        df = pd.read_csv(arquivo_iw, sep=';', encoding='utf-8')
        
        # --- REGRAS DE NEGÓCIO ---
        # Identificação de pacientes inseridos/autorizados no portal
        df['No_Portal'] = df['Nº Guia Solicitação (TISS)'].notna() | df['Senha Aprovação'].notna() | (df['Status Aut Orç'] == 'Autorizado')
        
        total_pacientes = len(df)
        inseridos = df['No_Portal'].sum()
        faltam = total_pacientes - inseridos
        
        # --- AUDITORIA DE ERROS E INCONSISTÊNCIAS ---
        # Verificação do tamanho da matrícula (Padrão Amil de 8 ou 9 dígitos)
        df['Tam_Matricula'] = df['Nr. Matricula'].astype(str).str.strip().str.len()
        erro_matricula = ~df['Tam_Matricula'].isin([8, 9])
        
        # Verificação de ausência de datas de vigência
        erro_datas = df['Data Início'].isna() | df['Data Fim'].isna()
        
        # Verificação de falta de vínculos críticos do IW
        erro_vinculo = df['Nr. Atendimento'].isna() | df['ID Orçam.'].isna()
        
        # Consolidação dos erros encontrados
        df['Possui_Erro'] = erro_matricula | erro_datas | erro_vinculo
        pacientes_com_erro = df[df['Possui_Erro'] == True][['Nr. Atendimento', 'Nome do Paciente', 'Nr. Matricula', 'Pessoa Resp Aut']]
        pacientes_com_erro.columns = ['Nº Atendimento', 'Nome do Paciente', 'Matrícula', 'Responsável']
        
        # --- EXIBIÇÃO DO PAINEL DE INDICADORES (KPIs) ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total no Relatório (IW)", f"{total_pacientes}")
        with col2:
            st.metric("✅ Inseridos no Portal", f"{inseridos}", delta=f"+{inseridos} Concluídos")
        with col3:
            st.metric("⏳ Pendentes (Faltam)", f"{faltam}", delta=f"-{inseridos} Restantes", delta_color="inverse")
        with col4:
            st.metric("🚨 Cadastros Incorretos", f"{len(pacientes_com_erro)}")
            
        st.markdown("---")
        
        # Divisão da tela em duas seções principais
        col_esq, col_dir = st.columns([4, 6])
        
        with col_esq:
            st.markdown("### 🏆 Produtividade da Equipe")
            st.write("Volume total de processos sob a responsabilidade de cada colaborador:")
            if 'Pessoa Resp Aut' in df.columns:
                produtividade = df['Pessoa Resp Aut'].value_counts().reset_index()
                produtividade.columns = ['Colaborador', 'Pacientes Atribuídos']
                st.dataframe(produtividade, use_container_width=True, hide_index=True)
            else:
                st.warning("Coluna de responsáveis não localizada no arquivo.")
                
        with col_dir:
            st.markdown("### 🔍 Lista de Erros Detectados")
            st.write("Corrija estes cadastros no IW para evitar glosas ou atrasos na Amil:")
            
            if len(pacientes_com_erro) > 0:
                st.dataframe(pacientes_com_erro, use_container_width=True, hide_index=True)
                
                # Botão para baixar planilha só com as falhas para repassar para a equipe
                csv_erros = pacientes_com_erro.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Lista de Erros para Correção (.csv)",
                    data=csv_erros,
                    file_name="correcoes_pendentes_amil.csv",
                    mime="text/csv",
                )
            else:
                st.success("Sensacional! Nenhuma inconsistência de cadastro foi detectada no lote atual.")
                
    except Exception as e:
        st.error(f"Erro ao ler o arquivo. Certifique-se de que exportou o relatório correto do IW. Detalhes técnicos: {e}")
else:
    st.info("Aguardando o upload da planilha para atualizar os dados...")