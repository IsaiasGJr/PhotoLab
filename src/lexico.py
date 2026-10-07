#!/usr/bin/env python3
"""Analisador lexico da PhotoLab (etapa E2).

Uso:
    python src/lexico.py exemplos/ola.photolab

Imprime um token por linha ("NOME 'texto' linha N") e, ao final, a contagem.
Se houver erro lexico, imprime linha e coluna de cada um e sai com codigo 1.

Antes da primeira execucao, gere o lexer com ./gerar.sh (cria a pasta gerado/).
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# gerar.sh escreve em gerado/; gerado/gramatica/ cobre quem rodar o antlr4
# direto da raiz do repositorio (o ANTLR preserva o caminho relativo do .g4).
sys.path.insert(0, str(RAIZ / "gerado"))
sys.path.insert(0, str(RAIZ / "gerado" / "gramatica"))

try:
    from antlr4 import InputStream
    from antlr4 import Token as AntlrToken
    from antlr4.error.ErrorListener import ErrorListener
except ImportError:
    sys.exit("Falta o runtime do ANTLR. Instale com: pip install antlr4-python3-runtime")

try:
    # "lexer grammar PhotoLab;" gera a classe PhotoLab em gerado/PhotoLab.py
    from PhotoLab import PhotoLab as PhotoLabLexer
except ImportError:
    sys.exit("Lexer nao encontrado em gerado/. Rode ./gerar.sh primeiro.")


class Token:
    def __init__(self, nome, texto, linha, coluna):
        self.nome = nome
        self.texto = texto
        self.linha = linha
        self.coluna = coluna  # 1-based


class ErroLexico:
    def __init__(self, linha, coluna, mensagem):
        self.linha = linha
        self.coluna = coluna  # 1-based
        self.mensagem = mensagem

    def __str__(self):
        return f"erro lexico (linha {self.linha}, coluna {self.coluna}): {self.mensagem}"


class _OuvinteDeErros(ErrorListener):
    """Recebe do ANTLR os caracteres que nenhuma regra do lexer reconhece."""

    PREFIXO = "token recognition error at: '"

    def __init__(self):
        super().__init__()
        self.erros = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        trecho = msg[len(self.PREFIXO):-1] if msg.startswith(self.PREFIXO) else msg
        if trecho == ".":
            texto = ("ponto solto: um numero real precisa de digito antes e "
                     "depois do ponto (ex.: 3.5)")
        else:
            texto = f"caractere invalido {trecho!r}: nenhuma regra do lexico o reconhece"
        self.erros.append(ErroLexico(line, column + 1, texto))


def _mensagem_erro_token(nome, texto):
    """Mensagem para os tokens ERRO_* (entradas quase corretas)."""
    if nome == "ERRO_TEXTO":
        return (f"texto sem fechar {texto}: falta a aspa de fechamento "
                "antes do fim da linha")
    if nome == "ERRO_NUMERO":
        if texto.endswith("."):
            return f"numero malformado '{texto}': falta digito depois do ponto"
        return (f"numero malformado '{texto}': numero seguido de letras "
                "(a PhotoLab nao tem unidades como px)")
    if nome == "ERRO_COR":
        return (f"cor malformada '{texto}': use #RGB ou #RRGGBB "
                "com digitos hexadecimais (0-9, a-f)")
    return f"entrada invalida '{texto}'"


def analisar(texto):
    """Tokeniza `texto`. Devolve (tokens, erros), ambos ordenados pela posicao."""
    lexer = PhotoLabLexer(InputStream(texto))
    ouvinte = _OuvinteDeErros()
    lexer.removeErrorListeners()
    lexer.addErrorListener(ouvinte)

    tokens, erros_de_token = [], []
    while True:
        t = lexer.nextToken()
        if t.type == AntlrToken.EOF:
            break
        nome = lexer.symbolicNames[t.type]
        if nome.startswith("ERRO_"):
            erros_de_token.append(
                ErroLexico(t.line, t.column + 1, _mensagem_erro_token(nome, t.text)))
        else:
            tokens.append(Token(nome, t.text, t.line, t.column + 1))

    # ouvinte.erros so esta completo depois de consumir toda a entrada
    erros = ouvinte.erros + erros_de_token
    return tokens, sorted(erros, key=lambda e: (e.linha, e.coluna))


def main(argv):
    if len(argv) != 2:
        sys.exit("uso: python src/lexico.py <arquivo.photolab>")
    caminho = Path(argv[1])
    try:
        texto = caminho.read_text(encoding="utf-8")
    except OSError as e:
        sys.exit(f"nao foi possivel ler {caminho}: {e.strerror}")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    tokens, erros = analisar(texto)
    for t in tokens:
        print(f"{t.nome} {t.texto!r} linha {t.linha}")
    print(f"{len(tokens)} tokens reconhecidos")

    if erros:
        print(f"{len(erros)} erro(s) lexico(s) em {caminho}:", file=sys.stderr)
        for e in erros:
            print(f"  {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
