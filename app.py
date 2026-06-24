import streamlit as st
import pandas as pd
import plotly.express as px

# --- TRATAMENTO DOS DADOS PARA A VISÃO QUANTITATIVA DE EQUIPE ---
# 1. Limpeza de colunas para evitar erros de acentuação do arquivo original
df_amil.columns = df_amil.columns.str.strip()

# Ajustando dinamicamente o nome da coluna de classificação por causa de encoding
col_classificacao = [c for c in df_amil.columns if 'Classific' in c][0]
col_paciente = [c for c in df_amil.columns if 'Paciente' in c][0]
col_prontuario = [c for c in df_amil.columns if 'Pront' in c][0]
col_responsavel = [c for c in df_amil.columns if 'Resp' in c or 'Colaborador' in c][0] # Ajuste se for 'Pessoa Resp Aut'

# 2. Padronizar Classificação de Atendimento (ID vs AD)
df_amil['Classific_Agrupada'] = df_amil[col_classificacao].fillna('').astype(str).apply(
    lambda x: 'ID' if x.strip().startswith('ID') else ('AD' if x.strip().startswith('AD') else 'Outros')
)

# 3. Identificar se o Input/Inserção foi validado no portal Amil
# (Ajuste os nomes das colunas de guias/senhas de acordo com o seu df_amil principal se necessário)
guia_valida_num = df_amil['Nº Guia Solicitação (TISS)'].fillna('').astype(str).str.strip().str.isnumeric() if 'Nº Guia Solicitação (TISS)' in df_amil.columns else pd.Series(False, index=df_amil.index)
senha_valida = df_amil['Senha Aprovação'].fillna('').astype(str).str.strip() != '' if 'Senha Aprovação' in df_amil.columns else pd.Series(False, index=df_amil.index)
status_autorizado = df_amil['Status Aut Orç'].fillna('').astype(str).str.strip() == 'Autorizado' if 'Status Aut Orç' in df_amil.columns else pd.Series(False, index=df_amil.index)

df_amil['Is_Input_Feito'] = guia_valida_num | senha_valida | status_autorizado

# --- CONTAGEM REAL E ÚNICA DE PACIENTES POR COLABORADOR ---
# Removemos duplicidades de linhas para contar o PACIENTE de fato, garantindo o ID/AD correto
df_pacientes_unicos = df_amil.drop_duplicates(subset=[col_responsavel, col_prontuario]).copy()

# Criando colunas de checagem para a soma quantitativa
df_pacientes_unicos['Qtd_ID'] = df_pacientes_unicos['Classific_Agrupada'] == 'ID'
df_pacientes_unicos['Qtd_AD'] = df_pacientes_unicos['Classific_Agrupada'] == 'AD'

# Agrupando para consolidar os totais físicos da equipe
prod_colaborador = df_pacientes_unicos.groupby(col_responsavel).agg(
    Pacientes_ID=('Qtd_ID', 'sum'),
    Pacientes_AD=('Qtd_AD', 'sum'),
    Total_Pacientes=(col_prontuario, 'count') # Conta o número real e físico de pacientes atribuídos
).reset_index()

# Para os inputs, contamos quantas linhas de pendências gerais foram resolvidas/inseridas no portal por colaborador
df_inputs = df_amil.groupby(col_responsavel)['Is_Input_Feito'].sum().reset_index()

# Unificando a tabela final de métricas
resumo_equipe = pd.merge(prod_colaborador, df_inputs, on=col_responsavel)

# Renomeando para exibição limpa na tela
resumo_equipe.columns = [
    'Colaborador', 
    'Nº Pacientes ID', 
    'Nº Pacientes AD', 
    'Quantitativo Total Pacientes', 
    'Total de Inputs Realizados'
]

# --- RENDERIZAÇÃO NA INTERFACE STREAMLIT ---
st.title("👥 Gestão de Carga de Trabalho da Equipe")
st.markdown("Esta tabela apresenta o **volume físico e absoluto** de pacientes únicos e de procedimentos por colaborador.")

# Exibição da tabela formatada sem cifras monetárias
st.dataframe(resumo_equipe.style.format({
    'Nº Pacientes ID': '{:,.0f}',
    'Nº Pacientes AD': '{:,.0f}',
    'Quantitativo Total Pacientes': '{:,.0f}',
    'Total de Inputs Realizados': '{:,.0f}'
}), use_container_width=True)

# --- GRÁFICO DE BARRAS EMPILHADAS (MÉTRICA PURAMENTE QUANTITATIVA) ---
st.subheader("📊 Distribuição de Carga (Número de Pacientes Físicos)")

# Monta o dataframe longo com pacientes únicos para alimentar o gráfico do Plotly
df_grafico_longo = df_pacientes_unicos[df_pacientes_unicos['Classific_Agrupada'].isin(['ID', 'AD'])].groupby(
    [col_responsavel, 'Classific_Agrupada']
).size().reset_index(name='Quantidade de Pacientes')

fig_carga = px.bar(
    df_grafico_longo,
    x=col_responsavel,
    y='Quantidade de Pacientes',
    color='Classific_Agrupada',
    title="Volume de Pacientes Únicos por Funcionário (AD vs ID)",
    labels={col_responsavel: 'Colaborador', 'Quantidade de Pacientes': 'Nº de Pacientes Ativos', 'Classific_Agrupada': 'Classificação'},
    barmode='stack', # Empilha AD e ID para que o topo da barra mostre o volume total físico do funcionário
    color_discrete_map={'ID': '#003366', 'AD': '#3399ff'} # Cores corporativas em tons de azul
)

st.plotly_chart(fig_carga, use_container_width=True)
