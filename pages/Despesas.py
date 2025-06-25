import streamlit as st
import pandas as pd
from utils.queries import *
from utils.functions.despesas import *
from utils.functions.dados_gerais import *
from utils.components import *
from utils.user import logout

st.set_page_config(
  layout = 'wide',
  page_title = 'Despesas',
  page_icon=':money_with_wings:',
  initial_sidebar_state="collapsed"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')



config_sidebar()
col, col2, col3 = st.columns([6, 1, 1])
with col:
  st.title('DESPESAS')
with col2:
  st.button(label="Atualizar", on_click = st.cache_data.clear)
with col3:
  if st.button("Logout"):
    logout()

st.divider()

lojasComDados = preparar_dados_lojas_user()
data_inicio_default, data_fim_default = preparar_dados_datas()
lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)
st.divider()

despesasDetalhadas = GET_DESPESAS()
despesasDetalhadas = filtrar_por_datas(despesasDetalhadas, data_inicio, data_fim, 'Data_Emissao')
despesasDetalhadas = filtrar_por_classe_selecionada(despesasDetalhadas, 'Loja', lojas_selecionadas)

Despesas2 = GET_DESPESAS().drop_duplicates()
Orcamentos = GET_ORCAMENTOS_DESPESAS().drop_duplicates()
Despesas = pd.merge(Despesas2, Orcamentos, on=['Primeiro_Dia_Mes', 'Loja', 'Classificacao_Contabil_1', 'Classificacao_Contabil_2'], how='outer')
Despesas['Data_Emissao'] = Despesas['Data_Emissao'].fillna(Despesas['Primeiro_Dia_Mes'])
Despesas = filtrar_por_datas(Despesas, data_inicio, data_fim, 'Data_Emissao')
Despesas = filtrar_por_classe_selecionada(Despesas, 'Loja', lojas_selecionadas)
despesasConfig = config_despesas_por_classe(Despesas)

tab1, tab2 = st.tabs(['Despesas', 'Despesas Detalhadas'])

with tab1:
    with st.container(border=True):
        col0, col1, col2 = st.columns([1, 15, 1])
        with col1:
            st.write("")
            st.markdown("## Despesas")
            st.write("")
            despesasConfig = despesasConfig[~((despesasConfig['Orçamento'] == 0) & (despesasConfig['Valor Realizado'] == 0))]
            lista_class_contabil_1 = despesasConfig['Class. Contábil 1'].dropna().unique().tolist()
            altura_linha = 35
            for classe in lista_class_contabil_1:
                df_classe = despesasConfig[despesasConfig['Class. Contábil 1'] == classe]
                df_classe = df_classe.drop(columns=['Class. Contábil 1']).reset_index(drop=True)
                orcamento_total = df_classe['Orçamento'].sum()
                realizado_total = df_classe['Valor Realizado'].sum()
                orc_realiz_total = df_classe['Orçamento - Realiz.'].sum()
                if orcamento_total != 0:
                    atingimento = (realizado_total / orcamento_total) * 100
                else:
                    atingimento = "Não há orçamento"
                linha_total = pd.DataFrame({
					"Class. Contábil 2": ["Total"],
					"Orçamento": [orcamento_total],
					"Valor Realizado": [realizado_total],
					"Orçamento - Realiz.": [orc_realiz_total],
					"Atingimento do Orçamento": [atingimento],
				})


                df_classe = pd.concat([df_classe, linha_total], ignore_index=True)
                df_classe = format_columns_brazilian(
                    df_classe,
                    [
                        "Orçamento",
                        "Valor Realizado",
                        "Orçamento - Realiz.",
                        "Atingimento do Orçamento",
                    ]
                )
                df_classe["Atingimento do Orçamento"] = df_classe["Atingimento do Orçamento"].apply(
					lambda x: f"{x} %"
				)
                
                df_classe.loc[df_classe["Orçamento"] == '0,00', "Atingimento do Orçamento"] = (
					"Não há Orçamento"
				)
                
                df_despesas_styled = df_classe.style.map(highlight_values, subset=['Orçamento - Realiz.'])

                st.markdown(f"#### {classe}")
                st.dataframe(
                    df_despesas_styled,
                    height=altura_linha * len(df_classe) + 35,
                    use_container_width=True,
                    hide_index=True
                )

                

despesaDetalhadaConfig = config_despesas_detalhado(despesasDetalhadas)

classificacoes1 = preparar_dados_classe_selecionada(despesaDetalhadaConfig, 'Class. Contábil 1')

with tab2:
  with st.container(border=True):
    st.write("")
    col0, col1, col2 = st.columns([1, 15, 1])
    with col1:
      col3, col4, col5, col6 = st.columns([2, 1, 1, 1], vertical_alignment='center')
      with col3:
        st.markdown("## Despesas Detalhadas")
      with col4:
        classificacoes_1_selecionadas = st.multiselect(label='Selecione Classificação Contábil 1', options=classificacoes1)
        despesaDetalhadaConfig = filtrar_por_classe_selecionada(despesaDetalhadaConfig, 'Class. Contábil 1', classificacoes_1_selecionadas)
      with col5:
        classificacoes2 = preparar_dados_classe_selecionada(despesaDetalhadaConfig, 'Class. Contábil 2')
        classificacoes_2_selecionadas = st.multiselect(label='Selecione Classificação Contábil 2', options=classificacoes2)
        despesaDetalhadaConfig = filtrar_por_classe_selecionada(despesaDetalhadaConfig, 'Class. Contábil 2', classificacoes_2_selecionadas)
      with col6:
        fornecedores = preparar_dados_classe_selecionada(despesaDetalhadaConfig, 'Fornecedor')
        fornecedores_selecionados = st.multiselect(label='Selecione Fornecedores', options=fornecedores)
        despesaDetalhadaConfig = filtrar_por_classe_selecionada(despesaDetalhadaConfig, 'Fornecedor', fornecedores_selecionados)
      st.write("")
      valorTotal = despesaDetalhadaConfig['Valor'].sum()
      valorTotal = format_brazilian(valorTotal)
      despesaDetalhadaConfig = format_columns_brazilian(despesaDetalhadaConfig, ['Valor'])
      despesaDetalhadaConfig = despesaDetalhadaConfig.rename(columns={'Doc_Serie': 'Doc. Série'})
      despesaDetalhadaConfig = despesaDetalhadaConfig[['ID Despesa', 'Loja', 'Class. Contábil 1', 'Class. Contábil 2',  'Fornecedor', 'Doc. Série', 'Data Emissão', 'Data Vencimento', 'Descrição', 'Status',  'Valor' ]]
      st.dataframe(despesaDetalhadaConfig, height=500, use_container_width=True, hide_index=True)
      st.markdown(f"**Valor Total = R$ {valorTotal}**")