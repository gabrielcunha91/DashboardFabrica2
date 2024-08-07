import streamlit as st
import pandas as pd
from utils.functions.dados_gerais import *
from utils.queries import *
from utils.components import *


def config_Faturamento_zig(lojas_selecionadas, data_inicio, data_fim):
  FaturamentoZig = GET_FATURAM_ZIG(data_inicio, data_fim)

  filtrar_por_classe_selecionada(FaturamentoZig, 'Loja', lojas_selecionadas)
  categorias_desejadas = ['Alimentos', 'Bebidas', 'Couvert', 'Gifts', 'Serviço', 'Delivery']
  FaturamentoZig = FaturamentoZig[FaturamentoZig['Categoria'].isin(categorias_desejadas)]
  FaturamentoZig = filtrar_por_classe_selecionada(FaturamentoZig, 'Loja', lojas_selecionadas)

  # Cálculo de novas colunas
  FaturamentoZig['Valor Bruto Venda'] = FaturamentoZig['Preco'] * FaturamentoZig['Qtd_Transacao']
  FaturamentoZig['Valor Líquido Venda'] = FaturamentoZig['Valor Bruto Venda'] - FaturamentoZig['Desconto']

  # Renomear colunas
  FaturamentoZig = FaturamentoZig.rename(columns={
    'ID_Venda_EPM': 'ID Venda', 'Data_Venda': 'Data da Venda', 'ID_Produto_EPM': 'ID Produto',
    'Nome_Produto': 'Nome Produto', 'Preco': 'Preço Unitário', 'Qtd_Transacao': 'Quantia comprada',
    'Valor Bruto Venda': 'Valor Bruto Venda', 'Desconto': 'Desconto', 'Valor Líquido Venda': 'Valor Líquido Venda',
    'Categoria': 'Categoria', 'Tipo': 'Tipo'
  })
  # Formatação de datas
  FaturamentoZig = format_date_brazilian(FaturamentoZig, 'Data da Venda')

  return FaturamentoZig


def config_orcamento_faturamento(lojas_selecionadas, data_inicio, data_fim):
  FaturamZigAgregado = GET_FATURAM_ZIG_AGREGADO()
  OrcamFaturam = GET_ORCAM_FATURAM()

  # Conversão de tipos para a padronização de valores
  FaturamZigAgregado['ID_Loja'] = FaturamZigAgregado['ID_Loja'].astype(str)
  OrcamFaturam['ID_Loja'] = OrcamFaturam['ID_Loja'].astype(str)
  FaturamZigAgregado['Primeiro_Dia_Mes'] = pd.to_datetime(FaturamZigAgregado['Primeiro_Dia_Mes'], format='%y-%m-%d')
  OrcamFaturam['Primeiro_Dia_Mes'] = pd.to_datetime(OrcamFaturam['Primeiro_Dia_Mes'])


  # Padronização de categorias (para não aparecer as categorias não desejadas)
  categorias_desejadas = ['Alimentos', 'Bebidas', 'Couvert', 'Gifts', 'Serviço', 'Delivery']
  OrcamFaturam = OrcamFaturam[OrcamFaturam['Categoria'].isin(categorias_desejadas)]
  FaturamZigAgregado = FaturamZigAgregado[FaturamZigAgregado['Categoria'].isin(categorias_desejadas)]


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

  FaturamZigAgregado['Loja'] = FaturamZigAgregado['Loja'].replace(substituicoesNomes)
  FaturamZigAgregado['ID_Loja'] = FaturamZigAgregado['ID_Loja'].replace(substituicoesIds)

  FaturamZigAgregado = filtrar_por_classe_selecionada(FaturamZigAgregado, 'Loja', lojas_selecionadas)
  OrcamFaturam = filtrar_por_classe_selecionada(OrcamFaturam, 'Loja', lojas_selecionadas)

  # Faz o merge das tabelas
  OrcamentoFaturamento = pd.merge(FaturamZigAgregado, OrcamFaturam, on=['ID_Loja', 'Loja', 'Primeiro_Dia_Mes', 'Ano_Mes', 'Categoria'], how='outer')
  OrcamentoFaturamento = OrcamentoFaturamento.dropna(subset=['Categoria'])

  OrcamentoFaturamento['Data_Evento'] = OrcamentoFaturamento['Data_Evento'].fillna(OrcamentoFaturamento['Primeiro_Dia_Mes'])
  OrcamentoFaturamento['Data_Evento'] = pd.to_datetime(OrcamentoFaturamento['Data_Evento'])
  
  
  # Agora filtra
  OrcamentoFaturamento = filtrar_por_datas(OrcamentoFaturamento, data_inicio, data_fim, 'Data_Evento')

  contagem_delivery = OrcamentoFaturamento[OrcamentoFaturamento['Categoria'] == 'Delivery'].shape[0]
  

  # Exclui colunas que não serão usadas na análise, agrupa tuplas de valores de categoria iguais e renomeia as colunas restantes
  OrcamentoFaturamento.drop(['ID_Loja', 'Loja', 'Data_Evento', 'Primeiro_Dia_Mes'], axis=1, inplace=True)
  OrcamentoFaturamento = OrcamentoFaturamento.groupby('Categoria').agg({
    'Orcamento_Faturamento': 'sum',
    'Valor_Bruto': 'sum',
    'Desconto': 'sum',
    'Valor_Liquido': 'sum'
  }).reset_index()
  OrcamentoFaturamento.columns = ['Categoria', 'Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido']

  # Conversão de valores para padronização
  cols = ['Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido']
  OrcamentoFaturamento[cols] = OrcamentoFaturamento[cols].astype(float)

  if 'Delivery' in OrcamentoFaturamento['Categoria'].values:
    OrcamentoFaturamento.loc[OrcamentoFaturamento['Categoria'] == 'Delivery', 'Orçamento'] /= contagem_delivery


  # Criação da coluna 'Faturam - Orçamento' e da linha 'Total Geral'
  OrcamentoFaturamento['Faturam - Orçamento'] = OrcamentoFaturamento['Valor Bruto'] - OrcamentoFaturamento['Orçamento']
  Total = OrcamentoFaturamento[['Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido', 'Faturam - Orçamento']].sum()
  NovaLinha = pd.DataFrame([{
    'Categoria': 'Total Geral', 'Orçamento': Total['Orçamento'], 'Valor Bruto': Total['Valor Bruto'],
    'Desconto': Total['Desconto'], 'Valor Líquido': Total['Valor Líquido'],
    'Faturam - Orçamento': Total['Faturam - Orçamento']
  }])
  OrcamentoFaturamento = pd.concat([OrcamentoFaturamento, NovaLinha], ignore_index=True)

  OrcamentoFaturamento['Atingimento %'] = (OrcamentoFaturamento['Valor Bruto']/OrcamentoFaturamento['Orçamento']) *100
  OrcamentoFaturamento['Atingimento %'] = OrcamentoFaturamento['Atingimento %'].apply(format_brazilian)
  OrcamentoFaturamento['Atingimento %'] = OrcamentoFaturamento['Atingimento %'].apply(lambda x: x + '%')

  OrcamentoFaturamento = OrcamentoFaturamento.reindex(['Categoria', 'Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido',
    'Atingimento %', 'Faturam - Orçamento'], axis=1)

  return OrcamentoFaturamento




def top_dez(dataframe, categoria):
  df = dataframe[dataframe['Categoria'] == categoria]

  # Agrupar por ID Produto
  agrupado = df.groupby(['ID Produto', 'Nome Produto']).agg({
    'Preço Unitário': 'mean',
    'Quantia comprada': 'sum',
    'Valor Bruto Venda': 'sum',
    'Desconto': 'sum',
    'Valor Líquido Venda': 'sum'
  }).reset_index()

  # Ordenar por Valor Líquido Venda em ordem decrescente
  topDez = agrupado.sort_values(by='Valor Líquido Venda', ascending=False).head(10).reset_index(drop=True)

  topDez['Valor Líquido Venda'] = topDez['Valor Líquido Venda'].astype(float)
  topDez['Valor Bruto Venda'] = topDez['Valor Bruto Venda'].astype(float)
  # max_valor_liq_venda = topDez['Valor Líquido Venda'].max()
  # max_valor_bru_venda = topDez['Valor Bruto Venda'].max()

  valor_total_bruto = topDez['Valor Bruto Venda'].sum()
  valor_total_liq = topDez['Valor Líquido Venda'].sum()
  
  topDez['% do Valor Líquido Total'] = (topDez['Valor Líquido Venda']/valor_total_liq) * 100
  topDez['% do Valor Bruto Total'] = (topDez['Valor Bruto Venda']/valor_total_bruto) * 100

  # topDez['Comparação Valor Líq.'] = topDez['Valor Líquido Venda']
  # topDez['Comparação Valor Bruto'] = topDez['Valor Bruto Venda']

  # Aplicar a formatação brasileira nas colunas
  colunas = ['Valor Líquido Venda', 'Valor Bruto Venda']
  topDez = format_columns_brazilian(topDez, colunas)
  
  topDez = format_columns_brazilian(topDez, ['Preço Unitário', 'Desconto'])
  topDez['Quantia comprada'] = topDez['Quantia comprada'].apply(lambda x: str(x))

  # Reordenar as colunas
  colunas_ordenadas = [
    'Nome Produto', 'Preço Unitário', 'Quantia comprada', '% do Valor Bruto Total', 
    'Valor Bruto Venda', 'Desconto', '% do Valor Líquido Total', 'Valor Líquido Venda'
  ]
  topDez = topDez.reindex(columns=colunas_ordenadas)

  st.data_editor(
    topDez,
    width=1080,
    column_config={
      "% do Valor Líquido Total": st.column_config.ProgressColumn(
        "% do Valor Líquido Total",
        help="O Valor Líquido da Venda do produto em porcentagem",
        format="%.2f%%",
        min_value=0,
        max_value=100,
    ),
      "% do Valor Bruto Total": st.column_config.ProgressColumn(
        "% do Valor Bruto Total",
        help="O Valor Bruto da Venda do produto em porcentagem",
        format="%.2f%%",
        min_value=0,
        max_value=100,
      ),
    },
    disabled=True,
    hide_index=True,
  )


  return topDez