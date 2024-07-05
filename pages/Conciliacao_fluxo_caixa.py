import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions_fluxo_caixa import *
from utils.functions import config_sidebar
from workalendar.america import Brazil


st.set_page_config(
    page_title="Conciliacao",
    page_icon="📃",
    layout="wide"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')

config_sidebar()

taxa_credito_antecipado = 0.0265
taxa_credito_padrao = 0.016
taxa_debito = 0.0095
taxa_app = 0.0074
taxa_pix = 0.0074

df_lojas = GET_LOJAS()

lojas = df_lojas["Loja"].unique()
loja = st.selectbox("Loja", lojas)

# Defina um dicionário para mapear nomes de lojas a IDs de lojas
mapeamento_lojas = dict(zip(df_lojas["Loja"], df_lojas["ID_Loja"]))

# Obtenha o ID da loja selecionada
id_loja = mapeamento_lojas[loja]

st.write(id_loja)


st.divider()
st.markdown("Faturamento Zig")

serie_datas_feriados = config_feriados()

df_faturam_zig = config_faturam_zig_fluxo_caixa(serie_datas_feriados)
df_faturam_zig_loja = df_faturam_zig[df_faturam_zig['ID_Loja'] == id_loja]
df_faturam_zig_loja

st.divider()
st.markdown("Receitas Extraordinárias")

df_receitas_extraord = config_receitas_extraord_fluxo_caixa()
df_receitas_extraord_loja = df_receitas_extraord[df_receitas_extraord['ID_Loja'] == id_loja]
df_receitas_extraord_loja

st.divider()
st.markdown("View Parcelamentos Agrupados - Receitas Extraord")

df_view_parc_agrup = config_view_parc_agrup()
df_view_parc_loja = df_view_parc_agrup[df_view_parc_agrup['ID_Loja'] == id_loja]
df_view_parc_loja

st.divider()
st.markdown("Custos BlueMe Sem Parcelamento")

df_custos_blueme_sem_parcelamento = config_custos_blueme_sem_parcelamento()
df_custos_blueme_sem_parcelamento_loja = df_custos_blueme_sem_parcelamento[df_custos_blueme_sem_parcelamento['ID_Loja'] == id_loja]
df_custos_blueme_sem_parcelamento_loja


st.divider()
st.markdown("Custos BlueMe Com Parcelamento")

df_custos_blueme_com_parcelamento = config_custos_blueme_com_parcelamento()
df_custos_blueme_com_parcelamento_loja = df_custos_blueme_com_parcelamento[df_custos_blueme_com_parcelamento['ID_Loja'] == id_loja]
df_custos_blueme_com_parcelamento_loja

st.divider()
st.markdown("Extratos Bancários")

df_extratos = config_extratos()
df_extratos_loja = df_extratos[df_extratos['ID_Loja'] == id_loja]
df_extratos_loja


st.divider()
st.markdown("Mutuos")

df_mutuos = config_mutuos()
df_mutuos_loja = df_mutuos[((df_mutuos['ID_Loja_Saida'] == id_loja) | (df_mutuos['ID_Loja_Entrada'] == id_loja))]
df_mutuos_loja

st.divider()
st.markdown("Tesouraria - Transações")

df_tesouraria_trans = config_tesouraria_trans()
df_tesouraria_trans_loja = df_tesouraria_trans[df_tesouraria_trans['ID_Loja'] == id_loja]
df_tesouraria_trans_loja

st.divider()


