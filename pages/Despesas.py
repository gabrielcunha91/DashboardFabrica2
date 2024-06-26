import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions import *
from utils.components import *
from utils.user import logout

st.set_page_config(
  layout = 'wide',
  page_title = 'Despesas',
  page_icon=':money_with_wings:',
  initial_sidebar_state="collapsed"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')


def main():
  config_sidebar()
  col, colx = st.columns([5, 1])
  with col:
    st.title('Despesas')
  with colx:
    if st.button("Logout"):
      logout()
  st.divider()

  lojasComDados = preparar_dados_lojas(GET_RECEIT_EXTRAORD())
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  Despesas = GET_DESPESAS()
  Despesas = filtrar_por_datas(Despesas, data_inicio, data_fim, 'Data_Evento')
  Despesas = filtrar_por_classe_selecionada(Despesas, 'Loja', lojas_selecionadas)
  despesasConfig = config_despesas_por_classe(Despesas)
  despesasConfigStyled = despesasConfig.style.applymap(highlight_values, subset=['Orçamento - Realiz.'])

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Despesas por Classe:")
      st.dataframe(despesasConfigStyled, height=500, width=1080, hide_index=True)

  despesaDetalhada, valorTotal = config_despesas_detalhado(Despesas)
  valorTotal = format_brazilian(valorTotal)

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 15, 1])
    with col1:
      st.subheader("Despesas Detalhadas:")
      st.dataframe(despesaDetalhada, height=500, width=1250, hide_index=True)
      st.write('Valor Total = R$', valorTotal)


if __name__ == '__main__':
  main()
