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

@st.cache_data
def GET_FATURAM_ZIG_AGREGADO():
  return dataframe_query(f''' 
  SELECT
    tl.ID AS ID_Loja,
    tl.NOME AS Loja,
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
    T_LOJAS tl ON tfza.ID_LOJA = tl.ID
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
    tl.ID AS ID_Loja,
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
    T_LOJAS tl ON te.FK_LOJA = tl.ID
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
    tl.NOME as 'Loja',
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
    LEFT JOIN T_LOJAS tl ON (tiv.LOJA_ID = tl.`KEY`)
  WHERE CAST(tiv.EVENT_DATE as DATETIME) >= {data_inicial_str} AND CAST(tiv.EVENT_DATE as DATETIME) <= {data_final_str}
  ''')



@st.cache_data
def GET_RECEIT_EXTRAORD():
  #'Data_Evento' é, na realidade, a data da competencia, eu só coloquei esse nome pra ficar mais fácil de programar
  return dataframe_query(f'''
  SELECT
    tre.ID as 'ID_receita',
    tl.NOME as 'Loja',
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
    INNER JOIN T_LOJAS tl ON (te.FK_LOJA = tl.ID)
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

def GET_DESPESAS():
  #'Data_Evento' é, na realidade, a data da emissão, eu só coloquei esse nome pra ficar mais fácil de programar
  return dataframe_query(f'''
  SELECT * FROM (
    SELECT 
      tdr.ID AS ID,
      tl.NOME AS Loja,
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
    LEFT JOIN T_LOJAS tl ON te.FK_LOJA = tl.ID
    LEFT JOIN T_FORNECEDOR tf ON tdr.FK_FORNECEDOR = tf.ID
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID
    LEFT JOIN T_ASSOCIATIVA_PLANO_DE_CONTAS tapdc ON tccg2.ID = tapdc.FK_CLASSIFICACAO_GRUPO_2
    LEFT JOIN T_CLASSIFICACAO_PLANO_DE_CONTAS tcpdc ON tapdc.FK_CLASSIFICACAO_PLANO_DE_CONTAS = tcpdc.ID
    LEFT JOIN T_ORCAMENTOS to2 ON tapdc.FK_CLASSIFICACAO_GRUPO_2 = to2.FK_CLASSIFICACAO_2 
      AND MONTH(CAST(tdr.COMPETENCIA AS DATE)) = to2.MES
      AND to2.FK_EMPRESA = te.ID
    WHERE tdr.FK_DESPESA_TEKNISA IS NULL
      AND tdr.COMPETENCIA >= '2024-01-01 00:00:00'
      AND NOT EXISTS (
        SELECT 1
        FROM T_DESPESA_RAPIDA_ITEM tdri
        WHERE tdri.FK_DESPESA_RAPIDA = tdr.ID
      )
    UNION ALL
    SELECT 
      tcap.ID AS ID,
      tl.NOME AS Loja,
      tcap.FORNECEDOR_RAZAO_SOCIAL AS Fornecedor,
      tcap.DOC_SERIE AS Doc_Serie,
      CAST(tcap.DATA_EMISSAO AS DATE) AS Data_Emissao,
      CAST(tcap.DATA_VENCIMENTO AS DATE) AS Data_Vencimento,
      tcap.DESCRICAO AS Descricao,
      tcap.VALOR_LIQUIDO AS Valor_Liquido,
      tapdc.DESCRICAO_PLANO_DE_CONTAS AS Plano_de_Contas,
      tcpdc.DESCRICAO AS Class_Plano_de_Contas,
      to2.VALOR AS Orcamento,
      tcap.STATUS_NF AS Status
    FROM T_TEKNISA_CONTAS_A_PAGAR tcap
    JOIN T_LOJAS tl ON tcap.EMPRESA = tl.TEKNISA_CONTAS_A_PAGAR_NOME
    JOIN T_EMPRESAS te ON te.FK_LOJA = tl.ID
    LEFT JOIN T_ASSOCIATIVA_PLANO_DE_CONTAS tapdc ON tcap.TIPO_DE_CONTA = tapdc.TIPO_DE_CONTA_TEKNISA
    LEFT JOIN T_CLASSIFICACAO_PLANO_DE_CONTAS tcpdc ON tapdc.FK_CLASSIFICACAO_PLANO_DE_CONTAS = tcpdc.ID
    LEFT JOIN T_ORCAMENTOS to2 ON tapdc.FK_CLASSIFICACAO_GRUPO_2 = to2.FK_CLASSIFICACAO_2 
      AND MONTH(CAST(tcap.DATA_EMISSAO AS DATE)) = to2.MES
      AND to2.FK_EMPRESA = te.ID
    WHERE tcap.DATA_EMISSAO >= '2024-01-01 00:00:00'
      AND tcap.STATUS_NF = 'Real'
  ) AS despesas
  WHERE Class_Plano_de_Contas IS NOT NULL;
  ''')



############################### A PARTIT DAQUI É TD DO CMV ####################################

@st.cache_data
def GET_FATURAM_ZIG_ALIM_BEB_MENSAL():
  return dataframe_query(f'''
  SELECT
    tfza.ID_LOJA AS ID_Loja,
    tl.NOME AS Loja,
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
    T_LOJAS tl on tfza.ID_LOJA = tl.ID
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
    tl.ID AS ID_Loja,
    tl.NOME AS Loja,
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
    JOIN T_LOJAS tl ON tvee.FK_LOJA = tl.ID
    JOIN T_INSUMOS_NIVEL_1 tin ON tvee.FK_INSUMO_NIVEL_1 = tin.ID
  GROUP BY
    tl.ID,
    tl.NOME,
    Primeiro_Dia_Mes,
    LAST_DAY(CAST(DATE_FORMAT(CAST(tvee.DATA_CONTAGEM AS DATE), '%Y-%m-01') AS DATE))
  ORDER BY
    tl.ID,
    Primeiro_Dia_Mes;
''')



@st.cache_data
def GET_INSUMOS_AGRUPADOS_BLUE_ME_POR_CATEG_SEM_PEDIDO():
  return dataframe_query(f'''
  WITH subquery AS (
    SELECT
      tdr.ID AS tdr_ID,
      tl.ID AS ID_Loja,
      tl.NOME AS Loja,
      CAST(DATE_FORMAT(CAST(tdr.COMPETENCIA AS DATE), '%Y-%m-01') AS DATE) AS Primeiro_Dia_Mes,
      tdr.VALOR_LIQUIDO AS Valor_Liquido,
      tccg2.DESCRICAO AS Class_Cont_Grupo_2
    FROM
      T_DESPESA_RAPIDA tdr
    JOIN T_EMPRESAS te ON tdr.FK_LOJA = te.ID
    LEFT JOIN T_LOJAS tl ON te.FK_LOJA = tl.ID
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
      tl.ID,
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
      tl.ID AS ID_Loja,
      tl.NOME AS Loja,
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
    LEFT JOIN T_LOJAS tl ON te.FK_LOJA = tl.ID
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