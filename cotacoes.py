import plotly.express as px
import streamlit as st
import datetime
import yfinance as yf

def cotações():
    # Define o símbolo da moeda para visualizar
    ticker = st.selectbox(
                    'Selecione o ativo',
                ['BRL=X','^VIX','GC=F','SI=F','CL=F'],
                    label_visibility='collapsed')
    # Adiciona widgets interativos para o intervalo de data e o tempo gráfico
    start_date = st.sidebar.date_input('Data de início', value=datetime.date(2021, 1, 1))
    end_date = st.sidebar.date_input('Data final', value=datetime.date.today())
    # Faz a solicitação dos dados do yfinance
    df = yf.download(ticker, start=start_date, end=end_date)
    # Calcula a variação diária, semanal e mensal
    df['Var_Daily'] = df['Close'].pct_change()
    df['Var_7Days'] = df['Close'].pct_change(periods=7)
    df['Var_30Days'] = df['Close'].pct_change(periods=30)
    # Plota o gráfico usando a nova coluna de data arredondada como o eixo x e os valores médios do preço de compra como o eixo y
    fig = px.line(df, x=df.index, y='Close')
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='Cotação',
        yaxis=dict(showgrid=False) 
        )
    # Exibe o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"""Variação diária: {df['Var_Daily'].iloc[-1]:.2%} 
                | Variação nos últimos 7 dias: {df['Var_7Days'].iloc[-1]:.2%} 
                | Variação nos últimos 30 dias: {df['Var_30Days'].iloc[-1]:.2%}""")