# Diário de projeto — PhotoLab

Uma entrada por sessão de trabalho: o que foi tentado e o que aconteceu. As entradas abaixo registram o que de fato ocorreu até aqui; o grupo continua o diário a partir da próxima sessão.

## 09/09
Escolhemos o domínio: em vez de uma linguagem de propósito geral, uma linguagem para **prototipar interfaces** (telas, componentes e navegação entre telas). A ideia inicial era uma linguagem "não voltada a programação", que acabou sendo uma linguagem para criar protótipos. Nome provisório: ProtoLang. Rascunhamos as construções (tela, componente, layout, navegação, estado, template).

## 10/09
Renomeamos a linguagem para **PhotoLab**. A extensão dos arquivos-fonte, que era `.proto`, passou a ser `.photolab`.

## 23/09
Primeira gramática (v0.1), **combinada** (lexer + parser) e sem expressões. Tentamos rodar o `antlr4` no ambiente de desenvolvimento e não conseguimos: a máquina não tinha a ferramenta instalada e a rede bloqueava o download. A gramática ficou escrita à mão, sem nunca ter sido compilada.

## 07/10
Releitura do enunciado da E2 e descoberta de que a v0.1 não atendia: o léxico precisa de números **reais** e de **operadores**, e a v0.1 só tinha inteiros e a seta `->`. Decidimos acrescentar uma parte aritmética pequena: `const`, expressões com `+ - * /` e uma lista de atributos nos componentes (`size`, `color`, `gap`…). Os atributos deram sentido a números, cores e booleanos.

Problemas encontrados e como resolvemos:

- Pip e Maven continuavam bloqueados, mas achamos um `antlr-4.11.1-complete.jar` já instalado em outro pacote da máquina. Usamos esse jar para gerar e rodar o lexer pelo alvo **Java**. O runtime **Python** do ANTLR não pôde ser instalado, então os testes de `lexico.py` rodaram com um runtime de mentira (um módulo que chama o lexer Java e repassa os tokens). Eles testam o código de `lexico.py` e a gramática, mas **não** o runtime Python real. Falta rodar `./gerar.sh` e os testes com `antlr4-python3-runtime` instalado.
- Uma gramática `grammar PhotoLab;` com só regras de lexer faz o ANTLR imprimir `error(99): grammar PhotoLab has no rules` (reclama da parte de parser, que ficou vazia). Trocamos para `lexer grammar PhotoLab;`. Efeito colateral: a classe gerada passa a se chamar `PhotoLab` (e não `PhotoLabLexer`), por isso o `import` em `lexico.py` usa `from PhotoLab import PhotoLab as PhotoLabLexer`. Na E3 isso muda de novo, quando entrar o parser.
- O comando `antlr4 -o gerado gramatica/PhotoLab.g4` rodado da raiz escreve em `gerado/gramatica/`, porque o ANTLR preserva o caminho relativo do `.g4`. O `gerar.sh` agora entra em `gramatica/` antes de gerar, e `lexico.py` procura nos dois lugares.
- `12px` seria lido sem erro como `12` seguido do identificador `px`, e `3.` como `3` seguido de um `.` solto, sem uma mensagem que explique o problema. Criamos regras `ERRO_NUMERO`, `ERRO_TEXTO` e `ERRO_COR`, escritas depois das regras corretas, para o lexer reconhecer essas entradas quase certas e o `lexico.py` dar a mensagem específica. Empate de tamanho entre uma regra correta e uma `ERRO_*` é resolvido pela ordem no arquivo, por isso a ordem importa.
- `//` (comentário) colide visualmente com `/` (divisão). Sem problema técnico, porque o ANTLR escolhe o casamento mais longo e `//` vence; deixamos explícito na especificação que a divisão é um `/` só e que `//` dentro de um texto é parte do texto.
