# Clima por CEP — etapa 1

Este primeiro passo consulta a API ViaCEP e mostra cidade e estado. Depois,
vamos usar a cidade e o estado para consultar a geocodificação e a previsão
do tempo no Open-Meteo.

## Preparar

No terminal, instale a dependência:

```bash
python -m pip install request
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

Documentação: [ViaCEP](https://viacep.com.br/), [geocodificação Open-Meteo](https://open-meteo.com/en/docs/geocoding-api) e [previsão Open-Meteo](https://open-meteo.com/en/docs).

