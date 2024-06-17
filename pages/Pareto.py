import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from utils.functions import *


if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')

def main ():
  config_sidebar()
  # Dados de exemplo
  data = {
    'Categoria': ['A', 'B', 'C', 'D', 'E'],
    'Frequencia': [50, 30, 15, 4, 1]
  }

  df = pd.DataFrame(data)
  df = df.sort_values(by='Frequencia', ascending=False)
  df['Porcentagem Acumulada'] = df['Frequencia'].cumsum() / df['Frequencia'].sum() * 100

  # Configuração do gráfico
  options = {
    "title": {
      "text": "Diagrama de Pareto",
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
        "data": df['Categoria'].tolist()
      }
    ],
    "yAxis": [
      {
        "type": "value",
        "name": "Frequencia"
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
        "name": "Frequencia",
        "type": "bar",
        "data": df['Frequencia'].tolist()
      },
      {
        "name": "Porcentagem Acumulada",
        "type": "line",
        "yAxisIndex": 1,
        "data": df['Porcentagem Acumulada'].tolist()
      }
    ]
  }

  # Renderizar o gráfico no Streamlit
  st.title('Diagrama de Pareto com Streamlit ECharts')
  st_echarts(options=options)


if __name__ == '__main__':
  main()

