import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import os

def main():
    st.title("Herbarium MS 5.1")
    
        # Adicionar uma imagem
    st.image("logo.png", caption="Uma poderosa ferramenta na identificação de amostras desconhecidas", use_column_width=True)
    
    # Adicionar instruções e informações
    st.write("## Instruções Gerais")
    st.write(
        """
        Bem-vindo ao aplicativo Herbarium MS 5.0, um aplicativo de busca de similaridade química entre amostras desconhecidas e amostras autênticas de herbários. 
       
        **Como usar:**
        1. Faça download do arquivo Excel "Preparação Herbarium MS" e siga os passos descritos na planilha "apresentação".
        2. Após o preparo dos dados, salve o arquivo como "Pasta de trabalho do Excel" ou formato ".xlsx".
        3. Carregue seu arquivo Excel na área indicada "Drag and drop file here".
        4. O aplicativo calculará a similaridade química entre sua amostra desconhecida e amostras de exsicatas contidas no banco de dados.
        4. Os resultados, incluindo as amostras mais semelhantes e seus metadados, serão exibidos na tela.

        **Exemplos:**
        Use os links abaixo para baixar arquivos de exemplo e testar a ferramenta.
        
        """
    )

    # Adicionar uma coluna para colocar os botões de download
    col1, col2, col3 = st.columns([1, 2, 1])

    # Posicionar os botões no centro usando a coluna do meio
    with col2:
        st.subheader("Arquivos de Exemplo")
    
    with col1:
        st.subheader(" ")
        st.download_button(
            label="Baixar Exemplo 1",
            data=open("Exemplo_U_guatterioides.xlsx", "rb"),
            file_name="Exemplo_U_guatterioides.xlsx"
        )
        st.download_button(
            label="Baixar Exemplo 2",
            data=open("Exemplo_U_rufescens.xlsx", "rb"),
            file_name="Exemplo_U_rufescens.xlsx"
        )
        st.download_button(
            label="Baixar Exemplo 3",
            data=open("Exemplo_U_floribunda.xlsx", "rb"),
            file_name="Exemplo_U_floribunda.xlsx"
        )
        st.download_button(
            label="Baixar Exemplo 4",
            data=open("Exemplo_U_duckei.xlsx", "rb"),
            file_name="Exemplo_U_duckei.xlsx"
        )
        st.download_button(
            label="Baixar Exemplo 5",
            data=open("Exemplo_U_stipitata.xlsx", "rb"),
            file_name="Exemplo_U_stipitata.xlsx"
        )


    # Caminho do arquivo Excel com as planilhas do banco de dados
    banco_de_dados_path = 'banco_de_dados.xlsx'
    
    # Verificar se o arquivo de banco de dados existe
    if not os.path.exists(banco_de_dados_path):
        st.error(f"O arquivo {banco_de_dados_path} não foi encontrado. Verifique se o arquivo está na pasta do aplicativo.")
        return

    # Ler o banco de dados
    dados_ajust = pd.read_excel(banco_de_dados_path, sheet_name='herbario_massas', index_col=0)
    dados_amostras = pd.read_excel(banco_de_dados_path, sheet_name='herbario_metadados', index_col=0)
    
    # Carregar a amostra desconhecida através do upload
    amostra_file = st.file_uploader("Escolha o arquivo Excel da amostra desconhecida", type="xlsx")

    if amostra_file is not None:
        # Ler a amostra desconhecida
        amostra_desconhecida = pd.read_excel(amostra_file, sheet_name='amostra_desconhecida', index_col=0)

        # Preencher valores ausentes com 0
        dados_ajust = dados_ajust.fillna(0)
        amostra_desconhecida = amostra_desconhecida.fillna(0)

        # Calcular a similaridade de cosseno
        similarities = cosine_similarity(amostra_desconhecida, dados_ajust)

        # Converter a matriz de similaridade para um DataFrame
        similarity_df = pd.DataFrame(similarities, index=amostra_desconhecida.index, columns=dados_ajust.index)

        # Ordenar as similaridades em ordem decrescente para cada amostra desconhecida
        sorted_similarity_df = similarity_df.apply(lambda row: row.sort_values(ascending=False), axis=1)

        # Extrair os metadados das 3 amostras mais semelhantes
        metadados_columns = ['Espécie', 'Gênero', 'Família', 'Herbário', 'Exsicata', 'Data coleta']
        dados_amostras = dados_amostras[metadados_columns]

        # Função para obter os 3 melhores metadados
        def get_top_metadata(similarity_row, top_n=3):
            top_samples = similarity_row.head(top_n).index
            return dados_amostras.loc[top_samples]

        # Adicionar metadados à matriz de similaridade ordenada
        metadata_df = pd.DataFrame()
        for amostra in sorted_similarity_df.index:
            top_metadata = get_top_metadata(sorted_similarity_df.loc[amostra])
            top_metadata = top_metadata.reset_index().rename(columns={'index': 'codigo'})
            
            # Garantir que 'top_metadata' tenha exatamente 3 linhas
            top_metadata = top_metadata.head(3)
            
            # Extraindo similaridades
            top_similarities = sorted_similarity_df.loc[amostra].head(3).values
            
            # Certificar que top_similarities tenha exatamente 3 valores
            if len(top_similarities) < 3:
                top_similarities = list(top_similarities) + [0] * (3 - len(top_similarities))
            
            # Garantir que 'similaridade' tenha a mesma quantidade de linhas que 'top_metadata'
            if len(top_metadata) > len(top_similarities):
                top_similarities += [0] * (len(top_metadata) - len(top_similarities))
            
            top_metadata['similaridade'] = top_similarities[:len(top_metadata)]
            
            metadata_df = pd.concat([metadata_df, top_metadata], axis=0)

        # Mostrar o DataFrame com similaridade e metadados
        st.write(metadata_df)

if __name__ == "__main__":
    main()
