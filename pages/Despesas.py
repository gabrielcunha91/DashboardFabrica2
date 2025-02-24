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



config_sidebar()
col, col2, col3 = st.columns([6, 1, 1])
with col:
  st.title('DESPESAS')
with col2:
  st.button(label="Atualizar", on_click = st.cache_data.clear)
with col3:
  if st.button("Logout"):
    logout()

st.divider()

lojasComDados = preparar_dados_lojas_user()
data_inicio_default, data_fim_default = preparar_dados_datas()
lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
st.divider()

# Despesas = GET_DESPESAS()
despesasDetalhadas = GET_DESPESAS()
despesasDetalhadas = filtrar_por_datas(despesasDetalhadas, data_inicio, data_fim, 'Data_Evento')
despesasDetalhadas = filtrar_por_classe_selecionada(despesasDetalhadas, 'Loja', lojas_selecionadas)

Despesas2 = GET_DESPESAS2().drop_duplicates()
Orcamentos = GET_ORCAMENTOS_DESPESAS().drop_duplicates()
Despesas = pd.merge(Despesas2, Orcamentos, on=['Primeiro_Dia_Mes', 'Loja', 'Plano_de_Contas', 'Class_Plano_de_Contas'], how='outer')
Despesas['Data_Evento'] = Despesas['Data_Evento'].fillna(Despesas['Primeiro_Dia_Mes'])
Despesas = filtrar_por_datas(Despesas, data_inicio, data_fim, 'Data_Evento')
Despesas = filtrar_por_classe_selecionada(Despesas, 'Loja', lojas_selecionadas)
despesasConfig = config_despesas_por_classe(Despesas)
despesasConfigStyled = despesasConfig.style.map(highlight_values, subset=['Orçamento - Realiz.'])

with st.container(border=True):
  col0, col1, col2 = st.columns([1, 10, 1])
  with col1:
    st.subheader("Despesas:")
    st.dataframe(despesasConfigStyled, height=500, use_container_width=True, hide_index=True)

despesaDetalhadaConfig = config_despesas_detalhado(despesasDetalhadas)

classificacoes = preparar_dados_classe_selecionada(despesaDetalhadaConfig, 'Plano de Contas')

with st.container(border=True):
  col0, col1, col2 = st.columns([1, 15, 1])
  with col1:
    col3, col4, col5 = st.columns([2, 1, 1])
    with col3:
      st.subheader("Despesas Detalhadas:")
    with col4:
      classificacoes_selecionadas = st.multiselect(label='Selecione Classificações', options=classificacoes)
      despesaDetalhadaConfig = filtrar_por_classe_selecionada(despesaDetalhadaConfig, 'Plano de Contas', classificacoes_selecionadas)
    with col5:
      fornecedores = preparar_dados_classe_selecionada(despesaDetalhadaConfig, 'Fornecedor')
      fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedores)
      despesaDetalhadaConfig = filtrar_por_classe_selecionada(despesaDetalhadaConfig, 'Fornecedor', fornecedores_selecionados)
    valorTotal = despesaDetalhadaConfig['Valor'].sum()
    valorTotal = format_brazilian(valorTotal)
    despesaDetalhadaConfig = format_columns_brazilian(despesaDetalhadaConfig, ['Valor'])
    st.dataframe(despesaDetalhadaConfig, height=500, use_container_width=True, hide_index=True)
    st.write('Valor Total = R$', valorTotal)


