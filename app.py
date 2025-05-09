import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Token da Mandaê (pode esconder isso num arquivo .env se quiser depois)
API_TOKEN = "cd8c9ce94d3c9f9fb6b8ee77c9e8b681"
API_URL = "https://api.mandae.com.br/v2/tracking/"

# Função para consultar a API da Mandaê
def consultar_status(codigo):
    headers = {"Authorization": f"Token {API_TOKEN}"}
    try:
        response = requests.get(f"{API_URL}{codigo}", headers=headers, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            status = dados.get("status", "Indefinido")
            ultima_atualizacao = dados.get("updated_at", "")
            return status, ultima_atualizacao
        else:
            return f"Erro {response.status_code}", ""
    except Exception as e:
        return "Erro na conexão", ""

# Título da página
st.title("Rastreamento de Pedidos - Mandaê")

# Upload de arquivo
arquivo = st.file_uploader("Faça upload da planilha (.csv)", type=["csv"])

if arquivo is not None:
    # Leitura do CSV
    df = pd.read_csv(arquivo)

    if 'Pedido' not in df.columns or 'Envio codigo' not in df.columns:
        st.error("A planilha precisa conter as colunas: 'Pedido' e 'Envio codigo'")
    else:
        st.success("Planilha carregada com sucesso!")
        resultados = []

        with st.spinner("Consultando status dos pedidos..."):
            for _, row in df.iterrows():
                pedido = row['Pedido']
                codigo = str(row['Envio codigo']).strip()
                status, ultima_data = consultar_status(codigo)
                resultados.append({
                    "Pedido": pedido,
                    "Código de Rastreio": codigo,
                    "Status": status,
                    "Última Atualização": ultima_data
                })

        # Criar DataFrame com os resultados
        resultado_df = pd.DataFrame(resultados)
        st.dataframe(resultado_df)

        # Download do arquivo final
        csv = resultado_df.to_csv(index=False)
        st.download_button(
            label="📥 Baixar resultado em CSV",
            data=csv,
            file_name="rastreio_mandae.csv",
            mime="text/csv"
        )
