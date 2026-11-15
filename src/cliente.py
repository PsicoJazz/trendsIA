# Para executar direto do código principal
# python src/app.py

import requests

from configuracoes import config


class ClienteLLM:

    def __init__(self):
        self.base_url = config.LLM_BASE_URL.rstrip("/")
        self.modelo = config.LLM_MODEL
        self.timeout = config.LLM_TIMEOUT

    def gerar_resposta(self, system_prompt, user_prompt):

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.modelo,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                verify=True
            )

            response.raise_for_status()

            resultado = response.json()

            return resultado["message"]["content"]

        except requests.exceptions.Timeout:
            raise RuntimeError(
                "Tempo limite excedido ao consultar a LLM."
            )

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "Não foi possível conectar ao servidor Ollama."
            )

        except requests.exceptions.HTTPError as erro:
            raise RuntimeError(
                f"Erro HTTP na comunicação com a LLM: {erro}"
            )

        except (KeyError, ValueError) as erro:
            raise RuntimeError(
                f"Resposta inválida recebida da LLM: {erro}"
            )
