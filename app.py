import streamlit as st
import pandas as pd
import requests
import unicodedata

# Configuração da página
st.set_page_config(page_title="Rastreamento Intelipost", layout="wide")
st.title("📦 Rastreamento de Encomendas - Intelipost")

st.markdown("Faça upload de um arquivo CSV com as colunas 'Pedido' e 'Envio codigo' para consultar o status de rastreio.")

uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")

# Função para normalizar colunas
def normalizar_colunas(colunas):
    return [unicodedata.normalize('NFKD', c).encode('ascii', errors='ignore').decode('utf-8').strip().lower() for c in colunas]

# Consulta de status via Intelipost
def buscar_status_intelipost(codigo):
    url = f"https://api.intelipost.com.br/api/v1/tracking/{codigo}"
    headers = {
        "logistic-provider-api-key": "f831fdc3-dc90-dd4f-66d7-2f7c023560d0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            eventos = data.get("events", [])
            if eventos:
                ultimo = eventos[0]
                descricao = ultimo.get("description", "Sem descrição")
                data_evento = ultimo.get("event_date", "")
                return f"{descricao} em {data_evento}"
            else:
                return "Sem eventos encontrados"
        elif response.status_code == 404:
            return "Código não encontrado"
        else:
            return f"Erro: {response.status_code}"
    except Exception as e:
        return "Erro na consulta"

# Processamento do CSV
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';')
        df.columns = normalizar_colunas(df.columns)

        if 'pedido' not in df.columns or 'envio codigo' not in df.columns:
            st.error("O arquivo precisa conter as colunas 'Pedido' e 'Envio codigo'.")
        else:
            rastreios = []

            with st.spinner('Consultando a API Intelipost...'):
                for _, row in df.iterrows():
                    pedido = row['pedido']
                    codigo = str(row['envio codigo']).strip()
                    if not codigo:
                        rastreios.append({"Pedido": pedido, "Código": codigo, "Status": "Código vazio"})
                        continue

                    status = buscar_status_intelipost(codigo)
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
