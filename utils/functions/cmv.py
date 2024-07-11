import pandas as pd
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *


def merge_dataframes(dfs):
  merged_df = dfs[0]
  suffixes = ['', '_df2', '_df3', '_df4', '_df5', '_df6']

  for i, df in enumerate(dfs[1:], start=1):
    merged_df = merged_df.merge(df, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', suffixes[i]))

  merged_df.fillna(0, inplace=True)
  merged_df.infer_objects(copy=False)

  merged_df['Compras_Alimentos'] = merged_df['BlueMe_Sem_Pedido_Alimentos'] + merged_df['BlueMe_Com_Pedido_Valor_Liq_Alimentos']
  merged_df['Compras_Bebidas'] = merged_df['BlueMe_Sem_Pedido_Bebidas'] + merged_df['BlueMe_Com_Pedido_Valor_Liq_Bebidas']

  selected_columns = ['ID_Loja', 'Loja', 'Primeiro_Dia_Mes', 'Faturam_Bruto_Aliment', 
                      'Faturam_Bruto_Bebidas', 'Estoque_Inicial_Alimentos', 
                      'Estoque_Final_Alimentos', 'Estoque_Inicial_Bebidas', 
                      'Estoque_Final_Bebidas', 'Estoque_Inicial_Descart_Hig_Limp', 
                      'Estoque_Final_Descart_Hig_Limp', 'BlueMe_Sem_Pedido_Alimentos', 
                      'BlueMe_Com_Pedido_Valor_Liq_Alimentos', 'Compras_Alimentos', 
                      'BlueMe_Sem_Pedido_Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas', 
                      'Compras_Bebidas', 'Entrada_Transf_Alim', 'Saida_Transf_Alim', 
                      'Entrada_Transf_Bebidas', 'Saida_Transf_Bebidas', 
                      'Consumo_Interno', 'Quebras_e_Perdas']

  result_df = merged_df[selected_columns]
  return result_df


def config_tabelas_iniciais_cmv(lojas_selecionadas, data_inicio, data_fim):
  df1 = GET_FATURAM_ZIG_ALIM_BEB_MENSAL()
  df2 = GET_ESTOQUES_POR_CATEG_AGRUPADOS()
  df3 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_SEM_PEDIDO()  
  df4 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_coM_PEDIDO()
  df5 = GET_TRANSF_ESTOQUE_AGRUPADOS()  
  df6 = GET_PERDAS_E_CONSUMO_AGRUPADOS()

  df3 = df3[df3['ID_Loja'] != 296]

  dfs = [df1, df2, df3, df4, df5, df6]
  for i, df in enumerate(dfs):
    df_filtrado = filtrar_por_classe_selecionada(df, 'Loja', lojas_selecionadas)
    df_filtrado = filtrar_por_datas(df_filtrado, data_inicio, data_fim, 'Primeiro_Dia_Mes')
    dfs[i] = df_filtrado

  df1, df2, df3, df4, df5, df6 = dfs

  dfFinal = merge_dataframes(dfs)
  return dfFinal

def config_tabela_CMV(df):
  df = pd.DataFrame(df)
  newDF = df.drop(['ID_Loja', 'BlueMe_Sem_Pedido_Alimentos', 'BlueMe_Com_Pedido_Valor_Liq_Alimentos', 
                   'Compras_Alimentos', 'BlueMe_Sem_Pedido_Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas', 
                   'Compras_Bebidas', 'Entrada_Transf_Alim', 'Saida_Transf_Alim', 'Entrada_Transf_Bebidas', 
                   'Saida_Transf_Bebidas', 'Consumo_Interno', 'Quebras_e_Perdas', ], axis=1)
  
  newDF.rename(columns = {'Loja': 'Loja', 'Primeiro_Dia_Mes': 'Mês', 'Faturam_Bruto_Aliment': 'Faturam. Alim.', 
                         'Estoque_Inicial_Alimentos': 'Estoque Inicial Alim.', 'Estoque_Final_Alimentos': 'Estoque Final Alim.',
                          'Faturam_Bruto_Bebidas': 'Faturam. Bebidas', 'Estoque_Inicial_Bebidas': 'Estoque Inicial Bebidas', 
                         'Estoque_Final_Bebidas': 'Estoque Final Bebidas', 'Estoque_Inicial_Descart_Hig_Limp': 'Estoque Inicial Limp/Hig', 
                         'Estoque_Final_Descart_Hig_Limp': 'Estoque Final Limp/Hig'}, inplace=True)
  
  newDF = format_date_brazilian(newDF, 'Mês')
  return newDF

def config_tabela_compras(df):
  df = pd.DataFrame(df)
  newDF = df.drop(['ID_Loja', 'Faturam_Bruto_Aliment', 'Faturam_Bruto_Bebidas', 
                   'Estoque_Inicial_Alimentos', 'Estoque_Final_Alimentos', 'Estoque_Inicial_Bebidas', 
                   'Estoque_Final_Bebidas', 'Estoque_Inicial_Descart_Hig_Limp', 
                   'Estoque_Final_Descart_Hig_Limp', 'Entrada_Transf_Alim', 'Saida_Transf_Alim', 
                   'Entrada_Transf_Bebidas', 'Saida_Transf_Bebidas', 'Consumo_Interno', 'Quebras_e_Perdas', ], axis=1)
  
  newDF.rename(columns = {'Loja': 'Loja', 'Primeiro_Dia_Mes': 'Mês', 'Compras_Alimentos': 'Compras Alim.', 'BlueMe_Sem_Pedido_Alimentos': 'BlueMe S/ Pedido Alim.', 
                          'BlueMe_Com_Pedido_Valor_Liq_Alimentos': 'BlueMe C/ Pedido Alim.',  'Compras_Bebidas': 'Compras Bebidas',
                          'BlueMe_Sem_Pedido_Bebidas': 'BlueMe S/ Pedido Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas': 'BlueMe C/ Pedido Bebidas'},
                          inplace=True)

  newDF = format_date_brazilian(newDF, 'Mês')
  return newDF

def config_tabela_transferencias(df):
  df = pd.DataFrame(df)
  newDF = df.drop(['ID_Loja', 'Faturam_Bruto_Aliment', 'Faturam_Bruto_Bebidas', 'Estoque_Inicial_Alimentos', 'Estoque_Final_Alimentos', 
                   'Estoque_Inicial_Bebidas', 'Estoque_Final_Bebidas', 'Estoque_Inicial_Descart_Hig_Limp', 
                   'Estoque_Final_Descart_Hig_Limp', 'BlueMe_Sem_Pedido_Alimentos', 'BlueMe_Com_Pedido_Valor_Liq_Alimentos', 
                   'Compras_Alimentos', 'BlueMe_Sem_Pedido_Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas', 'Compras_Bebidas'], axis=1)
  
  newDF.rename(columns = {'Loja': 'Loja', 'Primeiro_Dia_Mes': 'Mês', 'Entrada_Transf_Alim': 'Entrada Transf. Alim.', 'Saida_Transf_Alim': 'Saida Transf. Alim.', 
                          'Entrada_Transf_Bebidas': 'Entrada Transf. Bebidas', 'Saida_Transf_Bebidas': 'Saida Transf. Bebidas', 
                          'Consumo_Interno': 'Consumo Interno', 'Quebras_e_Perdas': 'Quebras e Perdas'}, inplace=True)

  newDF = format_date_brazilian(newDF, 'Mês')
  return newDF

def config_insumos_blueme_sem_pedido(df, data_inicio, data_fim):
  df = pd.DataFrame(df)
  df = df.drop(['ID_Loja', 'Primeiro_Dia_Mes'], axis=1)
  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data_Emissao')

  df = format_date_brazilian(df, 'Data_Emissao')

  df.rename(columns = {'tdr_ID': 'tdr ID', 'Loja': 'Loja', 'Fornecedor': 'Fornecedor', 'Plano_de_Contas': 'Classificacao',
                       'Doc_Serie': 'Doc_Serie', 'Data_Emissao': 'Data Emissão', 'Valor_Liquido': 'Valor Líquido'}, inplace=True)
  df['Valor Líquido'] = df['Valor Líquido'].astype(float)
  return df


def config_insumos_blueme_com_pedido(df, data_inicio, data_fim):
  df = pd.DataFrame(df)
  df = df.drop(['ID_Loja', 'Primeiro_Dia_Mes'], axis=1)
  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data_Emissao')

  df = format_date_brazilian(df, 'Data_Emissao')

  df['Valor_Insumos'] = df['Valor_Insumos'].astype(float)
  df['Valor_Liquido'] = df['Valor_Liquido'].astype(float)
  df['Insumos - V. Líq'] = df['Valor_Insumos'] - df['Valor_Liquido']

  df.rename(columns = {'tdr_ID': 'tdr ID', 'Loja': 'Loja', 'Fornecedor': 'Fornecedor', 'Doc_Serie': 'Doc_Serie', 'Data_Emissao': 'Data Emissão',
                       'Valor_Liquido': 'Valor Líquido', 'Valor_Insumos': 'Valor Insumos', 'Valor_Liq_Alimentos': 'Valor Líq. Alimentos',
                       'Valor_Liq_Bebidas': 'Valor Líq. Bebidas', 'Valor_Liq_Descart_Hig_Limp': 'Valor Líq. Hig/Limp.', 
                       'Valor_Liq_Outros': 'Valor Líq. Outros'}, inplace=True)

  nova_ordem = ['tdr ID', 'Loja', 'Fornecedor', 'Doc_Serie', 'Data Emissão', 'Valor Líquido', 'Valor Insumos', 'Insumos - V. Líq', 'Valor Líq. Alimentos',
                'Valor Líq. Bebidas', 'Valor Líq. Hig/Limp.', 'Valor Líq. Outros']
  df = df[nova_ordem]

  return df

