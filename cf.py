import pandas as pd
import streamlit as st
import data as dt

def clash_flow_table():
    cia = st.selectbox('Empresa', dt.nome_cia)
    ticker = dt.arq_dre.loc[dt.arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
    dfc = dt.arq_dfc.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dva = dt.arq_dva.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dre = dt.arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")

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