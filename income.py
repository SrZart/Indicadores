import pandas as pd
import streamlit as st
import data as dt

def income_table():
    cia = st.selectbox('Empresa', dt.nome_cia)
    ticker = dt.arq_dre.loc[dt.arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
    #Cria uma lista de seleção pelo nome da empresa, e busca o código CVM
    dre = dt.arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
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
    if len(contas) >= 5:
        contas['R_CAGR'] = round(((contas['Receita'].iloc[-1] / contas['Receita'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
        contas['LL_CAGR'] = round(((contas['LL'].iloc[-1] / contas['LL'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
        contas['C_CAGR'] = round(((contas['Custo'].iloc[-1] / contas['Custo'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
        contas['DVGA_CAGR'] = round(((contas['D_VGA'].iloc[-1] / contas['D_VGA'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%'
    else:
        contas['R_CAGR'] = 'Empresa não possui 5 anos de histórico'
        contas['LL_CAGR'] = 'Empresa não possui 5 anos de histórico'
        contas['C_CAGR'] = 'Empresa não possui 5 anos de histórico'
        contas['DVGA_CAGR'] = 'Empresa não possui 5 anos de histórico'
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