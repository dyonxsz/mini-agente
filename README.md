# Mini-agente do curso

Anotações do ambiente que montei para as aulas de "Construindo um Mini-Agente com IA".
Por enquanto só existe a base para rodar os exemplos. Os arquivos de cada aula vão
entrar em `aulas/` conforme o professor liberar.

## O que tem na pasta

- `.venv` com Python 3.14.3
- `requirements.txt` com as bibliotecas do curso
- `.env` já com a chave e `.env.example` com o modelo
- `agente.py`, um chat de exemplo que usa ferramentas
- `scripts/verificar_ambiente.py`, que confere se está tudo instalado
- `aulas/` e `dados/` ainda vazias

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

Digite `sair` para encerrar. Os exercícios de cada aula vão para `aulas/`, sem
misturar com esse exemplo.

## Chave da API

A chave é a mesma do projeto Observa Cidade. Ela é do Gemini e fica na variável
`GEMINI_API_KEY` do Windows, então o `.env` só aponta para ela:

```
OPENAI_API_KEY=${GEMINI_API_KEY}
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-3.5-flash-lite
```

O SDK da OpenAI fala com o Gemini por esse endereço compatível. Testei uma chamada
de chat com o `openai` do venv e respondeu normal.

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

## O que falta

- Copiar os arquivos das aulas para `aulas/`.

O `.env` está no `.gitignore`, então a chave não vai junto para o repositório.
