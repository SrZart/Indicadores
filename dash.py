import streamlit as st
import altair as alt
import pandas as pd
from fredapi import Fred
import datetime
import plotly.express as px
import wget
from zipfile import ZipFile

# Inicializa a API do FRED com sua chave de API
fred = Fred(api_key='3f8e03c66ff45fa8aff0577a3a08bbaa')

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
    if 'Spread taxa de juros' in opcao:
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
                    title='Spread entre títulos do tesouro americano de 30 anos e de 3 meses',
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
    #Define o código da variação monetária
    if 'Variação monetária - EUA' in opcao:
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
    #Define o código dos ativos do FED
    if 'Total de ativos do FED' in opcao:
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

#Inicia programa para baixar e consolidar dados de cias abertas
if 'Dados cia aberta' in init:
    opcao1 = st.sidebar.multiselect(
        'Selecione o gráfico',
        ['Baixar dados da CVM'])
    if 'Baixar dados da CVM' in opcao1:
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
                        arq_cons_data.to_csv(f'DADOS/dfp_cia_aberta_{arq_cons}_{start_year}-{end_year}.csv', index=False)
                    st.text("Dados consolidados e salvos em arquivos CSV.")
            cvm_data()
####
####