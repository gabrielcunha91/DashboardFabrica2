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


def config_compras_quantias(df, data_inicio, data_fim, lojas_selecionadas):
  df = df.sort_values(by='Nome Produto', ascending=False)

  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data Compra')
  df = filtrar_por_lojas(df, lojas_selecionadas)

  df = df.drop(['Fornecedor', 'Data Compra'], axis=1)
  df['Quantidade'] = df['Quantidade'].astype(str)
  df['Valor'] = df['Valor'].astype(str)
  df['Quantidade'] = df['Quantidade'].str.replace(',', '.').astype(float)
  df['Valor'] = df['Valor'].str.replace(',', '.').astype(float)
  df['Fator de Proporção'] = df['Fator de Proporção'].astype(float)

  df = df.groupby(['Nome Produto', 'Loja', 'Categoria'], as_index=False).agg({
    'Quantidade': 'sum',
    'Valor': 'sum',
    'Unidade de Medida': 'first',
    'Fator de Proporção': 'first'
  })

  df['Quantidade Ajustada'] = df['Quantidade'] * df['Fator de Proporção']
  df['Valor Unitário'] = df['Valor'] / df['Quantidade']
  df['Valor Unit. Ajustado'] = df['Valor'] / df['Quantidade Ajustada']

  df['Quantidade'] = df['Quantidade'].round(2)
  df['Quantidade Ajustada'] = df['Quantidade Ajustada'].round(2)
  df['Valor'] = df['Valor'].round(2)
  df['Valor Unitário'] = df['Valor Unitário'].round(2)
  df['Valor Unit. Ajustado'] = df['Valor Unit. Ajustado'].round(2)

  return df

##comparar valor unitário com outras casas
def config_por_categ_avaliada(df, categoria):
  df.sort_values(by=categoria, ascending=False, inplace=True)
  df['Porcentagem Acumulada'] = df[categoria].cumsum() / df[categoria].sum() * 100
  df['Porcentagem'] = (df[categoria] / df[categoria].sum()) * 100
  return df


def preparar_filtros(tabIndex):
  lojasComDados = preparar_dados_lojas(GET_FATURAM_ZIG_ALIM_BEB_MENSAL())
  data_inicio_default, data_fim_default = preparar_dados_datas()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores_pareto(lojasComDados, data_inicio_default, data_fim_default, tab_index=tabIndex)
  st.divider()
  return lojas_selecionadas, data_inicio, data_fim


def diagrama_pareto_por_categ_avaliada(df, categoria, key):
  df = df.head(10)
  # Configuração do gráfico
  options = {
    "title": {
      "text": "",
      "left": "center"
    },
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {
        "type": "shadow"
      }
    },
    "xAxis": [
      {
        "type": "category",
        "data": df['Nome Produto'].tolist()
      }
    ],
    "yAxis": [
      {
        "type": "value",
        "name": categoria
      },
      {
        "type": "value",
        "name": "Porcentagem Acumulada",
        "axisLabel": {
          "formatter": "{value} %"
        }
      }
    ],
    "series": [
      {
        "name": categoria,
        "type": "bar",
        "data": df[categoria].tolist()
      },
      {
        "name": "Porcentagem Acumulada",
        "type": "line",
        "yAxisIndex": 1,
        "data": df['Porcentagem Acumulada'].tolist()
      }
    ]
  }
  st_echarts(options=options, key=key)


def criar_seletores_pareto(LojasComDados, data_inicio_default, data_fim_default, tab_index):
  col1, col2, col3 = st.columns([2, 1, 1])

  # Adiciona seletores
  with col1:
    lojas_selecionadas = st.multiselect(
      label='Selecione Lojas', 
      options=LojasComDados, 
      key=f'lojas_multiselect_{tab_index}'
    )
  with col2:
    data_inicio = st.date_input(
      'Data de Início', 
      value=data_inicio_default, 
      key=f'data_inicio_input_{tab_index}', 
      format="DD/MM/YYYY"
    )
  with col3:
    data_fim = st.date_input(
      'Data de Fim', 
      value=data_fim_default, 
      key=f'data_fim_input_{tab_index}', 
      format="DD/MM/YYYY"
    )

  return lojas_selecionadas, data_inicio, data_fim



def main ():
  config_sidebar()

  dfNomeEstoque = pd.DataFrame(GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE())
  dfNomeCompras = pd.DataFrame(GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA())
  dfNomeCompras2 = dfNomeCompras.copy()
  dfNomeEstoque2 = dfNomeEstoque.copy()
  dfNomeCompras3 = dfNomeCompras.copy()
  dfNomeEstoque3 = dfNomeEstoque.copy()



  tab1, tab2, tab3, tab4 = st.tabs(["ALIMENTOS", "BEBIDAS", " PRODUTOS DE LIMP/HIGIENE", "COMPARATIVO ENTRE LOJAS"])
  with tab1:
    lojas_selecionadas, data_inicio, data_fim = preparar_filtros(1)
    dfNomeEstoque = config_compras_quantias(dfNomeEstoque, data_inicio, data_fim, lojas_selecionadas)
    dfNomeCompras = config_compras_quantias(dfNomeCompras, data_inicio, data_fim, lojas_selecionadas)

    dfNomeEstoque = dfNomeEstoque[dfNomeEstoque['Categoria'] == 'ALIMENTOS']
    Alim_por_valor = config_por_categ_avaliada(dfNomeEstoque.copy(), 'Valor')
    Alim_valor_unit_ajust = config_por_categ_avaliada(dfNomeEstoque.copy(), 'Valor Unit. Ajustado')
    Alim_valor_unitario = config_por_categ_avaliada(dfNomeCompras.copy(), 'Valor Unitário')

    st.dataframe(dfNomeEstoque)
    st.dataframe(dfNomeCompras)

    with st.container(border=True):
      st.subheader('Diagrama de Pareto sobre Alimentos em relação ao valor total')
      diagrama_pareto_por_categ_avaliada(Alim_por_valor, 'Valor', key='alim_valor')
    with st.container(border=True):    
      st.subheader('Diagrama de Pareto sobre Alimentos em relação ao valor Unitário de cada')
      diagrama_pareto_por_categ_avaliada(Alim_valor_unitario, 'Valor Unitário', key='alim_valor_unitario')
    with st.container(border=True):
      st.subheader('Diagrama de Pareto sobre Alimentos em relação ao valor unitário ajustado')
      diagrama_pareto_por_categ_avaliada(Alim_valor_unit_ajust, 'Valor Unit. Ajustado', key='alim_valor_unit_ajust')

  with tab2:
    lojas_selecionadas, data_inicio, data_fim = preparar_filtros(2)
    dfNomeEstoque2 = config_compras_quantias(dfNomeEstoque2, data_inicio, data_fim, lojas_selecionadas)
    dfNomeCompras2 = config_compras_quantias(dfNomeCompras2, data_inicio, data_fim, lojas_selecionadas)

    dfNomeEstoque2 = dfNomeEstoque2[dfNomeEstoque2['Categoria'] == 'BEBIDAS']
    Beb_por_valor = config_por_categ_avaliada(dfNomeEstoque2.copy(), 'Valor')
    Beb_valor_unit_ajust = config_por_categ_avaliada(dfNomeEstoque2.copy(), 'Valor Unit. Ajustado')
    Beb_valor_unitario = config_por_categ_avaliada(dfNomeCompras2.copy(), 'Valor Unitário')

    st.dataframe(dfNomeEstoque2)
    st.dataframe(dfNomeCompras2)

    with st.container(border=True):
      st.subheader('Diagrama de Pareto sobre Bebidas em relação ao valor total')
      diagrama_pareto_por_categ_avaliada(Beb_por_valor, 'Valor', key='beb_valor')
    with st.container(border=True):    
      st.subheader('Diagrama de Pareto sobre Bebidas em relação ao valor Unitário de cada')
      diagrama_pareto_por_categ_avaliada(Beb_valor_unitario, 'Valor Unitário', key='beb_valor_unitario')
    with st.container(border=True):
      st.subheader('Diagrama de Pareto sobre Bebidas em relação ao valor unitário ajustado')
      diagrama_pareto_por_categ_avaliada(Beb_valor_unit_ajust, 'Valor Unit. Ajustado', key='beb_valor_unit_ajust')

  with tab3:
    lojas_selecionadas, data_inicio, data_fim = preparar_filtros(3)
    dfNomeEstoque3 = config_compras_quantias(dfNomeEstoque3, data_inicio, data_fim, lojas_selecionadas)
    dfNomeCompras3 = config_compras_quantias(dfNomeCompras3, data_inicio, data_fim, lojas_selecionadas)

    dfNomeEstoque3 = dfNomeEstoque3[dfNomeEstoque3['Categoria'] == 'DESCARTAVEIS/HIGIENE E LIMPEZA']
    Limp_por_valor = config_por_categ_avaliada(dfNomeEstoque3.copy(), 'Valor')
    Limp_valor_unit_ajust = config_por_categ_avaliada(dfNomeEstoque3.copy(), 'Valor Unit. Ajustado')
    Limp_valor_unitario = config_por_categ_avaliada(dfNomeCompras3.copy(), 'Valor Unitário')

    st.dataframe(dfNomeEstoque3)
    st.dataframe(dfNomeCompras3)

    with st.container(border=True):
        st.subheader('Diagrama de Pareto sobre Produtos de Limpeza e Higiene em relação ao valor total')
        diagrama_pareto_por_categ_avaliada(Limp_por_valor, 'Valor', key='limp_valor')
    with st.container(border=True):    
        st.subheader('Diagrama de Pareto sobre Produtos de Limpeza e Higiene em relação ao valor Unitário de cada')
        diagrama_pareto_por_categ_avaliada(Limp_valor_unitario, 'Valor Unitário', key='limp_valor_unitario')
    with st.container(border=True):
        st.subheader('Diagrama de Pareto sobre Produtos de Limpeza e Higiene em relação ao valor unitário ajustado')
        diagrama_pareto_por_categ_avaliada(Limp_valor_unit_ajust, 'Valor Unit. Ajustado', key='limp_valor_unit_ajust')




if __name__ == '__main__':
  main()

