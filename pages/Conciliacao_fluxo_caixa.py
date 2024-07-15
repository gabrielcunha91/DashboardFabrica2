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
lojas = df_lojas["Loja"].unique()
loja = st.selectbox("Loja", lojas)

# Defina um dicionário para mapear nomes de lojas a IDs de lojas
mapeamento_lojas = dict(zip(df_lojas["Loja"], df_lojas["ID_Loja"]))

# Obtenha o ID da loja selecionada
id_loja = mapeamento_lojas[loja]
st.write('ID da loja selecionada:', id_loja)

st.divider()
st.subheader("Faturamento Zig")

serie_datas_feriados = config_feriados()
df_faturam_zig = config_faturam_zig_fluxo_caixa(serie_datas_feriados)
df_faturam_zig_loja = df_faturam_zig[df_faturam_zig['ID_Loja'] == id_loja]
st.dataframe(df_faturam_zig_loja, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Receitas Extraordinárias")

df_receitas_extraord = config_receitas_extraord_fluxo_caixa()
df_receitas_extraord_loja = df_receitas_extraord[df_receitas_extraord['ID_Loja'] == id_loja]
st.dataframe(df_receitas_extraord_loja, use_container_width=True, hide_index=True)

st.divider()
st.subheader("View Parcelamentos Agrupados - Receitas Extraord")

df_view_parc_agrup = config_view_parc_agrup()
df_view_parc_loja = df_view_parc_agrup[df_view_parc_agrup['ID_Loja'] == id_loja]
st.dataframe(df_view_parc_loja, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Custos BlueMe Sem Parcelamento")

df_custos_blueme_sem_parcelamento = config_custos_blueme_sem_parcelamento()
df_custos_blueme_sem_parcelamento_loja = df_custos_blueme_sem_parcelamento[df_custos_blueme_sem_parcelamento['ID_Loja'] == id_loja]
st.dataframe(df_custos_blueme_sem_parcelamento_loja, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Custos BlueMe Com Parcelamento")

df_custos_blueme_com_parcelamento = config_custos_blueme_com_parcelamento()
df_custos_blueme_com_parcelamento_loja = df_custos_blueme_com_parcelamento[df_custos_blueme_com_parcelamento['ID_Loja'] == id_loja]
st.dataframe(df_custos_blueme_com_parcelamento_loja, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Extratos Bancários")

df_extratos = config_extratos()
df_extratos_loja = df_extratos[df_extratos['ID_Loja'] == id_loja]
st.dataframe(df_extratos_loja, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Mutuos")

df_mutuos = config_mutuos()
df_mutuos_loja = df_mutuos[((df_mutuos['ID_Loja_Saida'] == id_loja) | (df_mutuos['ID_Loja_Entrada'] == id_loja))]
st.dataframe(df_mutuos_loja, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Tesouraria - Transações")

df_tesouraria_trans = config_tesouraria_trans()
df_tesouraria_trans_loja = df_tesouraria_trans[df_tesouraria_trans['ID_Loja'] == id_loja]
st.dataframe(df_tesouraria_trans_loja, use_container_width=True, hide_index=True)

st.divider()

