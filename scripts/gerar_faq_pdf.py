"""Gera o FAQ do Observa Cidade em Markdown e PDF.

O conteúdo é o mesmo da base do assistente do projeto (FaqInitializer, no backend).
Rode este script quando quiser atualizar o FAQ:

    python scripts/gerar_faq_pdf.py

Ele escreve:
    dados/faq_observa_cidade.md
    dados/faq_observa_cidade.pdf
"""

from __future__ import annotations

import os
import sys
from collections import OrderedDict
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(RAIZ, "dados")
CAMINHO_MD = os.path.join(PASTA_DADOS, "faq_observa_cidade.md")
CAMINHO_PDF = os.path.join(PASTA_DADOS, "faq_observa_cidade.pdf")

# (categoria, pergunta, resposta)
FAQS = [
    (
        "Ocorrências",
        "Como registro uma ocorrência?",
        "Na tela inicial toque no botão central de nova ocorrência, escolha a categoria "
        "(por exemplo buraco, iluminação, lixo ou alagamento), descreva o problema, "
        "confirme o local e envie. O GPS do celular é usado para marcar o ponto.",
    ),
    (
        "Ocorrências",
        "Preciso anexar foto para abrir uma ocorrência?",
        "A foto é opcional, mas ajuda muito a equipe a entender o problema. Você pode tirar "
        "uma foto na hora ou escolher uma da galeria. A imagem fica anexada à ocorrência.",
    ),
    (
        "Ocorrências",
        "Como acompanho o andamento da minha ocorrência?",
        "Abra a ocorrência na lista da tela inicial. Lá aparecem o status atual "
        "(Pendente, Em andamento ou Resolvida), o histórico de mudanças e os "
        "comentários da equipe.",
    ),
    (
        "Ocorrências",
        "O que significa cada status da ocorrência?",
        "Pendente: registrada e aguardando análise. Em andamento: a equipe já assumiu e está "
        "atuando. Resolvida: o problema foi atendido. Você recebe uma notificação "
        "quando o status muda.",
    ),
    (
        "Ocorrências",
        "Posso editar ou excluir uma ocorrência que registrei?",
        "Sim, mas apenas as ocorrências criadas por você. Na tela de detalhes aparecem as "
        "opções de editar e excluir. Ocorrências de outros cidadãos ficam somente "
        "para visualização.",
    ),
    (
        "Ocorrências",
        "Quais categorias de ocorrência existem?",
        "As categorias são definidas pela prefeitura e aparecem no formulário de nova "
        "ocorrência, com nome e ícone. Exemplos comuns: buraco na via, iluminação "
        "pública, limpeza e lixo, alagamento, poda de árvore e sinalização.",
    ),
    (
        "Ocorrências",
        "Quanto tempo leva para uma ocorrência ser resolvida?",
        "O prazo varia conforme a categoria e a agenda da secretaria responsável, por isso o "
        "aplicativo não promete uma data fixa. Você acompanha cada etapa pelo status "
        "e pelas notificações.",
    ),
    (
        "Localização",
        "Por que o aplicativo pede acesso à localização?",
        "A localização é usada para marcar automaticamente o endereço da ocorrência e mostrar "
        "no mapa o ponto exato do problema. Sem esse acesso você ainda pode informar o "
        "endereço manualmente.",
    ),
    (
        "Notificações",
        "Recebo aviso quando minha ocorrência é atualizada?",
        "Sim. Sempre que o status muda ou a equipe comenta, aparece uma notificação no ícone "
        "de sino da tela inicial. Toque nela para ver o detalhe da ocorrência.",
    ),
    (
        "Administração",
        "Como funciona o aplicativo para o administrador?",
        "O administrador vê um painel com todas as ocorrências, pode filtrar por status, "
        "alterar o status, responder comentários, gerenciar usuários e consultar "
        "estatísticas e chamados de suporte.",
    ),
    (
        "Administração",
        "O que o administrador consegue fazer com os usuários?",
        "No menu de usuários o administrador consulta a lista de cidadãos cadastrados, "
        "promove ou remove permissões e pode desativar contas em caso de uso "
        "indevido do aplicativo.",
    ),
    (
        "Administração",
        "Onde vejo as estatísticas das ocorrências?",
        "Na tela inicial do administrador há um resumo com totais por status e por categoria, "
        "além dos indicadores mais recentes. Esses números são calculados direto no "
        "banco de dados da aplicação.",
    ),
    (
        "Suporte",
        "Como abro um chamado para o suporte?",
        "Acesse Ajuda e Suporte no perfil, escreva o assunto e a mensagem. O chamado fica "
        "registrado e a equipe responde pelo próprio aplicativo, na lista dos seus "
        "chamados.",
    ),
    (
        "Conta",
        "Esqueci minha senha. Como recupero o acesso?",
        "Na tela de login toque em esqueci minha senha e informe o telefone cadastrado. "
        "Siga as instruções enviadas para definir uma nova senha. Se não conseguir, "
        "abra um chamado em Ajuda e Suporte.",
    ),
    (
        "Conta",
        "Como altero meus dados de cadastro?",
        "Abra a tela de perfil. Lá você atualiza nome, telefone e foto, e também pode trocar "
        "a senha. O e-mail de login não pode ser alterado pelo aplicativo.",
    ),
    (
        "Privacidade",
        "Meus dados pessoais ficam seguros?",
        "Sim. O acesso à API é protegido por autenticação com token, as senhas são guardadas "
        "criptografadas e cada cidadão só enxerga e altera as próprias ocorrências. "
        "As imagens também exigem autenticação para serem abertas.",
    ),
    (
        "Aplicativo",
        "O aplicativo funciona sem internet?",
        "O envio e a consulta das ocorrências precisam de conexão com a internet. Se a rede "
        "estiver instável, os dados digitados podem ser perdidos; envie novamente "
        "quando a conexão voltar.",
    ),
    (
        "Assistente",
        "O que é o assistente virtual do Observa Cidade?",
        "É este chat de ajuda. Ele consulta uma base de perguntas frequentes sobre o "
        "aplicativo e, quando a inteligência artificial está habilitada, redige a "
        "resposta com base nessa mesma base. Se não souber, orienta a abrir um "
        "chamado no suporte.",
    ),
    (
        "Assistente",
        "Como o assistente usa inteligência artificial?",
        "A pergunta é comparada com a base de conhecimento por similaridade de texto. Os "
        "trechos mais relevantes servem de contexto para o modelo de linguagem, que "
        "responde em português. Sem chave de IA configurada, a própria base responde.",
    ),
    (
        "Assistente",
        "O assistente pode errar a resposta?",
        "Pode. Ele só usa as informações da base de conhecimento e evita inventar prazos, "
        "telefones ou políticas. Quando não encontra o assunto, avisa que não sabe e "
        "sugere abrir um chamado em Ajuda e Suporte.",
    ),
]


def agrupar() -> OrderedDict[str, list[tuple[str, str]]]:
    grupos: OrderedDict[str, list[tuple[str, str]]] = OrderedDict()
    for categoria, pergunta, resposta in FAQS:
        grupos.setdefault(categoria, []).append((pergunta, resposta))
    return grupos


def escrever_markdown(grupos: OrderedDict[str, list[tuple[str, str]]]) -> None:
    linhas = [
        "# FAQ do Observa Cidade",
        "",
        "Base de conhecimento do assistente virtual do aplicativo.",
        "",
    ]
    for categoria, itens in grupos.items():
        linhas.append(f"## {categoria}")
        linhas.append("")
        for pergunta, resposta in itens:
            linhas.append(f"### {pergunta}")
            linhas.append(resposta)
            linhas.append("")
    with open(CAMINHO_MD, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas))


def escrever_pdf(grupos: OrderedDict[str, list[tuple[str, str]]]) -> None:
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        spaceAfter=6,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor="#555555",
        spaceAfter=18,
    )
    categoria = ParagraphStyle(
        "Categoria",
        parent=estilos["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        spaceBefore=14,
        spaceAfter=6,
    )
    pergunta = ParagraphStyle(
        "Pergunta",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=4,
    )
    resposta = ParagraphStyle(
        "Resposta",
        parent=estilos["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )

    documento = SimpleDocTemplate(
        CAMINHO_PDF,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="FAQ do Observa Cidade",
        author="Observa Cidade",
    )

    historia = [
        Paragraph("FAQ do Observa Cidade", titulo),
        Paragraph("Base de conhecimento do assistente virtual", subtitulo),
    ]
    for nome_categoria, itens in grupos.items():
        historia.append(Paragraph(escape(nome_categoria), categoria))
        for texto_pergunta, texto_resposta in itens:
            historia.append(Paragraph(escape(texto_pergunta), pergunta))
            historia.append(Paragraph(escape(texto_resposta), resposta))

    documento.build(historia)


def main() -> None:
    os.makedirs(PASTA_DADOS, exist_ok=True)
    grupos = agrupar()
    escrever_markdown(grupos)
    escrever_pdf(grupos)
    print(f"Markdown: {CAMINHO_MD}")
    print(f"PDF:      {CAMINHO_PDF}")
    print(f"Perguntas: {len(FAQS)}")


if __name__ == "__main__":
    main()
