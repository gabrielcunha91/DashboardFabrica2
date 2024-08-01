import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.dados_gerais import *
from utils.functions.previsao_faturamento import *
from workalendar.america import Brazil

st.set_page_config(
    page_title="Previsao_faturamento",
    page_icon="💰",
    layout="wide"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
    st.switch_page('Login.py')


st.title('PREVISÃO DE FATURAMENTO')
config_sidebar()
st.divider()

dfCompensacoes = GET_COMPENSACOES_ZIG_AGRUPADAS()
dfCompensacoes['Data_Compensacao'] = pd.to_datetime(dfCompensacoes['Data_Compensacao'])
df_parciais = criar_parciais(dfCompensacoes)
df_parciais = df_parciais.loc[:,~df_parciais.columns.duplicated()]
df_unificado = unificar_parciais(df_parciais)

# Defina o intervalo de datas
hoje = datetime.now()
end_date = hoje + timedelta(days=7)
start_date = hoje - timedelta(days=7)

# Filtre os dados com base no intervalo de datas
filtered_df = df_unificado[(df_unificado['Data_Parcial'] >= start_date) & (df_unificado['Data_Parcial'] <= end_date)]
grouped_df = filtered_df.groupby(['Data_Parcial', 'Empresa'], as_index=False).agg({'Valor_Parcial': 'sum'})
sorted_df = grouped_df.sort_values(by=['Data_Parcial', 'Empresa'])

lojasComDados = preparar_dados_lojas_user()
lojasSelecionadas = st.multiselect(label='Selecione Lojas', options=lojasComDados, key='lojas_multiselect')
st.divider()

sorted_df = filtrar_por_classe_selecionada(sorted_df, 'Empresa', lojasSelecionadas)
sorted_df = format_date_brazilian(sorted_df, 'Data_Parcial')
sorted_df = format_columns_brazilian(sorted_df, ['Valor_Parcial'])
sorted_df.rename(columns = {'Empresa': 'Loja', 'Data_Parcial': 'Data', 'Valor_Parcial': 'Valor Projetado'}, inplace=True)


with st.container(border=True):
  col, col1, col2 = st.columns([1, 8, 1])
  with col1:
    st.subheader('Previsão:')
  col, col1, col2 = st.columns([3, 8, 3])
  with col1:
    st.dataframe(sorted_df, width=700, hide_index=True)
