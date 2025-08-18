import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import mysql.connector

LOGGER = get_logger(__name__)

def mysql_connection():
  mysql_config = st.secrets["mysql"]
  # Cria a conexão com MySQL
  conn = mysql.connector.connect(
    host=mysql_config['host'],
    port=mysql_config['port'],
    database=mysql_config['database'],
    user=mysql_config['username'],
    password=mysql_config['password']
  )    
  return conn

def execute_query(query):
  conn = mysql_connection()
  cursor = conn.cursor()
  cursor.execute(query)

  # Obter nomes das colunas
  column_names = [col[0] for col in cursor.description]
  
  # Obter resultados
  result = cursor.fetchall()
  
  cursor.close()
  return result, column_names


def dataframe_query(query):
  resultado, nomeColunas = execute_query(query)
  dataframe = pd.DataFrame(resultado, columns=nomeColunas)
  return dataframe


########### Permissions #############

@st.cache_data
def GET_PERMISSIONS(email):
  emailStr = f"'{email}'"
  return dataframe_query(f''' 
  SELECT 
	  tg.POSICAO AS 'Permissao'
  FROM
	  ADMIN_USERS au 
	  LEFT JOIN T_GRUPO_USUARIO tgu ON au.ID = tgu.FK_USUARIO 
	  LEFT JOIN T_GRUPO tg ON tgu.FK_GRUPO = tg.id
  WHERE au.LOGIN = {emailStr}
  ''')

@st.cache_data
def GET_LOJAS_USER(email):
  emailStr = f"'{email}'"
  return dataframe_query(f'''
  SELECT 
	  te.NOME_FANTASIA AS 'Loja'
  FROM
  	ADMIN_USERS au 
	  LEFT JOIN T_USUARIOS_EMPRESAS tue ON au.ID = tue.FK_USUARIO 
	  LEFT JOIN T_EMPRESAS te ON tue.FK_EMPRESA = te.ID
	  LEFT JOIN T_LOJAS tl ON te.ID = tl.ID
  WHERE au.LOGIN = {emailStr}
  ''')

@st.cache_data
def GET_USERNAME(email):
  emailStr = f"'{email}'"
  return dataframe_query(f'''
  SELECT 
	  au.FULL_NAME AS 'Nome'
  FROM
  	ADMIN_USERS au 
  WHERE au.LOGIN = {emailStr}
  ''')

#############3 get lojas #########

@st.cache_data
def GET_LOJAS():
  return dataframe_query(f'''
  SELECT 
	  te.NOME_FANTASIA AS 'Loja'
  FROM
	  T_EMPRESAS te 
  ''')



######## Faturamento zig #########




@st.cache_data
def GET_FATURAM_ZIG_AGREGADO(data_inicio, data_fim):
  return dataframe_query(f''' 
  SELECT
    te.ID AS ID_Loja,
    te.NOME_FANTASIA AS Loja,
    CASE 
      WHEN te.ID IN (103, 112, 118, 139) THEN 'Delivery'
      ELSE tivc2.DESCRICAO 
    END AS Categoria,
    cast(date_format(cast(tiv.EVENT_DATE as date), '%Y-%m-01') as date) AS Primeiro_Dia_Mes,
    concat(year(cast(tiv.EVENT_DATE as date)), '-', month(cast(tiv.EVENT_DATE as date))) AS Ano_Mes,
    cast(tiv.EVENT_DATE as date) AS Data_Evento,
    SUM((tiv.UNIT_VALUE * tiv.COUNT)) AS Valor_Bruto,
    SUM(tiv.DISCOUNT_VALUE) AS Desconto,
    SUM((tiv.UNIT_VALUE * tiv.COUNT) - tiv.DISCOUNT_VALUE) AS Valor_Liquido
  FROM T_ITENS_VENDIDOS tiv
  LEFT JOIN T_ITENS_VENDIDOS_CADASTROS tivc ON tiv.PRODUCT_ID = tivc.ID_ZIGPAY
  LEFT JOIN T_ITENS_VENDIDOS_CATEGORIAS tivc2 ON tivc.FK_CATEGORIA = tivc2.ID
  LEFT JOIN T_ITENS_VENDIDOS_TIPOS tivt ON tivc.FK_TIPO = tivt.ID
  LEFT JOIN T_EMPRESAS te ON tiv.LOJA_ID = te.ID_ZIGPAY
  WHERE cast(tiv.EVENT_DATE as date) >= '{data_inicio}'
    AND cast(tiv.EVENT_DATE as date) <= '{data_fim}'
  GROUP BY 
    ID_Loja,
    Categoria,
    Primeiro_Dia_Mes;
''')  




@st.cache_data
def GET_ORCAM_FATURAM():
  return dataframe_query(f'''
  SELECT
    te.ID AS ID_Loja,
    te.NOME_FANTASIA AS Loja,
    CONCAT(to2.ANO, '-', to2.MES) AS Ano_Mes,
    cast(date_format(cast(CONCAT(to2.ANO, '-', to2.MES, '-01') AS date), '%Y-%m-01') as date) AS Primeiro_Dia_Mes,
    to2.VALOR AS Orcamento_Faturamento,
    CASE
      WHEN tccg.DESCRICAO IN ('VENDA DE ALIMENTO', 'Alimentação') THEN 'Alimentos'
      WHEN tccg.DESCRICAO IN ('VENDA DE BEBIDAS', 'Bebida') THEN 'Bebidas'
      WHEN tccg.DESCRICAO IN ('VENDA DE COUVERT/ SHOWS', 'Artístico (couvert/shows)') THEN 'Couvert'
      WHEN tccg.DESCRICAO IN ('SERVICO', 'Serviço') THEN 'Serviço'
      WHEN tccg.DESCRICAO IN ('DELIVERY', 'Delivery') THEN 'Delivery'
      WHEN tccg.DESCRICAO IN ('GIFTS', 'Gifts') THEN 'Gifts'
      ELSE tccg.DESCRICAO
    END AS Categoria
  FROM
    T_ORCAMENTOS to2
  JOIN
    T_EMPRESAS te ON to2.FK_EMPRESA = te.ID
  JOIN
    T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg ON to2.FK_CLASSIFICACAO_2 = tccg.ID
  WHERE
    to2.FK_CLASSIFICACAO_1 IN (178, 245)
  ORDER BY
    ID_Loja,
    Ano_Mes;
  ''')

@st.cache_data
def GET_FATURAM_ZIG(data_inicial, data_final):
  # Formatando as datas para o formato de string com aspas simples
  data_inicial_str = f"'{data_inicial.strftime('%Y-%m-%d %H:%M:%S')}'"
  data_final_str = f"'{data_final.strftime('%Y-%m-%d %H:%M:%S')}'"
    
  return dataframe_query(f'''
  SELECT tiv.ID AS 'ID_Venda_EPM',
    te.NOME_FANTASIA AS Loja,
    tiv.TRANSACTION_DATE as 'Data_Venda',
    CAST(tiv.EVENT_DATE as DATE) as 'Data_Evento',
    tivc.ID as 'ID_Produto_EPM',
    tiv.PRODUCT_NAME as 'Nome_Produto',
    tiv.UNIT_VALUE as 'Preco',
    tiv.COUNT as 'Qtd_Transacao',
    tiv.DISCOUNT_VALUE as 'Desconto',
    tivc2.DESCRICAO as 'Categoria',
    tivt.DESCRICAO as 'Tipo'
  FROM T_ITENS_VENDIDOS tiv 
    LEFT JOIN T_ITENS_VENDIDOS_CADASTROS tivc ON (tiv.PRODUCT_ID = tivc.ID_ZIGPAY)
    LEFT JOIN T_ITENS_VENDIDOS_CATEGORIAS tivc2 ON (tivc.FK_CATEGORIA = tivc2.ID)
    LEFT JOIN T_ITENS_VENDIDOS_TIPOS tivt ON (tivc.FK_TIPO = tivt.ID)
    LEFT JOIN T_EMPRESAS te ON (tiv.LOJA_ID = te.ID_ZIGPAY)
  WHERE CAST(tiv.EVENT_DATE as DATETIME) >= {data_inicial_str} AND CAST(tiv.EVENT_DATE as DATETIME) <= {data_final_str}
  ''')



############### Receitas extraordinárias ################

@st.cache_data
def GET_RECEIT_EXTRAORD():
  #'Data_Evento' é, na realidade, a data da competencia, eu só coloquei esse nome pra ficar mais fácil de programar
  return dataframe_query(f'''
  SELECT
    tre.ID as 'ID_receita',
    te.NOME_FANTASIA as 'Loja',
    trec3.NOME as 'Cliente',
    trec.CLASSIFICACAO as 'Classificacao',
    tep.ID as 'ID_Evento',
    tep.NOME_EVENTO as 'Nome_Evento',
    tre.VALOR as 'Valor_Total',
    CAST(tre.DATA_OCORRENCIA AS DATE) as 'Data_Evento',
    tre.VALOR_CATEGORIA_AB as 'Categ_AB',
    tre.VALOR_CATEGORIA_ALUGUEL as 'Categ_Aluguel',
    tre.VALOR_CATEGORIA_ARTISTICO as 'Categ_Artist',
    tre.VALOR_CATEGORIA_COUVERT as 'Categ_Couvert',
    tre.VALOR_CATEGORIA_LOCACAO as 'Categ_Locacao',
    tre.VALOR_CATEGORIA_PATROCINIO as 'Categ_Patroc',
    tre.VALOR_CATEGORIA_TAXA_SERVICO as 'Categ_Taxa_Serv'
  FROM T_RECEITAS_EXTRAORDINARIAS tre
    INNER JOIN T_EMPRESAS te ON (tre.FK_EMPRESA = te.ID)
    LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLASSIFICACAO trec ON (tre.FK_CLASSIFICACAO = trec.ID)
    LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec3 ON (tre.FK_CLIENTE = trec3.ID)
    LEFT JOIN T_EVENTO_PRE tep ON (tre.FK_EVENTO = tep.ID)
  WHERE tre.FK_STATUS_PGTO = 103 
    AND CAST(tre.DATA_OCORRENCIA AS DATE) >= '2023-10-01'
  ''')


def GET_CLSSIFICACAO():
  return dataframe_query(f'''
  SELECT
    trec.CLASSIFICACAO as 'Classificacao'
  FROM T_RECEITAS_EXTRAORDINARIAS_CLASSIFICACAO trec 
  GROUP BY trec.CLASSIFICACAO 
''')


############## Despesas ################

@st.cache_data
def GET_DESPESAS():
  return dataframe_query(f'''
  SELECT 
    tdr.ID AS ID,
    te.NOME_FANTASIA AS Loja,
    tf.CORPORATE_NAME AS Fornecedor,
    tdr.NF AS Doc_Serie,
    STR_TO_DATE(tdr.COMPETENCIA, '%Y-%m-%d') AS Data_Emissao,
    STR_TO_DATE(tdr.VENCIMENTO, '%Y-%m-%d') AS Data_Vencimento,
    CAST(DATE_FORMAT(CAST(tdr.COMPETENCIA AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes,
    tdr.OBSERVACAO AS Descricao,
    tdr.VALOR_LIQUIDO AS Valor_Liquido,
    tccg2.DESCRICAO AS Classificacao_Contabil_2,
    tccg1.DESCRICAO AS Classificacao_Contabil_1,
    CASE 
      WHEN tdr.FK_Status = 'Provisionado' THEN 'Provisionado'
      ELSE 'Real'
    END AS Status
  FROM T_DESPESA_RAPIDA tdr
  JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID
  LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID
  LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID
  LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg1 ON tccg2.FK_GRUPO_1 = tccg1.ID
  WHERE tccg1.FK_VERSAO_PLANO_CONTABIL = 103
    AND NOT EXISTS (
      SELECT 1
      FROM T_DESPESA_RAPIDA_ITEM tdri
      WHERE tdri.FK_DESPESA_RAPIDA = tdr.ID);
''')


@st.cache_data
def GET_ORCAMENTOS_DESPESAS():
  return dataframe_query(f'''
  SELECT
    to2.ID AS ID_Orcamento,
    te.NOME_FANTASIA AS Loja,
    tccg2.DESCRICAO AS Classificacao_Contabil_2,
    tccg1.DESCRICAO AS Classificacao_Contabil_1,
    to2.VALOR AS Orcamento,
    cast(date_format(cast(CONCAT(to2.ANO, '-', to2.MES, '-01') AS date), '%Y-%m-01') as date) AS Primeiro_Dia_Mes
  FROM
    T_ORCAMENTOS to2 
  LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON to2.FK_CLASSIFICACAO_2 = tccg2.ID
  LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg1 ON tccg2.FK_GRUPO_1 = tccg1.ID
  LEFT JOIN T_EMPRESAS te ON to2.FK_EMPRESA = te.ID;
''')

############################### CMV ###################################

@st.cache_data
def GET_FATURAM_ZIG_ALIM_BEB_MENSAL(data_inicio, data_fim):
  return dataframe_query(f'''
  SELECT
    te.ID AS ID_Loja,
    te.NOME_FANTASIA AS Loja,
    tivc2.DESCRICAO AS Categoria,
    CASE 
      WHEN te.ID IN (103, 112, 118, 139) THEN 1
      ELSE 0 
    END AS Delivery,
    cast(date_format(cast(tiv.EVENT_DATE AS date), '%Y-%m-01') AS date) AS Primeiro_Dia_Mes,
    concat(year(cast(tiv.EVENT_DATE AS date)), '-', month(cast(tiv.EVENT_DATE AS date))) AS Ano_Mes,
    cast(tiv.EVENT_DATE AS date) AS Data_Evento,
    SUM((tiv.UNIT_VALUE * tiv.COUNT)) AS Valor_Bruto,
    SUM(tiv.DISCOUNT_VALUE) AS Desconto,
    SUM((tiv.UNIT_VALUE * tiv.COUNT) - tiv.DISCOUNT_VALUE) AS Valor_Liquido
  FROM T_ITENS_VENDIDOS tiv
  LEFT JOIN T_ITENS_VENDIDOS_CADASTROS tivc ON tiv.PRODUCT_ID = tivc.ID_ZIGPAY
  LEFT JOIN T_ITENS_VENDIDOS_CATEGORIAS tivc2 ON tivc.FK_CATEGORIA = tivc2.ID
  LEFT JOIN T_ITENS_VENDIDOS_TIPOS tivt ON tivc.FK_TIPO = tivt.ID
  LEFT JOIN T_EMPRESAS te ON tiv.LOJA_ID = te.ID_ZIGPAY
  WHERE cast(tiv.EVENT_DATE AS date) >= '{data_inicio}'
    AND cast(tiv.EVENT_DATE AS date) <= '{data_fim}'
    AND tivc2.DESCRICAO IN ('Alimentos', 'Bebidas')
  GROUP BY 
    ID_Loja,
    Categoria,
    Primeiro_Dia_Mes;
''')

def GET_VALORACAO_ESTOQUE(loja, data_contagem):
  return dataframe_query(f'''
  SELECT 
  	te.ID AS 'ID_Loja',
  	te.NOME_FANTASIA AS 'Loja',
  	tin5.ID AS 'ID_Insumo',
  	REPLACE(tin5.DESCRICAO, ',', '.') AS 'Insumo',
  	tci.QUANTIDADE_INSUMO AS 'Quantidade',
  	tin5.FK_INSUMOS_NIVEL_4 AS 'ID_Nivel_4',
  	tudm.UNIDADE_MEDIDA_NAME AS 'Unidade_Medida',
    tin.DESCRICAO AS 'Categoria',
  	tve.VALOR_EM_ESTOQUE AS 'Valor_em_Estoque',
  	tci.DATA_CONTAGEM
  FROM T_VALORACAO_ESTOQUE tve 
  LEFT JOIN T_CONTAGEM_INSUMOS tci ON tve.FK_CONTAGEM = tci.ID 
  LEFT JOIN T_EMPRESAS te ON tci.FK_EMPRESA = te.ID 
  LEFT JOIN T_INSUMOS_NIVEL_5 tin5 ON tci.FK_INSUMO = tin5.ID
  LEFT JOIN T_INSUMOS_NIVEL_4 tin4 ON tin5.FK_INSUMOS_NIVEL_4 = tin4.ID 
  LEFT JOIN T_INSUMOS_NIVEL_3 tin3 ON tin4.FK_INSUMOS_NIVEL_3 = tin3.ID 
  LEFT JOIN T_INSUMOS_NIVEL_2 tin2 ON tin3.FK_INSUMOS_NIVEL_2 = tin2.ID
  LEFT JOIN T_INSUMOS_NIVEL_1 tin ON tin2.FK_INSUMOS_NIVEL_1 = tin.ID
  LEFT JOIN T_UNIDADES_DE_MEDIDAS tudm ON tin5.FK_UNIDADE_MEDIDA = tudm.ID
  WHERE tci.QUANTIDADE_INSUMO != 0
    AND tci.DATA_CONTAGEM = '{data_contagem}'
    AND te.NOME_FANTASIA = '{loja}'
  ORDER BY DATA_CONTAGEM DESC
  ''')



@st.cache_data
def GET_EVENTOS_CMV(data_inicio, data_fim):
  return dataframe_query(f'''
  SELECT 
    te.ID AS 'ID_Loja',
   	te.NOME_FANTASIA AS 'Loja',
   	SUM(tec.VALOR_EVENTOS_A_B) AS 'Valor',
   	tec.DATA AS 'Data',
    cast(date_format(cast(tec.DATA AS date), '%Y-%m-01') AS date) AS 'Primeiro_Dia_Mes'
  FROM T_EVENTOS_CMV tec 
  LEFT JOIN T_EMPRESAS te ON tec.FK_EMPRESA = te.ID 
  WHERE tec.DATA BETWEEN '{data_inicio}' AND '{data_fim}'
  GROUP BY te.ID
  ''')


@st.cache_data
def GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_SEM_PEDIDO():
  return dataframe_query(f'''
    WITH subquery AS (
    SELECT
      tdr.ID AS tdr_ID,
      te.ID AS ID_Loja,
      te.NOME_FANTASIA AS Loja,
      CAST(DATE_FORMAT(CAST(tdr.COMPETENCIA AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes,
      tdr.VALOR_PAGAMENTO AS Valor,
      tccg2.DESCRICAO AS Class_Cont_Grupo_2
    FROM
      T_DESPESA_RAPIDA tdr
    JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID
    LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID
    LEFT JOIN T_ASSOCIATIVA_PLANO_DE_CONTAS tapdc ON tccg2.ID = tapdc.FK_CLASSIFICACAO_GRUPO_2
    LEFT JOIN T_DESPESA_STATUS tds ON tdr.ID = tds.FK_DESPESA_RAPIDA
    LEFT JOIN T_STATUS ts ON tds.FK_STATUS_NAME = ts.ID
    LEFT JOIN T_STATUS_PAGAMENTO tsp2 ON ts.FK_STATUS_PAGAMENTO = tsp2.ID
    WHERE
      tdr.FK_DESPESA_TEKNISA IS NULL
      AND tccg.ID IN (162, 205, 236)
      AND NOT EXISTS (
        SELECT 1
        FROM T_DESPESA_RAPIDA_ITEM tdri
        WHERE tdri.FK_DESPESA_RAPIDA = tdr.ID
      )
    GROUP BY
      tdr.ID,
      te.ID,
      tccg2.DESCRICAO,
      CAST(DATE_FORMAT(CAST(tdr.COMPETENCIA AS DATE), '%Y-%m-01') AS DATE)
  )
  SELECT
    ID_Loja,
    Loja,
    Primeiro_Dia_Mes,
    SUM(Valor) AS BlueMe_Sem_Pedido_Valor,
    SUM(CASE
      WHEN Class_Cont_Grupo_2 IN ('ALIMENTOS', 'Insumos - Alimentos') THEN Valor
      ELSE 0
    END) AS BlueMe_Sem_Pedido_Alimentos,
    SUM(CASE
      WHEN Class_Cont_Grupo_2 IN ('BEBIDAS', 'Insumos - Bebidas') THEN Valor
      ELSE 0
    END) AS BlueMe_Sem_Pedido_Bebidas,
    SUM(CASE
      WHEN Class_Cont_Grupo_2 IN ('EMBALAGENS', 'Insumos - Embalagens') THEN Valor
      ELSE 0
      END) AS BlueMe_Sem_Pedido_Descart_Hig_Limp,
    SUM(CASE
      WHEN Class_Cont_Grupo_2 NOT IN ('ALIMENTOS', 'Insumos - Alimentos', 'BEBIDAS', 'Insumos - Bebidas', 'EMBALAGENS', 'Insumos - Embalagens') THEN Valor
      ELSE 0
      END) AS BlueMe_Sem_Pedido_Outros
  FROM subquery
  GROUP BY
    ID_Loja,
    Primeiro_Dia_Mes
  ORDER BY
    ID_Loja,
    Primeiro_Dia_Mes;
''')


@st.cache_data
def GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_COM_PEDIDO():
  return dataframe_query(f'''
  select
    vibmcp.ID_Loja AS ID_Loja,
    vibmcp.Loja AS Loja,
    vibmcp.Primeiro_Dia_Mes AS Primeiro_Dia_Mes,
    sum(vibmcp.Valor_Liquido) AS BlueMe_Com_Pedido_Valor_Liquido,
    sum(vibmcp.Valor_Insumos) AS BlueMe_Com_Pedido_Valor_Insumos,
    sum(vibmcp.Valor_Liq_Alimentos) AS BlueMe_Com_Pedido_Valor_Liq_Alimentos,
    sum(vibmcp.Valor_Liq_Bebidas) AS BlueMe_Com_Pedido_Valor_Liq_Bebidas,
    sum(vibmcp.Valor_Liq_Descart_Hig_Limp) AS BlueMe_Com_Pedido_Valor_Liq_Descart_Hig_Limp,
    sum(vibmcp.Valor_Liq_Outros) AS BlueMe_Com_Pedido_Valor_Liq_Outros
  from
    View_Insumos_BlueMe_Com_Pedido vibmcp
  group by
    vibmcp.ID_Loja,
    vibmcp.Primeiro_Dia_Mes
  order by
    vibmcp.ID_Loja,
    vibmcp.Primeiro_Dia_Mes;
''')



@st.cache_data
def GET_TRANSF_ESTOQUE():
  return dataframe_query(f'''
  SELECT
    tti.ID as 'ID_Transferencia',
    te.ID as 'ID_Loja_Saida',
    te.NOME_FANTASIA as 'Casa_Saida',
    te2.ID as 'ID_Loja_Entrada',
    te2.NOME_FANTASIA as 'Casa_Entrada',
    tti.DATA_TRANSFERENCIA as 'Data_Transferencia',
    tin5.ID as 'ID_Insumo_Nivel_5',
    tin5.DESCRICAO as 'Insumo_Nivel_5',
    tin.DESCRICAO as 'Categoria',
    tti.QUANTIDADE as 'Quantidade',
    tudm.UNIDADE_MEDIDA_NAME as 'Unidade_Medida',
    tti.VALOR_TRANSFERENCIA as 'Valor_Transferencia',
    tti.OBSERVACAO as 'Observacao'
  FROM T_TRANSFERENCIAS_INSUMOS tti 
    LEFT JOIN T_EMPRESAS te ON (tti.FK_EMRPESA_SAIDA = te.ID)
    LEFT JOIN T_EMPRESAS te2 ON tti.FK_EMPRESA_ENTRADA = te2.ID
    LEFT JOIN T_INSUMOS_NIVEL_5 tin5 ON tti.FK_INSUMO_NIVEL_5 = tin5.ID
    LEFT JOIN T_INSUMOS_NIVEL_4 tin4 ON tin5.FK_INSUMOS_NIVEL_4 = tin4.ID 
    LEFT JOIN T_INSUMOS_NIVEL_3 tin3 ON tin4.FK_INSUMOS_NIVEL_3 = tin3.ID 
    LEFT JOIN T_INSUMOS_NIVEL_2 tin2 ON tin3.FK_INSUMOS_NIVEL_2 = tin2.ID 
    LEFT JOIN T_INSUMOS_NIVEL_1 tin ON tin2.FK_INSUMOS_NIVEL_1 = tin.id
    LEFT JOIN T_UNIDADES_DE_MEDIDAS tudm ON (tin5.FK_UNIDADE_MEDIDA = tudm.ID)
  ORDER BY tti.ID DESC
''')


@st.cache_data
def GET_PERDAS_E_CONSUMO_AGRUPADOS():
  return dataframe_query(f'''
  WITH vpec AS (
    SELECT
      tpecc.ID AS Perdas_ID,
      tl.ID AS ID_Loja,
      tl.NOME_FANTASIA AS Loja,
      tpecc.DATA_BAIXA AS Data_Baixa,        
      CASE
        WHEN tpecc.FK_MOTIVO = 106 THEN tpecc.VALOR
        ELSE 0
      END AS Consumo_Interno,
      CASE
        WHEN tpecc.FK_MOTIVO <> 106 THEN tpecc.VALOR
        ELSE 0
      END AS Quebras_e_Perdas,
      CAST(DATE_FORMAT(CAST(tpecc.DATA_BAIXA AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes
    FROM
      T_PERDAS_E_CONSUMO_CONSOLIDADOS tpecc
    JOIN T_EMPRESAS tl ON tpecc.FK_EMPRESA = tl.ID
  )
  SELECT
    vpec.ID_Loja,
    vpec.Loja,
    vpec.Primeiro_Dia_Mes,
    SUM(vpec.Consumo_Interno) AS Consumo_Interno,
    SUM(vpec.Quebras_e_Perdas) AS Quebras_e_Perdas
  FROM vpec
  GROUP BY
    vpec.ID_Loja,
    vpec.Primeiro_Dia_Mes
  ORDER BY
    vpec.ID_Loja,
    vpec.Primeiro_Dia_Mes;
''')

  

@st.cache_data
def GET_INSUMOS_BLUE_ME_COM_PEDIDO():
  return dataframe_query(f'''
  SELECT
    vbmcp.tdr_ID AS tdr_ID,
    vbmcp.ID_Loja AS ID_Loja,
    vbmcp.Loja AS Loja,
    vbmcp.Fornecedor AS Fornecedor,
    vbmcp.Doc_Serie AS Doc_Serie,
    vbmcp.Data_Emissao AS Data_Emissao,
    vbmcp.Valor_Liquido AS Valor_Liquido,
    vbmcp.Valor_Insumos AS Valor_Cotacao,
    CAST(DATE_FORMAT(CAST(vbmcp.Data_Emissao AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Alimentos / virapc.Valor_Total_Insumos)), 2) AS Valor_Liq_Alimentos,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Bebidas / virapc.Valor_Total_Insumos)), 2) AS Valor_Liq_Bebidas,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Descartaveis_Higiene_Limpeza / virapc.Valor_Total_Insumos)), 2) AS Valor_Liq_Descart_Hig_Limp,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Gelo_Gas_Carvao_Velas / virapc.Valor_Total_Insumos)), 2) AS Valor_Gelo_Gas_Carvao_Velas,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Utensilios / virapc.Valor_Total_Insumos)), 2) AS Valor_Utensilios,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Outros / virapc.Valor_Total_Insumos)), 2) AS Valor_Liq_Outros
  FROM
    View_BlueMe_Com_Pedido vbmcp
  LEFT JOIN View_Insumos_Receb_Agrup_Por_Categ virapc ON
    vbmcp.tdr_ID = virapc.tdr_ID
''')


 

@st.cache_data
def GET_INSUMOS_BLUE_ME_SEM_PEDIDO():
  return dataframe_query(f'''
  SELECT
    subquery.tdr_ID AS tdr_ID,
    subquery.ID_Loja AS ID_Loja,
    subquery.Loja AS Loja,
    subquery.Fornecedor AS Fornecedor,
    subquery.Doc_Serie AS Doc_Serie,
    subquery.Data_Emissao AS Data_Emissao,
    subquery.Valor AS Valor,
    subquery.Plano_de_Contas AS Plano_de_Contas,
    subquery.Primeiro_Dia_Mes AS Primeiro_Dia_Mes
  FROM
    (
    SELECT
      tdr.ID AS tdr_ID,
      te.ID AS ID_Loja,
      te.NOME_FANTASIA AS Loja,
      tf.CORPORATE_NAME AS Fornecedor,
      tdr.NF AS Doc_Serie,
      tdr.COMPETENCIA AS Data_Emissao,
      tdr.VENCIMENTO AS Data_Vencimento,
      tccg2.DESCRICAO AS Class_Cont_Grupo_2,
      tccg.DESCRICAO AS Class_Cont_Grupo_1,
      tdr.OBSERVACAO AS Observacao,
      tdr.VALOR_PAGAMENTO AS Valor,
      tccg2.DESCRICAO AS Plano_de_Contas,
      tsp2.DESCRICAO AS Status,
      CAST(DATE_FORMAT(CAST(tdr.COMPETENCIA AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes,
      ROW_NUMBER() OVER (PARTITION BY tdr.ID
      ORDER BY
        tds.ID DESC) AS row_num
    FROM
      T_DESPESA_RAPIDA tdr
    JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID
    LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON tdr.FK_FORMA_PAGAMENTO = tfdp.ID
    LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID
    LEFT JOIN T_STATUS_CONFERENCIA_DOCUMENTACAO tscd ON tdr.FK_CONFERENCIA_DOCUMENTACAO = tscd.ID
    LEFT JOIN T_STATUS_APROVACAO_DIRETORIA tsad ON tdr.FK_APROVACAO_DIRETORIA = tsad.ID
    LEFT JOIN T_STATUS_APROVACAO_CAIXA tsac ON tdr.FK_APROVACAO_CAIXA = tsac.ID
    LEFT JOIN T_STATUS_PAGAMENTO tsp ON tdr.FK_STATUS_PGTO = tsp.ID
    LEFT JOIN T_CALENDARIO tc ON tdr.PREVISAO_PAGAMENTO = tc.ID
    LEFT JOIN T_CALENDARIO tc2 ON tdr.FK_DATA_REALIZACAO_PGTO = tc2.ID
    LEFT JOIN T_TEKNISA_CONTAS_A_PAGAR ttcap ON tdr.FK_DESPESA_TEKNISA = ttcap.ID
    LEFT JOIN T_DESPESA_RAPIDA_ITEM tdri ON tdr.ID = tdri.FK_DESPESA_RAPIDA
    LEFT JOIN T_DESPESA_STATUS tds ON tdr.ID = tds.FK_DESPESA_RAPIDA
    LEFT JOIN T_STATUS ts ON tds.FK_STATUS_NAME = ts.ID
    LEFT JOIN T_STATUS_PAGAMENTO tsp2 ON ts.FK_STATUS_PAGAMENTO = tsp2.ID
    WHERE
      tdri.ID IS NULL
      AND tdr.FK_DESPESA_TEKNISA IS NULL
      AND tccg.ID IN (162, 205, 236)
    ) subquery
  WHERE
    subquery.row_num = 1;
''')



def GET_VALORACAO_PRODUCAO(data):
  return dataframe_query(f'''
  SELECT
    te.ID as 'ID_Loja',
    te.NOME_FANTASIA as 'Loja',
    tipc.DATA_CONTAGEM as 'Data_Contagem',
    DATE_FORMAT(DATE_SUB(tipc.DATA_CONTAGEM, INTERVAL 1 MONTH), '%m/%Y') AS 'Mes_Texto',
    tip.NOME_ITEM_PRODUZIDO as 'Item_Produzido',
    tudm.UNIDADE_MEDIDA_NAME as 'Unidade_Medida',
    tipc.QUANTIDADE_INSUMO as 'Quantidade',
    tin.DESCRICAO as 'Categoria',
    tipv.VALOR as 'Valor_Unidade_Medida',
    ROUND(tipc.QUANTIDADE_INSUMO * tipv.VALOR, 2) as 'Valor_Total'
  FROM T_ITENS_PRODUCAO_CONTAGEM tipc
  LEFT JOIN T_ITENS_PRODUCAO_VALORACAO tipv ON (tipc.FK_ITEM_PRODUZIDO = tipv.FK_ITEM_PRODUZIDO) AND (DATE_FORMAT(tipc.DATA_CONTAGEM, '%m/%Y') = DATE_FORMAT(tipv.DATA_VALORACAO, '%m/%Y'))
  LEFT JOIN T_ITENS_PRODUCAO tip ON (tipv.FK_ITEM_PRODUZIDO = tip.ID)
  LEFT JOIN T_EMPRESAS te ON (tip.FK_EMPRESA = te.ID)
  LEFT JOIN T_INSUMOS_NIVEL_1 tin ON (tip.FK_INSUMO_NIVEL_1 = tin.ID)
  LEFT JOIN T_UNIDADES_DE_MEDIDAS tudm ON (tip.FK_UNIDADE_MEDIDA = tudm.ID)
  WHERE tipc.DATA_CONTAGEM = '{data}'
  ''')




######################## PARETO ##############################




#Essa query está com um problema: O fator de proporção. Ele estava em outra tabela, a qual foi descontinuada para a criação de duas: T_INSUMOS_ESTOQUE 
# E T_ASSOCIATIVA_COMPRA_ESTOQUE. Ainda não foi feita a migração dos dados para essas tabelas, então a query não está funcionando.
# Nas tabelas, o que está errado por conta do fator de proporção é o "Valor unitário" e tudo relacionado a ele.
@st.cache_data
def GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA():
  return dataframe_query(f'''
  SELECT 	
  	tin4.ID AS 'ID Produto Nivel 4',	
  	te.NOME_FANTASIA AS 'Loja', 
  	tf.FANTASY_NAME AS 'Fornecedor', 
  	tin4.DESCRICAO AS 'Nome Produto', 
	  tin.DESCRICAO AS 'Categoria',
  	CAST(REPLACE(tdri.QUANTIDADE, ',', '.') AS DECIMAL(10, 2)) AS 'Quantidade',
  	tdri.UNIDADE_MEDIDA AS 'Unidade de Medida',
  	tdri.VALOR AS 'Valor Total', 
    (tdri.VALOR / (CAST(REPLACE(tdri.QUANTIDADE, ',', '.') AS DECIMAL(10, 2)))) AS 'Valor Unitário',
  	tdr.COMPETENCIA AS 'Data Compra',
  	1 AS 'Fator de Proporção'
  FROM T_DESPESA_RAPIDA_ITEM tdri
  LEFT JOIN T_INSUMOS_NIVEL_5 tin5 ON tdri.FK_INSUMO = tin5.ID
  LEFT JOIN T_INSUMOS_NIVEL_4 tin4 ON tin5.FK_INSUMOS_NIVEL_4 = tin4.ID 
  LEFT JOIN T_INSUMOS_NIVEL_3 tin3 ON tin4.FK_INSUMOS_NIVEL_3 = tin3.ID 
  LEFT JOIN T_INSUMOS_NIVEL_2 tin2 ON tin3.FK_INSUMOS_NIVEL_2 = tin2.ID 
  LEFT JOIN T_INSUMOS_NIVEL_1 tin ON tin2.FK_INSUMOS_NIVEL_1 = tin.id
  LEFT JOIN T_DESPESA_RAPIDA tdr ON tdri.FK_DESPESA_RAPIDA = tdr.ID 
  LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID 
  LEFT JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID 
  WHERE tdr.COMPETENCIA > '2024-01-01'
''')
  


def GET_COMPRAS_PRODUTOS_COM_RECEBIMENTO(data_inicio, data_fim, categoria):
  return dataframe_query(f'''
  SELECT 	
  	tin4.ID AS 'ID Produto Nivel 4',
  	tin4.DESCRICAO AS 'Nome Produto', 
	  tin.DESCRICAO AS 'Categoria',
  	te.NOME_FANTASIA AS 'Loja', 
  	tf.FANTASY_NAME AS 'Fornecedor', 
  	tdr.COMPETENCIA AS 'Data Compra',
  	CAST(REPLACE(tdri.QUANTIDADE, ',', '.') AS DECIMAL(10, 2)) AS 'Quantidade',
  	tdri.UNIDADE_MEDIDA AS 'Unidade de Medida',
  	tdri.VALOR AS 'Valor Total', 
    (tdri.VALOR / (CAST(REPLACE(tdri.QUANTIDADE, ',', '.') AS DECIMAL(10, 2)))) AS 'Valor Unitário',
  	tps.DATA AS 'Data_Recebida'
  FROM T_DESPESA_RAPIDA_ITEM tdri
  LEFT JOIN T_INSUMOS_NIVEL_5 tin5 ON tdri.FK_INSUMO = tin5.ID
  LEFT JOIN T_INSUMOS_NIVEL_4 tin4 ON tin5.FK_INSUMOS_NIVEL_4 = tin4.ID 
  LEFT JOIN T_INSUMOS_NIVEL_3 tin3 ON tin4.FK_INSUMOS_NIVEL_3 = tin3.ID 
  LEFT JOIN T_INSUMOS_NIVEL_2 tin2 ON tin3.FK_INSUMOS_NIVEL_2 = tin2.ID 
  LEFT JOIN T_INSUMOS_NIVEL_1 tin ON tin2.FK_INSUMOS_NIVEL_1 = tin.id
  LEFT JOIN T_DESPESA_RAPIDA tdr ON tdri.FK_DESPESA_RAPIDA = tdr.ID 
  LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID 
  LEFT JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID 
  LEFT JOIN T_PEDIDOS tp ON tp.ID = tdr.FK_PEDIDO
  LEFT JOIN T_PEDIDO_STATUS tps ON tps.FK_PEDIDO = tp.ID
  WHERE tdr.COMPETENCIA >= '{data_inicio}'
    AND tdr.COMPETENCIA <= '{data_fim}'
    AND tin.DESCRICAO = '{categoria}'
  GROUP BY 
    tin5.ID,
    tdr.COMPETENCIA
  ORDER BY
    tdr.COMPETENCIA DESC
  ''')


#################################### FLUXO DE CAIXA ########################################


def GET_SALDOS_BANCARIOS():
  return dataframe_query(f"""
SELECT * FROM View_Saldos_Bancarios
WHERE Data >= CURDATE() 
AND Data < DATE_ADD(CURDATE(), INTERVAL 14 DAY)
AND Empresa IS NOT NULL
ORDER BY Data ASC
""")


def GET_VALOR_LIQUIDO_RECEBIDO():
  return dataframe_query(f'''
SELECT
  tc.DATA AS Data,
  te.NOME_FANTASIA AS Empresa,
  sum(trem.VALOR_RECEBIDO) AS Valor_Liquido_Recebido
FROM
  T_CALENDARIO tc
LEFT JOIN T_RECEITAS_EXTRATOS_MANUAL trem on
  tc.DATA = trem.DATA
LEFT JOIN T_EMPRESAS te on
  trem.FK_LOJA = te.ID
WHERE tc.DATA >= CURDATE() 
	AND tc.DATA < DATE_ADD(CURDATE(), INTERVAL 14 DAY)
	AND te.NOME_FANTASIA IS NOT NULL
GROUP BY
  te.NOME_FANTASIA,
  tc.DATA
ORDER BY tc.DATA ASC;
''')

def GET_PROJECAO_ZIG():
  return dataframe_query(f'''
SELECT * FROM View_Projecao_Zig_Agrupadas
WHERE Data >= CURDATE() 
AND Data < DATE_ADD(CURDATE(), INTERVAL 14 DAY)
AND Empresa IS NOT NULL
ORDER BY Data ASC
''')



def GET_RECEITAS_EXTRAORD_FLUXO_CAIXA():
  return dataframe_query(f'''
    SELECT
      tc.DATA AS Data,
      te.NOME_FANTASIA AS Empresa,
      SUM(parcelas.VALOR_PARCELA) AS Receita_Projetada_Extraord
    FROM
        T_CALENDARIO tc
    LEFT JOIN (
        -- Subquery unificada de parcelas e eventos
        SELECT CONCAT('R-', vpa.ID) AS ID_UNIFICADO,	
              vpa.FK_EMPRESA,
              vpa.FK_CLIENTE,
              vpa.DATA_VENCIMENTO,
              vpa.DATA_RECEBIMENTO,
              vpa.VALOR_PARCELA
        FROM View_Parcelas_Agrupadas vpa

        UNION ALL

        SELECT CONCAT('E-', tep.ID) AS ID_UNIFICADO,
              te.ID AS FK_EMPRESA,
              trec.ID AS FK_CLIENTE,
              tpep.DATA_VENCIMENTO_PARCELA AS DATA_VENCIMENTO,
              tpep.DATA_RECEBIMENTO_PARCELA AS DATA_RECEBIMENTO,
              tpep.VALOR_PARCELA
        FROM T_PARCELAS_EVENTOS_PRICELESS tpep
        LEFT JOIN T_EVENTOS_PRICELESS tep ON tep.ID = tpep.FK_EVENTO_PRICELESS
        LEFT JOIN T_EMPRESAS te ON te.ID = tep.FK_EMPRESA
        LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec ON trec.ID = tep.FK_CLIENTE
    ) AS parcelas ON tc.DATA = parcelas.DATA_VENCIMENTO
    LEFT JOIN T_EMPRESAS te ON parcelas.FK_EMPRESA = te.ID
    WHERE
        parcelas.DATA_VENCIMENTO IS NOT NULL
        AND parcelas.DATA_RECEBIMENTO IS NULL
        AND tc.DATA >= CURDATE() 
        AND tc.DATA < DATE_ADD(CURDATE(), INTERVAL 14 DAY)
        AND te.NOME_FANTASIA IS NOT NULL
    GROUP BY
        te.NOME_FANTASIA,
        parcelas.DATA_VENCIMENTO
    ORDER BY
        te.NOME_FANTASIA,
        parcelas.DATA_VENCIMENTO,
        Data ASC;
''')


def GET_RECEITAS_EXTRAORD_DO_DIA(data):
  return dataframe_query(f'''
  SELECT 
    vpa.ID AS ID_Receita_Extraordinária,
    te.NOME_FANTASIA AS Empresa,
    trec.NOME AS Nome_Cliente,
    vpa.OBSERVACOES AS Observações,
    trec2.CLASSIFICACAO AS Classificação,
    vpa.DATA_VENCIMENTO AS Data_Vencimento_Parcela,
    vpa.VALOR_PARCELA AS Valor_Parcela
FROM (
    SELECT
        tre.ID,
        tre.FK_EMPRESA,
        tre.FK_CLIENTE,
        tre.OBSERVACOES,
        tre.FK_CLASSIFICACAO,
        tre.DATA_VENCIMENTO_PARCELA_1 AS DATA_VENCIMENTO,
        tre.DATA_RECEBIMENTO_PARCELA_1 AS DATA_RECEBIMENTO,
        tre.VALOR_PARCELA_1 AS VALOR_PARCELA
    FROM T_RECEITAS_EXTRAORDINARIAS tre
    UNION ALL
    SELECT
        tre.ID,
        tre.FK_EMPRESA,
        tre.FK_CLIENTE,
        tre.OBSERVACOES,
        tre.FK_CLASSIFICACAO,
        tre.DATA_VENCIMENTO_PARCELA_2 AS DATA_VENCIMENTO,
        tre.DATA_RECEBIMENTO_PARCELA_2 AS DATA_RECEBIMENTO,
        tre.VALOR_PARCELA_2 AS VALOR_PARCELA
    FROM T_RECEITAS_EXTRAORDINARIAS tre
    UNION ALL
    SELECT
        tre.ID,
        tre.FK_EMPRESA,
        tre.FK_CLIENTE,
        tre.OBSERVACOES,
        tre.FK_CLASSIFICACAO,
        tre.DATA_VENCIMENTO_PARCELA_3 AS DATA_VENCIMENTO,
        tre.DATA_RECEBIMENTO_PARCELA_3 AS DATA_RECEBIMENTO,
        tre.VALOR_PARCELA_3 AS VALOR_PARCELA
    FROM T_RECEITAS_EXTRAORDINARIAS tre
    UNION ALL
    SELECT
        tre.ID,
        tre.FK_EMPRESA,
        tre.FK_CLIENTE,
        tre.OBSERVACOES,
        tre.FK_CLASSIFICACAO,
        tre.DATA_VENCIMENTO_PARCELA_4 AS DATA_VENCIMENTO,
        tre.DATA_RECEBIMENTO_PARCELA_4 AS DATA_RECEBIMENTO,
        tre.VALOR_PARCELA_4 AS VALOR_PARCELA
    FROM T_RECEITAS_EXTRAORDINARIAS tre
    UNION ALL
    SELECT
        tre.ID,
        tre.FK_EMPRESA,
        tre.FK_CLIENTE,
        tre.OBSERVACOES,
        tre.FK_CLASSIFICACAO,
        tre.DATA_VENCIMENTO_PARCELA_5 AS DATA_VENCIMENTO,
        tre.DATA_RECEBIMENTO_PARCELA_5 AS DATA_RECEBIMENTO,
        tre.VALOR_PARCELA_5 AS VALOR_PARCELA
    FROM T_RECEITAS_EXTRAORDINARIAS tre
) AS vpa
LEFT JOIN T_EMPRESAS te ON vpa.FK_EMPRESA = te.ID
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec ON vpa.FK_CLIENTE = trec.ID
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLASSIFICACAO trec2 ON vpa.FK_CLASSIFICACAO = trec2.ID 
WHERE
    vpa.DATA_VENCIMENTO IS NOT NULL
    AND vpa.DATA_RECEBIMENTO IS NULL
    AND te.NOME_FANTASIA IS NOT NULL

UNION ALL

SELECT 
    CONCAT('E-', tep.ID) AS ID_Receita_Extraordinária,
    te.NOME_FANTASIA AS Empresa,
    trec.NOME AS Nome_Cliente,
    tep.OBSERVACOES AS Observações,
    'Eventos' AS Classificação,
    tpep.DATA_VENCIMENTO_PARCELA AS Data_Vencimento_Parcela,
    tpep.VALOR_PARCELA AS Valor_Parcela
FROM T_PARCELAS_EVENTOS_PRICELESS tpep
LEFT JOIN T_EVENTOS_PRICELESS tep ON tep.ID = tpep.FK_EVENTO_PRICELESS
LEFT JOIN T_EMPRESAS te ON te.ID = tep.FK_EMPRESA
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec ON tep.FK_CLIENTE = trec.ID
WHERE
    tpep.DATA_VENCIMENTO_PARCELA IS NOT NULL
    AND tpep.DATA_RECEBIMENTO_PARCELA IS NULL 
    AND te.NOME_FANTASIA IS NOT NULL;
''')


def GET_DESPESAS_APROVADAS():
  return dataframe_query(f'''
SELECT
vvap.Empresa as 'Empresa',
vvap.Data as 'Data',
SUM(vvap.Valores_Aprovados_Previsao) as 'Despesas_Aprovadas_Pendentes' 
FROM View_Valores_Aprovados_Previsao vvap
WHERE Data >= CURDATE() 
AND Data < DATE_ADD(CURDATE(), INTERVAL 14 DAY)
AND Empresa IS NOT NULL
GROUP BY Data, Empresa  
ORDER BY Data ASC
''')

def GET_DESPESAS_PAGAS():
  return dataframe_query(f'''
SELECT
vvap.Empresa as 'Empresa',
vvap.Data as 'Data',
SUM(vvap.Valores_Pagos) as 'Despesas_Pagas' 
FROM View_Valores_Pagos_por_Previsao vvap
WHERE Data >= CURDATE() 
AND Data < DATE_ADD(CURDATE(), INTERVAL 14 DAY)
AND Empresa IS NOT NULL
GROUP BY Data, Empresa  
ORDER BY Data ASC
''')


def GET_LOJAS():
  return dataframe_query(f'''
SELECT
te.ID as 'ID_Loja',
te.NOME_FANTASIA as 'Loja'
FROM T_EMPRESAS te
''')


def GET_DESPESAS_PENDENTES(dataInicio, dataFim):
  # Formatando as datas para o formato de string com aspas simples
  dataStr = f"'{dataInicio.strftime('%Y-%m-%d %H:%M:%S')}'"
  datafimstr = f"'{dataFim.strftime('%Y-%m-%d %H:%M:%S')}'"
######### NA PARTE DAS DESPESAS PARCELADAS, HÁ NA VIEW DO GABS UMA APROVAÇÃO DA DIRETORIA QUE PODE DAR DIFERENÇA #########
  return dataframe_query(f'''
  SELECT
    DATE_FORMAT(tc.DATA, '%Y-%m-%d') as 'Previsao_Pgto',
    tdr.VENCIMENTO AS 'Data_Vencimento',
    tdr.ID as 'ID_Despesa',
    "Nulo" as 'ID_Parcela',
    te.NOME_FANTASIA as 'Loja',
    tf.FANTASY_NAME as 'Fornecedor',
    tdr.VALOR_LIQUIDO as 'Valor',
    "Falso" as 'Parcelamento',
    CASE
        WHEN tdr.FK_STATUS_PGTO = 103 THEN 'Pago'
        ELSE 'Pendente'
    END as 'Status_Pgto'
  FROM T_DESPESA_RAPIDA tdr 
  INNER JOIN T_EMPRESAS te ON (tdr.FK_LOJA = te.ID)
  INNER JOIN T_FORNECEDOR tf ON (tdr.FK_FORNECEDOR = tf.ID)
  LEFT JOIN T_CALENDARIO tc ON (tdr.PREVISAO_PAGAMENTO = tc.ID)
  LEFT JOIN T_DEPESA_PARCELAS tdp ON (tdp.FK_DESPESA = tdr.ID)
  WHERE tdp.ID is NULL 
    AND tc.DATA >= {dataStr}
    AND tc.DATA <= {datafimstr}
  UNION ALL
  SELECT
    DATE_FORMAT(tc.DATA, '%Y-%m-%d') as 'Previsao_Pgto',
    tdr.VENCIMENTO AS 'Data_Vencimento',
    tdr.ID as 'ID_Despesa',
    tdp.ID as 'ID_Parcela',
    te.NOME_FANTASIA as 'Loja',
    tf.FANTASY_NAME as 'Fornecedor',
    tdp.VALOR as 'Valor',
    "True" as 'Parcelamento',
    CASE
        WHEN tdp.PARCELA_PAGA = 1 THEN 'Pago'
        ELSE 'Pendente'
    END as 'Status_Pgto'
  FROM T_DESPESA_RAPIDA tdr 
  LEFT JOIN T_EMPRESAS te ON (tdr.FK_LOJA = te.ID)
  LEFT JOIN T_FORNECEDOR tf ON (tdr.FK_FORNECEDOR = tf.ID)
  LEFT JOIN T_DEPESA_PARCELAS tdp ON (tdp.FK_DESPESA = tdr.ID)
  LEFT JOIN T_CALENDARIO tc ON (tdp.FK_PREVISAO_PGTO = tc.ID)
  WHERE tdp.ID is NOT NULL 
    AND tc.DATA >= {dataStr}
    AND tc.DATA <= {datafimstr}
''')

###########################  Previsão Faturamento  #############################


def GET_PREVISOES_ZIG_AGRUPADAS():
  return dataframe_query(f'''
  SELECT
    te.NOME_FANTASIA AS Empresa,
    tzf.DATA AS Data,
    SUM(tzf.VALOR) AS Valor
  FROM
    T_ZIG_FATURAMENTO tzf
    LEFT JOIN T_EMPRESAS te ON tzf.FK_LOJA = te.ID
  WHERE
    tzf.DATA >= '2023-08-01 00:00:00'
    AND tzf.VALOR > 0
  GROUP BY
    Data,
    Empresa
  ORDER BY
    Data,
    Empresa;
''')



def GET_FATURAMENTO_REAL():
  return dataframe_query(f'''
  SELECT
	  te.NOME_FANTASIA as 'Loja',
	  tzf.DATA as 'Data',
	  SUM(tzf.VALOR) as 'Valor_Faturado' 
	FROM T_ZIG_FATURAMENTO tzf 
	INNER JOIN T_EMPRESAS te ON (tzf.FK_LOJA = te.ID)
	GROUP BY te.ID, tzf.DATA
''')