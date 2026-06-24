import streamlit as st
import pandas as pd
import plotly.express as px

# --- TRATAMENTO OPERACIONAL DE EQUIPE (QUANTITATIVO) ---
# 1. Ajustando os nomes das colunas e tratando o encoding do arquivo original
df_amil.columns = df_amil.columns.str.strip()

# Identificando as colunas de forma dinâmica para evitar erros com acentuações no arquivo (.csv)
col_classificacao = [c for c in df_amil.columns if 'Classific' in c][0]
col_paciente = [c for c in df_amil.columns if 'Paciente' in c][0]
col_prontuario = [c for c in df_amil.columns if 'Pront' in c][0]

# IMPORTANTE: Caso sua coluna de funcionários tenha outro nome no seu df_amil principal (ex: 'Colaborador', 'Usuário'), altere aqui:
col_responsavel = 'Pessoa Resp Aut' 

# 2. Agrupando as classificações para extrair apenas "ID" ou "AD"
df_amil['Classific_Agrupada'] = df_amil[col_classificacao].fillna('').astype(str).apply(
    lambda x: 'ID' if x.strip().upper().startswith('ID') else ('AD' if x.strip().upper().startswith('AD') else 'Outros')
)

# 3. Métrica de inputs concluídos/inseridos com sucesso no portal
guia_valida_num = df_amil['Nº Guia Solicitação (TISS)'].fillna('').astype(str).str.strip().str.isnumeric() if 'Nº Guia Solicitação (TISS)' in df_amil.columns else pd.Series(False, index=df_amil.index)
senha_valida = df_amil['Senha Aprovação'].fillna('').astype(str).str.strip() != '' if 'Senha Aprovação' in df_amil.columns else pd.Series(False, index=df_amil.index)
status_autorizado = df_amil['Status Aut Orç'].fillna('').astype(str).str.strip() == 'Autorizado' if 'Status Aut Orç' in df_amil.columns else pd.Series(False, index=df_amil.index)

df_amil['Is_Input_Feito'] = guia_valida_num | senha_valida | status_autorizado

# --- CONTAGEM FÍSICA E ÚNICA POR PACIENTE (EVITA DUPLICAR SE FOR O MESMO PACIENTE EM MAIS DE UM SETOR) ---
# Removemos duplicidades considerando o par (Colaborador, ID Prontuário) para contar "por cabeça"
df_pacientes_unicos = df_amil.drop_duplicates(subset=[col_responsavel, col_prontuario]).copy()

df_pacientes_unicos['Qtd_ID'] = df_pacientes_unicos['Classific_Agrupada'] == 'ID'
df_pacientes_unicos['Qtd_AD'] = df_pacientes_unicos['Classific_Agrupada'] == 'AD'

# Agrupando a quantidade física de pacientes por colaborador
prod_colaborador = df_pacientes_unicos.groupby(col_responsavel).agg(
    Pacientes_ID=('Qtd_ID', 'sum'),
    Pacientes_AD=('Qtd_AD', 'sum'),
    Total_Pacientes=(col_prontuario, 'count') # Total absoluto de pacientes únicos alocados
).reset_index()

# Agrupando o total de inputs (contagem bruta de quantas linhas/pendências foram processadas com sucesso no portal)
df_inputs_totais = df_amil.groupby(col_responsavel)['Is_Input_Feito'].sum().reset_index()

# Mesclando as tabelas operacionais em um único resumo de equipe
resumo_equipe = pd.merge(prod_colaborador, df_inputs_totais, on=col_responsavel)

# Nomeando colunas para a tabela final do Streamlit
resumo_equipe.columns = [
    'Colaborador', 
    'Nº Pacientes ID', 
    'Nº Pacientes AD', 
    'Quantitativo Total Pacientes', 
    'Total de Inputs Realizados'
]

# --- CONSTRUÇÃO DA INTERFACE VISUAL NO STREAMLIT ---
st.title("👥 Produtividade e Carga da Equipe")
st.markdown("Esta seção apresenta a análise **quantitativa e operacional** (volume físico de pacientes e ações) por funcionário responsável.")

# Exibindo a tabela com os contadores numéricos puros (formatados como inteiros)
st.dataframe(resumo_equipe.style.format({
    'Nº Pacientes ID': '{:,.0f}',
    'Nº Pacientes AD': '{:,.0f}',
    'Quantitativo Total Pacientes': '{:,.0f}',
    'Total de Inputs Realizados': '{:,.0f}'
}), use_container_width=True)

# --- GRÁFICO DE ANÁLISE DE CARGA (PACIENTES REAL - BARRAS EMPILHADAS) ---
st.subheader("📊 Distribuição Física de Pacientes Ativos")

# Criando dataframe no formato longo para alimentar corretamente o Plotly Express
df_grafico_equipe = df_pacientes_unicos[df_pacientes_unicos['Classific_Agrupada'].isin(['ID', 'AD'])].groupby(
    [col_responsavel, 'Classific_Agrupada']
).size().reset_index(name='Quantidade de Pacientes')

fig_carga_trabalho = px.bar(
    df_grafico_equipe,
    x=col_responsavel,
    y='Quantidade de Pacientes',
    color='Classific_Agrupada',
    title="Volume de Pacientes sob Responsabilidade Direta (AD vs ID)",
    labels={col_responsavel: 'Colaborador', 'Quantidade de Pacientes': 'Nº de Pacientes Ativos (Únicos)', 'Classific_Agrupada': 'Classificação'},
    barmode='stack', # Garante que as duas categorias fiquem empilhadas mostrando o volume total no topo
    color_discrete_map={'ID': '#1a365d', 'AD': '#2b6cb0'} # Paleta em tons de azul escuro e claro
)

st.plotly_chart(fig_carga_trabalho, use_container_width=True)
