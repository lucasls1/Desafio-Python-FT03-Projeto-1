import re # Biblioteca Para localizar,identificar,validar,extrair e substituir padrões de texto.
import requests # Biblioteca para comunicação com sites, APIs

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
