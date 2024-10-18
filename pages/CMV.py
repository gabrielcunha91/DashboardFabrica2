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


def main():
  config_sidebar()
  col, colx = st.columns([5, 1])
  with col:
    st.title('CMV')
  with colx:
    if st.button("Logout"):
      logout()
  
  st.divider()

  lojasComDados = preparar_dados_lojas_user()
  data_inicio_default, data_fim_default = preparar_datas_ultimo_mes()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
  st.divider()

  data_inicio_mes_anterior = (data_inicio.replace(day=1) - timedelta(days=1)).replace(day=1)
  data_fim_mes_anterior = data_inicio.replace(day=1) - timedelta(days=1)

  # dfFinal = config_tabelas_iniciais_cmv(lojas_selecionadas, data_inicio, data_fim)
  df_faturamento_delivery, df_faturamento_zig, faturamento_bruto_alimentos, faturamento_bruto_bebidas, faturamento_alimentos_delivery, faturamento_bebidas_delivery = config_faturamento_bruto_zig(data_inicio, data_fim, lojas_selecionadas)
  df_faturamento_eventos, faturamento_alimentos_eventos, faturamento_bebidas_eventos = config_faturamento_eventos(data_inicio, data_fim, lojas_selecionadas, faturamento_bruto_alimentos, faturamento_bruto_bebidas)
  df_insumos_sem_pedido, df_insumos_com_pedido, compras_alimentos, compras_bebidas = config_compras(data_inicio, data_fim, lojas_selecionadas)
  df_valoracao_estoque_atual = config_valoracao_estoque(data_inicio, data_fim, lojas_selecionadas)
  df_valoracao_estoque_mes_anterior = config_valoracao_estoque(data_inicio_mes_anterior, data_fim_mes_anterior, lojas_selecionadas)

  valoracao_estoque_atual_alimentos = df_valoracao_estoque_atual[df_valoracao_estoque_atual['Categoria'] == 'ALIMENTOS']['Valor_em_Estoque'].sum()
  valoracao_estoque_atual_bebidas = df_valoracao_estoque_atual[df_valoracao_estoque_atual['Categoria'] == 'BEBIDAS']['Valor_em_Estoque'].sum()
  valoracao_estoque_mes_anterior_alimentos = df_valoracao_estoque_mes_anterior[df_valoracao_estoque_mes_anterior['Categoria'] == 'ALIMENTOS']['Valor_em_Estoque'].sum()
  valoracao_estoque_mes_anterior_bebidas = df_valoracao_estoque_mes_anterior[df_valoracao_estoque_mes_anterior['Categoria'] == 'BEBIDAS']['Valor_em_Estoque'].sum()
  variacao_estoque_alimentos = valoracao_estoque_atual_alimentos - valoracao_estoque_mes_anterior_alimentos
  variacao_estoque_bebidas = valoracao_estoque_atual_bebidas - valoracao_estoque_mes_anterior_bebidas



  df_faturamento_total = config_faturamento_total(df_faturamento_delivery, df_faturamento_zig, df_faturamento_eventos)
  st.dataframe(df_faturamento_total)


  cmv_alimentos = compras_alimentos - variacao_estoque_alimentos
  cmv_bebidas = compras_bebidas - variacao_estoque_bebidas

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


  col1, col2, col3, col4, col5, col6 = st.columns(6)
  with col1:
    with st.container(border=True):
      st.write('Faturam. Alimentos')
      st.write('R$', faturamento_bruto_alimentos)
  with col2:
    with st.container(border=True):
      st.write('Faturam. Bebidas')
      st.write('R$', faturamento_bruto_bebidas)  
  with col3:
    with st.container(border=True):
      st.write('Faturam. Alim. Delivery.')
      st.write('R$', faturamento_alimentos_delivery)  
  with col4:
    with st.container(border=True):
      st.write('Faturam. Beb. Delivery.')
      st.write('R$', faturamento_bebidas_delivery)
  with col5:
    with st.container(border=True):
      st.write('Faturam. Alim. Eventos.')
      st.write('R$', faturamento_alimentos_eventos)
  with col6:
    with st.container(border=True):
      st.write('Faturam. Beb. Eventos.')
      st.write('R$', faturamento_bebidas_eventos)

  col7, col8, col9, col10 = st.columns(4)
  with col7:
    with st.container(border=True):
      st.write('Variação Estoque Alimentos')
      st.write('R$', variacao_estoque_alimentos)
  with col8:
    with st.container(border=True):
      st.write('Variação Estoque Bebidas')
      st.write('R$', variacao_estoque_bebidas)
  with col9:
    with st.container(border=True):
      st.write('Compras Alimentos')
      st.write('R$', compras_alimentos)
  with col10:
    with st.container(border=True):
      st.write('Compras Bebidas')
      st.write('R$', compras_bebidas)

      
  
  col11, col12, col13, col14, col15 = st.columns(5)
  with col11:
    with st.container(border=True):
      st.write('CMV Alimentos')
      st.write(' R$', cmv_alimentos)
  with col12:
    with st.container(border=True):
      st.write('CMV Bebidas')
      st.write('R$', cmv_bebidas)
  with col13:
    with st.container(border=True):
      st.write('CMV Percentual Alimentos')
      st.write(cmv_percentual_alim, '%')
  with col14:
    with st.container(border=True):
      st.write('CMV Percentual Bebidas')
      st.write(cmv_percentual_bebidas, '%')
  with col15:
    with st.container(border=True):
      st.write('CMV Percentual Geral')
      st.write(cmv_percentual_geral, '%')

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Faturamento Bruto e Estoque por Categoria')

      # dfFaturamento = config_tabela_CMV(dfFinal)
      # dfFaturamento['Mês'] = pd.to_datetime(dfFaturamento['Mês'], format='%d-%m-%Y')
      # # Formatando a data para "nome do mês/ano"
      # dfFaturamento['Mês'] = dfFaturamento['Mês'].apply(lambda x: format_date(x, format='MMMM/yyyy', locale='pt_BR'))
      # st.dataframe(dfFaturamento, use_container_width=True, hide_index=True)
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Compras')
      dfcompras = config_tabela_compras(dfFinal.copy())
      dfcompras['Mês'] = pd.to_datetime(dfcompras['Mês'], format='%d-%m-%Y')
      # Formatando a data para "nome do mês/ano"
      dfcompras['Mês'] = dfcompras['Mês'].apply(lambda x: format_date(x, format='MMMM/yyyy', locale='pt_BR'))
      st.dataframe(dfcompras, use_container_width=True, hide_index=True)
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      st.subheader('Transferências e gastos extras')
      dfTransf = config_tabela_transferencias(dfFinal.copy())
      dfTransf['Mês'] = pd.to_datetime(dfTransf['Mês'], format='%d-%m-%Y')
      # Formatando a data para "nome do mês/ano"
      dfTransf['Mês'] = dfTransf['Mês'].apply(lambda x: format_date(x, format='MMMM/yyyy', locale='pt_BR'))
      st.dataframe(dfTransf, use_container_width=True, hide_index=True)

  insumosSemPedido = config_insumos_blueme_sem_pedido(GET_INSUMOS_BLUE_ME_SEM_PEDIDO(), data_inicio, data_fim)
  insumosComPedido = config_insumos_blueme_com_pedido(GET_INSUMOS_BLUE_ME_COM_PEDIDO(), data_inicio, data_fim)
  classificacoes = preparar_dados_classe_selecionada(insumosSemPedido, 'Classificacao')
  forneceforesSemPedido = preparar_dados_classe_selecionada(insumosSemPedido, 'Fornecedor') 
  fornecedoresComPedido = preparar_dados_classe_selecionada(insumosSemPedido, 'Fornecedor') 

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      col4, col5, col6 = st.columns([5, 4, 4])
      with col4:
        st.subheader('Insumos BlueMe sem Pedido')
      with col5:
        classificacoes_selecionadas = st.multiselect(label='Selecione Classificações', options=classificacoes)
        insumosSemPedido.rename(columns = {'Classificacao': 'Classificação'}, inplace=True)
        insumosSemPedido = filtrar_por_classe_selecionada(insumosSemPedido, 'Classificação', classificacoes_selecionadas)
      with col6:
        fornecedores_selecionadss = st.multiselect(label='Selecione Fornecedores', options=forneceforesSemPedido, key=1)
        insumosSemPedido = filtrar_por_classe_selecionada(insumosSemPedido, 'Fornecedor', fornecedores_selecionadss)
      valorTotal = insumosSemPedido['Valor Líquido'].sum()
      valorTotal = format_brazilian(valorTotal)
      insumosSemPedido = format_columns_brazilian(insumosSemPedido, ['Valor Líquido'])
      st.dataframe(insumosSemPedido, use_container_width=True, hide_index=True)
      st.write('Valor Líquido Total: R$', valorTotal)
  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 12, 1])
    with col1:
      col4, col5, = st.columns([7, 5])
      with col4:
        st.subheader('Insumos BlueMe com Pedido')
      with col5:
        fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedoresComPedido, key=2)
        insumosComPedido = filtrar_por_classe_selecionada(insumosComPedido, 'Fornecedor', fornecedores_selecionados)
      valorTotal = insumosComPedido['Valor Líquido'].sum()
      cols = ['Valor Líquido', 'Valor Insumos', 'Insumos - V. Líq']
      valorTotal = format_brazilian(valorTotal)
      insumosComPedido = format_columns_brazilian(insumosComPedido, cols)
      st.dataframe(insumosComPedido, use_container_width=True, hide_index=True)
      st.write('Valor Líquido Total: R$', valorTotal)

if __name__ == '__main__':
  main()
