import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Dash - Plano de Ação das Filiais", layout="wide")
st.title("📊 Acompanhamento do Plano de Ação por Filial")

# 2. Função turbinada com carimbo de tempo
@st.cache_data(ttl=600)
def carregar_dados():
    url = "https://diaslog-my.sharepoint.com/:x:/g/personal/icaro_nascimento_mmdeliverytransportes_com_br/IQB2Q3wsfo_HRIQyu8lOeQCgAch4BvKQ7ZcvvTOdPHeQS0g?download=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()
    
    df = pd.read_excel(BytesIO(response.content), engine='openpyxl', skiprows=2)
    
    # Tratamento e Limpeza
    df.rename(columns={df.columns[0]: 'Filial'}, inplace=True)
    df = df.dropna(subset=['Filial'])
    df = df.fillna(0)
    
    # Conversão para Porcentagem
    for col in df.columns[1:]:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('%', '').astype(float)
            df.loc[df[col] > 1, col] = df[col] / 100
    
    # Captura o momento exato da atualização
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    return df, timestamp

try:
    # Agora a função retorna dois valores: o dataframe e o horário
    df, ultima_atualizacao = carregar_dados()

    # 3. Barra lateral
    st.sidebar.header("Configurações")
    
    # Exibição do Feedback de Atualização na barra lateral
    st.sidebar.info(f"🕒 **Última sincronização:**\n{ultima_atualizacao}")
    
    filiais = df['Filial'].unique().tolist()
    filiais_selecionadas = st.sidebar.multiselect(
        "Selecione as Filiais:",
        options=filiais,
        default=filiais
    )

    df_filtrado = df[df['Filial'].isin(filiais_selecionadas)]

    # 4. Indicadores de Topo (Cards de BI)
    if not df_filtrado.empty:
        cols_metricas = [col for col in df_filtrado.columns if col != 'Filial']
        
        media_geral = df_filtrado[cols_metricas].mean().mean()
        
        medias_por_filial = df_filtrado.set_index('Filial')[cols_metricas].mean(axis=1)
        filial_destaque = medias_por_filial.idxmax()
        valor_destaque = medias_por_filial.max()
        
        medias_por_etapa = df_filtrado[cols_metricas].mean()
        etapa_critica = medias_por_etapa.idxmin()
        valor_critico = medias_por_etapa.min()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Média de Implantação", f"{media_geral:.1%}")
        c2.metric(f"🏆 Liderando: {filial_destaque}", f"{valor_destaque:.1%}")
        c3.metric(f"⚠️ Foco: {etapa_critica}", f"{valor_critico:.1%}")
        
        st.divider()

        # 5. Tabela Formatada
        st.subheader("Visão Geral do Preenchimento")
        formato_pct = {col: "{:.1%}" for col in df_filtrado.columns if col != 'Filial'}
        st.dataframe(df_filtrado.style.format(formato_pct), use_container_width=True)

        # 6. Gráfico
        df_melted = df_filtrado.melt(id_vars=['Filial'], var_name='Etapa', value_name='Status')
        
        st.subheader("Evolução por Etapa")
        fig = px.bar(
            df_melted, x='Filial', y='Status', color='Etapa', 
            barmode='group', text_auto='.1%'
        )
        fig.update_layout(yaxis_tickformat='.0%', yaxis_title="Progresso (%)", yaxis=dict(range=[0, 1.1]))
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
