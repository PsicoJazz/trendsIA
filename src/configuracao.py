
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()


class Configuracoes:

    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL")


config = Configuracoes()
