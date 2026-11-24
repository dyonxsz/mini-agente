# Mini-agente do curso

Anotações do ambiente que montei para as aulas de "Construindo um Mini-Agente com IA".
Por enquanto só existe a base para rodar os exemplos. Os arquivos de cada aula vão
entrar em `aulas/` conforme o professor liberar.

## O que tem na pasta

- `.venv` com Python 3.14.3
- `requirements.txt` com as bibliotecas do curso
- `.env` e `.env.example`
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

- Colocar a chave da OpenAI no `.env`, no lugar de `sua-chave-aqui` (o professor
  ainda vai passar).
- Copiar os arquivos das aulas para `aulas/`.

O `.env` está no `.gitignore`, então a chave não vai junto para o repositório.
