import streamlit as st
import pandas as pd
from workalendar.america import Brazil
from datetime import datetime, timedelta
from utils.queries import *
from utils.components import *

def config_permissoes_user():
  username = st.session_state.get('userName', 'Usuário desconhecido')
  dfpermissao = GET_PERMISSIONS(username)
  permissao = dfpermissao['Permissao'].tolist()
  nomeUser = GET_USERNAME(username)
  nomeUser = ' '.join(nomeUser['Nome'].tolist())  
  return permissao, nomeUser, username


def config_sidebar():
  permissao, Nomeuser, username = config_permissoes_user()
  st.sidebar.header(f"Bem-vindo(a) {Nomeuser}!")
  if st.session_state['loggedIn']:
    if 'Administrador' in permissao or 'Acesso Caixa' in permissao:
      st.sidebar.title("Menu")
      st.sidebar.page_link("pages/Faturamento_Zig.py", label="Faturamento ZIGPAY")
      st.sidebar.page_link("pages/Faturamento_Receitas_Extraordinárias.py", label="Receitas Extraordinárias")
      st.sidebar.page_link("pages/Despesas.py", label="Despesas")
      st.sidebar.page_link("pages/CMV.py", label="CMV")
      st.sidebar.page_link("pages/Pareto_Geral.py", label="Curva ABC")
      st.sidebar.subheader('Fluxo de caixa:')
      st.sidebar.page_link("pages/Previsao_Faturamento.py", label="Previsão de Faturamento")
      st.sidebar.page_link("pages/Projecao_fluxo_caixa.py", label="Projeção")
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
  first_day_of_current_month = today.replace(day=1) 

  # Usar esses valores como default
  data_inicio_default = first_day_of_current_month.date()
  data_fim_default = today.date()
  
  return data_inicio_default, data_fim_default


def preparar_datas_ultimo_mes():
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
  permissao, nomeuser, username = config_permissoes_user()
  if 'Administrador' in permissao:
    dflojas = GET_LOJAS()
    lojasARemover = ['Casa Teste', 'Casa Teste 2', 'Casa Teste 3']
    dflojas = dflojas[~dflojas['Loja'].isin(lojasARemover)]
  else:
    dflojas = GET_LOJAS_USER(username)

  lojas = dflojas['Loja'].tolist()

  lojasReais = ['Abaru - Priceless', 'Arcos', 'Bar Brahma - Centro', 'Bar Léo - Centro', 'Blue Note - São Paulo', 'Blue Note SP (Novo)',
                'Delivery Bar Leo Centro', 'Delivery Fabrica de Bares', 'Delivery Jacaré', 'Delivery Orfeu', 'Edificio Rolim', 'Escritório Fabrica de Bares', 
                'Girondino ', 'Girondino - CCBB', 'Hotel Maraba', 'Jacaré', 'Love Cabaret', 'Notiê - Priceless', 'Orfeu', 'Priceless', 'Riviera Bar', 
                'Sanduiche comunicação LTDA ', 'Tempus Fugit  Ltda ', 'Ultra Evil Premium Ltda ', 'Bar Brahma - Granja', 'Brahma - Ribeirão']

  lojasReaisSet = set(lojasReais)
  lojas = [loja for loja in lojas if loja in lojasReaisSet]

  lojas.sort(key=str.lower)

  # Verificar se ambas as lojas estão na lista
  if 'Abaru - Priceless' in lojas and 'Notiê - Priceless' in lojas:
    # Remover a 'loja 1' da lista
    lojas.remove('Abaru - Priceless')
    
    # Encontrar o índice da 'loja 3' para inserir a 'loja 1' logo após
    indice_loja_alvo = lojas.index('Notiê - Priceless')
    
    # Inserir a 'loja 1' após a 'loja 3'
    lojas.insert(indice_loja_alvo + 1, 'Abaru - Priceless')

  return lojas


def preparar_dados_lojas_user_projecao_fluxo():
  permissao, nomeuser, username = config_permissoes_user()
  if 'Administrador' in permissao:
    dflojas = GET_LOJAS()
    lojasARemover = ['Casa Teste', 'Casa Teste 2', 'Casa Teste 3']
    dflojas = dflojas[~dflojas['Loja'].isin(lojasARemover)]
  else:
    dflojas = GET_LOJAS_USER(username)

  lojas = dflojas['Loja'].tolist()

  lojasReais = ['Abaru - Priceless', 'Arcos', 'All bar', 'Bar Brahma Aeroclube', 'Brahma Aricanduva',
                'Bar Brahma - Centro', 'Bar Brasilia -  Aeroporto', 'Bardassê', 'Bar Léo - Centro', 'Bar Léo - Vila Madalena', 'Blue Note - São Paulo', 'Blue Note SP (Novo)',
                'Colorado Aeroporto BSB', 'Delivery Bar Leo Centro', 'Delivery Fabrica de Bares', 'Delivery Jacaré', 'Delivery Orfeu', 'Duroc ', 'Edificio Rolim', 'Escritório Fabrica de Bares', 'FDB DIGITAL PARTICIPACOES LTDA', 'FDB HOLDING INFERIOR LTDA', 'FDB HOLDING SUPERIOR LTDA', 'Filial', 'Hbar participacoes e empreendimentos ', 'Ilha das Flores ', 'Lojinha - Brahma', 'Navarro', 'Patizal ',  'Piratininga', 'Tundra',
                'Girondino ', 'Girondino - CCBB', 'Hotel Maraba', 'Jacaré', 'Love Cabaret', 'Notiê - Priceless', 'Orfeu', 'Priceless', 'Riviera Bar', 
                'Sanduiche comunicação LTDA ', 'Tempus Fugit  Ltda ', 'Ultra Evil Premium Ltda ', 'Bar Brahma - Granja', 'Brahma - Ribeirão']

  lojasReaisSet = set(lojasReais)
  lojas = [loja for loja in lojas if loja in lojasReaisSet]

  lojas.sort(key=str.lower)

  # Verificar se ambas as lojas estão na lista
  if 'Abaru - Priceless' in lojas and 'Notiê - Priceless' in lojas:
    # Remover a 'loja 1' da lista
    lojas.remove('Abaru - Priceless')
    
    # Encontrar o índice da 'loja 3' para inserir a 'loja 1' logo após
    indice_loja_alvo = lojas.index('Notiê - Priceless')
    
    # Inserir a 'loja 1' após a 'loja 3'
    lojas.insert(indice_loja_alvo + 1, 'Abaru - Priceless')

  return lojas


def preparar_dados_classe_selecionada(df, classe):
  dados = df[classe].dropna().unique().tolist() 
  dados.sort(key=str.lower)
  return dados


def filtrar_por_datas(dataframe, data_inicio, data_fim, categoria):
  data_inicio = pd.Timestamp(data_inicio)
  data_fim = pd.Timestamp(data_fim)
  
 
  dataframe.loc[:, categoria] = pd.to_datetime(dataframe[categoria], errors='coerce')
  
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
    num = float(num)
    return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
  except (ValueError, TypeError):
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


def highlight_values_inverse(val):
  if '-' in val:
    color = 'green' 
  elif val == '0,00' or val == 'nan':
    color = 'black'
  else:
    color = 'red'
  return f'color: {color}'