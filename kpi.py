import pandas as pd
import streamlit as st
import data as dt


def indicadores():
    cia = st.selectbox('Empresa', dt.nome_cia, label_visibility='collapsed')
    ticker = dt.arq_dre.loc[dt.arq_dre['DENOM_CIA'] == cia, 'CD_CVM'].iloc[0]
    dre = dt.arq_dre.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpa = dt.arq_bpa.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    bpp = dt.arq_bpp.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dfc = dt.arq_dfc.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")
    dva = dt.arq_dva.query("ORDEM_EXERC == 'ÚLTIMO' and CD_CVM == @ticker")

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
        'jsp': dva.query("CD_CONTA == '7.08.04.01'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
        'dividendo': dva.query("CD_CONTA == '7.08.04.02'").groupby('DT_FIM_EXERC')['VL_CONTA'].sum().astype(float),
    })
    contas['caixa_total'] = contas['caixa'] + contas['ap_fin']
    contas['d_total'] = contas['d_cp'] + contas['d_lp']
    contas['d_liquida'] = contas['d_total'] - contas['caixa_total']
    contas['d_total_$'] = contas['d_cp_e'] + contas['d_lp_e']
    contas['Dividendos e jsp'] = contas['dividendo'] + contas['jsp']
    contas['d_cp%'] = round(contas['d_cp'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['d_lp%'] = round(contas['d_lp'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['d_l/pl'] = round(contas['d_liquida'] / contas['pl'],2).astype(str)
    contas['d_cp/LOP'] = round(contas['d_cp'] / contas['LOP'],2).astype(str)
    contas['d_e%'] = round(contas['d_total_$'] / contas['d_total'] * 100, 2).astype(str) + '%'
    contas['ROIC'] = round(contas['LOP'] / (contas['ativo'] - (contas['caixa_total'] + contas['fornecedores'])) * 100, 2).astype(str) + '%'
    contas['payout'] = round(contas['Dividendos e jsp'] / contas['LL'] * 100, 2).astype(str) + '%'
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
    st.table(df_ind)