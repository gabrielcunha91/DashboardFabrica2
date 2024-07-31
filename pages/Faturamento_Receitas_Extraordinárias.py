import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.faturam_receit_extraord import *
from utils.functions.dados_gerais import *
from utils.components import *
from utils.user import logout

st.set_page_config(
  layout = 'wide',
  page_title = 'Faturamento Extraordinário',
  page_icon='💎',
  initial_sidebar_state="collapsed"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')

def main():
  config_sidebar()
  col, colx = st.columns([5, 1])
  with col:
    st.title('RECEITAS EXTRAORDINÁRIAS')
  with colx:
    if st.button("Logout"):
      logout()
  st.divider()

  lojasComDados = preparar_dados_lojas_user()
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  ReceitExtraord = config_receit_extraord(lojas_selecionadas, data_inicio, data_fim)
  FaturamReceitExtraord, Totais = faturam_receit_extraord(ReceitExtraord)
  df_agrupado = ReceitExtraord.groupby('Data Evento').agg({'Valor Total': 'sum', 'ID': 'count'}).reset_index()
  df_agrupado.rename(columns={'ID': 'Quantidade de Eventos'}, inplace=True)


  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Faturamento Receitas Extaordinárias:")
      st.dataframe(FaturamReceitExtraord, use_container_width=True, hide_index=True)
      st.write("Faturamento Extraordinário Total:")
      st.dataframe(Totais, use_container_width=True, hide_index=True)


  classificacoes = ['Eventos', 'Coleta de Óleo', 'Bilheteria', 'Patrocínio', 'Premium Corp']

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 15, 1])
    with col1:
      col3, col4 = st.columns([2, 1])
      with col3:
        st.subheader("Detalhamento por Classificação:")
      with col4:
        classificacoes_selecionadas = st.multiselect(label='Selecione Classificações', options=classificacoes)
      DfFiltrado = filtrar_por_classe_selecionada(ReceitExtraord, 'Classificação', classificacoes_selecionadas)
      DfFiltrado = format_columns_brazilian(DfFiltrado, ['Valor Total', 'Categ. AB', 'Categ. Aluguel', 'Categ. Artista', 'Categ. Couvert', 'Categ. Locação', 'Categ. Patrocínio', 'Categ. Taxa de serviço'])
      st.dataframe(DfFiltrado, use_container_width=True, hide_index=True)


if __name__ == '__main__':
  main()
