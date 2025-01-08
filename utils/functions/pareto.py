import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *
from dateutil.relativedelta import relativedelta
from streamlit_echarts import st_echarts


def config_media_anterior(df, data_inicio, data_fim, lojas_selecionadas):
  df2 = df.copy()
  primeiro_dia_dois_meses_antes = data_inicio.replace(day=1) - timedelta(days=1)
  primeiro_dia_dois_meses_antes = primeiro_dia_dois_meses_antes.replace(month=(primeiro_dia_dois_meses_antes.month - 2) % 12 + 1, day=1)
  data_inicio = primeiro_dia_dois_meses_antes

  df2 = filtrar_por_datas(df2, data_inicio, data_fim, 'Data Compra')
  df2 = filtrar_por_classe_selecionada(df2, 'Loja', lojas_selecionadas)
  df2['V. Unit. 3 Meses Ant.'] = df2['Valor Total'] / df2['Quantidade']

  df2 = df2.groupby(['ID Produto Nivel 4', 'Nome Produto', 'Loja', 'Categoria'], as_index=False).agg({
    'V. Unit. 3 Meses Ant.': 'first',
  })

  return df2


def config_compras_quantias(df, data_inicio, data_fim, lojas_selecionadas):
  df = df.sort_values(by='Nome Produto', ascending=False)
  df = filtrar_por_classe_selecionada(df, 'Loja' , lojas_selecionadas)

  df['Quantidade'] = df['Quantidade'].astype(str)
  df['Valor Total'] = df['Valor Total'].astype(str)
  df['Quantidade'] = df['Quantidade'].str.replace(',', '.').astype(float)
  df['Valor Total'] = df['Valor Total'].str.replace(',', '.').astype(float)

  df2 = config_media_anterior(df, data_inicio, data_fim, lojas_selecionadas)

  dfSemFiltroData = df.copy()

  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data Compra')

  df = df.groupby(['ID Produto Nivel 4', 'Nome Produto', 'Loja', 'Categoria'], as_index=False).agg({
    'Quantidade': 'sum',
    'Valor Total': 'sum',
    'Valor Unitário': 'mean',
    'Unidade de Medida': 'first',
    'Fator de Proporção': 'first'
  })

  df = df.merge(df2, how='left', on=['ID Produto Nivel 4', 'Nome Produto', 'Loja', 'Categoria'])
  df = df.sort_values(by='Nome Produto', ascending=True)

  df['Valor Unitário'] = df['Valor Total'] / df['Quantidade']

  df['Quantidade'] = df['Quantidade'].round(2)
  df['Valor Total'] = df['Valor Total'].round(2)
  df['Valor Unitário'] = df['Valor Unitário'].round(2)
  df['V. Unit. 3 Meses Anteriores'] = df['V. Unit. 3 Meses Ant.'].round(2)
  nova_ordem = ['ID Produto Nivel 4', 'Nome Produto', 'Loja', 'Categoria', 'Quantidade', 'Valor Total', 'Unidade de Medida', 'Valor Unitário', 'V. Unit. 3 Meses Anteriores']
  df = df[nova_ordem]

  return df, dfSemFiltroData


def config_por_categ_avaliada(df, categoria):
  df.sort_values(by=categoria, ascending=False, inplace=True)
  df['Porcentagem Acumulada'] = df[categoria].cumsum() / df[categoria].sum() * 100
  df['Porcentagem'] = (df[categoria] / df[categoria].sum()) * 100
  produto = []
  produto.append(df['Nome Produto'].iloc[0])
  return df, produto


def preparar_filtros(tabIndex):
  lojasComDados = preparar_dados_lojas_user()
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores_pareto(lojasComDados, data_inicio_default, data_fim_default, tab_index=tabIndex)
  st.divider()
  return lojas_selecionadas, data_inicio, data_fim


def config_tabela_para_pareto(dfNomeCompras, categoria, key):
  lojas_selecionadas, data_inicio, data_fim = preparar_filtros(key)
  dfNomeCompras, dfSemFiltroData = config_compras_quantias(dfNomeCompras, data_inicio, data_fim, lojas_selecionadas)

  dfNomeCompras = dfNomeCompras[dfNomeCompras['Categoria'] == categoria]
  dfSemFiltroData = dfSemFiltroData[dfSemFiltroData['Categoria'] == categoria]
  
  return dfNomeCompras, lojas_selecionadas, dfSemFiltroData, data_fim


def config_diagramas_pareto(dfNomeCompras, categoria, categString):
  df_por_valor, produto = config_por_categ_avaliada(dfNomeCompras.copy(), 'Valor Total')

  keyDiagrama1 = categoria + '_valor'

  with st.container(border=True):
    st.subheader('Diagrama de Pareto sobre ' + categString + ' em relação ao valor total')
    diagrama_pareto_por_categ_avaliada(df_por_valor, 'Valor Total', key=keyDiagrama1)
  
  return produto

def grafico_historico_precos(df_filtrado, key):

  df_filtrado = df_filtrado[df_filtrado['Valor Unitário'].notna() & (df_filtrado['Valor Unitário'] != 0)]

  # Obtém os produtos únicos
  produtos = df_filtrado['Nome Produto'].unique()
  
  # Prepara os dados para o eixo X (meses)
  meses = df_filtrado['Mês'].unique()
  meses = sorted(meses, key=lambda x: pd.to_datetime(x, format='%m/%Y'))  # Ordena os meses
  
  # Prepara os dados para o gráfico
  series = []
  for produto in produtos:
    df_produto = df_filtrado[df_filtrado['Nome Produto'] == produto]
    valores = [
      df_produto[df_produto['Mês'] == mes]['Valor Unitário'].iloc[0] if mes in df_produto['Mês'].values else None
      for mes in meses
    ]
    series.append({
      "name": produto,
      "type": "line",
      "data": valores
    })
  
  # Configurações do gráfico
  option = {
    "tooltip": {"trigger": "axis"},
    "legend": {"data": list(produtos)},
    "xAxis": {"type": "category", "data": list(meses)},
    "yAxis": {"type": "value"},
    "series": series
  }
  
  # Renderiza o gráfico no Streamlit
  st_echarts(options=option, key=key)


def config_historico_valores(df, data_fim, key):
  df.drop(['ID Produto Nivel 4', 'Loja', 'Fornecedor', 'Categoria', 'Quantidade', 'Valor Total', 'Unidade de Medida', 'Fator de Proporção'], axis=1, inplace=True)
  df['Data Compra'] = pd.to_datetime(df['Data Compra'], format='%Y-%m-%d')
  data_fim = pd.to_datetime(data_fim, format='%d-%m-%Y', errors='coerce')
  # Calculando os últimos 6 meses
  data_anterior = [data_fim - relativedelta(months=i) for i in range(0, 6)]

  # Filtrando o DataFrame por produto e meses
  dfs_mensais = []
  for i, data in enumerate(data_anterior):
    mes = data.strftime('%m/%Y')
    df_mes = df[
      (df['Data Compra'].dt.month == data.month) &
      (df['Data Compra'].dt.year == data.year)
    ]
    df_mes['Mês'] = mes

    df_mes_grouped = df_mes.groupby(['Nome Produto', 'Mês'], as_index=False).agg({
      'Valor Unitário': 'mean'
    })
    dfs_mensais.append(df_mes_grouped)

  df_filtrado = pd.concat(dfs_mensais, ignore_index=True)    
  grafico_historico_precos(df_filtrado, key)
  return

def pesquisa_por_produto(dfNomeCompras, key, data_fim, dfSemDataFiltrada, key_grafico, produto_mais_significativo):
  col0, col, col1, col2 = st.columns([1.6, 15, 8, 2])
  with col:
    st.subheader('Compras de insumos agrupadas por período selecionado')
  with col1:
    search_term = st.text_input('Pesquisar por nome do produto:', '', key=key)
    if search_term:
      filtered_df = dfNomeCompras[dfNomeCompras['Nome Produto'].str.contains(search_term, case=False, na=False)]
      dfSemDataFiltrada = dfSemDataFiltrada[dfSemDataFiltrada['Nome Produto'].str.contains(search_term, case=False, na=False)]
    else:
      filtered_df = dfNomeCompras
      dfSemDataFiltrada = filtrar_por_classe_selecionada(dfSemDataFiltrada, 'Nome Produto', produto_mais_significativo)
  row1 = st.columns([1, 15, 1])
  row1[1].dataframe(filtered_df, use_container_width=True,hide_index=True)
  st.divider()
  col0, col, col1, col2 = st.columns([1.6, 15, 8, 2])
  with col:
    st.subheader('Histórico de preço do produto selecionado')
  row1 = st.columns([1, 15, 1])
  with row1[1]:
    config_historico_valores(dfSemDataFiltrada, data_fim, key_grafico)


def config_compras_insumos_detalhadas(categoria, key_data1, key_data2, keysearch, lojas_selecionadas):
  data_inicio_default, data_fim_default = preparar_dados_datas()
  col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
  with col1: 
    st.subheader('Detalhamento de compras')
  with col2:
    data_inicio = st.date_input('Data Início da Compra', value=data_inicio_default, key=key_data1, format="DD/MM/YYYY")
  with col3:
    data_fim = st.date_input('Data Fim da Compra', value=data_fim_default, key=key_data2, format="DD/MM/YYYY") 
    df = GET_COMPRAS_PRODUTOS_COM_RECEBIMENTO(data_inicio, data_fim, categoria)
  with col4:
    search_term = st.text_input('Pesquisar por nome do produto:', '', key=keysearch)
    if search_term:
      filtered_df = df[df['Nome Produto'].str.contains(search_term, case=False, na=False)]
    else:
      filtered_df = df
  filtered_df = filtrar_por_classe_selecionada(filtered_df, 'Loja', lojas_selecionadas)


  row1 = st.columns([1, 15, 1])
  row1[1].dataframe(filtered_df, use_container_width=True,hide_index=True)


def create_columns_comparativo(df):
  df.loc[:,'Quantidade'] = df['Quantidade'].astype(str)
  df.loc[:,'Valor Total'] = df['Valor Total'].astype(str)
  df.loc[:,'Quantidade'] = df['Quantidade'].str.replace(',', '.').astype(float)
  df.loc[:, 'Valor Total'] = df['Valor Total'].str.replace(',', '.').astype(float)
  df = df[df['Quantidade'] > 0]
  df = df.groupby(['ID Produto Nivel 4', 'Nome Produto', 'Loja'], as_index=False).agg({
    'Valor Total': 'sum',
    'Quantidade': 'sum',
    'Fornecedor': 'first',
    'Unidade de Medida': 'first',
  })

  df['Valor Unitário'] = df['Valor Total'] / df['Quantidade']
  df['Valor Unitário'] = df['Valor Unitário'].round(2)
  df = df.drop(['Valor Total'], axis=1)

  return df


def comparativo_entre_lojas(df):
  data_inicio_default, data_fim_default = preparar_dados_datas()
  # Seletores para loja e produto
  with st.container(border=True):
    st.subheader('Comparativo Valor Unitário por Insumo')
    lojas = df['Loja'].unique()
    col, col1 = st.columns(2)
    with col:
      loja1 = st.selectbox('Selecione a primeira loja:', lojas)
    with col1:
      loja2 = st.selectbox('Selecione a segunda loja:', lojas)

    col, col1, col2, col3 = st.columns([3, 2, 1, 1])
    with col:
      search_term = st.text_input('Pesquise parte do nome de um produto:', '', key='input_pesquisa_comparacao_ind')
      # Filtrando produtos com base no termo de pesquisa
      if search_term:
        produtos_filtrados = df[df['Nome Produto'].str.contains(search_term, case=False, na=False)]['Nome Produto'].unique()
      else:
        produtos_filtrados = df['Nome Produto'].unique()
    with col1:
      # Seletor de produto com base na pesquisa
      if len(produtos_filtrados) > 0:
        produto_selecionado = st.selectbox('Selecione o produto com base na pesquisa:', produtos_filtrados, key='input_prod_comparacao_ind')
      else:
        produto_selecionado = None
        st.warning('Nenhum produto encontrado.')
    with col2:
      data_inicio = st.date_input('Data de Início', value=data_inicio_default, key='data_inicio_input', format="DD/MM/YYYY")
    with col3:
      data_fim = st.date_input('Data de Fim', value=data_fim_default, key='data_fim_input', format="DD/MM/YYYY")

    data_inicio = pd.to_datetime(data_inicio)
    data_fim = pd.to_datetime(data_fim)

    # Filtrando os dataframes com base nas seleções
    if produto_selecionado:
      df_loja1 = df[(df['Loja'] == loja1) & (df['Nome Produto'] == produto_selecionado)]
      df_loja2 = df[(df['Loja'] == loja2) & (df['Nome Produto'] == produto_selecionado)]

      filtrar_por_datas(df_loja1, data_inicio, data_fim, 'Data Compra')
      filtrar_por_datas(df_loja2, data_inicio, data_fim, 'Data Compra')

      df_loja1 = create_columns_comparativo(df_loja1)
      df_loja2 = create_columns_comparativo(df_loja2)

      df_loja1 = df_loja1.drop(['Loja', 'Quantidade'], axis=1)
      df_loja2 = df_loja2.drop(['Loja', 'Quantidade'], axis=1)

      df_loja1 = df_loja1.rename(columns = {'Unidade de Medida': 'Unid. Medida'})
      df_loja2 = df_loja2.rename(columns = {'Unidade de Medida': 'Unid. Medida'})

      df_loja1['Valor Unitário'] = df_loja1['Valor Unitário'].apply(format_brazilian)
      df_loja2['Valor Unitário'] = df_loja2['Valor Unitário'].apply(format_brazilian)

      # Exibindo os dataframes filtrados lado a lado
      with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
          st.subheader(f'{loja1}')
          st.dataframe(df_loja1, use_container_width=True, hide_index=True)

        with col2:
          st.subheader(f'{loja2}')
          st.dataframe(df_loja2, use_container_width=True, hide_index=True)
    else:
        st.info('Selecione um produto para visualizar os dados.')



def comparativo_valor_mais_baixo(df1):
  df = df1.copy()
  data_inicio_default, data_fim_default = preparar_dados_datas()
  with st.container(border=True):
    st.subheader('Comparação de valor unitário - Menor Preço')
    lojas = df['Loja'].unique()
    col, col1, col2 = st.columns([5, 3, 3])
    with col:
      loja1 = st.selectbox('Selecione uma loja:', lojas)
    with col1:
      data_inicio = st.date_input('Data de Início', value=data_inicio_default, key='data_inicio_input2', format="DD/MM/YYYY")
    with col2:
      data_fim = st.date_input('Data de Fim', value=data_fim_default, key='data_fim_input2', format="DD/MM/YYYY")

    col3, col4, col5 = st.columns([5, 3, 3])
    with col3:
      search_term = st.text_input('Pesquise parte do nome de um produto:', '', key='input_pesquisa_menor_preco')
      # Filtrando produtos com base no termo de pesquisa
      if search_term:
        produtos_filtrados = df[df['Nome Produto'].str.contains(search_term, case=False, na=False)]['Nome Produto'].unique()
      else:
        produtos_filtrados = df['Nome Produto'].unique()
      produtos_filtrados = np.append(produtos_filtrados, 'Todos')
    with col4:
      # Seletor de produto com base na pesquisa
      if len(produtos_filtrados) > 0:
        produto_selecionado = st.multiselect('Selecione produtos com base na pesquisa:', produtos_filtrados, default=['Todos'], key='input_prod_menor_preco')
      else:
        produto_selecionado = None
        st.warning('Nenhum produto encontrado.')

    data_inicio = pd.to_datetime(data_inicio)
    data_fim = pd.to_datetime(data_fim)

    filtrar_por_datas(df, data_inicio, data_fim, 'Data Compra')

    df2 = df.copy()
    df2 = create_columns_comparativo(df2)
    df_min = df2.loc[df2.groupby('Nome Produto')['Valor Unitário'].idxmin()]
    df_min = df_min.rename(columns={'Loja': 'Loja Menor Preço', 'Quantidade': 'Qtd. Menor Preço', 'Fornecedor': 'Forn. Menor Preço', 'Valor Unitário': 'Menor V. Unit.'})

    df = df[df['Loja'] == loja1]
    df = create_columns_comparativo(df)

    newdf = df.merge(df_min, how='left', on=['ID Produto Nivel 4', 'Nome Produto', 'Unidade de Medida'])

    # Se produto_selecionado for 'Todos', não aplicamos filtro adicional
    if produto_selecionado and 'Todos' not in produto_selecionado:
      newdf = newdf[newdf['Nome Produto'].isin(produto_selecionado)]

    newdf = newdf.drop(['Unidade de Medida', 'Loja'], axis=1)
    newdf['Diferença Preços'] = newdf['Valor Unitário'] - newdf['Menor V. Unit.']
    newdf = newdf.sort_values(by='Diferença Preços', ascending=False).reset_index(drop=True)
    newdf = newdf.rename(columns={'ID Produto Nivel 4': 'ID Prod.'})
    newdf = format_columns_brazilian(newdf, ['Valor Unitário', 'Menor V. Unit.', 'Diferença Preços'])
    st.dataframe(newdf, use_container_width=True, hide_index=True)

