# Requisitos: Instale com 'pip install yfinance streamlit pandas matplotlib'

import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import unicodedata
import os
import requests
import io

# Lista simplificada de ações e FIIs (adicione mais conforme desejar)
ATIVOS_B3 = [
    # Bancos
    {"Codigo": "ITUB4", "Nome": "Itaú Unibanco"},
    {"Codigo": "BBDC4", "Nome": "Bradesco"},
    {"Codigo": "BBAS3", "Nome": "Banco do Brasil"},
    {"Codigo": "SANB11", "Nome": "Santander"},
    {"Codigo": "BPAC11", "Nome": "BTG Pactual"},
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
    # Elétricas
    {"Codigo": "ELET3", "Nome": "Eletrobras ON"},
    {"Codigo": "ELET6", "Nome": "Eletrobras PNB"},
    {"Codigo": "ENBR3", "Nome": "EDP Brasil"},
    {"Codigo": "CMIG4", "Nome": "Cemig"},
    {"Codigo": "CPLE6", "Nome": "Copel"},
    {"Codigo": "TAEE11", "Nome": "Taesa"},
    {"Codigo": "ENGI11", "Nome": "Engie Brasil"},
    {"Codigo": "EQTL3", "Nome": "Equatorial"},
    # Varejo e consumo
    {"Codigo": "MGLU3", "Nome": "Magazine Luiza"},
    {"Codigo": "VIIA3", "Nome": "Via"},
    {"Codigo": "LREN3", "Nome": "Lojas Renner"},
    {"Codigo": "AMER3", "Nome": "Americanas"},
    {"Codigo": "RAIL3", "Nome": "Rumo"},
    {"Codigo": "WEGE3", "Nome": "WEG"},
    {"Codigo": "RENT3", "Nome": "Localiza"},
    {"Codigo": "ABEV3", "Nome": "Ambev"},
    {"Codigo": "B3SA3", "Nome": "B3"},
    {"Codigo": "CYRE3", "Nome": "Cyrela"},
    {"Codigo": "EZTC3", "Nome": "EZTEC"},
    {"Codigo": "MRVE3", "Nome": "MRV"},
    {"Codigo": "BRML3", "Nome": "BR Malls"},
    {"Codigo": "MULT3", "Nome": "Multiplan"},
    {"Codigo": "HYPE3", "Nome": "Hypera"},
    {"Codigo": "RADL3", "Nome": "Raia Drogasil"},
    {"Codigo": "SULA11", "Nome": "SulAmérica"},
    {"Codigo": "CIEL3", "Nome": "Cielo"},
    {"Codigo": "VVAR3", "Nome": "Via Varejo"},
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
    # Adicione mais ativos conforme desejar!
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
    st.subheader("Dados Fundamentais")
    st.write(f"**Empresa/FII:** {info.get('longName', 'N/A')}")
    st.write(f"**Setor:** {info.get('sector', 'N/A')}")
    st.write(f"**Preço atual:** R$ {info.get('previousClose', 'N/A'):.2f}")
    st.write(f"**P/L:** {info.get('trailingPE', 'N/A')}")
    st.write(f"**P/VPA:** {info.get('priceToBook', 'N/A')}")
    st.write(f"**Dividend Yield:** {round(info.get('dividendYield', 0) * 100, 2)}%")
    st.write(f"**EV/EBITDA:** {info.get('enterpriseToEbitda', 'N/A')}")
    st.write(f"**Dívida Líquida/EBITDA:** {info.get('debtToEbitda', 'N/A')}")
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

# ====== NOVO: Perfil do investidor ======
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

# ====== NOVO: Análise Técnica ======
def analise_tecnica(historico):
    st.subheader("📉 Análise Técnica Básica")
    historico = historico.copy()
    historico['MM21'] = historico['Close'].rolling(window=21).mean()
    historico['MM50'] = historico['Close'].rolling(window=50).mean()
    # IFR (RSI)
    delta = historico['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / roll_down
    historico['RSI'] = 100.0 - (100.0 / (1.0 + rs))
    fig, ax = plt.subplots(figsize=(12, 6))
    historico['Close'].plot(ax=ax, color='#2196F3', linewidth=2, label='Preço')
    historico['MM21'].plot(ax=ax, color='orange', linestyle='--', label='Média Móvel 21')
    historico['MM50'].plot(ax=ax, color='green', linestyle='--', label='Média Móvel 50')
    ax.set_ylabel("Preço de Fechamento (R$)")
    ax.set_xlabel("Data")
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    ax.legend()
    st.pyplot(fig)
    st.write(f"**RSI (14 dias):** {historico['RSI'].iloc[-1]:.2f}")
    if historico['RSI'].iloc[-1] > 70:
        st.warning("RSI indica sobrecompra (pode haver correção em breve)")
    elif historico['RSI'].iloc[-1] < 30:
        st.success("RSI indica sobrevenda (pode haver oportunidade de compra)")
    else:
        st.info("RSI em zona neutra")

# ====== NOVO: Análise Setorial ======
def analise_setorial(info):
    st.subheader("🌐 Análise Setorial e Macroeconômica")
    setor = info.get('sector', 'N/A')
    explicacao = {
        'Financial Services': 'Setor financeiro tende a ser resiliente, mas sensível a juros.',
        'Energy': 'Setor de energia pode ser cíclico e sensível a commodities.',
        'Utilities': 'Setor de utilidade pública costuma ser defensivo.',
        'Real Estate': 'Setor imobiliário é sensível a juros e ciclos econômicos.',
        'Consumer Defensive': 'Setor defensivo, menos sensível a crises.',
        'Basic Materials': 'Setor de commodities é cíclico e depende do mercado global.',
        'Industrials': 'Setor industrial depende do crescimento econômico.',
        'Healthcare': 'Setor de saúde tende a ser resiliente.',
        'Technology': 'Setor de tecnologia pode ter alto crescimento, mas também volatilidade.',
        'N/A': 'Setor não informado.'
    }
    st.write(f"**Setor:** {setor}")
    st.info(explicacao.get(setor, 'Setor não identificado.'))

# ====== MELHORIA: Recomendações personalizadas ======
def analise_sugestiva(info):
    st.subheader("📌 Recomendações por Horizonte de Investimento e Perfil")
    pl = info.get('trailingPE')
    dy = info.get('dividendYield')
    roe = info.get('returnOnEquity')
    debt_equity = info.get('debtToEquity')
    price_to_book = info.get('priceToBook')
    ev_ebitda = info.get('enterpriseToEbitda')
    sugestoes = []
    # Perfil de crescimento
    if 'crescimento' in perfil.lower() or 'longo' in perfil.lower():
        if roe and roe > 0.15:
            sugestoes.append("📈 ROE forte para crescimento a longo prazo.")
        if pl and pl < 15:
            sugestoes.append("P/L razoável para crescimento.")
    # Perfil de dividendos
    if 'dividendos' in perfil.lower():
        if dy and dy > 0.05:
            sugestoes.append("💰 Bom Dividend Yield para renda passiva.")
        else:
            sugestoes.append("Dividend Yield baixo para foco em dividendos.")
    # Perfil de risco
    if 'baixa' in perfil.lower():
        if debt_equity and debt_equity < 1:
            sugestoes.append("💪 Baixa alavancagem financeira (baixo risco)")
        else:
            sugestoes.append("⚠️ Alavancagem financeira elevada para perfil conservador.")
    if 'alta' in perfil.lower():
        if debt_equity and debt_equity > 2:
            sugestoes.append("⚠️ Alavancagem alta, atenção ao risco!")
    # Recomendações gerais
    if pl and pl > 20:
        sugestoes.append("⚠️ P/L elevado, ação pode estar cara.")
    if price_to_book and price_to_book > 2:
        sugestoes.append("⚠️ P/VPA elevado, atenção ao valuation.")
    if ev_ebitda and ev_ebitda > 12:
        sugestoes.append("⚠️ EV/EBITDA elevado para o setor.")
    if not sugestoes:
        sugestoes.append("Sem alertas relevantes para o perfil selecionado.")
    for s in sugestoes:
        st.write(s)

# App Streamlit
st.title("📈 Avaliador de Ações e FIIs - Fundamentalista e Técnico")

with st.expander("🔍 Como analisar uma ação ou FII? (clique para ver dicas)"):
    st.markdown("""
**1. Análise Fundamentalista (saúde e valor da empresa)**  
- **Lucro e crescimento:**  
  - Lucro por ação (LPA): mede o lucro líquido dividido pelo número de ações.  
  - Histórico de crescimento: a empresa está crescendo ano após ano?  
- **Valuation (valor justo da ação):**  
  - P/L (Preço/Lucro): compara o preço da ação com o lucro da empresa. Um P/L muito alto pode indicar ação cara.  
  - P/VPA (Preço/Valor Patrimonial por Ação): mede quanto o mercado está pagando sobre o valor contábil da empresa.  
  - Dividend Yield: rendimento que o investidor recebe em dividendos.  
  - EV/EBITDA: útil para comparar empresas do mesmo setor.  
- **Endividamento:**  
  - Dívida líquida/EBITDA: mostra se a empresa tem fôlego para pagar suas dívidas.  
  - Grau de alavancagem: dívida sobre o patrimônio.  
- **Governança corporativa:**  
  - A empresa tem práticas transparentes e sólidas de gestão?  
  - Está envolvida em escândalos ou investigações?  

**2. Análise Técnica (movimento do preço da ação)**  
- Suporte e resistência  
- Tendência de alta ou baixa  
- Volume de negociações  
- Indicadores técnicos: IFR (Índice de Força Relativa), MACD, médias móveis  

**3. Análise Setorial e Macroeconômica**  
- O setor da empresa está em crescimento ou retração?  
- Como a economia afeta o negócio (juros, inflação, câmbio)?  
- A empresa está exposta a riscos regulatórios?  

**4. Perfil do investidor**  
- Você busca crescimento ou renda passiva (dividendos)?  
- Qual seu prazo de investimento?  
- Qual o seu nível de tolerância a risco?  
    """)

df_ativos = carregar_ativos_b3()

nome_empresa = st.text_input("Nome da empresa ou fundo:")
codigo_sugerido = ""
if not df_ativos.empty and nome_empresa:
    codigo_sugerido = buscar_codigo_por_nome(nome_empresa, df_ativos)

if codigo_sugerido:
    st.info(f"Código sugerido: {codigo_sugerido}")
    codigo = st.text_input("Código da ação/FII:", value=codigo_sugerido)
else:
    codigo = st.text_input("Código da ação/FII:")

if st.button("Analisar"):
    try:
        info, historico = obter_dados(codigo)
        mostrar_dados_fundamentais(info)
        mostrar_grafico(historico)
        analise_temporal(historico)
        analise_tecnica(historico)
        analise_setorial(info)
        analise_sugestiva(info)
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
