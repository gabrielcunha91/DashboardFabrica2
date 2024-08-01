import streamlit as st
import pandas as pd
import numpy as np
from utils.queries import *
from workalendar.america import Brazil
from utils.functions.dados_gerais import *
import openpyxl
import os



# Função para criar os dados parciais
def criar_parciais(df):
  df_parciais = pd.DataFrame()
  for i in range(1, 5):
    parcial = df.copy()
    parcial['Data_Parcial'] = parcial['Data_Compensacao'] + pd.DateOffset(days=7 * i)
    parcial['Valor_Parcial'] = (parcial['Valor_Compensado'] / 4).round(2)
    parcial = parcial.rename(columns={'Data_Parcial': f'Data_Parcial_{i}', 'Valor_Parcial': f'Valor_Parcial_{i}'})
    df_parciais = pd.concat([df_parciais, parcial[['Empresa', f'Data_Parcial_{i}', f'Valor_Parcial_{i}']]], axis=1)

  for i in range(1, 5):
    df_parciais[f'Data_Parcial_{i}'] = pd.to_datetime(df_parciais[f'Data_Parcial_{i}'])

  return df_parciais



def unificar_parciais(df):
  # Crie uma lista para armazenar os DataFrames intermediários
  dfs = []

  temp_df_1 = pd.DataFrame({
    'Empresa': df['Empresa'],
    'Data_Parcial': df[f'Data_Parcial_{1}'],
    'Valor_Parcial': df[f'Valor_Parcial_{1}']
  })
  temp_df_2 = pd.DataFrame({
    'Empresa': df['Empresa'],
    'Data_Parcial': df[f'Data_Parcial_{2}'],
    'Valor_Parcial': df[f'Valor_Parcial_{2}']
  })
  temp_df_3 = pd.DataFrame({
    'Empresa': df['Empresa'],
    'Data_Parcial': df[f'Data_Parcial_{3}'],
    'Valor_Parcial': df[f'Valor_Parcial_{3}']
  })
  temp_df_4 = pd.DataFrame({
    'Empresa': df['Empresa'],
    'Data_Parcial': df[f'Data_Parcial_{4}'],
    'Valor_Parcial': df[f'Valor_Parcial_{4}']
  })

  dfs = [temp_df_1, temp_df_2, temp_df_3, temp_df_4]

  # Concatene todos os DataFrames temporários em um único DataFrame
  result_df = pd.concat(dfs, ignore_index=True)

  return result_df
