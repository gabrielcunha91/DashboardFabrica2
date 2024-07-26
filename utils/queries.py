import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import mysql.connector

LOGGER = get_logger(__name__)

def mysql_connection():
  mysql_config = st.secrets["mysql"]
  # Cria a conexão com MySQL
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
	  au.LOGIN AS 'Login',
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

# @st.cache_data
# def GET_FATURAM_ZIG_AGREGADO():
#   return dataframe_query(f''' 
#   SELECT
#     tl.ID AS ID_Loja,
#     tl.NOME AS Loja,
#     tfza.CATEGORIA AS Categoria,
#     cast(tfza.DATA_EVENTO as date) AS Data_Evento,
#     cast(date_format(cast(tfza.DATA_EVENTO as date), '%Y-%m-01') as date) AS Primeiro_Dia_Mes,
#     concat(year(cast(tfza.DATA_EVENTO as date)), '-', month(cast(tfza.DATA_EVENTO as date))) AS Ano_Mes,
#     sum(tfza.VALOR_TRANSACAO_BRUTO) AS Valor_Bruto,
#     sum(tfza.DESCONTO) AS Desconto,
#     sum(tfza.VALOR_TRANSACAO_LIQUIDO) AS Valor_Liquido
#   FROM
#     T_FATURAMENTO_ZIG_AGREGADO tfza
#   JOIN 
#     T_LOJAS tl ON tfza.ID_LOJA = tl.ID
#   GROUP BY
#     tfza.ID_LOJA,
#     Categoria,
#     Primeiro_Dia_Mes
#   ORDER BY
#     Primeiro_Dia_Mes,
#     Loja,
#     Categoria;
#   ''')

@st.cache_data
def GET_FATURAM_ZIG_AGREGADO():
  return dataframe_query(f''' 
  SELECT
    te.ID AS ID_Loja,
    te.NOME_FANTASIA AS Loja,
    tfza.CATEGORIA AS Categoria,
    cast(tfza.DATA_EVENTO as date) AS Data_Evento,
    cast(date_format(cast(tfza.DATA_EVENTO as date), '%Y-%m-01') as date) AS Primeiro_Dia_Mes,
    concat(year(cast(tfza.DATA_EVENTO as date)), '-', month(cast(tfza.DATA_EVENTO as date))) AS Ano_Mes,
    sum(tfza.VALOR_TRANSACAO_BRUTO) AS Valor_Bruto,
    sum(tfza.DESCONTO) AS Desconto,
    sum(tfza.VALOR_TRANSACAO_LIQUIDO) AS Valor_Liquido
  FROM
    T_FATURAMENTO_ZIG_AGREGADO tfza
  JOIN 
    T_EMPRESAS te ON tfza.ID_LOJA = te.ID 
  GROUP BY
    tfza.ID_LOJA,
    Categoria,
    Primeiro_Dia_Mes
  ORDER BY
    Primeiro_Dia_Mes,
    Loja,
    Categoria;
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
      WHEN tccg.DESCRICAO = 'VENDA DE ALIMENTO' THEN 'Alimentos'
      WHEN tccg.DESCRICAO = 'VENDA DE BEBIDAS' THEN 'Bebidas'
      WHEN tccg.DESCRICAO = 'VENDA DE COUVERT/ SHOWS' THEN 'Couvert'
      WHEN tccg.DESCRICAO = 'SERVICO' THEN 'Serviço'
      WHEN tccg.DESCRICAO = 'DELIVERY' THEN 'Delivery'
      ELSE tccg.DESCRICAO
    END AS Categoria
  FROM
    T_ORCAMENTOS to2
  JOIN
    T_EMPRESAS te ON to2.FK_EMPRESA = te.ID
  JOIN
    T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg ON to2.FK_CLASSIFICACAO_2 = tccg.ID
  WHERE
    to2.FK_CLASSIFICACAO_1 = 178
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



############### Receitas extraordinárias ################

@st.cache_data
def GET_RECEIT_EXTRAORD():
  #'Data_Evento' é, na realidade, a data da competencia, eu só coloquei esse nome pra ficar mais fácil de programar
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

def GET_DESPESAS():
  #'Data_Evento' é, na realidade, a data da emissão, eu só coloquei esse nome pra ficar mais fácil de programar
  #Vai mudar com a Vmarket
  # Corrigir datas competencia e vencimento
  return dataframe_query(f'''
    SELECT 
      tdr.ID AS ID,
      te.NOME_FANTASIA AS Loja,
      tf.CORPORATE_NAME AS Fornecedor,
      tdr.NF AS Doc_Serie,
      STR_TO_DATE(tdr.COMPETENCIA, '%Y-%m-%d') AS Data_Evento,
      STR_TO_DATE(tdr.VENCIMENTO, '%Y-%m-%d') AS Data_Vencimento,
      tdr.OBSERVACAO AS Descricao,
      tdr.VALOR_LIQUIDO AS Valor_Liquido,
      tapdc.DESCRICAO_PLANO_DE_CONTAS AS Plano_de_Contas,
      tcpdc.DESCRICAO AS Class_Plano_de_Contas,
      to2.VALOR AS Orcamento,
      CASE 
          WHEN tdr.FK_Status = 'Provisionado' THEN 'Provisionado'
          ELSE 'Real'
      END AS Status
    FROM T_DESPESA_RAPIDA tdr
    JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID
    LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID
    LEFT JOIN T_ASSOCIATIVA_PLANO_DE_CONTAS tapdc ON tccg2.ID = tapdc.FK_CLASSIFICACAO_GRUPO_2
    LEFT JOIN T_CLASSIFICACAO_PLANO_DE_CONTAS tcpdc ON tapdc.FK_CLASSIFICACAO_PLANO_DE_CONTAS = tcpdc.ID
    LEFT JOIN T_ORCAMENTOS to2 ON tapdc.FK_CLASSIFICACAO_GRUPO_2 = to2.FK_CLASSIFICACAO_2 
      AND MONTH(CAST(tdr.COMPETENCIA AS DATE)) = to2.MES
      AND to2.FK_EMPRESA = te.ID
    WHERE tdr.FK_DESPESA_TEKNISA IS NULL
      AND tdr.COMPETENCIA >= '2024-01-01 00:00:00'
      AND tdr.VENCIMENTO >= '2024-01-01 00:00:00'
      AND NOT EXISTS (
        SELECT 1
        FROM T_DESPESA_RAPIDA_ITEM tdri
        WHERE tdri.FK_DESPESA_RAPIDA = tdr.ID);
''')


############################### CMV ###################################

@st.cache_data
def GET_FATURAM_ZIG_ALIM_BEB_MENSAL():
  return dataframe_query(f'''
  SELECT
    tfza.ID_LOJA AS ID_Loja,
    te.NOME_FANTASIA AS Loja,
    CAST(DATE_FORMAT(CAST(tfza.DATA_EVENTO AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes,
    SUM(CASE
      WHEN tfza.CATEGORIA = 'Alimentos' THEN ROUND(CAST(tfza.VALOR_TRANSACAO_BRUTO AS DECIMAL(10, 2)), 2)
      ELSE 0
    END) AS Faturam_Bruto_Aliment,
    SUM(CASE
      WHEN tfza.CATEGORIA = 'Bebidas' THEN ROUND(CAST(tfza.VALOR_TRANSACAO_BRUTO AS DECIMAL(10, 2)), 2)
      ELSE 0
    END) AS Faturam_Bruto_Bebidas
  FROM
    T_FATURAMENTO_ZIG_AGREGADO tfza
  JOIN 
    T_EMPRESAS te ON tfza.ID_LOJA = te.ID 
  GROUP BY
    tfza.ID_LOJA,
    Primeiro_Dia_Mes
  ORDER BY
    tfza.ID_LOJA,
    Primeiro_Dia_Mes;
''')


@st.cache_data
def GET_ESTOQUES_POR_CATEG_AGRUPADOS():
  return dataframe_query(f'''
SELECT
    te.ID AS ID_Loja,
    te.NOME_FANTASIA AS Loja,
    CAST(DATE_FORMAT(CAST(tvee.DATA_CONTAGEM AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes,
    LAST_DAY(CAST(DATE_FORMAT(CAST(tvee.DATA_CONTAGEM AS DATE), '%Y-%m-01') AS DATE)) AS Ultimo_Dia_Mes,
    SUM(CASE
      WHEN tin.DESCRICAO = 'ALIMENTOS' THEN tvee.VALOR_EM_ESTOQUE
      ELSE 0
    END) AS Estoque_Inicial_Alimentos,
    SUM(CASE
    WHEN tin.DESCRICAO = 'BEBIDAS' THEN tvee.VALOR_EM_ESTOQUE
    ELSE 0
    END) AS Estoque_Inicial_Bebidas,
    SUM(CASE
      WHEN tin.DESCRICAO = 'DESCARTAVEIS/ HIGIENE E LIMPEZA' THEN tvee.VALOR_EM_ESTOQUE
      ELSE 0
    END) AS Estoque_Inicial_Descart_Hig_Limp,
    SUM(CASE
      WHEN tin.DESCRICAO = 'ALIMENTOS' THEN (SELECT tvee2.VALOR_EM_ESTOQUE
                                            FROM T_VALOR_EM_ESTOQUE tvee2
                                            WHERE tvee2.FK_LOJA = tvee.FK_LOJA
                                              AND tvee2.FK_INSUMO_NIVEL_1 = tvee.FK_INSUMO_NIVEL_1
                                              AND DATE_FORMAT(CAST(tvee2.DATA_CONTAGEM AS DATE), '%Y-%m-01') = (LAST_DAY(CAST(DATE_FORMAT(CAST(tvee.DATA_CONTAGEM AS DATE), '%Y-%m-01') AS DATE)) + INTERVAL 1 DAY)
                                              LIMIT 1)
      ELSE 0
    END) AS Estoque_Final_Alimentos,
    SUM(CASE
      WHEN tin.DESCRICAO = 'BEBIDAS' THEN (SELECT tvee2.VALOR_EM_ESTOQUE
                                          FROM T_VALOR_EM_ESTOQUE tvee2
                                          WHERE tvee2.FK_LOJA = tvee.FK_LOJA
                                            AND tvee2.FK_INSUMO_NIVEL_1 = tvee.FK_INSUMO_NIVEL_1
                                            AND DATE_FORMAT(CAST(tvee2.DATA_CONTAGEM AS DATE), '%Y-%m-01') = (LAST_DAY(CAST(DATE_FORMAT(CAST(tvee.DATA_CONTAGEM AS DATE), '%Y-%m-01') AS DATE)) + INTERVAL 1 DAY)
                                            LIMIT 1)
      ELSE 0
    END) AS Estoque_Final_Bebidas,
    SUM(CASE
      WHEN tin.DESCRICAO = 'DESCARTAVEIS/ HIGIENE E LIMPEZA' THEN (SELECT tvee2.VALOR_EM_ESTOQUE
                                                                  FROM T_VALOR_EM_ESTOQUE tvee2
                                                                  WHERE tvee2.FK_LOJA = tvee.FK_LOJA
                                                                    AND tvee2.FK_INSUMO_NIVEL_1 = tvee.FK_INSUMO_NIVEL_1
                                                                    AND DATE_FORMAT(CAST(tvee2.DATA_CONTAGEM AS DATE), '%Y-%m-01') = (LAST_DAY(CAST(DATE_FORMAT(CAST(tvee.DATA_CONTAGEM AS DATE), '%Y-%m-01') AS DATE)) + INTERVAL 1 DAY)
                                                                    LIMIT 1)
           ELSE 0
    END) AS Estoque_Final_Descart_Hig_Limp
  FROM
    T_VALOR_EM_ESTOQUE tvee
    JOIN T_EMPRESAS te ON tvee.FK_LOJA = te.ID
    JOIN T_INSUMOS_NIVEL_1 tin ON tvee.FK_INSUMO_NIVEL_1 = tin.ID
  GROUP BY
    te.ID,
    te.NOME_FANTASIA ,
    Primeiro_Dia_Mes,
    LAST_DAY(CAST(DATE_FORMAT(CAST(tvee.DATA_CONTAGEM AS DATE), '%Y-%m-01') AS DATE))
  ORDER BY
    te.ID,
    Primeiro_Dia_Mes;
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
      tdr.VALOR_LIQUIDO AS Valor_Liquido,
      tccg2.DESCRICAO AS Class_Cont_Grupo_2
    FROM
      T_DESPESA_RAPIDA tdr
    JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID
    LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID
    LEFT JOIN T_ASSOCIATIVA_PLANO_DE_CONTAS tapdc ON tccg2.ID = tapdc.FK_CLASSIFICACAO_GRUPO_2
    JOIN T_DESPESA_STATUS tds ON tdr.ID = tds.FK_DESPESA_RAPIDA
    JOIN T_STATUS ts ON tds.FK_STATUS_NAME = ts.ID
    JOIN T_STATUS_PAGAMENTO tsp2 ON ts.FK_STATUS_PAGAMENTO = tsp2.ID
    WHERE
      tdr.FK_DESPESA_TEKNISA IS NULL
      AND tccg.ID = 162
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
    SUM(Valor_Liquido) AS BlueMe_Sem_Pedido_Valor_Liquido,
    SUM(CASE
      WHEN Class_Cont_Grupo_2 = 'ALIMENTOS' THEN Valor_Liquido
      ELSE 0
    END) AS BlueMe_Sem_Pedido_Alimentos,
    SUM(CASE
      WHEN Class_Cont_Grupo_2 = 'BEBIDAS' THEN Valor_Liquido
      ELSE 0
    END) AS BlueMe_Sem_Pedido_Bebidas,
    SUM(CASE
      WHEN Class_Cont_Grupo_2 = 'EMBALAGENS' THEN Valor_Liquido
      ELSE 0
      END) AS BlueMe_Sem_Pedido_Descart_Hig_Limp,
    SUM(CASE
      WHEN Class_Cont_Grupo_2 NOT IN ('ALIMENTOS', 'BEBIDAS', 'EMBALAGENS') THEN Valor_Liquido
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
def GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_coM_PEDIDO():
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


# @st.cache_data
# def GET_DADOS_PARA_INSUMOS_COM_PEDIDO():
#   return dataframe_query(f'''
# WITH vibmcp AS (SELECT
#     DISTINCT tdr.ID AS tdr_ID,
#     te.ID AS ID_Loja,
#     te.NOME_FANTASIA AS Loja,
#     tf.CORPORATE_NAME AS Fornecedor,
#     tdr.NF AS Doc_Serie,
#     tdr.COMPETENCIA AS Data_Emissao,
#     cast(date_format(cast(tdr.COMPETENCIA as date), '%Y-%m-01') as date) AS Primeiro_Dia_Mes,
#     tdr.OBSERVACAO AS Observacao,
#     tdr.VALOR_LIQUIDO AS Valor_Liquido,
#     SUM(tdri.VALOR) OVER (PARTITION BY tdri.FK_DESPESA_RAPIDA) AS Valor_Total_Insumos_Compra,
#     tin5.ID AS ID_Insumo_Nivel_5,
#     tin5.DESCRICAO AS Nome_Insumo_Nivel_5,
#     tin1.DESCRICAO AS Nome_Insumo_Nivel_1,
#     tdri.QUANTIDADE AS Quantidade,
#     tdri.UNIDADE_MEDIDA AS Unidade_Medida,
#     tdri.VALOR AS Valor_Insumos,
#     SUM(tdri.VALOR) AS Valor_Total_Insumos,
#     SUM(CASE
#         WHEN tin1.DESCRICAO = 'ALIMENTOS' THEN tdri.VALOR
#         ELSE 0
#     END) AS Valor_Alimentos,
#     SUM(CASE
#         WHEN tin1.DESCRICAO = 'BEBIDAS' THEN tdri.VALOR
#         ELSE 0
#     END) AS Valor_Bebidas,
#     SUM(CASE
#         WHEN tin1.DESCRICAO = 'DESCARTAVEIS/HIGIENE E LIMPEZA' THEN tdri.VALOR
#         ELSE 0
#     END) AS Valor_Descartaveis_Higiene_Limpeza,
#     SUM(CASE
#         WHEN tin1.DESCRICAO NOT IN ('ALIMENTOS', 'BEBIDAS', 'DESCARTAVEIS/HIGIENE E LIMPEZA') THEN tdri.VALOR
#         ELSE 0
#     END) AS Valor_Outros,
#     ROUND(tdr.VALOR_LIQUIDO * (SUM(CASE WHEN tin1.DESCRICAO = 'ALIMENTOS' THEN tdri.VALOR ELSE 0 END) / SUM(tdri.VALOR)), 2) AS Valor_Liq_Alimentos,
#     ROUND(tdr.VALOR_LIQUIDO * (SUM(CASE WHEN tin1.DESCRICAO = 'BEBIDAS' THEN tdri.VALOR ELSE 0 END) / SUM(tdri.VALOR)), 2) AS Valor_Liq_Bebidas,
#     ROUND(tdr.VALOR_LIQUIDO * (SUM(CASE WHEN tin1.DESCRICAO = 'DESCARTAVEIS/HIGIENE E LIMPEZA' THEN tdri.VALOR ELSE 0 END) / SUM(tdri.VALOR)), 2) AS Valor_Liq_Descart_Hig_Limp,
#     ROUND(tdr.VALOR_LIQUIDO * (SUM(CASE WHEN tin1.DESCRICAO NOT IN ('ALIMENTOS', 'BEBIDAS', 'DESCARTAVEIS/HIGIENE E LIMPEZA') THEN tdri.VALOR ELSE 0 END) / SUM(tdri.VALOR)), 2) AS Valor_Liq_Outros
# FROM
#     T_DESPESA_RAPIDA tdr
#     JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID
#     LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON tdr.FK_FORMA_PAGAMENTO = tfdp.ID
#     LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID
#     LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID
#     LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID
#     LEFT JOIN T_STATUS_CONFERENCIA_DOCUMENTACAO tscd ON tdr.FK_CONFERENCIA_DOCUMENTACAO = tscd.ID
#     LEFT JOIN T_STATUS_APROVACAO_DIRETORIA tsad ON tdr.FK_APROVACAO_DIRETORIA = tsad.ID
#     LEFT JOIN T_STATUS_APROVACAO_CAIXA tsac ON tdr.FK_APROVACAO_CAIXA = tsac.ID
#     LEFT JOIN T_STATUS_PAGAMENTO tsp ON tdr.FK_STATUS_PGTO = tsp.ID
#     LEFT JOIN T_CALENDARIO tc ON tdr.PREVISAO_PAGAMENTO = tc.ID
#     LEFT JOIN T_CALENDARIO tc2 ON tdr.FK_DATA_REALIZACAO_PGTO = tc2.ID
#     LEFT JOIN T_ASSOCIATIVA_PLANO_DE_CONTAS tapdc ON tccg2.ID = tapdc.FK_CLASSIFICACAO_GRUPO_2
#     LEFT JOIN View_Cargos_PJ vcpj ON tf.CORPORATE_NAME = vcpj.Codigo_PJ
#     LEFT JOIN T_DESPESA_RAPIDA_ITEM tdri ON tdr.ID = tdri.FK_DESPESA_RAPIDA
#     LEFT JOIN T_INSUMOS_NIVEL_5 tin5 ON tdri.FK_INSUMO = tin5.ID
#     LEFT JOIN T_INSUMOS_NIVEL_4 tin4 ON tin5.FK_INSUMOS_NIVEL_4 = tin4.ID
#     LEFT JOIN T_INSUMOS_NIVEL_3 tin3 ON tin4.FK_INSUMOS_NIVEL_3 = tin3.ID
#     LEFT JOIN T_INSUMOS_NIVEL_2 tin2 ON tin3.FK_INSUMOS_NIVEL_2 = tin2.ID
#     LEFT JOIN T_INSUMOS_NIVEL_1 tin1 ON tin2.FK_INSUMOS_NIVEL_1 = tin1.ID
# WHERE
#     tdri.ID IS NOT NULL
#     AND tin5.ID IS NOT NULL
# GROUP BY
#     tdr.ID,
#     te.ID,
#     te.NOME_FANTASIA,
#     tf.CORPORATE_NAME,
#     tdr.NF,
#     tdr.COMPETENCIA,
#     tdr.OBSERVACAO,
#     tdr.VALOR_LIQUIDO,
#     tin5.ID,
#     tin5.DESCRICAO,
#     tin1.DESCRICAO
# ORDER BY tdr.ID )
# select
#     vibmcp.ID_Loja AS ID_Loja,
#     vibmcp.Loja AS Loja,
#     vibmcp.Primeiro_Dia_Mes AS Primeiro_Dia_Mes,
#     sum(vibmcp.Valor_Liquido) AS BlueMe_Com_Pedido_Valor_Liquido,
#     sum(vibmcp.Valor_Insumos) AS BlueMe_Com_Pedido_Valor_Insumos,
#     sum(vibmcp.Valor_Liq_Alimentos) AS BlueMe_Com_Pedido_Valor_Liq_Alimentos,
#     sum(vibmcp.Valor_Liq_Bebidas) AS BlueMe_Com_Pedido_Valor_Liq_Bebidas,
#     sum(vibmcp.Valor_Liq_Descart_Hig_Limp) AS BlueMe_Com_Pedido_Valor_Liq_Descart_Hig_Limp,
#     sum(vibmcp.Valor_Liq_Outros) AS BlueMe_Com_Pedido_Valor_Liq_Outros
#   from
#     vibmcp
#   group by
#     vibmcp.ID_Loja,
#     vibmcp.Primeiro_Dia_Mes
#   order by
#     vibmcp.ID_Loja,
#     vibmcp.Primeiro_Dia_Mes;
# ''')


@st.cache_data
def GET_TRANSF_ESTOQUE_AGRUPADOS():
  return dataframe_query(f'''
  SELECT
    vte.ID_Loja,
    vte.Loja,
    vte.Primeiro_Dia_Mes,
    SUM(vte.Entrada_Transf_Alim) AS Entrada_Transf_Alim,
    SUM(vte.Saida_Transf_Alim) AS Saida_Transf_Alim,
    SUM(vte.Entrada_Transf_Bebidas) AS Entrada_Transf_Bebidas,
    SUM(vte.Saida_Transf_Bebidas) AS Saida_Transf_Bebidas
  FROM (
    SELECT
      tte.ID AS ID_Transf,
      tl.ID AS ID_Loja,
      tl.NOME AS Loja,
      tte.DATA_TRANSFERENCIA AS Data_Transf,
      tte.ENTRADA_TRANSF_ALIMENTOS AS Entrada_Transf_Alim,
      tte.SAIDA_TRANSF_ALIMENTOS AS Saida_Transf_Alim,
      tte.ENTRADA_TRANSF_BEBIDAS AS Entrada_Transf_Bebidas,
      tte.SAIDA_TRANSF_BEBIDAS AS Saida_Transf_Bebidas,
      CAST(DATE_FORMAT(CAST(tte.DATA_TRANSFERENCIA AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes
    FROM
      T_TRANSFERENCIAS_ESTOQUE tte
    JOIN T_LOJAS tl ON tte.FK_LOJA = tl.ID
  ) vte
  GROUP BY
    vte.ID_Loja,
    vte.Primeiro_Dia_Mes
  ORDER BY
    vte.ID_Loja;
''')


### Com t empresas:
  # SELECT
  #   vte.ID_Loja,
  #   vte.Loja,
  #   vte.Primeiro_Dia_Mes,
  #   SUM(vte.Entrada_Transf_Alim) AS Entrada_Transf_Alim,
  #   SUM(vte.Saida_Transf_Alim) AS Saida_Transf_Alim,
  #   SUM(vte.Entrada_Transf_Bebidas) AS Entrada_Transf_Bebidas,
  #   SUM(vte.Saida_Transf_Bebidas) AS Saida_Transf_Bebidas
  # FROM (
  #   SELECT
  #     tte.ID AS ID_Transf,
  #     tl.ID AS ID_Loja,
  #     tl.NOME_FANTASIA AS Loja,
  #     tte.DATA_TRANSFERENCIA AS Data_Transf,
  #     tte.ENTRADA_TRANSF_ALIMENTOS AS Entrada_Transf_Alim,
  #     tte.SAIDA_TRANSF_ALIMENTOS AS Saida_Transf_Alim,
  #     tte.ENTRADA_TRANSF_BEBIDAS AS Entrada_Transf_Bebidas,
  #     tte.SAIDA_TRANSF_BEBIDAS AS Saida_Transf_Bebidas,
  #     CAST(DATE_FORMAT(CAST(tte.DATA_TRANSFERENCIA AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes
  #   FROM
  #     T_TRANSFERENCIAS_ESTOQUE tte
  #   JOIN T_EMPRESAS tl ON tte.FK_LOJA = tl.ID
  # ) vte
  # GROUP BY
  #   vte.ID_Loja,
  #   vte.Primeiro_Dia_Mes
  # ORDER BY
  #   vte.ID_Loja;


@st.cache_data
def GET_PERDAS_E_CONSUMO_AGRUPADOS():
  return dataframe_query(f'''
  WITH vpec AS (
    SELECT
      tpecc.ID AS Perdas_ID,
      tl.ID AS ID_Loja,
      tl.NOME AS Loja,
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
    JOIN T_LOJAS tl ON tpecc.FK_LOJA = tl.ID
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

  # WITH vpec AS (
  #   SELECT
  #     tpecc.ID AS Perdas_ID,
  #     tl.ID AS ID_Loja,
  #     tl.NOME_FANTASIA AS Loja,
  #     tpecc.DATA_BAIXA AS Data_Baixa,        
  #     CASE
  #       WHEN tpecc.FK_MOTIVO = 106 THEN tpecc.VALOR
  #       ELSE 0
  #     END AS Consumo_Interno,
  #     CASE
  #       WHEN tpecc.FK_MOTIVO <> 106 THEN tpecc.VALOR
  #       ELSE 0
  #     END AS Quebras_e_Perdas,
  #     CAST(DATE_FORMAT(CAST(tpecc.DATA_BAIXA AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes
  #   FROM
  #     T_PERDAS_E_CONSUMO_CONSOLIDADOS tpecc
  #   JOIN T_EMPRESAS tl ON tpecc.FK_LOJA = tl.ID
  # )
  # SELECT
  #   vpec.ID_Loja,
  #   vpec.Loja,
  #   vpec.Primeiro_Dia_Mes,
  #   SUM(vpec.Consumo_Interno) AS Consumo_Interno,
  #   SUM(vpec.Quebras_e_Perdas) AS Quebras_e_Perdas
  # FROM vpec
  # GROUP BY
  #   vpec.ID_Loja,
  #   vpec.Primeiro_Dia_Mes
  # ORDER BY
  #   vpec.ID_Loja,
  #   vpec.Primeiro_Dia_Mes;






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
    vbmcp.Valor_Insumos AS Valor_Insumos,
    CAST(DATE_FORMAT(CAST(vbmcp.Data_Emissao AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Alimentos / virapc.Valor_Total_Insumos)), 2) AS Valor_Liq_Alimentos,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Bebidas / virapc.Valor_Total_Insumos)), 2) AS Valor_Liq_Bebidas,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Descartaveis_Higiene_Limpeza / virapc.Valor_Total_Insumos)), 2) AS Valor_Liq_Descart_Hig_Limp,
    ROUND((vbmcp.Valor_Liquido * (virapc.Valor_Outros / virapc.Valor_Total_Insumos)), 2) AS Valor_Liq_Outros
  FROM
    View_BlueMe_Com_Pedido vbmcp
  LEFT JOIN View_Insumos_Receb_Agrup_Por_Categ virapc ON
    vbmcp.tdr_ID = virapc.tdr_ID;
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
    subquery.Valor_Liquido AS Valor_Liquido,
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
      tdr.VALOR_LIQUIDO AS Valor_Liquido,
      tapdc.DESCRICAO_PLANO_DE_CONTAS AS Plano_de_Contas,
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
    LEFT JOIN T_ASSOCIATIVA_PLANO_DE_CONTAS tapdc ON tccg2.ID = tapdc.FK_CLASSIFICACAO_GRUPO_2
    LEFT JOIN T_TEKNISA_CONTAS_A_PAGAR ttcap ON tdr.FK_DESPESA_TEKNISA = ttcap.ID
    LEFT JOIN T_DESPESA_RAPIDA_ITEM tdri ON tdr.ID = tdri.FK_DESPESA_RAPIDA
    JOIN T_DESPESA_STATUS tds ON tdr.ID = tds.FK_DESPESA_RAPIDA
    JOIN T_STATUS ts ON tds.FK_STATUS_NAME = ts.ID
    JOIN T_STATUS_PAGAMENTO tsp2 ON ts.FK_STATUS_PAGAMENTO = tsp2.ID
    WHERE
      tdri.ID IS NULL
      AND tdr.FK_DESPESA_TEKNISA IS NULL
      AND tccg.ID = 162
    ) subquery
  WHERE
    subquery.row_num = 1;
''')

######################## PARETO ##############################

@st.cache_data
def GET_COMPRAS_PRODUTOS_QUANTIA_NOME_COMPRA():
  return dataframe_query(f'''
  SELECT 	
  	tin5.ID AS 'ID Produto',
  	te.NOME_FANTASIA AS 'Loja', 
  	tf.FANTASY_NAME AS 'Fornecedor', 
  	tin5.DESCRICAO AS 'Nome Produto', 
	tin.DESCRICAO AS 'Categoria',
  	tdri.QUANTIDADE AS 'Quantidade',
  	tdri.UNIDADE_MEDIDA AS 'Unidade de Medida',
  	tdri.VALOR AS 'Valor Total', 
  	tdr.COMPETENCIA AS 'Data Compra',
  	tice.FATOR_DE_PROPORCAO AS 'Fator de Proporção'
  FROM T_DESPESA_RAPIDA_ITEM tdri
  LEFT JOIN T_INSUMOS_NIVEL_5 tin5 ON tdri.FK_INSUMO = tin5.ID
  LEFT JOIN T_INSUMOS_NIVEL_4 tin4 ON tin5.FK_INSUMOS_NIVEL_4 = tin4.ID 
  LEFT JOIN T_INSUMOS_NIVEL_3 tin3 ON tin4.FK_INSUMOS_NIVEL_3 = tin3.ID 
  LEFT JOIN T_INSUMOS_NIVEL_2 tin2 ON tin3.FK_INSUMOS_NIVEL_2 = tin2.ID 
  LEFT JOIN T_INSUMOS_NIVEL_1 tin ON tin2.FK_INSUMOS_NIVEL_1 = tin.id
  LEFT JOIN T_DESPESA_RAPIDA tdr ON tdri.FK_DESPESA_RAPIDA = tdr.ID 
  LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID 
  LEFT JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID 
  LEFT JOIN T_INSUMOS_COMPRA_ESTOQUE tice ON tin5.ID = tice.FK_INSUMO_COMPRA 
  WHERE tdr.COMPETENCIA > '2024-01-01'
''')
  
@st.cache_data
def GET_COMPRAS_PRODUTOS_QUANTIA_NOME_ESTOQUE():
  return dataframe_query(f'''
    SELECT 	
  	tin5.ID AS 'ID Produto',
  	te.NOME_FANTASIA AS 'Loja', 
  	tf.FANTASY_NAME AS 'Fornecedor', 
  	tin5.DESCRICAO AS 'Nome Produto', 
	  tin.DESCRICAO AS 'Categoria',
  	tdri.QUANTIDADE AS 'Quantidade',
  	tdri.UNIDADE_MEDIDA AS 'Unidade de Medida',
  	tdri.VALOR AS 'Valor Total', 
  	tdr.COMPETENCIA AS 'Data Compra',
  	tice.FATOR_DE_PROPORCAO AS 'Fator de Proporção'
  FROM T_DESPESA_RAPIDA_ITEM tdri
  LEFT JOIN T_INSUMOS_COMPRA_ESTOQUE tice ON tdri.FK_INSUMO = tice.FK_INSUMO_COMPRA
  LEFT JOIN T_INSUMOS_NIVEL_5 tin5 ON tice.FK_INSUMO_ESTOQUE = tin5.ID
  LEFT JOIN T_INSUMOS_NIVEL_4 tin4 ON tin5.FK_INSUMOS_NIVEL_4 = tin4.ID 
  LEFT JOIN T_INSUMOS_NIVEL_3 tin3 ON tin4.FK_INSUMOS_NIVEL_3 = tin3.ID 
  LEFT JOIN T_INSUMOS_NIVEL_2 tin2 ON tin3.FK_INSUMOS_NIVEL_2 = tin2.ID 
  LEFT JOIN T_INSUMOS_NIVEL_1 tin ON tin2.FK_INSUMOS_NIVEL_1 = tin.id
  LEFT JOIN T_DESPESA_RAPIDA tdr ON tdri.FK_DESPESA_RAPIDA = tdr.ID 
  LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID 
  LEFT JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID 
  WHERE tdr.COMPETENCIA > '2024-01-01'
''')

#################################### FLUXO DE CAIXA ########################################


def GET_SALDOS_BANCARIOS():
  return dataframe_query(f"""
SELECT * FROM View_Saldos_Bancarios
WHERE `Data` >= CURDATE() 
AND `Data` < DATE_ADD(CURDATE(), INTERVAL 8 DAY)
AND Empresa IS NOT NULL
ORDER BY `Data` ASC
""")

# def GET_VALOR_LIQUIDO_RECEBIDO():
#   return dataframe_query(f'''
# SELECT * FROM View_Receitas_Extratos_Manual
# WHERE `Data` >= CURDATE() 
# AND `Data` < DATE_ADD(CURDATE(), INTERVAL 8 DAY)
# AND Empresa IS NOT NULL
# ORDER BY `Data` ASC
# ''')

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
	AND tc.DATA < DATE_ADD(CURDATE(), INTERVAL 8 DAY)
	AND te.NOME_FANTASIA IS NOT NULL
GROUP BY
  te.NOME_FANTASIA,
  tc.DATA
ORDER BY tc.DATA ASC;
''')

def GET_PROJECAO_ZIG():
  # Mudei a view fonte pra unir a t zig faturamento ao t empresas, mas precisa mudar a tabela!!
  return dataframe_query(f'''
SELECT * FROM View_Projecao_Zig_Agrupadas
WHERE `Data` >= CURDATE() 
AND `Data` < DATE_ADD(CURDATE(), INTERVAL 8 DAY)
AND Empresa IS NOT NULL
ORDER BY `Data` ASC
''')

def GET_RECEITAS_EXTRAORD_FLUXO_CAIXA():
  # Mudei sem problemas, já unia a t empresas
  return dataframe_query(f'''
SELECT * FROM View_Previsao_Receitas_Extraord
WHERE `Data` >= CURDATE() 
AND `Data` < DATE_ADD(CURDATE(), INTERVAL 8 DAY)
AND Empresa IS NOT NULL
ORDER BY `Data` ASC
''')

def GET_DESPESAS_APROVADAS():
  #mudei p t empresas na view
  return dataframe_query(f'''
SELECT
vvap.Empresa as 'Empresa',
vvap.`Data` as 'Data',
SUM(vvap.Valores_Aprovados_Previsao) as 'Despesas_Aprovadas_Pendentes' 
FROM View_Valores_Aprovados_Previsao vvap
WHERE `Data` >= CURDATE() 
AND `Data` < DATE_ADD(CURDATE(), INTERVAL 8 DAY)
AND Empresa IS NOT NULL
GROUP BY `Data`, Empresa  
ORDER BY `Data` ASC
''')

def GET_DESPESAS_PAGAS():
  # Feito
  return dataframe_query(f'''
SELECT
vvap.Empresa as 'Empresa',
vvap.`Data` as 'Data',
SUM(vvap.Valores_Pagos) as 'Despesas_Pagas' 
FROM View_Valores_Pagos_por_Previsao vvap
WHERE `Data` >= CURDATE() 
AND `Data` < DATE_ADD(CURDATE(), INTERVAL 8 DAY)
AND Empresa IS NOT NULL
GROUP BY `Data`, Empresa  
ORDER BY `Data` ASC
''')

def GET_FATURAMENTO_ZIG_FLUXO_CAIXA():
  # mudei pra t empresas mas a t zig faturamento deve ser mudada pra query dar certo
  return dataframe_query(f'''
SELECT
tzf.ID AS 'tzf_ID',
te.ID as 'ID_Loja',
te.NOME_FANTASIA AS 'Loja',
tzf.DATA AS 'Data_Faturamento',
tzf.VALOR AS 'Valor_Faturado',
tzf.TIPO_PAGAMENTO AS 'Tipo_Pagamento'
FROM T_ZIG_FATURAMENTO tzf
LEFT JOIN T_EMPRESAS te ON (tzf.FK_LOJA = te.ID)
WHERE (tzf.DATA >= '2024-05-01 00:00:00' AND tzf.VALOR > 0)
ORDER BY te.NOME_FANTASIA, tzf.DATA;
''')

def GET_LOJAS():
  return dataframe_query(f'''
SELECT
te.ID as 'ID_Loja',
te.NOME_FANTASIA as 'Loja'
FROM T_EMPRESAS te
''')


def GET_RECEITAS_EXTRAORD_CONCILIACAO():
  return dataframe_query(f'''
SELECT
tre.ID as 'ID_receita',
te.ID as 'ID_Loja',
te.NOME_FANTASIA as 'Loja',
trec3.NOME as 'Cliente',
trec.CLASSIFICACAO as 'Classificacao',
tep.ID as 'ID_Evento',
tep.NOME_EVENTO as 'Nome_Evento',
tre.VALOR as 'Valor_Total',
tfdp.DESCRICAO as 'Forma_de_Pagamento',
CAST(tre.DATA_OCORRENCIA AS DATE) as 'Data_Competencia',
tsp.DESCRICAO as 'Status_Pgto',
tre.VALOR_CATEGORIA_AB as 'Categ_AB',
tre.VALOR_CATEGORIA_ALUGUEL as 'Categ_Aluguel',
tre.VALOR_CATEGORIA_ARTISTICO as 'Categ_Artist',
tre.VALOR_CATEGORIA_COUVERT as 'Categ_Couvert',
tre.VALOR_CATEGORIA_LOCACAO as 'Categ_Locacao',
tre.VALOR_CATEGORIA_PATROCINIO as 'Categ_Patroc',
tre.VALOR_CATEGORIA_TAXA_SERVICO as 'Categ_Taxa_Serv',
tre.VALOR_PARCELA_1 as 'Valor_Parc_1',
tre.DATA_VENCIMENTO_PARCELA_1 as 'Data_Venc_Parc_1',
tre.DATA_RECEBIMENTO_PARCELA_1 as 'Data_Receb_Parc_1',
tre.VALOR_PARCELA_2 as 'Valor_Parc_2',
tre.DATA_VENCIMENTO_PARCELA_2 as 'Data_Venc_Parc_2',
tre.DATA_RECEBIMENTO_PARCELA_2 as 'Data_Receb_Parc_2',
tre.VALOR_PARCELA_3 as 'Valor_Parc_3',
tre.DATA_VENCIMENTO_PARCELA_3 as 'Data_Venc_Parc_3',
tre.DATA_RECEBIMENTO_PARCELA_3 as 'Data_Receb_Parc_3',
tre.VALOR_PARCELA_4 as 'Valor_Parc_4',
tre.DATA_VENCIMENTO_PARCELA_4 as 'Data_Venc_Parc_4',
tre.DATA_RECEBIMENTO_PARCELA_4 as 'Data_Receb_Parc_4',
tre.VALOR_PARCELA_5 as 'Valor_Parc_5',
tre.DATA_VENCIMENTO_PARCELA_5 as 'Data_Venc_Parc_5',
tre.DATA_RECEBIMENTO_PARCELA_5 as 'Data_Receb_Parc_5'
FROM T_RECEITAS_EXTRAORDINARIAS tre
INNER JOIN T_EMPRESAS te ON (tre.FK_EMPRESA = te.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLASSIFICACAO trec ON (tre.FK_CLASSIFICACAO = trec.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec3 ON (tre.FK_CLIENTE = trec3.ID)
LEFT JOIN T_EVENTO_PRE tep ON (tre.FK_EVENTO = tep.ID)
LEFT JOIN T_STATUS_PAGAMENTO tsp ON (tre.FK_STATUS_PGTO = tsp.ID)
LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON (tep.FK_FORMA_PAGAMENTO = tfdp.ID)
''')

def GET_VIEW_PARC_AGRUP():
  return dataframe_query(f'''
SELECT 
ROW_NUMBER() OVER (ORDER BY te.NOME_FANTASIA ASC, vpa.DATA_VENCIMENTO ASC) AS 'Numero_Linha',
vpa.ID as 'ID_Receita',
te.ID as 'ID_Loja',
te.NOME_FANTASIA as 'Loja',
trec.NOME as 'Cliente',
vpa.DATA_VENCIMENTO as 'Data_Vencimento',
vpa.DATA_RECEBIMENTO as 'Data_Recebimento',
vpa.VALOR_PARCELA as 'Valor_Parcela',
tre.DATA_OCORRENCIA as 'Data_Ocorrencia',
trec2.CONCAT_CATEGORIA_CLASSIFICACAO as 'Categoria_Class'
FROM View_Parcelas_Agrupadas vpa
INNER JOIN T_EMPRESAS te ON (vpa.FK_EMPRESA = te.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS tre ON (vpa.ID = tre.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec ON (vpa.FK_CLIENTE = trec.ID)
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLASSIFICACAO trec2 ON (tre.FK_CLASSIFICACAO = trec2.ID)
WHERE vpa.DATA_VENCIMENTO IS NOT NULL
ORDER BY vpa.DATA_RECEBIMENTO DESC;
''')

def GET_CUSTOS_BLUEME_SEM_PARCELAMENTO():
  return dataframe_query(f'''
SELECT 
tdr.ID as 'ID_Despesa',
tdr.FK_DESPESA_TEKNISA as 'FK_Despesa_Teknisa',
te.ID as 'ID_Loja',
te.NOME_FANTASIA as 'Casa',
tf.CORPORATE_NAME as 'Fornecedor_Razao_Social',
tdr.VALOR_LIQUIDO as 'Valor',
tdr.VENCIMENTO as 'Data_Vencimento',
tc.`DATA` as 'Previsao_Pgto',
tc2.`DATA` as 'Realizacao_Pgto',    
tdr.COMPETENCIA as 'Data_Competencia',
tdr.LANCAMENTO as 'Data_Lancamento',
tfdp.DESCRICAO as 'Forma_Pagamento',
tccg.DESCRICAO as 'Class_Cont_1',
tccg2.DESCRICAO as 'Class_Cont_2',
CONCAT(YEAR(tdr.VENCIMENTO),'-',WEEKOFYEAR(tdr.VENCIMENTO)) as 'Ano_Semana_Vencimento', 
tscd.DESCRICAO as 'Status_Conf_Document',
tsad.DESCRICAO as 'Status_Aprov_Diret',
tsac.DESCRICAO as 'Status_Aprov_Caixa',
tsp.DESCRICAO as 'Status_Pgto'
FROM T_DESPESA_RAPIDA tdr
INNER JOIN T_EMPRESAS te ON (tdr.FK_LOJA = te.ID)
LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON (tdr.FK_FORMA_PAGAMENTO = tfdp.ID)
LEFT JOIN T_FORNECEDOR tf ON (tdr.FK_FORNECEDOR = tf.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID)
LEFT JOIN T_STATUS_CONFERENCIA_DOCUMENTACAO tscd ON (tdr.FK_CONFERENCIA_DOCUMENTACAO = tscd.ID)
LEFT JOIN T_STATUS_APROVACAO_DIRETORIA tsad ON (tdr.FK_APROVACAO_DIRETORIA = tsad.ID)
LEFT JOIN T_STATUS_APROVACAO_CAIXA tsac ON (tdr.FK_APROVACAO_CAIXA = tsac.ID)
LEFT JOIN T_STATUS_PAGAMENTO tsp ON (tdr.FK_STATUS_PGTO = tsp.ID)
LEFT JOIN T_CALENDARIO tc ON (tdr.PREVISAO_PAGAMENTO = tc.ID)	
LEFT JOIN T_CALENDARIO tc2 ON (tdr.FK_DATA_REALIZACAO_PGTO = tc2.ID)
LEFT JOIN T_DEPESA_PARCELAS tdp ON (tdp.FK_DESPESA = tdr.ID)
WHERE 
    te.ID IS NOT NULL
    AND tdp.FK_DESPESA IS NULL
    AND (tdr.FK_DESPESA_TEKNISA IS NULL OR tdr.BIT_DESPESA_TEKNISA_PENDENTE = 1)
    AND tsp.DESCRICAO = "Pago"
    AND tc2.`DATA` >= '2024-05-01 00:00:00'
ORDER BY 
    tc2.`DATA` DESC
''')

def GET_CUSTOS_BLUEME_COM_PARCELAMENTO():
  return dataframe_query(f'''
SELECT 
tdp.ID as 'ID_Parcela',
tdr.ID as 'ID_Despesa',
te.NOME_FANTASIA as 'Empresa',
te.ID as 'ID_Loja',
tf.CORPORATE_NAME as 'Fornecedor_Razao_Social',
CASE
    WHEN tdp.FK_DESPESA IS NOT NULL
        THEN 'True'
    ELSE 'False'
END AS 'Parcelamento',
CASE 
    WHEN tdp.FK_DESPESA IS NOT NULL
        THEN COUNT(tdp.ID) OVER (PARTITION BY tdr.ID)
    ELSE NULL 
END AS 'Qtd_Parcelas',
tdp.PARCELA as 'Num_Parcela',
tdp.VALOR as 'Valor_Parcela',
DATE_FORMAT(DATE_ADD(tdp.`DATA`, INTERVAL 30 SECOND), '%d/%m/%Y') as 'Vencimento_Parcela',
DATE_FORMAT(DATE_ADD(tc.`DATA`, INTERVAL 30 SECOND), '%d/%m/%Y') AS 'Previsao_Parcela',
DATE_FORMAT(DATE_ADD(tc2.`DATA`, INTERVAL 30 SECOND), '%d/%m/%Y') AS 'Realiz_Parcela',
tdr.VALOR_PAGAMENTO as 'Valor_Original',
tdr.VALOR_LIQUIDO as 'Valor_Liquido',
DATE_ADD(STR_TO_DATE(tdr.LANCAMENTO, '%Y-%m-%d'), INTERVAL 30 SECOND) as 'Data_Lancamento',
tfdp.DESCRICAO as 'Forma_Pagamento',
tccg.DESCRICAO as 'Class_Cont_1',
tccg2.DESCRICAO as 'Class_Cont_2',
CONCAT(YEAR(tdr.VENCIMENTO),'-',WEEKOFYEAR(tdr.VENCIMENTO)) as 'Ano_Semana_Vencimento', 
tscd.DESCRICAO as 'Status_Conf_Document',
tsad.DESCRICAO as 'Status_Aprov_Diret',
tsac.DESCRICAO as 'Status_Aprov_Caixa',
CASE
    WHEN tdp.PARCELA_PAGA = 1 
        THEN 'Parcela_Paga'
    ELSE 'Parcela_Pendente'
END as 'Status_Pgto'
FROM T_DESPESA_RAPIDA tdr
INNER JOIN T_EMPRESAS te ON (tdr.FK_LOJA = te.ID)
LEFT JOIN T_FORMAS_DE_PAGAMENTO tfdp ON (tdr.FK_FORMA_PAGAMENTO = tfdp.ID)
LEFT JOIN T_FORNECEDOR tf ON (tdr.FK_FORNECEDOR = tf.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID)
LEFT JOIN T_STATUS_CONFERENCIA_DOCUMENTACAO tscd ON (tdr.FK_CONFERENCIA_DOCUMENTACAO = tscd.ID)
LEFT JOIN T_STATUS_APROVACAO_DIRETORIA tsad ON (tdr.FK_APROVACAO_DIRETORIA = tsad.ID)
LEFT JOIN T_STATUS_APROVACAO_CAIXA tsac ON (tdr.FK_APROVACAO_CAIXA = tsac.ID)
LEFT JOIN T_STATUS_PAGAMENTO tsp ON (tdr.FK_STATUS_PGTO = tsp.ID)
LEFT JOIN T_DEPESA_PARCELAS tdp ON (tdp.FK_DESPESA = tdr.ID)
LEFT JOIN T_CALENDARIO tc ON (tdp.FK_PREVISAO_PGTO = tc.ID)
LEFT JOIN T_CALENDARIO tc2 ON (tdp.FK_DATA_REALIZACAO_PGTO = tc2.ID)
WHERE 
    tdp.FK_DESPESA IS NOT NULL
    AND (tdr.FK_DESPESA_TEKNISA IS NULL OR tdr.BIT_DESPESA_TEKNISA_PENDENTE = 1)
    AND tdp.PARCELA_PAGA = 1
    AND tc2.`DATA` >= '2024-05-01 00:00:00'
ORDER BY 
    tc2.`DATA` DESC
''')

def GET_EXTRATOS_BANCARIOS():
  return dataframe_query(f'''
SELECT
teb.ID as 'ID_Extrato_Bancario',
tcb.ID as 'ID_Conta_Bancaria',
tcb.NOME_DA_CONTA as 'Nome_Conta_Bancaria',
te.ID as 'ID_Loja',
te.NOME_FANTASIA as 'Loja',
teb.DATA_TRANSACAO as 'Data_Transacao',
CASE 
    WHEN teb.FK_TIPO_CREDITO_DEBITO = 100 THEN 'CREDITO'
    ELSE 'DEBITO'
END as 'Tipo_Credito_Debito',
teb.DESCRICAO_TRANSACAO as 'Descricao_Transacao',
teb.VALOR as 'Valor'
FROM T_EXTRATOS_BANCARIOS teb
INNER JOIN T_CONTAS_BANCARIAS tcb ON (teb.FK_CONTA_BANCARIA = tcb.ID)
INNER JOIN T_EMPRESAS te ON (tcb.FK_LOJA = te.ID)
WHERE teb.DESCRICAO_TRANSACAO NOT LIKE '%RESG AUTOMATICO%'
AND teb.DESCRICAO_TRANSACAO NOT LIKE '%APLICACAO AUTOMATICA%'
ORDER BY teb.DATA_TRANSACAO DESC
''')

def GET_MUTUOS():
  return dataframe_query(f'''
SELECT
tm.ID as 'Mutuo_ID',
tm.`DATA` as 'Data_Mutuo',
te.ID as 'ID_Loja_Saida',
te.NOME_FANTASIA as 'Loja_Saida',
te2.ID as 'ID_Loja_Entrada',
te2.NOME_FANTASIA as 'Loja_Entrada',
tm.VALOR as 'Valor',
tm.TAG_FATURAM_ZIG as 'Tag_Faturam_Zig'
FROM T_MUTUOS tm 
LEFT JOIN T_EMPRESAS te ON (tm.FK_LOJA_SAIDA = te.ID)
LEFT JOIN T_EMPRESAS te2 ON (tm.FK_LOJA_ENTRADA = te2.ID)
ORDER BY tm.`DATA` DESC
''')

def GET_TESOURARIA_TRANSACOES():
  return dataframe_query(f'''
SELECT
ttt.ID as 'tes_ID',
te.ID as 'ID_Loja',
te.NOME_FANTASIA as 'Loja',
ttt.DATA_TRANSACAO as 'Data_Transacao',
ttt.VALOR as 'Valor',
ttt.DESCRICAO as 'Descricao'
FROM T_TESOURARIA_TRANSACOES ttt 
INNER JOIN T_EMPRESAS te ON (ttt.FK_LOJA = te.ID)   
''')


@st.cache_data
def GET_DESPESAS_PENDENTES(data):
  # Formatando as datas para o formato de string com aspas simples
  dataStr = f"'{data.strftime('%Y-%m-%d %H:%M:%S')}'"
  return dataframe_query(f'''
SELECT
    tc.DATA as 'Data',
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
    AND tc.DATA = {dataStr}
UNION ALL
SELECT
    tc.DATA as 'Data',
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
INNER JOIN T_EMPRESAS te ON (tdr.FK_LOJA = te.ID)
INNER JOIN T_FORNECEDOR tf ON (tdr.FK_FORNECEDOR = tf.ID)
LEFT JOIN T_DEPESA_PARCELAS tdp ON (tdp.FK_DESPESA = tdr.ID)
LEFT JOIN T_CALENDARIO tc ON (tdp.FK_PREVISAO_PGTO = tc.ID)
WHERE tdp.ID is NOT NULL 
    AND tc.DATA = {dataStr}
    AND (tdp.PARCELA_PAGA = 0 OR tdp.PARCELA_PAGA IS NULL);
''')