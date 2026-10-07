"""Testes do analisador lexico da PhotoLab.

Rodar (a partir da raiz do repositorio, depois de ./gerar.sh):
    python -m unittest discover -s testes -v
"""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import lexico  # noqa: E402


def ler(relativo):
    return (RAIZ / relativo).read_text(encoding="utf-8")


def nomes(fonte):
    """Nomes dos tokens reconhecidos em `fonte` (erros devem ser zero)."""
    tokens, erros = lexico.analisar(fonte)
    assert erros == [], [str(e) for e in erros]
    return [t.nome for t in tokens]


def posicoes_de_erro(fonte):
    _, erros = lexico.analisar(fonte)
    return [(e.linha, e.coluna) for e in erros]


class ExemplosValidos(unittest.TestCase):
    def test_nenhum_erro(self):
        for nome in ("ola", "login", "catalogo"):
            with self.subTest(exemplo=nome):
                tokens, erros = lexico.analisar(ler(f"exemplos/{nome}.photolab"))
                self.assertEqual([str(e) for e in erros], [])
                self.assertGreater(len(tokens), 0)

    def test_contagem_do_menor_exemplo(self):
        tokens, _ = lexico.analisar(ler("exemplos/ola.photolab"))
        self.assertEqual(len(tokens), 13)


class Tokens(unittest.TestCase):
    def test_palavra_chave_x_identificador(self):
        self.assertEqual(nomes("screen"), ["SCREEN"])
        self.assertEqual(nomes("screens"), ["IDENT"])
        self.assertEqual(nomes("Screen"), ["IDENT"])  # case-sensitive

    def test_inteiro_e_real(self):
        self.assertEqual(nomes("3"), ["INTEIRO"])
        self.assertEqual(nomes("3.5"), ["REAL"])
        self.assertEqual(nomes("007"), ["INTEIRO"])

    def test_booleanos(self):
        self.assertEqual(nomes("true false"), ["TRUE", "FALSE"])

    def test_cores(self):
        self.assertEqual(nomes("#fff #1A73E8"), ["COR", "COR"])

    def test_texto_com_escape_e_virgula(self):
        self.assertEqual(nomes(r'"a\"b, c"'), ["TEXTO"])

    def test_operadores(self):
        self.assertEqual(nomes("a + b - c * d / e"),
                         ["IDENT", "MAIS", "IDENT", "MENOS", "IDENT",
                          "VEZES", "IDENT", "DIVIDIDO", "IDENT"])
        self.assertEqual(nomes("a->b"), ["IDENT", "SETA", "IDENT"])
        self.assertEqual(nomes("const x = 1"), ["CONST", "IDENT", "IGUAL", "INTEIRO"])

    def test_comentario_e_descartado_e_nao_e_divisao(self):
        self.assertEqual(nomes("5 / 2 // resto ignorado: @ $ ;"),
                         ["INTEIRO", "DIVIDIDO", "INTEIRO"])
        self.assertEqual(nomes("// so comentario"), [])

    def test_espaco_em_branco_descartado(self):
        self.assertEqual(nomes("  \t\n\r\n  "), [])

    def test_navegacao(self):
        self.assertEqual(nomes("on tap Card -> go(Home)"),
                         ["ON", "TAP", "IDENT", "SETA", "GO",
                          "ABRE_PAR", "IDENT", "FECHA_PAR"])

    def test_linha_e_coluna_dos_tokens(self):
        tokens, _ = lexico.analisar("screen A {\n  text \"x\"\n}")
        texto = [t for t in tokens if t.nome == "TEXT"][0]
        self.assertEqual((texto.linha, texto.coluna), (2, 3))


class Erros(unittest.TestCase):
    def test_caractere_invalido(self):
        self.assertEqual(
            posicoes_de_erro(ler("exemplos/invalidos/caractere_invalido.photolab")),
            [(5, 21)])

    def test_texto_sem_fechar(self):
        self.assertEqual(
            posicoes_de_erro(ler("exemplos/invalidos/texto_sem_fechar.photolab")),
            [(4, 10)])

    def test_numero_malformado(self):
        self.assertEqual(
            posicoes_de_erro(ler("exemplos/invalidos/numero_malformado.photolab")),
            [(4, 26)])

    def test_numero_com_unidade(self):
        self.assertEqual(posicoes_de_erro("size: 12px"), [(1, 7)])

    def test_cor_malformada(self):
        self.assertEqual(posicoes_de_erro("color: #12"), [(1, 8)])
        self.assertEqual(posicoes_de_erro("color: #abcd"), [(1, 8)])

    def test_dois_pontos_no_real(self):
        self.assertEqual(posicoes_de_erro("x 1.2.3"), [(1, 6)])

    def test_varios_erros_vem_em_ordem(self):
        self.assertEqual(posicoes_de_erro("@\n$"), [(1, 1), (2, 1)])

    def test_erro_nao_conta_como_token_reconhecido(self):
        tokens, erros = lexico.analisar('text "aberto')
        self.assertEqual([t.nome for t in tokens], ["TEXT"])
        self.assertEqual(len(erros), 1)


if __name__ == "__main__":
    unittest.main()
