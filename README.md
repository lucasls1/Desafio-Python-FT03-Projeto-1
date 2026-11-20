# Clima por CEP — etapa 1

Este primeiro passo consulta a API ViaCEP e mostra cidade e estado. Depois,
vamos usar a cidade e o estado para consultar a geocodificação e a previsão
do tempo no Open-Meteo.

## Preparar

No terminal, entre nesta pasta e instale a dependência:

```bash
python -m pip install -r requirements.txt
```

## Executar

```bash
python App.py
```

Informe um CEP de oito números, por exemplo `01001-000`. A consulta exige
conexão com a internet.

## Como as APIs são conectadas

1. ViaCEP retorna `localidade` e `uf` para o CEP.
2. Open-Meteo Geocoding converte cidade e estado em latitude e longitude.
3. Open-Meteo Forecast recebe as coordenadas e retorna a temperatura atual.

No código, `params={...}` deixa o `requests` montar os parâmetros da URL com
o formato correto.

## Resiliência nesta etapa

- Cada chamada tem timeout de 10 segundos.
- Falhas de conexão, timeout, HTTP 429 e erros HTTP 5xx podem ser tentados de
  novo, até três tentativas no total.
- A espera entre retentativas cresce: 1 segundo, depois 2 segundos. Para HTTP
  429, o programa respeita o cabeçalho `Retry-After` quando ele informa um
  intervalo numérico.
- Há pelo menos 1 segundo entre chamadas consecutivas às APIs.
- Erros HTTP 4xx diferentes de 429 não são repetidos, pois normalmente indicam
  um problema na solicitação.

  ## Transformação e SQL

`transformacao.py` carrega as duas respostas JSON em tabelas temporárias
SQLite e retorna uma linha por dia de previsão. O SQL usa `json_each` para
abrir o array de datas e consulta os outros arrays pela mesma posição, uma
operação equivalente a `UNNEST`/`EXPLODE`.

Transformações aplicadas:

1. **Tipos e datas:** temperaturas e chuva são convertidas para números com
   `CAST`; as datas são normalizadas em ISO para ordenação e deduplicação e
   exibidas no formato `dia/mês/ano` com `strftime(...)`.
2. **Nulos:** `COALESCE` substitui bairro/cidade/UF ausentes e considera chuva
   ausente como `0.0` mm.
3. **Deduplicação:** CEP é chave primária da tabela de endereços; previsões
   repetidas para o mesmo CEP e data são reduzidas com `ROW_NUMBER()`.
4. **JOIN:** endereço e previsão são combinados pelo CEP.
5. **Enriquecimento de métricas:** calcula amplitude térmica (máxima menos
   mínima) e classifica o dia como `com chuva` ou `sem chuva`.

Os dados SQLite ficam em memória durante a execução; ainda não tem um
banco persistente em arquivo.

Documentação: [ViaCEP](https://viacep.com.br/), [geocodificação Open-Meteo](https://open-meteo.com/en/docs/geocoding-api) e [previsão Open-Meteo](https://open-meteo.com/en/docs).

