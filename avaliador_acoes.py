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

def obter_dados(codigo):
    try:
        codigo_formatado = formatar_codigo_acao(codigo)
        acao = yf.Ticker(codigo_formatado)
        
        # Verificar se o ativo existe
        try:
            info = acao.info
            if not info:
                st.error(f"❌ Ativo {codigo} não encontrado.")
                return None, None
        except Exception as e:
            st.error(f"❌ Erro ao obter informações do ativo {codigo}: {str(e)}")
            return None, None
            
        # Obter histórico com tratamento de erro
        try:
            historico = acao.history(period="1y")
            if historico.empty:
                st.warning(f"⚠️ Não foi possível obter histórico para {codigo}.")
                return info, None
        except Exception as e:
            st.warning(f"⚠️ Erro ao obter histórico para {codigo}: {str(e)}")
            return info, None

        return info, historico
        
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados: {str(e)}")
        st.info("💡 Dica: Verifique se o código da ação/FII está correto e tente novamente.")
        return None, None

def mostrar_dados_fundamentais(info):
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
                preco = info.get('previousClose')
                if preco is not None:
                    st.write(f"**Preço atual:** R$ {float(preco):.2f}")
                else:
                    st.write("**Preço atual:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar informações básicas: {str(e)}")
        
        st.markdown("### Indicadores de Valuation")
        with st.container():
            try:
                pl = info.get('trailingPE')
                if pl is not None:
                    st.write(f"**P/L:** {float(pl):.2f} *<small>(Preço/Lucro)</small>*", unsafe_allow_html=True)
                else:
                    st.write("**P/L:** N/A")
                    
                p_vpa = info.get('priceToBook')
                if p_vpa is not None:
                    st.write(f"**P/VPA:** {float(p_vpa):.2f} *<small>(Preço/Valor Patrimonial)</small>*", unsafe_allow_html=True)
                else:
                    st.write("**P/VPA:** N/A")
                    
                ev_ebitda = info.get('enterpriseToEbitda')
                if ev_ebitda is not None:
                    st.write(f"**EV/EBITDA:** {float(ev_ebitda):.2f} *<small>(Valor da Empresa/EBITDA)</small>*", unsafe_allow_html=True)
                else:
                    st.write("**EV/EBITDA:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores de valuation: {str(e)}")
    
    with col2:
        st.markdown("### Indicadores de Rentabilidade")
        with st.container():
            try:
                dy = info.get('dividendYield')
                if dy is not None:
                    st.write(f"**Dividend Yield:** {float(dy) * 100:.2f}%", unsafe_allow_html=True)
                else:
                    st.write("**Dividend Yield:** N/A")
                    
                roe = info.get('returnOnEquity')
                if roe is not None:
                    st.write(f"**ROE:** {float(roe) * 100:.2f}%", unsafe_allow_html=True)
                else:
                    st.write("**ROE:** N/A")
                    
                margem_bruta = info.get('grossMargins')
                if margem_bruta is not None:
                    st.write(f"**Margem Bruta:** {float(margem_bruta) * 100:.2f}%", unsafe_allow_html=True)
                else:
                    st.write("**Margem Bruta:** N/A")
                    
                margem_liquida = info.get('profitMargins')
                if margem_liquida is not None:
                    st.write(f"**Margem Líquida:** {float(margem_liquida) * 100:.2f}%", unsafe_allow_html=True)
                else:
                    st.write("**Margem Líquida:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores de rentabilidade: {str(e)}")
        
        st.markdown("### Mais Indicadores de Rentabilidade")
        with st.container():
            try:
                margem_ebitda = info.get('ebitdaMargins')
                if margem_ebitda is not None:
                    st.write(f"**Margem EBITDA:** {float(margem_ebitda) * 100:.2f}%", unsafe_allow_html=True)
                else:
                    st.write("**Margem EBITDA:** N/A")
                    
                margem_operacional = info.get('operatingMargins')
                if margem_operacional is not None:
                    st.write(f"**Margem Operacional:** {float(margem_operacional) * 100:.2f}%", unsafe_allow_html=True)
                else:
                    st.write("**Margem Operacional:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores adicionais: {str(e)}")

        st.markdown("### Indicadores de Endividamento")
        with st.container():
            try:
                debt_ebitda = info.get('debtToEbitda')
                if debt_ebitda is not None:
                    st.write(f"**Dívida Líquida/EBITDA:** {float(debt_ebitda):.2f}")
                else:
                    st.write("**Dívida Líquida/EBITDA:** N/A")
                    
                debt_equity = info.get('debtToEquity')
                if debt_equity is not None:
                    st.write(f"**Dívida/Patrimônio Líquido:** {float(debt_equity):.2f}")
                else:
                    st.write("**Dívida/Patrimônio Líquido:** N/A")
                    
                liquidez = info.get('currentRatio')
                if liquidez is not None:
                    st.write(f"**Liquidez Corrente:** {float(liquidez):.2f}")
                else:
                    st.write("**Liquidez Corrente:** N/A")
                    
                caixa = info.get('totalCash')
                if caixa is not None:
                    st.write(f"**Caixa Total:** R$ {float(caixa):,.2f}")
                else:
                    st.write("**Caixa Total:** N/A")
                    
                divida = info.get('totalDebt')
                if divida is not None:
                    st.write(f"**Dívida Total:** R$ {float(divida):,.2f}")
                else:
                    st.write("**Dívida Total:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores de endividamento: {str(e)}")

        st.markdown("### Indicadores de Fluxo de Caixa")
        with st.container():
            try:
                fco = info.get('operatingCashflow')
                if fco is not None:
                    st.write(f"**Fluxo de Caixa Operacional:** R$ {float(fco):,.2f}")
                else:
                    st.write("**Fluxo de Caixa Operacional:** N/A")
                    
                fcl = info.get('freeCashflow')
                if fcl is not None:
                    st.write(f"**Fluxo de Caixa Livre:** R$ {float(fcl):,.2f}")
                else:
                    st.write("**Fluxo de Caixa Livre:** N/A")
            except Exception as e:
                st.warning(f"⚠️ Erro ao mostrar indicadores de fluxo de caixa: {str(e)}")

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
        # Obter dados históricos dos indicadores com tratamento de erro
        try:
            historico_indicadores = acao.history(period="5y")
            if historico_indicadores.empty:
                st.warning("⚠️ Não foi possível obter dados históricos para este período.")
                return
        except Exception as e:
            st.warning(f"⚠️ Erro ao obter histórico: {str(e)}")
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
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📊 Dados Fundamentais",
                "📈 Gráfico e Análise Temporal",
                "🌐 Análise Setorial",
                "📌 Recomendações",
                "💰 Valuation Avançado",
                "📜 Demonstrações Financeiras Históricas"
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
                
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados: {str(e)}")
        st.info("💡 Dica: Verifique se o código da ação/FII está correto e tente novamente.")
