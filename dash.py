import streamlit as st
import altair as alt
import pandas as pd
from fredapi import Fred
import datetime
import plotly.express as px
import wget
from zipfile import ZipFile

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
def formatar_data(df):
    df['DT_FIM_EXERC'] = pd.to_datetime(df['DT_FIM_EXERC'])
    df['DT_FIM_EXERC'] = df['DT_FIM_EXERC'].dt.strftime('%d-%m-%Y')
    return df

arq_dre = pd.read_csv(f'DADOS/dfp_cia_aberta_DRE_con.csv')
arq_dre = formatar_data(arq_dre)
nome_cia = arq_dre['DENOM_CIA'].unique()

arq_bpa = pd.read_csv(f'DADOS/dfp_cia_aberta_BPA_con.csv')
arq_bpa = formatar_data(arq_bpa)

arq_bpp = pd.read_csv(f'DADOS/dfp_cia_aberta_BPP_con.csv')
arq_bpp = formatar_data(arq_bpp)

arq_dfc = pd.read_csv(f'DADOS/dfp_cia_aberta_DFC_MI_con.csv')
arq_dfc = formatar_data(arq_dfc)

arq_dva = pd.read_csv(f'DADOS/dfp_cia_aberta_DVA_con.csv')
arq_dva = formatar_data(arq_dva)

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
    dre = arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    #Busca os dados 
    contas = pd.DataFrame({
        'Receita': dre.query("CD_CONTA == '3.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'Custo': dre.query("CD_CONTA == '3.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'LB': dre.query("CD_CONTA == '3.03'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'D_V': dre.query("CD_CONTA == '3.04.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'D_GA': dre.query("CD_CONTA == '3.04.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'LOP': dre.query("CD_CONTA == '3.05'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'LL': dre.query("CD_CONTA == '3.11'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
    })
    contas['D_VGA'] = contas['D_V'] + contas['D_GA']
    contas['MB'] = round(contas['LB'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['ML'] = round(contas['LL'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['MOP'] = round(contas['LOP'] / contas['Receita'] * 100, 2).astype(str) + '%'
    contas['R_CAGR'] = round(((contas['Receita'].iloc[-1] / contas['Receita'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    contas['LL_CAGR'] = round(((contas['LL'].iloc[-1] / contas['LL'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    contas['C_CAGR'] = round(((contas['Custo'].iloc[-1] / contas['Custo'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    contas['DVGA_CAGR'] = round(((contas['D_VGA'].iloc[-1] / contas['D_VGA'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    df_it = pd.DataFrame()
    df_it['Receita'] = contas.groupby('DT_FIM_EXERC')['Receita'].sum().map('{:,.0f}'.format)
    df_it['Custo'] = contas.groupby('DT_FIM_EXERC')['Custo'].sum().map('{:,.0f}'.format)
    df_it['Lucro Bruto'] = contas.groupby('DT_FIM_EXERC')['LB'].sum().map('{:,.0f}'.format)
    df_it['Despesas VGA'] = contas.groupby('DT_FIM_EXERC')['D_VGA'].sum().map('{:,.0f}'.format)
    df_it['Lucro Operacional'] = contas.groupby('DT_FIM_EXERC')['LOP'].sum().map('{:,.0f}'.format)
    df_it['Lucro Liquido'] = contas.groupby('DT_FIM_EXERC')['LL'].sum().map('{:,.0f}'.format)
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
    dre = arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpa = arq_bpa.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpp = arq_bpp.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")

    contas = pd.DataFrame({
        'ativo': bpa.query("CD_CONTA == '1'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'ativo_cp': bpa.query("CD_CONTA == '1.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'caixa': bpa.query("CD_CONTA == '1.01.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'ap_fin': bpa.query("CD_CONTA == '1.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'contas_receber': bpa.query("CD_CONTA == '1.01.03'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),    
        'estoques': bpa.query("CD_CONTA == '1.01.04'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'passivo_cp': bpp.query("CD_CONTA == '2.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'fornecedores': bpp.query("CD_CONTA == '2.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_cp': bpp.query("CD_CONTA == '2.01.04'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_cp_e': bpp.query("CD_CONTA == '2.01.04.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'passivo_lp': bpp.query("CD_CONTA == '2.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_lp': bpp.query("CD_CONTA == '2.02.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_lp_e': bpp.query("CD_CONTA == '2.02.01.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'pl': bpp.query("CD_CONTA == '2.03'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'LOP': dre.query("CD_CONTA == '3.05'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
    })
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
    df_bt['Ativo Total'] = contas.groupby('DT_FIM_EXERC')['ativo'].sum().map('{:,.0f}'.format)
    df_bt['Caixa'] = contas.groupby('DT_FIM_EXERC')['caixa'].sum().map('{:,.0f}'.format)
    df_bt['Aplicações financeiras'] = contas.groupby('DT_FIM_EXERC')['ap_fin'].sum().map('{:,.0f}'.format)
    df_bt['Estoques'] = contas.groupby('DT_FIM_EXERC')['estoques'].sum().map('{:,.0F}'.format)
    df_bt['Passivo circulante'] = contas.groupby('DT_FIM_EXERC')['passivo_cp'].sum().map('{:,.0f}'.format)
    df_bt['Passivo não circulante'] = contas.groupby('DT_FIM_EXERC')['passivo_lp'].sum().map('{:,.0f}'.format)
    df_bt['Fornecedores'] = contas.groupby('DT_FIM_EXERC')['fornecedores'].sum().map('{:,.0f}'.format)
    df_bt['Dívida total'] = contas.groupby('DT_FIM_EXERC')['d_total'].sum().map('{:,.0f}'.format)
    df_bt['Patrimônio Líquido'] = contas.groupby('DT_FIM_EXERC')['pl'].sum().map('{:,.0f}'.format)
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
    dfc = arq_dfc.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dva = arq_dva.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dre = arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    contas = pd.DataFrame({
        'LOP': dre.query("CD_CONTA == '3.05'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'imposto': dre.query("CD_CONTA == '3.08'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'll_exerc': dfc.query("CD_CONTA == '6.01.01.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'D&A': dfc.query("CD_CONTA == '6.01.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'ir': dfc.query("CD_CONTA == '6.01.01.07'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'a_bens': dfc.query("CD_CONTA == '6.02.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'c_bens': dfc.query("CD_CONTA == '6.02.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'cap_div': dfc.query("CD_CONTA == '6.03.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'pag_div': dfc.query("CD_CONTA == '6.03.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'recompra': dfc.query("CD_CONTA == '6.03.07'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'juros': dfc.query("CD_CONTA == '6.03.09'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'jsp': dva.query("CD_CONTA == '7.08.04.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'dividendo': dva.query("CD_CONTA == '7.08.04.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
    })
    contas['FCO'] = contas['LOP'] + contas['D&A'] + (contas['imposto']*-1) 
    contas['Capex'] = contas['a_bens'] + contas['c_bens']
    contas['FCL'] = contas['FCO'] + contas['Capex']
    contas['Dividendos e jsp'] = contas['dividendo'] + contas['jsp']
    df_cft = pd.DataFrame()
    df_cft['FCO'] = contas.groupby('DT_FIM_EXERC')['FCO'].sum().map('{:,.0f}'.format)
    df_cft['Capex'] = contas.groupby('DT_FIM_EXERC')['Capex'].sum().map('{:,.0f}'.format)
    df_cft['FCL'] = contas.groupby('DT_FIM_EXERC')['FCL'].sum().map('{:,.0f}'.format)
    df_cft['Dividendos e JSP'] = contas.groupby('DT_FIM_EXERC')['Dividendos e jsp'].sum().map('{:,.0f}'.format)
    df_cft['Captação de divida'] = contas.groupby('DT_FIM_EXERC')['cap_div'].sum().map('{:,.0f}'.format)
    df_cft['Pagamento de divida'] = contas.groupby('DT_FIM_EXERC')['pag_div'].sum().map('{:,.0f}'.format)
    df_cft['Compra/Venda de ações'] = contas.groupby('DT_FIM_EXERC')['recompra'].sum().map('{:,.0f}'.format)

    df_cft = df_cft.sort_index(ascending=False)   
    df_cft = df_cft.transpose()
    st._arrow_table(df_cft)
#Cria função para criar tabela de indicadores
def indicadores():
    dre = arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpa = arq_bpa.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpp = arq_bpp.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dfc = arq_dfc.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")

    contas = pd.DataFrame({
        'ativo': bpa.query("CD_CONTA == '1'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'ativo_cp': bpa.query("CD_CONTA == '1.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'caixa': bpa.query("CD_CONTA == '1.01.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'ap_fin': bpa.query("CD_CONTA == '1.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'passivo_cp': bpp.query("CD_CONTA == '2.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'fornecedores': bpp.query("CD_CONTA == '2.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_cp': bpp.query("CD_CONTA == '2.01.04'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_cp_e': bpp.query("CD_CONTA == '2.01.04.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_lp': bpp.query("CD_CONTA == '2.02.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_lp_e': bpp.query("CD_CONTA == '2.02.01.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'pl': bpp.query("CD_CONTA == '2.03'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'Receita': dre.query("CD_CONTA == '3.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'LB': dre.query("CD_CONTA == '3.03'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'LOP': dre.query("CD_CONTA == '3.05'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'LL': dre.query("CD_CONTA == '3.11'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'dividendo': dfc.query("CD_CONTA == '6.03.05'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
    })
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
    contas['payout'] = round((contas['dividendo']*-1) / contas['LL'] * 100, 2).astype(str) + '%'
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
#Cria função para realizar o valuation
def valuation():
    dre = arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpa = arq_bpa.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpp = arq_bpp.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dfc = arq_dfc.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dva = arq_dva.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")

    rf = st.sidebar.number_input('Retorno livre de risco em %:')/100
    rm = st.sidebar.number_input('Retorno de mercado em %:')/100
    g = st.sidebar.number_input('Taxa de crescimento na perpetuidade em %: ')/100
    b = st.sidebar.number_input('Beta da ação: ') 
    num_acoes = st.sidebar.number_input('Número de ações:', min_value=0)
    tx_desc = st.sidebar.number_input('Taxa de desconto em %:')/100
    contas = pd.DataFrame({
        'ativo': bpa.query("CD_CONTA == '1'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_cp': bpp.query("CD_CONTA == '2.01.04'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'd_lp': bpp.query("CD_CONTA == '2.02.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'pl': bpp.query("CD_CONTA == '2.03'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'LOP': dre.query("CD_CONTA == '3.05'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'despesa_fin': dre.query("CD_CONTA == '3.06.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'resultado_antes_ir': dre.query("CD_CONTA == '3.07'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'imposto': dre.query("CD_CONTA == '3.08'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'll_exerc': dfc.query("CD_CONTA == '6.01.01.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'D&A': dfc.query("CD_CONTA == '6.01.01.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'ir': dfc.query("CD_CONTA == '6.01.01.07'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'a_bens': dfc.query("CD_CONTA == '6.02.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'c_bens': dfc.query("CD_CONTA == '6.02.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'juros': dfc.query("CD_CONTA == '6.03.09'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'jsp': dva.query("CD_CONTA == '7.08.04.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
    })
    contas['d_total'] = contas['d_cp'] + contas['d_lp']
    contas['FCO'] = contas['LOP'] + contas['D&A'] + (contas['imposto']*-1) 
    contas['Capex'] = contas['a_bens'] + contas['c_bens']
    contas['FCL'] = contas['FCO'] + contas['Capex']
    contas['tax'] = contas['imposto'] / contas['resultado_antes_ir']
    contas['LOP_CAGR'] = round((contas['d_total'].iloc[-1] / contas['d_total'].iloc[-5]) ** (1/5) - 1)
    contas['FCL_CAGR'] = round((contas['FCL'].iloc[-1] / contas['FCL'].iloc[-5]) ** (1/5) - 1)

    ke = (rf + b * (rm - rf))
    kd = (((contas['despesa_fin']*-1) - contas['jsp']) / contas['d_total'])
    wacc = ((ke * (contas['pl'] / (contas['d_total'] + contas['pl']))) + (kd * (contas['d_total'] / (contas['d_total'] + contas['pl']))))*(1 - contas['tax'])

    # Calcular o valor presente do FCL para cada ano
   
    vp_fcl = []
    for n in range(1, 6):
        vp = contas['FCL'].iloc[-n] / ((1 + wacc) ** n)
        vp_fcl.append(vp)

    # Calcular o valor presente da perpetuidade
    fcl_5 = contas['FCL'].iloc[-1] * (1 + g) ** 5
    vp_p = fcl_5 / ((wacc - g) * (1 + wacc) ** 5)

    # Somar os valores presentes e calcular o valor justo da ação
    vp_fcl_total_fcl = sum(vp_fcl) + vp_p
    valor_justo_fcl = vp_fcl_total_fcl / num_acoes
    valor_entrada_fcl = valor_justo_fcl * tx_desc
    # Calcular o valor presente do LOP para cada ano
    vp_lop = []
    for n in range(1, 6):
        vp_op = contas['LOP'].iloc[-n] / ((1 + wacc) ** n)
        vp_lop.append(vp_op)

     # Calcular o valor presente da perpetuidade
    lop_5 = contas['LOP'].iloc[-1] * (1 + g) ** 5
    vp_p_lop = lop_5 / ((wacc - g) * (1 + wacc) ** 5)

    # Somar os valores presentes e calcular o valor justo da ação
    vp_lop_total_lop = sum(vp_lop) + vp_p_lop
    valor_justo_lop = vp_lop_total_lop / num_acoes
    valor_entrada_lop = valor_justo_lop * tx_desc

    valor_justo_fcl = valor_justo_fcl.map('{:,.2f}'.format)
    valor_justo_lop = valor_justo_lop.map('{:,.2f}'.format)
    valor_entrada_fcl = valor_entrada_fcl.map('{:,.2f}'.format)
    valor_entrada_lop = valor_entrada_lop.map('{:,.2f}'.format)
    f_wacc = round(wacc * 100, 2).astype(str) + '%'
    
    st.write('WACC:',f_wacc.iloc[-1])
    st.write('FCL:','{:,.0f}'.format(contas['FCL'].iloc[-1]))
    st.write('LOP:','{:,.0f}'.format(contas['LOP'].iloc[-1]))
    st.subheader('Valor justo por FCL:')
    st.write('R$' + valor_justo_fcl.iloc[-1])
    st.write('Preço de entrada:','R$' + valor_entrada_fcl.iloc[-1])
    st.subheader('Valor justo por Lucro operacional:')
    st.write('R$' + valor_justo_lop.iloc[-1])
    st.write('Preço de entrada:','R$' + valor_entrada_lop.iloc[-1])
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
    if 'Valuation' in opcao1:
        cia = st.selectbox('Empresa', nome_cia)
        st.header(opcao1)
        ticker = arq_dre.loc[arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
        valuation()
###