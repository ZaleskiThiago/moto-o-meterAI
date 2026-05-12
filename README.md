# 🏍️ Moto-o-Meter AI: Inteligência Artificial na Análise de Mercado (Versys-X 300)

O Moto-o-Meter AI é um pipeline de Engenharia de Dados de ponta a ponta que utiliza LLMs (Large Language Models) locais para identificar as melhores oportunidades de compra da Kawasaki Versys-X 300. O projeto transforma anúncios brutos em insights financeiros, detectando automaticamente sinistros e avaliando o custo-benefício real.

## 🏗️ Arquitetura do Projeto (Medallion AI Architecture)

O projeto segue os princípios de um Data Lakehouse, agora integrado com uma camada de inferência de IA:

- Bronze (Raw): Dados brutos extraídos via Web Scraping (Playwright) de portais como Mercado Livre
- Silver (AI Enriched): Processamento via Pandas para limpeza, deduplicação e o JOIN com a Tabela Fipe baseado em Ano e Versão (STD vs TR) com Inferência local usando Ollama + Gemma 4. A IA analisa a descrição para detectar sinistros (leilão/furto);
- Gold : Como I.A não é muito boa em calculo mas sim predicção, a validação se o preço é realmente atrativo é feito com o resultado do enriquecimento da I.A com os parametros definidos de métrica (Sinistrada valor acima de 10% abaixo, enquanto não sinistrada com valor 5% abaixo);

## 🧠 O "Cérebro" do Projeto: Gemma 4 + Ollama

Diferente de modelos tradicionais de busca por palavras-chave, este pipeline utiliza o Gemma 4 com temperature: 0 para garantir:

- **Detecção de Contexto**: Diferencia "Moto de leilão" (Sinistrada) de "Não é de leilão" (Falso Positivo).
- **Resumo da Descrição:** Analisa se acessórios (baús, protetores) justificam um preço acima da Fipe.
- **Extração Estruturada:** Retorna os insights diretamente em JSON para integração imediata no pipeline.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** [Python 3.10+](https://www.python.org/) 🐍❤ (no meu caso com o [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main))
- **LLM Engine:** [Ollama](https://ollama.com/) (Rodando [Gemma 4](https://deepmind.google/models/gemma/gemma-4/))
- **Análise de Dados:** [Pandas ](https://pandas.pydata.org/)& [NumPy](https://numpy.org/)
- **Web Scraping:** [Playwright ](https://playwright.dev/python/docs/intro)(com bypass de automação)
- **Ambiente:** [WSL2 no Windows](https://learn.microsoft.com/pt-br/windows/wsl/install) ou Linux Nativo com suporte ao processamento usando o [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## 📊 Estrutura de Dados (Camada Gold)

O output final entrega um Json pronto para decisão:

| Chave           | Valor             | Formato |
| --------------- | ----------------- | ------- |
| titulo          | Kawasaki Versys-x | String  |
| versao          | "TR" ou "STD"     | String  |
| ano             | 2022              | Integer |
| km              | 17.861            | Float   |
| preco           | 26999.0           | Float   |
| preco_fipe      | 30920             | Float   |
| diferenca_valor | 3921.0            | Float   |
| percentual_diff | 12.68111254851229 | Float   |
| sinistrada      | true ou false     | Boolean |
| valor_atrativo  | true ou false     | Boolean |
| link            | link_do_anuncio   | String  |

## 🚀 Como Executar

Inicie o Servidor Ollama:

```bash
ollama run gemma4:e2b
```

No meu caso como uso o Docker no Windows + WSL2

```bash
docker exec -it ollama ollama run gemma4:e2b
```

Instale as Dependências:

```bash
pip install -r requirements.txt
```

Rode o Pipeline Completo:

```bash
python main.py
```

## 📋 Notas de Implementação

- **Performance**: O processamento de inferência é feito em lote (batch). Com cerca de 56 anúncios, o uso de GPU (via DirectML ou CUDA) é altamente recomendado ainda mais se for processar largas quantidades
- **Precisão**: O uso do Gemma 4 mostrou-se superior ao Llama 3 para extração de dados estruturados e lógica booleana neste domínio específico.
- **Filtros de Qualidade**: A Camada Gold exclui automaticamente anúncios com preços não atrativos
- Estou deixando os arquivos JSON base (gerados no moto-o-meter) assim como os arquivos processados para ter uma noção dos resultados de cada camada
- Você pode utilizar o projeto para outros modelos de moto, mas o uso é por conta e risco, sendo necessário montar o JSON de informações da tabela FIPE para sua moto e suas versões, os arquivos são entregues "as-is"
