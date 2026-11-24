"""Aula 3: PDF -> chunks -> banco vetorial no ChromaDB.

Lê o FAQ do Observa Cidade, corta o texto em pedaços com overlap e salva os
vetores em dados/banco_vetorial_faq. No fim, faz uma busca semântica de teste.

Rode com:
    python aulas/03_criar_banco_vetorial.py
"""

import os
import sys

import chromadb
from pypdf import PdfReader

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
caminho_pdf = os.path.join(RAIZ, "dados", "faq_observa_cidade.pdf")
caminho_banco = os.path.join(RAIZ, "dados", "banco_vetorial_faq")

if not os.path.exists(caminho_pdf):
    raise SystemExit(f"PDF não encontrado: {caminho_pdf}")

# 1. LENDO O ARQUIVO PDF
leitor = PdfReader(caminho_pdf)
texto = ""
for pagina in leitor.pages:
    texto += (pagina.extract_text() or "") + "\n"

# 2. CHUNKS COM OVERLAP (JANELA DESLIZANTE)
tamanho_chunk = 450
overlap = 80
chunks = []
inicio = 0

while inicio < len(texto):
    chunks.append(texto[inicio : inicio + tamanho_chunk])
    inicio += tamanho_chunk - overlap

# 3. BANCO VETORIAL (CHROMADB COM EMBEDDING NATIVO)
cliente_chroma = chromadb.PersistentClient(path=caminho_banco)

# Apaga a coleção antiga para não misturar com um FAQ anterior.
try:
    cliente_chroma.delete_collection("faq_colecao")
except Exception:
    pass

# get_or_create_collection usa o embedding nativo do ChromaDB por padrão.
# Na primeira vez ele baixa o modelo all-MiniLM-L6-v2 (~80 MB).
colecao = cliente_chroma.get_or_create_collection(
    name="faq_colecao",
    metadata={"hnsw:space": "cosine"},
)

ids = [f"chunk_{i}" for i in range(len(chunks))]
colecao.upsert(ids=ids, documents=chunks)
print(f"{len(chunks)} chunks salvos com sucesso!")

# 4. TESTE DE BUSCA SEMÂNTICA
pergunta = "Como registro uma ocorrência com foto?"
resultado = colecao.query(query_texts=[pergunta], n_results=2)

print("\n--- Teste de Busca ---")
print("Pergunta:", pergunta)
for i, trecho in enumerate(resultado["documents"][0], 1):
    print(f"\n[{i}] {trecho.strip()}")
