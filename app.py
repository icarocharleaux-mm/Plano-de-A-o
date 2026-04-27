import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

# 1. Configuração da página
st.set_page_config(page_title="Dash - Plano de Ação das Filiais", layout="wide")
st.title("📊 Acompanhamento do Plano de Ação por Filial")

# 2. Função turbinada sugerida para contornar o bloqueio de bot
@st.cache_data(ttl=600) # Atualiza a cada 10 minutos (600 segundos)
def carregar_dados():
    # URL do SharePoint corporativo com o ?download=1 no final
    url = "https://diaslog-my.sharepoint.com/:x:/g/personal/icaro_nascimento_mmdeliverytransportes_com_br/IQB2Q3wsfo_HRIQyu8lOeQCgAch4BvKQ7ZcvvTOdPHeQS0g?download=1"
    
    # "Disfarça" a requisição como se fosse um navegador Chrome no Windows
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    # Faz o download forçado
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status() # Vai acusar erro se ainda assim der 403 ou 401
    
    # Lê o Excel da memória usando BytesIO
    df = pd.read_excel(BytesIO(response.content), engine='openpyxl', skiprows=2)
    
    # --- Limpeza dos dados ---
    # Renomeando a primeira coluna para 'Filial' (caso ela venha sem nome)
    df.rename(columns={df.columns[0]: 'Filial'}, inplace=True)
    
    # Remove linhas onde a Filial está vazia e preenche o resto com 0
    df = df.dropna(subset=['Filial'])
    df = df.fillna(0)
    
    return df

try:
    df = carregar_dados()

    # 3. Barra lateral com filtros
    st.sidebar.header("Filtros")
    filiais = df['Filial'].unique().tolist()
    filiais_selecionadas = st.sidebar.multiselect(
        "Selecione as Filiais para visualizar:",
        options=filiais,
        default=filiais
    )

    df_filtrado = df[df['Filial'].isin(filiais_selecionadas)]

    # 4. Exibição da Tabela
    st.subheader("Visão Geral do Preenchimento")
    st.dataframe(df_filtrado, use_container_width=True)

    # 5. Gráfico
    df_melted = df_filtrado.melt(
        id_vars=['Filial'], 
        var_name='Etapa do Plano de Ação', 
        value_name='Status/Progresso'
    )

    st.subheader("Evolução por Etapa")
    fig = px.bar(
        df_melted, 
        x='Filial', 
        y='Status/Progresso', 
        color='Etapa do Plano de Ação', 
        barmode='group',
        text_auto='.2f'
    )
    
    fig.update_layout(xaxis_title="Filial", yaxis_title="Status do Preenchimento")
    st.plotly_chart(fig, use_container_width=True)

except requests.exceptions.HTTPError as err:
    st.error(f"Erro de HTTP: {err}")
    st.warning("O SharePoint da empresa exigiu autenticação de login (Cookies/Token), e apenas o 'disfarce' do navegador não foi suficiente. A alternativa mais rápida será usar o Google Sheets!")
except Exception as e:
    st.error(f"Ocorreu um erro: {e}")
