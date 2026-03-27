import streamlit as st
import pandas as pd
import plotly.express as px
import re
from io import BytesIO
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS
# ==========================================
st.set_page_config(layout="wide", page_title="Dashboard de Contratos", page_icon="📊")

st.markdown("""
<style>
    /* Margens responsivas e layout wide otimizado */
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 2rem !important; 
    }
    /* Fundo 100% branco para o Menu Lateral (Sidebar) */
    [data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
    }
    /* Tabs Congeladas no Topo (Position Sticky) */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        position: sticky; top: 0; z-index: 999; background-color: white;
        padding-top: 10px; padding-bottom: 10px; border-bottom: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNÇÕES DE LIMPEZA, FORMATAÇÃO E COMPONENTES
# ==========================================
@st.cache_data
def clean_currency(val):
    if pd.isna(val):
        return 0.0
    clean_str = str(val).replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

@st.cache_data
def extract_year(date_str):
    if pd.isna(date_str):
        return None
    match = re.search(r'(\d{4})', str(date_str))
    return int(match.group(1)) if match else None

def formatar_moeda_br(valor):
    valor_formatado = f"{valor:,.2f}"
    valor_br = valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor_br}"

def criar_card_metrica(titulo, valor):
    """Cria um Card HTML customizado para garantir o tamanho da fonte"""
    html = f"""
    <div style="background-color: #FFFFFF; padding: 20px; border-radius: 10px; 
                border-left: 6px solid #1E3A8A; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); 
                text-align: center; margin-bottom: 20px;">
        <h4 style="color: #555555; font-size: 1.4rem; margin-bottom: 5px; font-weight: 500;">{titulo}</h4>
        <h2 style="color: #2E7D32; font-size: 2.8rem; margin: 0; font-weight: 800;">{valor}</h2>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 3. TABELAS E EXPORTAÇÃO
# ==========================================
def render_custom_html_table(df):
    styles = [
        {'selector': 'th', 'props': [('background-color', '#1E3A8A'), ('color', 'white'), ('font-size', '15px'), ('text-align', 'center'), ('padding', '12px')]},
        {'selector': 'td', 'props': [('font-size', '14px'), ('padding', '10px'), ('border-bottom', '1px solid #E0E0E0'), ('text-align', 'center')]},
        {'selector': 'tr:hover td', 'props': [('background-color', '#F5F5F5')]}
    ]
    html_table = df.style.set_table_styles(styles).hide(axis="index").to_html()
    st.markdown(html_table, unsafe_allow_html=True)

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()

# ==========================================
# 4. GESTÃO DE ESTADO (ROTEAMENTO)
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = "Capa"

# ==========================================
# 5. CARREGAMENTO DOS DADOS (Exemplo)
# ==========================================
@st.cache_data
def load_data():
    data = {
        "NOME DA EMPRESA": ["M. N. LEITE", "VECTORE CONSULTORIA", "URUS LTDA", "LB CENTAURO"],
        "MODALIDADE": ["INEXIGIBILIDADE", "INEXIGIBILIDADE", "DISPENSA", "PREGÃO ELETRÔNICO"],
        "VALOR CONTRATO": ["R$ 150.000,50", "R$ 2.300.000,00", "R$ 45.000,00", "R$ 80.500,25"],
        "DATA REF": ["15/02/2025", "20/03/2026", "10/01/2026", "05/05/2025"]
    }
    df = pd.DataFrame(data)
    df['VALOR_NUMERICO'] = df['VALOR CONTRATO'].apply(clean_currency)
    df['ANO_REF'] = df['DATA REF'].apply(extract_year)
    return df

df = load_data()

# ==========================================
# 6. PÁGINA: CAPA
# ==========================================
if st.session_state.page == "Capa":
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Sistema de Controle de Contratos</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80", width="stretch")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Acessar Painel", width="stretch"):
            st.session_state.page = "Painel"
            st.rerun()

# ==========================================
# 7. PÁGINA: PAINEL PRINCIPAL
# ==========================================
elif st.session_state.page == "Painel":
    
    with st.sidebar:
        st.header("🔍 Filtros Globais")
        st.write("Selecione abaixo para filtrar:")
        
        anos_disponiveis = df['ANO_REF'].dropna().unique().tolist()
        modalidades = df['MODALIDADE'].dropna().unique().tolist()
        
        ano_selecionado = st.multiselect("Filtrar por Ano:", anos_disponiveis, default=anos_disponiveis, key="filtro_ano")
        modalidade_selecionada = st.multiselect("Modalidade:", modalidades, default=modalidades, key="filtro_modalidade")
        
        if st.button("🗑️ Limpar Todos os Filtros", width="stretch"):
            if "filtro_ano" in st.session_state: del st.session_state["filtro_ano"]
            if "filtro_modalidade" in st.session_state: del st.session_state["filtro_modalidade"]
            st.rerun()
            
        st.markdown("---")
        if st.button("⬅️ Voltar para Capa", width="stretch"):
            st.session_state.page = "Capa"
            st.rerun()

    df_filtrado = df.copy()
    if ano_selecionado: df_filtrado = df_filtrado[df_filtrado['ANO_REF'].isin(ano_selecionado)]
    if modalidade_selecionada: df_filtrado = df_filtrado[df_filtrado['MODALIDADE'].isin(modalidade_selecionada)]

    ano_atual = datetime.now().year
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    tab1, tab2 = st.tabs(["📊 Visão Geral", "📄 Detalhamento e Tabelas"])
    
    with tab1:
        st.markdown(f"#### Exercício: {ano_atual} (última atualização: {data_hoje})")
        st.write("---")
        
        # UTILIZANDO OS NOVOS CARDS CUSTOMIZADOS
        m1, m2, m3 = st.columns(3)
        with m1:
            criar_card_metrica("Total de Contratos", len(df_filtrado))
        with m2:
            criar_card_metrica("Valor Total Estimado", formatar_moeda_br(df_filtrado['VALOR_NUMERICO'].sum()))
        with m3:
            criar_card_metrica("Empresas Únicas", df_filtrado['NOME DA EMPRESA'].nunique())
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            df_bar = df_filtrado.groupby('MODALIDADE', as_index=False)['VALOR_NUMERICO'].sum()
            fig_bar = px.bar(df_bar, x='MODALIDADE', y='VALOR_NUMERICO', title="<b>Valor por Modalidade</b>", color_discrete_sequence=['#1E3A8A'])
            
            fig_bar.update_layout(
                separators=",.",
                font=dict(size=16), # Aumentou a fonte dos eixos
                title=dict(font=dict(size=24)) # Aumentou drasticamente o título
            ) 
            fig_bar.update_traces(hovertemplate='Modalidade: %{x}<br>Valor: R$ %{y:,.2f}')
            st.plotly_chart(fig_bar, width="stretch")
            
        with c2:
            fig_pie = px.pie(df_filtrado, names='MODALIDADE', values='VALOR_NUMERICO', title="<b>Distribuição das Modalidades</b>")
            
            fig_pie.update_layout(
                separators=",.",
                font=dict(size=16),
                title=dict(font=dict(size=24))
            )
            fig_pie.update_traces(hovertemplate='Modalidade: %{label}<br>Valor: R$ %{value:,.2f}', textfont_size=16)
            st.plotly_chart(fig_pie, width="stretch")

    with tab2:
        st.markdown(f"#### Detalhamento de Dados - Exercício: {ano_atual} (última atualização: {data_hoje})")
        st.write("---")
        
        st.write("**Visualização de Dados (HTML Styled Table)**")
        render_custom_html_table(df_filtrado[['NOME DA EMPRESA', 'MODALIDADE', 'VALOR CONTRATO', 'DATA REF', 'ANO_REF']])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        excel_file = convert_df_to_excel(df_filtrado)
        st.download_button(
            label="📥 Exportar Dados Filtrados para Excel (.xlsx)",
            data=excel_file,
            file_name=f"Relatorio_Contratos_{data_hoje.replace('/', '-')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )