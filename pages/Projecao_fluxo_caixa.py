import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.dados_gerais import *
from utils.functions.fluxo_de_caixa import *
from workalendar.america import Brazil
from utils.user import logout

st.set_page_config(
    page_title="Fluxo_Caixa",
    page_icon="💰",
    layout="wide"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
    st.switch_page('Login.py')

col, col2, col3 = st.columns([6, 1, 1])
with col:
  st.title('PROJEÇÃO - Fluxo de Caixa')
with col2:
  st.button(label="Atualizar", on_click = st.cache_data.clear)
with col3:
  if st.button("Logout"):
    logout()

config_sidebar()


bares = preparar_dados_lojas_user_projecao_fluxo()
# bares = df_projecao_bares["Empresa"].unique()

with st.container(border=True):
  col1, col2, col3 = st.columns([3, 1, 1])
  with col1:
    bar = st.multiselect("Bares", bares)
  with col2:
    data_fim = st.date_input("Data de Fim", value=datetime.today()+timedelta(days=7), key='data_fim_input', format="DD/MM/YYYY", min_value=datetime.today()+timedelta(days=1), max_value=datetime.today()+timedelta(days=12))
  with col3:
    multiplicador = st.number_input("Selecione um multiplicador", value=1.0, key='multiplicador_input')
  df_projecao_bares = config_projecao_bares(multiplicador, data_fim)
  df_projecao_bar = df_projecao_bares[df_projecao_bares["Empresa"].isin(bar)]
  df_projecao_bar["Data"] = pd.to_datetime(df_projecao_bar["Data"], dayfirst=True)
  df_projecao_bar = df_projecao_bar.sort_values(by=["Empresa", "Data"])
  df_projecao_bar_com_soma = somar_total(df_projecao_bar)
  columns_projecao_bar_com_soma = ['Data', 'Empresa', 'Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord',
                                 'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas', 'Saldo_Final']
  df_projecao_bar_com_soma = df_projecao_bar_com_soma[columns_projecao_bar_com_soma]
  df_projecao_bar_com_soma = format_columns_brazilian(df_projecao_bar_com_soma, ['Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord',
                                 'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas', 'Saldo_Final'])
  st.dataframe(df_projecao_bar_com_soma, use_container_width=True, hide_index=True)

st.divider()


# Projeção Agrupada
with st.container(border=True):
  col1, col2, col3 = st.columns([3, 1, 1])
  with col1:
    st.subheader('Projeção de bares agrupados:' )
  with col2:
    data_fim2 = st.date_input("Data de Fim", value=datetime.today()+timedelta(days=7), key='data_fim_input2', format="DD/MM/YYYY", min_value=datetime.today()+timedelta(days=1), max_value=datetime.today()+timedelta(days=12))
  with col3:
    multiplicador2 = st.number_input("Selecione um multiplicador", value=1.0, key='multiplicador_input2')
  st.markdown(
    """*Bar Brahma, Bar Léo, Bar Brasilia, Edificio Rolim, Hotel Maraba, 
    Jacaré, Orfeu, Riviera, Tempus, Escritorio Fabrica de Bares, Priceless, Bar Brahma - Granja, Edificio Rolim, Girondino - CCBB, Girondino, Brahma Ribeirao*
    """
  )

  df_projecao_grouped = config_projecao_bares(multiplicador2, data_fim2)
  df_projecao_grouped = config_grouped_projecao(df_projecao_grouped)
  df_projecao_grouped_com_soma = somar_total(df_projecao_grouped)

  columns_projecao_grouped = ['Data', 'Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord',
                            'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas', 'Saldo_Final']
  df_projecao_grouped_com_soma = df_projecao_grouped_com_soma[columns_projecao_grouped]
  df_projecao_grouped_com_soma = format_columns_brazilian(df_projecao_grouped_com_soma, ['Saldo_Inicio_Dia', 'Valor_Liquido_Recebido', 'Valor_Projetado_Zig', 'Receita_Projetada_Extraord',
                            'Despesas_Aprovadas_Pendentes', 'Despesas_Pagas', 'Saldo_Final'])

  st.dataframe(df_projecao_grouped_com_soma, use_container_width=True, hide_index=True)

st.divider()

with st.container(border=True):
  st.subheader('Despesas do dia')
  lojasComDados = preparar_dados_lojas_user_projecao_fluxo()
  col1, col2, col3, col4 = st.columns([5, 3, 4, 4])
  # Adiciona seletores
  with col1:
    lojasSelecionadas = st.multiselect(label='Selecione Lojas', options=lojasComDados, key='lojas_multiselect')
  with col2:
    checkbox = st.checkbox(label='Adicionar lojas agrupadas', key='checkbox_lojas_despesas')
    if checkbox:
      lojasAgrupadas = [
        'Bar Brahma - Centro', 'Bar Léo - Centro', 'Bar Brasilia -  Aeroporto ', 'Bar Brasilia -  Aeroporto', 'Delivery Bar Leo Centro', 
        'Delivery Fabrica de Bares', 'Delivery Orfeu', 'Edificio Rolim', 'Hotel Maraba', 'Jacaré', 'Orfeu', 'Riviera Bar', 'Tempus', 
        'Escritório Fabrica de Bares', 'Priceless', 'Bar Brahma - Granja', 'Edificio Rolim', 'Girondino - CCBB', 'Girondino ', 'Brahma - Ribeirão'
      ]
      lojasSelecionadas.extend(lojasAgrupadas)
    checkbox2 = st.checkbox(label='Apenas Pendentes', key='checkbox_despesas_pendentes')
    checkbox3 = st.checkbox(label='Apenas Pagas', key='checkbox_despesas_pagas')
  with col3:
    dataSelecionada = st.date_input('Data de Início (da Previsão de pagamento)', value=datetime.today(), key='data_inicio_input', format="DD/MM/YYYY")
  with col4:
    dataSelecionada2 = st.date_input('Data de Fim (da Previsão de pagamento)', value=datetime.today(), key='data_fim_input3', format="DD/MM/YYYY")

  dataSelecionada = pd.to_datetime(dataSelecionada)
  dataSelecionada2 = pd.to_datetime(dataSelecionada2)
  df = config_despesas_a_pagar(lojasSelecionadas, dataSelecionada, dataSelecionada2)
  if checkbox2:
    df = filtrar_por_classe_selecionada(df, 'Status_Pgto', ['Pendente'])
  if checkbox3:
    df = filtrar_por_classe_selecionada(df, 'Status_Pgto', ['Pago'])
  valorTotal = df['Valor'].sum()
  valorTotal = format_brazilian(valorTotal)
  df = format_columns_brazilian(df, ['Valor'])
  st.dataframe(df, use_container_width=True, hide_index=True)
  st.write('Valor total das despesas selecionadas = R$', valorTotal)



with st.container(border=True):
  st.subheader('Receitas extraordinárias do dia')
  lojasComDados = preparar_dados_lojas_user_projecao_fluxo()
  col1, col2, col3 = st.columns([5, 2, 3])
  with col1:
    lojasSelecionadas2 = st.multiselect(label='Selecione Lojas', options=lojasComDados, key='lojas_multiselect2')
  with col2:
    checkboxLojas = st.checkbox(label='Adicionar lojas agrupadas', key='checkbox_lojas_extraord')
    if checkboxLojas:
      lojasAgrupadas = [
            'Bar Brahma - Centro', 'Bar Léo - Centro', 'Bar Brasilia - Aeroporto',
            'Bar Brasilia - Aeroporto', 'Delivery Bar Leo Centro', 'Delivery Fabrica de Bares',
            'Delivery Orfeu', 'Edificio Rolim', 'Hotel Maraba', 'Jacaré', 'Orfeu', 'Riviera Bar', 'Tempus', 
            'Escritório Fabrica de Bares', 'Priceless', 'Bar Brahma - Granja', 'Edificio Rolim', 'Girondino - CCBB', 'Girondino '
      ]
      lojasSelecionadas2.extend(lojasAgrupadas)
  with col3:
    dataSelecionada2 = st.date_input('Selecione uma Data', value=datetime.today(), key='data_inicio_input2', format="DD/MM/YYYY")

  dataSelecionada2 = pd.to_datetime(dataSelecionada2)
  df = GET_RECEITAS_EXTRAORD_DO_DIA(dataSelecionada2)
  df = filtrar_por_classe_selecionada(df, 'Empresa', lojasSelecionadas2)
  df = filtrar_por_datas(df, dataSelecionada2, dataSelecionada2, 'Data_Vencimento_Parcela')
  valorTotal = df['Valor_Parcela'].sum()
  valorTotal = format_brazilian(valorTotal)
  df = format_columns_brazilian(df, ['Valor_Parcela'])
  st.dataframe(df, use_container_width=True, hide_index=True)
  st.write('Valor total das receitas extraordinárias selecionadas = R$', valorTotal)