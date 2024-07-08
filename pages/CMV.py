import streamlit as st
import pandas as pd
from babel.dates import format_date
from utils.queries import *
from utils.functions import *
from utils.components import *
from utils.user import logout

st.set_page_config(
  layout = 'wide',
  page_title = 'CMV',
  page_icon=':⚖',
  initial_sidebar_state="collapsed"
)  
pd.set_option('future.no_silent_downcasting', True)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')


def main():
  config_sidebar()
  col, colx = st.columns([5, 1])
  with col:
    st.title('CMV')
  with colx:
    if st.button("Logout"):
      logout()
  
  st.divider()

  lojasComDados = preparar_dados_lojas_user()
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  dfFinal = config_tabelas_iniciais_cmv(lojas_selecionadas, data_inicio, data_fim)
 
  FaturamBrutoAliment = dfFinal['Faturam_Bruto_Aliment'].sum()
  FaturamBrutoBebidas = dfFinal['Faturam_Bruto_Bebidas'].sum()
  ComprasAlim = dfFinal['Compras_Alimentos'].sum()
  ComprasBeb = dfFinal['Compras_Bebidas'].sum()
  DeltaEstoqueAlim = ((dfFinal['Estoque_Final_Alimentos'].sum()) - (dfFinal['Estoque_Inicial_Alimentos'].sum()))
  DeltaEstoqueBebidas = ((dfFinal['Estoque_Final_Bebidas'].sum()) - (dfFinal['Estoque_Inicial_Bebidas'].sum()))
  CMVAlim = (ComprasAlim - DeltaEstoqueAlim)
  CMVBebidas = (ComprasBeb - DeltaEstoqueBebidas)
  CMVPercentualAlim = (CMVAlim / FaturamBrutoAliment) * 100
  CMVPercentualBebidas = (CMVBebidas / FaturamBrutoBebidas) * 100
  CMVPercentualGeral = ((CMVAlim + CMVBebidas)/(FaturamBrutoAliment+FaturamBrutoBebidas)) * 100

  FaturamBrutoAliment = format_brazilian(FaturamBrutoAliment)
  FaturamBrutoBebidas = format_brazilian(FaturamBrutoBebidas)
  ComprasAlim = format_brazilian(ComprasAlim)
  ComprasBeb = format_brazilian(ComprasBeb)
  DeltaEstoqueAlim = format_brazilian(DeltaEstoqueAlim)
  DeltaEstoqueBebidas = format_brazilian(DeltaEstoqueBebidas)
  CMVAlim = format_brazilian(CMVAlim)
  CMVBebidas = format_brazilian(CMVBebidas)
  CMVPercentualAlim = format_brazilian(CMVPercentualAlim)
  CMVPercentualBebidas = format_brazilian(CMVPercentualBebidas)
  CMVPercentualGeral = format_brazilian(CMVPercentualGeral)

  col1, col2, col3, col4, col5, col6 = st.columns(6)
  with col1:
    with st.container(border=True):
      st.write('Faturam. Alimentos')
      st.write('R$', FaturamBrutoAliment)
  with col2:
    with st.container(border=True):
      st.write('Faturam. Bebidas')
      st.write('R$', FaturamBrutoBebidas)  
  with col3:
    with st.container(border=True):
      st.write('Compras Alim.')
      st.write('R$', ComprasAlim)  
  with col4:
    with st.container(border=True):
      st.write('Compras Bebidas')
      st.write('R$', ComprasBeb)
  with col5:
    with st.container(border=True):
      st.write('Δ Estoque Alimentos')
      st.write('R$', DeltaEstoqueAlim)
  with col6:
    with st.container(border=True):
      st.write('Δ Estoque Bebidas')
      st.write(' R$', DeltaEstoqueBebidas)

  col7, col8, col9, col10, col11 = st.columns(5)
  with col7:
    with st.container(border=True):
      st.write('CMV Alimentos')
      st.write(' R$', CMVAlim)
  with col8:
    with st.container(border=True):
      st.write('CMV Bebidas')
      st.write('R$', CMVBebidas)
  with col9:
    with st.container(border=True):
      st.write('CMV Percentual Alimentos')
      st.write(CMVPercentualAlim, '%')
  with col10:
    with st.container(border=True):
      st.write('CMV Percentual Bebidas')
      st.write(CMVPercentualBebidas, '%')
  with col11:
    with st.container(border=True):
      st.write('CMV Percentual Geral')
      st.write(CMVPercentualGeral, '%')

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Fatutamentos brutos e Estoques')
      st.dataframe(config_tabela_CMV(dfFinal), width=1200, hide_index=True)
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Compras')
      dfcompras = config_tabela_compras(dfFinal.copy())
      dfcompras['Mês'] = pd.to_datetime(dfcompras['Mês'], format='%d-%m-%Y')
      # Formatando a data para "nome do mês/ano"
      dfcompras['Mês'] = dfcompras['Mês'].apply(lambda x: format_date(x, format='MMMM/yyyy', locale='pt_BR'))
      st.dataframe(dfcompras, width=1200, hide_index=True)
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Transferências e gastos extras')
      dfTransf = config_tabela_transferencias(dfFinal.copy())
      dfTransf['Mês'] = pd.to_datetime(dfTransf['Mês'], format='%d-%m-%Y')
      # Formatando a data para "nome do mês/ano"
      dfTransf['Mês'] = dfTransf['Mês'].apply(lambda x: format_date(x, format='MMMM/yyyy', locale='pt_BR'))
      st.dataframe(dfTransf, width=1200, hide_index=True)

  insumosSemPedido = config_insumos_blueme_sem_pedido(GET_INSUMOS_BLUE_ME_SEM_PEDIDO(), data_inicio, data_fim)
  insumosComPedido = config_insumos_blueme_com_pedido(GET_INSUMOS_BLUE_ME_COM_PEDIDO(), data_inicio, data_fim)
  classificacoes = preparar_dados_classe_selecionada(insumosSemPedido, 'Classificacao')
  forneceforesSemPedido = preparar_dados_classe_selecionada(insumosSemPedido, 'Fornecedor') 
  fornecedoresComPedido = preparar_dados_classe_selecionada(insumosSemPedido, 'Fornecedor') 

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      col4, col5, col6 = st.columns([5, 4, 4])
      with col4:
        st.subheader('Insumos BlueMe sem Pedido')
      with col5:
        classificacoes_selecionadas = st.multiselect(label='Selecione Classificações', options=classificacoes)
        insumosSemPedido.rename(columns = {'Classificacao': 'Classificação'}, inplace=True)
        insumosSemPedido = filtrar_por_classe_selecionada(insumosSemPedido, 'Classificação', classificacoes_selecionadas)
      with col6:
        fornecedores_selecionadss = st.multiselect(label='Selecione Fornecedores', options=forneceforesSemPedido, key=1)
        insumosSemPedido = filtrar_por_classe_selecionada(insumosSemPedido, 'Fornecedor', fornecedores_selecionadss)
      valorTotal = insumosSemPedido['Valor Líquido'].sum()
      valorTotal = format_brazilian(valorTotal)
      insumosSemPedido = format_columns_brazilian(insumosSemPedido, ['Valor Líquido'])
      st.dataframe(insumosSemPedido, width=1200, hide_index=True)
      st.write('Valor Líquido Total = R$', valorTotal)
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      col4, col5, = st.columns([7, 5])
      with col4:
        st.subheader('Insumos BlueMe com Pedido')
      with col5:
        fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedoresComPedido, key=2)
        insumosComPedido = filtrar_por_classe_selecionada(insumosComPedido, 'Fornecedor', fornecedores_selecionados)
      valorTotal = insumosComPedido['Valor Líquido'].sum()
      cols = ['Valor Líquido', 'Valor Insumos', 'Insumos - V. Líq']
      valorTotal = format_brazilian(valorTotal)
      insumosComPedido = format_columns_brazilian(insumosComPedido, cols)
      st.dataframe(insumosComPedido, width=1200, hide_index=True)
      st.write('Valor Líquido Total = R$', valorTotal)

if __name__ == '__main__':
  main()
