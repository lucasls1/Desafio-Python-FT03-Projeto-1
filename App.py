import re # Biblioteca Para localizar,identificar,validar,extrair e substituir padrões de texto.
import requests # Biblioteca para comunicação com sites, APIs
import time

MAX_TENTATIVAS = 3 # Número maximo de tentatis de chamadas a APIs
INTERVALO_MINIMO = 1.0  # segundos entre chamadas às APIs
_ultima_requisicao = 0.0 # Guarda o tempo da ultima requisição 

# Função para Controlar as tentativas de requisição a API
def fazer_requisicao(url: str, params: dict | None = None) -> requests.Response:
   
    global _ultima_requisicao
    # controle de tentativas 
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        # Controle de intervalo
        agora = time.monotonic() # mede o tempo decorrido
        espera = INTERVALO_MINIMO - (agora - _ultima_requisicao)
        if espera > 0:
            time.sleep(espera)

        try:
            resposta = requests.get(url, params=params, timeout=10)
            _ultima_requisicao = time.monotonic()
            resposta.raise_for_status() # verifica se ocorreu erro
            return resposta
        except requests.exceptions.HTTPError as erro:
            status = erro.response.status_code if erro.response is not None else None
            temporario = status == 429 or (status is not None and status >= 500)
            # Verificação caso não seja temporario ou já tiver atigindo o numero de tentativas, retornar o erro
            if not temporario or tentativa == MAX_TENTATIVAS:
                raise

            # Se a API informar quando tentar de novo (429), respeitamos esse valor.
            retry_after = erro.response.headers.get("Retry-After") if status == 429 else None
            try:
                espera_retentativa = float(retry_after) if retry_after else 2 ** (tentativa - 1)
            except ValueError:
                espera_retentativa = 2 ** (tentativa - 1) # intevalo entre tentativas
            print(f"API respondeu HTTP {status}. Nova tentativa em {espera_retentativa:g}s...")
            time.sleep(espera_retentativa)
            # tratamento de falhas de conexão
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if tentativa == MAX_TENTATIVAS:
                raise
            espera_retentativa = 2 ** (tentativa - 1)
            print(f"Falha temporária de conexão. Nova tentativa em {espera_retentativa}s...")
            time.sleep(espera_retentativa)

    raise RuntimeError("As tentativas de consulta terminaram sem resposta.")

# Função que recebe um CEP, Limpa os caracteres e verifica se possui 8 Números.
def consultar_cep(cep:str) -> dict | None:
    cep_limpo = re.sub(r"\D","",cep) # Remoção de tudo que não é número.
    if len(cep_limpo) != 8: # Validação da quantidade de Digitos.
        raise ValueError("O CEP deve conter 8 Números.") # Tratamento de Erro
    
    
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"  # Montagem da URL
    resposta = requests.get(url,timeout=10) # Requisição a API
    resposta.raise_for_status() # Verificação de Erro HTTP

    dados= resposta.json() # Converte o resultado para JSON

    # Verifica se o CEP Existe 
    if dados.get("erro"):
        return None
    return dados
def buscar_coordenadas(cidade: str, uf: str) -> dict | None:
    """Busca latitude e longitude da cidade no Open-Meteo."""
    resposta = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": f"{cidade}, {uf}, Brazil",
            "count": 1,
            "language": "pt",
            "countryCode": "BR",
        },
        timeout=10,
    )
    resposta.raise_for_status()
    resultados = resposta.json().get("results", [])
    return resultados[0] if resultados else None

def consultar_clima(latitude: float, longitude: float) -> dict:
    """Busca a temperatura atual para as coordenadas informadas."""
    resposta = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "timezone": "America/Sao_Paulo",
        },
        timeout=10,
    )
    resposta.raise_for_status()
    return resposta.json()

# Função Principal
def main() -> None:
    cep = input("Digite um CEP (Com ou sem hífen)")  # Inserção do CEP

    # Inicio do Tratamento de Erros
    try:
        endereco = consultar_cep(cep) # Chamada da Função

        # Verifica se o CEP foi Encontrato
        if endereco is None:
            print("CEP não encontrado.")
            return
        #Exibição do Resultado 
        print("\nEndereço encontrado:")
        print(f"Logradouro: {endereco.get('logradouro') or 'Não informado'}")
        print(f"Bairro: {endereco.get('bairro') or 'Não informado'}")
        print(f"Cidade: {endereco.get('localidade')}")
        print(f"Estado: {endereco.get('uf')}")

        local = buscar_coordenadas(endereco["localidade"], endereco["uf"])
        if local is None:
            print("\nNão encontrei as coordenadas dessa cidade no Open-Meteo.")
            return

        clima = consultar_clima(local["latitude"], local["longitude"])
        atual = clima["current"]
        print("\nClima atual:")
        print(f"Horário: {atual['time']}")
        print(f"Temperatura: {atual['temperature_2m']} °C")
        
        # Tratamento para erros de valores invalidos
    except ValueError as erro:
         print(f"Entrada inválida: {erro}")
         # Tratamento para erros de tempo de espera
    except requests.exceptions.Timeout:
        print("A consulta demorou demais. Tente novamente.")
        # Tratamento de demais tipos de erros de comunicação HTTP
    except requests.exceptions.RequestException as erro:
        print(f"Não foi possível consultar a ViaCEP: {erro}")

# Execução do programa
main() # chamada da função principal.
