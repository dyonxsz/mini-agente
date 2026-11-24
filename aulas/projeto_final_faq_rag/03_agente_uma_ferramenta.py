"""Projeto final - Script 03: agente com uma ferramenta.

O agente só tem a ferramenta buscar_no_faq. Ele decide quando chamar a busca,
recebe o trecho do FAQ e monta a resposta.

Antes de rodar, crie o banco:
    python aulas/03_criar_banco_vetorial.py

Depois:
    python aulas/projeto_final_faq_rag/03_agente_uma_ferramenta.py
"""

import json
import os
import sys

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(RAIZ, ".env"))

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
)
modelo = os.getenv("OPENAI_CHAT_MODEL", "gemini-3.5-flash-lite")

cliente_chroma = chromadb.PersistentClient(
    path=os.path.join(RAIZ, "dados", "banco_vetorial_faq")
)
try:
    colecao = cliente_chroma.get_collection(name="faq_colecao")
except Exception:
    raise SystemExit(
        "Banco vetorial não encontrado. Rode primeiro:\n"
        "    python aulas/03_criar_banco_vetorial.py"
    )


def buscar_no_faq(termo_busca):
    resultado = colecao.query(query_texts=[termo_busca], n_results=2)
    return "\n---\n".join(resultado["documents"][0])


ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "buscar_no_faq",
            "description": "Busca informações oficiais no FAQ do Observa Cidade sobre o aplicativo, ocorrências, conta, privacidade e suporte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "termo_busca": {
                        "type": "string",
                        "description": "O assunto ou dúvida a pesquisar",
                    }
                },
                "required": ["termo_busca"],
            },
        },
    }
]

historico = [
    {
        "role": "system",
        "content": (
            "Você é o assistente virtual do Observa Cidade e tem uma ferramenta: buscar_no_faq. "
            "Use a ferramenta para dúvidas sobre o aplicativo, ocorrências, conta, privacidade e suporte. "
            "Se a ferramenta não trouxer a resposta, diga que não encontrou essa informação "
            "e recomende abrir um chamado em Ajuda e Suporte. "
            "Para cumprimentos, responda diretamente sem usar a ferramenta."
        ),
    }
]

print("=" * 60)
print("Agente com 1 ferramenta iniciado! Digite 'sair' para encerrar.")
print("=" * 60)

while True:
    pergunta = input("\nVocê: ").strip()
    if pergunta.lower() in ["sair", "exit"]:
        print("Até logo!")
        break
    if not pergunta:
        continue

    historico.append({"role": "user", "content": pergunta})

    while True:
        resposta = cliente.chat.completions.create(
            model=modelo,
            messages=historico,
            tools=ferramentas,
            temperature=0,
        )
        mensagem = resposta.choices[0].message
        historico.append(mensagem)

        if not mensagem.tool_calls:
            print(f"\nAgente: {mensagem.content}")
            break

        # Se pediu ferramenta, executamos a busca e devolvemos o resultado
        for pedido in mensagem.tool_calls:
            if pedido.function.name == "buscar_no_faq":
                args = json.loads(pedido.function.arguments)
                print(
                    f"   [Agente usou a ferramenta: buscar_no_faq('{args['termo_busca']}')]"
                )
                resultado_faq = buscar_no_faq(args["termo_busca"])
                historico.append(
                    {
                        "role": "tool",
                        "tool_call_id": pedido.id,
                        "content": resultado_faq,
                    }
                )
