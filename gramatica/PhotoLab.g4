lexer grammar PhotoLab;

// =====================================================================
// PhotoLab v0.2 — Etapa E2: SOMENTE regras de lexer (nomes em MAIUSCULAS).
// As regras de parser entram na E3.
//
// Convencoes desta gramatica:
//  - Uma regra por palavra-chave, para o parser da E3 poder usar cada uma.
//  - Palavras-chave vem ANTES de IDENT: em empate de tamanho, o ANTLR
//    escolhe a regra escrita primeiro.
//  - As regras ERRO_* existem para o lexer reconhecer, e nao esconder,
//    entradas quase corretas (texto sem fechar, numero malformado, cor
//    malformada). O src/lexico.py trata todo token ERRO_* como erro.
//  - Caractere que nenhuma regra reconhece (@, $, ;, ...) e reportado
//    pelo proprio ANTLR como "token recognition error".
// =====================================================================

// ---------------------------------------------------------------------
// Palavras-chave: declaracoes de nivel superior
// ---------------------------------------------------------------------
PROJECT   : 'project' ;
IMPORT    : 'import' ;
CONST     : 'const' ;
TEMPLATE  : 'template' ;
SCREEN    : 'screen' ;

// ---------------------------------------------------------------------
// Palavras-chave: corpo de projeto e de tela
// ---------------------------------------------------------------------
THEME     : 'theme' ;
START     : 'start' ;
STATE     : 'state' ;
FOR       : 'for' ;
NOTE      : 'note' ;

// Componentes
TEXT      : 'text' ;
BUTTON    : 'button' ;
INPUT     : 'input' ;
IMAGE     : 'image' ;
CHECKBOX  : 'checkbox' ;
LIST      : 'list' ;
CARD      : 'card' ;

// Layout
ROW       : 'row' ;
COLUMN    : 'column' ;
GRID      : 'grid' ;

// Lista com template: "list of 6 items using template X"
OF        : 'of' ;
ITEMS     : 'items' ;
USING     : 'using' ;

// Navegacao: "on tap X -> go(Y)"
ON        : 'on' ;
TAP       : 'tap' ;
GO        : 'go' ;

// Modificadores de componente
SECURE    : 'secure' ;
DISABLED  : 'disabled' ;

// Booleanos
TRUE      : 'true' ;
FALSE     : 'false' ;

// ---------------------------------------------------------------------
// Operadores
// ---------------------------------------------------------------------
SETA      : '->' ;   // navegacao entre telas (nao e operador de expressao)
MAIS      : '+' ;
MENOS     : '-' ;
VEZES     : '*' ;
DIVIDIDO  : '/' ;
IGUAL     : '=' ;    // usado somente em "const nome = expressao"

// ---------------------------------------------------------------------
// Pontuacao
// ---------------------------------------------------------------------
ABRE_CHAVE  : '{' ;
FECHA_CHAVE : '}' ;
ABRE_PAR    : '(' ;
FECHA_PAR   : ')' ;
DOIS_PONTOS : ':' ;
VIRGULA     : ',' ;

// ---------------------------------------------------------------------
// Literais
// ---------------------------------------------------------------------
// Real exige digito dos dois lados do ponto: 3.5 e valido; 3. e .5 nao.
REAL      : DIGITO+ '.' DIGITO+ ;
INTEIRO   : DIGITO+ ;

// Cor: #RGB ou #RRGGBB
COR       : '#' HEX HEX HEX ( HEX HEX HEX )? ;

// Texto entre aspas duplas, em uma unica linha, com escapes \" \\ \n \t
TEXTO     : '"' ( ESCAPE | ~["\\\r\n] )* '"' ;

// Identificador (nomes de tela, template, estado, constante, atributo)
IDENT     : [a-zA-Z_] [a-zA-Z_0-9]* ;

// ---------------------------------------------------------------------
// Entradas quase corretas, reconhecidas para poder dar erro preciso
// (precisam vir DEPOIS das regras corretas: empate de tamanho -> a
// regra correta, escrita antes, vence)
// ---------------------------------------------------------------------
ERRO_TEXTO   : '"' ~["\r\n]* ;                   // aspa aberta e nunca fechada
ERRO_NUMERO  : DIGITO+ '.'                       // "3."   ponto sem digito depois
             | DIGITO+ ( '.' DIGITO+ )? [a-zA-Z_] [a-zA-Z_0-9]*   // "12px", "3.5abc"
             ;
ERRO_COR     : '#' [a-zA-Z_0-9]* ;               // "#12", "#abcd", "#ggg"

// ---------------------------------------------------------------------
// Descartados
// ---------------------------------------------------------------------
COMENTARIO : '//' ~[\r\n]* -> skip ;
ESPACO     : [ \t\r\n]+    -> skip ;

// ---------------------------------------------------------------------
// Fragmentos auxiliares
// ---------------------------------------------------------------------
fragment DIGITO : [0-9] ;
fragment HEX    : [0-9a-fA-F] ;
fragment ESCAPE : '\\' ["\\nt] ;
