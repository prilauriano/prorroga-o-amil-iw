# --- ⚙️ PLANILHA 2 (SETORES) ---
        atendimentos_pendentes_setores = set()
        setores_agrupados = None
        df_s_consolidado = pd.DataFrame()
        
        if arquivos_setores:
            lista_dfs_setores = []
            for arq_s in arquivos_setores:
                # CORREÇÃO DE CODIFICAÇÃO AQUI
                if arq_s.name.endswith('.csv'):
                    try: 
                        df_s_temp = pd.read_csv(arq_s, sep=';', encoding='utf-8')
                    except: 
                        arq_s.seek(0)
                        df_s_temp = pd.read_csv(arq_s, sep=';', encoding='iso-8859-1')
                else:
                    df_s_temp = pd.read_excel(arq_s)
                    
                df_s_temp.columns = df_s_temp.columns.str.strip()
                lista_dfs_setores.append(df_s_temp)
            
            df_s_consolidado = pd.concat(lista_dfs_setores, ignore_index=True)
