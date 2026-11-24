"""Aula 2: memória da conversa.

A primeira chamada apresenta a usuária. A segunda faz a mesma pergunta sem
mandar o histórico; a terceira manda o histórico e mostra a diferença.

Rode com:
    python aulas/02_memoria.py
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

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


def perguntar(mensagens: list[dict]) -> str:
    resposta = cliente.chat.completions.create(
        model=modelo,
        messages=mensagens,
    )
    return resposta.choices[0].message.content


print("=" * 60)
print("CHAMADA 1 - a usuária se apresenta")
print("=" * 60)

apresentacao = (
    "Oi! Meu nome é Ana\n"
    "e meu projeto é um sistema\n"
    "de estoque de uma farmácia."
)
resposta_1 = perguntar([{"role": "user", "content": apresentacao}])
print("USER     :", apresentacao)
print("ASSISTANT:", resposta_1)

print()
print("=" * 60)
print("CHAMADA 2 - sem memória (só a pergunta nova)")
print("=" * 60)

pergunta = "Qual é o meu nome e o que eu faço?"
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
