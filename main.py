import requests
import json
import pandas as pd

def analisar_anuncio_ia(titulo, descricao,model="gemma4:e2b"):
    url = "http://localhost:11434/api/generate"
    
    # O "System Prompt" vai dentro do prompt principal no Ollama
    prompt = f"""
    Contexto: Você é um assistente técnico de compras.
    Entrada: 
    - Moto: {titulo}
    - Descrição: \"\"\"{descricao}\"\"\"

    Tarefa: 
    1. SINISTRADA: Analise se a descrição confirma leilão/sinistro/pequena monta/media monta/furto/roubo. (Ignore frases como "não é leilão").
    2. opiniao_curta: Resumo do achado referente a informação de Sinistrada ou resumo util da descrição sobre dono e detalhes

    Responda APENAS o JSON:
    {{
        "sinistrada": boolean,
        "opiniao_curta": "string curta explicando o porquê"
    }}
"""
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
        "temperature": 0
        }
    }

    try:
        response = requests.post(url, json=payload)
        return response.json()['response']
    except Exception as e:
        return f"Erro: {e}"

# Teste para ver o JSON nascendo:
if __name__ == "__main__":
    #Configuração de validação de boa compra:
    pct_viabilidade_n_sinistrada = 5.0
    pct_viabilidade_sinistrada = 10.0

    #Por o volume ser baixo, o Pandas vai suprir, caso fosse 100 mil linhas ai seria necessário o PySpark
    with open('json/bronze_motos_com_descricao.json', 'r', encoding='utf-8') as f:
        df_motos = pd.DataFrame(json.load(f))

    with open('json/fipe_vx300.json', 'r', encoding='utf-8') as f:
        df_fipe = pd.DataFrame(json.load(f))

    #Aqui vamos começar a brincadeira
    #Precisamos montar um DF Silver com 3 informações:
    # Ano moto = ano fipe
    # Versao moto = versao fipe
    # Valor fipe baseado nas 2 infos acima
    df_silver = pd.merge(df_motos,
                         df_fipe,
                         on=['ano','versao'],
                         how='left')
    
    # No seu DataFrame de análise
    df_silver['diferenca_valor'] = df_silver['preco_fipe'] - df_silver['preco']
    df_silver['percentual_diff'] = (df_silver['diferenca_valor'] / df_silver['preco_fipe']) * 100


    for row in df_silver.itertuples(index=True):
        print(f"""
                Analisando {row.titulo}
                ano: {row.ano}
                Versão: {row.versao}
                Preço: {row.preco}
                FIPE: {row.preco_fipe}
                Diferença de valor = {row.diferenca_valor:.2f}
                Percentual = {row.percentual_diff:.2f}
                """)
        analise_ia_json = analisar_anuncio_ia(titulo=row.titulo,
                                              descricao=row.descricao)

        print(analise_ia_json)
        json_retorno = json.loads(analise_ia_json)
        if json_retorno['opiniao_curta']:
            df_silver.at[row.Index, 'sinistrada'] = json_retorno['sinistrada']

        valor_atrativo = False
        #Aqui vamos ver a questão de sinistro e calcular viabilidade
        if df_silver.at[row.Index, 'sinistrada'] == True:
            #Aqui precisa ser um valor mais em conta
            if row.percentual_diff > pct_viabilidade_sinistrada:
                valor_atrativo = True
        else:
            if row.percentual_diff > pct_viabilidade_n_sinistrada:
                valor_atrativo = True
        
        #Escreve no Dataframe:
        df_silver.at[row.Index, 'valor_atrativo'] = valor_atrativo
        
            

        print(f"{30*'='}")

    # df_silver.to_json('json/silver_motos_avaliadas.json', 
                #   orient='records', 
                #   force_ascii=False)
    
    dados = df_silver.to_dict(orient="records")
    #Salvando o Json de formato mais legível por pura estética de leitura
    with open('json/silver_motos_avaliadas.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    # print(resultado)

    #Cria a DF Gold, mas ainda sem o filtro
    colunas_gold = [
    'titulo', 'versao', 'ano', 'km', 'preco', 
    'preco_fipe', 'diferenca_valor', 'percentual_diff', 
    'sinistrada', 'valor_atrativo', 'link'
    ]
    df_gold = df_silver[colunas_gold].copy()
    
    #Gerando o JSON Gold com os resultados atrativos
    df_gold = df_gold[df_gold['valor_atrativo'] == True].reset_index(drop=True)
    dados_gold = df_gold.to_dict(orient="records")
    with open('json/gold_motos_atrativas.json', 'w', encoding='utf-8') as f:
        json.dump(dados_gold, f, ensure_ascii=False, indent=4)
    
