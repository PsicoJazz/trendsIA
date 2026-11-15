
from cliente import ClienteLLM
from prompts import SYSTEM_PROMPT, montar_prompt


def main():

    print("=" * 50)
    print("              AULAFLOW AI")
    print("     Organizador Inteligente de Aulas")
    print("=" * 50)

    anotacoes = input(
        "\nDigite suas anotações de aula:\n"
    )

    if not anotacoes.strip():
        print("\nErro: informe alguma anotação.")
        return

    cliente = ClienteLLM()

    prompt = montar_prompt(anotacoes)

    print("\nConsultando o modelo Qwen 3.5 9B...")

    try:

        resposta = cliente.gerar_resposta(
            SYSTEM_PROMPT,
            prompt
        )

        print("\n===== PLANEJAMENTO GERADO =====")
        print(resposta)

    except RuntimeError as erro:

        print(f"\nFalha na aplicação: {erro}")


if __name__ == "__main__":
    main()
