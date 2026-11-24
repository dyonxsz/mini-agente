"""Aula 2: memória da conversa.

A primeira chamada apresenta a usuária. A segunda faz a mesma pergunta sem
mandar o histórico; a terceira manda o histórico e mostra a diferença.

Rode com:
    python aulas/02_memoria.py
"""

import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(RAIZ, ".env"))

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
)
modelo = os.getenv("OPENAI_CHAT_MODEL", "gemini-3.5-flash-lite")


def perguntar(mensagens: list[dict], max_tokens: int = 300) -> str:
    for tentativa in range(4):
        try:
            resposta = cliente.chat.completions.create(
                model=modelo,
                messages=mensagens,
                max_tokens=max_tokens,
            )
            return resposta.choices[0].message.content
        except RateLimitError:
            if tentativa == 3:
                raise
            espera = 15 * (tentativa + 1)
            print(f"Limite de requisições atingido; esperando {espera}s...")
            time.sleep(espera)


print("=" * 60)
print("CHAMADA 1 - a usuária se apresenta")
print("=" * 60)

apresentacao = (
    "Oi! Meu nome é Ana\n"
    "e meu projeto é o Observa Cidade,\n"
    "um aplicativo para registrar ocorrências urbanas."
)
resposta_1 = perguntar([{"role": "user", "content": apresentacao}])
print("USER     :", apresentacao)
print("ASSISTANT:", resposta_1)

print()
print("=" * 60)
print("CHAMADA 2 - sem memória (só a pergunta nova)")
print("=" * 60)

pergunta = "Qual é o meu nome e qual é o meu projeto?"
resposta_2 = perguntar([{"role": "user", "content": pergunta}])
print("USER     :", pergunta)
print("ASSISTANT:", resposta_2)

print()
print("=" * 60)
print("CHAMADA 3 - com memória (histórico completo)")
print("=" * 60)

historico = [
    {"role": "user", "content": apresentacao},
    {"role": "assistant", "content": resposta_1},
    {"role": "user", "content": pergunta},
]
resposta_3 = perguntar(historico)
print("USER     :", pergunta)
print("ASSISTANT:", resposta_3)
