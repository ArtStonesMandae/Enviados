import streamlit as st
import pandas as pd
import requests
import unicodedata

# Configuração inicial da página
st.set_page_config(page_title="Rastreamento Mandaê", layout="wide")
st.title("📦 Rastreamento de Encomendas - Mandaê (via API)")

st.markdown("Faça upload de um arquivo CSV com as colunas 'Pedido' e 'Envio codigo' para consultar o status de rastreio via Mandaê.")

uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")

# Normalização de colunas para evitar erros com acentos e maiúsculas
def normalizar_colunas(colunas):
    return [unicodedata.normalize('NFKD', c).encode('ascii', errors='ignore').decode('utf-8').strip().lower() for c in colunas]

# Função para consultar status na API da Mandaê
def buscar_status_mandae(codigo):
    url = f"https://api.mandae.com.br/v2/tracking/{codigo}"
    headers = {"Authorization": "Token cd8c9ce94d3c9f9fb6b8ee77c9e8b681"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Sem status')
            updated = data.get('updated_at', '')
            return f"{status} em {updated}" if updated else status
        elif response.status_code == 404:
            return "Código não encontrado"
        else:
            return f"Erro: {response.status_code}"
    except Exception as e:
        return "Erro na consulta"

# Leitura e processamento do arquivo CSV
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';')
        df.columns = normalizar_colunas(df.columns)

        if 'pedido' not in df.columns or 'envio codigo' not in df.columns:
            st.error("O arquivo precisa conter as colunas 'Pedido' e 'Envio codigo'.")
        else:
            rastreios = []

            with st.spinner('Consultando a API Mandaê...'):
                for _, row in df.iterrows():
                    pedido = row['pedido']
                    codigo = str(row['envio codigo']).strip()
                    if not codigo:
                        rastreios.append({"Pedido": pedido, "Código": codigo, "Status": "Código vazio"})
                        continue

                    status = buscar_status_mandae(codigo)
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
