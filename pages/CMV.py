import streamlit as st
import pandas as pd
from babel.dates import format_date
from utils.queries import *
from utils.functions.cmv import *
from utils.functions.dados_gerais import *
from utils.components import *
from utils.user import logout

st.set_page_config(
  layout = 'wide',
  page_title = 'CMV',
  page_icon=':⚖',
  initial_sidebar_state="collapsed"
)  
pd.set_option('future.no_silent_downcasting', True)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')


config_sidebar()
col, col2, col3 = st.columns([6, 1, 1])
with col:
  st.title('CMV')
with col2:
  st.button(label="Atualizar", on_click = st.cache_data.clear)
with col3:
  if st.button("Logout"):
    logout()

st.divider()

lojasComDados = preparar_dados_lojas_user()

if 'Abaru - Priceless' in lojasComDados and 'Notiê - Priceless' in lojasComDados:
  lojasComDados.remove('Abaru - Priceless')
  lojasComDados.remove('Notiê - Priceless')
if 'Blue Note - São Paulo' in lojasComDados and 'Blue Note SP (Novo)' in lojasComDados:
  lojasComDados.remove('Blue Note - São Paulo')
  lojasComDados.remove('Blue Note SP (Novo)')
  lojasComDados.append('Blue Note - Agregado')
if 'Girondino - CCBB' in lojasComDados and 'Girondino ' in lojasComDados:
  lojasComDados.remove('Girondino - CCBB')
  lojasComDados.remove('Girondino ')
  lojasComDados.append('Girondino - Agregado')

lojasComDados.sort()

data_inicio_default, data_fim_default = preparar_datas_ultimo_mes()
lojas_selecionadas, data_inicio, data_fim = criar_seletores_cmv(lojasComDados, data_inicio_default, data_fim_default)
st.divider()

data_inicio_mes_anterior = (data_inicio.replace(day=1) - timedelta(days=1)).replace(day=1)
data_fim_mes_anterior = data_inicio.replace(day=1) - timedelta(days=1)

df_faturamento_delivery, df_faturamento_zig, faturamento_bruto_alimentos, faturamento_bruto_bebidas, faturamento_alimentos_delivery, faturamento_bebidas_delivery = config_faturamento_bruto_zig(data_inicio, data_fim, lojas_selecionadas)
df_faturamento_eventos, faturamento_alimentos_eventos, faturamento_bebidas_eventos = config_faturamento_eventos(data_inicio, data_fim, lojas_selecionadas, faturamento_bruto_alimentos, faturamento_bruto_bebidas)
df_compras, compras_alimentos, compras_bebidas = config_compras(data_inicio, data_fim, lojas_selecionadas)
df_valoracao_estoque_atual = config_valoracao_estoque(data_inicio, data_fim, lojas_selecionadas)
df_valoracao_estoque_mes_anterior = config_valoracao_estoque(data_inicio_mes_anterior, data_fim_mes_anterior, lojas_selecionadas)
df_diferenca_estoque = config_diferenca_estoque(df_valoracao_estoque_atual, df_valoracao_estoque_mes_anterior)
df_variacao_estoque, variacao_estoque_alimentos, variacao_estoque_bebidas = config_variacao_estoque(df_valoracao_estoque_atual, df_valoracao_estoque_mes_anterior)
df_insumos_sem_pedido = config_insumos_blueme_sem_pedido(data_inicio, data_fim, lojas_selecionadas)
df_insumos_com_pedido = config_insumos_blueme_com_pedido(data_inicio, data_fim, lojas_selecionadas)
df_transf_e_gastos, saida_alimentos, saida_bebidas, entrada_alimentos, entrada_bebidas, consumo_interno, quebras_e_perdas = config_transferencias_gastos(data_inicio, data_fim, lojas_selecionadas)
df_transf_entradas, df_transf_saidas = config_transferencias_detalhadas(data_inicio, data_fim, lojas_selecionadas)
df_producao_alimentos, df_producao_bebidas, valor_producao_alimentos, valor_producao_bebidas = config_valoracao_producao(data_inicio, lojas_selecionadas)
df_producao_alimentos_mes_anterior, df_producao_bebidas_mes_anterior, valor_producao_alimentos_mes_anterior, valor_producao_bebidas_mes_anterior = config_valoracao_producao(data_inicio_mes_anterior, lojas_selecionadas)
df_diferenca_producao_alimentos = config_diferenca_producao(df_producao_alimentos, df_producao_alimentos_mes_anterior)
df_diferenca_producao_bebidas = config_diferenca_producao(df_producao_bebidas, df_producao_bebidas_mes_anterior)
df_producao_total = config_producao_agregada(df_producao_alimentos, df_producao_bebidas, df_producao_alimentos_mes_anterior, df_producao_bebidas_mes_anterior)

df_producao_alimentos.drop(columns=['ID_Loja', 'Loja'], inplace=True)
df_producao_bebidas.drop(columns=['ID_Loja', 'Loja'], inplace=True)
df_valoracao_estoque_atual.drop(columns=['ID_Loja', 'Loja'], inplace=True)


df_faturamento_total = config_faturamento_total(df_faturamento_delivery, df_faturamento_zig, df_faturamento_eventos)
df_valoracao_estoque_atual = format_columns_brazilian(df_valoracao_estoque_atual, ['Valor_em_Estoque', 'Quantidade'])
df_producao_alimentos = format_columns_brazilian(df_producao_alimentos, ['Valor_Total', 'Quantidade', 'Valor_Unidade_Medida'])
df_producao_bebidas = format_columns_brazilian(df_producao_bebidas, ['Valor_Total', 'Quantidade', 'Valor_Unidade_Medida'])
df_producao_total = format_columns_brazilian(df_producao_total, ['Valor Produção Mês Anterior', 'Valor Produção Atual'])
diferenca_producao_alimentos = valor_producao_alimentos - valor_producao_alimentos_mes_anterior
diferenca_producao_bebidas = valor_producao_bebidas - valor_producao_bebidas_mes_anterior

cmv_alimentos = compras_alimentos - variacao_estoque_alimentos - saida_alimentos + entrada_alimentos - consumo_interno - diferenca_producao_alimentos
cmv_bebidas = compras_bebidas - variacao_estoque_bebidas - saida_bebidas + entrada_bebidas - diferenca_producao_bebidas
faturamento_total_alimentos = faturamento_bruto_alimentos + faturamento_alimentos_delivery + faturamento_alimentos_eventos
faturamento_total_bebidas = faturamento_bruto_bebidas + faturamento_bebidas_delivery + faturamento_bebidas_eventos

if faturamento_total_alimentos != 0 and faturamento_total_bebidas != 0:
  cmv_percentual_alim = (cmv_alimentos / faturamento_total_alimentos) * 100
  cmv_percentual_bebidas = (cmv_bebidas / faturamento_total_bebidas) * 100
  cmv_percentual_geral = ((cmv_alimentos + cmv_bebidas)/(faturamento_total_alimentos+faturamento_total_bebidas)) * 100
else:
  cmv_percentual_alim = 0
  cmv_percentual_bebidas = 0
  cmv_percentual_geral = 0

faturamento_bruto_alimentos = format_brazilian(faturamento_bruto_alimentos)
faturamento_bruto_bebidas = format_brazilian(faturamento_bruto_bebidas)
faturamento_alimentos_delivery = format_brazilian(faturamento_alimentos_delivery)
faturamento_bebidas_delivery = format_brazilian(faturamento_bebidas_delivery)
faturamento_alimentos_eventos = format_brazilian(faturamento_alimentos_eventos)
faturamento_bebidas_eventos = format_brazilian(faturamento_bebidas_eventos)
compras_alimentos = format_brazilian(compras_alimentos)
compras_bebidas = format_brazilian(compras_bebidas)
variacao_estoque_alimentos = format_brazilian(variacao_estoque_alimentos)
variacao_estoque_bebidas = format_brazilian(variacao_estoque_bebidas) 
cmv_alimentos = format_brazilian(cmv_alimentos)
cmv_bebidas = format_brazilian(cmv_bebidas)
cmv_percentual_alim = format_brazilian(cmv_percentual_alim)
cmv_percentual_bebidas = format_brazilian(cmv_percentual_bebidas)
cmv_percentual_geral = format_brazilian(cmv_percentual_geral)
entrada_alimentos = format_brazilian(entrada_alimentos)
entrada_bebidas = format_brazilian(entrada_bebidas)
saida_alimentos = format_brazilian(saida_alimentos)
saida_bebidas = format_brazilian(saida_bebidas)
consumo_interno = format_brazilian(consumo_interno)
diferenca_producao_alimentos = format_brazilian(diferenca_producao_alimentos)
diferenca_producao_bebidas = format_brazilian(diferenca_producao_bebidas)

colA, colB = st.columns([1, 6])
  
with colA:
  with st.container():
      title_card_cmv('Faturamento')
  st.write('')
  with st.container():
      title_card_cmv('Estoque e Produção')
  st.write('')
  with st.container():
      title_card_cmv('Compras, Entradas e Saídas de A&B')
  st.write('')
  with st.container():
      title_card_cmv('CMV')


with colB:
  col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1], vertical_alignment='center')
  with col1:
    card_cmv('Faturamento Alimentos', f'R$ {faturamento_bruto_alimentos}', is_estoque=False)
  with col2:
    card_cmv('Faturamento Bebidas', f'R$ {faturamento_bruto_bebidas}', is_estoque=False)
  with col3:
    card_cmv('Faturam. Alim. Delivery', f'R$ {faturamento_alimentos_delivery}', is_estoque=False)
  with col4:
    card_cmv('Faturam. Beb. Delivery', f'R$ {faturamento_bebidas_delivery}', is_estoque=False)
  with col5:
    card_cmv('Faturam. Alim. Eventos', f'R$ {faturamento_alimentos_eventos}', is_estoque=False)
  with col6:
    card_cmv('Faturam. Beb. Eventos', f'R$ {faturamento_bebidas_eventos}', is_estoque=False)

  st.write('')

  col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1], vertical_alignment='center')
  with col1:
      card_cmv('Δ Estoque Alimentos', f'R$ {variacao_estoque_alimentos}', is_estoque=True)
  with col2:
      card_cmv('Δ Estoque Bebidas', f'R$ {variacao_estoque_bebidas}', is_estoque=True)
  with col3:
      card_cmv('Δ Produção Alimentos', f'R$ {diferenca_producao_alimentos}', is_estoque=True)
  with col4:
      card_cmv('Δ Produção Bebidas', f'R$ {diferenca_producao_bebidas}', is_estoque=True)
  with col5:
      card_cmv('Consumo Interno', f'R$ {consumo_interno}', is_estoque=True)

  st.write('')

  col1, col2, col3, col4, col5, col6 = st.columns(6)
  with col1:
    card_cmv('Compras Alimentos', f'R$ {compras_alimentos}', is_estoque=False)
  with col2:
    card_cmv('Compras Bebidas', f'R$ {compras_bebidas}', is_estoque=False)
  with col3:
    card_cmv('Entrada Alimentos', f'R$ {entrada_alimentos}', is_estoque=False)
  with col4:
    card_cmv('Saída Alimentos', f'R$ {saida_alimentos}', is_estoque=False)
  with col5:
    card_cmv('Entrada Bebidas', f'R$ {entrada_bebidas}', is_estoque=False)
  with col6:
    card_cmv('Saída Bebidas', f'R$ {saida_bebidas}', is_estoque=False)

  st.write('')

  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    card_cmv('CMV Alimentos', f'R$ {cmv_alimentos}', is_estoque=False)
  with col2:
    card_cmv('CMV Bebidas', f'R$ {cmv_bebidas}', is_estoque=False)
  with col3:
    card_cmv('CMV Percentual Alimentos', f'{cmv_percentual_alim} %', is_estoque=False)
  with col4:
    card_cmv('CMV Percentual Bebidas', f'{cmv_percentual_bebidas} %', is_estoque=False)
  with col5:
    card_cmv('CMV Percentual Geral', f'{cmv_percentual_geral} %', is_estoque=False)

st.divider()
st.markdown('<div style="page-break-before: always;"></div>', unsafe_allow_html=True)

with st.container(border=True):
  col0, col1, col2 = st.columns([1, 12, 1])
  with col1:
    st.subheader('Compras')
    st.dataframe(df_compras, hide_index=True)
    classificacoes = preparar_dados_classe_selecionada(df_insumos_sem_pedido, 'Classificacao')
    fornecedores_com_pedido = preparar_dados_classe_selecionada(df_insumos_com_pedido, 'Fornecedor') 
    with st.expander("Detalhes Insumos BlueMe Sem Pedido"):
      col3, col4, col5 = st.columns(3)
      with col4:
        classificacoes_selecionadas = st.multiselect(label='Selecione Classificação', options=classificacoes, key=1)
        df_insumos_sem_pedido = filtrar_por_classe_selecionada(df_insumos_sem_pedido, 'Classificacao', classificacoes_selecionadas)
      with col5:
        fornecedores_sem_pedido = preparar_dados_classe_selecionada(df_insumos_sem_pedido, 'Fornecedor') 
        fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedores_sem_pedido, key=3)
      df_insumos_sem_pedido = filtrar_por_classe_selecionada(df_insumos_sem_pedido, 'Fornecedor', fornecedores_selecionados)
      valor_total = df_insumos_sem_pedido['Valor'].sum()
      df_insumos_sem_pedido = format_columns_brazilian(df_insumos_sem_pedido, ['Valor'])
      valor_total = format_brazilian(valor_total)
      st.dataframe(df_insumos_sem_pedido, use_container_width=True, hide_index=True)
      st.write('Valor total = R$', valor_total)
    with st.expander("Detalhes Insumos BlueMe Com Pedido"):
      col3, col4, col5 = st.columns(3)
      with col5:
        fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedores_com_pedido, key=2)
      df_insumos_com_pedido = filtrar_por_classe_selecionada(df_insumos_com_pedido, 'Fornecedor', fornecedores_selecionados)
      valor_total_com_pedido = df_insumos_com_pedido['Valor Líquido'].sum()
      valor_alimentos = df_insumos_com_pedido['Valor Líq. Alimentos'].sum()
      valor_bebidas = df_insumos_com_pedido['Valor Líq. Bebidas'].sum()
      valor_hig = df_insumos_com_pedido['Valor Líq. Hig/Limp.'].sum()
      valor_gelo = df_insumos_com_pedido['Valor Líq Gelo/Gas/Carvão/Velas'].sum()
      valor_utensilios = df_insumos_com_pedido['Valor Líq. Utensilios'].sum()
      valor_outros = df_insumos_com_pedido['Valor Líq. Outros'].sum()

      valor_total_com_pedido = format_brazilian(valor_total_com_pedido)
      valor_alimentos = format_brazilian(valor_alimentos)
      valor_bebidas = format_brazilian(valor_bebidas) 
      valor_hig = format_brazilian(valor_hig) 
      valor_gelo = format_brazilian(valor_gelo)
      valor_utensilios = format_brazilian(valor_utensilios)
      valor_outros = format_brazilian(valor_outros)
      df_insumos_com_pedido = format_columns_brazilian(df_insumos_com_pedido, ['Valor Líquido', 'Valor Cotação', 'Insumos - V. Líq', 'Valor Líq. Alimentos','Valor Líq. Bebidas',
                                        'Valor Líq. Hig/Limp.', 'Valor Líq Gelo/Gas/Carvão/Velas', 'Valor Líq. Utensilios', 'Valor Líq. Outros'])
      st.dataframe(df_insumos_com_pedido, use_container_width=True, hide_index=True)
      st.write(
        f"Valor Total = R\\$ {valor_total_com_pedido},  \n"
        f"Valor Alimentos = R\\$ {valor_alimentos},  \n"
        f"Valor Bebidas = R\\$ {valor_bebidas},  \n"
        f"Valor Hig/Limp. = R\\$ {valor_hig},  \n"
        f"Valor Gelo = R\\$ {valor_gelo},  \n"
        f"Valor Utensílios = R\\$ {valor_utensilios},  \n"
        f"Valor Outros = R\\$ {valor_outros}"
      )

df_valoracao_estoque_atual = df_valoracao_estoque_atual.rename(columns={
    'ID_Insumo': 'ID Insumo',
    'Valor_em_Estoque': 'Valor em Estoque',
    'Unidade_Medida': 'Unidade de Medida'
})
df_valoracao_estoque_atual = df_valoracao_estoque_atual[['Categoria', 'ID Insumo', 'Insumo', 'Unidade de Medida', 'Quantidade', 'Valor em Estoque']]
with st.container(border=True):
  col0, col1, col2 = st.columns([1, 12, 1])
  with col1:
    st.subheader('Valoração e Variação de Estoque')
    st.dataframe(df_variacao_estoque, use_container_width=True, hide_index=True)
    with st.expander("Detalhes Valoração Estoque Atual"):
      st.dataframe(df_valoracao_estoque_atual, use_container_width=True, hide_index=True)
    with st.expander("Diferença de Estoque"):
      st.dataframe(df_diferenca_estoque, use_container_width=True, hide_index=True)

df_producao_alimentos = df_producao_alimentos.rename(columns={
    'Item_Produzido': 'Item Produzido',
    'Unidade_Medida': 'Unidade de Medida',
    'Valor_Unidade_Medida': 'Valor Unidade de Medida',
    'Valor_Total': 'Valor Total'
})
df_producao_alimentos = df_producao_alimentos[['Categoria', 'Item Produzido', 'Unidade de Medida', 'Valor Unidade de Medida', 'Quantidade', 'Valor Total']]
df_producao_bebidas = df_producao_bebidas.rename(columns={
    'Item_Produzido': 'Item Produzido',
    'Unidade_Medida': 'Unidade de Medida',
    'Valor_Unidade_Medida': 'Valor Unidade Medida',
    'Valor_Total': 'Valor Total'
})
df_producao_bebidas = df_producao_bebidas[['Categoria', 'Item Produzido', 'Unidade de Medida', 'Valor Unidade Medida', 'Quantidade', 'Valor Total']]

df_diferenca_producao_alimentos = df_diferenca_producao_alimentos.rename(columns={
    'Item_Produzido': 'Item Produzido'
})
df_diferenca_producao_alimentos = df_diferenca_producao_alimentos[['Categoria', 'Item Produzido', 'Unidade de Medida', 'Quantidade Anterior', 'Valor Total Anterior', 'Quantidade Atual', 'Valor Total Atual', 'Diferença Quantidade', 'Diferença Valor Total']]
df_diferenca_producao_bebidas = df_diferenca_producao_bebidas.rename(columns={
    'Item_Produzido': 'Item Produzido'
})
df_diferenca_producao_bebidas = df_diferenca_producao_bebidas[['Categoria', 'Item Produzido', 'Unidade de Medida', 'Quantidade Anterior', 'Valor Total Anterior', 'Quantidade Atual', 'Valor Total Atual', 'Diferença Quantidade', 'Diferença Valor Total']]

with st.container(border=True):
  col0, col1, col2 = st.columns([1, 12, 1])
  with col1:
    st.subheader('Inventário de Produção')
    st.dataframe(df_producao_total, use_container_width=True, hide_index=True)
    with st.expander("Detalhes Valoração Estoque Atual"):
      st.subheader('Valoração de Produção Alimentos')
      st.dataframe(df_producao_alimentos, use_container_width=True, hide_index=True)
      st.subheader('Valoração de Produção Bebidas')
      st.dataframe(df_producao_bebidas, use_container_width=True, hide_index=True)
    with st.expander("Diferença de valoração de Produção"):
      st.subheader('Diferença de Produção Alimentos')
      st.dataframe(df_diferenca_producao_alimentos, use_container_width=True, hide_index=True)
      st.subheader('Diferença de Produção Bebidas')
      st.dataframe(df_diferenca_producao_bebidas, use_container_width=True, hide_index=True)

with st.container(border=True):
  col0, col1, col2 = st.columns([1, 12, 1])
  with col1:
    st.subheader('Transferências e Gastos Extras')
    st.dataframe(df_transf_e_gastos, use_container_width=True, hide_index=True)
    with st.expander("Detalhes Transferências Entradas"):
      st.dataframe(df_transf_entradas, use_container_width=True, hide_index=True)
    with st.expander("Detalhes Transferências Saídas"):
      st.dataframe(df_transf_saidas, use_container_width=True, hide_index=True)

# Seções de cards
sections = {
    "Faturamento": {
        'Faturamento Alimentos': faturamento_bruto_alimentos,
        'Faturamento Bebidas': faturamento_bruto_bebidas,
        'Faturamento Alim. Delivery': faturamento_alimentos_delivery,
        'Faturamento Beb. Delivery': faturamento_bebidas_delivery,
        'Faturamento Alim. Eventos': faturamento_alimentos_eventos,
        'Faturamento Beb. Eventos': faturamento_bebidas_eventos
    },
    "Estoque e Produção": {
        'Δ Estoque Alimentos': variacao_estoque_alimentos,
        'Δ Estoque Bebidas': variacao_estoque_bebidas,
        'Δ Produção Alimentos': diferenca_producao_alimentos,
        'Δ Produção Bebidas': diferenca_producao_bebidas,
        'Consumo Interno': consumo_interno
    },
    "Compras, Entradas e Saídas de A&B": {
        'Compras Alimentos': compras_alimentos,
        'Compras Bebidas': compras_bebidas,
        'Entradas Alimentos': entrada_alimentos,
        'Entradas Bebidas': entrada_bebidas,
        'Saídas Alimentos': saida_alimentos,
        'Saídas Bebidas': saida_bebidas
    },
    "CMV": {
        'CMV Alimentos': cmv_alimentos,
        'CMV Bebidas': cmv_bebidas,
        'CMV Percentual Alimentos': f'{cmv_percentual_alim} %',
        'CMV Percentual Bebidas': f'{cmv_percentual_bebidas} %',
        'CMV Percentual Geral': f'{cmv_percentual_geral} %'
    }
}