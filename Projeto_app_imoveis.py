# Projeto House rocket Iméveis ( empresa de compra e venda de imóveis ) 
# Python back-end and Streamlit front-end.  

# Import das bibliotecas usadas no projeto de compra e venda de imóveis 

# Análise e estatística modelos matemáticos
import numpy as np
# Mineracao da base e leituras
import pandas as pd
# Desenvolvimento do app web 
import streamlit as st 
# Plotagens de gráficos 
import plotly.express as px 
# Análise e estatíticas
import scipy.stats as stats
# Tratamento de imagens em geral 
from PIL import Image 
# Modeloso estatíticos com algebra linear 
from scipy.stats import skew, kurtosis
from streamlit_folium import folium_static 
import streamlit.components.v1 as components

# Configurações e parametrizaçõies necessárias para a criaçãio do app.python_streamlit for business 

# Configurações das imagens de logo e etc... 
st.set_page_config( 
                   page_icon='page_icon="🕮"',
                   layout='wide',
                  )

# Função para customização dos botões com css_html_styles, com o arquivo style.css na mesma pasta do projeto

with open(r'./style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)      

# Logo da sidebar 

# st.set_page_config(
#     page_title="Residential properties (Brazil)",
#     page_icon="🏢",
#     layout="centered",
#     initial_sidebar_state="collapsed",
# )

# logo = Image.open(
#                   ".//img//logo_sdb.png"
#                  )
logo = Image.open(
                  "./img/logo_sdb.png"
                 )
st.sidebar.image(logo,
		           caption="",
		           use_column_width=True)

# Carregando a logo e o nome da empresa 
logo = Image.open(
                  "./img/banner_st.png"
                 )
st.image(logo,
		   caption="",
		   use_column_width=True) 

# st.title(':sunglasses:')
st.markdown(
    "<h4 style='text-align: center; color:#2D3142;'>KC HOUSE INCORPORADORA E IMOBILIÁRIA</h4>", 
    unsafe_allow_html=True)
st.markdown(
    "<h6 style='text-align: center; color:#03045E;'<em>Imóveis para todos os estilos de vℹ️da <em></h6>", 
    unsafe_allow_html=True) 

# Função para ler a base de dados e função nativa do streamlit para limpar chache_resource 
@st.cache_resource 

def cache_data(path_in):
    data = pd.read_csv(path_in)         
          
# Aqui o placehoder vazio finalmente é atualizado com dados do filtered_df 
    info_sidebar = st.sidebar.empty()# placeholder, para informações filtradas que só serão carregadas depois
    info_sidebar.info("Registros:\t\t***{}***".format(data.shape[0])) 
                 
    return data  

st.sidebar.markdown('---')
st.sidebar.markdown(
    "<h4 style='text-align: center; color:darkpurple;'>MENU CONSULTAS </h4>", 
    unsafe_allow_html=True) 
     
st.markdown('---')

# Set Options format decimal for page rendering    
pd.set_option('display.float_format',lambda x: '%.2f' % x)   

 # Função para guarda-chuva para otiizar a base de dados e fazer alguns tratamentos no dataset raw.
 
 # Remoção de dados duplicados 
def duplicates(data):
    data = data.drop_duplicates(subset=['id'], keep = 'last') 
    data = data.drop(15870)
    
    return data 

# Função para tratamentos em especial datetime 
def get_tratamento(data):
    data['date']=pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')  
       
# Eliminando outliers em especial da coluna bedrooms 
    data=data[data['bedrooms'] != 33]
    
# Criando a feacture preço do valor_m²_imovel
    data['preco_m²']=data['price'] / (data['sqft_living'] * 0.093)  
    
# Separando ano com um nova feacture (ano) 
    data['ano'] = pd.to_datetime(data['date']).dt.strftime('%Y')
    
 # Criando a feacture frente para a água (lago/mar)
    data['frente_agua'] = 'NA'
    
    data['frente_agua'] = data['waterfront'].apply(lambda x: 'Waterfront' 
                                                          if x == 1 else
                                                        'No frente_agua')
    
# Criando a feacture que contem porão 

    data['com_porao'] = 'NA'
    
    data['com_porao'] = data['sqft_basement'].apply(lambda x: 'True' 
                                                       if x > 0 else
                                                            'False')
    
# Criando feacture mes month 
    
    data['mes'] = pd.to_datetime(data['date']).dt.strftime('%m') 

# Criando feacture temporado 
    
    data = data.copy()
    
    data['temporada'] = 'NA'
    
    data['temporada'] = data['mes'].apply(lambda x: 'primavera/verao' 
                                           if (x >= '03') & (x <='9') 
                                           else     'outono/inverno')
                                                                                                  
# Feactures recomendações de compra 

    dfzp = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()
    
    df2 = pd.merge(data, dfzp, on= 'zipcode', how='inner')
    df2.rename(columns={'price_x': 'price', 'price_y': 'median_price'}, inplace=True)
    
    df2['situacao'] = 'NA'
    
    for i in range(len(df2)):
        if (df2.loc[i, 'price'] > df2.loc[i, 'median_price']) &  (df2.loc[i, 'condition'] <=3) & (
                                                                 df2.loc[i, 'yr_renovated'] == 0): 
                                                                df2.loc[i, 'situacao'] = 'comprar'
        else:
            df2.loc[i, 'situacao'] = 'Não comprar' 

# Feacture recomenação para os preços de venda

    df2['venda_price'] = 'NA'
    
    for i in range(len(df2)): 
        
        if (df2.loc[i, 'temporada'] == 'primavera/verao') &  (df2.loc[i, 'situacao'] == 'comprar'):
                                              df2.loc[i, 'venda_price'] = df2.loc[i, 'price'] * 1.3
        elif (df2.loc[i, 'temporada'] == 'outono/inverno') & (df2.loc[i, 'situacao'] == 'comprar'):
                                              df2.loc[i, 'venda_price'] = df2.loc[i, 'price'] * 1.1
        else:
            df2.loc[i, 'venda_price'] = 0                                

# Criação da feactre lucro bruto

    df2['lucro_b'] = 'NA'

    for i in range(len(df2)):

        if df2.loc[i, 'venda_price'] > 0:
           df2.loc[i, 'lucro_b'] = df2.loc[i, 'venda_price'] - df2.loc[i, 'price']
        else:
            df2.loc[i, 'lucro_b'] = 0
            
    return data

# Criação de filtro com atritutos chave para análise e por preço dos imóveis.
     
def get_attributes_data(data):
                 
    st.sidebar.markdown(
    "<h4 style='text-align: center; color:darkpurple;'>FILTROS INTERATIVOS</h4>", 
    unsafe_allow_html=True)  
    
    st.sidebar.markdown('---') 
    
    
# Análise dados que serão trabalhados nas análises 
            
    if st.sidebar.button('***Clic***\t***Visualizar Dados*** ℹ️', use_container_width=False):
       st.write(data.head(5))  
       
    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>ANÁLISE DESCRITIVA DOS DADOS</h6>", 
    unsafe_allow_html=True)
                    
# Análise descritiva com describe: 

    descritiva = data[[ 'price', 'preco_m²', 'bedrooms','bathrooms','sqft_living', 
                      'sqft_lot', 'sqft_above', 'sqft_living15', 'sqft_lot15' ]].describe().drop(['count'])
    # st.write(describe)
    if st.sidebar.button('***Clic***\t***Análise descritiva*** ℹ️', use_container_width=False):
       st.write(descritiva.head(5))  
 
    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'> DADOS COM FILTRO POR ATRIBUTOS E LOCALIZAÇÃO </h6>", 
    unsafe_allow_html=True)      
           
# Criando lista de atributos para implentar filtros  

    f_filter = data[[ 'price', 'preco_m²', 'bedrooms','bathrooms','sqft_living', 
                      'sqft_lot', 'sqft_above', 'sqft_living15', 'sqft_lot15', 'zipcode']]

    f_attributes = st.sidebar.multiselect('Atritutos',f_filter.columns)                                                                                  
    f_zipcode    = st.sidebar.multiselect('Localização',f_filter['zipcode'].unique())  
    
    if ( f_zipcode != [] ) & ( 'zipcode' != [] ):
        data_f = data.loc[data['zipcode'].isin(f_zipcode), f_attributes]             
    elif ( f_zipcode != [] ) & ( 'zipcode' == [] ):
        data_f = data.loc[data[ 'zipcode'].isin(f_zipcode), :]             
    elif ( f_zipcode == [] ) & ( 'zipcode' != [] ):    
        data_f = data.loc[ :, f_attributes]      
    else:
        data_f = data.copy() 
    st.write(data_f.head()) # Gerando o filtro impresso
                
    return None 


# Criação métricas com base nos atributos do dataset para cenarização

def get_metricas(data):

   df1 = data[['id', 'zipcode']].groupby('zipcode').count().reset_index()
   df2 = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
   df3 = data[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
   df4 = data[['preco_m²', 'zipcode']].groupby('zipcode').mean().reset_index()
   
   gm1 = pd.merge(df1, df2, on='zipcode', how= 'inner' )   
   gm2 = pd.merge(gm1, df3, on='zipcode', how= 'inner' )
   gmd = pd.merge(gm2, df4, on='zipcode', how= 'inner' )

   gmd.columns = ['LOCALIZAÇÃO','TOTAL_IMOV','PREÇOS','ÁREA_ABERTA','PREÇO_M²']
   
  # Parâmetros de configuração de colunas quantidade 
   col1, col2 = st.columns(( 2 ))

   
# Criação de métricas de análise e estatística 

   attributes = data.select_dtypes(include=['int64','float64'] ) 
   attributes = attributes.iloc[:, 1: ]
   
   media   = pd.DataFrame( attributes.apply( np.mean ) )
   mediana = pd.DataFrame( attributes.apply( np.median ) ) 
   std     = pd.DataFrame( attributes.apply( np.std ) ) 
   min_    = pd.DataFrame( attributes.apply( np.min ) )
   max_    = pd.DataFrame( attributes.apply( np.max ) )
   skew    = pd.DataFrame( attributes.apply( lambda x:x.skew ()) ) 
   kurtosis  = pd.DataFrame( attributes.apply( lambda x:x.kurtosis ()) )
  
# Concatenando o DataFrame criado acima com as análises descritivas 

   dfm = pd.concat([min_, media, max_, mediana, std, skew, kurtosis],axis=1).reset_index() # Concate pelo eixo das colunas criando novo index
   
   dfm.columns = ['ATRIBUTOS', 'MÍNIMO', 'MÉDIA', 'MÁXIMO', 'MEDIANA', 'DESV.PADRÃO', 'SKEW', 'KURTOSIS'] 
   
   # Parâmetros de configuração de colunas quantidade 

   st.markdown(
   "<h6 style='text-align: center; color:#343A40;'>LOCALIZAÇÃO POR ZIPCODE E ANÁLISE ESTATÍSTICA DAS VARIÁVEIS</h6>", 
   unsafe_allow_html=True) 
   col1, col2 = st.columns(( 2 ))
   col1.dataframe( gmd ) 
   col2.dataframe( dfm )
     
   return None


# Criando função para gerar um mapa com a localização dos imóveis

def get_map(data):   
    houses = data[['id', 'price', 'lat', 'long']]
    map = px.scatter_mapbox(houses, 
                                   lat='lat', 
                                   lon='long',
                                   size='price',  
                                   color='price',
                                   color_continuous_scale=px.colors.cyclical.IceFire,
                                   size_max=15, 
                                   zoom=9.5) # Parametrizações de pletagem do mapa escolhido
    map.update_layout(mapbox_style='open-street-map') # Estilo do mapa usado
    map.update_layout(height=400, width=1000, margin={'r': 0, 'l': 0, 't': 0, 'b': 0}) # Cordenadas do mapa. 
    
    st.markdown(
   "<h6 style='text-align: center; color:#343A40;'>MAPA DE GEOPOSICIONAMENTO DOS IMÓVEIS POR ÁREAS</h6>", 
   unsafe_allow_html=True) 
    
    st.sidebar.markdown( 
                        "<h6 style='text-align: center; color:#343A40;'>Selecione Mapa</h6>", 
   unsafe_allow_html=True) 
       
    if st.sidebar.button('***Clic***\t***Visualizar Mapa*** ℹ️', disabled=False, use_container_width=True) is True:
       st.plotly_chart( map )

    return None

# Criando função para plotar gráficos 

def get_graficos( data ):

    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>CENARIZAÇÃO POR PREÇOS MÉDIOS DE COMPRA E MELHOR MÊS PARA VENDA </h6>", 
    unsafe_allow_html=True) 

    # grafico preço do imóvel por ano de construção
    min_yr_built = int( data['yr_built'].min() )
    max_yr_built = int( data['yr_built'].max() )
    
# Filtro por preços na sidebar  
   
    info_sidebar = st.sidebar.empty()
    price_filter = st.sidebar.slider('Preço',int(data.price.min()),
                                             int(data.price.max()))
    table = st.sidebar.empty()# placeholder, para informações filtradas que só serão carregadas depois,
# Quando a função preço mininmo e máximo forem chamada
 
# Filtros por ano de construção 
    
    st.sidebar.markdown(
    "<h4 style='text-align: center; color:darkpurple;'>FILTRO ANO CONSTRUÇÃO ℹ️ </h4>", 
    unsafe_allow_html=True) 
    f_yr_built = st.sidebar.slider( 'Ano', min_yr_built,
                                           max_yr_built,
                                           max_yr_built)
    
    df = data.loc[data['yr_built'] < f_yr_built]
    df = df[['yr_built', 'price']].groupby( 'yr_built' ).mean().reset_index() 
    
    fig1 = px.line( df, 'yr_built', 'price' )
        
    # Preço médio dos imóveis por dia de oferta

    df = data[['mes', 'price']].groupby( 'mes' ).mean().reset_index()
    fig2 = px.line( df, 'mes', 'price')
    
    col1, col2 = st.columns( 2 )
    col1.plotly_chart( fig1 ) 
    col2.plotly_chart( fig2 )
        
    st.markdown('---')
    
    # Preço médio dos imóveis por dia de oferta 
       
    # fig = yr_built = (data[['bedrooms', 'price']] ).groupby( 'bedrooms' ).mean().reset_index() 
    # st.bar_chart(yr_built)
    
    st.markdown(
    "<h6 style='text-align: center; color:darkpurple;'>CENARIZAÇÃO COM A MÉDIA DOS PREÇOS E QUANTIDADES DE QUARTOS </h6>", 
    unsafe_allow_html=True) 
    
    dfg = (data[['bedrooms', 'price']] ).groupby( 'bedrooms' ).mean().reset_index() 
    dfg = st.bar_chart(dfg, use_container_width=True) 
              
    return None 

# Criando função para cenarizações e análisar algumas hipóteses com plots ( gráficos ) 

def get_cenarizacoes( data ):

    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>CENARIZAÇÃO POR PREÇOS MÉDIOS DOS IMÓVEIS COM VISTA PARA A ÁGUA </h6>", 
    unsafe_allow_html=True)
    st.markdown(
    "<h8 style='text-align: center; color:#343A40;'>Se verdadeiro os imóveis com frente para a água, tem valorização em torno de 30%</h8>", 
    unsafe_allow_html=True)

    df = data[['frente_agua', 'price']].groupby('frente_agua').mean().reset_index()

    no_waterfront = df[df['frente_agua'] == 'No frente_agua']['price'].mean()
    waterfront    = df[df['frente_agua'] == 'Waterfront']['price'].mean()
    diferenca     = str(round(((100 / no_waterfront) * waterfront) - 100, 2)) + '%'

    df1 = {'no_waterfront': no_waterfront, 'waterfront': waterfront, 'preco_diferente': diferenca}
    df1 = pd.DataFrame([df1])
    st.dataframe( df1 )
    
    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>CENARIZAÇÃO POR ANO DE CONSTRUÇÃO</h6>", 
    unsafe_allow_html=True)
    st.markdown(
    "<h8 style='text-align: center; color:#343A40;'>Imóveis com ano de construção inferior a 1955, têm uma leve desvalorização</h8>", 
    unsafe_allow_html=True)

    acima_ano_55  = data[data['yr_built'] > 1955]['price'].mean()
    abaixo_ano_55 = data[data['yr_built'] <= 1955]['price'].mean()

    diferenca = str(round(((100 / acima_ano_55) * abaixo_ano_55) - 100, 2)) + '%'

    dffa = {'above_1955': acima_ano_55, 'below_1955': abaixo_ano_55, 'preco_diferente': diferenca}
    dffa = pd.DataFrame([dffa])
    st.dataframe( dffa )

# Imoveis com porao e área aberta menor, são mais caros ou mais baratos ( conceito aberto )

    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>CENARIZAÇÃO DOS IMÓVEIS EM CONCEITO ABERTO COM OU SEM PORÃO</h6>", 
    unsafe_allow_html=True)

    sem_porao = data[data['com_porao'] == 'False']['sqft_lot'].mean()
    com_porao = data[data['com_porao'] == 'True']['sqft_lot'].mean()
    diferenca = str(round((( 100 / com_porao) * sem_porao) - 100, 2 )) + '%'

    dffp = {'without_basement': sem_porao, 'with_basement': com_porao, 'sqft_lot_diference': diferenca}
    dffp = pd.DataFrame([dffp])
    st.dataframe( dffp )

# Valorização dos imóvei ao longo dos anos em termos de crescimento 

    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>CENARIZAÇÃO COM INDICADOR DE CRESCIMENTO DO IMÓVEIS ANO APÓS ANO</h6>", 
    unsafe_allow_html=True)

    df = data[['ano', 'price']].groupby('ano').mean().reset_index()
    df['ano'] = df['ano'].astype('int64')

    year_2014 = df[df['ano'] == 2014]['price'][0]
    year_2015 = df[df['ano'] == 2015]['price'][1]
    diferenca = str(round(((100 / year_2014) * year_2015) - 100, 2)) + '%'

    df1 = {'year_2014': year_2014, 'year_2015': year_2015, 'preco_diferente': diferenca}
    df1 = pd.DataFrame([df1])

    st.dataframe( df1 )

# Cenarização dos imóveis por ano de reformas

    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>CENARIZAÇÃO COM ANÁLISE DOS IMÓVEIS POR ANO DE REFORMAS</h6>", 
    unsafe_allow_html=True) 
    
    im3b  = data[(data['bathrooms'] == 3) & (data['yr_renovated'] > 0)]['price'].mean()
    im3bb = data[(data['bathrooms'] != 3) & (data['yr_renovated'] != 0)]['price'].mean()

    diferenca = str(round(((100 / im3bb ) * im3b) - 100, 2 )) + '%'

    df = {'no_revovated': im3bb, 'yes_renovated': im3b, 'preco_diferente': diferenca}
    df = pd.DataFrame([df])
    st.dataframe( df )
    
# Cenarização dos imóveis com maior número de quartos e sua valorização 
    
    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>CENARIZAÇÃO COM RECOMENDAÇÕES DE COMPRA E VENDA BASE TABELA</h6>", 
    unsafe_allow_html=True) 

    return None

# Criando função para gerar recomendações de compra e venda

def get_recomendacoes( data ):
    # st.title( '' )

    # Recomendações de compra
    
    df = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()

    df2 = pd.merge(data, df, on='zipcode', how='inner')
    df2.rename(columns={'price_x': 'price', 'price_y': 'median_price'}, inplace=True)

    df2['situacao'] = 'NA'

    for i in range(len(df2)):
        if (df2.loc[i, 'price'] < df2.loc[i, 'median_price']) & (df2.loc[i, 'condition'] >= 3) & (
                                                                  df2.loc[i, 'yr_renovated'] == 0):
                                                                 df2.loc[i, 'situacao'] = 'comprar'

        else:
            df2.loc[i, 'situacao'] = 'nao comprar'

    # Recomendações do preço de venda
    
    df2['venda_price'] = 'NA'

    for i in range(len(df2)):
        if (df2.loc[i, 'temporada'] == 'verao/primavera') & (df2.loc[i, 'situacao'] == 'comprar'):
                                             df2.loc[i, 'venda_price'] = df2.loc[i, 'price'] * 1.3
        elif (df2.loc[i, 'temporada'] == 'outono/inverno') & (df2.loc[i, 'situacao'] == 'comprar'):
                                             df2.loc[i, 'venda_price'] = df2.loc[i, 'price'] * 1.1
        else:
            df2.loc[i, 'venda_price'] = 0

    c1, c2 = st.columns( 2 )
    c1.dataframe(df2[['id', 'zipcode', 'condition', 'yr_renovated', 'price', 'median_price', 'situacao']])
    c2.dataframe( df2.loc[df2['venda_price'] > 0][['id', 'zipcode', 'price', 'median_price', 'situacao', 'venda_price']] )
          
# Cenarização do lucro bruto da kc house imóveis 
   
    df2['lucro_b'] = 'NA'

    for i in range( len( df2 ) ):

        if df2.loc[i, 'venda_price'] > 0:
            df2.loc[i, 'lucro_b'] = df2.loc[i, 'venda_price'] - df2.loc[i, 'price']

        else:
            df2.loc[i, 'lucro_b'] = 0

    df2['lucro_b'] = df2['lucro_b'].astype('int64')

    df3 = df2[df2['lucro_b'] > 0]
    df3 = df3[['zipcode', 'lucro_b']].groupby('zipcode').mean().reset_index()

    st.markdown(
    "<h6 style='text-align: center; color:#343A40;'>LUCRO MÉDIO POR LOCALIZAÇÃO DOS IMÓVEIS</h6>", 
    unsafe_allow_html=True)   
    st.dataframe( df3 )
       
    return data 


# Path da base de dados 
# Importação da base de dados 

if __name__ == "__main__": 
       
    path_in = (r'./base/kc_house_data.csv')
    data = cache_data( path_in )
    
    
# Parametros de chamada das funções 
    
    data = get_tratamento( data )
    get_attributes_data(data)
    get_metricas( data )
    get_map( data )
    get_graficos( data )
    get_cenarizacoes( data )
    get_recomendacoes( data ) 

# Finalização do projeto, com a função python running do projeto 

def run():
    if __name__ == '__main__':
        cache_data.run(data)    
    return True     

st.markdown('---')
st.markdown('***Claudio Fabian***') 

st.write("Acesso pelo LinkedIn: "
                         "[LinkedIn](https://www.linkedin.com/in/claudio-fabian-stychnicki-28a17155/)")

st.write("Acesso pelo GibHub:"
                         "[Github](https://github.com/fabian-gib-50?tab=repositories)")

# link = '[LinkedIn](linkedin.com/in/claudio-fabian-stychnicki-28a17155)'
# st.markdown(link, unsafe_allow_html=True)
st.markdown('---')
# --- (End of the App)