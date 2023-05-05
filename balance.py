import pandas as pd
import streamlit as st
import data as dt

def balance_table():
    cia = st.selectbox('Empresa', dt.nome_cia, label_visibility='collapsed')
    ticker = dt.arq_dre.loc[dt.arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
    dre = dt.arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpa = dt.arq_bpa.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpp = dt.arq_bpp.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")

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
    contas['d_e%'] = round(contas['d_total_$'] / contas['d_total'] * 100, 2).astype(str) + '%'
    if len(contas) >= 5:
        contas['D_CAGR'] = round(((contas['d_total'].iloc[-1] / contas['d_total'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%' 
        contas['DL_CAGR'] = round(((contas['d_liquida'].iloc[-1] / contas['d_liquida'].iloc[-5]) ** (1/5) - 1)*100, 2).astype(str) + '%' 
    else:
        contas['D_CAGR'] = 'Sem histórico suficiente'
        contas['DL_CAGR'] = 'Sem histórico suficiente'
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
    df_bt = df_bt.sort_index(ascending=False)   
    df_bt = df_bt.transpose()
    st._arrow_table(df_bt)
    st.subheader('CAGR últimos 5 anos:')
    st.markdown(f"""Dívida total: {contas['D_CAGR'].iloc[-1]} 
                | Dívida liquida: {contas['DL_CAGR'].iloc[-1]}
    """) 