
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import unicodedata

st.set_page_config(page_title="Rastreamento de Pedidos", layout="wide")
st.title("📦 Rastreamento de Encomendas - Correios")

st.markdown("Faça upload do arquivo CSV com os pedidos. O app buscará o status de cada código de rastreio.")

uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")

def normalizar_colunas(colunas):
    return [unicodedata.normalize('NFKD', c).encode('ascii', errors='ignore').decode('utf-8').strip().lower() for c in colunas]

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';')
        df.columns = normalizar_colunas(df.columns)

        if 'pedido' not in df.columns or 'envio codigo' not in df.columns:
            st.error("O arquivo precisa conter as colunas 'Pedido' e 'Envio codigo'.")
        else:
            rastreios = []

            with st.spinner('Buscando status dos pedidos...'):
                for _, row in df.iterrows():
                    pedido = row['pedido']
                    codigo = str(row['envio codigo']).strip()
                    if not codigo:
                        rastreios.append({"Pedido": pedido, "Código": codigo, "Status": "Código vazio"})
                        continue

                    url = f"https://www.linkcorreios.com.br/{codigo}"
                    headers = {"User-Agent": "Mozilla/5.0"}

                    try:
                        response = requests.get(url, headers=headers, timeout=10)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        status_html = soup.find("ul", class_="linha_status")
                        if status_html:
                            status = status_html.find("li").text.strip()
                        else:
                            status = "Status não encontrado"
                    except Exception:
                        status = "Erro na consulta"

                    rastreios.append({"Pedido": pedido, "Código": codigo, "Status": status})

            resultado_df = pd.DataFrame(rastreios)
            st.success("Consulta finalizada!")
            st.dataframe(resultado_df, use_container_width=True)

            csv = resultado_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar resultado em CSV",
                data=csv,
                file_name='status_rastreamento.csv',
                mime='text/csv'
            )
    except Exception as e:
        st.error("Erro ao ler o arquivo. Verifique se está no formato correto.")
