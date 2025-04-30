
import streamlit as st
import pandas as pd
import requests
import unicodedata

st.set_page_config(page_title="Rastreamento Correios - API Postmon", layout="wide")
st.title("📦 Rastreamento de Encomendas - Correios (via API Postmon)")

st.markdown("Faça upload de um arquivo CSV com as colunas 'Pedido' e 'Envio codigo' para consultar o status de rastreio dos Correios.")

uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")

def normalizar_colunas(colunas):
    return [unicodedata.normalize('NFKD', c).encode('ascii', errors='ignore').decode('utf-8').strip().lower() for c in colunas]

def buscar_status_postmon(codigo):
    url = f"https://api.postmon.com.br/v1/rastreio/ect/{codigo}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            eventos = data.get('eventos', [])
            if eventos:
                ultimo = eventos[0]
                descricao = ultimo.get('descricao', 'Sem descrição')
                data_evento = ultimo.get('data', '')
                return f"{descricao} em {data_evento}"
            else:
                return "Sem eventos"
        elif response.status_code == 404:
            return "Código não encontrado"
        else:
            return f"Erro: {response.status_code}"
    except Exception as e:
        return "Erro na consulta"

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';')
        df.columns = normalizar_colunas(df.columns)

        if 'pedido' not in df.columns or 'envio codigo' not in df.columns:
            st.error("O arquivo precisa conter as colunas 'Pedido' e 'Envio codigo'.")
        else:
            rastreios = []

            with st.spinner('Consultando a API Postmon...'):
                for _, row in df.iterrows():
                    pedido = row['pedido']
                    codigo = str(row['envio codigo']).strip()
                    if not codigo:
                        rastreios.append({"Pedido": pedido, "Código": codigo, "Status": "Código vazio"})
                        continue

                    status = buscar_status_postmon(codigo)
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
