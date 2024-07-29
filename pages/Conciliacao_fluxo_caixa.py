import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.dados_gerais import *
from utils.functions.fluxo_de_caixa import *

st.set_page_config(
    page_title="Conciliacao",
    page_icon="📃",
    layout="wide"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
    st.switch_page('Login.py')

config_sidebar()

df_lojas = GET_LOJAS()
lojas = preparar_dados_lojas_user()
# lojas = df_lojas["Loja"].unique()
loja = st.selectbox("Loja", lojas)

# Defina um dicionário para mapear nomes de lojas a IDs de lojas
mapeamento_lojas = dict(zip(df_lojas["Loja"], df_lojas["ID_Loja"]))

# Obtenha o ID da loja selecionada
id_loja = mapeamento_lojas[loja]
st.write('ID da loja selecionada:', id_loja)

excel_filename = 'Conciliacao_FB.xlsx'

st.divider()
st.subheader("Faturamento Zig")

serie_datas_feriados = config_feriados()
df_faturam_zig = config_faturam_zig_fluxo_caixa(serie_datas_feriados)
df_faturam_zig_loja = df_faturam_zig[df_faturam_zig['ID_Loja'] == id_loja]
st.dataframe(df_faturam_zig_loja, use_container_width=True, hide_index=True)
if st.button('Atualizar Faturam Zig'):
  sheet_name_zig = 'df_faturam_zig'
  export_to_excel(df_faturam_zig_loja, sheet_name_zig, excel_filename)
  st.success('Arquivo atualizado com sucesso!')

st.divider()
st.subheader("Receitas Extraordinárias")

df_receitas_extraord = config_receitas_extraord_fluxo_caixa()
df_receitas_extraord_loja = df_receitas_extraord[df_receitas_extraord['ID_Loja'] == id_loja]
st.dataframe(df_receitas_extraord_loja, use_container_width=True, hide_index=True)
if st.button('Atualizar Receitas Extraord'):
  sheet_name_receitas_extraord = 'df_receitas_extraord'
  export_to_excel(df_receitas_extraord_loja, sheet_name_receitas_extraord, excel_filename)
  st.success('Arquivo atualizado com sucesso!')

st.divider()
st.subheader("View Parcelamentos Agrupados - Receitas Extraord")

df_view_parc_agrup = config_view_parc_agrup()
df_view_parc_loja = df_view_parc_agrup[df_view_parc_agrup['ID_Loja'] == id_loja]
st.dataframe(df_view_parc_loja, use_container_width=True, hide_index=True)
if st.button('Atualizar View Parcelamentos Receitas Extraord'):
  sheet_name_view_parc_agrup = 'view_parc_agrup'
  export_to_excel(df_view_parc_loja, sheet_name_view_parc_agrup, excel_filename)
  st.success('Arquivo atualizado com sucesso!')

st.divider()
st.subheader("Custos BlueMe Sem Parcelamento")

df_custos_blueme_sem_parcelamento = config_custos_blueme_sem_parcelamento()
df_custos_blueme_sem_parcelamento_loja = df_custos_blueme_sem_parcelamento[df_custos_blueme_sem_parcelamento['ID_Loja'] == id_loja]
st.dataframe(df_custos_blueme_sem_parcelamento_loja, use_container_width=True, hide_index=True)
if st.button('Atualizar Custos BlueMe Sem Parcelamento'):
  sheet_name_custos_blueme_sem_parcelamento = 'df_blueme_sem_parcelamento'
  export_to_excel(df_custos_blueme_sem_parcelamento_loja, sheet_name_custos_blueme_sem_parcelamento, excel_filename)
  st.success('Arquivo atualizado com sucesso!')

st.divider()
st.subheader("Custos BlueMe Com Parcelamento")

df_custos_blueme_com_parcelamento = config_custos_blueme_com_parcelamento()
df_custos_blueme_com_parcelamento_loja = df_custos_blueme_com_parcelamento[df_custos_blueme_com_parcelamento['ID_Loja'] == id_loja]
st.dataframe(df_custos_blueme_com_parcelamento_loja, use_container_width=True, hide_index=True)
if st.button('Atualizar Custos BlueMe Com Parcelamento'):
  sheet_name_custos_blueme_com_parcelamento = 'df_blueme_com_parcelamento'
  export_to_excel(df_custos_blueme_com_parcelamento_loja, sheet_name_custos_blueme_com_parcelamento, excel_filename)
  st.success('Arquivo atualizado com sucesso!')

st.divider()
st.subheader("Extratos Bancários")

df_extratos = config_extratos()
df_extratos_loja = df_extratos[df_extratos['ID_Loja'] == id_loja]
st.dataframe(df_extratos_loja, use_container_width=True, hide_index=True)
if st.button('Atualizar Extratos'):
  sheet_name_extratos = 'df_extratos'
  export_to_excel(df_extratos_loja, sheet_name_extratos, excel_filename)
  st.success('Arquivo atualizado com sucesso!')

st.divider()
st.subheader("Mutuos")

df_mutuos = config_mutuos()
df_mutuos_loja = df_mutuos[((df_mutuos['ID_Loja_Saida'] == id_loja) | (df_mutuos['ID_Loja_Entrada'] == id_loja))]
st.dataframe(df_mutuos_loja, use_container_width=True, hide_index=True)
if st.button('Atualizar Mutuos'):
  df_mutuos_loja['Valor_Entrada'] = df_mutuos_loja.apply(lambda row: row['Valor'] if row['ID_Loja_Entrada'] == id_loja else 0, axis=1)
  df_mutuos_loja['Valor_Saida'] = df_mutuos_loja.apply(lambda row: row['Valor'] if row['ID_Loja_Saida'] == id_loja else 0, axis=1)
  df_mutuos_loja = df_mutuos_loja.drop('Valor', axis=1)
  sheet_name_mutuos = 'df_mutuos'
  export_to_excel(df_mutuos_loja, sheet_name_mutuos, excel_filename)
  st.success('Arquivo atualizado com sucesso!')

st.divider()
st.subheader("Tesouraria - Transações")

df_tesouraria_trans = config_tesouraria_trans()
df_tesouraria_trans_loja = df_tesouraria_trans[df_tesouraria_trans['ID_Loja'] == id_loja]
st.dataframe(df_tesouraria_trans_loja, use_container_width=True, hide_index=True)
if st.button('Atualizar Tesouraria Transações'):
  sheet_name_tesouraria = 'df_tesouraria_trans'
  export_to_excel(df_tesouraria_trans_loja, sheet_name_tesouraria, excel_filename)
  st.success('Arquivo atualizado com sucesso!')

st.divider()


if st.button('Baixar Excel'):
  if os.path.exists(excel_filename):
    with open(excel_filename, "rb") as file:
      file_content = file.read()
    st.download_button(
      label="Clique para baixar o arquivo Excel",
      data=file_content,
      file_name="Conciliacao_FB.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

