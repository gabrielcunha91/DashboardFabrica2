import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions import *
from utils.components import *


def main():
  st.set_page_config(
    layout = 'wide',
    page_title = 'Despesas'
  )
  st.title('Despesas')
  st.divider()

  lojasComDados = preparar_dados_lojas(GET_RECEIT_EXTRAORD())
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  Despesas = GET_DESPESAS()
  Despesas = filtrar_por_datas(Despesas, data_inicio, data_fim, 'Data_Evento')
  Despesas = filtrar_por_lojas(Despesas, lojas_selecionadas)
  
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Despesas por Classe:")
      st.dataframe(config_despesas_por_classe(Despesas), height=500, width=1080, hide_index=True)

  despesaDetalhada, valorTotal = config_despesas_detalhado(Despesas)

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 15, 1])
    with col1:
      st.subheader("Despesas Detalhadas:")
      st.dataframe(despesaDetalhada, height=500, width=1250, hide_index=True)
      
    col0, col1, col2 = st.columns([1, 10, 3])
    with col2:
      st.write('Valor Total = R$', valorTotal)


if __name__ == '__main__':
  main()
