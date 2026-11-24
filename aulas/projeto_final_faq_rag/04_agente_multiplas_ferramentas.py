"""Projeto final - Script 04: agente com múltiplas ferramentas.

O agente tem 3 ferramentas e precisa escolher a certa:
- buscar_no_faq: lê o FAQ (banco vetorial).
- calcular_desconto_pix: faz a conta exata em Python.
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


# 3. FERRAMENTA 2: CALCULAR (conta exata, feita em Python, não pelo LLM)
def calcular_desconto_pix(valor, tipo):
    # Regra de negócio real da loja: 10% em produtos, 5% em serviços
    percentual = 0.10 if tipo == "produto" else 0.05
    valor_com_desconto = valor * (1 - percentual)
    return (
        f"Valor original: R$ {valor:.2f} | Desconto PIX: {percentual:.0%} "
        f"| Valor final: R$ {valor_com_desconto:.2f}"
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
            "description": "Busca informações oficiais no FAQ da empresa sobre produtos, preços, regras e suporte.",
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
    # Ferramenta de CÁLCULO: faz a conta exata do desconto no PIX
    {
        "type": "function",
        "function": {
            "name": "calcular_desconto_pix",
            "description": "Calcula o valor final de uma compra com o desconto do PIX já aplicado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "valor": {
                        "type": "number",
                        "description": "Valor original em reais, sem desconto",
                    },
                    "tipo": {
                        "type": "string",
                        "enum": ["produto", "servico"],
                        "description": "Se é um produto ou um serviço",
                    },
                },
                "required": ["valor", "tipo"],
            },
        },
    },
    # Ferramenta de AÇÃO: grava um chamado novo (muda algo no mundo real)
    {
        "type": "function",
        "function": {
            "name": "abrir_chamado_suporte",
            "description": "Abre um chamado de suporte humano quando o cliente pede explicitamente para falar com o suporte "
            "ou quando o FAQ não tem a resposta para o problema dele.",
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
    "calcular_desconto_pix": calcular_desconto_pix,
    "abrir_chamado_suporte": abrir_chamado_suporte,
}

historico = [
    {
        "role": "system",
        "content": (
            "Você é o assistente virtual da empresa e tem 3 ferramentas. "
            "Use buscar_no_faq para dúvidas sobre regras, preços ou produtos. "
            "Use calcular_desconto_pix quando o cliente pedir o valor final de uma compra no PIX. "
            "Use abrir_chamado_suporte só quando o cliente pedir para falar com o suporte "
            "ou quando o FAQ não resolver o problema dele. "
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
