import pandas as pd
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *
import calendar


def config_faturamento_bruto_zig(data_inicio, data_fim, lojas_selecionadas):
  df = GET_FATURAM_ZIG_ALIM_BEB_MENSAL(data_inicio=data_inicio, data_fim=data_fim)
  df['Valor_Bruto'] = df['Valor_Bruto'].astype(float)

  df_delivery = df[df['Delivery'] == 1]
  df_zig = df[df['Delivery'] == 0]

  substituicoesIds = {
    '103': '116',
    '112': '104',
    '118': '114',
    '139': '105'
  }

  substituicoesNomes = {
    'Delivery Fabrica de Bares': 'Bar Brahma - Centro',
    'Delivery Bar Leo Centro': 'Bar Léo - Centro',
    'Delivery Orfeu': 'Orfeu',
    'Delivery Jacaré': 'Jacaré'
  }

  df_delivery['Loja'] = df_delivery['Loja'].replace(substituicoesNomes)
  df_delivery['ID_Loja'] = df_delivery['ID_Loja'].replace(substituicoesIds)

  df = filtrar_por_classe_selecionada(df, 'Loja', lojas_selecionadas)

  faturamento_bruto_alimentos = df[(df['Categoria'] == 'Alimentos') & (df['Delivery'] == 0)]['Valor_Bruto'].sum()
  faturamento_bruto_bebidas = df[(df['Categoria'] == 'Bebidas') & (df['Delivery'] == 0)]['Valor_Bruto'].sum()
  faturamento_alimentos_delivery = df[(df['Categoria'] == 'Alimentos') & (df['Delivery'] == 1)]['Valor_Bruto'].sum()
  faturamento_bebidas_delivery = df[(df['Categoria'] == 'Bebidas') & (df['Delivery'] == 1)]['Valor_Bruto'].sum()


  # faturamento_total_zig = faturamento_bruto_alimentos + faturamento_bruto_bebidas + faturamento_alimentos_delivery + faturamento_bebidas_delivery
  return df_delivery, df_zig, faturamento_bruto_alimentos, faturamento_bruto_bebidas, faturamento_alimentos_delivery, faturamento_bebidas_delivery

def config_faturamento_eventos(data_inicio, data_fim, lojas_selecionadas, faturamento_bruto_alimentos, faturamento_bruto_bebidas):
  df = GET_EVENTOS_CMV(data_inicio=data_inicio, data_fim=data_fim)
  df = filtrar_por_classe_selecionada(df, 'Loja', lojas_selecionadas)

  df['Valor'] = df['Valor'].astype(float)

  faturmento_total_zig = faturamento_bruto_alimentos + faturamento_bruto_bebidas
  faturamento_total_eventos = df['Valor'].sum()

  faturamento_alimentos_eventos = (faturamento_bruto_alimentos * faturamento_total_eventos) / faturmento_total_zig
  faturamento_bebidas_eventos = (faturamento_bruto_bebidas * faturamento_total_eventos) / faturmento_total_zig

  return df, faturamento_alimentos_eventos, faturamento_bebidas_eventos


def config_compras(data_inicio, data_fim, lojas_selecionadas):
  df1 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_SEM_PEDIDO()  
  df2 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_COM_PEDIDO()

  df1 = filtrar_por_datas(df1, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df2 = filtrar_por_datas(df2, data_inicio, data_fim, 'Primeiro_Dia_Mes')

  df1 = filtrar_por_classe_selecionada(df1, 'Loja', lojas_selecionadas)
  df2 = filtrar_por_classe_selecionada(df2, 'Loja', lojas_selecionadas)
  
  Compras_Alimentos = df1['BlueMe_Sem_Pedido_Alimentos'].sum() + df2['BlueMe_Com_Pedido_Valor_Liq_Alimentos'].sum()
  Compras_Bebidas = df1['BlueMe_Sem_Pedido_Bebidas'].sum() + df2['BlueMe_Com_Pedido_Valor_Liq_Bebidas'].sum()

  Compras_Alimentos = float(Compras_Alimentos)
  Compras_Bebidas = float(Compras_Bebidas)

  return df1, df2, Compras_Alimentos, Compras_Bebidas


def config_valoracao_estoque(data_inicio, data_fim, lojas_selecionadas):

  if data_inicio.month == 12:
    data_inicio = data_inicio.replace(year=data_inicio.year + 1, month=1, day=1)
  else:
    data_inicio = data_inicio.replace(month=data_inicio.month + 1, day=1)

  data_fim = data_inicio.replace(day=calendar.monthrange(data_inicio.year, data_inicio.month)[1])

  contagem_insumos = GET_CONTAGEM_INSUMOS()
  precos_consolidados_mes = GET_PRECOS_CONSOLIDADOS_MES()
  ultimos_precos = GET_ULTIMOS_PRECOS()
  precos_outras_lojas = GET_PRECOS_OUTRAS_LOJAS()

  contagem_insumos = filtrar_por_classe_selecionada(contagem_insumos, 'Loja', lojas_selecionadas)
  precos_consolidados_mes = filtrar_por_classe_selecionada(precos_consolidados_mes, 'Loja', lojas_selecionadas)
  ultimos_precos = filtrar_por_classe_selecionada(ultimos_precos, 'Loja', lojas_selecionadas)

  # 1. Left join entre Contagem_Insumos e Precos_Consolidados_Mes
  df_merged = pd.merge(contagem_insumos, 
                     precos_consolidados_mes, 
                     on=['ID_Insumo', 'Mes_Anterior_Texto', 'Loja'], 
                     how='left')
  

  # 2. Left join com Ultimos_Precos
  df_merged = pd.merge(df_merged, 
                     ultimos_precos[['ID_Insumo', 'Data_Ultima_Compra', 'Valor_Unidade_Medida', 'Loja']], 
                     on=['ID_Insumo', 'Loja'], 
                     how='left')


  # 3. Left join com Precos_Outras_Casas
  df_merged = pd.merge(df_merged, 
                     precos_outras_lojas[['ID_Insumo', 'Valor_Ultima_Compra_Global']], 
                     on='ID_Insumo', 
                     how='left')


  df_merged['Valor_em_Estoque'] = df_merged.apply(
    lambda row: 
        (float(row['Quantidade']) * float(row['Preco_Medio_Pago_no_Mes'])) 
        if pd.notna(row['Preco_Medio_Pago_no_Mes']) else
        (float(row['Quantidade']) * float(row['Valor_Unidade_Medida'])) 
        if pd.notna(row['Valor_Unidade_Medida']) else
        (float(row['Quantidade']) * float(row['Valor_Ultima_Compra_Global'])) 
        if pd.notna(row['Valor_Ultima_Compra_Global']) else 0, 
    axis=1
  )

  df_merged = filtrar_por_datas(df_merged, data_inicio, data_fim, 'Primeiro_Dia_Mes')

  df_merged = df_merged.drop(['ID_Contagem', 'Primeiro_Dia_Mes', 'Mes_Anterior_Texto', 'Nome_Insumo', 'Quantidade_Comprada_no_Mes', 'Preco_Medio_Pago_no_Mes', 'Valor_Total_Pago_no_Mes', 'Data_Ultima_Compra', 'Valor_Unidade_Medida', 'Valor_Ultima_Compra_Global'], axis=1)

  return df_merged


def config_faturamento_total(df_faturamento_delivery, df_faturamento_zig, df_faturamento_eventos):
  df_faturamento_eventos.rename(columns={'Valor': 'Faturamento_Eventos'})

  df_faturamento_delivery = df_faturamento_delivery.drop(['Ano_Mes', 'Data_Evento', 'Desconto', 'Valor_Liquido', 'Delivery'], axis=1)
  df_faturamento_zig = df_faturamento_zig.drop(['Ano_Mes', 'Data_Evento', 'Desconto', 'Valor_Liquido', 'Delivery'], axis=1)

  df_faturamento_zig_alimentos = df_faturamento_zig[df_faturamento_zig['Categoria'] == 'Alimentos']
  df_faturamento_zig_bebidas = df_faturamento_zig[df_faturamento_zig['Categoria'] == 'Bebidas']

  df_faturamento_zig_alimentos = df_faturamento_zig_alimentos.rename(columns={'Valor_Bruto': 'Faturamento_Alimentos'})
  df_faturamento_zig_bebidas = df_faturamento_zig_bebidas.rename(columns={'Valor_Bruto': 'Faturamento_Bebidas'})


  df_faturamento_delivery_alimentos = df_faturamento_delivery[df_faturamento_delivery['Categoria'] == 'Alimentos']
  df_faturamento_delivery_bebidas = df_faturamento_delivery[df_faturamento_delivery['Categoria'] == 'Bebidas']

  df_faturamento_delivery_alimentos = df_faturamento_delivery_alimentos.rename(columns={'Valor_Bruto': 'Faturamento_Delivery_Alimentos'})
  df_faturamento_delivery_bebidas = df_faturamento_delivery_bebidas.rename(columns={'Valor_Bruto': 'Faturamento_Delivery_Bebidas'})

  df_faturamento_zig_alimentos = df_faturamento_zig_alimentos.drop(['Categoria'], axis=1)
  df_faturamento_zig_bebidas = df_faturamento_zig_bebidas.drop(['Categoria'], axis=1)

  df_faturamento_delivery_alimentos = df_faturamento_delivery_alimentos.drop(['Categoria'], axis=1,)
  df_faturamento_delivery_bebidas = df_faturamento_delivery_bebidas.drop(['Categoria'], axis=1)

  st.dataframe(df_faturamento_zig_alimentos)
  st.dataframe(df_faturamento_zig_bebidas)
  st.dataframe(df_faturamento_delivery_alimentos)
  st.dataframe(df_faturamento_delivery_bebidas)
  st.dataframe(df_faturamento_eventos)

  df_faturamento_total = pd.merge(df_faturamento_zig_alimentos, df_faturamento_zig_bebidas, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')
  df_faturamento_total = pd.merge(df_faturamento_total, df_faturamento_delivery_alimentos, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')
  df_faturamento_total = pd.merge(df_faturamento_total, df_faturamento_delivery_bebidas, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')
  df_faturamento_total = pd.merge(df_faturamento_total, df_faturamento_eventos, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')

  df_faturamento_total = df_faturamento_total.fillna(0)

  return df_faturamento_total