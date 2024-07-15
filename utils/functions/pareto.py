import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *


def config_media_anterior(df, data_inicio, data_fim, lojas_selecionadas):
  df2 = df.copy()
  primeiro_dia_dois_meses_antes = data_inicio.replace(day=1) - timedelta(days=1)
  primeiro_dia_dois_meses_antes = primeiro_dia_dois_meses_antes.replace(month=(primeiro_dia_dois_meses_antes.month - 2) % 12 + 1, day=1)
  data_inicio = primeiro_dia_dois_meses_antes

  df2 = filtrar_por_datas(df2, data_inicio, data_fim, 'Data Compra')
  df2['V. Unit. 3 Meses Ant.'] = df2['Valor Total'] / df2['Quantidade']

  df2 = df2.groupby(['ID Produto', 'Nome Produto', 'Loja', 'Categoria'], as_index=False).agg({
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
  df['Fator de Proporção'] = df['Fator de Proporção'].astype(float)

  df2 = config_media_anterior(df, data_inicio, data_fim, lojas_selecionadas)

  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data Compra')

  df = df.groupby(['ID Produto', 'Nome Produto', 'Loja', 'Categoria'], as_index=False).agg({
    'Quantidade': 'sum',
    'Valor Total': 'sum',
    'Unidade de Medida': 'first',
    'Fator de Proporção': 'first',
    'Fornecedor': 'first'
  })

  df = df.merge(df2, how='left', on=['ID Produto', 'Nome Produto', 'Loja', 'Categoria'])
  df = df.sort_values(by='Nome Produto', ascending=True)

  df['Quantidade Ajustada'] = df['Quantidade'] * df['Fator de Proporção']
  df['Valor Unitário'] = df['Valor Total'] / df['Quantidade']
  df['Valor Unit. Ajustado'] = df['Valor Total'] / df['Quantidade Ajustada']

  df['Quantidade'] = df['Quantidade'].round(2)
  df['Quantidade Ajustada'] = df['Quantidade Ajustada'].round(2)
  df['Valor Total'] = df['Valor Total'].round(2)
  df['Valor Unitário'] = df['Valor Unitário'].round(2)
  df['Valor Unit. Ajustado'] = df['Valor Unit. Ajustado'].round(2)
  df['V. Unit. 3 Meses Ant.'] = df['V. Unit. 3 Meses Ant.'].round(2)
  nova_ordem = ['ID Produto', 'Nome Produto', 'Loja', 'Categoria', 'Quantidade', 'Valor Total', 'Unidade de Medida', 'Valor Unitário', 'V. Unit. 3 Meses Ant.',
                 'Quantidade Ajustada', 'Valor Unit. Ajustado', 'Fator de Proporção', 'Fornecedor']
  df = df[nova_ordem]

  return df




def config_por_categ_avaliada(df, categoria):
  df.sort_values(by=categoria, ascending=False, inplace=True)
  df['Porcentagem Acumulada'] = df[categoria].cumsum() / df[categoria].sum() * 100
  df['Porcentagem'] = (df[categoria] / df[categoria].sum()) * 100
  return df


def preparar_filtros(tabIndex):
  lojasComDados = preparar_dados_lojas_user()
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores_pareto(lojasComDados, data_inicio_default, data_fim_default, tab_index=tabIndex)
  st.divider()
  return lojas_selecionadas, data_inicio, data_fim


def config_tabela_para_pareto(dfNomeEstoque, dfNomeCompras, categoria, key):
  lojas_selecionadas, data_inicio, data_fim = preparar_filtros(key)
  dfNomeEstoque = config_compras_quantias(dfNomeEstoque, data_inicio, data_fim, lojas_selecionadas)
  dfNomeCompras = config_compras_quantias(dfNomeCompras, data_inicio, data_fim, lojas_selecionadas)

  dfNomeEstoque = dfNomeEstoque[dfNomeEstoque['Categoria'] == categoria]
  dfNomeCompras = dfNomeCompras[dfNomeCompras['Categoria'] == categoria]
  return dfNomeEstoque, dfNomeCompras


def config_diagramas_pareto(dfNomeEstoque, dfNomeCompras, categoria, categString):
  df_por_valor = config_por_categ_avaliada(dfNomeEstoque.copy(), 'Valor Total')
  df_valor_unitario = config_por_categ_avaliada(dfNomeCompras.copy(), 'Valor Unitário')
  df_valor_unit_ajust = config_por_categ_avaliada(dfNomeEstoque.copy(), 'Valor Unit. Ajustado')  

  keyDiagrama1 = categoria + '_valor'
  keyDiagrama2 = categoria + '_valor_unitario'
  keyDiagrama3 = categoria + '_valor_unit_ajust'

  with st.container(border=True):
    st.subheader('Diagrama de Pareto sobre ' + categString + ' em relação ao valor total')
    diagrama_pareto_por_categ_avaliada(df_por_valor, 'Valor Total', key=keyDiagrama1)
  with st.container(border=True):    
    st.subheader('Diagrama de Pareto sobre ' + categString + ' em relação ao valor Unitário de cada')
    diagrama_pareto_por_categ_avaliada(df_valor_unitario, 'Valor Unitário', key=keyDiagrama2)
  with st.container(border=True):
    st.subheader('Diagrama de Pareto sobre ' + categString + ' em relação ao valor unitário ajustado')
    diagrama_pareto_por_categ_avaliada(df_valor_unit_ajust, 'Valor Unit. Ajustado', key=keyDiagrama3)


def pesquisa_por_produto(dfNomeEstoque, key):
  dfNomeEstoque = dfNomeEstoque.drop(['Fornecedor'], axis=1)
  col0, col, col1, col2 = st.columns([1.6, 15, 8, 2])
  with col:
    st.subheader('Informações detalhadas dos produtos')
  with col1:
    search_term = st.text_input('Pesquisar por nome do produto:', '', key=key)
    if search_term:
      filtered_df = dfNomeEstoque[dfNomeEstoque['Nome Produto'].str.contains(search_term, case=False, na=False)]
    else:
      filtered_df = dfNomeEstoque
  row1 = st.columns([1, 15, 1])
  row1[1].dataframe(filtered_df, width=1100 ,hide_index=True)

def create_columns_comparativo(df):
  df.loc[:,'Quantidade'] = df['Quantidade'].astype(str)
  df.loc[:,'Valor Total'] = df['Valor Total'].astype(str)
  df.loc[:,'Quantidade'] = df['Quantidade'].str.replace(',', '.').astype(float)
  df.loc[:, 'Valor Total'] = df['Valor Total'].str.replace(',', '.').astype(float)
  df = df[df['Quantidade'] > 0]
  df = df.groupby(['ID Produto', 'Nome Produto', 'Loja'], as_index=False).agg({
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
    st.subheader('Comparativo individual por lojas selecionadas e produto selecionado')
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
    st.subheader('Comparação de valor unitário pago pela loja selecionada e loja que paga menor preço')
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

    newdf = df.merge(df_min, how='left', on=['ID Produto', 'Nome Produto', 'Unidade de Medida'])

    # Se produto_selecionado for 'Todos', não aplicamos filtro adicional
    if produto_selecionado and 'Todos' not in produto_selecionado:
      newdf = newdf[newdf['Nome Produto'].isin(produto_selecionado)]

    newdf = newdf.drop(['Unidade de Medida', 'Loja'], axis=1)
    newdf['Diferença Preços'] = newdf['Valor Unitário'] - newdf['Menor V. Unit.']
    newdf = newdf.sort_values(by='Diferença Preços', ascending=False).reset_index(drop=True)
    newdf = newdf.rename(columns={'ID Produto': 'ID Prod.'})
    newdf = format_columns_brazilian(newdf, ['Valor Unitário', 'Menor V. Unit.', 'Diferença Preços'])
    st.dataframe(newdf, use_container_width=True, hide_index=True)

