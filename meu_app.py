import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configurando a pagina para full scren
st.set_page_config(layout = 'wide', page_title = 'Dashboards de Vendas')


# Criando as Funções
def formata_numero(valor, prefixo = ''):
    for unidade in ['' , 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000

    return f'{prefixo} {valor:.2f} milhões'



# Inserindo Titulo na Pagina
st.title('DASBOARD DE VENDAS :shopping_trolley:')


# Buscandos dados via API
url = 'https://labdados.com/produtos'

###### Definindo os filtros na aba lateral
regioes = ['Brasil', 'Centro Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''




todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)


query_string = {'regiao' : regiao.lower(), 'ano' : ano}

response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')


filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]



############################################### TABELAS

###### RECEITAS

# Receita por Estados
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Receita Mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

# Receita por Categoria de Produtos
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)


###### QUANTIDADE DE VENDAS

# Vendas por Estados
vendas_estado = dados.groupby('Local da compra').size().reset_index(name = 'Quantidade de vendas')
vendas_estado = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estado, on = 'Local da compra').sort_values('Quantidade de vendas', ascending = False)

# Vendas Mensal
vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M')).size().reset_index(name = 'Quantidade de vendas')
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()

# Vendas por Categoria de Produtos
vendas_categorias = dados.groupby('Categoria do Produto').size().reset_index(name = 'Quantidade de vendas')


###### VENDEDORES

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))




############################################### GRÁFICOS

###### RECEITAS

# Receita por Estados - Mapa
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat' : False, 'lon' : False},
                                  title = 'Receita por estado')


# Receita por Estados - Barras
fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')


# Receita Mensal - Linhas
fig_receita_mensal = px.line(receita_mensal,
                            x = 'Mês',
                            y = 'Preço',
                            markers = True,
                            range_y = (0, receita_mensal.max()),
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')


# Receita por Categoria de Produtos - Barras
fig_receita_categorias = px.bar(receita_categorias,
                               text_auto = True,
                               title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')


###### QUANTIDADE DE VENDAS

# Vendas por Estados - Mapa
fig_mapa_vendas = px.scatter_geo(vendas_estado,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Quantidade de vendas',
                                 template = 'seaborn',
                                 hover_name = 'Local da compra',
                                 hover_data = {'lat' : False, 'lon' : False},
                                 title = 'Vendas por Estado')


# Vendas por Estados - Barras
fig_vendas_estado = px.bar(vendas_estado.head(),
                               x = 'Local da compra',
                               y = 'Quantidade de vendas',
                               text_auto = True,
                               title = 'Top estados (quantidade de vendas)')


# Vendas Mensal - Linhas
fig_vendas_mensal = px.line(vendas_mensal,
                           x = 'Mês',
                           y = 'Quantidade de vendas',
                           markers = True,
                           range_y = (0, vendas_mensal.max()),
                           color = 'Ano',
                           line_dash = 'Ano',
                           title = 'Quantidade de vendas mensal')


# Vendas por Categoria de Produtos - Barras
fig_vendas_categoria = px.bar(vendas_categorias,
                              x  = 'Categoria do Produto',
                              y = 'Quantidade de vendas',
                              text_auto = True,
                              title = 'Vendas por categoria')


############################################### VISUALIZAÇÃO NO STREAMLIT

###### Criação das Abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])


# Aba 1
with aba1:
    # Criação das colunas
    col1, col2 = st.columns(2)
    # Exibindo as Métricas e graficos nas colunas
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
        
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

# Aba 2
with aba2:
    # Criação das colunas
    col1, col2 = st.columns(2)
    # Exibindo as Métricas e gráficos nas colunas
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estado, use_container_width = True)
        
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categoria, use_container_width = True)

# Aba 3
with aba3:
    # Criação do input para escolhar da quantidade de vendedores
    quantidade_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    # Criação das colunas
    col1, col2 = st.columns(2)
    # Exibindo as Métricas e gráficos nas colunas
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(quantidade_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(quantidade_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {quantidade_vendedores} vendedores (receita)')
        fig_receita_vendedores.update_layout(yaxis_title = 'Vendedor', xaxis_title = 'Receita')


        
        st.plotly_chart(fig_receita_vendedores, use_container_width = True)
    
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))

        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(quantidade_vendedores),
                                     x = 'count',
                                     y = vendedores[['count']].sort_values('count', ascending = False).head(quantidade_vendedores).index,
                                     text_auto = True,
                                     title = f'Top {quantidade_vendedores} vendedores (quantidade vendas)')
        fig_vendas_vendedores.update_layout(yaxis_title = 'Vendedor', xaxis_title = 'Quantidade de vendas')

        st.plotly_chart(fig_vendas_vendedores, use_container_width = True)










