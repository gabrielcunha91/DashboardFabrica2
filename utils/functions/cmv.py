import pandas as pd
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *
import calendar
from babel.dates import format_date



def substituicao_deliverys(df):
  substituicoesIds = {
    103: 116,
    112: 104,
    118: 114,
    117: 114,
    139: 105
  }

  substituicoesNomes = {
    'Delivery Fabrica de Bares': 'Bar Brahma - Centro',
    'Hotel Maraba': 'Bar Brahma - Centro',
    'Delivery Bar Leo Centro': 'Bar Léo - Centro',
    'Delivery Orfeu': 'Orfeu',
    'Delivery Jacaré': 'Jacaré'
  }

  df.loc[:, 'Loja'] = df['Loja'].replace(substituicoesNomes)
  df.loc[:, 'ID_Loja'] = df['ID_Loja'].replace(substituicoesIds)
  return df

def primeiro_dia_mes_para_mes_ano(df):
  df['Primeiro_Dia_Mes'] = pd.to_datetime(df['Primeiro_Dia_Mes'], format='%d-%m-%Y')
  df['Primeiro_Dia_Mes'] = df['Primeiro_Dia_Mes'].apply(lambda x: format_date(x, format='MMMM/yyyy', locale='pt_BR'))
  return df


def config_faturamento_bruto_zig(data_inicio, data_fim, lojas_selecionadas):
  df = GET_FATURAM_ZIG_ALIM_BEB_MENSAL(data_inicio=data_inicio, data_fim=data_fim)
  df['Valor_Bruto'] = df['Valor_Bruto'].astype(float)
  df = df.dropna(subset=['ID_Loja'])

  df_delivery = df[df['Delivery'] == 1]
  df_zig = df[df['Delivery'] == 0]

  df_delivery = substituicao_deliverys(df_delivery)

  df_delivery = filtrar_por_classe_selecionada(df_delivery, 'Loja', lojas_selecionadas)
  df_zig = filtrar_por_classe_selecionada(df_zig, 'Loja', lojas_selecionadas)

  faturamento_bruto_alimentos = df_zig[(df_zig['Categoria'] == 'Alimentos')]['Valor_Bruto'].sum()
  faturamento_bruto_bebidas = df_zig[(df_zig['Categoria'] == 'Bebidas')]['Valor_Bruto'].sum()
  faturamento_alimentos_delivery = df_delivery[(df_delivery['Categoria'] == 'Alimentos')]['Valor_Bruto'].sum()
  faturamento_bebidas_delivery = df_delivery[(df_delivery['Categoria'] == 'Bebidas')]['Valor_Bruto'].sum()

  # faturamento_total_zig = faturamento_bruto_alimentos + faturamento_bruto_bebidas + faturamento_alimentos_delivery + faturamento_bebidas_delivery
  return df_delivery, df_zig, faturamento_bruto_alimentos, faturamento_bruto_bebidas, faturamento_alimentos_delivery, faturamento_bebidas_delivery



def config_faturamento_eventos(data_inicio, data_fim, lojas_selecionadas, faturamento_bruto_alimentos, faturamento_bruto_bebidas):
  df = GET_EVENTOS_CMV(data_inicio=data_inicio, data_fim=data_fim)
  df = filtrar_por_classe_selecionada(df, 'Loja', lojas_selecionadas)
  df = substituicao_deliverys(df)

  df['Valor'] = df['Valor'].astype(float)

  faturmento_total_zig = faturamento_bruto_alimentos + faturamento_bruto_bebidas
  faturamento_total_eventos = df['Valor'].sum()

  faturamento_alimentos_eventos = (faturamento_bruto_alimentos * faturamento_total_eventos) / faturmento_total_zig
  faturamento_bebidas_eventos = (faturamento_bruto_bebidas * faturamento_total_eventos) / faturmento_total_zig

  return df, faturamento_alimentos_eventos, faturamento_bebidas_eventos



def config_compras(data_inicio, data_fim, lojas_selecionadas):
# ARRUMAR: primeiro fazer o merge dos insumos agrupados e depois filtrar tudo
  df1 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_SEM_PEDIDO()  
  df2 = GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_COM_PEDIDO()

  df1 = substituicao_deliverys(df1)
  df2 = substituicao_deliverys(df2)

  df1 = filtrar_por_datas(df1, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df2 = filtrar_por_datas(df2, data_inicio, data_fim, 'Primeiro_Dia_Mes')

  df1 = filtrar_por_classe_selecionada(df1, 'Loja', lojas_selecionadas)
  df2 = filtrar_por_classe_selecionada(df2, 'Loja', lojas_selecionadas)

  Compras_Alimentos = df1['BlueMe_Sem_Pedido_Alimentos'].sum() + df2['BlueMe_Com_Pedido_Valor_Liq_Alimentos'].sum()
  Compras_Bebidas = df1['BlueMe_Sem_Pedido_Bebidas'].sum() + df2['BlueMe_Com_Pedido_Valor_Liq_Bebidas'].sum()

  Compras_Alimentos = float(Compras_Alimentos)
  Compras_Bebidas = float(Compras_Bebidas)

  df_compras = pd.merge(df2, df1, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')
  df_compras = df_compras.drop(columns={'BlueMe_Com_Pedido_Valor_Liquido', 'BlueMe_Com_Pedido_Valor_Insumos', 'BlueMe_Com_Pedido_Valor_Liq_Descart_Hig_Limp', 'BlueMe_Com_Pedido_Valor_Liq_Outros', 'BlueMe_Sem_Pedido_Valor_Liquido', 'BlueMe_Sem_Pedido_Descart_Hig_Limp', 'BlueMe_Sem_Pedido_Outros'})
  df_compras = primeiro_dia_mes_para_mes_ano(df_compras)
  df1 = primeiro_dia_mes_para_mes_ano(df1)
  df2 = primeiro_dia_mes_para_mes_ano(df2)
  df1 = df1.rename(columns={'Primeiro_Dia_Mes': 'Mes Ano'})
  df2 = df2.rename(columns={'Primeiro_Dia_Mes': 'Mes Ano'})

  df_compras['Compras Alimentos'] = df_compras['BlueMe_Com_Pedido_Valor_Liq_Alimentos'] + df_compras['BlueMe_Sem_Pedido_Alimentos']
  df_compras['Compras Bebidas'] = df_compras['BlueMe_Com_Pedido_Valor_Liq_Bebidas'] + df_compras['BlueMe_Sem_Pedido_Bebidas']
  df_compras = df_compras.rename(columns={'Primeiro_Dia_Mes': 'Mes Ano', 'BlueMe_Com_Pedido_Valor_Liq_Alimentos': 'BlueMe c/ Pedido Alim.', 'BlueMe_Com_Pedido_Valor_Liq_Bebidas': 'BlueMe c/ Pedido Bebidas', 'BlueMe_Sem_Pedido_Alimentos': 'BlueMe s/ Pedido Alim.', 'BlueMe_Sem_Pedido_Bebidas': 'BlueMe s/ Pedido Bebidas'})

  df_compras = df_compras[['ID_Loja', 'Loja', 'Mes Ano', 'BlueMe c/ Pedido Alim.', 'BlueMe s/ Pedido Alim.', 'Compras Alimentos', 'BlueMe c/ Pedido Bebidas', 'BlueMe s/ Pedido Bebidas', 'Compras Bebidas']]

  return df_compras, Compras_Alimentos, Compras_Bebidas



def config_insumos_blueme_sem_pedido(data_inicio, data_fim, lojas_selecionadas):
  df = GET_INSUMOS_BLUE_ME_SEM_PEDIDO()
  df = df.drop(['Primeiro_Dia_Mes'], axis=1)
  df = filtrar_por_classe_selecionada(df, 'Loja', lojas_selecionadas)
  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data_Emissao')
  df = format_date_brazilian(df, 'Data_Emissao')

  df.rename(columns = {'tdr_ID': 'tdr ID', 'ID_Loja': 'ID Loja', 'Loja': 'Loja', 'Fornecedor': 'Fornecedor', 'Plano_de_Contas': 'Classificacao',
                       'Doc_Serie': 'Doc_Serie', 'Data_Emissao': 'Data Emissão', 'Valor_Liquido': 'Valor Líquido'}, inplace=True)
  df['Valor Líquido'] = df['Valor Líquido'].astype(float)
  return df


def config_insumos_blueme_com_pedido(data_inicio, data_fim, lojas_selecionadas):
  df = GET_INSUMOS_BLUE_ME_COM_PEDIDO()
  df = df.drop(['Primeiro_Dia_Mes'], axis=1)
  df = filtrar_por_classe_selecionada(df, 'Loja', lojas_selecionadas)
  df = filtrar_por_datas(df, data_inicio, data_fim, 'Data_Emissao')

  df = format_date_brazilian(df, 'Data_Emissao')

  df['Valor_Cotacao'] = df['Valor_Cotacao'].astype(float)
  df['Valor_Liquido'] = df['Valor_Liquido'].astype(float)
  df['Insumos - V. Líq'] = df['Valor_Cotacao'] - df['Valor_Liquido']

  df.rename(columns = {'tdr_ID': 'tdr ID', 'ID_Loja': 'ID Loja', 'Loja': 'Loja', 'Fornecedor': 'Fornecedor', 'Doc_Serie': 'Doc_Serie', 'Data_Emissao': 'Data Emissão',
                       'Valor_Liquido': 'Valor Líquido', 'Valor_Cotacao': 'Valor Cotação', 'Valor_Liq_Alimentos': 'Valor Líq. Alimentos',
                       'Valor_Liq_Bebidas': 'Valor Líq. Bebidas', 'Valor_Liq_Descart_Hig_Limp': 'Valor Líq. Hig/Limp.', 'Valor_Gelo_Gas_Carvao_Velas': 'Valor Líq Gelo/Gas/Carvão/Velas',
                       'Valor_Utensilios': 'Valor Líq. Utensilios', 'Valor_Liq_Outros': 'Valor Líq. Outros'}, inplace=True)

  nova_ordem = ['tdr ID', 'ID Loja', 'Loja', 'Fornecedor', 'Doc_Serie', 'Data Emissão', 'Valor Líquido', 'Valor Cotação', 'Insumos - V. Líq', 'Valor Líq. Alimentos',
                'Valor Líq. Bebidas', 'Valor Líq. Hig/Limp.', 'Valor Líq Gelo/Gas/Carvão/Velas', 'Valor Líq. Utensilios', 'Valor Líq. Outros']
  df = df[nova_ordem]
  return df


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
  df_merged = df_merged.drop(['ID_Contagem', 'Primeiro_Dia_Mes', 'Data_Contagem', 'Mes_Anterior_Texto', 'Nome_Insumo', 'Quantidade_Comprada_no_Mes', 'Preco_Medio_Pago_no_Mes', 'Valor_Total_Pago_no_Mes', 'Data_Ultima_Compra', 'Valor_Unidade_Medida', 'Valor_Ultima_Compra_Global'], axis=1)

  return df_merged

def config_variacao_estoque(df_valoracao_estoque_atual, df_valoracao_estoque_mes_anterior):
  valoracao_estoque_atual_alimentos = df_valoracao_estoque_atual[df_valoracao_estoque_atual['Categoria'] == 'ALIMENTOS']['Valor_em_Estoque'].sum()
  valoracao_estoque_atual_bebidas = df_valoracao_estoque_atual[df_valoracao_estoque_atual['Categoria'] == 'BEBIDAS']['Valor_em_Estoque'].sum()

  valoracao_estoque_mes_anterior_alimentos = df_valoracao_estoque_mes_anterior[df_valoracao_estoque_mes_anterior['Categoria'] == 'ALIMENTOS']['Valor_em_Estoque'].sum()
  valoracao_estoque_mes_anterior_bebidas = df_valoracao_estoque_mes_anterior[df_valoracao_estoque_mes_anterior['Categoria'] == 'BEBIDAS']['Valor_em_Estoque'].sum()
  
  variacao_estoque_alimentos = valoracao_estoque_atual_alimentos - valoracao_estoque_mes_anterior_alimentos
  variacao_estoque_bebidas = valoracao_estoque_atual_bebidas - valoracao_estoque_mes_anterior_bebidas

  df_valoracao_estoque_atual = df_valoracao_estoque_atual.rename(columns={'Valor_em_Estoque': 'Estoque Atual', 'Quantidade': 'Quantidade Atual'})
  df_valoracao_estoque_mes_anterior = df_valoracao_estoque_mes_anterior.rename(columns={'Valor_em_Estoque': 'Estoque Mes Anterior', 'Quantidade': 'Quantidade Mes Anterior'})

  df_variacao_estoque = pd.merge(df_valoracao_estoque_mes_anterior, df_valoracao_estoque_atual, on=['ID_Loja', 'Loja', 'Categoria', 'ID_Insumo', 'Insumo', 'Unidade_Medida'], how='outer').fillna(0)
  df_variacao_estoque = df_variacao_estoque.rename(columns={'ID_Loja': 'ID Loja', 'Unidade_Medida': 'Unidade de Medida', 'ID_Insumo': 'ID Insumo'})

  df_variacao_estoque = df_variacao_estoque.groupby(['ID Loja', 'Loja', 'Categoria']).agg({
    'Estoque Mes Anterior': 'sum',
    'Estoque Atual': 'sum'
  }).reset_index()

  df_variacao_estoque = df_variacao_estoque[df_variacao_estoque['Categoria'] != 0]
  df_variacao_estoque = format_columns_brazilian(df_variacao_estoque, ['Estoque Mes Anterior', 'Estoque Atual'])

  return df_variacao_estoque, variacao_estoque_alimentos, variacao_estoque_bebidas

def config_faturamento_total(df_faturamento_delivery, df_faturamento_zig, df_faturamento_eventos):
  df_faturamento_eventos.rename(columns={'Valor': 'Faturamento_Eventos'})

  df_faturamento_delivery = df_faturamento_delivery.drop(['Ano_Mes', 'Data_Evento', 'Desconto', 'Valor_Liquido', 'Delivery'], axis=1)
  df_faturamento_zig = df_faturamento_zig.drop(['Ano_Mes', 'Data_Evento', 'Desconto', 'Valor_Liquido', 'Delivery'], axis=1)
  df_faturamento_zig_alimentos = df_faturamento_zig[df_faturamento_zig['Categoria'] == 'Alimentos']
  df_faturamento_zig_bebidas = df_faturamento_zig[df_faturamento_zig['Categoria'] == 'Bebidas']
  df_faturamento_zig_alimentos = df_faturamento_zig_alimentos.rename(columns={'Valor_Bruto': 'Faturamento Alimentos'})
  df_faturamento_zig_bebidas = df_faturamento_zig_bebidas.rename(columns={'Valor_Bruto': 'Faturamento Bebidas'})

  df_faturamento_delivery_alimentos = df_faturamento_delivery[df_faturamento_delivery['Categoria'] == 'Alimentos']
  df_faturamento_delivery_bebidas = df_faturamento_delivery[df_faturamento_delivery['Categoria'] == 'Bebidas']
  df_faturamento_delivery_alimentos = df_faturamento_delivery_alimentos.rename(columns={'Valor_Bruto': 'Faturamento Delivery Alimentos'})
  df_faturamento_delivery_bebidas = df_faturamento_delivery_bebidas.rename(columns={'Valor_Bruto': 'Faturamento Delivery Bebidas'})

  df_faturamento_zig_alimentos = df_faturamento_zig_alimentos.drop(['Categoria'], axis=1)
  df_faturamento_zig_bebidas = df_faturamento_zig_bebidas.drop(['Categoria'], axis=1)
  df_faturamento_delivery_alimentos = df_faturamento_delivery_alimentos.drop(['Categoria'], axis=1,)
  df_faturamento_delivery_bebidas = df_faturamento_delivery_bebidas.drop(['Categoria'], axis=1)

  df_faturamento_eventos = df_faturamento_eventos.rename(columns={'Valor': 'Faturamento Eventos'})

  df_faturamento_total = pd.merge(df_faturamento_zig_alimentos, df_faturamento_zig_bebidas, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')
  df_faturamento_total = pd.merge(df_faturamento_total, df_faturamento_delivery_alimentos, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')
  df_faturamento_total = pd.merge(df_faturamento_total, df_faturamento_delivery_bebidas, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')
  df_faturamento_total = pd.merge(df_faturamento_total, df_faturamento_eventos, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')

  df_faturamento_total = df_faturamento_total.fillna(0)
  df_faturamento_total = df_faturamento_total.drop(['Data'], axis=1)  

  df_faturamento_total = primeiro_dia_mes_para_mes_ano(df_faturamento_total)
  df_faturamento_total = df_faturamento_total.rename(columns={'Primeiro_Dia_Mes': 'Mês'})
  df_faturamento_total = format_columns_brazilian(df_faturamento_total, ['Faturamento Alimentos', 'Faturamento Bebidas', 'Faturamento Delivery Alimentos', 'Faturamento Delivery Bebidas', 'Faturamento Eventos'])

  return df_faturamento_total



def config_transferencias_gastos(data_inicio, data_fim, lojas_selecionadas):
  df_transf_estoque = GET_TRANSF_ESTOQUE_AGRUPADOS()  
  df_perdas_e_consumo = GET_PERDAS_E_CONSUMO_AGRUPADOS()

  df_transf_e_gastos = pd.merge(df_transf_estoque, df_perdas_e_consumo, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes'], how='outer')
  df_transf_e_gastos = filtrar_por_datas(df_transf_e_gastos, data_inicio, data_fim, 'Primeiro_Dia_Mes')
  df_transf_e_gastos = filtrar_por_classe_selecionada(df_transf_e_gastos, 'Loja', lojas_selecionadas)

  df_transf_e_gastos = primeiro_dia_mes_para_mes_ano(df_transf_e_gastos)
  df_transf_e_gastos = df_transf_e_gastos.rename(columns={'Primeiro_Dia_Mes': 'Mês'})
  df_transf_e_gastos = format_columns_brazilian(df_transf_e_gastos, ['Entrada_Transf_Alim', 'Saida_Transf_Alim', 'Entrada_Transf_Bebidas', 'Saida_Transf_Bebidas', 'Consumo_Interno', 'Quebras_e_Perdas'])

  return df_transf_e_gastos