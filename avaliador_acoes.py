# Requisitos: Instale com 'pip install yfinance streamlit pandas matplotlib requests beautifulsoup4'

import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import unicodedata
import os
import requests
from bs4 import BeautifulSoup
import io
import math
import sys

# Configuração específica para o Streamlit Cloud
if 'streamlit.runtime.scriptrunner.script_run_context' in sys.modules:
    st.set_option('deprecation.showfileUploaderEncoding', False)
    st.set_option('deprecation.showPyplotGlobalUse', False)

# Tentar importar o Selenium, se não estiver disponível, usar alternativa
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Configuração da página com tratamento de erro
try:
    st.set_page_config(
        page_title="Avaliador de Ações e FIIs",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception as e:
    st.error(f"Erro ao configurar a página: {str(e)}")
    st.info("Tentando continuar com configurações padrão...")

# Lista simplificada de ações e FIIs (adicione mais conforme desejar)
ATIVOS_B3 = [
    # Bancos
    {"Codigo": "ITUB4", "Nome": "Itaú Unibanco"},
    {"Codigo": "BBDC4", "Nome": "Bradesco"},
    {"Codigo": "BBAS3", "Nome": "Banco do Brasil"},
    {"Codigo": "SANB11", "Nome": "Santander"},
    {"Codigo": "BPAC11", "Nome": "BTG Pactual"},
    {"Codigo": "BRSR6", "Nome": "Banco do Estado do Rio Grande do Sul"},
    {"Codigo": "BIDI4", "Nome": "Banco Inter"},
    {"Codigo": "BIDI11", "Nome": "Banco Inter"},
    {"Codigo": "CASH3", "Nome": "Méliuz"},
    {"Codigo": "CARD3", "Nome": "CSU CardSystem"},
    {"Codigo": "CIEL3", "Nome": "Cielo"},
    {"Codigo": "PAGS", "Nome": "PagSeguro"},
    {"Codigo": "STOC31", "Nome": "StoneCo"},
    
    # Commodities e energia
    {"Codigo": "VALE3", "Nome": "Vale"},
    {"Codigo": "PETR4", "Nome": "Petrobras PN"},
    {"Codigo": "PETR3", "Nome": "Petrobras ON"},
    {"Codigo": "SUZB3", "Nome": "Suzano"},
    {"Codigo": "CSNA3", "Nome": "CSN"},
    {"Codigo": "GGBR4", "Nome": "Gerdau"},
    {"Codigo": "USIM5", "Nome": "Usiminas"},
    {"Codigo": "JBSS3", "Nome": "JBS"},
    {"Codigo": "BRFS3", "Nome": "BRF"},
    {"Codigo": "CMIN3", "Nome": "CSN Mineração"},
    {"Codigo": "KLBN4", "Nome": "Klabin"},
    {"Codigo": "NATU3", "Nome": "Natura"},
    {"Codigo": "PRIO3", "Nome": "PetroRio"},
    {"Codigo": "RADL3", "Nome": "Raia Drogasil"},
    {"Codigo": "RENT3", "Nome": "Localiza"},
    {"Codigo": "TOTS3", "Nome": "TOTVS"},
    {"Codigo": "WEGE3", "Nome": "WEG"},
    
    # Elétricas
    {"Codigo": "ELET3", "Nome": "Eletrobras ON"},
    {"Codigo": "ELET6", "Nome": "Eletrobras PNB"},
    {"Codigo": "ENBR3", "Nome": "EDP Brasil"},
    {"Codigo": "CMIG4", "Nome": "Cemig"},
    {"Codigo": "CPLE6", "Nome": "Copel"},
    {"Codigo": "TAEE11", "Nome": "Taesa"},
    {"Codigo": "ENGI11", "Nome": "Engie Brasil"},
    {"Codigo": "EQTL3", "Nome": "Equatorial"},
    {"Codigo": "EGIE3", "Nome": "Engie Brasil Energia"},
    {"Codigo": "NEOE3", "Nome": "Neoenergia"},
    {"Codigo": "TRPL4", "Nome": "Transmissão Paulista"},
    
    # Varejo e consumo
    {"Codigo": "MGLU3", "Nome": "Magazine Luiza"},
    {"Codigo": "VIIA3", "Nome": "Via"},
    {"Codigo": "LREN3", "Nome": "Lojas Renner"},
    {"Codigo": "AMER3", "Nome": "Americanas"},
    {"Codigo": "RAIL3", "Nome": "Rumo"},
    {"Codigo": "ABEV3", "Nome": "Ambev"},
    {"Codigo": "B3SA3", "Nome": "B3"},
    {"Codigo": "CYRE3", "Nome": "Cyrela"},
    {"Codigo": "EZTC3", "Nome": "EZTEC"},
    {"Codigo": "MRVE3", "Nome": "MRV"},
    {"Codigo": "BRML3", "Nome": "BR Malls"},
    {"Codigo": "MULT3", "Nome": "Multiplan"},
    {"Codigo": "HYPE3", "Nome": "Hypera"},
    {"Codigo": "SULA11", "Nome": "SulAmérica"},
    {"Codigo": "VVAR3", "Nome": "Via Varejo"},
    {"Codigo": "CVCB3", "Nome": "CVC Brasil"},
    {"Codigo": "GRND3", "Nome": "Grendene"},
    {"Codigo": "HAPV3", "Nome": "Hapvida"},
    {"Codigo": "LWSA3", "Nome": "Locaweb"},
    {"Codigo": "MELI", "Nome": "Mercado Livre"},
    {"Codigo": "NTCO3", "Nome": "Natura & Co"},
    {"Codigo": "QUAL3", "Nome": "Qualicorp"},
    {"Codigo": "SOMA3", "Nome": "Grupo Soma"},
    {"Codigo": "TIMS3", "Nome": "TIM"},
    {"Codigo": "VIVT3", "Nome": "Telefônica Brasil"},
    
    # FIIs populares
    {"Codigo": "HGLG11", "Nome": "CSHG Logística FII"},
    {"Codigo": "MXRF11", "Nome": "Maxi Renda FII"},
    {"Codigo": "KNRI11", "Nome": "Kinea Renda Imobiliária FII"},
    {"Codigo": "VISC11", "Nome": "Vinci Shopping Centers FII"},
    {"Codigo": "XPLG11", "Nome": "XP Log FII"},
    {"Codigo": "HGBS11", "Nome": "CSHG Brasil Shopping FII"},
    {"Codigo": "BCFF11", "Nome": "BTG Pactual Fundo de Fundos FII"},
    {"Codigo": "VILG11", "Nome": "Vinci Logística FII"},
    {"Codigo": "XPML11", "Nome": "XP Malls FII"},
    {"Codigo": "RECT11", "Nome": "REC Renda Imobiliária FII"},
    {"Codigo": "RBRF11", "Nome": "RBR Alpha FII"},
    {"Codigo": "BBPO11", "Nome": "BB Progressivo II FII"},
    {"Codigo": "BRCR11", "Nome": "BTG Pactual Corporate Office Fund FII"},
    {"Codigo": "PLCR11", "Nome": "Plaza FII"},
    {"Codigo": "SHPH11", "Nome": "Shopping Pátio Higienópolis FII"},
    {"Codigo": "ALZR11", "Nome": "Alianza Trust Renda Imobiliária FII"},
    {"Codigo": "ARCT11", "Nome": "Arctium Real Estate FII"},
    {"Codigo": "ARRI11", "Nome": "Átrio Reit Recebíveis Imobiliários FII"},
    {"Codigo": "BARI11", "Nome": "Barigui Rendimentos Imobiliários FII"},
    {"Codigo": "BCRI11", "Nome": "BTG Pactual Crédito Imobiliário FII"},
    {"Codigo": "BTLG11", "Nome": "BTG Pactual Logística FII"},
    {"Codigo": "CARE11", "Nome": "Mauá Capital Recebíveis Imobiliários FII"},
    {"Codigo": "DEVA11", "Nome": "Devant Recebíveis Imobiliários FII"},
    {"Codigo": "FIIB11", "Nome": "Kinea Índice de Preços FII"},
    {"Codigo": "FLMA11", "Nome": "FLMA Crédito Imobiliário FII"},
    {"Codigo": "GGRC11", "Nome": "GGR Covepi FII"},
    {"Codigo": "HGCR11", "Nome": "CSHG Crédito Imobiliário FII"},
    {"Codigo": "HGRU11", "Nome": "CSHG Renda Urbana FII"},
    {"Codigo": "HSAF11", "Nome": "Hsi Malls Fundo de Investimento Imobiliário"},
    {"Codigo": "IRDM11", "Nome": "Iridium Recebíveis Imobiliários FII"},
    {"Codigo": "JSRE11", "Nome": "JS Real Estate Multigestão FII"},
    {"Codigo": "KFOF11", "Nome": "Kinea FoF FII"},
    {"Codigo": "KNSC11", "Nome": "Kinea Securities FII"},
    {"Codigo": "MALL11", "Nome": "Malls Brasil Plural FII"},
    {"Codigo": "MGFF11", "Nome": "Mogno Fundo de Investimento Imobiliário"},
    {"Codigo": "MORE11", "Nome": "More Real Estate FII"},
    {"Codigo": "NEWL11", "Nome": "Newport Logística FII"},
    {"Codigo": "PVBI11", "Nome": "VBI Prime Properties FII"},
    {"Codigo": "RBVA11", "Nome": "Rio Bravo Renda Varejo FII"},
    {"Codigo": "RBVO11", "Nome": "Rio Bravo Renda Varejo FII"},
    {"Codigo": "RCRB11", "Nome": "Rio Bravo Crédito Imobiliário FII"},
    {"Codigo": "RCRI11", "Nome": "REC Renda Imobiliária FII"},
    {"Codigo": "RZAK11", "Nome": "Riza Akin FII"},
    {"Codigo": "SNCI11", "Nome": "Suno Recebíveis Imobiliários FII"},
    {"Codigo": "TEPP11", "Nome": "Tellus Properties FII"},
    {"Codigo": "TRXF11", "Nome": "TRX Real Estate FII"},
    {"Codigo": "URPR11", "Nome": "Urca Prime Renda FII"},
    {"Codigo": "VERE11", "Nome": "Vértice Renda Imobiliária FII"},
    {"Codigo": "VIFI11", "Nome": "Vinci Imobiliário FII"},
    {"Codigo": "VINO11", "Nome": "Vinci Offices FII"},
    {"Codigo": "VSLH11", "Nome": "Vinci Shopping FII"},
    {"Codigo": "XPCI11", "Nome": "XP Crédito Imobiliário FII"},
    {"Codigo": "XPIN11", "Nome": "XP Industrial FII"},
    {"Codigo": "XPLG11", "Nome": "XP Log FII"},
    {"Codigo": "XPML11", "Nome": "XP Malls FII"},
    {"Codigo": "XPPR11", "Nome": "XP Properties FII"}
]

def carregar_ativos_b3():
    df = pd.DataFrame(ATIVOS_B3)
    df['NomeBusca'] = df['Nome'].str.lower().apply(lambda x: unicodedata.normalize('NFKD', str(x)).encode('ascii', errors='ignore').decode('utf-8'))
    df['CodigoBusca'] = df['Codigo'].str.lower()
    return df

def buscar_codigo_por_nome(nome, df_ativos):
    if df_ativos.empty:
        return None
    nome = nome.strip().lower()
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', errors='ignore').decode('utf-8')
    resultados = df_ativos[df_ativos['NomeBusca'].str.contains(nome)]
    if not resultados.empty:
        return resultados.iloc[0]['Codigo']
    resultados = df_ativos[df_ativos['CodigoBusca'] == nome]
    if not resultados.empty:
        return resultados.iloc[0]['Codigo']
    return None

def formatar_codigo_acao(codigo):
    """
    Formata o código da ação/FII para o padrão do Yahoo Finance
    """
    try:
        # Remover espaços e converter para maiúsculas
        codigo = codigo.strip().upper()
        
        # Verificar se o código já termina com .SA
        if not codigo.endswith('.SA'):
            codigo = f"{codigo}.SA"
            
        return codigo
    except Exception as e:
        st.error(f"❌ Erro ao formatar código: {str(e)}")
        return codigo

def buscar_dados_multiplas_fontes(codigo):
    """
    Busca dados do ativo em múltiplas fontes
    """
    dados = {
        'yahoo': None,
        'status_invest': None,
        'investing': None,
        'infomoney': None
    }
    
    # Remover .SA para usar em outras URLs
    codigo_limpo = codigo.replace('.SA', '')
    
    # 1. Yahoo Finance
    try:
        codigo_formatado = formatar_codigo_acao(codigo)
        acao = yf.Ticker(codigo_formatado)
        info_yahoo = acao.info
        historico_yahoo = acao.history(period="5y") # Buscar 5 anos para Barsi
        dividendos_yahoo = acao.dividends
        
        if info_yahoo or (historico_yahoo is not None and not historico_yahoo.empty) or (dividendos_yahoo is not None and not dividendos_yahoo.empty):
            dados['yahoo'] = {
                'info': info_yahoo,
                'historico': historico_yahoo,
                'dividendos': dividendos_yahoo
            }
    except:
        pass # Ignorar erros do Yahoo Finance
    
    # 2. Status Invest
    try:
        url_status = f"https://statusinvest.com.br/acoes/{codigo_limpo.lower()}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response_status = requests.get(url_status, headers=headers)
        info_status = {}
        
        if response_status.status_code == 200:
            soup_status = BeautifulSoup(response_status.text, 'html.parser')
            
            # Buscar Preço atual (Selector mais genérico)
            try:
                preco_element = soup_status.select_one('div.price > strong')
                if preco_element:
                    info_status['preco_atual'] = float(preco_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.'))
            except:
                pass
            
            # Buscar LPA (Selector mais genérico)
            try:
                lpa_element = soup_status.select_one('div[title=\'Lucro por Ação\'] > strong')
                if lpa_element:
                    info_status['lpa'] = float(lpa_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.'))
                else: # Tentar buscar por texto na página, caso o seletor falhe
                    lpa_element_alt = soup_status.find(string=lambda text: text and 'Lucro por Ação' in text)
                    if lpa_element_alt:
                        strong_value = lpa_element_alt.find_next('strong')
                        if strong_value:
                            info_status['lpa'] = float(strong_value.text.strip().replace('R$', '').replace('.', '').replace(',', '.'))
            except:
                pass
            
            # Buscar VPA (Selector mais genérico)
            try:
                vpa_element = soup_status.select_one('div[title=\'Valor Patrimonial por Ação\'] > strong')
                if vpa_element:
                    info_status['vpa'] = float(vpa_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.'))
                else: # Tentar buscar por texto na página
                    vpa_element_alt = soup_status.find(string=lambda text: text and 'Valor Patrimonial por Ação' in text)
                    if vpa_element_alt:
                        strong_value = vpa_element_alt.find_next('strong')
                        if strong_value:
                            info_status['vpa'] = float(strong_value.text.strip().replace('R$', '').replace('.', '').replace(',', '.'))
            except:
                pass
            
            # Buscar Dividend Yield (Selector mais genérico)
            try:
                dy_element = soup_status.select_one('div[title=\'Dividend Yield\'] > strong')
                if dy_element:
                    info_status['dividend_yield'] = float(dy_element.text.strip().replace('%', '').replace('.', '').replace(',', '.')) / 100
            except:
                pass
            
            # Buscar P/L (Selector mais genérico)
            try:
                pl_element = soup_status.select_one('div[title=\'P/L\'] > strong')
                if pl_element:
                    info_status['pl'] = float(pl_element.text.strip().replace('.', '').replace(',', '.'))
            except:
                pass
            
            # Buscar P/VP (Selector mais genérico)
            try:
                pvp_element = soup_status.select_one('div[title=\'P/VP\'] > strong')
                if pvp_element:
                    info_status['p_vp'] = float(pvp_element.text.strip().replace('.', '').replace(',', '.'))
            except:
                pass
            
            # Buscar ROE (Selector mais genérico)
            try:
                roe_element = soup_status.select_one('div[title=\'ROE\'] > strong')
                if roe_element:
                    info_status['roe'] = float(roe_element.text.strip().replace('%', '').replace('.', '').replace(',', '.')) / 100
            except:
                pass
            
            # Buscar Margem EBITDA (Selector mais genérico)
            try:
                margem_element = soup_status.select_one('div[title=\'Margem EBITDA\'] > strong')
                if margem_element:
                    info_status['margem_ebitda'] = float(margem_element.text.strip().replace('%', '').replace('.', '').replace(',', '.')) / 100
            except:
                pass
            
            # Buscar histórico de dividendos anuais (Status Invest) - Refinando busca
            try:
                dividendos_anuais = {}
                # Tentar encontrar a tabela pelo ID ou uma classe comum
                tabela_dividendos_anuais = soup_status.find('table', id='table-historical-dividends') # Exemplo de ID comum
                if not tabela_dividendos_anuais: # Tentar outra classe comum
                    tabela_dividendos_anuais = soup_status.find('table', class_='history-table')
                
                if tabela_dividendos_anuais:
                    # Assumir que a primeira coluna é o ano e a segunda é o valor pago no ano
                    # Pode ser necessário inspecionar o HTML para confirmar
                    rows = tabela_dividendos_anuais.find('tbody').find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            try:
                                ano = int(cols[0].text.strip())
                                valor_text = cols[1].text.strip() # Assumindo que a segunda coluna tem o valor
                                # Limpar e converter o valor
                                valor = float(valor_text.replace('%', '').replace('R$', '').replace('.', '').replace(',', '.').strip())
                                dividendos_anuais[ano] = valor
                            except:
                                pass # Ignorar linhas com dados inválidos
                
                    # Converter o dicionário para Series do Pandas com índice como ano
                    if dividendos_anuais:
                        series_dividendos = pd.Series(dividendos_anuais)
                        series_dividendos.index = pd.to_datetime(series_dividendos.index, format='%Y').to_period('Y').to_timestamp() # Converter ano para timestamp de final de ano
                        info_status['dividendos_anuais'] = series_dividendos
            except Exception as e:
                # print(f"Erro ao buscar dividendos anuais no Status Invest: {str(e)}") # Para debug
                pass
            
            if info_status:
                dados['status_invest'] = info_status
    except Exception as e:
        # print(f"Erro geral ao buscar dados no Status Invest: {str(e)}") # Para debug
        pass # Ignorar erros do Status Invest
    
    # 3. Investing.com
    try:
        codigo_limpo = codigo.replace('.SA', '')
        info_investing = {}
        
        # Buscar dados fundamentais (LPA, VPA) na página de resumo financeiro
        url_fundamental_investing = f"https://br.investing.com/equities/{codigo_limpo.lower()}-financial-summary"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response_fundamental_investing = requests.get(url_fundamental_investing, headers=headers)
        
        if response_fundamental_investing.status_code == 200:
            soup_fundamental_investing = BeautifulSoup(response_fundamental_investing.text, 'html.parser')
            
            # Buscar DRE para encontrar LPA - Refinando busca
            try:
                dre_div = soup_fundamental_investing.find('div', id='income-statement') # Tentar encontrar por ID
                if not dre_div: # Tentar por classe comum
                    dre_div = soup_fundamental_investing.find('section', class_='financial-statements-section') # Exemplo de classe
                
                if dre_div:
                    tabela = dre_div.find('table')
                    if tabela:
                        df_dre = pd.read_html(str(tabela))[0]
                        # Buscar linha de Lucro por Ação (pode variar a descrição ou posição)
                        # Procurar pela primeira coluna que contenha 'Lucro por Ação' ou 'Earnings Per Share'
                        lpa_row = df_dre[df_dre.iloc[:, 0].str.contains('Lucro por Ação|Earnings Per Share', na=False, case=False)]
                        if not lpa_row.empty:
                            # Obter o último valor de LPA (coluna mais à direita)
                            lpa_text = lpa_row.iloc[0, -1]
                            # Tentar converter para float (pode ter '-', parênteses, vírgulas, etc.)
                            try:
                                lpa = float(lpa_text.replace('(', '-').replace(')', '').replace('.', '').replace(',', '.').strip())
                                info_investing['lpa'] = lpa
                            except:
                                # print(f"Erro ao converter LPA Investing: {lpa_text}") # Para debug
                                pass
            except Exception as e:
                # print(f"Erro ao buscar DRE Investing: {str(e)}") # Para debug
                pass
            
            # Buscar Balanço para encontrar VPA - Refinando busca
            try:
                balanco_div = soup_fundamental_investing.find('div', id='balance-sheet') # Tentar encontrar por ID
                if not balanco_div: # Tentar por classe comum
                    balanco_div = soup_fundamental_investing.find('section', class_='financial-statements-section') # Exemplo de classe
                
                if balanco_div:
                    tabela = balanco_div.find('table')
                    if tabela:
                        df_balanco = pd.read_html(str(tabela))[0]
                        # Buscar linha de Valor Patrimonial por Ação (pode variar a descrição ou posição)
                        # Procurar pela primeira coluna que contenha 'Valor Patrimonial por Ação' ou 'Book Value Per Share'
                        vpa_row = df_balanco[df_balanco.iloc[:, 0].str.contains('Valor Patrimonial por Ação|Book Value Per Share', na=False, case=False)]
                        if not vpa_row.empty:
                            # Obter o último valor de VPA (coluna mais à direita)
                            vpa_text = vpa_row.iloc[0, -1]
                            # Tentar converter para float
                            try:
                                vpa = float(vpa_text.replace('(', '-').replace(')', '').replace('.', '').replace(',', '.').strip())
                                info_investing['vpa'] = vpa
                            except:
                                # print(f"Erro ao converter VPA Investing: {vpa_text}") # Para debug
                                pass
            except Exception as e:
                # print(f"Erro ao buscar Balanço Investing: {str(e)}") # Para debug
                pass
            
        # Buscar histórico de dividendos na página de dividendos do Investing.com - Refinando busca
        url_dividendos_investing = f"https://br.investing.com/equities/{codigo_limpo.lower()}-dividends"
        response_dividendos_investing = requests.get(url_dividendos_investing, headers=headers)
        
        if response_dividendos_investing.status_code == 200:
            soup_dividendos_investing = BeautifulSoup(response_dividendos_investing.text, 'html.parser')
            
            # Buscar tabela de dividendos - Refinando busca
            try:
                tabela_dividendos = soup_dividendos_investing.find('table', id='dividendsHistoryData') # Tentar encontrar por ID
                if not tabela_dividendos: # Tentar por classe comum
                    tabela_dividendos = soup_dividendos_investing.find('table', class_='historical_data_table') # Exemplo de classe
                
                if tabela_dividendos:
                    dividendos_investing_lista = []
                    # Encontrar o corpo da tabela
                    tbody = tabela_dividendos.find('tbody')
                    if tbody:
                        for row in tbody.find_all('tr'): # Iterar sobre as linhas do corpo
                            cols = row.find_all('td')
                            # Assumindo que a data está na primeira coluna e o valor na segunda
                            if len(cols) >= 2:
                                try:
                                    data_str = cols[0].text.strip()
                                    valor_str = cols[1].text.strip()
                                    # Converter data e valor
                                    data = pd.to_datetime(data_str, format='%d/%m/%Y')
                                    valor = float(valor_str.replace(',', '.').strip())
                                    dividendos_investing_lista.append({'data': data, 'valor': valor})
                                except:
                                    # print(f"Erro ao processar linha de dividendo Investing: {row.text}") # Para debug
                                    pass # Ignorar linhas com dados inválidos
                    
                    # Converter para DataFrame e calcular dividendos anuais
                    if dividendos_investing_lista:
                        df_dividendos_investing = pd.DataFrame(dividendos_investing_lista)
                        df_dividendos_investing.set_index('data', inplace=True)
                        df_dividendos_investing.sort_index(inplace=True)
                        # Calcular dividendos acumulados por ano
                        # O site investing.com já parece listar os dividendos por data de pagamento/ex, precisamos somar por ano
                        dividendos_anuais = df_dividendos_investing.resample('YE')['valor'].sum()
                        info_investing['dividendos_anuais'] = dividendos_anuais
            except Exception as e:
                # print(f"Erro ao buscar tabela de dividendos Investing: {str(e)}") # Para debug
                pass
        
        # Buscar dados básicos (Preço, Variação, Volume) na página principal do Investing.com - Refinando busca
        url_basico_investing = f"https://br.investing.com/equities/{codigo_limpo.lower()}"
        response_basico_investing = requests.get(url_basico_investing, headers=headers)
        if response_basico_investing.status_code == 200:
            soup_basico_investing = BeautifulSoup(response_basico_investing.text, 'html.parser')
            # Preço atual
            try:
                # Tentar seletores comuns para preço
                preco_element = soup_basico_investing.select_one('#last_last') # ID comum
                if not preco_element: # Tentar outra classe comum
                    preco_element = soup_basico_investing.select_one('div. traders-data > span.value') # Exemplo de classe
                
                if preco_element:
                    info_investing['preco_atual'] = float(preco_element.text.replace(',', '.').strip())
            except:
                pass
            # Variação
            try:
                # Tentar seletores comuns para variação
                variacao_element = soup_basico_investing.select_one('#last_last + span') # Variação geralmente ao lado do preço
                if not variacao_element: # Tentar outra classe comum
                    variacao_element = soup_basico_investing.select_one('div.traders-data > span.change-percent') # Exemplo de classe
                
                if variacao_element:
                    info_investing['variacao'] = float(variacao_element.text.replace('%', '').replace(',', '.').strip())
            except:
                pass
             # Volume
            try:
                # Tentar encontrar o volume buscando por texto ou seletores comuns
                volume_element = soup_basico_investing.find(string=lambda text: text and 'Volume' in text)
                if volume_element:
                    volume_value_element = volume_element.find_next(['span', 'strong'])
                    if volume_value_element:
                        info_investing['volume'] = volume_value_element.text.strip() # Manter como string para preservar M/K
            except Exception as e:
                # print(f"Erro ao buscar volume Investing: {str(e)}") # Para debug
                pass
        
        if info_investing:
            dados['investing'] = info_investing
    except Exception as e:
        # print(f"Erro geral ao buscar dados no Investing.com: {str(e)}") # Para debug
        pass # Ignorar erros do Investing.com
    
    # 4. InfoMoney
    try:
        codigo_limpo = codigo.replace('.SA', '')
        url_infomoney = f"https://www.infomoney.com.br/cotacoes/b3/{codigo_limpo.lower()}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response_infomoney = requests.get(url_infomoney, headers=headers)
        info_infomoney = {}
        
        if response_infomoney.status_code == 200:
            soup_infomoney = BeautifulSoup(response_infomoney.text, 'html.parser')
            
            # Buscar Preço atual (Selector mais genérico)
            try:
                preco_element = soup_infomoney.select_one('div.price > strong')
                if preco_element:
                    info_infomoney['preco_atual'] = float(preco_element.text.strip().replace('R$', '').replace('.', '').replace(',', '.'))
            except:
                pass
            
            # Buscar Variação (Selector mais genérico)
            try:
                variacao_element = soup_infomoney.select_one('div.price')
                if variacao_element:
                    variacao_element = variacao_element.find_next('div')
                    if variacao_element:
                        info_infomoney['variacao'] = float(variacao_element.text.strip().replace('%', '').replace(',', '.'))
            except:
                pass
            
            # Buscar Volume (Selector mais genérico)
            try:
                volume_element = soup_infomoney.select_one('div.volume')
                if volume_element:
                    volume_text = volume_element.find_next('div').text.strip()
                    info_infomoney['volume'] = volume_text # Manter como string
            except:
                pass
            
            # Buscar DRE para encontrar LPA - Refinando busca
            try:
                dre_div = soup_infomoney.find('div', {'id': 'demonstrativo-resultados'})
                if not dre_div: # Tentar por classe comum
                    dre_div = soup_infomoney.find('section', class_='data_tables') # Exemplo de classe
                
                if dre_div:
                    tabela = dre_div.find('table')
                    if tabela:
                        df_dre = pd.read_html(str(tabela))[0]
                        # Buscar linha de Lucro por Ação
                        lpa_row = df_dre[df_dre.iloc[:, 0].str.contains('LUCRO/PREJUÍZO POR AÇÃO|Lucro por Ação', na=False, case=False)]
                        if not lpa_row.empty:
                            # Obter o último valor de LPA (coluna mais à direita)
                            lpa_text = lpa_row.iloc[0, -1]
                            try:
                                lpa = float(lpa_text.replace('(', '-').replace(')', '').replace('.', '').replace(',', '.').strip())
                                info_infomoney['lpa'] = lpa
                            except:
                                # print(f"Erro ao converter LPA InfoMoney: {lpa_text}") # Para debug
                                pass
            except Exception as e:
                # print(f"Erro ao buscar DRE InfoMoney: {str(e)}") # Para debug
                pass
            
            # Buscar Balanço para encontrar VPA - Refinando busca
            try:
                balanco_div = soup_infomoney.find('div', {'id': 'balanco-patrimonial'})
                if not balanco_div: # Tentar por classe comum
                    balanco_div = soup_infomoney.find('section', class_='data_tables') # Exemplo de classe
                
                if balanco_div:
                    tabela = balanco_div.find('table')
                    if tabela:
                        df_balanco = pd.read_html(str(tabela))[0]
                        # Buscar linha de Valor Patrimonial por Ação
                        vpa_row = df_balanco[df_balanco.iloc[:, 0].str.contains('PATRIMÔNIO LÍQUIDO POR AÇÃO|Valor Patrimonial por Ação|Patrimônio Líquido', na=False, case=False)]
                        if not vpa_row.empty:
                            # Obter o último valor de VPA (coluna mais à direita)
                            vpa_text = vpa_row.iloc[0, -1]
                            try:
                                vpa = float(vpa_text.replace('(', '-').replace(')', '').replace('.', '').replace(',', '.').strip())
                                info_infomoney['vpa'] = vpa
                            except:
                                # print(f"Erro ao converter VPA InfoMoney: {vpa_text}") # Para debug
                                pass
            except Exception as e:
                # print(f"Erro ao buscar Balanço InfoMoney: {str(e)}") # Para debug
                pass
            
            # Buscar histórico de dividendos anuais (InfoMoney) - Refinando busca
            # InfoMoney geralmente lista proventos em uma seção separada.
            # Tentar encontrar a tabela de proventos.
            try:
                proventos_div = soup_infomoney.find('div', {'id': 'proventos'}) # Exemplo de ID
                if proventos_div:
                    tabela_proventos = proventos_div.find('table')
                    if tabela_proventos:
                        df_proventos = pd.read_html(str(tabela_proventos))[0]
                        # Converter a coluna de data para datetime e extrair o ano
                        df_proventos['Data'] = pd.to_datetime(df_proventos['Data'], format='%d/%m/%Y', errors='coerce')
                        # Filtrar linhas onde a data foi convertida com sucesso
                        df_proventos = df_proventos.dropna(subset=['Data'])
                        # Calcular o total de proventos por ano
                        dividendos_anuais = df_proventos.groupby(df_proventos['Data'].dt.year)['Valor'].sum()
                        # Converter para Series do Pandas e ajustar o índice para timestamp de final de ano
                        if not dividendos_anuais.empty:
                            series_dividendos = pd.Series(dividendos_anuais)
                            series_dividendos.index = pd.to_datetime(series_dividendos.index, format='%Y').to_period('Y').to_timestamp()
                            info_infomoney['dividendos_anuais'] = series_dividendos
            except Exception as e:
                # print(f"Erro ao buscar dividendos anuais no InfoMoney: {str(e)}") # Para debug
                pass
            
            if info_infomoney:
                dados['infomoney'] = info_infomoney
    except Exception as e:
        # print(f"Erro geral ao buscar dados no InfoMoney: {str(e)}") # Para debug
        pass # Ignorar erros do InfoMoney
    
    return dados

def obter_dados(codigo):
    """
    Função modificada para buscar dados de múltiplas fontes
    """
    try:
        dados = buscar_dados_multiplas_fontes(codigo)
        
        # Combinar dados de todas as fontes, priorizando Investing/InfoMoney para LPA/VPA e Dividendos
        info_combinado = {}
        historico = None
        dividendos_historico = None
        
        # Priorizar Investing e InfoMoney para LPA/VPA
        if dados['investing'] and ('lpa' in dados['investing'] or 'vpa' in dados['investing']):
            info_combinado.update({k: v for k, v in dados['investing'].items() if k in ['lpa', 'vpa']})
        elif dados['infomoney'] and ('lpa' in dados['infomoney'] or 'vpa' in dados['infomoney']):
            info_combinado.update({k: v for k, v in dados['infomoney'].items() if k in ['lpa', 'vpa']})
        elif dados['status_invest'] and ('lpa' in dados['status_invest'] or 'vpa' in dados['status_invest']):
            info_combinado.update({k: v for k, v in dados['status_invest'].items() if k in ['lpa', 'vpa']})
        elif dados['yahoo']:
            info_combinado.update({k: v for k, v in dados['yahoo']['info'].items() if k in ['earningsPerShare', 'bookValue']}) # Yahoo usa nomes diferentes
            if 'earningsPerShare' in info_combinado:
                info_combinado.pop('earningsPerShare')
            if 'bookValue' in info_combinado:
                info_combinado.pop('bookValue')
        
        # Priorizar Investing e Status Invest para Dividendos Históricos Anuais
        if dados['investing'] and 'dividendos_anuais' in dados['investing']:
            dividendos_historico = dados['investing']['dividendos_anuais']
        elif dados['status_invest'] and 'dividendos_anuais' in dados['status_invest']:
            dividendos_historico = dados['status_invest']['dividendos_anuais']
        elif dados['yahoo'] and 'dividendos' in dados['yahoo'] and not dados['yahoo']['dividendos'].empty: # Yahoo tem dividendos por data, não anual
            # Calcular dividendos anuais a partir do Yahoo
            df_dividendos_yahoo = dados['yahoo']['dividendos']
            df_dividendos_yahoo.index = pd.to_datetime(df_dividendos_yahoo.index) # Garantir datetime index
            dividendos_historico = df_dividendos_yahoo.resample('YE').sum()
        
        # Usar Yahoo para histórico de preços
        if dados['yahoo'] and dados['yahoo']['historico'] is not None:
            historico = dados['yahoo']['historico']
        
        # Combinar o restante dos dados, priorizando Yahoo como base
        if dados['yahoo']:
            for key, value in dados['yahoo']['info'].items():
                if key not in info_combinado:
                    info_combinado[key] = value
        
        # Complementar com dados do Status Invest (exceto LPA, VPA, DY, dividendos que já priorizamos)
        if dados['status_invest']:
            for key, value in dados['status_invest'].items():
                if key not in info_combinado and key not in ['lpa', 'vpa', 'dividend_yield', 'dividendos_anuais']:
                    info_combinado[key] = value
        
        # Complementar com dados do Investing.com (exceto LPA, VPA, dividendos que já priorizamos)
        if dados['investing']:
            for key, value in dados['investing'].items():
                if key not in info_combinado and key not in ['lpa', 'vpa', 'dividendos_anuais']:
                    info_combinado[key] = value
        
        # Complementar com dados do InfoMoney (exceto LPA, VPA que já priorizamos)
        if dados['infomoney']:
            for key, value in dados['infomoney'].items():
                if key not in info_combinado and key not in ['lpa', 'vpa']:
                    info_combinado[key] = value
        
        # Adicionar dividendos históricos anuais ao info_combinado para fácil acesso
        info_combinado['dividendos_anuais'] = dividendos_historico
        
        if not info_combinado:
            st.error(f"❌ Ativo {codigo} não encontrado em nenhuma fonte.")
            return None, None
            
        return info_combinado, historico
        
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados: {str(e)}")
        st.info("""
        💡 Dicas:
        - Verifique se o código da ação/FII está correto
        - Tente novamente em alguns minutos
        - Verifique se o ativo está listado corretamente
        - Dados foram buscados em múltiplas fontes:
          * Yahoo Finance
          * Status Invest
          * Investing.com
          * InfoMoney
        """)
        return None, None

def mostrar_dados_fundamentais(info):
    """
    Função modificada para mostrar dados de múltiplas fontes
    """
    if info is None:
        st.warning("⚠️ Não há dados fundamentais disponíveis para este ativo.")
        return
        
    st.subheader("📊 Dados Fundamentais")
    
    # Criar colunas para os dados fundamentais
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Informações Básicas")
        with st.container():
            try:
                st.write(f"**Empresa/FII:** {info.get('longName', 'N/A')}")
                st.write(f"**Setor:** {info.get('sector', 'N/A')}")
                
                # Mostrar preço principal disponível
                preco = info.get('previousClose')
                if preco is not None:
                    st.write(f"**Preço atual:** R$ {float(preco):.2f}")
                elif 'preco_atual' in info and info['preco_atual'] is not None:
                     st.write(f"**Preço atual:** R$ {float(info['preco_atual']):.2f}")
                else:
                    st.write("**Preço atual:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar informações básicas: {str(e)}")
        
        st.markdown("### Indicadores de Valuation")
        with st.container():
            try:
                # P/L
                pl = info.get('trailingPE')
                if pl is not None:
                    st.write(f"**P/L:** {float(pl):.2f}")
                elif 'pl' in info and info['pl'] is not None:
                    st.write(f"**P/L:** {float(info['pl']):.2f}")
                else:
                    st.write("**P/L:** N/A")
                    
                # P/VPA
                pvpa = info.get('priceToBook')
                if pvpa is not None:
                    st.write(f"**P/VPA:** {float(pvpa):.2f}")
                elif 'p_vp' in info and info['p_vp'] is not None:
                    st.write(f"**P/VPA:** {float(info['p_vp']):.2f}")
                else:
                    st.write("**P/VPA:** N/A")
                    
                # EV/EBITDA
                if 'enterpriseToEbitda' in info:
                    st.write(f"**EV/EBITDA:** {float(info['enterpriseToEbitda']):.2f}")
                else:
                    st.write("**EV/EBITDA:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores de valuation: {str(e)}")
    
    with col2:
        st.markdown("### Indicadores de Rentabilidade")
        with st.container():
            try:
                # Dividend Yield
                dy = info.get('dividendYield')
                if dy is not None:
                    st.write(f"**Dividend Yield:** {float(dy) * 100:.2f}%")
                elif 'dividend_yield' in info and info['dividend_yield'] is not None:
                    st.write(f"**Dividend Yield:** {float(info['dividend_yield']) * 100:.2f}%")
                else:
                    st.write("**Dividend Yield:** N/A")
                    
                # ROE
                roe = info.get('returnOnEquity')
                if roe is not None:
                    st.write(f"**ROE:** {float(roe) * 100:.2f}%")
                elif 'roe' in info and info['roe'] is not None:
                    st.write(f"**ROE:** {float(info['roe']) * 100:.2f}%")
                else:
                    st.write("**ROE:** N/A")
                    
                # Margens
                if 'grossMargins' in info:
                    st.write(f"**Margem Bruta:** {float(info['grossMargins']) * 100:.2f}%")
                else:
                    st.write("**Margem Bruta:** N/A")
                    
                if 'profitMargins' in info:
                    st.write(f"**Margem Líquida:** {float(info['profitMargins']) * 100:.2f}%")
                else:
                    st.write("**Margem Líquida:** N/A")
                
                if 'margem_ebitda' in info and info['margem_ebitda'] is not None:
                    st.write(f"**Margem EBITDA:** {float(info['margem_ebitda']) * 100:.2f}%")
                elif 'ebitdaMargins' in info and info['ebitdaMargins'] is not None:
                    st.write(f"**Margem EBITDA:** {float(info['ebitdaMargins']) * 100:.2f}%")
                else:
                    st.write("**Margem EBITDA:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores de rentabilidade: {str(e)}")

        st.markdown("### Indicadores de Endividamento")
        with st.container():
            try:
                if 'debtToEbitda' in info:
                    st.write(f"**Dívida Líquida/EBITDA:** {float(info['debtToEbitda']):.2f}")
                else:
                    st.write("**Dívida Líquida/EBITDA:** N/A")
                    
                if 'debtToEquity' in info:
                    st.write(f"**Dívida/Patrimônio Líquido:** {float(info['debtToEquity']):.2f}")
                else:
                    st.write("**Dívida/Patrimônio Líquido:** N/A")
                    
                if 'currentRatio' in info:
                    st.write(f"**Liquidez Corrente:** {float(info['currentRatio']):.2f}")
                else:
                    st.write("**Liquidez Corrente:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores de endividamento: {str(e)}")

        st.markdown("### Indicadores de Fluxo de Caixa")
        with st.container():
            try:
                if 'operatingCashflow' in info:
                    st.write(f"**Fluxo de Caixa Operacional:** R$ {float(info['operatingCashflow']):,.2f}")
                else:
                    st.write("**Fluxo de Caixa Operacional:** N/A")
                    
                if 'freeCashflow' in info:
                    st.write(f"**Fluxo de Caixa Livre:** R$ {float(info['freeCashflow']):,.2f}")
                else:
                    st.write("**Fluxo de Caixa Livre:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores de fluxo de caixa: {str(e)}")

def mostrar_grafico(historico):
    st.subheader("📈 Tendência de Preço")
    
    # Importar plotly
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import mplfinance as mpf
    
    # Criar figura com subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, 
                       row_heights=[0.7, 0.3])
    
    # Adicionar candlesticks
    fig.add_trace(go.Candlestick(
        x=historico.index,
        open=historico['Open'],
        high=historico['High'],
        low=historico['Low'],
        close=historico['Close'],
        name='Preço'
    ), row=1, col=1)
    
    # Calcular e adicionar médias móveis
    historico['MA20'] = historico['Close'].rolling(window=20).mean()
    historico['MA50'] = historico['Close'].rolling(window=50).mean()
    historico['MA200'] = historico['Close'].rolling(window=200).mean()
    
    # Adicionar médias móveis ao gráfico
    fig.add_trace(go.Scatter(
        x=historico.index,
        y=historico['MA20'],
        name='MA20',
        line=dict(color='blue', width=1)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=historico.index,
        y=historico['MA50'],
        name='MA50',
        line=dict(color='orange', width=1)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=historico.index,
        y=historico['MA200'],
        name='MA200',
        line=dict(color='purple', width=1)
    ), row=1, col=1)
    
    # Adicionar volume
    colors = ['red' if row['Open'] > row['Close'] else 'green' for index, row in historico.iterrows()]
    
    fig.add_trace(go.Bar(
        x=historico.index,
        y=historico['Volume'],
        name='Volume',
        marker_color=colors
    ), row=2, col=1)
    
    # Calcular RSI
    delta = historico['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Adicionar RSI
    fig.add_trace(go.Scatter(
        x=historico.index,
        y=rsi,
        name='RSI',
        line=dict(color='purple', width=1)
    ), row=2, col=1)
    
    # Adicionar linhas de referência do RSI
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # Configurar layout
    fig.update_layout(
        title='Gráfico em Tempo Real',
        yaxis_title='Preço (R$)',
        yaxis2_title='Volume/RSI',
        xaxis_rangeslider_visible=False,
        height=800,
        template='plotly_dark'
    )
    
    # Configurar eixos
    fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume/RSI", row=2, col=1)
    
    # Adicionar botões de zoom
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=False),
            type="date"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=list([
                    dict(label="1D",
                         method="relayout",
                         args=[{"xaxis.range": [historico.index[-1] - pd.Timedelta(days=1), historico.index[-1]]}]),
                    dict(label="1W",
                         method="relayout",
                         args=[{"xaxis.range": [historico.index[-1] - pd.Timedelta(weeks=1), historico.index[-1]]}]),
                    dict(label="1M",
                         method="relayout",
                         args=[{"xaxis.range": [historico.index[-1] - pd.Timedelta(days=30), historico.index[-1]]}]),
                    dict(label="3M",
                         method="relayout",
                         args=[{"xaxis.range": [historico.index[-1] - pd.Timedelta(days=90), historico.index[-1]]}]),
                    dict(label="1Y",
                         method="relayout",
                         args=[{"xaxis.range": [historico.index[-1] - pd.Timedelta(days=365), historico.index[-1]]}]),
                    dict(label="ALL",
                         method="relayout",
                         args=[{"xaxis.range": [historico.index[0], historico.index[-1]]}])
                ])
            )
        ]
    )
    
    # Mostrar gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar informações sobre os indicadores
    st.markdown("""
    **Indicadores Técnicos:**
    - MA20 (azul): Média móvel de 20 períodos
    - MA50 (laranja): Média móvel de 50 períodos
    - MA200 (roxo): Média móvel de 200 períodos
    - RSI: Indicador de Força Relativa (sobrecompra > 70, sobrevenda < 30)
    """)
    
    # Análise técnica automática
    st.markdown("### 📊 Análise Técnica")
    
    # Análise de tendência
    ultimo_preco = historico['Close'].iloc[-1]
    ma20_atual = historico['MA20'].iloc[-1]
    ma50_atual = historico['MA50'].iloc[-1]
    ma200_atual = historico['MA200'].iloc[-1]
    rsi_atual = rsi.iloc[-1]
    
    # Determinar tendência
    if ultimo_preco > ma20_atual and ma20_atual > ma50_atual and ma50_atual > ma200_atual:
        st.success("✅ Tendência de alta forte: Preço acima de todas as médias móveis")
    elif ultimo_preco > ma20_atual and ma20_atual > ma50_atual:
        st.success("✅ Tendência de alta: Preço acima das médias de 20 e 50 períodos")
    elif ultimo_preco < ma20_atual and ma20_atual < ma50_atual and ma50_atual < ma200_atual:
        st.warning("⚠️ Tendência de baixa forte: Preço abaixo de todas as médias móveis")
    elif ultimo_preco < ma20_atual and ma20_atual < ma50_atual:
        st.warning("⚠️ Tendência de baixa: Preço abaixo das médias de 20 e 50 períodos")
    else:
        st.info("ℹ️ Tendência lateral ou em transição")
    
    # Análise de RSI
    if rsi_atual > 70:
        st.warning(f"⚠️ RSI em sobrecompra ({rsi_atual:.1f})")
    elif rsi_atual < 30:
        st.success(f"✅ RSI em sobrevenda ({rsi_atual:.1f})")
    else:
        st.info(f"ℹ️ RSI neutro ({rsi_atual:.1f})")
    
    # Análise de volume
    volume_medio = historico['Volume'].mean()
    volume_atual = historico['Volume'].iloc[-1]
    
    if volume_atual > volume_medio * 1.5:
        st.info("📊 Volume acima da média - Possível movimento significativo")
    elif volume_atual < volume_medio * 0.5:
        st.info("📊 Volume abaixo da média - Movimento fraco")

def mostrar_indicadores_historicos(acao):
    st.subheader("📊 Evolução dos Indicadores")
    
    try:
        # Definir os períodos a serem tentados
        periodos = ['5y', '2y', '1y', '6mo', '3mo']
        
        # Loop para tentar obter histórico com diferentes períodos
        for periodo in periodos:
            try:
                historico_indicadores = acao.history(period=periodo, interval="1d")
                if historico_indicadores is not None and not historico_indicadores.empty:
                    st.info(f"ℹ️ Dados históricos obtidos para o período de {periodo}")
                    break # Sai do loop se obtiver dados com sucesso
            except Exception as e:
                # Ignora erros para tentar o próximo período
                pass # Corrigido: Apenas ignora e continua o loop

        if historico_indicadores is None or historico_indicadores.empty:
            st.warning("⚠️ Não foi possível obter dados históricos para este ativo.")
            st.info("""
            💡 Dicas:
            1. Verifique se o ativo está listado corretamente
            2. Alguns ativos podem ter dados limitados
            3. Tente novamente em alguns minutos
            4. Para FIIs, alguns indicadores podem não estar disponíveis
            """)
            return
        
        # Criar colunas para os gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de P/L Histórico
            try:
                if 'trailingPE' in acao.info and acao.info['trailingPE'] is not None:
                    st.markdown("### P/L Histórico")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    # Calcular P/L histórico usando preço e lucro por ação
                    if 'earningsPerShare' in acao.info and acao.info['earningsPerShare'] is not None and acao.info['earningsPerShare'] > 0:
                        pl_historico = historico_indicadores['Close'] / acao.info['earningsPerShare']
                        pl_historico.plot(ax=ax, color='#4CAF50', linewidth=2)
                        ax.set_ylabel("P/L")
                        ax.grid(True, linestyle='--', alpha=0.7)
                        st.pyplot(fig)
                    else:
                        st.info("ℹ️ Dados de LPA não disponíveis para cálculo do P/L histórico.")
            except Exception as e:
                st.info("ℹ️ Não foi possível gerar o gráfico de P/L histórico.")
            
            # Gráfico de Dividend Yield Histórico
            try:
                if not historico_indicadores['Dividends'].empty:
                    st.markdown("### Dividend Yield Histórico")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    # Calcular DY histórico
                    dy_historico = (historico_indicadores['Dividends'] / historico_indicadores['Close']) * 100
                    dy_historico.plot(ax=ax, color='#FF9800', linewidth=2)
                    ax.set_ylabel("Dividend Yield (%)")
                    ax.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig)
                else:
                    st.info("ℹ️ Dados de dividendos não disponíveis para este período.")
            except Exception as e:
                st.info("ℹ️ Não foi possível gerar o gráfico de Dividend Yield histórico.")
        
        with col2:
            # Gráfico de ROE Histórico
            try:
                if 'returnOnEquity' in acao.info and acao.info['returnOnEquity'] is not None:
                    st.markdown("### ROE Histórico")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    # Usar ROE atual como referência
                    roe_atual = acao.info['returnOnEquity'] * 100
                    ax.axhline(y=roe_atual, color='#9C27B0', linestyle='-', label=f'ROE Atual: {roe_atual:.2f}%')
                    ax.set_ylabel("ROE (%)")
                    ax.grid(True, linestyle='--', alpha=0.7)
                    ax.legend()
                    st.pyplot(fig)
                else:
                    st.info("ℹ️ Dados de ROE não disponíveis.")
            except Exception as e:
                st.info("ℹ️ Não foi possível gerar o gráfico de ROE histórico.")
            
            # Gráfico de Margem EBITDA Histórica
            try:
                if 'ebitdaMargins' in acao.info and acao.info['ebitdaMargins'] is not None:
                    st.markdown("### Margem EBITDA Histórica")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    # Usar margem EBITDA atual como referência
                    margem_atual = acao.info['ebitdaMargins'] * 100
                    ax.axhline(y=margem_atual, color='#E91E63', linestyle='-', label=f'Margem Atual: {margem_atual:.2f}%')
                    ax.set_ylabel("Margem EBITDA (%)")
                    ax.grid(True, linestyle='--', alpha=0.7)
                    ax.legend()
                    st.pyplot(fig)
                else:
                    st.info("ℹ️ Dados de Margem EBITDA não disponíveis.")
            except Exception as e:
                st.info("ℹ️ Não foi possível gerar o gráfico de Margem EBITDA histórica.")
        
        # Adicionar mais indicadores em uma nova linha
        col3, col4 = st.columns(2)
        
        with col3:
            # Gráfico de Dívida/PL Histórico
            try:
                if 'debtToEquity' in acao.info and acao.info['debtToEquity'] is not None:
                    st.markdown("### Dívida/PL Histórico")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    # Usar Dívida/PL atual como referência
                    debt_equity_atual = acao.info['debtToEquity']
                    ax.axhline(y=debt_equity_atual, color='#F44336', linestyle='-', label=f'Dívida/PL Atual: {debt_equity_atual:.2f}')
                    ax.set_ylabel("Dívida/PL")
                    ax.grid(True, linestyle='--', alpha=0.7)
                    ax.legend()
                    st.pyplot(fig)
                else:
                    st.info("ℹ️ Dados de Dívida/PL não disponíveis.")
            except Exception as e:
                st.info("ℹ️ Não foi possível gerar o gráfico de Dívida/PL histórico.")
        
        with col4:
            # Gráfico de P/VPA Histórico
            try:
                if 'priceToBook' in acao.info and acao.info['priceToBook'] is not None:
                    st.markdown("### P/VPA Histórico")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    # Calcular P/VPA histórico usando preço e VPA
                    if 'bookValue' in acao.info and acao.info['bookValue'] is not None and acao.info['bookValue'] > 0:
                        pvpa_historico = historico_indicadores['Close'] / acao.info['bookValue']
                        pvpa_historico.plot(ax=ax, color='#3F51B5', linewidth=2)
                        ax.set_ylabel("P/VPA")
                        ax.grid(True, linestyle='--', alpha=0.7)
                        st.pyplot(fig)
                    else:
                        st.info("ℹ️ Dados de VPA não disponíveis para cálculo do P/VPA histórico.")
            except Exception as e:
                st.info("ℹ️ Não foi possível gerar o gráfico de P/VPA histórico.")
        
        # Adicionar nota explicativa
        st.info("""
        **Nota:** Alguns indicadores mostram apenas o valor atual como referência (linha horizontal) 
        devido à limitação de dados históricos disponíveis no Yahoo Finance. 
        Os gráficos de P/L, Dividend Yield e P/VPA mostram a evolução histórica quando os dados estão disponíveis.
        """)
        
    except Exception as e:
        st.warning(f"⚠️ Erro ao gerar os gráficos de indicadores históricos: {str(e)}")
        st.info("""
        💡 Dicas:
        1. Verifique se o ativo está listado corretamente
        2. Alguns indicadores podem não estar disponíveis para este ativo
        3. Tente novamente em alguns minutos
        4. Para FIIs, alguns indicadores podem não ser aplicáveis
        """)

def analise_temporal(historico):
    st.subheader("⏱️ Análise Temporal")
    historico.index = historico.index.tz_localize(None)
    tres_meses_atras = datetime.now() - timedelta(days=90)
    dados_3m = historico[historico.index >= tres_meses_atras]
    variacao_3m = ((dados_3m['Close'].iloc[-1] / dados_3m['Close'].iloc[0]) - 1) * 100 if not dados_3m.empty else 0
    seis_meses_atras = datetime.now() - timedelta(days=180)
    dados_6m = historico[historico.index >= seis_meses_atras]
    variacao_6m = ((dados_6m['Close'].iloc[-1] / dados_6m['Close'].iloc[0]) - 1) * 100 if not dados_6m.empty else 0
    variacao_1a = ((historico['Close'].iloc[-1] / historico['Close'].iloc[0]) - 1) * 100 if not historico.empty else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(): # Usando container para agrupar
            st.markdown("### Variação 3 meses")
            st.metric(label="", value=f"{variacao_3m:.2f}%")
    with col2:
        with st.container(): # Usando container para agrupar
            st.markdown("### Variação 6 meses")
            st.metric(label="", value=f"{variacao_6m:.2f}%")
    with col3:
        with st.container(): # Usando container para agrupar
            st.markdown("### Variação 1 ano")
            st.metric(label="", value=f"{variacao_1a:.2f}%")

# ====== NOVO: Análise Setorial e Notícias ======
def buscar_noticias_multiplas_fontes(codigo):
    """
    Busca notícias de múltiplas fontes para o ativo
    """
    noticias = []
    
    # Remover .SA se presente
    codigo = codigo.replace('.SA', '')
    
    # 1. Buscar no Yahoo Finance
    try:
        ticker_obj = yf.Ticker(f"{codigo}.SA")
        noticias_yahoo = ticker_obj.news
        if noticias_yahoo:
            for n in noticias_yahoo:
                noticias.append({
                    'titulo': n['title'],
                    'link': n['link'],
                    'fonte': n.get('publisher', 'Yahoo Finance'),
                    'data': datetime.fromtimestamp(n['providerPublishTime']).strftime('%d/%m/%Y %H:%M')
                })
    except:
        pass
    
    # 2. Buscar no InfoMoney
    try:
        url = f"https://www.infomoney.com.br/cotacoes/b3/{codigo.lower()}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            noticias_div = soup.find('div', {'class': 'news-list'})
            if noticias_div:
                for noticia in noticias_div.find_all('article'):
                    try:
                        titulo = noticia.find('h3').text.strip()
                        link = noticia.find('a')['href']
                        if not link.startswith('http'):
                            link = 'https://www.infomoney.com.br' + link
                        data = noticia.find('time').text.strip()
                        noticias.append({
                            'titulo': titulo,
                            'link': link,
                            'fonte': 'InfoMoney',
                            'data': data
                        })
                    except:
                        continue
    except:
        pass
    
    # 3. Buscar no Investing.com
    try:
        url = f"https://br.investing.com/equities/{codigo.lower()}-news"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            noticias_div = soup.find('div', {'class': 'largeTitle'})
            if noticias_div:
                for noticia in noticias_div.find_all('article'):
                    try:
                        titulo = noticia.find('a').text.strip()
                        link = noticia.find('a')['href']
                        if not link.startswith('http'):
                            link = 'https://br.investing.com' + link
                        data = noticia.find('span', {'class': 'date'}).text.strip()
                        noticias.append({
                            'titulo': titulo,
                            'link': link,
                            'fonte': 'Investing.com',
                            'data': data
                        })
                    except:
                        continue
    except:
        pass
    
    # 4. Buscar no Status Invest
    try:
        url = f"https://statusinvest.com.br/acoes/{codigo.lower()}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            noticias_div = soup.find('div', {'class': 'news-list'})
            if noticias_div:
                for noticia in noticias_div.find_all('div', {'class': 'news-item'}):
                    try:
                        titulo = noticia.find('a').text.strip()
                        link = noticia.find('a')['href']
                        if not link.startswith('http'):
                            link = 'https://statusinvest.com.br' + link
                        data = noticia.find('span', {'class': 'date'}).text.strip()
                        noticias.append({
                            'titulo': titulo,
                            'link': link,
                            'fonte': 'Status Invest',
                            'data': data
                        })
                    except:
                        continue
    except:
        pass
    
    # Ordenar notícias por data (mais recentes primeiro)
    noticias.sort(key=lambda x: x['data'], reverse=True)
    
    return noticias

def analise_setorial_noticias(info, codigo_acao):
    st.subheader("🌐 Análise Setorial e Notícias")
    setor = info.get('sector', 'N/A')
    explicacao = {
        'Financial Services': 'Setor financeiro tende a ser resiliente, mas sensível a juros. Inclui bancos, seguradoras e serviços de investimento.',
        'Energy': 'Setor de energia pode ser cíclico e sensível a commodities e geopolítica. Inclui petróleo, gás e energias renováveis.',
        'Utilities': 'Setor de utilidade pública costuma ser defensivo e regulado. Inclui empresas de energia elétrica, água e gás.',
        'Real Estate': 'Setor imobiliário é sensível a juros, inflação e ciclos econômicos. Inclui construtoras, incorporadoras e fundos imobiliários (FIIs).',
        'Consumer Defensive': 'Setor defensivo, menos sensível a crises econômicas. Inclui alimentos, bebidas, produtos domésticos e higiene.',
        'Basic Materials': 'Setor de commodities é cíclico e depende do mercado global e preços das matérias-primas. Inclui mineração, siderurgia, papel e celulose.',
        'Industrials': 'Setor industrial depende do crescimento econômico e investimento em infraestrutura. Inclui bens de capital, transporte e serviços industriais.',
        'Healthcare': 'Setor de saúde tende a ser resiliente. Inclui hospitais, laboratórios e farmacêuticas.',
        'Technology': 'Setor de tecnologia pode ter alto crescimento, mas também volatilidade. Inclui software, hardware e serviços de TI.',
        'Consumer Cyclical': 'Setor cíclico, sensível ao consumo e renda disponível. Inclui varejo (não defensivo), viagens e lazer.',
        'Communication Services': 'Setor de serviços de comunicação. Inclui telecomunicações e mídia.',
        'N/A': 'Setor não informado.'
    }
    st.write(f"**Setor:** **{setor}**")
    st.info(explicacao.get(setor, 'Setor não identificado ou sem explicação detalhada disponível.'))
    st.markdown("---")
    
    st.markdown("### 📰 Notícias Recentes")
    try:
        with st.spinner('Buscando notícias recentes...'):
            noticias = buscar_noticias_multiplas_fontes(codigo_acao)
            
            if noticias:
                for n in noticias[:10]:  # Exibir as 10 notícias mais recentes
                    with st.container():
                        st.markdown(f"**[{n['titulo']}]({n['link']})**")
                        st.markdown(f"*Fonte: {n['fonte']} - {n['data']}* <br>", unsafe_allow_html=True)
                        st.markdown("---")
            else:
                st.info("""
                Nenhuma notícia recente encontrada para este ativo.
                
                **Dicas:**
                - Verifique se o código do ativo está correto
                - Alguns ativos podem ter menos cobertura na mídia
                - Tente novamente em alguns minutos
                - Verifique se o ativo está listado corretamente
                """)
                
    except Exception as e:
        st.warning(f"Não foi possível buscar notícias: {str(e)}")
        st.info("""
        **Dicas:**
        - Verifique se o código do ativo está correto
        - Alguns ativos podem ter menos cobertura na mídia
        - Tente novamente em alguns minutos
        - Verifique se o ativo está listado corretamente
        """)

# ====== MELHORIA: Recomendações personalizadas ======
def analise_sugestiva(info, perfil):
    st.subheader("📌 Recomendações por Horizonte de Investimento e Perfil")
    
    # Definir pesos por perfil
    pesos = {
        'Crescimento (busca valorização)': {
            'roe': 3,
            'pl': 2,
            'crescimento_lucro': 3,
            'margem_ebitda': 2,
            'dividend_yield': 1,
            'divida_ebitda': 2,
            'liquidez': 1
        },
        'Dividendos (busca renda passiva)': {
            'dividend_yield': 3,
            'payout': 2,
            'divida_ebitda': 2,
            'liquidez': 2,
            'roe': 1,
            'pl': 1,
            'crescimento_lucro': 1
        },
        'Baixa tolerância a risco': {
            'divida_ebitda': 3,
            'liquidez': 3,
            'dividend_yield': 2,
            'margem_ebitda': 2,
            'pl': 1,
            'roe': 1
        },
        'Alta tolerância a risco': {
            'crescimento_lucro': 3,
            'roe': 2,
            'pl': 2,
            'margem_ebitda': 2,
            'divida_ebitda': 1
        },
        'Neutro': {
            'roe': 2,
            'pl': 2,
            'dividend_yield': 2,
            'divida_ebitda': 2,
            'liquidez': 2
        }
    }

    # Obter indicadores
    pl = info.get('trailingPE')
    dy = info.get('dividendYield')
    roe = info.get('returnOnEquity')
    debt_equity = info.get('debtToEquity')
    price_to_book = info.get('priceToBook')
    ev_ebitda = info.get('enterpriseToEbitda')
    debt_ebitda = info.get('debtToEbitda')
    current_ratio = info.get('currentRatio')
    payout_ratio = info.get('payoutRatio')
    ebitda_margins = info.get('ebitdaMargins')
    operating_margins = info.get('operatingMargins')
    operating_cashflow = info.get('operatingCashflow')
    free_cashflow = info.get('freeCashflow')
    
    # Tentar obter crescimento do lucro (se disponível)
    try:
        acao = yf.Ticker(info.get('symbol'))
        historico = acao.history(period="2y")
        if not historico.empty and 'earningsPerShare' in info:
            lpa_atual = info['earningsPerShare']
            lpa_anterior = historico['Close'].iloc[-252] / pl if pl is not None else None
            if lpa_anterior and lpa_anterior > 0:
                crescimento_lucro = (lpa_atual - lpa_anterior) / lpa_anterior
            else:
                crescimento_lucro = None
        else:
            crescimento_lucro = None
    except:
        crescimento_lucro = None

    sugestoes = []
    score = 0
    max_score = 0

    # Obter pesos do perfil selecionado
    perfil_pesos = pesos.get(perfil, pesos['Neutro'])
    
    # Análise para perfil de Crescimento
    if 'crescimento' in perfil.lower():
        # ROE
        if roe is not None:
            peso = perfil_pesos['roe']
            max_score += peso * 2
            if roe > 0.15:
                sugestoes.append(f"📈 ROE forte ({roe*100:.1f}%). Excelente para crescimento.")
                score += peso * 2
            elif roe > 0.08:
                sugestoes.append(f"✅ ROE moderado ({roe*100:.1f}%). Aceitável para crescimento.")
                score += peso
            else:
                sugestoes.append(f"⚠️ ROE baixo ({roe*100:.1f}%). Atenção para perfil crescimento.")
                score -= peso

        # Crescimento do Lucro
        if crescimento_lucro is not None:
            peso = perfil_pesos['crescimento_lucro']
            max_score += peso * 2
            if crescimento_lucro > 0.15:
                sugestoes.append(f"📈 Crescimento do lucro forte ({crescimento_lucro*100:.1f}%). Muito positivo.")
                score += peso * 2
            elif crescimento_lucro > 0.05:
                sugestoes.append(f"✅ Crescimento do lucro moderado ({crescimento_lucro*100:.1f}%).")
                score += peso
            else:
                sugestoes.append(f"⚠️ Crescimento do lucro baixo ({crescimento_lucro*100:.1f}%).")
                score -= peso

        # P/L
        if pl is not None:
            peso = perfil_pesos['pl']
            max_score += peso
            if pl < 15:
                sugestoes.append(f"✅ P/L razoável ({pl:.1f}). Bom para crescimento.")
                score += peso
            elif pl < 25:
                sugestoes.append(f"ℹ️ P/L moderado ({pl:.1f}).")
                score += peso/2
            else:
                sugestoes.append(f"⚠️ P/L elevado ({pl:.1f}).")
                score -= peso

    # Análise para perfil de Dividendos
    if 'dividendos' in perfil.lower():
        # Dividend Yield
        if dy is not None:
            peso = perfil_pesos['dividend_yield']
            max_score += peso * 2
            if dy > 0.06:
                sugestoes.append(f"💰 Excelente Dividend Yield ({dy*100:.1f}%).")
                score += peso * 2
            elif dy > 0.04:
                sugestoes.append(f"✅ Bom Dividend Yield ({dy*100:.1f}%).")
                score += peso
            else:
                sugestoes.append(f"⚠️ Dividend Yield baixo ({dy*100:.1f}%).")
                score -= peso

        # Payout
        if payout_ratio is not None:
            peso = perfil_pesos['payout']
            max_score += peso
            if 0.4 <= payout_ratio <= 0.7:
                sugestoes.append(f"✅ Payout saudável ({payout_ratio*100:.1f}%).")
                score += peso
            elif payout_ratio > 0.7:
                sugestoes.append(f"⚠️ Payout elevado ({payout_ratio*100:.1f}%).")
                score -= peso
            else:
                sugestoes.append(f"ℹ️ Payout baixo ({payout_ratio*100:.1f}%).")
                score += peso/2

    # Análise para perfil de Baixo Risco
    if 'baixa' in perfil.lower():
        # Dívida/EBITDA
        if debt_ebitda is not None:
            peso = perfil_pesos['divida_ebitda']
            max_score += peso * 2
            if debt_ebitda < 2:
                sugestoes.append(f"💪 Dívida/EBITDA baixa ({debt_ebitda:.1f}). Excelente para perfil conservador.")
                score += peso * 2
            elif debt_ebitda < 3.5:
                sugestoes.append(f"✅ Dívida/EBITDA moderada ({debt_ebitda:.1f}).")
                score += peso
            else:
                sugestoes.append(f"⚠️ Dívida/EBITDA elevada ({debt_ebitda:.1f}).")
                score -= peso

        # Liquidez
        if current_ratio is not None:
            peso = perfil_pesos['liquidez']
            max_score += peso * 2
            if current_ratio > 1.8:
                sugestoes.append(f"💪 Excelente liquidez ({current_ratio:.1f}).")
                score += peso * 2
            elif current_ratio > 1.2:
                sugestoes.append(f"✅ Boa liquidez ({current_ratio:.1f}).")
                score += peso
            else:
                sugestoes.append(f"⚠️ Liquidez baixa ({current_ratio:.1f}).")
                score -= peso

    # Análise para perfil de Alto Risco
    if 'alta' in perfil.lower():
        # Crescimento do Lucro
        if crescimento_lucro is not None:
            peso = perfil_pesos['crescimento_lucro']
            max_score += peso * 2
            if crescimento_lucro > 0.20:
                sugestoes.append(f"📈 Crescimento do lucro muito forte ({crescimento_lucro*100:.1f}%).")
                score += peso * 2
            elif crescimento_lucro > 0.10:
                sugestoes.append(f"✅ Crescimento do lucro bom ({crescimento_lucro*100:.1f}%).")
                score += peso
            else:
                sugestoes.append(f"ℹ️ Crescimento do lucro moderado ({crescimento_lucro*100:.1f}%).")
                score += peso/2

        # ROE
        if roe is not None:
            peso = perfil_pesos['roe']
            max_score += peso
            if roe > 0.20:
                sugestoes.append(f"📈 ROE muito forte ({roe*100:.1f}%).")
                score += peso
            elif roe > 0.15:
                sugestoes.append(f"✅ ROE forte ({roe*100:.1f}%).")
                score += peso/2

    # Análise para perfil Neutro
    if 'neutro' in perfil.lower():
        # ROE
        if roe is not None:
            peso = perfil_pesos['roe']
            max_score += peso
            if roe > 0.12:
                sugestoes.append(f"✅ ROE bom ({roe*100:.1f}%).")
                score += peso
            elif roe > 0.08:
                sugestoes.append(f"ℹ️ ROE moderado ({roe*100:.1f}%).")
                score += peso/2

        # P/L
        if pl is not None:
            peso = perfil_pesos['pl']
            max_score += peso
            if 10 <= pl <= 20:
                sugestoes.append(f"✅ P/L adequado ({pl:.1f}).")
                score += peso
            elif 5 <= pl < 10 or 20 < pl <= 25:
                sugestoes.append(f"ℹ️ P/L moderado ({pl:.1f}).")
                score += peso/2
            else:
                sugestoes.append(f"⚠️ P/L fora da faixa ideal ({pl:.1f}).")
                score -= peso

    # Análise de Margens (comum a todos os perfis)
    if ebitda_margins is not None:
        peso = perfil_pesos.get('margem_ebitda', 1)
        max_score += peso
        if ebitda_margins > 0.20:
            sugestoes.append(f"📈 Margem EBITDA forte ({ebitda_margins*100:.1f}%).")
            score += peso
        elif ebitda_margins > 0.15:
            sugestoes.append(f"✅ Margem EBITDA boa ({ebitda_margins*100:.1f}%).")
            score += peso/2
        else:
            sugestoes.append(f"ℹ️ Margem EBITDA moderada ({ebitda_margins*100:.1f}%).")
            score += peso/3

    # Calcular score final (0-10)
    if max_score > 0:
        score_final = max(0, min(10, round((score / max_score) * 10)))
    else:
        score_final = 0

    # Exibir resultados
    st.markdown("--- ")
    st.subheader("Sumário e Score Fundamental")
    st.write(f"**Perfil Selecionado:** {perfil}")
    st.write(f"**Score Fundamental (0-10):** **{score_final}/10**")
    
    if score_final >= 8:
        st.success("⭐ Análise Fundamentalista Forte para o perfil.")
    elif score_final >= 5:
        st.info("✅ Análise Fundamentalista Moderada para o perfil.")
    else:
        st.warning("⚠️ Análise Fundamentalista Apresenta Pontos de Atenção para o perfil.")

    st.markdown("--- ")
    st.subheader("Detalhamento das Sugestões:")
    if not sugestoes:
        st.info("Sem alertas ou sugestões relevantes com base nos indicadores e perfil selecionado.")
    for s in sugestoes:
        if "📈" in s or "💰" in s or "💪" in s or "✅" in s:
            st.success(s)
        elif "⚠️" in s:
            st.warning(s)
        else:
            st.info(s)

    # Adicionar nota sobre limitações
    st.info("""
    **Nota:** Esta análise é baseada em dados disponíveis no Yahoo Finance e pode não refletir 
    todas as nuances do ativo. Recomenda-se complementar com outras fontes de informação e 
    análise fundamentalista mais detalhada.
    """)

def buscar_acoes_tradingview():
    """
    Busca todas as ações listadas no TradingView Screener
    """
    if not SELENIUM_AVAILABLE:
        st.error("❌ O módulo Selenium não está disponível. Por favor, instale-o usando: pip install selenium webdriver_manager")
        st.info("💡 Alternativa: Use a lista predefinida de ações ou adicione manualmente os códigos desejados.")
        return []
        
    try:
        st.info("🔄 Iniciando busca de ações no TradingView...")
        
        # Configurar o Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Inicializar o driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            # Acessar o TradingView Screener
            driver.get("https://br.tradingview.com/screener/")
            
            # Aguardar o carregamento da página
            time.sleep(5)  # Aguardar carregamento inicial
            
            # Aguardar até que a tabela de ações seja carregada
            wait = WebDriverWait(driver, 20)
            tabela = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tv-screener-table")))
            
            # Extrair dados das ações
            acoes = []
            linhas = tabela.find_elements(By.TAG_NAME, "tr")
            
            for linha in linhas[1:]:  # Pular o cabeçalho
                colunas = linha.find_elements(By.TAG_NAME, "td")
                if len(colunas) >= 2:
                    codigo = colunas[0].text.strip()
                    nome = colunas[1].text.strip()
                    if codigo and nome:
                        acoes.append({
                            "Codigo": codigo,
                            "Nome": nome
                        })
            
            if acoes:
                # Atualizar a lista global de ativos
                global ATIVOS_B3
                ATIVOS_B3 = acoes
                return acoes
            else:
                st.warning("⚠️ Não foi possível encontrar ações no TradingView.")
                return []
                
        finally:
            driver.quit()
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar ações no TradingView: {str(e)}")
        st.info("💡 Alternativa: Use a lista predefinida de ações ou adicione manualmente os códigos desejados.")
        return []

def buscar_acoes_brasileiras():
    """
    Busca todas as ações brasileiras usando a API do Yahoo Finance
    """
    try:
        # Lista de índices brasileiros para buscar ações
        indices = ['^BVSP', '^IBXX']  # Bovespa e IBXX
        
        todas_acoes = []
        for indice in indices:
            ticker = yf.Ticker(indice)
            # Buscar componentes do índice
            componentes = ticker.info.get('components', [])
            if componentes:
                for componente in componentes:
                    if isinstance(componente, str) and componente.endswith('.SA'):
                        codigo = componente.replace('.SA', '')
                        try:
                            info = yf.Ticker(componente).info
                            nome = info.get('longName', codigo)
                            todas_acoes.append({
                                "Codigo": codigo,
                                "Nome": nome
                            })
                        except:
                            continue
        
        if todas_acoes:
            # Atualizar a lista global de ativos
            global ATIVOS_B3
            ATIVOS_B3 = todas_acoes
            return todas_acoes
        else:
            st.warning("⚠️ Não foi possível encontrar ações brasileiras.")
            return []
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar ações brasileiras: {str(e)}")
        return []

def adicionar_acao_manual():
    """
    Permite que o usuário adicione uma ação manualmente
    """
    st.subheader("➕ Adicionar Nova Ação")
    
    col1, col2 = st.columns(2)
    with col1:
        codigo = st.text_input("Código da ação (ex: PETR4):").strip().upper()
    with col2:
        nome = st.text_input("Nome da empresa:").strip()
    
    if st.button("Adicionar"):
        if codigo and nome:
            try:
                # Verificar se a ação existe no Yahoo Finance
                ticker = yf.Ticker(f"{codigo}.SA")
                info = ticker.info
                
                if info:
                    # Adicionar à lista global
                    global ATIVOS_B3
                    nova_acao = {
                        "Codigo": codigo,
                        "Nome": nome
                    }
                    ATIVOS_B3.append(nova_acao)
                    st.success(f"✅ Ação {codigo} adicionada com sucesso!")
                else:
                    st.error("❌ Ação não encontrada no Yahoo Finance.")
            except Exception as e:
                st.error(f"❌ Erro ao adicionar ação: {str(e)}")
        else:
            st.warning("⚠️ Preencha todos os campos.")

def buscar_dados_status_invest(codigo):
    """
    Busca dados do Status Invest para ações brasileiras
    """
    try:
        # Remover .SA se presente
        codigo = codigo.replace('.SA', '')
        
        # URL do Status Invest
        url = f"https://statusinvest.com.br/acoes/{codigo.lower()}"
        
        # Fazer a requisição
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Dicionário para armazenar os dados
            dados = {}
            
            # Buscar LPA
            try:
                lpa_element = soup.find('div', {'title': 'Lucro por Ação'})
                if lpa_element:
                    lpa_text = lpa_element.find_next('strong').text.strip()
                    lpa = float(lpa_text.replace('R$', '').replace('.', '').replace(',', '.').strip())
                    dados['lpa'] = lpa
            except:
                pass
            
            # Buscar VPA
            try:
                vpa_element = soup.find('div', {'title': 'Valor Patrimonial por Ação'})
                if vpa_element:
                    vpa_text = vpa_element.find_next('strong').text.strip()
                    vpa = float(vpa_text.replace('R$', '').replace('.', '').replace(',', '.').strip())
                    dados['vpa'] = vpa
            except:
                pass
            
            # Buscar Dividend Yield
            try:
                dy_element = soup.find('div', {'title': 'Dividend Yield'})
                if dy_element:
                    dy_text = dy_element.find_next('strong').text.strip()
                    dy = float(dy_text.replace('%', '').replace('.', '').replace(',', '.').strip()) / 100
                    dados['dy'] = dy
            except:
                pass
            
            # Buscar histórico de dividendos
            try:
                dividendos = []
                tabela_dividendos = soup.find('table', {'id': 'dy-history'})
                if tabela_dividendos:
                    for row in tabela_dividendos.find_all('tr')[1:]:  # Pular cabeçalho
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            data = cols[0].text.strip()
                            valor = float(cols[1].text.replace('R$', '').replace('.', '').replace(',', '.').strip())
                            dividendos.append({'data': data, 'valor': valor})
                    dados['dividendos'] = dividendos
            except:
                pass
            
            return dados
        else:
            return None
            
    except Exception as e:
        st.warning(f"Erro ao buscar dados no Status Invest: {str(e)}")
        return None

def calcular_preco_justo_graham(info, codigo=None):
    """
    Calcula o Preço Justo de Benjamin Graham (fórmula simplificada VI = √(22,5 x LPA x VPA)).
    Utiliza dados de múltiplas fontes consolidados no dicionário 'info'.
    """
    # Acessar LPA e VPA diretamente do info consolidado
    lpa = info.get('lpa', None)
    vpa = info.get('vpa', None)
    
    if lpa is None or lpa <= 0 or vpa is None or vpa <= 0:
        # Não é possível calcular se faltarem dados válidos
        return None
    
    try:
        # Fórmula simplificada de Graham: VI = sqrt(22.5 * LPA * VPA)
        preco_justo = math.sqrt(22.5 * abs(lpa) * abs(vpa)) # Usar abs para evitar erro com LPA negativo
        return preco_justo
    except:
        return None

def calcular_preco_teto_barsi(info, historico, codigo=None, taxa_desejada=0.06):
    """
    Calcula o Preço Teto de Décio Barsi.
    Utiliza histórico de dividendos anuais consolidado no dicionário 'info'.
    """
    # Acessar dividendos históricos anuais do info consolidado
    dividendos_anuais = info.get('dividendos_anuais', None)

    if dividendos_anuais is None or dividendos_anuais.empty:
        return None

    try:
        hoje = datetime.now()
        cinco_anos_atras = hoje - timedelta(days=5*365)

        # Filtrar dividendos dos últimos 5 anos
        dividendos_5a = dividendos_anuais[dividendos_anuais.index >= cinco_anos_atras]

        if dividendos_5a.empty:
            return None

        # Calcular a média dos dividendos anuais dos últimos 5 anos
        media_dividendos_anuais = dividendos_5a.mean()

        if taxa_desejada > 0 and media_dividendos_anuais > 0:
            # Fórmula de Barsi: Preço Teto = (Média Anual de Dividendos / Taxa Desejada) * 12 (para converter anual para mensal)
            # A fórmula original de Barsi é (Dividendos por Ação / Yield Desejado), onde o yield desejado é em relação ao preço atual.
            # Adaptando para a média anual e yield desejado anual:
            # Preço Teto = Média Anual de Dividendos / Taxa Desejada Anual
            preco_teto = media_dividendos_anuais / taxa_desejada
            return preco_teto
        else:
            return None
            
    except Exception as e:
        # print(f"Erro no cálculo de Barsi: {str(e)}") # Para debug
        return None

def buscar_demonstracoes_status_invest(codigo):
    """
    Busca demonstrações financeiras do Status Invest
    """
    try:
        # Remover .SA se presente
        codigo = codigo.replace('.SA', '')
        
        # URL do Status Invest
        url = f"https://statusinvest.com.br/acoes/{codigo.lower()}"
        
        # Fazer a requisição
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Dicionário para armazenar as demonstrações
            demonstracoes = {
                'dre': None,
                'balanco': None,
                'fluxo_caixa': None
            }
            
            # Buscar DRE
            try:
                dre_div = soup.find('div', {'id': 'dados-dre'})
                if dre_div:
                    tabela = dre_div.find('table')
                    if tabela:
                        # Converter tabela HTML para DataFrame
                        df_dre = pd.read_html(str(tabela))[0]
                        demonstracoes['dre'] = df_dre
            except:
                pass
            
            # Buscar Balanço Patrimonial
            try:
                balanco_div = soup.find('div', {'id': 'dados-balancete'})
                if balanco_div:
                    tabela = balanco_div.find('table')
                    if tabela:
                        # Converter tabela HTML para DataFrame
                        df_balanco = pd.read_html(str(tabela))[0]
                        demonstracoes['balanco'] = df_balanco
            except:
                pass
            
            # Buscar Fluxo de Caixa
            try:
                fluxo_div = soup.find('div', {'id': 'dados-fluxo-caixa'})
                if fluxo_div:
                    tabela = fluxo_div.find('table')
                    if tabela:
                        # Converter tabela HTML para DataFrame
                        df_fluxo = pd.read_html(str(tabela))[0]
                        demonstracoes['fluxo_caixa'] = df_fluxo
            except:
                pass
            
            return demonstracoes
        else:
            return None

    except Exception as e:
        st.warning(f"Erro ao buscar demonstrações no Status Invest: {str(e)}")
        return None

def buscar_demonstracoes_investing(codigo):
    """
    Busca demonstrações financeiras do Investing.com
    """
    try:
        # Remover .SA se presente
        codigo = codigo.replace('.SA', '')
        
        # URL do Investing.com
        url = f"https://br.investing.com/equities/{codigo.lower()}-financial-summary"
        
        # Fazer a requisição
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Dicionário para armazenar as demonstrações
            demonstracoes = {
                'dre': None,
                'balanco': None,
                'fluxo_caixa': None
            }
            
            # Buscar DRE
            try:
                dre_div = soup.find('div', {'id': 'income-statement'})
                if dre_div:
                    tabela = dre_div.find('table')
                    if tabela:
                        df_dre = pd.read_html(str(tabela))[0]
                        demonstracoes['dre'] = df_dre
            except:
                pass
            
            # Buscar Balanço Patrimonial
            try:
                balanco_div = soup.find('div', {'id': 'balance-sheet'})
                if balanco_div:
                    tabela = balanco_div.find('table')
                    if tabela:
                        df_balanco = pd.read_html(str(tabela))[0]
                        demonstracoes['balanco'] = df_balanco
            except:
                pass
            
            # Buscar Fluxo de Caixa
            try:
                fluxo_div = soup.find('div', {'id': 'cash-flow'})
                if fluxo_div:
                    tabela = fluxo_div.find('table')
                    if tabela:
                        df_fluxo = pd.read_html(str(tabela))[0]
                        demonstracoes['fluxo_caixa'] = df_fluxo
            except:
                pass
            
            return demonstracoes
        else:
            return None
            
    except Exception as e:
        st.warning(f"Erro ao buscar demonstrações no Investing.com: {str(e)}")
        return None

def buscar_demonstracoes_infomoney(codigo):
    """
    Busca demonstrações financeiras do InfoMoney
    """
    try:
        # Remover .SA se presente
        codigo = codigo.replace('.SA', '')
        
        # URL do InfoMoney
        url = f"https://www.infomoney.com.br/cotacoes/b3/{codigo.lower()}/"
        
        # Fazer a requisição
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Dicionário para armazenar as demonstrações
            demonstracoes = {
                'dre': None,
                'balanco': None,
                'fluxo_caixa': None
            }
            
            # Buscar DRE
            try:
                dre_div = soup.find('div', {'id': 'demonstrativo-resultados'})
                if dre_div:
                    tabela = dre_div.find('table')
                    if tabela:
                        df_dre = pd.read_html(str(tabela))[0]
                        demonstracoes['dre'] = df_dre
            except:
                pass
            
            # Buscar Balanço Patrimonial
            try:
                balanco_div = soup.find('div', {'id': 'balanco-patrimonial'})
                if balanco_div:
                    tabela = balanco_div.find('table')
                    if tabela:
                        df_balanco = pd.read_html(str(tabela))[0]
                        demonstracoes['balanco'] = df_balanco
            except:
                pass
            
            # Buscar Fluxo de Caixa
            try:
                fluxo_div = soup.find('div', {'id': 'fluxo-caixa'})
                if fluxo_div:
                    tabela = fluxo_div.find('table')
                    if tabela:
                        df_fluxo = pd.read_html(str(tabela))[0]
                        demonstracoes['fluxo_caixa'] = df_fluxo
            except:
                pass
            
            return demonstracoes
        else:
            return None
            
    except Exception as e:
        st.warning(f"Erro ao buscar demonstrações no InfoMoney: {str(e)}")
        return None

# App Streamlit
# Usar colunas para colocar a logo ao lado do título
col_logo, col_title = st.columns([1, 3]) # Ajuste os valores [1, 3] para controlar a largura das colunas

with col_logo:
    # Adicionar a logo usando o URL
    try:
        # Usar o URL fornecido para a imagem
        st.image("https://i.imgur.com/oAuOpaD.png", width=100) # Ajuste a largura conforme necessário
    except Exception as e:
        st.warning(f"⚠️ Não foi possível carregar a logo: {e}")

with col_title:
    st.title("Avaliador de Ações e FIIs")

# Sidebar
with st.sidebar:
    st.header("🔍 Buscar Ativo")
    
    # Campo de busca por nome
    nome_empresa = st.text_input("Nome da empresa ou fundo:", key="nome_empresa")
    df_ativos = carregar_ativos_b3()
    codigo_sugerido = ""
    if not df_ativos.empty and nome_empresa:
        codigo_sugerido = buscar_codigo_por_nome(nome_empresa, df_ativos)
    
    # Campo de código
    if codigo_sugerido:
        st.info(f"💡 Código sugerido: {codigo_sugerido}")
        codigo = st.text_input("Código da ação/FII:", value=codigo_sugerido, key="codigo_acao")
    else:
        codigo = st.text_input("Código da ação/FII:", key="codigo_acao")
    
    st.markdown("---")
    
    # Perfil de investimento
    st.header("⚙️ Configurações")
    perfil = st.selectbox(
        'Qual seu perfil de investimento?',
        [
            'Neutro',
            'Crescimento (busca valorização)',
            'Dividendos (busca renda passiva)',
            'Curto prazo',
            'Médio prazo',
            'Longo prazo',
            'Baixa tolerância a risco',
            'Alta tolerância a risco'
        ]
    )
    
# Análise automática quando o código for digitado
if codigo:
    try:
        with st.spinner('Carregando dados...'):
            info, historico = obter_dados(codigo)
            st.session_state['dados_cache'] = st.session_state.get('dados_cache', {})
            st.session_state['dados_cache'][codigo] = {'info': info, 'historico': historico}
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados: {str(e)}")
        st.info("💡 Dica: Verifique se o código da ação/FII está correto e tente novamente.")

    # Criar abas para organizar as informações
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dados Fundamentais",
        "📈 Gráfico e Análise Temporal",
        "🌐 Análise Setorial",
        "📌 Recomendações",
        "📜 Demonstrações Financeiras Históricas"
    ])

    with tab1:
        mostrar_dados_fundamentais(info)

    with tab2:
        st.subheader("📈 Tendência de Preço")

        # Botão para atualizar o gráfico
        if st.button("Atualizar Gráfico"):
            with st.spinner(f'Atualizando dados para {codigo}...'):
                info, historico = obter_dados(codigo) # Rebusca os dados mais recentes
                st.session_state['dados_cache'][codigo] = {'info': info, 'historico': historico} # Atualiza o cache
                # Streamlit irá re-executar o script após clicar no botão

        # Verificar se há dados históricos antes de tentar plotar
        if historico is not None and not historico.empty:
            mostrar_grafico(historico)
            analise_temporal(historico)
            # A função mostrar_indicadores_historicos precisa do objeto Ticker, não apenas do histórico
            try:
                acao_obj = yf.Ticker(formatar_codigo_acao(codigo))
                mostrar_indicadores_historicos(acao_obj)
            except Exception as e:
                st.warning(f"⚠️ Não foi possível carregar indicadores históricos: {e}")
        else:
            st.info("ℹ️ Dados históricos não disponíveis para exibir o gráfico.")

    with tab3:
        analise_setorial_noticias(info, codigo)

    with tab4:
        analise_sugestiva(info, perfil)

    with tab5:
        st.subheader("📜 Demonstrações Financeiras Históricas")

        try:
            # Obter demonstrações do Yahoo Finance (aqui talvez precise ajustar para usar o objeto 'acao_obj' se ele foi criado)
            # Ou manter a criação local se for mais simples e rápido
            acao_obj_demo = yf.Ticker(formatar_codigo_acao(codigo))
            financials = acao_obj_demo.financials
            balance_sheet = acao_obj_demo.balance_sheet
            cashflow = acao_obj_demo.cashflow

            # Buscar demonstrações de todas as fontes
            demonstracoes_status = buscar_demonstracoes_status_invest(codigo)
            demonstracoes_investing = buscar_demonstracoes_investing(codigo)
            demonstracoes_infomoney = buscar_demonstracoes_infomoney(codigo)

            # Exibir Demonstrativos em abas
            st.markdown("### Demonstrativo de Resultados (DRE)")
            tabs_dre = st.tabs(["Yahoo Finance", "Status Invest", "Investing.com", "InfoMoney"])

            with tabs_dre[0]:
                if not financials.empty:
                    st.dataframe(financials.T.style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Yahoo Finance")

            with tabs_dre[1]:
                if demonstracoes_status and demonstracoes_status['dre'] is not None:
                    st.dataframe(demonstracoes_status['dre'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Status Invest")

            with tabs_dre[2]:
                if demonstracoes_investing and demonstracoes_investing['dre'] is not None:
                    st.dataframe(demonstracoes_investing['dre'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Investing.com")

            with tabs_dre[3]:
                if demonstracoes_infomoney and demonstracoes_infomoney['dre'] is not None:
                    st.dataframe(demonstracoes_infomoney['dre'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no InfoMoney")

            st.markdown("--- ")

            st.markdown("### Balanço Patrimonial")
            tabs_balanco = st.tabs(["Yahoo Finance", "Status Invest", "Investing.com", "InfoMoney"])

            with tabs_balanco[0]:
                if not balance_sheet.empty:
                    st.dataframe(balance_sheet.T.style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Yahoo Finance")

            with tabs_balanco[1]:
                if demonstracoes_status and demonstracoes_status['balanco'] is not None:
                    st.dataframe(demonstracoes_status['balanco'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Status Invest")

            with tabs_balanco[2]:
                if demonstracoes_investing and demonstracoes_investing['balanco'] is not None:
                    st.dataframe(demonstracoes_investing['balanco'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Investing.com")

            with tabs_balanco[3]:
                if demonstracoes_infomoney and demonstracoes_infomoney['balanco'] is not None:
                    st.dataframe(demonstracoes_infomoney['balanco'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no InfoMoney")

            st.markdown("--- ")

            st.markdown("### Demonstrativo de Fluxo de Caixa")
            tabs_fluxo = st.tabs(["Yahoo Finance", "Status Invest", "Investing.com", "InfoMoney"])

            with tabs_fluxo[0]:
                if not cashflow.empty:
                    st.dataframe(cashflow.T.style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Yahoo Finance")

            with tabs_fluxo[1]:
                if demonstracoes_status and demonstracoes_status['fluxo_caixa'] is not None:
                    st.dataframe(demonstracoes_status['fluxo_caixa'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Status Invest")

            with tabs_fluxo[2]:
                if demonstracoes_investing and demonstracoes_investing['fluxo_caixa'] is not None:
                    st.dataframe(demonstracoes_investing['fluxo_caixa'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no Investing.com")

            with tabs_fluxo[3]:
                if demonstracoes_infomoney and demonstracoes_infomoney['fluxo_caixa'] is not None:
                    st.dataframe(demonstracoes_infomoney['fluxo_caixa'].style.format(precision=2))
                else:
                    st.info("Dados não disponíveis no InfoMoney")

        except Exception as e:
            st.warning(f"Não foi possível obter ou exibir as demonstrações financeiras: {str(e)}")
            st.info("""
            **Dicas:**
            - Verifique se o código do ativo está correto
            - Alguns FIIs podem não ter demonstrações disponíveis
            - Tente novamente em alguns minutos
            - Verifique se o ativo está listado corretamente
            - Dados foram buscados em múltiplas fontes:
              * Yahoo Finance
              * Status Invest
              * Investing.com
              * InfoMoney
            """)