import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions import *
from utils.components import *

def main():
  st.set_page_config(
    layout = 'wide',
    page_title = 'Faturamento Extraordinário'
  )
  st.title('Faturamento (Receitas Extraordinárias)')
  st.divider()

  lojasComDados = preparar_dados_lojas(GET_RECEIT_EXTRAORD())
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  ReceitExtraord = config_receit_extraord(lojas_selecionadas, data_inicio, data_fim)
  FaturamReceitExtraord = faturam_receit_extraord(ReceitExtraord)
  df_agrupado = ReceitExtraord.groupby('Data Evento').agg({'Valor Total': 'sum', 'ID': 'count'}).reset_index()
  df_agrupado.rename(columns={'ID': 'Quantidade de Eventos'}, inplace=True)


  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Faturamento Receitas Extaordinárias:")
      st.dataframe(FaturamReceitExtraord, width=1080, hide_index=True)
  st.divider()

  classificacoes = preparar_dados_classificacoes(GET_CLSSIFICACAO())
  classificacoes_selecionadas = st.multiselect(label='Selecione Classificações', options=classificacoes)
  DfFiltrado = filtrar_por_classificacao(ReceitExtraord, classificacoes_selecionadas)
  st.divider()

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 15, 1])
    with col1:
      st.subheader("Detalhamento de acordo com a classificação selecionada:")
      st.dataframe(DfFiltrado, hide_index=True)

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 15, 1])
    with col1:
      st.subheader("Análise Por Dia:")
      plotar_grafico(df_agrupado)



if __name__ == '__main__':
  main()
