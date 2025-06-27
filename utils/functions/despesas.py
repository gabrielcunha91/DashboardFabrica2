import pandas as pd
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *


def config_despesas_por_classe(df):
    df = df.drop(
        df[
            df["Classificacao_Contabil_1"].isin(
                ["Custo Mercadoria Vendida", "Faturamento Bruto"]
            )
        ].index
    )

    # Sua lista com a ordem desejada
    ordem_DRE = [
        "Impostos sobre Venda",
        "Custos Artístico Geral",
        "Custos de Eventos",
        "Deduções sobre Venda",
        "Mão de Obra - PJ",
        "Mão de Obra - Salários",
        "Mão de Obra - Extra",
        "Mão de Obra - Encargos e Provisões",
        "Mão de Obra - Benefícios",
        "Mão de Obra - Pro Labores",
        "Gorjeta",
        "Custo de Ocupação",
        "Utilidades",
        "Informática e TI",
        "Despesas com Transporte / Hospedagem",
        "Manutenção",
        "Marketing",
        "Serviços de Terceiros",
        "Locação de Equipamentos",
        "Sistema de Franquias",
        "Despesas Financeiras",
        "Patrocínio",
        "Dividendos e Remunerações Variáveis",
        "Endividamento",
        "Imposto de Renda",
        "Investimento - CAPEX"
    ]

    df = df.sort_values(by=["Classificacao_Contabil_1", "Classificacao_Contabil_2"])

    df = df.groupby(
        ["Classificacao_Contabil_1", "Classificacao_Contabil_2"], as_index=False
    ).agg({"Orcamento": "sum", "Valor_Liquido": "sum"})

    df["Orcamento"] = df["Orcamento"].fillna(0)
    df['Classificacao_Contabil_1'] = pd.Categorical(df['Classificacao_Contabil_1'], categories=ordem_DRE, ordered=True)
    df = df.sort_values('Classificacao_Contabil_1', na_position='last')
    
    df = df.rename(
        columns={
            "Classificacao_Contabil_1": "Class. Contábil 1",
            "Classificacao_Contabil_2": "Class. Contábil 2",
            "Orcamento": "Orçamento",
            "Valor_Liquido": "Valor Realizado",
        }
    )
    
    df["Orçamento"] = df["Orçamento"].astype(float)
    df["Valor Realizado"] = df["Valor Realizado"].astype(float)

    df["Orçamento - Realiz."] = df["Orçamento"] - df["Valor Realizado"]
    
    df["Atingimento do Orçamento"] = (df["Valor Realizado"] / df["Orçamento"]) * 100
    
    return df

def config_despesas_detalhado(df):
    df = df.rename(
        columns={
            "ID": "ID Despesa",
            "Loja": "Loja",
            "Classificacao_Contabil_1": "Class. Contábil 1",
            "Classificacao_Contabil_2": "Class. Contábil 2",
            "Fornecedor": "Fornecedor",
            "Doc_Serie": "Doc_Serie",
            "Data_Emissao": "Data Emissão",
            "Data_Vencimento": "Data Vencimento",
            "Descricao": "Descrição",
            "Status": "Status",
            "Valor_Liquido": "Valor",
        }
    )

    df = format_date_brazilian(df, "Data Emissão")
    df = format_date_brazilian(df, "Data Vencimento")

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df.fillna({"Valor": 0}, inplace=True)
    df["Valor"] = df["Valor"].astype(float)

    cols = [
        "ID Despesa",
        "Loja",
        "Fornecedor",
        "Doc_Serie",
        "Valor",
        "Data Emissão",
        "Data Vencimento",
        "Descrição",
        "Class. Contábil 1",
        "Class. Contábil 2",
        "Status",
    ]

    return df[cols]


def df_ordem_DRE(df):
    ordem_DRE = [
        "Custo Artístico Geral",
        "Custos de Eventos",
        "Deduções sobre Venda",
        "Mão de Obra - PJ"
        "Mão de Obra - Benefícios",
        "Mão de Obra - Extra",
        "Mão de Obra - Salários",
        "Custo de Ocupação",
        "Utilidades",
        "Informática e TI",
        "Manutenção",
        "Despesas com Transporte / Hospedagem",
        "Marketing",
        "Serviços de Terceiros",
        "Locação de Equipamentos",
        "Despesas Financeiras",
        "Investimento - CAPEX",
        "Dividendos e Remunerações Variáveis",
        "Gorjeta",
		"Endividamento"
    ]
    
	# Dataframe com as classificações na ordem da DRE
    df_ordenado = pd.DataFrame()
    for idx, tuple in df.iterrows():
        if tuple['Class. Contábil 1'] in ordem_DRE:
            df_ordenado = pd.concat([df_ordenado, pd.DataFrame([tuple])], ignore_index=True)
         

def exibir_despesas(despesasConfig, exibir_detalhamento=True, layout_impressao=False):
    despesasConfig = despesasConfig[~((despesasConfig['Orçamento'] == 0) & (despesasConfig['Valor Realizado'] == 0))]
    lista_class_contabil_1 = despesasConfig['Class. Contábil 1'].dropna().unique().tolist()
    altura_linha = 35
    altura_titulo = 55
    altura_cabecalho = 570
    altura_atual = altura_cabecalho
    altura_max_pagina = 1200
    for classe in lista_class_contabil_1:
        df_classe = despesasConfig[despesasConfig['Class. Contábil 1'] == classe]
        df_classe = df_classe.drop(columns=['Class. Contábil 1']).reset_index(drop=True)
        orcamento_total = df_classe['Orçamento'].sum()
        realizado_total = df_classe['Valor Realizado'].sum()
        orc_realiz_total = df_classe['Orçamento - Realiz.'].sum()
        if orcamento_total != 0:
            atingimento = (realizado_total / orcamento_total) * 100
        else:
            atingimento = "Não há orçamento"
        linha_total = pd.DataFrame({
          "Class. Contábil 2": ["Total"],
          "Orçamento": [orcamento_total],
          "Valor Realizado": [realizado_total],
          "Orçamento - Realiz.": [orc_realiz_total],
          "Atingimento do Orçamento": [atingimento],
        })

        df_classe = pd.concat([df_classe, linha_total], ignore_index=True)
        df_classe = format_columns_brazilian(
            df_classe,
            [
                "Orçamento",
                "Valor Realizado",
                "Orçamento - Realiz.",
                "Atingimento do Orçamento",
            ]
        )
        df_classe["Atingimento do Orçamento"] = df_classe["Atingimento do Orçamento"].apply(lambda x: f"{x} %")
        
        df_classe.loc[df_classe["Orçamento"] == '0,00', "Atingimento do Orçamento"] = ("Não há Orçamento")

        if not exibir_detalhamento:
          df_classe = df_classe.tail(1)
        
        df_despesas_styled = df_classe.style.map(highlight_values, subset=['Orçamento - Realiz.']).apply(highlight_total_row, axis=1)

        altura_dataframe = altura_linha * len(df_classe) + 35
        altura_secao = altura_titulo + altura_dataframe + 60

        if altura_atual + altura_secao > altura_max_pagina:
            st.markdown('<div style="page-break-before: always;"></div>', unsafe_allow_html=True)
            altura_atual = 40

        st.markdown(f"#### {classe}")
        st.dataframe(
            df_despesas_styled,
            height=altura_linha * len(df_classe) + 35,
            use_container_width=True,
            hide_index=True
        )
        altura_atual += altura_secao


def highlight_total_row(row):
    if row['Class. Contábil 2'] == 'Total':
        return [
            'background-color: #f0f2f6; color: black;' if col != 'Orçamento - Realiz.' else 'background-color: #f0f2f6;'
            for col in row.index
        ]
    else:
        return [''] * len(row)