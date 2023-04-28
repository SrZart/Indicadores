import pandas as pd
import numpy as np

def formatar_data(df):
    df['DT_FIM_EXERC'] = pd.to_datetime(df['DT_FIM_EXERC'])
    df['DT_FIM_EXERC'] = df['DT_FIM_EXERC'].dt.strftime('%d-%m-%Y')
    return df
arq_dre = pd.read_csv(f'DADOS/dfp_cia_aberta_DRE_con.csv')
arq_dre = formatar_data(arq_dre)
nome_cia = arq_dre['DENOM_CIA'].unique()
nome_cia = np.sort(nome_cia)

arq_bpa = pd.read_csv(f'DADOS/dfp_cia_aberta_BPA_con.csv')
arq_bpa = formatar_data(arq_bpa)

arq_bpp = pd.read_csv(f'DADOS/dfp_cia_aberta_BPP_con.csv')
arq_bpp = formatar_data(arq_bpp)

arq_dfc = pd.read_csv(f'DADOS/dfp_cia_aberta_DFC_MI_con.csv')
arq_dfc = formatar_data(arq_dfc)

arq_dva = pd.read_csv(f'DADOS/dfp_cia_aberta_DVA_con.csv')
arq_dva = formatar_data(arq_dva)