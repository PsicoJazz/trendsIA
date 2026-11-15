
from cliente import ClienteLLM


def testar_conexao():

    cliente = ClienteLLM()

    resposta = cliente.gerar_resposta(
        "Você é um assistente de testes. Responda somente JSON.",
        "Retorne um JSON com status igual a funcionando."
    )

    print("Resposta recebida:")
    print(resposta)

    assert resposta.strip(), "A resposta está vazia."

    print("\nTeste concluído!")


if __name__ == "__main__":
    testar_conexao()
