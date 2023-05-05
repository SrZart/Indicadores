import streamlit as st
from income import income_table
from val import valuation 
from balance import balance_table
from kpi import indicadores
from cf import clash_flow_table 
from cvm import cvm_data
from fred import chart_spread, chart_var_monet, chart_fed_asset

#Define a pagina no modo wide
st.set_page_config(layout="wide")
#Escolha dos gráficos a serem exibidos
init = st.selectbox(
    'Selecione a opção desejada',
    ['Indicadores enconômicos','Dados cia aberta'],
)
#Inicia programa de indicadores econômicos
if 'Indicadores enconômicos' in init:
    opcao = st.sidebar.selectbox(
        'Selecione o gráfico',
        ['Spread taxa de juros','Variação monetária - EUA','Total de ativos do FED']) 
    #chama função para criar gráfico do spread dos títulos americanos
    if 'Spread taxa de juros' in opcao:
        chart_spread()
    #Chama função para criar gráfico da variação monetária
    if 'Variação monetária - EUA' in opcao:
        chart_var_monet()
    #Chama função para criar gráficos dos ativos do FED
    if 'Total de ativos do FED' in opcao:
        chart_fed_asset()
#Inicia programa para baixar e consolidar dados de cias abertas
if 'Dados cia aberta' in init:
    opcao1 = st.sidebar.selectbox(
        'Selecione o gráfico',
        ['Análise Fundamentalista','Baixar dados da CVM'])
    if 'Baixar dados da CVM' in opcao1:
        cvm_data()
    if 'Análise Fundamentalista' in opcao1:
        val_tipo = st.radio(
                'Selecione o setor',
                ('Industria','Financeiro')
            )
        if 'Industria' in val_tipo:
            sa_opt = st.sidebar.selectbox(
                '',
                ['Resultado', 'Balanço patrimonial', 'Fluxo de caixa', 'Indicadores', 'Valuation']
            )
            if 'Resultado' in sa_opt:
                st.header(sa_opt)
                income_table()
            if 'Balanço patrimonial' in sa_opt:
                st.header(sa_opt)
                balance_table()
            if 'Fluxo de caixa' in sa_opt:
                st.header(sa_opt)
                clash_flow_table()
            if 'Indicadores' in sa_opt:
                st.header(sa_opt)
                indicadores()
            if 'Valuation' in sa_opt:
                st.header(opcao1)
                valuation() 
###