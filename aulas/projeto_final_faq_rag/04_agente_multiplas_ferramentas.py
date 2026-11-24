"""Projeto final - Script 04: agente com múltiplas ferramentas.

O agente tem 3 ferramentas e precisa escolher a certa:
- buscar_no_faq: lê o FAQ do Observa Cidade (banco vetorial).
- calcular_prioridade: aplica a regra de triagem em Python.
- abrir_chamado_suporte: grava um chamado em CSV.

Antes de rodar, crie o banco:
    python aulas/03_criar_banco_vetorial.py

Depois:
    python aulas/projeto_final_faq_rag/04_agente_multiplas_ferramentas.py
"""

import csv
import json
import os
import sys
from datetime import datetime

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(RAIZ, ".env"))

# 1. CONEXÕES
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

ARQUIVO_CHAMADOS = os.path.join(RAIZ, "dados", "chamados_suporte.csv")


# 2. FERRAMENTA 1: BUSCAR (a mesma do Script 03, só LÊ o FAQ)
def buscar_no_faq(termo_busca):
    resultado = colecao.query(query_texts=[termo_busca], n_results=2)
    return "\n---\n".join(resultado["documents"][0])


# 3. FERRAMENTA 2: CALCULAR (regra de triagem exata, feita em Python, não pelo LLM)
def calcular_prioridade(categoria, risco):
    categoria = (categoria or "").strip().lower()
    risco = (risco or "").strip().lower()

    prioridade = {"baixo": "baixa", "medio": "média", "alto": "alta"}.get(
        risco, "média"
    )

    criticas = {"alagamento", "buraco", "iluminacao", "deslizamento"}
    if risco == "alto" and categoria in criticas:
        prioridade = "crítica"

    return (
        f"Categoria: {categoria or 'não informada'} | "
        f"Risco: {risco or 'não informado'} | "
        f"Prioridade sugerida: {prioridade}"
    )


# 4. FERRAMENTA 3: AGIR (grava um chamado em CSV, muda algo no mundo real)
def abrir_chamado_suporte(nome_cliente, assunto):
    numero_chamado = datetime.now().strftime("%Y%m%d%H%M%S")
    existe_arquivo = os.path.exists(ARQUIVO_CHAMADOS)

    with open(ARQUIVO_CHAMADOS, "a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        if not existe_arquivo:
            escritor.writerow(["numero_chamado", "cliente", "assunto", "data_hora"])
        escritor.writerow(
            [numero_chamado, nome_cliente, assunto, datetime.now().isoformat()]
        )

    return f"Chamado #{numero_chamado} aberto com sucesso para {nome_cliente}."


# 5. DESCREVENDO AS 3 FERRAMENTAS PARA O MODELO ESCOLHER
ferramentas = [
    # Ferramenta de LEITURA: busca um trecho do FAQ
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
    },
    # Ferramenta de CÁLCULO: aplica a regra de triagem da prefeitura
    {
        "type": "function",
        "function": {
            "name": "calcular_prioridade",
            "description": "Classifica a prioridade de uma ocorrência a partir da categoria e do risco informado pelo cidadão.",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "description": "Categoria da ocorrência, como buraco, iluminacao, lixo ou alagamento",
                    },
                    "risco": {
                        "type": "string",
                        "enum": ["baixo", "medio", "alto"],
                        "description": "Risco informado pelo cidadão",
                    },
                },
                "required": ["categoria", "risco"],
            },
        },
    },
    # Ferramenta de AÇÃO: grava um chamado novo (muda algo no mundo real)
    {
        "type": "function",
        "function": {
            "name": "abrir_chamado_suporte",
            "description": "Abre um chamado de suporte no aplicativo quando o cidadão pede explicitamente para falar com o suporte "
            "ou quando o FAQ não tem a resposta para o problema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_cliente": {
                        "type": "string",
                        "description": "Nome do cliente",
                    },
                    "assunto": {
                        "type": "string",
                        "description": "Resumo curto do problema do cliente",
                    },
                },
                "required": ["nome_cliente", "assunto"],
            },
        },
    },
]

# Dicionário liga o nome da ferramenta à função Python que realmente executa
funcoes_disponiveis = {
    "buscar_no_faq": buscar_no_faq,
    "calcular_prioridade": calcular_prioridade,
    "abrir_chamado_suporte": abrir_chamado_suporte,
}

historico = [
    {
        "role": "system",
        "content": (
            "Você é o assistente virtual do Observa Cidade e tem 3 ferramentas. "
            "Use buscar_no_faq para dúvidas sobre o aplicativo, ocorrências, conta, privacidade ou suporte. "
            "Use calcular_prioridade quando o cidadão informar a categoria e o risco de uma ocorrência. "
            "Use abrir_chamado_suporte só quando o cidadão pedir para falar com o suporte "
            "ou quando o FAQ não resolver o problema. "
            "Para cumprimentos ou perguntas gerais, responda diretamente sem usar ferramentas."
        ),
    }
]

print("=" * 60)
print("Agente com 3 ferramentas iniciado! Digite 'sair' para encerrar.")
print("=" * 60)

# 6. LOOP DO AGENTE NO TERMINAL
while True:
    pergunta = input("\nVocê: ").strip()
    if pergunta.lower() in ["sair", "exit"]:
        print("Até logo!")
        break
    if not pergunta:
        continue

    historico.append({"role": "user", "content": pergunta})

    # Ciclo de decisão do Agente
    while True:
        resposta = cliente.chat.completions.create(
            model=modelo,
            messages=historico,
            tools=ferramentas,
            temperature=0,
        )
        mensagem = resposta.choices[0].message
        historico.append(mensagem)

        # Se não pediu ferramenta, exibe a resposta final e volta ao usuário
        if not mensagem.tool_calls:
            print(f"\nAgente: {mensagem.content}")
            break

        # Se pediu ferramenta, descobrimos qual e chamamos a função certa
        for pedido in mensagem.tool_calls:
            nome_funcao = pedido.function.name
            argumentos = json.loads(pedido.function.arguments)
            print(f"   [Agente usou a ferramenta: {nome_funcao}({argumentos})]")

            funcao = funcoes_disponiveis[nome_funcao]
            resultado_funcao = funcao(**argumentos)

            historico.append(
                {
                    "role": "tool",
                    "tool_call_id": pedido.id,
                    "content": resultado_funcao,
                }
            )
