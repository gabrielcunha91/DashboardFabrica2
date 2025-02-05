import pandas as pd
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *


def config_despesas_por_classe(df):
  df = df[df['Class_Plano_de_Contas'] != 'a. Compras de Alimentos, Bebidas e Embalagens']
  df = df.sort_values(by=['Class_Plano_de_Contas', 'Plano_de_Contas'])
  df = df.groupby(['Class_Plano_de_Contas', 'Plano_de_Contas'], as_index=False).agg({
    'Orcamento': 'sum',
    'ID': 'count',
    'Valor_Liquido': 'sum'
  }).rename(columns={'ID': 'Qtd_Lancamentos'})

  df['Orcamento'] = df['Orcamento'].fillna(0)
  df['Orcamento'] = df.apply(lambda row: row['Orcamento'] / row['Qtd_Lancamentos'] if row['Qtd_Lancamentos'] > 0 else row['Orcamento'], axis=1)


  formatted_rows = []
  current_category = None

  for _, row in df.iterrows():
    if row['Class_Plano_de_Contas'] != current_category:
      current_category = row['Class_Plano_de_Contas']
      formatted_rows.append({'Class_Plano_de_Contas': current_category, 'Plano_de_Contas': '', 'Qtd_Lancamentos': None, 'Orcamento': None, 'Valor_Liquido': None})
    formatted_rows.append({'Class_Plano_de_Contas': '', 'Plano_de_Contas': row['Plano_de_Contas'], 'Qtd_Lancamentos': row['Qtd_Lancamentos'], 'Orcamento': row['Orcamento'], 'Valor_Liquido': row['Valor_Liquido']})

  df = pd.DataFrame(formatted_rows)
  df = df.rename(columns={'Class_Plano_de_Contas': 'Classe Plano de Contas', 'Plano_de_Contas': 'Plano de Contas', 'Qtd_Lancamentos': 'Qtd. de Lançamentos', 
                          'Orcamento': 'Orçamento', 'Valor_Liquido': 'Valor Realizado'})

  df['Orçamento'] = pd.to_numeric(df['Orçamento'], errors='coerce')
  df['Valor Realizado'] = pd.to_numeric(df['Valor Realizado'], errors='coerce')
  df.fillna({'Orçamento': 0, 'Valor Realizado': 0}, inplace=True)
  df['Orçamento'] = df['Orçamento'].astype(float)
  df['Valor Realizado'] = df['Valor Realizado'].astype(float)

  df['Orçamento - Realiz.'] = df['Orçamento'] - df['Valor Realizado']

  df = format_columns_brazilian(df, ['Orçamento', 'Valor Realizado', 'Orçamento - Realiz.'])

  # Converter 'Qtd. de Lançamentos' para int e substituir valores nas linhas das classes
  df['Qtd. de Lançamentos'] = df['Qtd. de Lançamentos'].fillna(0).astype(int)
  df['Qtd. de Lançamentos'] = df['Qtd. de Lançamentos'].astype(str)
  df.loc[df['Plano de Contas'] == '', 'Qtd. de Lançamentos'] = ''

  # Remover zeros nas linhas das classes
  for col in ['Orçamento', 'Valor Realizado', 'Orçamento - Realiz.']:
    df.loc[df['Plano de Contas'] == '', col] = ''

  return df

def config_despesas_detalhado(df):
  df.drop(['Orcamento', 'Class_Plano_de_Contas'], axis=1, inplace=True)
  df = df.rename(columns = {'Loja': 'Loja', 'Plano_de_Contas' : 'Plano de Contas', 'Fornecedor': 'Fornecedor', 'Doc_Serie': 'Doc_Serie', 'Data_Evento': 'Data Emissão',
                             'Data_Vencimento': 'Data Vencimento', 'Descricao': 'Descrição', 'Status': 'Status', 'Valor_Liquido': 'Valor'})

  df = format_date_brazilian(df, 'Data Emissão')
  df = format_date_brazilian(df, 'Data Vencimento')

  df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
  df.fillna({'Valor': 0}, inplace=True)
  df['Valor'] = df['Valor'].astype(float)

  cols = ['Loja', 'Fornecedor', 'Doc_Serie', 'Valor', 'Data Emissão', 'Data Vencimento', 'Descrição', 'Plano de Contas', 'Status']
  
  return df[cols]
