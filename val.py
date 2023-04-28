import pandas as pd
import streamlit as st
import data as dt

def valuation():
    cia = st.selectbox('Empresa', dt.nome_cia)
    ticker = dt.arq_dre.loc[dt.arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
    dre = dt.arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpa = dt.arq_bpa.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpp = dt.arq_bpp.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dfc = dt.arq_dfc.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dva = dt.arq_dva.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")

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

    ke = (rf + b * (rm - rf))
    kd = (((contas['despesa_fin']*-1) - contas['jsp']) / contas['d_total'])
    wacc = ((ke * (contas['pl'] / (contas['d_total'] + contas['pl']))) + (kd * (contas['d_total'] / (contas['d_total'] + contas['pl']))))*(1 - contas['tax'])

    # Calcular o valor presente do FCL para cada ano
   
    vp_fcl = []
    for n in range(1, 6):
        vp = contas['FCL'].iloc[-1] / ((1 + wacc) ** n)
        vp_fcl.append(vp)

    # Calcular o valor presente da perpetuidade
    fcl_5 = contas['FCL'].iloc[-1] * (1 + g) ** 5
    vp_p = fcl_5 / ((wacc - g) * (1 + wacc) ** 5)

    # Somar os valores presentes e calcular o valor justo da ação
    vp_fcl_total_fcl = sum(vp_fcl) + vp_p
    valor_justo_fcl = vp_fcl_total_fcl / num_acoes
    valor_entrada_fcl = valor_justo_fcl - (valor_justo_fcl * tx_desc)
    # Calcular o valor presente do LOP para cada ano
    vp_lop = []
    for n in range(1, 6):
        vp_op = contas['LOP'].iloc[-1] / ((1 + wacc) ** n)
        vp_lop.append(vp_op)

     # Calcular o valor presente da perpetuidade
    lop_5 = contas['LOP'].iloc[-1] * (1 + g) ** 5
    vp_p_lop = lop_5 / ((wacc - g) * (1 + wacc) ** 5)

    # Somar os valores presentes e calcular o valor justo da ação
    vp_lop_total_lop = sum(vp_lop) + vp_p_lop
    valor_justo_lop = vp_lop_total_lop / num_acoes
    valor_entrada_lop = valor_justo_lop - (valor_justo_lop * tx_desc)

    valor_justo_fcl = valor_justo_fcl.map('{:,.2f}'.format)
    valor_justo_lop = valor_justo_lop.map('{:,.2f}'.format)
    valor_entrada_fcl = valor_entrada_fcl.map('{:,.2f}'.format)
    valor_entrada_lop = valor_entrada_lop.map('{:,.2f}'.format)
    f_wacc = round(wacc * 100, 2).astype(str) + '%'
    df_val = pd.DataFrame()
    df_val['Valor justo FCL'] = valor_justo_fcl
    df_val['Valor justo LOP'] = valor_justo_lop
    st.write('WACC:',f_wacc.iloc[-1])
    st.write('FCL:','{:,.0f}'.format(contas['FCL'].iloc[-1]).replace(',','.'))
    st.write('LOP:','{:,.0f}'.format(contas['LOP'].iloc[-1]).replace(',','.'))
    st.subheader('Valor justo por FCL:')
    st.write('R$' + valor_justo_fcl.iloc[-1])
    st.write('Preço de entrada:','R$' + valor_entrada_fcl.iloc[-1])
    st.subheader('Valor justo por Lucro operacional:')
    st.write('R$' + valor_justo_lop.iloc[-1])
    st.write('Preço de entrada:','R$' + valor_entrada_lop.iloc[-1])
    st.subheader('Histórico de valor justo')
    df_val = df_val.sort_index(ascending=False)   
    df_val = df_val.transpose()
    st._arrow_table(df_val)