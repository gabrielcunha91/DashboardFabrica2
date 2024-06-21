import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from utils.queries import *
from utils.functions import *
from utils.components import *

st.set_page_config(
  layout = 'wide',
  page_title = 'Análise Pereto',
  page_icon='🎯',
  initial_sidebar_state="collapsed"
)


if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')

##comparar valor unitário com outras casas

def config_tabela_para_pareto(dfNomeEstoque, dfNomeCompras, categoria, key):
  lojas_selecionadas, data_inicio, data_fim = preparar_filtros(key)
  dfNomeEstoque = config_compras_quantias(dfNomeEstoque, data_inicio, data_fim, lojas_selecionadas)
  dfNomeCompras = config_compras_quantias(dfNomeCompras, data_inicio, data_fim, lojas_selecionadas)

  dfNomeEstoque = dfNomeEstoque[dfNomeEstoque['Categoria'] == categoria]
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
  df = df.groupby(['Nome Produto', 'Loja'], as_index=False).agg({
    'Valor Total': 'sum',
    'Quantidade': 'sum',
    'Fornecedor': 'first',
    'Unidade de Medida': 'first',
  })

  df['Valor Unitário'] = df['Valor Total'] / df['Quantidade']
  df['Valor Unitário'] = df['Valor Unitário'].round(2)
  df = df.drop(['Valor Total', 'Quantidade', 'Loja'], axis=1)

  return df


def comparativo_entre_lojas(df):
  data_inicio_default, data_fim_default = preparar_dados_datas()
  # Seletores para loja e produto
  lojas = df['Loja'].unique()
  col, col1 = st.columns(2)
  with col:
    loja1 = st.selectbox('Selecione a primeira loja:', lojas)
  with col1:
    loja2 = st.selectbox('Selecione a segunda loja:', lojas)

  col, col1, col2, col3 = st.columns([3, 2, 1, 1])
  with col:
    search_term = st.text_input('Pesquise parte do nome de um produto:', '')
    # Filtrando produtos com base no termo de pesquisa
    if search_term:
      produtos_filtrados = df[df['Nome Produto'].str.contains(search_term, case=False, na=False)]['Nome Produto'].unique()
    else:
      produtos_filtrados = df['Nome Produto'].unique()
  with col1:
    # Seletor de produto com base na pesquisa
    if len(produtos_filtrados) > 0:
      produto_selecionado = st.selectbox('Selecione o produto com base na pesquisa:', produtos_filtrados)
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

    # Exibindo os dataframes filtrados lado a lado
    with st.container(border=True):
      col1, col2 = st.columns(2)
      with col1:
        st.subheader(f'{loja1}')
        st.dataframe(df_loja1, hide_index=True)

      with col2:
        st.subheader(f'{loja2}')
        st.dataframe(df_loja2, hide_index=True)
  else:
      st.info('Selecione um produto para visualizar os dados.')


def main ():
  config_sidebar()
  streamlit_style = """
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 270px;} 
   </style>
    """
  st.markdown(streamlit_style, unsafe_allow_html=True)

  dfComparativo = GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE()

  tab1, tab2, tab3, tab4 = st.tabs(["ALIMENTOS", "BEBIDAS", " PRODUTOS DE LIMP/HIGIENE", "COMPARATIVO ENTRE LOJAS"])
  with tab1:
    dfNomeEstoque, dfNomeCompras = config_tabela_para_pareto(GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE(), GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA(), 'ALIMENTOS', 1)
    config_diagramas_pareto(dfNomeEstoque, dfNomeCompras, 'ALIMENTOS', 'Alimentos')
    with st.container(border=True):
      dfNomeEstoque = dfNomeEstoque.drop(['Categoria', 'Fator de Proporção'], axis=1)
      pesquisa_por_produto(dfNomeEstoque, 1)

  with tab2:
    dfNomeEstoque2, dfNomeCompras2 = config_tabela_para_pareto(GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE(), GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA(), 'BEBIDAS', 2)
    config_diagramas_pareto(dfNomeEstoque2, dfNomeCompras2, 'BEBIDAS', 'Bebidas')
    with st.container(border=True):
      dfNomeEstoque2 = dfNomeEstoque2.drop(['Categoria', 'Fator de Proporção'], axis=1)
      pesquisa_por_produto(dfNomeEstoque2, 2)

  with tab3:
    dfNomeEstoque3, dfNomeCompras3 = config_tabela_para_pareto(GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE(), GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA(), 'DESCARTAVEIS/HIGIENE E LIMPEZA', 3)
    config_diagramas_pareto(dfNomeEstoque3, dfNomeCompras3, 'DESCARTAVEIS/HIGIENE E LIMPEZA', 'Produtos de Limpeza e Higiene')
    with st.container(border=True):
      dfNomeEstoque3 = dfNomeEstoque3.drop(['Categoria', 'Fator de Proporção'], axis=1)
      pesquisa_por_produto(dfNomeEstoque3, 3)

  with tab4:
    st.title('Comparativo de Valores Unitários entre Lojas')
    comparativo_entre_lojas(dfComparativo)



if __name__ == '__main__':
  main()

