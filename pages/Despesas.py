import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.despesas import *
from utils.functions.dados_gerais import *
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

  lojasComDados = preparar_dados_lojas_user()
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  Despesas = GET_DESPESAS()
  Despesas = filtrar_por_datas(Despesas, data_inicio, data_fim, 'Data_Evento')
  Despesas = filtrar_por_classe_selecionada(Despesas, 'Loja', lojas_selecionadas)
  despesasConfig = config_despesas_por_classe(Despesas)
  despesasConfigStyled = despesasConfig.style.map(highlight_values, subset=['Orçamento - Realiz.'])

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Despesas por Classe:")
      st.dataframe(despesasConfigStyled, height=500, use_container_width=True, hide_index=True)

  despesaDetalhada = config_despesas_detalhado(Despesas)

  classificacoes = preparar_dados_classe_selecionada(despesaDetalhada, 'Plano de Contas')

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 15, 1])
    with col1:
      col3, col4, col5 = st.columns([2, 1, 1])
      with col3:
        st.subheader("Despesas Detalhadas:")
      with col4:
        classificacoes_selecionadas = st.multiselect(label='Selecione Classificações', options=classificacoes)
        despesaDetalhada = filtrar_por_classe_selecionada(despesaDetalhada, 'Plano de Contas', classificacoes_selecionadas)
      with col5:
        fornecedores = preparar_dados_classe_selecionada(despesaDetalhada, 'Fornecedor')
        fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedores)
        despesaDetalhada = filtrar_por_classe_selecionada(despesaDetalhada, 'Fornecedor', fornecedores_selecionados)
      valorTotal = despesaDetalhada['Valor'].sum()
      valorTotal = format_brazilian(valorTotal)
      despesaDetalhada = format_columns_brazilian(despesaDetalhada, ['Valor'])
      st.dataframe(despesaDetalhada, height=500, use_container_width=True, hide_index=True)
      st.write('Valor Total = R$', valorTotal)

if __name__ == '__main__':
  main()
