# Requisitos: Instale com 'pip install yfinance streamlit pandas matplotlib requests beautifulsoup4'

import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date # Importar date
import unicodedata
import os
import requests
from bs4 import BeautifulSoup
import io
import math

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

# Configuração da página
st.set_page_config(
    page_title="Avaliador de Ações e FIIs",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    codigo = codigo.strip().upper()
    if not codigo.endswith('.SA'):
        codigo = f"{codigo}.SA"
    return codigo

def obter_dados(codigo):
    codigo_formatado = formatar_codigo_acao(codigo)
    acao = yf.Ticker(codigo_formatado)
    info = acao.info
    historico = acao.history(period="1y")

    return info, historico

def mostrar_dados_fundamentais(info):
    st.subheader("📊 Dados Fundamentais")
    
    # Criar colunas para os dados fundamentais
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Informações Básicas")
        with st.container(): # Usando container para agrupar
            st.write(f"**Empresa/FII:** {info.get('longName', 'N/A')}")
            st.write(f"**Setor:** {info.get('sector', 'N/A')}")
            st.write(f"**Preço atual:** R$ {info.get('previousClose', 'N/A'):.2f}")
        
        st.markdown("### Indicadores de Valuation")
        with st.container(): # Usando container para agrupar
            st.write(f"**P/L:** {info.get('trailingPE', 'N/A')} *<small>(Preço/Lucro)</small>*", unsafe_allow_html=True)
            st.write(f"**P/VPA:** {info.get('priceToBook', 'N/A')} *<small>(Preço/Valor Patrimonial)</small>*", unsafe_allow_html=True)
            st.write(f"**EV/EBITDA:** {info.get('enterpriseToEbitda', 'N/A')} *<small>(Valor da Empresa/EBITDA)</small>*", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Indicadores de Rentabilidade")
        with st.container(): # Usando container para agrupar
            st.write(f"**Dividend Yield:** {round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') is not None else 'N/A'}%", unsafe_allow_html=True)
            st.write(f"**ROE:** {round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') is not None else 'N/A'}%", unsafe_allow_html=True)
            st.write(f"**Margem Bruta:** {round(info.get('grossMargins', 0) * 100, 2) if info.get('grossMargins') is not None else 'N/A'}%", unsafe_allow_html=True)
            st.write(f"**Margem Líquida:** {round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') is not None else 'N/A'}%", unsafe_allow_html=True)
        
        st.markdown("### Mais Indicadores de Rentabilidade")
        with st.container():
            st.write(f"**Margem EBITDA:** {round(info.get('ebitdaMargins', 0) * 100, 2) if info.get('ebitdaMargins') is not None else 'N/A'}%", unsafe_allow_html=True)
            st.write(f"**Margem Operacional:** {round(info.get('operatingMargins', 0) * 100, 2) if info.get('operatingMargins') is not None else 'N/A'}%", unsafe_allow_html=True)

        st.markdown("### Indicadores de Endividamento")
        with st.container(): # Usando container para agrupar
            st.write(f"**Dívida Líquida/EBITDA:** {info.get('debtToEbitda', 'N/A')}")
            st.write(f"**Dívida/Patrimônio Líquido:** {info.get('debtToEquity', 'N/A')}") # Adicionando Dívida/PL
            st.write(f"**Liquidez Corrente:** {info.get('currentRatio', 'N/A')}")
            st.write(f"**Caixa Total:** R$ {info.get('totalCash', 'N/A'):,.2f}")
            st.write(f"**Dívida Total:** R$ {info.get('totalDebt', 'N/A'):,.2f}")

        st.markdown("### Indicadores de Fluxo de Caixa")
        with st.container():
            st.write(f"**Fluxo de Caixa Operacional:** R$ {info.get('operatingCashflow', 'N/A'):,.2f}")
            st.write(f"**Fluxo de Caixa Livre:** R$ {info.get('freeCashflow', 'N/A'):,.2f}")

def mostrar_grafico(historico):
    st.subheader("📈 Tendência de Preço")
    fig, ax = plt.subplots(figsize=(12, 6))
    historico['Close'].plot(ax=ax, color='#2196F3', linewidth=2)
    ax.set_ylabel("Preço de Fechamento (R$)")
    ax.set_xlabel("Data")
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    st.pyplot(fig)

def mostrar_indicadores_historicos(acao):
    st.subheader("📊 Evolução dos Indicadores")
    
    try:
        # Obter dados históricos dos indicadores
        # Usar um período maior para ter mais dados históricos
        historico_indicadores = acao.history(period="5y")
        
        # Criar colunas para os gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de P/L Histórico
            if 'trailingPE' in acao.info:
                st.markdown("### P/L Histórico")
                fig, ax = plt.subplots(figsize=(10, 4))
                # Calcular P/L histórico usando preço e lucro por ação
                if 'earningsPerShare' in acao.info and acao.info['earningsPerShare'] > 0:
                    pl_historico = historico_indicadores['Close'] / acao.info['earningsPerShare']
                    pl_historico.plot(ax=ax, color='#4CAF50', linewidth=2)
                    ax.set_ylabel("P/L")
                    ax.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig)
            
            # Gráfico de Dividend Yield Histórico
            if not historico_indicadores['Dividends'].empty:
                st.markdown("### Dividend Yield Histórico")
                fig, ax = plt.subplots(figsize=(10, 4))
                # Calcular DY histórico
                dy_historico = (historico_indicadores['Dividends'] / historico_indicadores['Close']) * 100
                dy_historico.plot(ax=ax, color='#FF9800', linewidth=2)
                ax.set_ylabel("Dividend Yield (%)")
                ax.grid(True, linestyle='--', alpha=0.7)
                st.pyplot(fig)
        
        with col2:
            # Gráfico de ROE Histórico
            if 'returnOnEquity' in acao.info:
                st.markdown("### ROE Histórico")
                fig, ax = plt.subplots(figsize=(10, 4))
                # Usar ROE atual como referência
                roe_atual = acao.info['returnOnEquity'] * 100
                ax.axhline(y=roe_atual, color='#9C27B0', linestyle='-', label=f'ROE Atual: {roe_atual:.2f}%')
                ax.set_ylabel("ROE (%)")
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend()
                st.pyplot(fig)
            
            # Gráfico de Margem EBITDA Histórica
            if 'ebitdaMargins' in acao.info:
                st.markdown("### Margem EBITDA Histórica")
                fig, ax = plt.subplots(figsize=(10, 4))
                # Usar margem EBITDA atual como referência
                margem_atual = acao.info['ebitdaMargins'] * 100
                ax.axhline(y=margem_atual, color='#E91E63', linestyle='-', label=f'Margem Atual: {margem_atual:.2f}%')
                ax.set_ylabel("Margem EBITDA (%)")
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend()
                st.pyplot(fig)
        
        # Adicionar mais indicadores em uma nova linha
        col3, col4 = st.columns(2)
        
        with col3:
            # Gráfico de Dívida/PL Histórico
            if 'debtToEquity' in acao.info:
                st.markdown("### Dívida/PL Histórico")
                fig, ax = plt.subplots(figsize=(10, 4))
                # Usar Dívida/PL atual como referência
                debt_equity_atual = acao.info['debtToEquity']
                ax.axhline(y=debt_equity_atual, color='#F44336', linestyle='-', label=f'Dívida/PL Atual: {debt_equity_atual:.2f}')
                ax.set_ylabel("Dívida/PL")
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend()
                st.pyplot(fig)
        
        with col4:
            # Gráfico de P/VPA Histórico
            if 'priceToBook' in acao.info:
                st.markdown("### P/VPA Histórico")
                fig, ax = plt.subplots(figsize=(10, 4))
                # Calcular P/VPA histórico usando preço e VPA
                if 'bookValue' in acao.info and acao.info['bookValue'] > 0:
                    pvpa_historico = historico_indicadores['Close'] / acao.info['bookValue']
                    pvpa_historico.plot(ax=ax, color='#3F51B5', linewidth=2)
                    ax.set_ylabel("P/VPA")
                    ax.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig)
        
        # Adicionar nota explicativa
        st.info("""
        **Nota:** Alguns indicadores mostram apenas o valor atual como referência (linha horizontal) 
        devido à limitação de dados históricos disponíveis no Yahoo Finance. 
        Os gráficos de P/L, Dividend Yield e P/VPA mostram a evolução histórica quando os dados estão disponíveis.
        """)
        
    except Exception as e:
        st.warning(f"Não foi possível gerar os gráficos de indicadores históricos: {str(e)}")
        st.info("Alguns indicadores podem não estar disponíveis para este ativo ou período.")

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
            ticker_obj = yf.Ticker(codigo_acao)
            noticias = ticker_obj.news
            
            if noticias:
                for n in noticias[:5]: # Exibir as 5 notícias mais recentes
                    with st.container(): # Cada notícia em um container
                        st.markdown(f"**[{n['title']}]({n['link']})**") # Título clicável
                        
                        # Formatar a data
                        try:
                            data = datetime.fromtimestamp(n['providerPublishTime'])
                            data_formatada = data.strftime('%d/%m/%Y %H:%M')
                        except:
                            data_formatada = "Data não disponível"
                        
                        # Exibir fonte e data
                        st.markdown(f"*Fonte: {n.get('publisher', 'Fonte não disponível')} - {data_formatada}* <br>", unsafe_allow_html=True)
                        
            else:
                st.info("Nenhuma notícia recente encontrada para este ativo.")
                
    except Exception as e:
        st.warning(f"Não foi possível buscar notícias: {str(e)}")
        st.info("Dica: Alguns ativos podem não ter notícias disponíveis ou podem estar com acesso temporariamente indisponível.")

# ====== MELHORIA: Recomendações personalizadas ======
def analise_sugestiva(info, perfil):
    st.subheader("📌 Recomendações por Horizonte de Investimento e Perfil")
    pl = info.get('trailingPE')
    dy = info.get('dividendYield')
    roe = info.get('returnOnEquity')
    debt_equity = info.get('debtToEquity')
    price_to_book = info.get('priceToBook')
    ev_ebitda = info.get('enterpriseToEbitda')
    debt_ebitda = info.get('debtToEbitda')
    current_ratio = info.get('currentRatio')
    payout_ratio = info.get('payoutRatio')

    # Novas métricas
    ebitda_margins = info.get('ebitdaMargins')
    operating_margins = info.get('operatingMargins')
    operating_cashflow = info.get('operatingCashflow')
    free_cashflow = info.get('freeCashflow')

    sugestoes = []
    score = 0
    # Ajustar max_score para acomodar novas métricas
    max_score = 15 # Aumentado para refletir mais critérios

    # Pontuação e sugestões baseadas no perfil

    # Crescimento (busca valorização) / Longo prazo
    if 'crescimento' in perfil.lower() or 'longo' in perfil.lower():
        if roe is not None:
            if roe > 0.15: # Bom ROE para crescimento
                sugestoes.append("📈 ROE forte (Mais de 15%). Potencial de crescimento a longo prazo.")
                score += 2
            elif roe > 0.08:
                 sugestoes.append("ℹ️ ROE moderado. Rentabilidade razoável sobre o patrimônio.")
                 score += 1
        if pl is not None:
            if pl < 15: # P/L razoável para crescimento
                sugestoes.append("✅ P/L razoável (Abaixo de 15). Indicativo de valorização.")
                score += 2
            elif pl < 25:
                sugestoes.append("ℹ️ P/L moderado (Entre 15 e 25). Atenção ao valuation.")
                score += 1
            else:
                sugestoes.append("⚠️ P/L elevado (Acima de 25). Ação pode estar cara para o perfil crescimento.")
                score -= 1
        
        # Adicionar critérios de crescimento baseados em margens e fluxo de caixa
        if ebitda_margins is not None and ebitda_margins > 0.20: # Boa margem EBITDA
            sugestoes.append("📈 Alta Margem EBITDA (Mais de 20%). Sinal de eficiência operacional.")
            score += 1
        if operating_margins is not None and operating_margins > 0.15: # Boa margem Operacional
            sugestoes.append("📈 Alta Margem Operacional (Mais de 15%). Indicia boa gestão de custos.")
            score += 1
        if free_cashflow is not None and free_cashflow > 0: # Gerando Fluxo de Caixa Livre
            sugestoes.append("💰 Gerando Fluxo de Caixa Livre positivo. Essencial para reinvestimento e crescimento.")
            score += 1

    # Dividendos (busca renda passiva)
    if 'dividendos' in perfil.lower():
        if dy is not None:
            if dy > 0.06: # Bom Dividend Yield
                sugestoes.append("💰 Excelente Dividend Yield (Mais de 6%). Ótimo para renda passiva.")
                score += 3
            elif dy > 0.04:
                sugestoes.append("✅ Bom Dividend Yield (Entre 4% e 6%). Boa opção para dividendos.")
                score += 2
            elif dy > 0.02:
                 sugestoes.append("ℹ️ Dividend Yield moderado (Entre 2% e 4%).")
                 score += 1
            else:
                sugestoes.append("⚠️ Dividend Yield baixo (Abaixo de 2%). Não ideal para foco em dividendos.")
                score -= 1
        else:
             sugestoes.append("ℹ️ Dividend Yield não disponível ou muito baixo.")
             score -= 1
        if payout_ratio is not None and payout_ratio > 0.5 and payout_ratio < 1.1: # Payout saudável (distribui lucro)
             sugestoes.append("✅ Payout Ratio saudável. Empresa distribui parte do lucro como dividendos.")
             score += 1
        elif payout_ratio is not None and payout_ratio >= 1.1:
             sugestoes.append("⚠️ Payout Ratio acima de 100%. Empresa pode estar distribuindo mais do que lucra.")
             score -= 1
        # Adicionar critério de fluxo de caixa para dividendos (gerar caixa para pagar proventos)
        if operating_cashflow is not None and operating_cashflow > 0: # Gerando Fluxo de Caixa Operacional positivo
             sugestoes.append("💰 Gerando Fluxo de Caixa Operacional positivo. Essencial para sustentar dividendos.")
             score += 1

    # Risco e Saúde Financeira (Baixa tolerância / Neutro)
    if 'baixa' in perfil.lower() or 'neutro' in perfil.lower():
        if debt_equity is not None:
            if debt_equity < 0.8: # Baixa alavancagem
                sugestoes.append("💪 Baixa alavancagem financeira (Dívida/Patrimônio abaixo de 0.8). Baixo risco financeiro.")
                score += 2
            elif debt_equity < 1.5:
                sugestoes.append("✅ Alavancagem financeira moderada (Dívida/Patrimônio entre 0.8 e 1.5).")
                score += 1
            else:
                sugestoes.append(f"⚠️ Alavancagem financeira elevada (Dívida/Patrimônio: {debt_equity:.2f}). Maior risco financeiro para perfil conservador.")
                score -= 2
        if debt_ebitda is not None:
            if debt_ebitda < 2: # Baixa dívida em relação ao Ebitda
                 sugestoes.append("💪 Dívida Líquida/EBITDA baixa (Abaixo de 2). Empresa gera caixa para pagar dívida.")
                 score += 2
            elif debt_ebitda < 3.5:
                 sugestoes.append("✅ Dívida Líquida/EBITDA moderada (Entre 2 e 3.5).")
                 score += 1
            else:
                 sugestoes.append(f"⚠️ Dívida Líquida/EBITDA elevada ({debt_ebitda:.2f}). Atenção ao endividamento.")
                 score -= 2
        if current_ratio is not None:
            if current_ratio > 1.8: # Boa liquidez
                 sugestoes.append("💪 Ótima liquidez corrente (Acima de 1.8). Forte capacidade de pagar dívidas de curto prazo.")
                 score += 2
            elif current_ratio > 1.2:
                 sugestoes.append("✅ Boa liquidez corrente (Entre 1.2 e 1.8). Capacidade saudável de pagamento no curto prazo.")
                 score += 1
            else:
                 sugestoes.append(f"⚠️ Liquidez corrente baixa ({current_ratio:.2f}). Atenção à capacidade de pagamento no curto prazo.")
                 score -= 2

        # Adicionar critérios de saúde financeira baseados em margens e fluxo de caixa
        if ebitda_margins is not None and ebitda_margins > 0.10: # Margem EBITDA razoável para saúde
             sugestoes.append("✅ Margem EBITDA razoável. Boa capacidade de gerar caixa operacional antes de depreciação/amortização.")
             score += 1
        if operating_margins is not None and operating_margins > 0.08: # Margem Operacional razoável para saúde
             sugestoes.append("✅ Margem Operacional razoável. Indicia controle sobre custos operacionais.")
             score += 1
        if operating_cashflow is not None and operating_cashflow > 0: # Gerando Fluxo de Caixa Operacional positivo
             sugestoes.append("💪 Gerando Fluxo de Caixa Operacional positivo. Fundamental para a sustentabilidade.")
             score += 1

    # Risco (Alta tolerância)
    if 'alta' in perfil.lower():
         if debt_equity is not None and debt_equity > 2.5: # Alta alavancagem pode ser tolerada, mas com alerta
              sugestoes.append(f"ℹ️ Alavancagem alta ({debt_equity:.2f}). Perfil de maior risco pode considerar, mas com cautela.")

    # Recomendações gerais de Valuation (para todos, exceto se conflitar muito com perfil específico)
    if 'neutro' in perfil.lower() or ('crescimento' not in perfil.lower() and 'dividendos' not in perfil.lower()):
        if pl is not None and pl > 25:
            sugestoes.append(f"⚠️ P/L elevado ({pl:.2f}), atenção ao valuation.")
        if price_to_book is not None and price_to_book > 2.5:
            sugestoes.append(f"⚠️ P/VPA elevado ({price_to_book:.2f}), atenção ao valuation.")
        if ev_ebitda is not None and ev_ebitda > 15:
            sugestoes.append(f"⚠️ EV/EBITDA elevado ({ev_ebitda:.2f}). Pode indicar empresa cara.")

    # Ajustar score para a escala 0-10 (simplificado)
    # Definir limites mínimos e máximos razoáveis para o score bruto
    # Recalcular min_raw_score e max_raw_score com base nas novas métricas
    min_raw_score_novo = -12 # Estimativa ajustada
    max_raw_score_novo = 17 # Estimativa ajustada
    # Mapear o score bruto para a escala 0-10
    score_final = max(0, min(10, round((score - min_raw_score_novo) / (max_raw_score_novo - min_raw_score_novo) * 10)))

    st.markdown("--- ")
    st.subheader("Sumário e Score Fundamental (Simplificado)")
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

def calcular_preco_justo_graham(lpa, vpa):
    """
    Calcula o Preço Justo de Benjamin Graham (fórmula simplificada VI = √(22,5 x LPA x VPA)).
    Retorna None se os dados necessários não estiverem disponíveis ou forem inválidos.
    """
    if lpa is None or vpa is None or lpa <= 0 or vpa <= 0:
        return None
    try:
        # Fórmula simplificada de Graham: VI = sqrt(22.5 * LPA * VPA)
        # Alguns usam um multiplicador de 15x PL e 1.5x P/VPA, cujo produto é 22.5
        preco_justo = math.sqrt(22.5 * lpa * vpa)
        return preco_justo
    except:
        return None

def calcular_preco_teto_barsi(historico, info, taxa_desejada=0.06):
    """
    Calcula o Preço Teto de Décio Barsi.
    Usa a média do Dividend Yield dos últimos 5 anos e a taxa de retorno desejada.
    Retorna None se os dados necessários não estiverem disponíveis ou forem inválidos.
    """
    if historico.empty or info is None:
        return None

    try:
        # Obter histórico de dividendos e preços dos últimos 5 anos
        hoje = datetime.now()
        cinco_anos_atras = hoje - timedelta(days=5*365) # Aproximadamente 5 anos

        # Filtrar histórico de preços para os últimos 5 anos
        historico_5a = historico[historico.index >= cinco_anos_atras]

        if historico_5a.empty:
            return None

        # Calcular o DY anual para cada um dos últimos 5 anos
        yields_anuais = []
        for ano in range(hoje.year - 4, hoje.year + 1): # Últimos 5 anos (inclusive o atual incompleto)
            inicio_ano = datetime(ano, 1, 1)
            fim_ano = datetime(ano, 12, 31) if ano < hoje.year else hoje

            historico_ano = historico[(historico.index >= inicio_ano) & (historico.index <= fim_ano)]
            if historico_ano.empty:
                continue

            # Obter dividendos pagos no ano
            # Nota: yfinance .dividends retorna a série de dividendos, precisamos filtrar pelo período
            # Isso pode ser um pouco complexo de alinhar perfeitamente com o histórico de preços do período.
            # Uma abordagem mais robusta seria pegar os dividendos de todo o período e agrupá-los por ano,
            # e usar o preço médio ou o preço final do ano para calcular o yield anual.

            # Simplificando: vamos somar os dividendos pagos no ano e dividir pelo preço médio do ano
            try:
                acao_temp = yf.Ticker(info.get('symbol'))
                dividendos_periodo = acao_temp.dividends[(acao_temp.dividends.index >= inicio_ano) & (acao_temp.dividends.index <= fim_ano)]
                total_dividendos_ano = dividendos_periodo.sum()
            except:
                total_dividendos_ano = 0 # Nenhum dividendo no ano ou erro

            preco_medio_ano = historico_ano['Close'].mean()

            if preco_medio_ano > 0:
                yield_anual = total_dividendos_ano / preco_medio_ano
                yields_anuais.append(yield_anual)

        if not yields_anuais:
            return None

        media_yields = sum(yields_anuais) / len(yields_anuais)

        if taxa_desejada > 0 and media_yields > 0:
            preco_teto = (media_yields * info.get('previousClose', 0)) / taxa_desejada # Multiplicar pelo preço atual para ter o valor em R$
            return preco_teto
        else:
            return None
    except Exception as e:
        # st.error(f"Erro no cálculo do Preço Teto: {e}") # Remover em produção
        return None

def analise_especifica_fii(codigo):
    """
    Realiza análise específica para FIIs, buscando métricas importantes
    """
    st.subheader("🏢 Análise Específica de FII")
    
    try:
        # Tentar obter dados do FII
        fii = yf.Ticker(codigo)
        info = fii.info
        
        # Verificar se é realmente um FII
        if not info.get('quoteType') == 'ETF' or not codigo.endswith('11'):
            st.warning("⚠️ Este ativo não parece ser um FII. Algumas métricas podem não ser aplicáveis.")
            return
        
        # Criar colunas para organizar as informações
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Métricas de Distribuição")
            # Dividend Yield (já disponível no Yahoo Finance)
            dy = info.get('dividendYield', 0) * 100 if info.get('dividendYield') is not None else None
            if dy is not None:
                st.write(f"**Dividend Yield:** {dy:.2f}%")
            
            # Payout (já disponível no Yahoo Finance)
            payout = info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') is not None else None
            if payout is not None:
                st.write(f"**Payout:** {payout:.2f}%")
            
            # Valor Patrimonial por Cota (VPC)
            vpc = info.get('bookValue')
            if vpc is not None:
                st.write(f"**Valor Patrimonial por Cota (VPC):** R$ {vpc:.2f}")
            
            # P/VPC (Preço/Valor Patrimonial por Cota)
            p_vpc = info.get('priceToBook')
            if p_vpc is not None:
                st.write(f"**P/VPC:** {p_vpc:.2f}")
        
        with col2:
            st.markdown("### 📈 Métricas de Gestão")
            # Patrimônio Líquido
            pl = info.get('totalAssets')
            if pl is not None:
                st.write(f"**Patrimônio Líquido:** R$ {pl:,.2f}")
            
            # Número de Cotistas (se disponível)
            cotistas = info.get('sharesOutstanding')
            if cotistas is not None:
                st.write(f"**Número de Cotas:** {cotistas:,.0f}")
            
            # Taxa de Administração (se disponível)
            taxa_admin = info.get('annualReportExpenseRatio', 0) * 100 if info.get('annualReportExpenseRatio') is not None else None
            if taxa_admin is not None:
                st.write(f"**Taxa de Administração:** {taxa_admin:.2f}%")
        
        # Adicionar alertas e recomendações específicas para FIIs
        st.markdown("### ⚠️ Alertas e Recomendações")
        
        # Verificar Dividend Yield
        if dy is not None:
            if dy < 6:
                st.warning("⚠️ Dividend Yield abaixo de 6%. Verifique se o FII está distribuindo adequadamente.")
            elif dy > 12:
                st.warning("⚠️ Dividend Yield muito alto (>12%). Verifique a sustentabilidade da distribuição.")
        
        # Verificar P/VPC
        if p_vpc is not None:
            if p_vpc > 1.2:
                st.warning("⚠️ P/VPC acima de 1.2. O FII pode estar negociando com ágio significativo.")
            elif p_vpc < 0.8:
                st.info("ℹ️ P/VPC abaixo de 0.8. O FII pode estar negociando com deságio.")
        
        # Verificar Taxa de Administração
        if taxa_admin is not None:
            if taxa_admin > 1.5:
                st.warning("⚠️ Taxa de administração elevada (>1.5%). Pode impactar significativamente os retornos.")
        
        # Adicionar nota sobre limitações
        st.info("""
        **Nota:** Algumas métricas importantes para FIIs como Vacância Física/Financeira, 
        Prazo Médio dos Contratos e Número de Cotistas podem não estar disponíveis no Yahoo Finance. 
        Recomenda-se consultar o site do FII ou a CVM para informações mais detalhadas.
        """)
        
    except Exception as e:
        st.error(f"❌ Erro ao analisar FII: {str(e)}")
        st.info("💡 Algumas métricas podem não estar disponíveis para este FII.")

# App Streamlit
st.title("📈 Avaliador de Ações e FIIs")

# Sidebar
with st.sidebar:
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
    
    st.markdown("---")
    st.markdown("### 📚 Guia Rápido")
    with st.expander("Como analisar uma ação ou FII?"):
        st.markdown("""
        **1. Análise Fundamentalista**  
        - Lucro e crescimento
        - Valuation
        - Endividamento
        - Governança
        
        **2. Análise Técnica**  
        - Tendências
        - Volume
        - Indicadores
        
        **3. Análise Setorial**
        - Setor
        - Economia
        - Riscos
        """)

    # Adicionar seção para adicionar ações manualmente na sidebar
    st.markdown("---")
    with st.expander("➕ Adicionar Ação Manualmente"):
        adicionar_acao_manual()

# Área principal
col1, col2 = st.columns([2, 1])
with col1:
    nome_empresa = st.text_input("🔍 Nome da empresa ou fundo:")
    df_ativos = carregar_ativos_b3()
    codigo_sugerido = ""
    if not df_ativos.empty and nome_empresa:
        codigo_sugerido = buscar_codigo_por_nome(nome_empresa, df_ativos)

with col2:
    if codigo_sugerido:
        st.info(f"💡 Código sugerido: {codigo_sugerido}")
        codigo = st.text_input("📝 Código da ação/FII:", value=codigo_sugerido)
    else:
        codigo = st.text_input("📝 Código da ação/FII:")

if st.button("🔍 Analisar"):
    try:
        with st.spinner('Carregando dados...'):
            info, historico = obter_dados(codigo)
            
            # Criar abas para organizar as informações
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "📊 Dados Fundamentais",
                "📈 Gráfico e Análise Temporal",
                "🌐 Análise Setorial",
                "📌 Recomendações",
                "💰 Valuation Avançado",
                "📜 Demonstrações Financeiras Históricas",
                "🏢 Análise FII"
            ])
            
            with tab1:
                mostrar_dados_fundamentais(info)
            
            with tab2:
                mostrar_grafico(historico)
                analise_temporal(historico)
                mostrar_indicadores_historicos(yf.Ticker(codigo))
            
            with tab3:
                analise_setorial_noticias(info, codigo)
            
            with tab4:
                analise_sugestiva(info, perfil)

            with tab5:
                st.subheader("💰 Valuation Avançado")

                # Cálculo e exibição do Preço Justo de Graham
                lpa = info.get('earningsPerShare', None)
                vpa = info.get('bookValue', None)
                preco_justo = calcular_preco_justo_graham(lpa, vpa)

                st.markdown("### Preço Justo de Benjamin Graham (Simplificado)")
                if preco_justo is not None:
                    st.write(f"**Preço Justo:** R$ {preco_justo:.2f}")
                    preco_atual = info.get('previousClose')
                    if preco_atual is not None:
                        if preco_atual < preco_justo:
                            st.success(f"✅ Preço atual (R$ {preco_atual:.2f}) está ABAIXO do Preço Justo de Graham.")
                        elif preco_atual > preco_justo:
                            st.warning(f"⚠️ Preço atual (R$ {preco_atual:.2f}) está ACIMA do Preço Justo de Graham.")
                        else:
                             st.info(f"ℹ️ Preço atual (R$ {preco_atual:.2f}) é igual ao Preço Justo de Graham.")
                else:
                    # Mensagem mais específica
                    mensagem_erro_graham = "Não foi possível calcular o Preço Justo de Graham. "
                    if lpa is None or lpa <= 0:
                        mensagem_erro_graham += "LPA (Lucro por Ação) não disponível ou inválido. "
                    if vpa is None or vpa <= 0:
                        mensagem_erro_graham += "VPA (Valor Patrimonial por Ação) não disponível ou inválido."
                    if lpa is not None and vpa is not None and lpa > 0 and vpa > 0:
                         mensagem_erro_graham = "Erro no cálculo do Preço Justo de Graham." # Erro inesperado
                    st.info(mensagem_erro_graham.strip())

                st.markdown("--- ")

                # Cálculo e exibição do Preço Teto de Barsi
                preco_teto = calcular_preco_teto_barsi(historico, info)

                st.markdown("### Preço Teto de Décio Barsi (Taxa Desejada: 6%)")
                if preco_teto is not None:
                    st.write(f"**Preço Teto:** R$ {preco_teto:.2f}")
                    preco_atual = info.get('previousClose')
                    if preco_atual is not None:
                        if preco_atual < preco_teto:
                            st.success(f"✅ Preço atual (R$ {preco_atual:.2f}) está ABAIXO do Preço Teto de Barsi.")
                        elif preco_atual > preco_teto:
                            st.warning(f"⚠️ Preço atual (R$ {preco_atual:.2f}) está ACIMA do Preço Teto de Barsi.")
                        else:
                            st.info(f"ℹ️ Preço atual (R$ {preco_atual:.2f}) é igual ao Preço Teto de Barsi.")
                else:
                    # Mensagem mais específica
                    mensagem_erro_barsi = "Não foi possível calcular o Preço Teto de Barsi. "
                    if historico.empty:
                         mensagem_erro_barsi += "Histórico de preços não disponível. "
                    if info is None:
                         mensagem_erro_barsi += "Informações do ativo não disponíveis. "
                    # A função calcular_preco_teto_barsi já trata a falta de dividendos ou média zero internamente,
                    # mas podemos adicionar uma nota sobre a dependência do histórico de dividendos.
                    mensagem_erro_barsi += "Verifique se o histórico de dividendos dos últimos 5 anos está disponível no Yahoo Finance para este ativo."
                    st.info(mensagem_erro_barsi.strip())
                
            with tab6: # Conteúdo da nova aba
                st.subheader("📜 Demonstrações Financeiras Históricas")

                try:
                    # Obter demonstrações financeiras
                    acao = yf.Ticker(codigo)
                    financials = acao.financials
                    balance_sheet = acao.balance_sheet
                    cashflow = acao.cashflow

                    # Exibir Income Statement
                    st.markdown("### Demonstrativo de Resultados (Income Statement)")
                    if not financials.empty:
                        # Transpor o DataFrame para que as datas fiquem nas colunas
                        st.dataframe(financials.T.style.format(precision=2))
                    else:
                        st.info("Demonstrativo de Resultados não disponível.")

                    st.markdown("--- ")

                    # Exibir Balanço Patrimonial
                    st.markdown("### Balanço Patrimonial (Balance Sheet)")
                    if not balance_sheet.empty:
                         # Transpor o DataFrame para que as datas fiquem nas colunas
                        st.dataframe(balance_sheet.T.style.format(precision=2))
                    else:
                        st.info("Balanço Patrimonial não disponível.")

                    st.markdown("--- ")

                    # Exibir Fluxo de Caixa
                    st.markdown("### Demonstrativo de Fluxo de Caixa (Cash Flow)")
                    if not cashflow.empty:
                         # Transpor o DataFrame para que as datas fiquem nas colunas
                        st.dataframe(cashflow.T.style.format(precision=2))
                    else:
                        st.info("Demonstrativo de Fluxo de Caixa não disponível.")

                except Exception as e:
                    st.warning(f"Não foi possível obter ou exibir as demonstrações financeiras: {str(e)}")
                    st.info("Verifique se o ativo é uma ação (FIIs geralmente não têm demonstrações detalhadas no yfinance) ou se os dados estão disponíveis para este período.")
                
            with tab7:
                analise_especifica_fii(codigo)
                
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados: {str(e)}")
        st.info("💡 Dica: Verifique se o código da ação/FII está correto e tente novamente.")
