import pandas as pd
import streamlit as st
import data as dt

def clash_flow_table():
    cia = st.selectbox('Empresa', dt.nome_cia, label_visibility='collapsed')
    ticker = dt.arq_dre.loc[dt.arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
    dfc = dt.arq_dfc.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dva = dt.arq_dva.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dre = dt.arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpa = dt.arq_bpa.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")

    contas = pd.DataFrame({
        'LOP': dre.query("CD_CONTA == '3.05'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'imposto': dre.query("CD_CONTA == '3.08'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'ativo_imob': bpa.query("CD_CONTA == '1.02.03'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'ativo_intan': bpa.query("CD_CONTA == '1.02.04'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'D&A': dva.query("CD_CONTA == '7.04.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'juros': dva.query("CD_CONTA == '7.08.03.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'jsp': dva.query("CD_CONTA == '7.08.04.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'dividendo': dva.query("CD_CONTA == '7.08.04.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
    })
    contas['ativo imob/intan'] = contas['ativo_imob'] + contas['ativo_intan']
    contas['Var_ativo'] = contas['ativo imob/intan'].iloc[-1] - contas['ativo imob/intan'].iloc[-2]
    contas['FCO'] = contas['LOP'] + (contas['D&A'] * -1) + contas['imposto'] 
    contas['Capex'] = contas['Var_ativo'] + (contas['D&A'] * -1)
    contas['FCL'] = contas['FCO'] - contas['Capex']
    contas['Dividendos e jsp'] = contas['dividendo'] + contas['jsp']
    df_cft = pd.DataFrame()
    df_cft['FCO'] = contas.groupby('DT_FIM_EXERC')['FCO'].sum().map('{:,.0f}'.format)
    df_cft['Capex'] = contas.groupby('DT_FIM_EXERC')['Capex'].sum().map('{:,.0f}'.format)
    df_cft['FCL'] = contas.groupby('DT_FIM_EXERC')['FCL'].sum().map('{:,.0f}'.format)
    df_cft['Dividendos e JSP'] = contas.groupby('DT_FIM_EXERC')['Dividendos e jsp'].sum().map('{:,.0f}'.format)
    df_cft['Pagamento de juros'] = contas.groupby('DT_FIM_EXERC')['juros'].sum().map('{:,.0f}'.format)

    df_cft = df_cft.sort_index(ascending=False)   
    df_cft = df_cft.transpose()
    st._arrow_table(df_cft)