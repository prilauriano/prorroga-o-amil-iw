import streamlit as st
import pandas as pd
import plotly.express as px

# --- PROCESSAMENTO DOS DADOS DA EQUIPE ---
# Certificando que as colunas chaves não possuem espaços e estão tratadas
df_amil.columns = df_amil.columns.str.strip()

# 1. Identificar Classificação (ID vs AD) de forma robusta baseado na coluna do seu arquivo
df_amil['Classific_Agrupada'] = df_amil['Classificação Atendimento'].fillna('').astype(str).apply(
    lambda x: 'ID' if x.startswith('ID') else ('AD' if x.startswith('AD') else 'Outros')
)

# 2. Identificar se o Input/Inserção foi feito no portal Amil (Baseado nos critérios definidos)
guia_valida_num = df_amil['Nº Guia Solicitação (TISS)'].fillna('').astype(str).str.strip().str.isnumeric()
senha_valida = df_amil['Senha Aprovação'].fillna('').astype(str).str.strip() != ''
status_autorizado = df_amil['Status Aut Orç'].fillna('').astype(str).str.strip() == 'Autorizado'
df_amil['Is_Input_Feito'] = guia_valida_num | senha_valida | status_autorizado

# 3. Criar colunas auxiliares para contagem por tipo
df_amil['Qtd_ID'] = df_amil['Classific_Agrupada'] == 'ID'
df_amil['Qtd_AD'] = df_amil['Classific_Agrupada'] == 'AD'

# 4. Agrupar por Colaborador (Pessoa Resp Aut) trazendo o quantitativo numérico de pacientes
prod_colaborador = df_amil.groupby('Pessoa Resp Aut').agg(
    Pacientes_ID=('Qtd_ID', 'sum'),
    Pacientes_AD=('Qtd_AD', 'sum'),
    Total_Pacientes=('Nome Paciente', 'count'),  # Quantitativo total bruto de pacientes (linhas)
    Inputs_Feitos=('Is_Input_Feito', 'sum')      # Quantidade de inserções validadas
).reset_index()

# Renomeando as colunas para exibição amigável na tabela
prod_colaborador.columns = [
    'Colaborador', 
    'Qtd Pacientes ID', 
    'Qtd Pacientes AD', 
    'Quantitativo Total de Pacientes', 
    'Total de Inputs Realizados'
]

# --- RENDERIZAÇÃO NA INTERFACE DO STREAMLIT ---
st.title("👥 Gestão de Equipe e Produtividade")
st.markdown("Visualização puramente quantitativa do volume de pacientes e inputs por colaborador.")

# Exibindo a tabela formatada com os números absolutos
st.dataframe(prod_colaborador.style.format({
    'Qtd Pacientes ID': '{:,.0f}',
    'Qtd Pacientes AD': '{:,.0f}',
    'Quantitativo Total de Pacientes': '{:,.0f}',
    'Total de Inputs Realizados': '{:,.0f}'
}), use_container_width=True)

# --- GRÁFICO VISUAL DE CARGA DE TRABALHO (ID vs AD) ---
st.subheader("📊 Distribuição de Carga de Trabalho por Complexidade")

# Preparando os dados para um gráfico do Plotly (derretendo a tabela para formato longo)
df_longo = df_amil[df_amil['Classific_Agrupada'].isin(['ID', 'AD'])].groupby(['Pessoa Resp Aut', 'Classific_Agrupada']).size().reset_index(name='Nº de Pacientes')

fig_equipe = px.bar(
    df_longo, 
    x='Pessoa Resp Aut', 
    y='Nº de Pacientes', 
    color='Classific_Agrupada',
    title="Volume de Pacientes por Colaborador (AD vs ID)",
    labels={'Pessoa Resp Aut': 'Colaborador', 'Nº de Pacientes': 'Número de Pacientes', 'Classific_Agrupada': 'Classificação'},
    barmode='stack', # Barras empilhadas para ver o total e a divisão ao mesmo tempo
    color_discrete_map={'ID': '#1f77b4', 'AD': '#aec7e8'} # Tons de azul para combinar com seu layout
)

st.plotly_chart(fig_equipe, use_container_width=True)
