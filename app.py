import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página
st.set_page_config(page_title="Dash - Plano de Ação das Filiais", layout="wide")
st.title("📊 Acompanhamento do Plano de Ação por Filial")

# 2. Função para carregar e tratar os dados
@st.cache_data
def carregar_dados():
    # Lê o arquivo tratando acentos e usando o separador correto
    df = pd.read_csv(r'C:\Users\RT\Desktop\plano\planilha.csv', skiprows=2, encoding='latin1', sep=';')
    
    # A primeira coluna fica sem nome por padrão, vamos renomeá-la para "Filial"
    df.rename(columns={'Unnamed: 0': 'Filial'}, inplace=True)
    
    # Remove linhas vazias e preenche os espaços em branco com 0
    df = df.dropna(subset=['Filial'])
    df = df.fillna(0)
    
    return df

df = carregar_dados()

# 3. Barra lateral com filtros
st.sidebar.header("Filtros")
filiais = df['Filial'].unique().tolist()
filiais_selecionadas = st.sidebar.multiselect(
    "Selecione as Filiais para visualizar:",
    options=filiais,
    default=filiais # Começa com todas selecionadas
)

# Filtra o dataframe com base na seleção
df_filtrado = df[df['Filial'].isin(filiais_selecionadas)]

# 4. Exibição da Tabela de Dados
st.subheader("Visão Geral do Preenchimento")
st.dataframe(df_filtrado, use_container_width=True)

# 5. Preparação dos dados para o gráfico (Transformando colunas em linhas para o Plotly)
df_melted = df_filtrado.melt(
    id_vars=['Filial'], 
    var_name='Etapa do Plano de Ação', 
    value_name='Status/Progresso'
)

# 6. Gráfico Interativo
st.subheader("Evolução por Etapa")
fig = px.bar(
    df_melted, 
    x='Filial', 
    y='Status/Progresso', 
    color='Etapa do Plano de Ação', 
    barmode='group',
    text_auto='.2f' # Mostra o valor em cima da barra
)

fig.update_layout(xaxis_title="Filial", yaxis_title="Status do Preenchimento")
st.plotly_chart(fig, use_container_width=True)