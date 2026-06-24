# --- ADICIONE ESTE BLOCO DENTRO DA ABA 1 (Resumo Geral) ---

if df_s_consolidado is not None:
    st.markdown("---")
    st.markdown("### 🏢 Pendências de Relatório por Setor Multidisciplinar")
    
    # Cruzando os dados da planilha principal (valores) com a de setores (pendências)
    df_amil_v = df[['Nr. Atendimento', 'Valor a Cobrar']].copy()
    df_setores_valores = pd.merge(df_s_consolidado, df_amil_v, left_on='Nº Atendimento', right_on='Nr. Atendimento', how='left')
    
    analise_setores = df_setores_valores.groupby('Grupo Especialidade').agg(
        Quantidade=('ID Pront.', 'count'),
        Valor_Total=('Valor a Cobrar', 'sum')
    ).reset_index()
    
    set_col1, set_col2 = st.columns(2)
    with set_col1:
        st.write("**Quantidade de Relatórios Pendentes por Setor**")
        st.bar_chart(analise_setores, x='Grupo Especialidade', y='Quantidade', color='#5C1220')
    with set_col2:
        st.write("**Impacto Financeiro Bloqueado por Setor (R$)**")
        st.bar_chart(analise_setores, x='Grupo Especialidade', y='Valor_Total', color='#C07C20')
