"""Projeto final: chatbot com RAG no FAQ do Observa Cidade.

Busca os trechos mais parecidos no banco vetorial e manda junto com a pergunta
para o modelo responder usando só o conteúdo do FAQ.

Antes de rodar, crie o banco:
    python aulas/03_criar_banco_vetorial.py

Depois:
    python aulas/projeto_final_faq_rag/03_chatbot_rag.py
"""

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

regras = (
    "Você é o assistente virtual do Observa Cidade. "
    "Responda às dúvidas usando APENAS as informações do FAQ fornecido. "
    "Se a resposta não estiver no FAQ, diga educadamente que não encontrou essa informação "
    "e recomende abrir um chamado em Ajuda e Suporte."
)

historico = [{"role": "system", "content": regras}]
print("=" * 60)
print("Chatbot RAG do Observa Cidade iniciado! Digite sua pergunta ou 'sair' para encerrar.")
print("=" * 60)

while True:
    pergunta = input("\nVocê: ").strip()

    if pergunta.lower() in ("sair", "exit"):
        print("Até logo!")
        break

    if not pergunta:
        continue

    # R (Retrieve): busca os 2 trechos mais relevantes no FAQ
    resultado = colecao.query(query_texts=[pergunta], n_results=2)
    contexto = "\n---\n".join(resultado["documents"][0])

    # A (Augment): adiciona o contexto na mensagem do usuário
    mensagem_usuario = f"Contexto do FAQ:\n{contexto}\n\nPergunta: {pergunta}"
    historico.append({"role": "user", "content": mensagem_usuario})

    # G (Generate): o modelo gera a resposta baseada no contexto
    resposta = cliente.chat.completions.create(
        model=modelo,
        messages=historico,
        temperature=0,
    )

    texto_resposta = resposta.choices[0].message.content
    historico.append({"role": "assistant", "content": texto_resposta})

    print(f"\nAssistente: {texto_resposta}")
