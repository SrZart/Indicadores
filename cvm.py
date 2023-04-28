import wget
from zipfile import ZipFile
import streamlit as st
import pandas as pd

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