import streamlit as st
import pandas as pd
from babel.dates import format_date
from utils.queries import *
from utils.functions.cmv import *
from utils.functions.dados_gerais import *
from utils.components import *
from utils.user import logout
import openpyxl

st.set_page_config(
  layout = 'wide',
  page_title = 'DRE',
  page_icon=':⚖',
  initial_sidebar_state="collapsed"
)  
pd.set_option('future.no_silent_downcasting', True)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')



# Permite o upload do arquivo
uploaded_file = st.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

# Verifica se um arquivo foi carregado
if uploaded_file is not None:
  # Carrega o arquivo Excel em um DataFrame
  df = pd.read_excel(uploaded_file, sheet_name='NomeDaPlanilha')

  # Exibe o conteúdo do DataFrame
  st.write("Dados carregados:")
  st.dataframe(df)

  # Procura pela palavra "TOTAL" na coluna B e pega o valor ao lado na coluna C
  total_row = df[df['B'] == 'TOTAL'].index[0]
  valor_total = df.at[total_row, 'C']

  st.write(f"O valor ao lado de 'TOTAL' é: {valor_total}")