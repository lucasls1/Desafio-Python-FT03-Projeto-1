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

