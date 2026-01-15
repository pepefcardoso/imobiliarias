import streamlit as st
from main import executar_agregador

st.set_page_config(page_title="Monitor de Imóveis", layout="wide")

def main_ui():
    st.title("🏠 Agregador de Imóveis")
    
    if st.button("🚀 Executar Monitorização"):
        
        with st.spinner("Pesquisando... Por favor aguarde."):
            try:
                df_resultados = executar_agregador()
                
                if not df_resultados.empty:
                    st.success(f"Pesquisa concluída! {len(df_resultados)} imóveis agregados.")
                    
                    st.subheader("Resultados Consolidados")
                    st.dataframe(
                        df_resultados,
                        use_container_width=True,
                        column_config={
                            "Link": st.column_config.LinkColumn("Link"),
                            "Preco": st.column_config.TextColumn("Preço")
                        }
                    )
                else:
                    st.warning("A pesquisa não encontrou imóveis.")
                    
            except Exception as e:
                st.error(f"Erro ao executar a pesquisa: {e}")

if __name__ == "__main__":
    main_ui()