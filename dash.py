import streamlit as st
import altair as alt
import pandas as pd
from fredapi import Fred
import datetime
import plotly.express as px
import wget
from zipfile import ZipFile
import plotly.graph_objects as go

#Define a pagina no modo wide
st.set_page_config(layout="wide")
# Inicializa a API do FRED com sua chave de API
fred = Fred(api_key='3f8e03c66ff45fa8aff0577a3a08bbaa')

#Cria função para baixar e consolidar arquivos da CVM
def cvm_data():
    st.title("Baixar e consolidar dados da CVM")

    # Solicita as informações iniciais do usuário
    start_year = st.number_input("Ano inicial:", min_value=2010, max_value=2023,step=1)
    end_year = st.number_input("Ano final:", min_value=2010, max_value=2023,step=1)+1

    # Define a URL e a lista de arquivos a serem baixados
    url_cvm = 'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/'
    if  st.button('Baixar arquivos'):
        arq_zip = []
        for ano in range(start_year, end_year):
            arq_zip.append(f'dfp_cia_aberta_{ano}.zip')
            arq_zip
        # Baixa e extrai os arquivos ZIP'
        st.text("Baixando arquivos...")
        for arq in arq_zip:
            wget.download(url_cvm+arq)
            ZipFile(arq, 'r').extractall('CVM')
            st.text("Arquivos baixados e extraídos com sucesso!")

        # Consolida os dados e salva em arquivos CSV
        st.text("Consolidando dados...")
        nome_arq_cons = ['BPA_con','BPP_con','DFC_MD_con','DFC_MI_con','DMPL_con','DRA_con','DRE_con','DVA_con']
        for arq_cons in nome_arq_cons:
            arq_cons_data = pd.DataFrame()
            for ano in range(start_year, end_year):
                arq_cons_data = pd.concat([arq_cons_data, pd.read_csv(f'CVM/dfp_cia_aberta_{arq_cons}_{ano}.csv', sep=';', decimal=',', encoding='ISO-8859-1')])
            arq_cons_data.to_csv(f'DADOS/dfp_cia_aberta_{arq_cons}.csv', index=False)
            st.text("Dados consolidados e salvos em DADOS")

#Cria função para criar gráficos do spread dos títulos do tesouro americano
def chart_spread():       
    opcao_spread1 = st.sidebar.selectbox(
        'Selecione o primeiro título do tesouro americano',
        ('30 Anos', '10 Anos', '2 Anos', '3 Meses')
    )
    if opcao_spread1:   
        opcao_spread2 = st.sidebar.selectbox(
            'Selecione o segundo título do tesouro americano',
            ('30 Anos', '10 Anos', '2 Anos', '3 Meses'), index=3    
        )   
    if opcao_spread1 and opcao_spread2:
    # Define os códigos dos títulos do tesouro americano
        bond_30y_code = 'DGS30'
        bond_3m_code = 'DGS3MO'
        bond_10y_code = 'DGS10'
        bond_2y_code = 'DGS2'

    # Obtém os dados dos títulos do tesouro americano
    bond_30y_hist = pd.DataFrame(fred.get_series(bond_30y_code, start_date, end_date))
    bond_3m_hist = pd.DataFrame(fred.get_series(bond_3m_code, start_date, end_date))
    bond_10y_hist = pd.DataFrame(fred.get_series(bond_10y_code, start_date, end_date))
    bond_2y_hist = pd.DataFrame(fred.get_series(bond_2y_code, start_date, end_date))

    # Renomeia as colunas para 'Close' em todas as tabelas de dados
    bond_30y_hist.columns = ['Close']
    bond_3m_hist.columns = ['Close']
    bond_10y_hist.columns = ['Close']
    bond_2y_hist.columns = ['Close']

    #Define título ao botão de opção
    if opcao_spread1 == '30 Anos':
        spread1 = bond_30y_hist
    elif opcao_spread1 == '10 Anos':
        spread1 = bond_10y_hist
    elif opcao_spread1 == '2 Anos':
        spread1 = bond_2y_hist
    elif opcao_spread1 == '3 Meses':
        spread1 = bond_3m_hist

    if opcao_spread2 == '30 Anos':
        spread2 = bond_30y_hist
    elif opcao_spread2 == '10 Anos':
        spread2 = bond_10y_hist
    elif opcao_spread2 == '2 Anos':
        spread2 = bond_2y_hist
    elif opcao_spread2 == '3 Meses':
        spread2 = bond_3m_hist
    # Calcula os spreads
    spread = spread1['Close'] - spread2['Close']

    # Cria o gráfico do spread entre títulos do tesouro americano de 30 anos e de 3 meses
    fig = px.line(y=spread, x=spread.index)
    fig.update_layout(
        title=f'Spread entre títulos do tesouro americano de {opcao_spread1} e {opcao_spread2}',
        xaxis_title='Data',
        yaxis_title='Spread',
        yaxis=dict(showgrid=False) 
    )
    fig.add_shape(
        type='line', x0=spread.index.min(), x1=spread.index.max(), y0=0, y1=0,
        line=dict(color='black', width=0.5, dash='dash')
    )
    fig.update_traces(hovertemplate='%{x}: %{y}%')  

    source1 = pd.DataFrame({'Date': spread.index, 'Spread': spread.values})
    chart1 = alt.Chart(source1).mark_line().encode(
        x='Date:T',
        y='Spread:Q',
        tooltip=['Date', 'Spread']
    ).properties(
        title=f'Spread entre títulos do tesouro americano de {opcao_spread1} e {opcao_spread2}'
    ).interactive()
    ref_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(strokeDash=[3, 3]).encode(y='y')
    chart1 = alt.layer(chart1, ref_line)
                
    if grafico == 'Tipo 1':
        st.plotly_chart(fig)  
    elif grafico == 'Tipo 2':   
        st.altair_chart(chart1, use_container_width=True)
#Cria data frame
arq_dre = pd.read_csv(f'DADOS/dfp_cia_aberta_DRE_con.csv')
arq_dre['DT_FIM_EXERC'] = pd.to_datetime(arq_dre['DT_FIM_EXERC'])
arq_dre['DT_FIM_EXERC'] = arq_dre['DT_FIM_EXERC'].dt.strftime('%d-%m-%Y')
nome_cia = arq_dre['DENOM_CIA'].unique()
arq_bpa = pd.read_csv(f'DADOS/dfp_cia_aberta_BPA_con.csv')
arq_bpa['DT_FIM_EXERC'] = pd.to_datetime(arq_bpa['DT_FIM_EXERC'])
arq_bpa['DT_FIM_EXERC'] = arq_bpa['DT_FIM_EXERC'].dt.strftime('%d-%m-%Y')
arq_bpp = pd.read_csv(f'DADOS/dfp_cia_aberta_BPP_con.csv')
arq_bpp['DT_FIM_EXERC'] = pd.to_datetime(arq_bpp['DT_FIM_EXERC'])
arq_bpp['DT_FIM_EXERC'] = arq_bpp['DT_FIM_EXERC'].dt.strftime('%d-%m-%Y')
arq_dfc = pd.read_csv(f'DADOS/dfp_cia_aberta_DFC_MI_con.csv')
arq_dfc['DT_FIM_EXERC'] = pd.to_datetime(arq_dfc['DT_FIM_EXERC'])
arq_dfc['DT_FIM_EXERC'] = arq_dfc['DT_FIM_EXERC'].dt.strftime('%d-%m-%Y')

#Cria função para criar gráfico da variação monetária americana
def chart_var_monet():
    m1_code = 'M1SL'  
        
    #Obtém os dados da variação monetária
    m1_hist = fred.get_series(m1_code, start_date, end_date)
    m1_hist = pd.Series(m1_hist)
    #Renomeia colunas
    m1_hist.columns = ['Close']
        
    #Cria gráficos de variação monetária
    fig = px.line(y=m1_hist, x=m1_hist.index)
    fig.update_layout(
        title='Variação monetária nos EUA',
        xaxis_title='Data',
        yaxis_title='M1 Bilhões de dólares',
        yaxis=dict(showgrid=False) 
    )
    fig.update_traces(hovertemplate='%{x}: $ %{y:,.2f}')  

    source1 = pd.DataFrame({'Date': m1_hist.index, 'M1 Bilhões de dólares': m1_hist.values})
    chart1 = alt.Chart(source1).mark_line().encode(
        x='Date:T',
        y='M1 Bilhões de dólares:Q',
        tooltip=['Date', 'M1 Bilhões de dólares']
    ).properties(
        title='Variação monetária nos EUA'
    ).interactive()
    if grafico == 'Tipo 1':
        st.plotly_chart(fig)  
    elif grafico == 'Tipo 2':   
        st.altair_chart(chart1, use_container_width=True)
#Cria função para criar gráfico do total de ativos do fed
def chart_fed_asset():
    fed_asset_code = 'WALCL'
    #Obtém dados dos ativos do fed
    fed_asset_hist = fred.get_series(fed_asset_code, start_date, end_date)

    #Cria gráfico de ativos do fed
    fig = px.line(y=fed_asset_hist, x=fed_asset_hist.index)
    fig.update_layout(
        title='Total de ativos do FED',
        xaxis_title='Data',
        yaxis_title='Ativos do Fed em milhões de dólares',
        yaxis=dict(showgrid=False) 
        )
    fig.update_traces(hovertemplate='%{x}: $ %{y:,.2f}')  

    source1 = pd.DataFrame({'Date': fed_asset_hist.index, 'Ativos do Fed em milhões de dólares': fed_asset_hist.values})
    chart1 = alt.Chart(source1).mark_line().encode(
        x='Date:T',
        y='Ativos do Fed em milhões de dólares:Q',
        tooltip=['Date', 'Ativos do Fed em milhões de dólares']
    ).properties(
        title='Total de ativos do FED'
    ).interactive()
    if grafico == 'Tipo 1':
        st.plotly_chart(fig)  
    elif grafico == 'Tipo 2':   
        st.altair_chart(chart1, use_container_width=True)   
#Cria função para criar tabela de resultado
def income_table():
    #Cria uma lista de seleção pelo nome da empresa, e busca o código CVM
    dre = arq_dre[(arq_dre['ORDEM_EXERC'] == 'ÚLTIMO') &
              (arq_dre['CD_CVM'] == ticker)]
    bpa = arq_bpa[(arq_bpa['ORDEM_EXERC'] == 'ÚLTIMO') &
              (arq_bpa['CD_CVM'] == ticker)]
    #Busca os dados 
    receita = dre[dre['CD_CONTA'] == '3.01']
    custo = dre[dre['CD_CONTA'] == '3.02']
    lb = dre[dre['CD_CONTA'] == '3.03']
    l_op = dre[dre['CD_CONTA'] == '3.05']
    ll = dre[dre['CD_CONTA'] == '3.11']
    despesas_vendas = dre[dre['CD_CONTA'] == '3.04.01']
    despesas_GA = dre[dre['CD_CONTA'] == '3.04.02'] 
    contas = pd.DataFrame()
    contas['Receita'] = receita.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['Custo'] = custo.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['LB'] = lb.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['LOP'] = l_op.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['LL'] = ll.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['D_V'] = despesas_vendas.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['D_GA'] = despesas_GA.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['D_VGA'] = contas['D_V'] + contas['D_GA']
    contas['MB'] = round(contas['LB'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['ML'] = round(contas['LL'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['MOP'] = round(contas['LOP'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['R_CAGR'] = round(((contas['Receita'].iloc[-1] / contas['Receita'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    contas['LL_CAGR'] = round(((contas['LL'].iloc[-1] / contas['LL'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    contas['C_CAGR'] = round(((contas['Custo'].iloc[-1] / contas['Custo'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    contas['DVGA_CAGR'] = round(((contas['D_VGA'].iloc[-1] / contas['D_VGA'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    df_it = pd.DataFrame()
    df_it['Receita'] = receita.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_it['Custo'] = custo.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_it['Lucro Bruto'] = lb.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_it['Despesas VGA'] = contas.groupby('DT_FIM_EXERC')['D_VGA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_it['Lucro Operacional'] = l_op.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_it['Lucro Liquido'] = ll.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_it['Margem Bruta'] = contas.groupby('DT_FIM_EXERC')['MB'].sum()
    df_it['Margem Operacional'] = contas.groupby('DT_FIM_EXERC')['MOP'].sum()
    df_it['Margem Liquida'] = contas.groupby('DT_FIM_EXERC')['ML'].sum()
    df_it = df_it.sort_index(ascending=False)   
    df_it = df_it.transpose()
    # cria tabela
    st._arrow_table(df_it)
    st.subheader('CAGR últimos 5 anos:')
    st.write('Receita: ', contas['R_CAGR'].iloc[-1])
    st.write('Custo: ', contas['C_CAGR'].iloc[-1])
    st.write('Despesas VGA: ', contas['DVGA_CAGR'].iloc[-1])
    st.write('Lucro liquido: ', contas['LL_CAGR'].iloc[-1]) 
#Cria função para criar tabela de balanço patrimonial
def balance_table():
    dre = arq_dre[(arq_dre['ORDEM_EXERC'] == 'ÚLTIMO') &
              (arq_dre['CD_CVM'] == ticker)]
    bpa = arq_bpa[(arq_bpa['ORDEM_EXERC'] == 'ÚLTIMO') &
            (arq_bpa['CD_CVM'] == ticker)]
    bpp = arq_bpp[(arq_bpp['ORDEM_EXERC'] == 'ÚLTIMO') &
            (arq_bpp['CD_CVM'] == ticker)]
    ativo = bpa[bpa['CD_CONTA'] == '1']
    ativo_cp = bpa[bpa['CD_CONTA'] == '1.01']
    caixa = bpa[bpa['CD_CONTA'] == '1.01.01']
    aplicacoes_fin = bpa[bpa['CD_CONTA'] == '1.01.02']
    contas_receber = bpa[bpa['CD_CONTA'] == '1.01.03']
    estoques = bpa[bpa['CD_CONTA'] == '1.01.04']
    passivo_cp = bpp[bpp['CD_CONTA'] == '2.01']
    passivo_lp = bpp[bpp['CD_CONTA'] == '2.02']
    pl = bpp[bpp['CD_CONTA'] == '2.03']
    divida_cp = bpp[bpp['CD_CONTA'] == '2.01.04']
    divida_lp = bpp[bpp['CD_CONTA'] == '2.02.01']
    divida_cp_estrangeira = bpp[bpp['CD_CONTA'] == '2.01.04.01.02']
    divida_lp_estrangeira = bpp[bpp['CD_CONTA'] == '2.02.01.01.02']
    fornecedores = bpp[bpp['CD_CONTA'] == '2.01.02']
    l_op = dre[dre['CD_CONTA'] == '3.05']
    contas = pd.DataFrame()
    contas['d_cp'] = divida_cp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['ativo_cp'] = ativo_cp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['passivo_cp'] = passivo_cp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['caixa'] = caixa.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['pl'] = pl.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['ap_fin'] = aplicacoes_fin.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['LOP'] = l_op.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['d_cp_e'] = divida_cp_estrangeira.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['d_lp_e'] = divida_lp_estrangeira.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['d_lp'] = divida_lp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['caixa_total'] = contas['caixa'] + contas['ap_fin']
    contas['d_total'] = contas['d_cp'] + contas['d_lp']
    contas['d_liquida'] = contas['d_total'] - contas['caixa_total']
    contas['d_total_$'] = contas['d_cp_e'] + contas['d_lp_e']
    contas['d_cp%'] = round(contas['d_cp'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['d_lp%'] = round(contas['d_lp'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['d_l/pl'] = round(contas['d_liquida'] / contas['pl'],2).astype(str)
    contas['d_cp/LOP'] = round(contas['d_cp'] / contas['LOP'],2).astype(str)
    contas['liquidez'] = round(contas['ativo_cp'] / contas['passivo_cp'],2).astype(str)
    contas['d_e%'] = round(contas['d_total_$'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['D_CAGR'] = round(((contas['d_total'].iloc[-1] / contas['d_total'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%' 
    contas['DL_CAGR'] = round(((contas['d_liquida'].iloc[-1] / contas['d_liquida'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%' 
    df_bt = pd.DataFrame()
    df_bt['Ativo Total'] = ativo.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Caixa'] = caixa.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Aplicações financeiras'] = aplicacoes_fin.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Contas a receber'] = contas_receber.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Estoques'] = estoques.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Passivo circulante'] = passivo_cp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Passivo não circulante'] = passivo_lp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Fornecedores'] = fornecedores.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Dívida total'] = contas.groupby('DT_FIM_EXERC')['d_total'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Patrimônio Líquido'] = pl.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_bt['Divida curto prazo'] = contas.groupby('DT_FIM_EXERC')['d_cp%'].sum()
    df_bt['Divida longo prazo'] = contas.groupby('DT_FIM_EXERC')['d_lp%'].sum()
    df_bt['Divida em moeda estrangeira'] = contas.groupby('DT_FIM_EXERC')['d_e%'].sum()
    df_bt['Dívida liquida/PL'] = contas.groupby('DT_FIM_EXERC')['d_l/pl'].sum()
    df_bt['Dívida curto prazo/Lucro Operacional'] = contas.groupby('DT_FIM_EXERC')['d_cp/LOP'].sum()
    df_bt['Liquidez corrente'] = contas.groupby('DT_FIM_EXERC')['liquidez'].sum()
    df_bt = df_bt.sort_index(ascending=False)   
    df_bt = df_bt.transpose()
    st._arrow_table(df_bt)
    st.subheader('CAGR últimos 5 anos:')
    st.write('Dívida Total: ', contas['D_CAGR'].iloc[-1]) 
    st.write('Dívida Liquida: ', contas['DL_CAGR'].iloc[-1]) 
#Cria função para criar tabela de fluxo de caixa
def clash_flow_table():
    dfc = arq_dfc[(arq_dfc['ORDEM_EXERC'] == 'ÚLTIMO') &
              (arq_dfc['CD_CVM'] == ticker)]
    ll_exercicio = dfc[dfc['CD_CONTA'] == '6.01.01.01']
    d_e_a = dfc[dfc['CD_CONTA'] == '6.01.01.02']
    ir = dfc[dfc['CD_CONTA'] == '6.01.01.07']
    juros =  dfc[dfc['CD_CONTA'] == '6.01.01.06']
    aquisicao_bens = dfc[dfc['CD_CONTA'] == '6.02.01']
    custo_bens = dfc[dfc['CD_CONTA'] == '6.02.02']
    recompra = dfc[dfc['CD_CONTA'] == '6.03.07']
    cap_div = dfc[dfc['CD_CONTA'] == '6.03.01']
    pag_div = dfc[dfc['CD_CONTA'] == '6.03.02']
    dividendo = dfc[dfc['CD_CONTA'] == '6.03.05']
    contas = pd.DataFrame()
    contas['ll_exerc'] = ll_exercicio.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['D&A'] = d_e_a.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['ir'] = ir.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['juros'] = juros.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['a_bens'] = aquisicao_bens.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['c_bens'] = custo_bens.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['FCO'] = contas['ll_exerc'] + contas['D&A'] + contas['ir'] + contas['juros']
    contas['Capex'] = contas['a_bens'] + contas['c_bens']
    contas['FCL'] = contas['FCO'] + contas['Capex']
    df_cft = pd.DataFrame()
    df_cft['FCO'] = contas.groupby('DT_FIM_EXERC')['FCO'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_cft['Capex'] = contas.groupby('DT_FIM_EXERC')['Capex'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_cft['FCL'] = contas.groupby('DT_FIM_EXERC')['FCL'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_cft['Dividendos'] = dividendo.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_cft['Captação de divida'] = cap_div.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_cft['Pagamento de divida'] = pag_div.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_cft['Compra/Venda de ações'] = recompra.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().apply(lambda x: format(x, ',').replace(',','.'))
    df_cft = df_cft.sort_index(ascending=False)   
    df_cft = df_cft.transpose()
    st._arrow_table(df_cft)
def indicadores():
    dre = arq_dre[(arq_dre['ORDEM_EXERC'] == 'ÚLTIMO') &
              (arq_dre['CD_CVM'] == ticker)]
    bpa = arq_bpa[(arq_bpa['ORDEM_EXERC'] == 'ÚLTIMO') &
            (arq_bpa['CD_CVM'] == ticker)]
    bpp = arq_bpp[(arq_bpp['ORDEM_EXERC'] == 'ÚLTIMO') &
            (arq_bpp['CD_CVM'] == ticker)]
    dfc = arq_dfc[(arq_dfc['ORDEM_EXERC'] == 'ÚLTIMO') &
              (arq_dfc['CD_CVM'] == ticker)]
    receita = dre[dre['CD_CONTA'] == '3.01']
    lb = dre[dre['CD_CONTA'] == '3.03']
    l_op = dre[dre['CD_CONTA'] == '3.05']
    ll = dre[dre['CD_CONTA'] == '3.11']
    ativo = bpa[bpa['CD_CONTA'] == '1']
    caixa = bpa[bpa['CD_CONTA'] == '1.01.01']
    aplicacoes_fin = bpa[bpa['CD_CONTA'] == '1.01.02']
    ativo_cp = bpa[bpa['CD_CONTA'] == '1.01']
    passivo_cp = bpp[bpp['CD_CONTA'] == '2.01']
    fornecedores = bpp[bpp['CD_CONTA'] == '2.01.02']
    divida_cp = bpp[bpp['CD_CONTA'] == '2.01.04']
    divida_lp = bpp[bpp['CD_CONTA'] == '2.02.01']
    divida_cp_estrangeira = bpp[bpp['CD_CONTA'] == '2.01.04.01.02']
    divida_lp_estrangeira = bpp[bpp['CD_CONTA'] == '2.02.01.01.02']
    pl = bpp[bpp['CD_CONTA'] == '2.03']
    dividendo = dfc[dfc['CD_CONTA'] == '6.03.05']
    contas = pd.DataFrame()
    contas['Receita'] = receita.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['LB'] = lb.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['LOP'] = l_op.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['LL'] = ll.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['ativo_cp'] = ativo_cp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['passivo_cp'] = passivo_cp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['pl'] = pl.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['div'] = dividendo.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['caixa'] = caixa.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['ap_fin'] = aplicacoes_fin.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)    
    contas['ativo'] = ativo.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['fornecedores'] = fornecedores.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['d_cp'] = divida_cp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['d_cp_e'] = divida_cp_estrangeira.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['d_lp_e'] = divida_lp_estrangeira.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['d_lp'] = divida_lp.groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float)
    contas['caixa_total'] = contas['caixa'] + contas['ap_fin']
    contas['d_total'] = contas['d_cp'] + contas['d_lp']
    contas['d_liquida'] = contas['d_total'] - contas['caixa_total']
    contas['d_total_$'] = contas['d_cp_e'] + contas['d_lp_e']
    contas['d_cp%'] = round(contas['d_cp'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['d_lp%'] = round(contas['d_lp'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['d_l/pl'] = round(contas['d_liquida'] / contas['pl'],2).astype(str)
    contas['d_cp/LOP'] = round(contas['d_cp'] / contas['LOP'],2).astype(str)
    contas['d_e%'] = round(contas['d_total_$'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['ROIC'] = round(contas['LOP'] / (contas['ativo'] - (contas['caixa_total'] + contas['fornecedores'])) * 100, 2).astype(str) + '%'
    contas['payout'] = round((contas['div']*-1) / contas['LL'] * 100, 2).astype(str) + '%'
    contas['MB'] = round(contas['LB'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['ML'] = round(contas['LL'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['MOP'] = round(contas['LOP'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['ROE'] = round(contas['LL'] / contas['pl'] * 100, 2).astype(str) + '%'
    contas['liquidez'] = round(contas['ativo_cp'] / contas['passivo_cp'],2).astype(str)
    df_ind = pd.DataFrame()
    df_ind['Liquidez corrente'] = contas.groupby('DT_FIM_EXERC')['liquidez'].sum()
    df_ind['Margem Bruta'] = contas.groupby('DT_FIM_EXERC')['MB'].sum()
    df_ind['Margem Operacional'] = contas.groupby('DT_FIM_EXERC')['MOP'].sum()
    df_ind['Margem Liquida'] = contas.groupby('DT_FIM_EXERC')['ML'].sum()
    df_ind['ROE'] = contas.groupby('DT_FIM_EXERC')['ROE'].sum()
    df_ind['ROIC'] = contas.groupby('DT_FIM_EXERC')['ROIC'].sum()
    df_ind['Payout'] = contas.groupby('DT_FIM_EXERC')['payout'].sum()
    df_ind['Divida curto prazo'] = contas.groupby('DT_FIM_EXERC')['d_cp%'].sum()
    df_ind['Divida longo prazo'] = contas.groupby('DT_FIM_EXERC')['d_lp%'].sum()
    df_ind['Divida em moeda estrangeira'] = contas.groupby('DT_FIM_EXERC')['d_e%'].sum()
    df_ind['Dívida liquida/PL'] = contas.groupby('DT_FIM_EXERC')['d_l/pl'].sum()
    df_ind['Dívida curto prazo/Lucro Operacional'] = contas.groupby('DT_FIM_EXERC')['d_cp/LOP'].sum()
    df_ind = df_ind.sort_index(ascending=False)   
    df_ind = df_ind.transpose()
    st._arrow_table(df_ind)
#Escolha dos gráficos a serem exibidos
init = st.selectbox(
    'Selecione a opção desejada',
    ['Indicadores enconômicos','Dados cia aberta'],
)
#Inicia programa de indicadores econômicos
if 'Indicadores enconômicos' in init:
    opcao = st.sidebar.multiselect(
        'Selecione o gráfico',
        ['Spread taxa de juros','Variação monetária - EUA','Total de ativos do FED'])    
    #Define o intervalo de data
    min_date = datetime.date(1950, 1, 1)
    start_date = st.sidebar.date_input('Data de inicio:',value=datetime.date(2018, 1, 1),min_value=min_date)
    end_date = st.sidebar.date_input('Data de final:',)
    #Escolhe o tipo de gráfico
    if opcao:
        grafico = st.radio(
            'Selecione o tipo de gráfico',
            ('Tipo 1', 'Tipo 2')
        )
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
        ['Análise Fundamentalista','Valuation','Baixar dados da CVM'])
    if 'Baixar dados da CVM' in opcao1:
        cvm_data()
    if 'Análise Fundamentalista' in opcao1:
        sa_opt = st.sidebar.selectbox(
            '',
            ['Resultado', 'Balanço patrimonial', 'Fluxo de caixa', 'Indicadores']
        )
        if 'Resultado' in sa_opt:
            cia = st.selectbox('Empresa', nome_cia)
            st.header(sa_opt)
            ticker = arq_dre.loc[arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
            income_table()
        if 'Balanço patrimonial' in sa_opt:
            cia = st.selectbox('Empresa', nome_cia)
            st.header(sa_opt)
            ticker = arq_dre.loc[arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
            balance_table()
        if 'Fluxo de caixa' in sa_opt:
            cia = st.selectbox('Empresa', nome_cia)
            st.header(sa_opt)
            ticker = arq_dre.loc[arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
            clash_flow_table()
        if 'Indicadores' in sa_opt:
            cia = st.selectbox('Empresa', nome_cia)
            st.header(sa_opt)
            ticker = arq_dre.loc[arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
            indicadores()
###