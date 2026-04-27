import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página
st.set_page_config(page_title="Dash - Plano de Ação das Filiais", layout="wide")
st.title("📊 Acompanhamento do Plano de Ação por Filial")

# 2. Função para carregar e tratar os dados
# ttl=60 significa que o cache dura 60 segundos. Depois disso, ele busca dados novos!
@st.cache_data(ttl=60) 
def carregar_dados():
    # Substitua a URL abaixo pelo link gerado no passo a passo (o que tem a palavra 'download' no meio)
    url = "https://diaslog-my.sharepoint.com/:x:/g/personal/icaro_nascimento_mmdeliverytransportes_com_br/IQB2Q3wsfo_HRIQyu8lOeQCgAch4BvKQ7ZcvvTOdPHeQS0g?download=1"
    
    # Lendo o arquivo Excel (.xlsx) diretamente da nuvem
    df = pd.read_excel(url, skiprows=2)
    
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

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.info("Verifique se o link da planilha é de download direto e público.")
