import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions import *
from utils.components import *

pd.set_option('future.no_silent_downcasting', True)

def main():
  st.set_page_config(
    layout = 'wide',
    page_title = 'CMV'
  )
  st.title('CMV')
  st.divider()

  lojasComDados = preparar_dados_lojas(GET_FATURAM_ZIG_ALIM_BEB_MENSAL())
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  df1 = GET_FATURAM_ZIG_ALIM_BEB_MENSAL()
  df2 = GET_ESTOQUES_POR_CATEG_AGRUPADOS()
  df3 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_SEM_PEDIDO()  
  df4 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_coM_PEDIDO()
  df5 = GET_TRANSF_ESTOQUE_AGRUPADOS()  
  df6 = GET_PERDAS_E_CONSUMO_AGRUPADOS()

  df3 = df3[df3['ID_Loja'] != 296]

  df1 = filtrar_por_lojas(df1, lojas_selecionadas)
  df1 = filtrar_por_datas(df1, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df2 = filtrar_por_lojas(df2, lojas_selecionadas)
  df2 = filtrar_por_datas(df2, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df3 = filtrar_por_lojas(df3, lojas_selecionadas)
  df3 = filtrar_por_datas(df3, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df4 = filtrar_por_lojas(df4, lojas_selecionadas)
  df4 = filtrar_por_datas(df4, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df5 = filtrar_por_lojas(df5, lojas_selecionadas)
  df5 = filtrar_por_datas(df5, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df6 = filtrar_por_lojas(df6, lojas_selecionadas)
  df6 = filtrar_por_datas(df6, data_inicio, data_fim, 'Primeiro_Dia_Mes')

  dfFinal = merge_dataframes(df1, df2, df3, df4, df5, df6)
 
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
      st.dataframe(config_tabela_compras(dfFinal), width=1200, hide_index=True)
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Transferências e gastos extras')
      st.dataframe(config_tabela_transferencias(dfFinal), width=1200, hide_index=True)

  insumosSemPedido = config_insumos_blueme_sem_pedido(GET_INSUMOS_BLUE_ME_SEM_PEDIDO(), data_inicio, data_fim)
  insumosComPedido = config_insumos_blueme_com_pedido(GET_INSUMOS_BLUE_ME_COM_PEDIDO(), data_inicio, data_fim)
  classificacoes = preparar_dados_classificacoes(insumosSemPedido)
  forneceforesSemPedido = preparar_dados_fornecedores(insumosSemPedido) 
  fornecedoresComPedido = preparar_dados_fornecedores(insumosComPedido)

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      col4, col5, col6 = st.columns([5, 4, 4])
      with col4:
        st.subheader('Insumos BlueMe sem Pedido')
      with col5:
        classificacoes_selecionadas = st.multiselect(label='Selecione Classificações', options=classificacoes)
        insumosSemPedido.rename(columns = {'Classificacao': 'Classificação'}, inplace=True)
        insumosSemPedido = filtrar_por_classificacao(insumosSemPedido, classificacoes_selecionadas)
      with col6:
        fornecedores_selecionadss = st.multiselect(label='Selecione Fornecedores', options=forneceforesSemPedido)
        insumosSemPedido = filtrar_por_fornecedor(insumosSemPedido, fornecedores_selecionadss)
      st.dataframe(insumosSemPedido, width=1200, hide_index=True)
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      col4, col5, = st.columns([7, 5])
      with col4:
        st.subheader('Insumos BlueMe com Pedido')
      with col5:
        fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedoresComPedido)
        insumosComPedido = filtrar_por_fornecedor(insumosComPedido, fornecedores_selecionados)
      st.dataframe(insumosComPedido, width=1200, hide_index=True)


if __name__ == '__main__':
  main()
