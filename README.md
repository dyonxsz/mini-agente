# Mini-agente do curso

Anotações do ambiente que montei para as aulas de "Construindo um Mini-Agente com IA".
Os exemplos que o professor passou estão em `aulas/`, junto com um FAQ de exemplo
em `dados/faq_projeto_exemplo.pdf`.

## O que tem na pasta

- `.venv` com Python 3.14.3
- `requirements.txt` com as bibliotecas do curso
- `.env` já com a chave e `.env.example` com o modelo
- `agente.py`, um chat de exemplo com duas ferramentas
- `aulas/` com os scripts das aulas e do projeto final
- `dados/` com o PDF do FAQ e o banco vetorial gerado
- `scripts/verificar_ambiente.py`, que confere se está tudo instalado

## Para rodar

No PowerShell, dentro desta pasta:

```powershell
cd C:\Users\dyone\CURSO-MINI-AGENTE
.venv\Scripts\Activate.ps1
python scripts\verificar_ambiente.py
```

Se aparecer "Ambiente OK", está pronto. Para sair do ambiente virtual:

```powershell
deactivate
```

## Aulas

A ordem que usei para testar:

```powershell
python aulas\01_personagens_e_regras.py
python aulas\02_memoria.py
python aulas\03_criar_banco_vetorial.py
python aulas\projeto_final_faq_rag\03_chatbot_rag.py
python aulas\projeto_final_faq_rag\03_agente_uma_ferramenta.py
python aulas\projeto_final_faq_rag\04_agente_multiplas_ferramentas.py
```

O `03_criar_banco_vetorial.py` precisa rodar antes dos três últimos, porque é ele
que lê o PDF e monta o banco em `dados/banco_vetorial_faq`. Na primeira vez o
ChromaDB baixa o modelo de embedding (~80 MB).

O `03_agente_uma_ferramenta.py` é a versão intermediária, com só a busca no FAQ.
O `04` é o agente com três ferramentas: buscar no FAQ, calcular desconto no PIX e
abrir chamado de suporte. O chamado fica em `dados/chamados_suporte.csv`.

## Agente de exemplo

`agente.py` é um chat de terminal com duas ferramentas (soma e data/hora). Serve
para confirmar que a chave e o function calling estão funcionando.

```powershell
.venv\Scripts\Activate.ps1
python agente.py
```

Exemplo:

```
Voce: Quanto e 37 + 58?
  [ferramenta] somar({'b': 58, 'a': 37}) -> 95
Agente: 37 + 58 = 95.
```

Digite `sair` para encerrar.

## Chave da API

A chave é a mesma do projeto Observa Cidade. Ela é do Gemini e fica na variável
`GEMINI_API_KEY` do Windows, então o `.env` só aponta para ela:

```
OPENAI_API_KEY=${GEMINI_API_KEY}
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-3.5-flash-lite
OPENAI_CHAT_MODEL=gemini-3.5-flash-lite
```

O SDK da OpenAI fala com o Gemini por esse endereço compatível. Testei as aulas e
o agente com essa configuração.

Se o professor entregar uma chave da OpenAI de verdade (`sk-...`), troque a linha
`OPENAI_API_KEY` pela chave e apague a `OPENAI_BASE_URL`. Também vale conferir o
nome do modelo nos exemplos, porque o curso pode usar `gpt-4o-mini` ou outro.

## Coisas que deram problema aqui

O PowerShell bloqueou a ativação do venv na primeira vez. Resolvi rodando uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Também tive um problema com o `python` fora do venv. Nesta máquina o atalho da
Microsoft Store fica na frente do Python de verdade no PATH, então `python --version`
pode responder que não encontrou o programa. Com o `.venv` ativado funciona normal,
porque a pasta `.venv\Scripts` passa na frente. Se quiser arrumar de vez, dá para
desligar os aliases `python.exe` e `python3.exe` nas configurações de aplicativos do
Windows.

O `.env` e o banco vetorial estão no `.gitignore`. Se o professor mandar mais
arquivos, é só copiar para `aulas/`.
