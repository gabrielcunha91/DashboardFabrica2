import pandas as pd
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *


def merge_dataframes(df1, df2, df3, df4, df5, df6):
  # Realiza a junção das tabelas
  merged_df = df1.merge(df2, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df2'))
  merged_df = merged_df.merge(df3, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df3'))
  merged_df = merged_df.merge(df4, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df4'))
  merged_df = merged_df.merge(df5, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df5'))
  merged_df = merged_df.merge(df6, on=['ID_Loja', 'Primeiro_Dia_Mes'], how='left', suffixes=('', '_df6'))

  # Preenche os valores nulos com zero (similar ao COALESCE)
  merged_df.fillna(0, inplace=True)
  merged_df.infer_objects(copy=False)

  # Calcular as colunas de compras (alimentos e bebidas)
  merged_df['Compras_Alimentos'] = (merged_df['BlueMe_Sem_Pedido_Alimentos'] + 
                                    merged_df['BlueMe_Com_Pedido_Valor_Liq_Alimentos'])
  merged_df['Compras_Bebidas'] = (merged_df['BlueMe_Sem_Pedido_Bebidas'] + 
                                  merged_df['BlueMe_Com_Pedido_Valor_Liq_Bebidas'])

  # Selecionar as colunas conforme a query SQL original
  result_df = merged_df[['ID_Loja', 'Loja', 'Primeiro_Dia_Mes', 'Faturam_Bruto_Aliment', 
                         'Faturam_Bruto_Bebidas', 'Estoque_Inicial_Alimentos', 
                         'Estoque_Final_Alimentos', 'Estoque_Inicial_Bebidas', 
                         'Estoque_Final_Bebidas', 'Estoque_Inicial_Descart_Hig_Limp', 
                         'Estoque_Final_Descart_Hig_Limp', 'BlueMe_Sem_Pedido_Alimentos', 
                         'BlueMe_Com_Pedido_Valor_Liq_Alimentos', 'Compras_Alimentos', 
                         'BlueMe_Sem_Pedido_Bebidas', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas', 
                         'Compras_Bebidas', 'Entrada_Transf_Alim', 
                         'Saida_Transf_Alim', 'Entrada_Transf_Bebidas', 
                         'Saida_Transf_Bebidas', 'Consumo_Interno', 'Quebras_e_Perdas']]
  return result_df

def config_tabelas_iniciais_cmv(lojas_selecionadas, data_inicio, data_fim):
  df1 = GET_FATURAM_ZIG_ALIM_BEB_MENSAL()
  df2 = GET_ESTOQUES_POR_CATEG_AGRUPADOS()
  df3 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_SEM_PEDIDO()  
  df4 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_coM_PEDIDO()
  df5 = GET_TRANSF_ESTOQUE_AGRUPADOS()  
  df6 = GET_PERDAS_E_CONSUMO_AGRUPADOS()

  df3 = df3[df3['ID_Loja'] != 296]

  df1 = filtrar_por_classe_selecionada(df1, 'Loja' , lojas_selecionadas)
  df1 = filtrar_por_datas(df1, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df2 = filtrar_por_classe_selecionada(df2, 'Loja' , lojas_selecionadas)
  df2 = filtrar_por_datas(df2, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df3 = filtrar_por_classe_selecionada(df3, 'Loja' , lojas_selecionadas)
  df3 = filtrar_por_datas(df3, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df4 = filtrar_por_classe_selecionada(df4, 'Loja' , lojas_selecionadas)
  df4 = filtrar_por_datas(df4, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df5 = filtrar_por_classe_selecionada(df5, 'Loja' , lojas_selecionadas)
  df5 = filtrar_por_datas(df5, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df6 = filtrar_por_classe_selecionada(df6, 'Loja' , lojas_selecionadas)
  df6 = filtrar_por_datas(df6, data_inicio, data_fim, 'Primeiro_Dia_Mes')

  dfFinal = merge_dataframes(df1, df2, df3, df4, df5, df6)
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

