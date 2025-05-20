# Requisitos: Instale com 'pip install yfinance streamlit pandas matplotlib'

import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

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
    st.subheader("Dados Fundamentais")
    st.write(f"**Empresa:** {info.get('longName', 'N/A')}")
    st.write(f"**Setor:** {info.get('sector', 'N/A')}")
    st.write(f"**Preço atual:** R$ {info.get('previousClose', 'N/A'):.2f}")
    st.write(f"**P/L:** {info.get('trailingPE', 'N/A')}")
    st.write(f"**Dividend Yield:** {round(info.get('dividendYield', 0) * 100, 2)}%")
    st.write(f"**ROE:** {round(info.get('returnOnEquity', 0) * 100, 2)}%")
    st.write(f"**Dívida/Patrimônio (Debt/Equity):** {info.get('debtToEquity', 'N/A')}")
    st.write(f"**Lucro por ação (EPS):** {info.get('trailingEps', 'N/A')}")

def mostrar_grafico(historico):
    st.subheader("Tendência de Preço - Último Ano")
    fig, ax = plt.subplots(figsize=(12, 6))
    historico['Close'].plot(ax=ax, color='#2196F3', linewidth=2)
    ax.set_ylabel("Preço de Fechamento (R$)")
    ax.set_xlabel("Data")
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    st.pyplot(fig)

def analise_temporal(historico):
    st.subheader("📊 Análise Temporal")
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
        st.metric("Variação 3 meses", f"{variacao_3m:.2f}%")
    with col2:
        st.metric("Variação 6 meses", f"{variacao_6m:.2f}%")
    with col3:
        st.metric("Variação 1 ano", f"{variacao_1a:.2f}%")

def analise_sugestiva(info):
    st.subheader("📌 Recomendações por Horizonte de Investimento")
    pl = info.get('trailingPE')
    dy = info.get('dividendYield')
    roe = info.get('returnOnEquity')
    debt_equity = info.get('debtToEquity')
    st.write("### Curto Prazo (3-6 meses)")
    if pl and pl < 10:
        st.success("✅ P/L atrativo para curto prazo")
    elif pl:
        st.warning(f"⚠️ P/L elevado para curto prazo: {pl:.2f}")
    st.write("### Médio Prazo (6-12 meses)")
    if dy and dy > 0.05:
        st.success("💰 Bom Dividend Yield para médio prazo")
    elif dy:
        st.info(f"ℹ️ Dividend Yield moderado: {dy * 100:.2f}%")
    st.write("### Longo Prazo (1+ anos)")
    if roe and roe > 0.15:
        st.success("📈 ROE forte para longo prazo")
    elif roe:
        st.info(f"ℹ️ ROE moderado: {roe * 100:.2f}%")
    if debt_equity and debt_equity < 1:
        st.success("💪 Baixa alavancagem financeira")
    elif debt_equity:
        st.warning(f"⚠️ Alavancagem financeira elevada: {debt_equity:.2f}")

# App Streamlit
st.title("📈 Avaliador de Ações - Fundamentalista e Técnico")
st.write("Insira o código da ação (ex: PETR4, VALE3)")
codigo = st.text_input("Código da ação:", value="PETR4")
if st.button("Analisar"):
    try:
        info, historico = obter_dados(codigo)
        mostrar_dados_fundamentais(info)
        mostrar_grafico(historico)
        analise_temporal(historico)
        analise_sugestiva(info)
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
