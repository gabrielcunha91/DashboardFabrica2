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
         
