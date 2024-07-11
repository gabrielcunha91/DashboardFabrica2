import streamlit as st
import pandas as pd
import numpy as np
from utils.queries import *
from workalendar.america import Brazil

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
  calendario_brasil = Brazil()
  anos_desejados = list(range(2023, 2031))
  datas_feriados = []

  for ano in anos_desejados:
    feriados_ano = calendario_brasil.holidays(ano)
    datas_feriados.extend([feriado[0] for feriado in feriados_ano])

  serie_datas_feriados = pd.Series(datas_feriados, name='Data_Feriado')
  serie_datas_feriados = pd.to_datetime(serie_datas_feriados)
  nova_data = pd.to_datetime('2024-03-29')
  serie_datas_feriados = pd.concat([serie_datas_feriados, pd.Series([nova_data])])

  serie_datas_feriados.reset_index(drop=True, inplace=True)
  return serie_datas_feriados



def config_faturam_zig_fluxo_caixa(serie_datas_feriados):
  # Definindo as taxas
  taxa_credito_antecipado = 0.0265
  taxa_credito_padrao = 0.016
  taxa_debito = 0.0095
  taxa_app = 0.0074
  taxa_pix = 0.0074

  # Obtendo os dados
  df_faturam_zig = GET_FATURAMENTO_ZIG_FLUXO_CAIXA() 
  df_faturam_zig['Data_Faturamento'] = pd.to_datetime(df_faturam_zig['Data_Faturamento'])
  df_faturam_zig['Valor_Faturado'] = df_faturam_zig['Valor_Faturado'].astype(float).round(2)
  df_faturam_zig['Antecipacao_Credito'] = df_faturam_zig['Loja'].apply(lambda x: 0 if x == 'Arcos' else 1)

  # Dicionário de taxas
  taxas = {
    'DÉBITO': taxa_debito,
    'CRÉDITO_ANTECIPADO': taxa_credito_antecipado,
    'CRÉDITO_PADRAO': taxa_credito_padrao,
    'APP': taxa_app,
    'PIX': taxa_pix,
  }

  # Aplicando as taxas
  df_faturam_zig['Taxa'] = df_faturam_zig.apply(
    lambda row: row['Valor_Faturado'] * taxas.get(
      f"{row['Tipo_Pagamento']}_ANTECIPADO" if row['Tipo_Pagamento'] == 'CRÉDITO' and row['Antecipacao_Credito'] == 1 else
      f"{row['Tipo_Pagamento']}_PADRAO" if row['Tipo_Pagamento'] == 'CRÉDITO' and row['Antecipacao_Credito'] == 0 else
      row['Tipo_Pagamento'], 0
    ), axis=1
  )

  df_faturam_zig['Valor_Compensado'] = df_faturam_zig['Valor_Faturado'] - df_faturam_zig['Taxa']
  df_faturam_zig['Valor_Compensado'] = df_faturam_zig.apply(lambda row: 0 if row['Tipo_Pagamento'] == 'BÔNUS' else row['Valor_Compensado'], axis=1)

  # Calculando custos Zig
  df_faturam_zig['Custos_Zig'] = 0.008 * df_faturam_zig['Valor_Faturado']
  df_faturam_zig['Accumulated_Cost'] = df_faturam_zig.groupby([df_faturam_zig['Data_Faturamento'].dt.year, df_faturam_zig['Data_Faturamento'].dt.month, df_faturam_zig['ID_Loja']])['Custos_Zig'].cumsum()
  
  exceeded_limit = df_faturam_zig['Accumulated_Cost'] >= 2800.00
  df_faturam_zig.loc[exceeded_limit, 'Custos_Zig'] = np.maximum(0, 2800.00 - (df_faturam_zig['Accumulated_Cost'] - df_faturam_zig['Custos_Zig']))
  df_faturam_zig.loc[exceeded_limit, 'Accumulated_Cost'] = np.minimum(2800.00, df_faturam_zig.loc[exceeded_limit, 'Accumulated_Cost'])
  
  df_faturam_zig = df_faturam_zig.drop('Accumulated_Cost', axis=1)

  df_faturam_zig['Valor_Final'] = df_faturam_zig['Valor_Compensado'] - df_faturam_zig['Custos_Zig']
  df_faturam_zig['Valor_Final'] = df_faturam_zig.apply(lambda row: row['Custos_Zig']*(-1) if row['Tipo_Pagamento'] in ['VOUCHER', 'DINHEIRO'] else row['Valor_Final'], axis=1)

  df_faturam_zig = df_faturam_zig.round({'Taxa': 2, 'Valor_Compensado': 2, 'Custos_Zig': 2, 'Valor_Final': 2})

  # Dicionário de dias de compensação
  dias_compensacao = {
    'DÉBITO': 1,
    'CRÉDITO_ANTECIPADO': 1,
    'CRÉDITO_PADRAO': 30,
    'PIX': 1,
    'DINHEIRO': 1,
    'APP': 1,
    'VOUCHER': 1,
  }

  # Função para calcular a data de compensação
  def calcular_data_compensacao(row):
    tipo_pagamento = f"{row['Tipo_Pagamento']}_ANTECIPADO" if row['Tipo_Pagamento'] == 'CRÉDITO' and row['Antecipacao_Credito'] == 1 else f"{row['Tipo_Pagamento']}_PADRAO" if row['Tipo_Pagamento'] == 'CRÉDITO' and row['Antecipacao_Credito'] == 0 else row['Tipo_Pagamento']
    data = row['Data_Faturamento'] + pd.Timedelta(days=dias_compensacao.get(tipo_pagamento, 0))
    while data in serie_datas_feriados.values or data.strftime('%A') in ['Saturday', 'Sunday']:
      data += pd.Timedelta(days=1)
    return data

  df_faturam_zig['Data_Compensacao'] = df_faturam_zig.apply(calcular_data_compensacao, axis=1)
  df_faturam_zig['Data_Compensacao'] = df_faturam_zig['Data_Compensacao'].dt.date
  df_faturam_zig['Data_Faturamento'] = df_faturam_zig['Data_Faturamento'].dt.date

  return df_faturam_zig



def config_receitas_extraord_fluxo_caixa():
  df_receitas_extraord = GET_RECEITAS_EXTRAORD_CONCILIACAO()
  cols = ['Data_Competencia', 'Data_Venc_Parc_1', 'Data_Receb_Parc_1', 'Data_Venc_Parc_2', 'Data_Receb_Parc_2', 'Data_Venc_Parc_3',
          'Data_Receb_Parc_3', 'Data_Venc_Parc_4', 'Data_Receb_Parc_4', 'Data_Venc_Parc_5', 'Data_Receb_Parc_5']
  
  for col in cols:
    df_receitas_extraord[col] = pd.to_datetime(df_receitas_extraord[col]).dt.date

  cols = ['Valor_Total', 'Categ_AB', 'Categ_Aluguel', 'Categ_Artist', 'Categ_Couvert', 'Categ_Locacao',
          'Categ_Patroc', 'Categ_Taxa_Serv', 'Valor_Parc_1', 'Valor_Parc_2', 'Valor_Parc_3', 'Valor_Parc_4', 'Valor_Parc_5']
  
  for col in cols:
    df_receitas_extraord[col] = df_receitas_extraord[col].astype(float).round(2)

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
  
  date_columns = ['Data_Vencimento', 'Data_Competencia', 'Data_Lancamento', 'Realizacao_Pgto', 'Previsao_Pgto']
  
  for col in date_columns:
    df_custos_blueme_sem_parcelamento[col] = pd.to_datetime(df_custos_blueme_sem_parcelamento[col], errors='coerce')
  
  return df_custos_blueme_sem_parcelamento
 


def config_custos_blueme_com_parcelamento():
  df_custos_blueme_com_parcelamento = GET_CUSTOS_BLUEME_COM_PARCELAMENTO()
  df_custos_blueme_com_parcelamento['Valor_Parcela'] = df_custos_blueme_com_parcelamento['Valor_Parcela'].astype(float).round(2)
  df_custos_blueme_com_parcelamento['Valor_Original'] = df_custos_blueme_com_parcelamento['Valor_Original'].astype(float).round(2)
  df_custos_blueme_com_parcelamento['Valor_Liquido'] = df_custos_blueme_com_parcelamento['Valor_Liquido'].astype(float).round(2)
  
  date_columns = ['Vencimento_Parcela', 'Previsao_Parcela', 'Realiz_Parcela', 'Data_Lancamento']
  
  for col in date_columns:
    df_custos_blueme_com_parcelamento[col] = pd.to_datetime(df_custos_blueme_com_parcelamento[col], format='%d/%m/%Y', errors='coerce')
  
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
  soma_colunas['Data'] = 'Total' 
  df_com_soma = pd.concat([df, soma_colunas], ignore_index=True)
  return df_com_soma