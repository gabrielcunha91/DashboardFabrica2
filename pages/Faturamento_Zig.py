import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.faturamento_zig import *
from utils.functions.dados_gerais import *
from utils.components import *
from utils.user import logout
import threading

st.set_page_config(
  layout = 'wide',
  page_title = 'Faturamento Zig',
  page_icon=':moneybag:',
  initial_sidebar_state="collapsed"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')

def main():
  config_sidebar()
  col, colx = st.columns([5, 1])
  with col:
    st.title('Faturamento Zig Agregado')
  with colx:
    if st.button("Logout"):
      logout()
  st.divider()

  lojasComDados = preparar_dados_lojas_user()
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)

  st.divider()

  threading.Thread(target=config_Faturamento_zig)
  OrcamentoFaturamento = config_orcamento_faturamento(lojas_selecionadas, data_inicio, data_fim) 
  orcamfatformatado = OrcamentoFaturamento.copy()
  orcamfatformatado = format_columns_brazilian(orcamfatformatado, ['Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido', 'Faturam - Orçamento'])

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 7])
    with col1:
      st.subheader("Faturamento Zig:")
      st.dataframe(orcamfatformatado, width=700, hide_index=True)
    with col2:
      st.subheader("Valores Líquidos:")
      Grafico_Donut(OrcamentoFaturamento)
  
  FaturamentoZig = config_Faturamento_zig(lojas_selecionadas, data_inicio, data_fim)

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Top Dez Alimentos:")
      top_dez(FaturamentoZig, 'Alimentos')

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Top Dez Bebidas:")
      top_dez(FaturamentoZig, 'Bebidas')

  with st.container(border=True):  
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Faturamento Por Dia:")
      faturam_por_dia(FaturamentoZig)

if __name__ == '__main__':
  main()
