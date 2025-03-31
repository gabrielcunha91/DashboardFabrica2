import pandas as pd
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *


def config_despesas_por_classe(df):
  df = df.drop(df[df['Classificacao_Contabil_1'].isin(['Custo Mercadoria Vendida', 'Faturamento Bruto'])].index)

  df = df.sort_values(by=['Classificacao_Contabil_1', 'Classificacao_Contabil_2'])
  df = df.groupby(['Classificacao_Contabil_1', 'Classificacao_Contabil_2', 'Loja'], as_index=False).agg({
    'Orcamento': 'first',
    'Valor_Liquido': 'sum'
  })

  df = df.groupby(['Classificacao_Contabil_1', 'Classificacao_Contabil_2'], as_index=False).agg({
    'Orcamento': 'sum',
    'Valor_Liquido': 'sum'
  })

  df['Orcamento'] = df['Orcamento'].fillna(0)

  formatted_rows = []
  current_category = None

  df = df.drop(df[(df['Orcamento'] == 0) & (df['Valor_Liquido'] == 0)].index)

  for _, row in df.iterrows():
    if row['Classificacao_Contabil_1'] != current_category:
      current_category = row['Classificacao_Contabil_1']
      formatted_rows.append({'Classificacao_Contabil_1': current_category, 'Classificacao_Contabil_2': '', 'Orcamento': None, 'Valor_Liquido': None})
    formatted_rows.append({'Classificacao_Contabil_1': '', 'Classificacao_Contabil_2': row['Classificacao_Contabil_2'], 'Orcamento': row['Orcamento'], 'Valor_Liquido': row['Valor_Liquido']})

  df = pd.DataFrame(formatted_rows)
  df = df.rename(columns={'Classificacao_Contabil_1': 'Class. Contábil 1', 'Classificacao_Contabil_2': 'Class. Contábil 2',
                          'Orcamento': 'Orçamento', 'Valor_Liquido': 'Valor Realizado'})

  df['Orçamento'] = pd.to_numeric(df['Orçamento'], errors='coerce')
  df['Valor Realizado'] = pd.to_numeric(df['Valor Realizado'], errors='coerce')
  df.fillna({'Orçamento': 0, 'Valor Realizado': 0}, inplace=True)
  df['Orçamento'] = df['Orçamento'].astype(float)
  df['Valor Realizado'] = df['Valor Realizado'].astype(float)

  df['Orçamento - Realiz.'] = df['Orçamento'] - df['Valor Realizado']
  df['Atingimento do Orçamento'] = (df['Valor Realizado']/df['Orçamento']) *100

  df = format_columns_brazilian(df, ['Orçamento', 'Valor Realizado', 'Orçamento - Realiz.', 'Atingimento do Orçamento'])
  df['Atingimento do Orçamento'] = df['Atingimento do Orçamento'].apply(lambda x: x + '%')

  # Remover zeros nas linhas das classes
  for col in ['Orçamento', 'Valor Realizado', 'Orçamento - Realiz.', 'Atingimento do Orçamento']:
    df.loc[df['Class. Contábil 2'] == '', col] = ''

  df.loc[df['Atingimento do Orçamento'] == 'inf%', 'Atingimento do Orçamento'] = 'Não há Orçamento'

  return df

def config_despesas_detalhado(df):
  df = df.rename(columns = {'ID': 'ID Despesa', 'Loja': 'Loja', 'Classificacao_Contabil_1': 'Class. Contábil 1', 'Classificacao_Contabil_2': 'Class. Contábil 2', 'Fornecedor': 'Fornecedor', 'Doc_Serie': 'Doc_Serie', 'Data_Emissao': 'Data Emissão',
                             'Data_Vencimento': 'Data Vencimento', 'Descricao': 'Descrição', 'Status': 'Status', 'Valor_Liquido': 'Valor'})

  df = format_date_brazilian(df, 'Data Emissão')
  df = format_date_brazilian(df, 'Data Vencimento')

  df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
  df.fillna({'Valor': 0}, inplace=True)
  df['Valor'] = df['Valor'].astype(float)

  cols = ['ID Despesa', 'Loja', 'Fornecedor', 'Doc_Serie', 'Valor', 'Data Emissão', 'Data Vencimento', 'Descrição', 'Class. Contábil 1', 'Class. Contábil 2', 'Status']
  
  return df[cols]
