# PhotoLab — Especificação da linguagem (v0.2 · etapa E2)

## 1. Para que serve

PhotoLab é uma linguagem textual para descrever protótipos de interfaces: quais telas existem, o que há dentro de cada uma e como o usuário navega entre elas. Um programa PhotoLab não calcula um resultado; ele descreve um produto, e as etapas seguintes do compilador o transformam em um protótipo navegável e num mapa de navegação.

## 2. Programa de exemplo

O programa abaixo é o arquivo `exemplos/catalogo.photolab`, comentado linha a linha. Ele usa todas as construções da linguagem: constantes, projeto, template, telas, layouts, estados, lista de itens de exemplo, atributos, navegação e anotação.

```
// Exemplo completo: catalogo de uma loja de fotos
const margem = 8                              // constante inteira
const tamTitulo = 20 + margem * 2             // * vem antes de +, entao vale 36
const proporcao = 3 / 2                       // divisao resulta em real: 1.5

project "Loja Foto" {                         // metadados do prototipo
    theme: "claro"                            // tema visual global
    start: Login                              // tela exibida primeiro
}

template CardProduto {                        // molde de um item de lista
    image "foto"                              // imagem de exemplo
    text "Nome do produto" (size: 16)         // texto com o atributo size
    text "R$ 0,00" (color: #2E7D32)           // atributo de cor no formato #RRGGBB
}

screen Login {                                // tela de entrada
    text "Bem-vindo de volta" (size: tamTitulo)   // atributo usa a constante
    input "E-mail"                            // campo de texto
    input "Senha" secure                      // campo com o conteudo mascarado
    checkbox "Lembrar de mim"                 // caixa de marcacao
    button "Entrar" -> go(Catalogo)           // botao que navega ate Catalogo
    note: "confirmar o texto do botao com a marca"   // anotacao de design
}

screen Catalogo {                             // tela principal
    row {                                     // layout horizontal
        text "Catalogo" (size: tamTitulo, color: #1A73E8)   // titulo em azul
        button "Sair" (gap: margem) -> go(Login)   // botao com espacamento
    }
    state carregando {                        // variante: buscando dados
        text "Carregando..."                  // mensagem de espera
    }
    state vazio {                             // variante: sem resultados
        text "Nenhum produto encontrado"      // mensagem de lista vazia
    }
    state pronto {                            // variante: com dados
        grid(2) {                             // grade de 2 colunas
            list of 6 items using template CardProduto   // 6 itens de exemplo
        }
    }
    on tap CardProduto -> go(Detalhes)        // tocar num item abre Detalhes
}

screen Detalhes for mobile {                  // versao para celular
    card {                                    // agrupa componentes
        image "foto grande" (width: 320, height: 180 * proporcao)   // calculo de altura
        text "Descricao do produto" (visible: true)   // atributo booleano
    }
    input "Quantidade" disabled               // campo desabilitado
    button "Comprar" -> go(Catalogo)          // volta ao catalogo
}
```

Lido de cima para baixo: as três primeiras linhas definem constantes numéricas que depois alimentam atributos; o bloco `project` diz o tema e qual tela abre primeiro; `CardProduto` é um molde reaproveitado pela lista da tela `Catalogo`; cada `screen` é uma tela, e cada `->` liga um componente à tela de destino. Os blocos `state` descrevem variações da mesma tela (carregando, vazia, com dados) sem duplicá-la.

## 3. Tipos de dado

| Tipo | Como se escreve | Exemplos | Onde aparece |
|---|---|---|---|
| texto | entre aspas duplas, em uma única linha; escapes `\"` `\\` `\n` `\t` | `"Entrar"`, `"ele disse \"oi\""` | rótulos, `theme`, `note`, `import` |
| inteiro | um ou mais dígitos | `0`, `16`, `007` | contagem de lista, `grid(2)`, atributos |
| real | dígitos, ponto, dígitos (os dois lados são obrigatórios) | `1.5`, `0.25` | atributos e constantes |
| cor | `#` seguido de 3 ou 6 dígitos hexadecimais | `#fff`, `#1A73E8` | atributos de cor |
| booleano | `true` ou `false` | `true` | atributos como `visible` |

Há uma conversão implícita: ao misturar inteiro e real numa conta, o resultado é real. Não há nenhuma outra conversão.

Nomes de telas, templates, estados, constantes e atributos são identificadores (letras ASCII, dígitos e `_`, sem começar por dígito). Eles **não são valores**: servem para nomear coisas e para se referir a elas (`go(Home)`, `using template CardProduto`). A linguagem é sensível a maiúsculas: `Screen` é um identificador, `screen` é palavra-chave.

## 4. Comandos

| Comando | Forma | O que faz |
|---|---|---|
| `const` | `const nome = expressão` | Declara uma constante numérica, usável em qualquer expressão depois da declaração. Não pode ser reatribuída. |
| `project` | `project "Nome" { theme: "claro"  start: Tela }` | Metadados do protótipo: tema visual e tela inicial. |
| `import` | `import "caminho.photolab"` | Inclui as declarações de outro arquivo. |
| `template` | `template Nome { componentes }` | Molde de componentes, reaproveitado por `list`. |
| `screen` | `screen Nome { … }` ou `screen Nome for mobile { … }` | Declara uma tela; o `for` indica a variante de dispositivo. |
| `state` | `state nome { … }` | Variação de uma tela (carregando, vazia, com dados…). |
| `text` | `text "rótulo"` | Texto estático. |
| `button` | `button "rótulo" -> go(Tela)` | Botão; o `-> go(…)` é opcional e faz o botão navegar. |
| `input` | `input "rótulo" secure` | Campo de entrada; aceita os modificadores `secure` e `disabled`. |
| `image` | `image "descrição"` | Imagem de exemplo. |
| `checkbox` | `checkbox "rótulo"` | Caixa de marcação; aceita o modificador `disabled`. |
| `list` | `list of 6 items using template Nome` | Repete um template N vezes com conteúdo de exemplo. |
| `card` | `card { componentes }` | Agrupa componentes numa unidade. |
| `row` `column` `grid` | `row { … }`, `grid(3) { … }` | Organizam o conteúdo na horizontal, na vertical ou em grade de N colunas. |
| `on tap` | `on tap Nome -> go(Tela)` | Faz o item nomeado (por exemplo, o template usado numa lista) navegar quando tocado. |
| `note` | `note: "texto"` | Anotação de design; não afeta o protótipo. |

**Atributos.** Qualquer componente aceita uma lista de atributos entre parênteses, antes do `->`: `text "Título" (size: 24, color: #1A73E8)`. Atributos conhecidos: `size`, `width`, `height`, `gap` (inteiro ou real), `color` e `background` (cor), `visible` (booleano). O valor de um atributo numérico pode ser uma expressão com constantes. Se o nome do atributo existe e se o tipo do valor está certo é verificado na análise semântica (E4), não no léxico.

## 5. Operadores e precedência

Do que une mais forte ao que une mais fraco:

| Nível | Operador | Significado | Associatividade |
|---|---|---|---|
| 1 | `( )` | parênteses: forçam a ordem | — |
| 2 | `-` (unário) | troca o sinal: `-5` | — |
| 3 | `*` `/` | multiplicação, divisão | esquerda |
| 4 | `+` `-` | soma, subtração | esquerda |

Os operadores aritméticos só valem para inteiro e real. Inteiro com inteiro dá inteiro em `+`, `-` e `*`; a divisão `/` sempre dá real (`3 / 2` vale `1.5`); misturar inteiro e real dá real. Dividir por zero é um erro. Não há soma de textos nem comparações.

Quatro símbolos **não são operadores de expressão**, por isso ficam fora da tabela de precedência: `->` liga um componente à tela de destino e só aparece no fim de uma declaração de componente; `=` só existe em `const`; `:` separa nome e valor (em `theme:`, `start:`, `note:` e nos atributos); `,` separa atributos.

## 6. Comentários

Um comentário começa em `//` e vai até o fim da linha; é descartado pelo analisador léxico. Não existe comentário de bloco. Duas consequências: `//` nunca é uma divisão (a divisão é um `/` só), e dentro de um texto `//` faz parte do texto (`"http://exemplo"` é um texto, não um comentário). Espaços, tabulações e quebras de linha também são descartados, e nenhum deles encerra comandos: a mesma tela pode ser escrita numa linha só ou em dez.

## 7. Três coisas que a linguagem deliberadamente não faz

**Não tem fluxo de controle nem funções.** Não há `if`, laços, funções definidas pelo usuário nem reatribuição de constantes. Um protótipo descreve estrutura e navegação; se ele passasse a executar a lógica do produto, viraria uma implementação, e perderia a pergunta para a qual existe: "é assim que o fluxo deve ser?". As variações de uma tela são expressas com `state`, que são descritas, nunca calculadas.

**Não acessa dados reais nem o mundo externo.** Não existe rede, arquivo, banco de dados nem entrada do usuário em tempo de execução. O conteúdo de uma `list` é sempre de exemplo. Com isso o mesmo arquivo gera sempre o mesmo protótipo, e qualquer pessoa pode abri-lo sem risco e sem configurar nada.

**Não posiciona nem estiliza livremente.** Não há coordenadas absolutas, CSS, unidades (`12px` é um erro léxico) nem sobreposição de elementos. A organização é só por `row`, `column`, `grid` e `card`, e a aparência se limita a um punhado de atributos. Isso impede que o protótipo vire design final pixel a pixel e mantém a conversa no fluxo, não no acabamento.

---

## Apêndice A — Resumo do léxico

Cada linha corresponde a uma ou mais regras de `gramatica/PhotoLab.g4`.

| Classe | Tokens | Reconhece |
|---|---|---|
| Palavras-chave | `PROJECT` `IMPORT` `CONST` `TEMPLATE` `SCREEN` `THEME` `START` `STATE` `FOR` `NOTE` `TEXT` `BUTTON` `INPUT` `IMAGE` `CHECKBOX` `LIST` `CARD` `ROW` `COLUMN` `GRID` `OF` `ITEMS` `USING` `ON` `TAP` `GO` `SECURE` `DISABLED` `TRUE` `FALSE` | as palavras reservadas, em minúsculas; não podem ser usadas como identificadores |
| Operadores | `SETA` `MAIS` `MENOS` `VEZES` `DIVIDIDO` `IGUAL` | `->` `+` `-` `*` `/` `=` |
| Pontuação | `ABRE_CHAVE` `FECHA_CHAVE` `ABRE_PAR` `FECHA_PAR` `DOIS_PONTOS` `VIRGULA` | `{` `}` `(` `)` `:` `,` |
| Literais | `INTEIRO` `REAL` `COR` `TEXTO` | os tipos da seção 3 |
| Identificador | `IDENT` | `[a-zA-Z_][a-zA-Z_0-9]*` |
| Descartados | `COMENTARIO` `ESPACO` | `//…` até o fim da linha; espaço, tabulação, quebra de linha |
| Entradas quase corretas | `ERRO_TEXTO` `ERRO_NUMERO` `ERRO_COR` | texto sem aspa final; `3.` ou `12px`; `#12`, `#abcd` |

**Erros léxicos.** O `src/lexico.py` aponta linha e coluna (a coluna começa em 1) de dois tipos de problema: caracteres que nenhuma regra reconhece (por exemplo `@`, `$`, `;` ou um `.` solto), que o próprio ANTLR sinaliza; e entradas que quase formam um token válido, que as regras `ERRO_*` capturam para dar uma mensagem específica (texto sem fechar, número malformado, cor malformada). Em ambos os casos o programa continua a análise, lista todos os erros do arquivo e termina com código de saída 1.
