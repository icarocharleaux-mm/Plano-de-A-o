import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

# 1. Configuração da página
st.set_page_config(page_title="Dash - Plano de Ação das Filiais", layout="wide")
st.title("📊 Acompanhamento do Plano de Ação por Filial")

# 2. Função para carregar e tratar os dados
@st.cache_data(ttl=600)
def carregar_dados():
    url = "https://diaslog-my.sharepoint.com/:x:/g/personal/icaro_nascimento_mmdeliverytransportes_com_br/IQB2Q3wsfo_HRIQyu8lOeQCgAch4BvKQ7ZcvvTOdPHeQS0g?download=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()
    
    # Lê o Excel pulando as 2 linhas de título
    df = pd.read_excel(BytesIO(response.content), engine='openpyxl', skiprows=2)
    
    # Renomeia a primeira coluna para 'Filial'
    df.rename(columns={df.columns[0]: 'Filial'}, inplace=True)
    
    # Limpa linhas vazias e preenche nulos com 0
    df = df.dropna(subset=['Filial'])
    df = df.fillna(0)
    
    # Garante que as colunas numéricas sejam tratadas como decimais (ex: 1.0, 0.05)
    # Se o Excel trouxer "90%" como texto, isso converte para 0.9
    for col in df.columns[1:]:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('%', '').astype(float)
            # Se o número for maior que 1 (ex: 90), divide por 100
            df.loc[df[col] > 1, col] = df[col] / 100
            
    return df

try:
    df = carregar_dados()

    # 3. Filtros
    st.sidebar.header("Filtros")
    filiais = df['Filial'].unique().tolist()
    filiais_selecionadas = st.sidebar.multiselect(
        "Selecione as Filiais:",
        options=filiais,
        default=filiais
    )

    df_filtrado = df[df['Filial'].isin(filiais_selecionadas)]

    # ---------------------------------------------------------
    # NOVO BLOCO: Indicadores de Topo (Resumo Estratégico)
    # ---------------------------------------------------------
    st.subheader("Resumo Estratégico - Marco Zero")
    
    if not df_filtrado.empty:
        # Pega apenas as colunas com as etapas do plano (exclui a coluna 'Filial')
        cols_metricas = [col for col in df_filtrado.columns if col != 'Filial']
        
        # 1. Média Geral do Plano de Ação
        media_geral = df_filtrado[cols_metricas].mean().mean()
        
        # 2. Filial Destaque (Calcula a média de cada filial e pega a maior)
        medias_por_filial = df_filtrado.set_index('Filial')[cols_metricas].mean(axis=1)
        filial_destaque = medias_por_filial.idxmax()
        valor_destaque = medias_por_filial.max()
        
        # 3. Etapa Crítica (Calcula a média de cada etapa e pega a menor)
        medias_por_etapa = df_filtrado[cols_metricas].mean()
        etapa_critica = medias_por_etapa.idxmin()
        valor_critico = medias_por_etapa.min()
        
        # Cria 3 colunas para colocar os cartões lado a lado
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Média Geral de Implantação", value=f"{media_geral:.1%}")
            
        with col2:
            st.metric(label=f"🏆 Liderando: {filial_destaque}", value=f"{valor_destaque:.1%}")
            
        with col3:
            st.metric(label=f"⚠️ Foco: {etapa_critica}", value=f"{valor_critico:.1%}")
            
    else:
        st.warning("Selecione pelo menos uma filial na barra lateral para ver os indicadores.")
        
    st.divider() # Adiciona uma linha de separação elegante antes da tabela
    # ---------------------------------------------------------

    # 4. Exibição da Tabela com Formatação de Porcentagem
    st.subheader("Visão Geral do Preenchimento")
    
    # Criamos um dicionário de formatação para todas as colunas exceto 'Filial'
    formato_pct = {col: "{:.1%}" for col in df_filtrado.columns if col != 'Filial'}
    
    st.dataframe(
        df_filtrado.style.format(formato_pct),
        use_container_width=True
    )

    # 5. Gráfico com Rótulos em Porcentagem
    df_melted = df_filtrado.melt(
        id_vars=['Filial'], 
        var_name='Etapa do Plano de Ação', 
        value_name='Status'
    )

    st.subheader("Evolução por Etapa")
    fig = px.bar(
        df_melted, 
        x='Filial', 
        y='Status', 
        color='Etapa do Plano de Ação', 
        barmode='group',
        text_auto='.1%' # Mostra a porcentagem em cima da barra (ex: 90.0%)
    )
    
    # Ajusta o eixo Y para mostrar porcentagem e define o limite em 100% (1.0)
    fig.update_layout(
        yaxis_tickformat='.0%',
        yaxis_title="Progresso (%)",
        xaxis_title="Filial",
        yaxis=dict(range=[0, 1.1]) # Vai até 110% para o rótulo não cortar
    )
    
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
