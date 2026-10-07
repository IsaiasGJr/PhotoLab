#!/usr/bin/env bash
# Regenera o lexer em Python a partir da gramatica. O codigo gerado fica em
# gerado/ e NAO vai para o Git (veja .gitignore).
#
# Rodamos de dentro de gramatica/ porque o ANTLR preserva o caminho relativo
# do .g4 dentro de -o: da raiz, a saida iria para gerado/gramatica/.
set -euo pipefail
cd "$(dirname "$0")/gramatica"
rm -rf ../gerado
antlr4 -Dlanguage=Python3 -visitor -o ../gerado PhotoLab.g4
echo "Lexer gerado em gerado/ (confira com: python src/lexico.py exemplos/ola.photolab)"
