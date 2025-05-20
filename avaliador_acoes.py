# Requisitos: Instale com 'pip install yfinance streamlit pandas matplotlib requests beautifulsoup4'

import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import unicodedata
import os
import requests
from bs4 import BeautifulSoup
import io

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
        
        st.markdown("### Indicadores de Endividamento")
        with st.container(): # Usando container para agrupar
            st.write(f"**Dívida Líquida/EBITDA:** {info.get('debtToEbitda', 'N/A')}")
            st.write(f"**Liquidez Corrente:** {info.get('currentRatio', 'N/A')}")
            st.write(f"**Caixa Total:** R$ {info.get('totalCash', 'N/A'):,.2f}")
            st.write(f"**Dívida Total:** R$ {info.get('totalDebt', 'N/A'):,.2f}")

def mostrar_grafico(historico):
    st.subheader("📈 Tendência de Preço")
    fig, ax = plt.subplots(figsize=(12, 6))
    historico['Close'].plot(ax=ax, color='#2196F3', linewidth=2)
    ax.set_ylabel("Preço de Fechamento (R$)")
    ax.set_xlabel("Data")
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    st.pyplot(fig)

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
    sugestoes = []
    score = 0
    max_score = 10

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
    min_raw_score = -8 # Estimativa do menor score possível
    max_raw_score = 10 # Estimativa do maior score possível
    # Mapear o score bruto para a escala 0-10
    score_final = max(0, min(10, round((score - min_raw_score) / (max_raw_score - min_raw_score) * 10)))

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
    try:
        url = "https://br.tradingview.com/screener/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Aqui precisamos encontrar o elemento correto que contém as ações
            # Como o TradingView usa JavaScript para carregar os dados, precisaremos
            # usar uma abordagem diferente, como Selenium ou a API do TradingView
            
            st.warning("⚠️ A busca direta no TradingView não está disponível no momento devido a limitações técnicas.")
            st.info("💡 Sugestão: Use a lista predefinida de ações ou adicione manualmente os códigos desejados.")
            
            return []
        else:
            st.error(f"❌ Erro ao acessar o TradingView: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar ações: {str(e)}")
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

    # Adicionar botão para buscar ações do TradingView
    if st.button("🔄 Atualizar Lista de Ações"):
        with st.spinner('Buscando ações brasileiras...'):
            acoes = buscar_acoes_brasileiras()
            if acoes:
                st.success(f"✅ {len(acoes)} ações encontradas!")
            else:
                st.info("ℹ️ Use a lista predefinida de ações ou adicione manualmente os códigos desejados.")

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
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Dados Fundamentais",
                "📈 Gráfico e Análise Temporal",
                "🌐 Análise Setorial",
                "📌 Recomendações"
            ])
            
            with tab1:
                mostrar_dados_fundamentais(info)
            
            with tab2:
                mostrar_grafico(historico)
                analise_temporal(historico)
            
            with tab3:
                analise_setorial_noticias(info, codigo)
            
            with tab4:
                analise_sugestiva(info, perfil)
                
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados: {str(e)}")
        st.info("💡 Dica: Verifique se o código da ação/FII está correto e tente novamente.")
