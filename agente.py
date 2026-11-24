"""Mini-agente de exemplo do curso.

Roda um chat no terminal e deixa o modelo usar duas ferramentas simples
(soma e data/hora). Serve para testar a chave e o caminho de function calling.

Uso:
    python agente.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

MODELO_PADRAO = "gemini-3.5-flash-lite"

INSTRUCOES = (
    "Voce e um mini-agente de exemplo. Responda em portugues, de forma curta. "
    "Use as ferramentas quando a pergunta pedir uma conta ou a data/hora."
)

FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "somar",
            "description": "Soma dois numeros.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Primeiro numero"},
                    "b": {"type": "number", "description": "Segundo numero"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "horario_atual",
            "description": "Retorna a data e a hora atuais.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def criar_cliente() -> OpenAI:
    chave = os.getenv("OPENAI_API_KEY", "").strip()
    if not chave:
        raise SystemExit("Falta OPENAI_API_KEY no .env")

    base = os.getenv("OPENAI_BASE_URL", "").strip()
    if base:
        return OpenAI(api_key=chave, base_url=base)
    return OpenAI(api_key=chave)


def executar_ferramenta(nome: str, argumentos: dict):
    if nome == "somar":
        return argumentos["a"] + argumentos["b"]
    if nome == "horario_atual":
        return datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"Ferramenta desconhecida: {nome}"


def conversar() -> None:
    cliente = criar_cliente()
    modelo = os.getenv("OPENAI_MODEL", MODELO_PADRAO).strip() or MODELO_PADRAO
    mensagens = [{"role": "system", "content": INSTRUCOES}]

    print(f"Mini-agente pronto (modelo {modelo}). Digite 'sair' para encerrar.\n")

    while True:
        try:
            pergunta = input("Voce: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if pergunta.lower() in {"sair", "exit", "quit"}:
            break
        if not pergunta:
            continue

        mensagens.append({"role": "user", "content": pergunta})

        while True:
            resposta = cliente.chat.completions.create(
                model=modelo,
                messages=mensagens,
                tools=FERRAMENTAS,
                tool_choice="auto",
            )
            mensagem = resposta.choices[0].message
            mensagens.append(mensagem)

            if not mensagem.tool_calls:
                print(f"Agente: {mensagem.content}\n")
                break

            for chamada in mensagem.tool_calls:
                nome = chamada.function.name
                try:
                    argumentos = json.loads(chamada.function.arguments or "{}")
                    resultado = executar_ferramenta(nome, argumentos)
                except Exception as exc:  # noqa: BLE001
                    argumentos = {}
                    resultado = f"erro: {exc}"

                print(f"  [ferramenta] {nome}({argumentos}) -> {resultado}")
                mensagens.append(
                    {
                        "role": "tool",
                        "tool_call_id": chamada.id,
                        "content": str(resultado),
                    }
                )


if __name__ == "__main__":
    conversar()
