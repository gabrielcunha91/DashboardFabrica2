import streamlit as st
import pandas as pd
from workalendar.america import Brazil
from datetime import datetime, timedelta
from utils.queries import *
from utils.components import *

####### DADOS GERAIS #######

def config_permissoes_user():
  username = st.session_state.get('userName', 'Usuário desconhecido')
  dfpermissao = GET_PERMISSIONS(username)
  permissao = dfpermissao['Permissao'].tolist()
  nomeUser = GET_USERNAME(username)
  nomeUser = nomeUser['Nome'].tolist()
  str1 = " "
  nomeUser = str1.join(nomeUser)
  return permissao, nomeUser


def config_sidebar():
  permissao, username = config_permissoes_user()
  st.sidebar.header(f"Bem-vindo(a) {username}!")
  if st.session_state['loggedIn']:
    if 'Administrador' in permissao:
      st.sidebar.title("Menu")
      st.sidebar.page_link("pages/Faturamento_Zig.py", label="Faturamento Zig")
      st.sidebar.page_link("pages/Faturamento_Receitas_Extraordinárias.py", label="Faturamento Receitas Extraordinárias")
      st.sidebar.page_link("pages/Despesas.py", label="Despesas")
      st.sidebar.page_link("pages/CMV.py", label="CMV")
      st.sidebar.page_link("pages/Pareto_Geral.py", label="Pareto")
      st.sidebar.page_link("pages/Projecao_fluxo_caixa.py", label="Projeção Fluxo de Caixa")
      st.sidebar.page_link("pages/Conciliacao_fluxo_caixa.py", label="Conciliação Fluxo de Caixa")
    elif 'Aprovador' in permissao:
      st.sidebar.title("Menu")
      st.sidebar.page_link("pages/Faturamento_Zig.py", label="Faturamento Zig")
      st.sidebar.page_link("pages/Faturamento_Receitas_Extraordinárias.py", label="Faturamento Receitas Extraordinárias")
      st.sidebar.page_link("pages/Despesas.py", label="Despesas")
      st.sidebar.page_link("pages/CMV.py", label="CMV")
      st.sidebar.page_link("pages/Pareto_Geral.py", label="Pareto")
    else:
      st.sidebar.title("Menu")
      st.sidebar.page_link("pages/Faturamento_Zig.py", label="Faturamento Zig")
  else:
    st.sidebar.write("Por favor, faça login para acessar o menu.")

def preparar_dados_datas():
  # Inicializa o calendário do Brasil
  cal = Brazil()
  today = datetime.today()

  # Determinar o primeiro e último dia do mês passado
  first_day_of_last_month = today.replace(day=1) - timedelta(days=1)
  first_day_of_last_month = first_day_of_last_month.replace(day=1)
  last_day_of_last_month = today.replace(day=1) - timedelta(days=1)

  # Usar esses valores como default
  data_inicio_default = first_day_of_last_month.date()
  data_fim_default = last_day_of_last_month.date()
  
  return data_inicio_default, data_fim_default


def preparar_dados_lojas_user():
  username = st.session_state.get('userName', 'Usuário desconhecido')
  dflojas = GET_LOJAS_USER(username)
  lojas = dflojas['Loja'].tolist()
  if 'Blue Note - São Paulo' in lojas or 'Blue Note SP (Novo)' in lojas:
    lojas.append('Blue Note - SP Jazz')
  lojas.sort(key=str.lower)
  return lojas

def preparar_dados_classe_selecionada(df, classe):
  dfCopia = df.copy()
  dados = dfCopia[classe].unique().tolist()
  dados = [dado for dado in dados if dado is not None]
  dados.sort(key=str.lower)
  return dados

def filtrar_por_datas(dataframe, data_inicio, data_fim, categoria):
  data_inicio = pd.Timestamp(data_inicio)
  data_fim = pd.Timestamp(data_fim)
  
  # Ensure the 'categoria' column is converted to datetime correctly
  dataframe.loc[:, categoria] = pd.to_datetime(dataframe[categoria])
  
  # Apply the filter using .loc to avoid SettingWithCopyWarning
  dataframe_filtered = dataframe.loc[
      (dataframe[categoria] >= data_inicio) & (dataframe[categoria] <= data_fim)
  ]
  
  return dataframe_filtered


def filtrar_por_classe_selecionada(dataframe, classe, valores_selecionados):
  if valores_selecionados:
    dataframe = dataframe[dataframe[classe].isin(valores_selecionados)]
  return dataframe


def format_brazilian(num):
  try:
    # Convertendo para float
    num = float(num)
    return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
  except (ValueError, TypeError):
    # Em caso de falha na conversão, retorna o valor original
    return num

def format_columns_brazilian(df, numeric_columns):
  for col in numeric_columns:
    if col in df.columns:
      df[col] = df[col].apply(format_brazilian)
  return df

def format_date_brazilian(df, date_column):
  df[date_column] = pd.to_datetime(df[date_column])
  df[date_column] = df[date_column].dt.strftime('%d-%m-%Y')
  return df


def highlight_values(val):
    color = 'red' if '-' in val else 'green'
    return f'color: {color}'
