"""Confere se o ambiente do curso esta pronto.

Uso (com o .venv ativado):
    python scripts/verificar_ambiente.py
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

try:  # deixa os acentos e simbolos funcionarem no terminal do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = Path(__file__).resolve().parent.parent

OK = "[OK]"
FALHA = "[X]"

problemas: list[str] = []


def checar(descricao: str, funcao) -> None:
    try:
        detalhe = funcao()
    except Exception as exc:  # noqa: BLE001
        print(f"{FALHA} {descricao}: {exc}")
        problemas.append(descricao)
    else:
        print(f"{OK} {descricao}" + (f" ({detalhe})" if detalhe else ""))


def verificar_python() -> str:
    if sys.version_info < (3, 10):
        raise RuntimeError("o curso precisa do Python 3.10 ou mais novo")
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def verificar_import(nome: str, pacote: str | None = None):
    def _inner():
        modulo = importlib.import_module(nome)
        return getattr(modulo, "__version__", "instalado")

    _inner.__doc__ = pacote or nome
    return _inner


def verificar_env() -> str:
    arquivo = RAIZ / ".env"
    if not arquivo.exists():
        raise RuntimeError("arquivo .env nao encontrado; copie .env.example para .env")

    from dotenv import load_dotenv

    load_dotenv(arquivo)
    chave = os.getenv("OPENAI_API_KEY", "").strip()
    if not chave:
        raise RuntimeError("OPENAI_API_KEY vazia no .env")
    if chave == "sua-chave-aqui":
        raise RuntimeError("troque 'sua-chave-aqui' pela chave entregue pelo professor")
    if chave != chave.strip():
        raise RuntimeError("a chave tem espacos sobrando")
    return "chave configurada"


def verificar_pasta_dados() -> str:
    pasta = RAIZ / "dados"
    if not pasta.exists():
        pasta.mkdir(parents=True, exist_ok=True)
    return str(pasta)


def main() -> int:
    print(f"Pasta do curso: {RAIZ}\n")

    checar("Python 3.10+", verificar_python)
    checar("Biblioteca openai", verificar_import("openai"))
    checar("Biblioteca python-dotenv", verificar_import("dotenv"))
    checar("Biblioteca tiktoken", verificar_import("tiktoken"))
    checar("Biblioteca torch", verificar_import("torch"))
    checar("Biblioteca sentence-transformers", verificar_import("sentence_transformers"))
    checar("Biblioteca chromadb", verificar_import("chromadb"))
    checar("Biblioteca pandas", verificar_import("pandas"))
    checar("Biblioteca sqlalchemy", verificar_import("sqlalchemy"))
    checar("Biblioteca pypdf", verificar_import("pypdf"))
    checar("Arquivo .env", verificar_env)
    checar("Pasta dados/", verificar_pasta_dados)

    print()
    if problemas:
        print(f"{FALHA} Faltam {len(problemas)} item(ns). Resolva o que esta marcado acima.")
        return 1

    print("Ambiente OK - pronto para começar!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
