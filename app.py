import streamlit as st
import pandas as pd
import plotly.express as px
from main import executar_agregador

st.set_page_config(
    page_title="Monitor de Imóveis | Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }

    /* Força a cor do texto para preto dentro dos cards (Título e Valor) */
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: #000000 !important;
    }

    div[data-testid="stDataFrameResizable"] { border-radius: 10px; overflow: hidden; }
    </style>
""", unsafe_allow_html=True)

class ImoveisApp:
    """
    Classe principal que gerencia a interface do Streamlit.
    Segue o padrão de encapsulamento para evitar variáveis globais soltas.
    """

    def __init__(self):
        self._inicializar_estado()

    def _inicializar_estado(self):
        """Inicializa o Session State para persistir dados entre interações."""
        if "dados" not in st.session_state:
            st.session_state["dados"] = pd.DataFrame()
        if "executou" not in st.session_state:
            st.session_state["executou"] = False

    def render(self):
        """Método principal de renderização da UI."""
        self._render_sidebar()
        self._render_header()

        if st.session_state["executou"] and not st.session_state["dados"].empty:
            self._render_dashboard(st.session_state["dados"])
            self._render_tabela(st.session_state["dados"])
        elif st.session_state["executou"] and st.session_state["dados"].empty:
            st.warning("⚠️ A pesquisa foi concluída, mas nenhum imóvel foi encontrado com os critérios atuais.")
        else:
            self._render_empty_state()

    def _render_sidebar(self):
        with st.sidebar:
            st.header("Painel de Controle")
            
            st.info("💡 Clique no botão abaixo para iniciar a coleta de dados em tempo real.")
            
            if st.button("🚀 Executar Monitorização", type="primary", use_container_width=True):
                self._executar_processo_scraping()

            st.markdown("---")
            st.caption(f"Versão do Sistema: 2.0.1")
            st.caption("Desenvolvido com Clean Architecture")

    def _render_header(self):
        st.title("🏠 Agregador de Imóveis Inteligente")
        st.markdown("Visualize, compare e analise oportunidades imobiliárias de múltiplas fontes.")

    def _render_empty_state(self):
        """Tela inicial antes da execução."""
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown("### 👈 Inicie a busca no menu lateral")
            st.markdown("O sistema irá conectar-se às imobiliárias configuradas e unificar os resultados aqui.")

    def _executar_processo_scraping(self):
        """Lógica de chamada do backend."""
        with st.spinner("🔍 Conectando aos sites, baixando HTML e processando dados..."):
            try:
                df_resultados = executar_agregador()
                
                if not df_resultados.empty:
                    df_resultados['Preco_Numerico'] = (
                        df_resultados['Preco']
                        .astype(str)
                        .str.replace('R$', '', regex=False)
                        .str.replace('.', '', regex=False)
                        .str.replace(',', '.', regex=False)
                        .str.replace('Consultar', '0', regex=False)
                        .str.strip()
                    )
                    df_resultados['Preco_Numerico'] = pd.to_numeric(df_resultados['Preco_Numerico'], errors='coerce')

                st.session_state["dados"] = df_resultados
                st.session_state["executou"] = True
                
                st.success("Processamento concluído com sucesso!")
                
            except Exception as e:
                st.error(f"Ocorreu um erro crítico durante a execução: {e}")

    def _render_dashboard(self, df: pd.DataFrame):
        """Exibe KPIs e Gráficos."""
        st.markdown("### 📊 Visão Geral")
        
        total_imoveis = len(df)
        
        media_preco = 0
        min_preco = 0
        
        if 'Preco_Numerico' in df.columns:
            media_preco = df['Preco_Numerico'].mean()
            imoveis_validos = df[df['Preco_Numerico'] > 0]
            if not imoveis_validos.empty:
                min_preco = imoveis_validos['Preco_Numerico'].min()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Imóveis", total_imoveis)
        col2.metric("Preço Médio", f"R$ {media_preco:,.2f}")
        col3.metric("Menor Valor", f"R$ {min_preco:,.2f}")
        col4.metric("Fontes", f"{df['Imobiliaria'].nunique()}")

        st.markdown("---")

        col_chart_1, col_chart_2 = st.columns(2)
        
        with col_chart_1:
            st.subheader("Distribuição por Imobiliária")
            if not df.empty:
                fig_pie = px.pie(df, names='Imobiliaria', title='Volume de Imóveis por Fonte', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart_2:
            st.subheader("Imóveis por Bairro")
            if 'Bairro' in df.columns and not df.empty:
                contagem_bairro = df['Bairro'].value_counts().reset_index()
                contagem_bairro.columns = ['Bairro', 'Quantidade']
                fig_bar = px.bar(contagem_bairro.head(10), x='Quantidade', y='Bairro', orientation='h', title='Top 10 Bairros')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar gráfico de bairros.")

    def _render_tabela(self, df: pd.DataFrame):
        """Exibe a tabela interativa e botões de exportação."""
        st.markdown("### 📋 Resultados Detalhados")
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Link": st.column_config.LinkColumn(
                    "Link Original", 
                    display_text="Acessar Imóvel"
                ),
                "Preco": st.column_config.TextColumn("Preço (R$)"),
                "Preco_Numerico": None,
                "Area": st.column_config.TextColumn("Área"),
                "Imobiliaria": st.column_config.Column("Fonte", width="small")
            }
        )

        col1, col2 = st.columns([1, 6])
        with col1:
            csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name="imoveis_monitorados.csv",
                mime="text/csv",
                key='download-csv'
            )

if __name__ == "__main__":
    app = ImoveisApp()
    app.render()