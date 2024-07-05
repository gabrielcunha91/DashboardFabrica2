import streamlit as st
import pandas as pd
import numpy as np
from utils.queries import *
from workalendar.america import Brazil

taxa_credito_antecipado = 0.0265
taxa_credito_padrao = 0.016
taxa_debito = 0.0095
taxa_app = 0.0074
taxa_pix = 0.0074


# df_saldos_bancarios = GET_SALDOS_BANCARIOS()
# df_saldos_bancarios['Data'] = pd.to_datetime(df_saldos_bancarios['Data'])

# df_valor_liquido = GET_VALOR_LIQUIDO_RECEBIDO()
# df_valor_liquido['Data'] = pd.to_datetime(df_valor_liquido['Data'])

# df_projecao_zig = GET_PROJECAO_ZIG()
# df_projecao_zig['Data'] = pd.to_datetime(df_projecao_zig['Data'])

# df_receitas_extraord_proj = GET_RECEITAS_EXTRAORD_FLUXO_CAIXA()
# df_receitas_extraord_proj['Data'] = pd.to_datetime(df_receitas_extraord_proj['Data'])

# df_despesas_aprovadas = GET_DESPESAS_APROVADAS()
# df_despesas_aprovadas['Data'] = pd.to_datetime(df_despesas_aprovadas['Data'])

# df_despesas_pagas = GET_DESPESAS_PAGAS()
# df_despesas_pagas['Data'] = pd.to_datetime(df_despesas_pagas['Data'])


# Unindo os DataFrames usando merge
def config_projecao_bares():
  df_saldos_bancarios = GET_SALDOS_BANCARIOS()
  df_valor_liquido = GET_VALOR_LIQUIDO_RECEBIDO()
  df_projecao_zig = GET_PROJECAO_ZIG()
  df_receitas_extraord_proj = GET_RECEITAS_EXTRAORD_FLUXO_CAIXA()
  df_despesas_aprovadas = GET_DESPESAS_APROVADAS()
  df_despesas_pagas = GET_DESPESAS_PAGAS()

  dfs = [df_saldos_bancarios, df_valor_liquido, df_projecao_zig, df_receitas_extraord_proj, df_despesas_aprovadas, df_despesas_pagas]
  for df in dfs:
    df['Data'] = pd.to_datetime(df['Data'])


  merged_df = pd.merge(df_saldos_bancarios, df_valor_liquido, on=['Data', 'Empresa'], how='outer')
  merged_df = pd.merge(merged_df, df_projecao_zig, on=['Data', 'Empresa'], how='outer')
  merged_df = pd.merge(merged_df, df_receitas_extraord_proj, on=['Data', 'Empresa'], how='outer')
  merged_df = pd.merge(merged_df, df_despesas_aprovadas, on=['Data', 'Empresa'], how='outer')
  merged_df = pd.merge(merged_df, df_despesas_pagas, on=['Data', 'Empresa'], how='outer')

  merged_df = merged_df.fillna(0)
  merged_df = merged_df.rename(columns={'Valor_Projetado': 'Valor_Projetado_Zig'})
  merged_df = merged_df.sort_values(by='Data')
  merged_df = merged_df.reset_index(drop=True)

  # Ajustando formatação
  cols = ['Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord', 'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas']
  for col in cols:
    merged_df[col] = merged_df[col].astype(float).round(2)

  # merged_df['Saldo_Inicio_Dia'] = merged_df['Saldo_Inicio_Dia'].astype(float).round(2)
  # merged_df['Valor_Liquido_Recebido'] = merged_df['Valor_Liquido_Recebido'].astype(float).round(2)
  # merged_df['Valor_Projetado_Zig'] = merged_df['Valor_Projetado_Zig'].astype(float).round(2)
  # merged_df['Receita_Projetada_Extraord'] = merged_df['Receita_Projetada_Extraord'].astype(float).round(2)
  # merged_df['Despesas_Aprovadas_Pendentes'] = merged_df['Despesas_Aprovadas_Pendentes'].astype(float).round(2)
  # merged_df['Despesas_Pagas'] = merged_df['Despesas_Pagas'].astype(float).round(2)


  merged_df['Valor_Projetado_Zig'] = merged_df.apply(lambda row: 0 if row['Valor_Liquido_Recebido'] > 0 else row['Valor_Projetado_Zig'], axis=1)
  merged_df['Saldo_Final'] = merged_df['Saldo_Inicio_Dia'] + merged_df['Valor_Liquido_Recebido'] + merged_df['Valor_Projetado_Zig'] + merged_df['Receita_Projetada_Extraord'] - merged_df['Despesas_Aprovadas_Pendentes'] - merged_df['Despesas_Pagas']
  houses_to_group = ['Bar Brahma - Centro', 'Bar Léo - Centro', 'Bar Brasilia -  Aeroporto ', 'Bar Brasilia -  Aeroporto', 'Delivery Bar Leo Centro', 
                  'Delivery Fabrica de Bares', 'Delivery Orfeu', 'Edificio Rolim', 'Hotel Maraba', 
                  'Jacaré', 'Orfeu', 'Riviera Bar', 'Tempus', 'Escritorio Fabrica de Bares']

  # Create a new column 'Group' based on the houses
  merged_df['Group'] = merged_df['Empresa'].apply(lambda x: 'Group' if any(house in x for house in houses_to_group) else 'Other')
  return merged_df


def config_grouped_projecao(df_projecao_bares):
  # Group by 'Data', 'Group', and 'Empresa', and sum the values
  grouped_df = df_projecao_bares.groupby(['Data', 'Group']).sum().reset_index()
  grouped_df = grouped_df[grouped_df['Group'] == 'Group']
  grouped_df = grouped_df.reset_index(drop=True)
  return grouped_df


def config_feriados():
  # Criar uma instância do calendário brasileiro
  calendario_brasil = Brazil()
  # Especificar os anos para os quais você deseja obter os feriados
  anos_desejados = list(range(2023, 2031))
  # Inicializar uma lista vazia para armazenar as datas dos feriados
  datas_feriados = []
  # Iterar pelos anos e obter as datas dos feriados
  for ano in anos_desejados:
    feriados_ano = calendario_brasil.holidays(ano)
    datas_feriados.extend([feriado[0] for feriado in feriados_ano])
  # Criar uma série com as datas dos feriados
  serie_datas_feriados = pd.Series(datas_feriados, name='Data_Feriado')
  serie_datas_feriados = pd.to_datetime(serie_datas_feriados)
  nova_data = pd.to_datetime('2024-03-29')
  serie_datas_feriados = pd.concat([serie_datas_feriados, pd.Series([nova_data])])
  # Resetar o índice
  serie_datas_feriados.reset_index(drop=True, inplace=True)
  return serie_datas_feriados



def config_faturam_zig_fluxo_caixa(serie_datas_feriados):
  df_faturam_zig = GET_FATURAMENTO_ZIG_FLUXO_CAIXA() 
  df_faturam_zig['Data_Faturamento'] = pd.to_datetime(df_faturam_zig['Data_Faturamento'])
  df_faturam_zig['Valor_Faturado'] = df_faturam_zig['Valor_Faturado'].astype(float).round(2)  
  df_faturam_zig['Antecipacao_Credito'] = 1
  df_faturam_zig['Antecipacao_Credito'] = df_faturam_zig.apply(lambda row: 0 if row['Loja'] == 'Arcos' else row['Antecipacao_Credito'], axis=1)
  df_faturam_zig[['Tipo_Pagamento']].drop_duplicates()
  df_faturam_zig['Taxa'] = 0.00
  df_faturam_zig['Taxa'] = df_faturam_zig.apply(lambda row: row['Valor_Faturado'] * taxa_debito if row['Tipo_Pagamento'] == 'DÉBITO' else row['Taxa'], axis=1)
  df_faturam_zig['Taxa'] = df_faturam_zig.apply(lambda row: row['Valor_Faturado'] * taxa_credito_antecipado if (row['Tipo_Pagamento'] == 'CRÉDITO' and row['Antecipacao_Credito'] == 1) else row['Taxa'], axis=1)
  df_faturam_zig['Taxa'] = df_faturam_zig.apply(lambda row: row['Valor_Faturado'] * taxa_credito_padrao if (row['Tipo_Pagamento'] == 'CRÉDITO' and row['Antecipacao_Credito'] == 0) else row['Taxa'], axis=1)
  df_faturam_zig['Taxa'] = df_faturam_zig.apply(lambda row: row['Valor_Faturado'] * taxa_app if row['Tipo_Pagamento'] == 'APP' else row['Taxa'], axis=1)
  df_faturam_zig['Taxa'] = df_faturam_zig.apply(lambda row: row['Valor_Faturado'] * taxa_pix if row['Tipo_Pagamento'] == 'PIX' else row['Taxa'], axis=1)
  df_faturam_zig['Valor_Compensado'] = df_faturam_zig['Valor_Faturado'] - df_faturam_zig['Taxa']
  # Tratando bonus
  df_faturam_zig['Valor_Compensado'] = df_faturam_zig.apply(lambda row: 0 if row['Tipo_Pagamento'] == 'BÔNUS' else row['Valor_Compensado'], axis=1)

  # Adicionando uma nova coluna 'Custos_Zig' ao dataframe
  df_faturam_zig['Custos_Zig'] = 0.008 * df_faturam_zig['Valor_Faturado']

  # Calculando o custo acumulado para cada mês
  df_faturam_zig['Accumulated_Cost'] = df_faturam_zig.groupby([df_faturam_zig['Data_Faturamento'].dt.year, df_faturam_zig['Data_Faturamento'].dt.month, df_faturam_zig['ID_Loja']])['Custos_Zig'].cumsum()

  # Identificando as linhas onde o custo acumulado atinge ou ultrapassa 2800.00
  exceeded_limit = df_faturam_zig['Accumulated_Cost'] >= 2800.00

  # Ajustando os valores de 'Custos_Zig' para evitar custos negativos
  df_faturam_zig.loc[exceeded_limit, 'Custos_Zig'] = np.maximum(0, 2800.00 - (df_faturam_zig['Accumulated_Cost'] - df_faturam_zig['Custos_Zig']))

  # Zerando o custo acumulado para as linhas onde atingiu o limite
  df_faturam_zig.loc[exceeded_limit, 'Accumulated_Cost'] = np.minimum(2800.00, df_faturam_zig.loc[exceeded_limit, 'Accumulated_Cost'])

  # Removendo a coluna temporária 'Accumulated_Cost'
  df_faturam_zig = df_faturam_zig.drop('Accumulated_Cost', axis=1)

  df_faturam_zig['Valor_Final'] = df_faturam_zig['Valor_Compensado'] - df_faturam_zig['Custos_Zig']
  # df_faturam_zig['Valor_Final'] = df_faturam_zig.apply(lambda row: 0 if row['Tipo_Pagamento'] == 'VOUCHER' else row['Valor_Final'], axis=1)
  df_faturam_zig['Valor_Final'] = df_faturam_zig.apply(lambda row: row['Custos_Zig']*(-1) if row['Tipo_Pagamento'] == 'VOUCHER' else row['Valor_Final'], axis=1)
  # df_faturam_zig['Valor_Final'] = df_faturam_zig.apply(lambda row: 0 if row['Tipo_Pagamento'] == 'DINHEIRO' else row['Valor_Final'], axis=1)
  df_faturam_zig['Valor_Final'] = df_faturam_zig.apply(lambda row: row['Custos_Zig']*(-1) if row['Tipo_Pagamento'] == 'DINHEIRO' else row['Valor_Final'], axis=1)

  df_faturam_zig['Taxa'] = df_faturam_zig['Taxa'].astype(float).round(2)
  df_faturam_zig['Valor_Compensado'] = df_faturam_zig['Valor_Compensado'].astype(float).round(2)
  df_faturam_zig['Custos_Zig'] = df_faturam_zig['Custos_Zig'].astype(float).round(2)
  df_faturam_zig['Valor_Final'] = df_faturam_zig['Valor_Final'].astype(float).round(2)

  df_faturam_zig[['Tipo_Pagamento']].drop_duplicates()
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig['Data_Faturamento']

  # Debito
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1) 
                                                            if row['Tipo_Pagamento'] == 'DÉBITO' else row['Data_Compensacao'], axis=1)
  # Credito Antecipado
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1) 
                                                            if (row['Tipo_Pagamento'] == 'CRÉDITO' 
                                                                and row['Antecipacao_Credito'] == 1) else row['Data_Compensacao'], axis=1)
    # Credito Padrao
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=30) 
                                                            if (row['Tipo_Pagamento'] == 'CRÉDITO' 
                                                                and row['Antecipacao_Credito'] == 0) else row['Data_Compensacao'], axis=1) 
  # Pix
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1) 
                                                            if row['Tipo_Pagamento'] == 'PIX' else row['Data_Compensacao'], axis=1)    
  # Dinheiro
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1) 
                                                            if row['Tipo_Pagamento'] == 'DINHEIRO' else row['Data_Compensacao'], axis=1)  
  # App
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1) 
                                                            if row['Tipo_Pagamento'] == 'APP' else row['Data_Compensacao'], axis=1)    
      # App
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1) 
                                                            if row['Tipo_Pagamento'] == 'VOUCHER' else row['Data_Compensacao'], axis=1)                                                                   
  # Ajuste Feriados (round 1)
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1) 
                                                            if row['Data_Compensacao'] in serie_datas_feriados.values else row['Data_Compensacao'], axis=1)
  # Ajuste fds
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1)
                                                            if row['Data_Compensacao'].strftime('%A') == 'Sunday' else row['Data_Compensacao'], axis=1)
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=2)
                                                            if row['Data_Compensacao'].strftime('%A') == 'Saturday' else row['Data_Compensacao'], axis=1)
  # Ajuste Feriados (round 2)
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(lambda row: row['Data_Compensacao'] + pd.Timedelta(days=1) 
                                                            if row['Data_Compensacao'] in serie_datas_feriados.values else row['Data_Compensacao'], axis=1)    
  # Retirando os horarios das datas
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig['Data_Compensacao'].dt.date
  df_faturam_zig['Data_Faturamento'] = df_faturam_zig['Data_Faturamento'].dt.date
  return df_faturam_zig




def config_receitas_extraord_fluxo_caixa():
  df_receitas_extraord = GET_RECEITAS_EXTRAORD_CONCILIACAO()
  cols = ['Data_Competencia', 'Data_Venc_Parc_1', 'Data_Receb_Parc_1', 'Data_Venc_Parc_2', 'Data_Receb_Parc_2', 'Data_Venc_Parc_3',
          'Data_Receb_Parc_3', 'Data_Venc_Parc_4', 'Data_Receb_Parc_4', 'Data_Venc_Parc_5', 'Data_Receb_Parc_5']
  for col in cols:
    df_receitas_extraord[col] = pd.to_datetime(df_receitas_extraord[col]).dt.date

  # df_receitas_extraord['Data_Competencia'] = pd.to_datetime(df_receitas_extraord['Data_Competencia']).dt.date
  # df_receitas_extraord['Data_Venc_Parc_1'] = pd.to_datetime(df_receitas_extraord['Data_Venc_Parc_1']).dt.date
  # df_receitas_extraord['Data_Receb_Parc_1'] = pd.to_datetime(df_receitas_extraord['Data_Receb_Parc_1']).dt.date
  # df_receitas_extraord['Data_Venc_Parc_2'] = pd.to_datetime(df_receitas_extraord['Data_Venc_Parc_2']).dt.date
  # df_receitas_extraord['Data_Receb_Parc_2'] = pd.to_datetime(df_receitas_extraord['Data_Receb_Parc_2']).dt.date
  # df_receitas_extraord['Data_Venc_Parc_3'] = pd.to_datetime(df_receitas_extraord['Data_Venc_Parc_3']).dt.date
  # df_receitas_extraord['Data_Receb_Parc_3'] = pd.to_datetime(df_receitas_extraord['Data_Receb_Parc_3']).dt.date
  # df_receitas_extraord['Data_Venc_Parc_4'] = pd.to_datetime(df_receitas_extraord['Data_Venc_Parc_4']).dt.date
  # df_receitas_extraord['Data_Receb_Parc_4'] = pd.to_datetime(df_receitas_extraord['Data_Receb_Parc_4']).dt.date
  # df_receitas_extraord['Data_Venc_Parc_5'] = pd.to_datetime(df_receitas_extraord['Data_Venc_Parc_5']).dt.date
  # df_receitas_extraord['Data_Receb_Parc_5'] = pd.to_datetime(df_receitas_extraord['Data_Receb_Parc_5']).dt.date

  cols = ['Valor_Total', 'Categ_AB', 'Categ_Aluguel', 'Categ_Artist', 'Categ_Couvert', 'Categ_Locacao',
          'Categ_Patroc', 'Categ_Taxa_Serv', 'Valor_Parc_1', 'Valor_Parc_2', 'Valor_Parc_3', 'Valor_Parc_4', 'Valor_Parc_5']
  for col in cols:
    df_receitas_extraord[col] = df_receitas_extraord[col].astype(float).round(2)


  # df_receitas_extraord['Valor_Total'] = df_receitas_extraord['Valor_Total'].astype(float).round(2)
  # df_receitas_extraord['Categ_AB'] = df_receitas_extraord['Categ_AB'].astype(float).round(2)
  # df_receitas_extraord['Categ_Aluguel'] = df_receitas_extraord['Categ_Aluguel'].astype(float).round(2)
  # df_receitas_extraord['Categ_Artist'] = df_receitas_extraord['Categ_Artist'].astype(float).round(2)
  # df_receitas_extraord['Categ_Couvert'] = df_receitas_extraord['Categ_Couvert'].astype(float).round(2)
  # df_receitas_extraord['Categ_Locacao'] = df_receitas_extraord['Categ_Locacao'].astype(float).round(2)
  # df_receitas_extraord['Categ_Patroc'] = df_receitas_extraord['Categ_Patroc'].astype(float).round(2)
  # df_receitas_extraord['Categ_Taxa_Serv'] = df_receitas_extraord['Categ_Taxa_Serv'].astype(float).round(2) 
  # df_receitas_extraord['Valor_Parc_1'] = df_receitas_extraord['Valor_Parc_1'].astype(float).round(2)
  # df_receitas_extraord['Valor_Parc_2'] = df_receitas_extraord['Valor_Parc_2'].astype(float).round(2) 
  # df_receitas_extraord['Valor_Parc_3'] = df_receitas_extraord['Valor_Parc_3'].astype(float).round(2) 
  # df_receitas_extraord['Valor_Parc_4'] = df_receitas_extraord['Valor_Parc_4'].astype(float).round(2) 
  # df_receitas_extraord['Valor_Parc_5'] = df_receitas_extraord['Valor_Parc_5'].astype(float).round(2)  
  return df_receitas_extraord


def config_view_parc_agrup():
  df_view_parc_agrup = GET_VIEW_PARC_AGRUP()
  df_view_parc_agrup = df_view_parc_agrup.drop('Numero_Linha', axis=1)
  df_view_parc_agrup['Data_Vencimento'] = df_view_parc_agrup['Data_Vencimento'].dt.date
  df_view_parc_agrup['Data_Recebimento'] = df_view_parc_agrup['Data_Recebimento'].dt.date
  df_view_parc_agrup['Data_Ocorrencia'] = df_view_parc_agrup['Data_Ocorrencia'].dt.date
  df_view_parc_agrup['Valor_Parcela'] = df_view_parc_agrup['Valor_Parcela'].astype(float).round(2)
  return df_view_parc_agrup



def config_custos_blueme_sem_parcelamento():
  df_custos_blueme_sem_parcelamento = GET_CUSTOS_BLUEME_SEM_PARCELAMENTO()
  df_custos_blueme_sem_parcelamento['Valor'] = df_custos_blueme_sem_parcelamento['Valor'].astype(float).round(2)
  df_custos_blueme_sem_parcelamento['Data_Vencimento'] = pd.to_datetime(df_custos_blueme_sem_parcelamento['Data_Vencimento'])
  df_custos_blueme_sem_parcelamento['Data_Competencia'] = pd.to_datetime(df_custos_blueme_sem_parcelamento['Data_Competencia'])
  df_custos_blueme_sem_parcelamento['Data_Lancamento'] = pd.to_datetime(df_custos_blueme_sem_parcelamento['Data_Lancamento'])
  df_custos_blueme_sem_parcelamento['Realizacao_Pgto'] = pd.to_datetime(df_custos_blueme_sem_parcelamento['Realizacao_Pgto'])
  df_custos_blueme_sem_parcelamento['Previsao_Pgto'] = pd.to_datetime(df_custos_blueme_sem_parcelamento['Previsao_Pgto'])    
  return df_custos_blueme_sem_parcelamento


def config_custos_blueme_com_parcelamento():
  df_custos_blueme_com_parcelamento = GET_CUSTOS_BLUEME_COM_PARCELAMENTO()           
  df_custos_blueme_com_parcelamento['Valor_Parcela'] = df_custos_blueme_com_parcelamento['Valor_Parcela'].astype(float).round(2)
  df_custos_blueme_com_parcelamento['Valor_Original'] = df_custos_blueme_com_parcelamento['Valor_Original'].astype(float).round(2)
  df_custos_blueme_com_parcelamento['Valor_Liquido'] = df_custos_blueme_com_parcelamento['Valor_Liquido'].astype(float).round(2)
  df_custos_blueme_com_parcelamento['Vencimento_Parcela'] = pd.to_datetime(df_custos_blueme_com_parcelamento['Vencimento_Parcela'], format='%d/%m/%Y')
  df_custos_blueme_com_parcelamento['Previsao_Parcela'] = pd.to_datetime(df_custos_blueme_com_parcelamento['Previsao_Parcela'], format='%d/%m/%Y')
  df_custos_blueme_com_parcelamento['Realiz_Parcela'] = pd.to_datetime(df_custos_blueme_com_parcelamento['Realiz_Parcela'], format='%d/%m/%Y')
  df_custos_blueme_com_parcelamento['Data_Lancamento'] = pd.to_datetime(df_custos_blueme_com_parcelamento['Data_Lancamento'], format='%d/%m/%Y')
  return df_custos_blueme_com_parcelamento



def config_extratos():
  df_extratos = GET_EXTRATOS_BANCARIOS()
  df_extratos['Data_Transacao'] = df_extratos['Data_Transacao'].dt.date
  df_extratos['Valor'] = df_extratos['Valor'].astype(float).round(2)
  return df_extratos


def config_mutuos():
  df_mutuos = GET_MUTUOS()
  df_mutuos['Data_Mutuo'] = df_mutuos['Data_Mutuo'].dt.date
  df_mutuos['Valor'] = df_mutuos['Valor'].astype(float).round(2)
  return df_mutuos

def config_tesouraria_trans():
  df_tesouraria_trans = GET_TESOURARIA_TRANSACOES()
  df_tesouraria_trans['Data_Transacao'] = df_tesouraria_trans['Data_Transacao'].dt.date
  df_tesouraria_trans['Valor'] = df_tesouraria_trans['Valor'].astype(float).round(2)
  return df_tesouraria_trans

def somar_total(df):
  colunas_numericas = df.select_dtypes(include=[int, float]).columns
  soma_colunas = df[colunas_numericas].sum().to_frame().T
  soma_colunas['Data'] = 'Total'  # Adiciona um rótulo 'Total' para a linha somada
  df_com_soma = pd.concat([df, soma_colunas], ignore_index=True)
  return df_com_soma