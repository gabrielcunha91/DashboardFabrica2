import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts


def criar_seletores(LojasComDados, data_inicio_default, data_fim_default):
  col1, col2, col3 = st.columns([2, 1, 1])

  # Adiciona seletores
  with col1:
    lojas_selecionadas = st.multiselect(label='Selecione Lojas', options=LojasComDados, key='lojas_multiselect')
  with col2:
    data_inicio = st.date_input('Data de Início', value=data_inicio_default, key='data_inicio_input', format="DD/MM/YYYY")
  with col3:
    data_fim = st.date_input('Data de Fim', value=data_fim_default, key='data_fim_input', format="DD/MM/YYYY")

  # Converte as datas selecionadas para o formato Timestamp
  data_inicio = pd.to_datetime(data_inicio)
  data_fim = pd.to_datetime(data_fim)
  return lojas_selecionadas, data_inicio, data_fim


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


def Grafico_Donut(df): 
  # Extrair dados do DataFrame
  data = []
  for index, row in df.iterrows():
    if row['Categoria'] != 'Total Geral':  # Ignorar a linha de 'Total Geral'
      data.append({"value": row['Valor Líquido'], "name": row['Categoria']})

  # Configurar opções do gráfico
  options = {
    "tooltip": {"trigger": "item"},
    "legend": {"orient": "vertical", "left": "5%", "top": "middle"},
    "series": [
      {
      "name": "Valor Líquido por Categoria",
      "type": "pie",
      "radius": ["40%", "70%"],
      "avoidLabelOverlap": False,
      "itemStyle": {
        "borderRadius": 10,
        "borderColor": "#fff",
        "borderWidth": 2,
      },
      "label": {"show": False, "position": "center"},
      "emphasis": {
          "label": {"show": True, "fontSize": "20", "fontWeight": "bold"}
      },
      "labelLine": {"show": False},
      "data": data,
      }
    ],
  }
  # Renderizar o gráfico
  st_echarts(
    options=options, height="300px", width="550px"
  )


def faturam_por_dia(df):
  df['Data da Venda'] = df['Data da Venda'].astype(str)

  # Preparar os dados para o gráfico de área empilhada
  df = df.groupby(['Data da Venda', 'Categoria'])['Valor Líquido Venda'].sum().reset_index()
  df['Valor Líquido Venda'] = df['Valor Líquido Venda'].astype(float)
  df = df.pivot(index='Data da Venda', columns='Categoria', values='Valor Líquido Venda').fillna(0)

  # Calcular o valor total diário
  df['Total'] = df.sum(axis=1)
  df.round({'Total': 2})
  df = df.reset_index()

  # Extrair datas e categorias
  datas = df['Data da Venda'].tolist()
  categorias = df.columns[1:-1].tolist()

  # Preparar séries de dados
  series = []
  for categoria in categorias:
    series.append({
      "name": categoria,
      "type": "line",
      "stack": "Total",
      "areaStyle": {},
      "emphasis": {"focus": "series"},
      "data": df[categoria].tolist(),
    })
  
  # Configurações do gráfico
  options = {
    "title": {"text": "  "},
    "tooltip": {
      "trigger": "axis",
      "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
    },
    "legend": {"data": categorias},
    "toolbox": {"feature": {"saveAsImage": {}}},
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "xAxis": [
      {
        "type": "category",
        "boundaryGap": False,
        "data": datas,
      }
    ],
    "yAxis": [{"type": "value"}],
    "series": series,
  }
    
  # Renderizar o gráfico no Streamlit
  st_echarts(options=options, height="400px")


def plotar_grafico(df):
  df['Valor Total'] = df['Valor Total'].astype(float)
  df['Quantidade de Eventos'] = df['Quantidade de Eventos'].astype(float)
  df['Data Evento'] = df['Data Evento'].astype(str)

  data = df.to_dict(orient='records')
  option = {
    'xAxis': {'type': 'category', 'data': [d['Data Evento'] for d in data]},
    'yAxis': [{'type': 'value', 'name': 'Valor Total'},
              {'type': 'value', 'name': 'Quantidade de Eventos'}],
    'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'cross'}},
    'series': [
      {'name': 'Valor Total', 'type': 'line', 'data': [d['Valor Total'] for d in data]},
      {'name': 'Quantidade de Eventos', 'type': 'line', 'yAxisIndex': 1, 'data': [d['Quantidade de Eventos'] for d in data]}
    ]
  }
  st_echarts(options=option)



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

