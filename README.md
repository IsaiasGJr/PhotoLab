# PhotoLab

# PhotoLab — Documentação da Estrutura da Linguagem

*Linguagem textual para criação rápida de protótipos de produto (telas, fluxos e navegação), implementada com ANTLR. "PhotoLab" é um nome provisório — troque à vontade.*

## Visão geral e objetivo

PhotoLab existe para descrever a estrutura e o fluxo de um produto (app, site, assistente conversacional) em texto simples, permitindo que alguém — designer, PO ou desenvolvedor — escreva um protótipo navegável sem depender de uma ferramenta visual e sem escrever código de verdade. O resultado da compilação de um arquivo PhotoLab não é um programa executável com lógica de negócio, é uma representação estrutural do produto: quais telas existem, o que cada uma contém, e como o usuário se move entre elas. Essa representação alimenta geradores de saída, como um protótipo HTML clicável ou um mapa de navegação.

A linguagem é deliberadamente pobre em recursos de programação. Não existem laços, funções recursivas, nem manipulação arbitrária de estado — apenas o vocabulário necessário para descrever interface, conteúdo de exemplo e transições. Isso mantém os arquivos legíveis por pessoas não técnicas e simplifica bastante a gramática ANTLR, já que não é preciso lidar com uma linguagem Turing-completa.

## Filosofia de design

Três princípios guiam as decisões de sintaxe. Declaratividade: você descreve o que existe, não os passos para construir. Legibilidade para não programadores: palavras-chave em português ou inglês simples, estrutura em blocos aninhados parecida com CSS/SCSS, sem símbolos crípticos. Progressão incremental: a gramática deve suportar uma versão mínima (telas estáticas) e crescer em versões seguintes (navegação, dados fake, estados, temas) sem quebrar o que já foi escrito.

## Estrutura do projeto

Um projeto PhotoLab é organizado em arquivos-fonte com extensão `.photolab`, agrupados por fluxo do produto. Um projeto típico teria uma pasta `screens/` com um arquivo por fluxo (`auth.photolab`, `checkout.photolab`, `perfil.photolab`), um arquivo `main.photolab` que importa os demais e declara metadados do projeto, e uma pasta `templates/` para componentes reutilizáveis compartilhados entre fluxos.

```
meu-produto/
  main.photolab
  screens/
    auth.photolab
    checkout.photolab
    perfil.photolab
  templates/
    card-produto.photolab
  saida/
    (gerado automaticamente pelo compilador)
```

O arquivo `main.photolab` concentra os `import` e define informações globais do protótipo, como tema padrão e a tela inicial:

```
project "Meu Produto" {
    theme: "claro"
    start: Login
}

import "screens/auth.photolab"
import "screens/checkout.photolab"
import "screens/perfil.photolab"
```

## Modelo conceitual

Esta seção descreve os elementos que compõem a linguagem do ponto de vista de quem escreve um protótipo. Cada um deles corresponde depois a um nó específico na árvore sintática abstrata (AST) que o compilador constrói.

### Tela (screen)

A tela é a unidade central da linguagem. Cada tela tem um nome e um corpo com componentes de interface e, opcionalmente, layout, navegação e anotações.

```
screen Login {
    text "Bem-vindo de volta"
    input "E-mail"
    input "Senha" secure
    button "Entrar" -> go(Home)
    button "Criar conta" -> go(Cadastro)
    note: "confirmar com o time de marca o texto do botão"
}
```

### Componentes

Componentes são os blocos visuais dentro de uma tela: `text`, `button`, `input`, `image`, `list`, `card`, `checkbox`, entre outros que podem ser adicionados depois. Cada componente aceita um rótulo textual e modificadores simples (`secure` para campo de senha, `disabled` para estado inativo, etc.). Componentes não têm comportamento embutido além de participar de eventos de navegação.

### Layout

Blocos de layout organizam componentes espacialmente sem exigir CSS: `row { }`, `column { }` e `grid(n) { }` agrupam componentes lado a lado, empilhados ou em grade.

```
screen Perfil {
    row {
        image "avatar"
        column {
            text "Nome do usuário"
            text "usuario@email.com"
        }
    }
}
```

### Navegação

A navegação é o que transforma um conjunto de telas soltas num protótipo de fluxo real. Ela é expressa como uma reação a um evento de componente: `button "X" -> go(TelaDestino)`, ou de forma mais geral `on tap CardProduto -> go(Detalhes)`. Toda relação de navegação declarada no arquivo alimenta, sem esforço extra, um grafo de telas que pode ser exportado como mapa de navegação.

### Dados de exemplo (placeholder data)

Para prototipar listas e conteúdo dinâmico sem um backend real, a linguagem oferece geração de conteúdo fake: `list of 6 items using template CardProduto`. O template referenciado é definido separadamente e reutilizado em qualquer lista.

```
template CardProduto {
    image "foto"
    text "Nome do produto"
    text "R$ 00,00"
}

screen Catalogo {
    list of 6 items using template CardProduto
}
```

### Estados de tela

Uma mesma tela pode ter variações de estado — vazio, carregando, erro, sucesso — declaradas como blocos alternativos dentro da tela, evitando duplicar a tela inteira para cada variação:

```
screen Catalogo {
    state loading { text "Carregando..." }
    state empty { text "Nenhum produto encontrado" }
    state loaded {
        list of 6 items using template CardProduto
    }
}
```

### Temas e variantes de dispositivo

Um protótipo pode declarar temas (`theme: "escuro"`) e variantes de tela por dispositivo (`screen Home for mobile { }` / `screen Home for desktop { }`), permitindo prototipar responsividade sem duplicar todo o conteúdo manualmente quando a diferença é pequena.

### Anotações

A palavra-chave `note:` insere um comentário de design visível para quem revisa o protótipo, mas que não afeta a saída funcional — serve para registrar dúvidas, decisões pendentes ou instruções para quem for implementar de verdade depois.

## Sintaxe geral

A sintaxe segue blocos delimitados por chaves, semelhante a CSS/SCSS, com palavras-chave que introduzem cada elemento. Comentários de linha usam `//`. Um exemplo completo de um fluxo pequeno de autenticação:

```
// Fluxo de login simplificado
screen Login {
    text "Bem-vindo de volta"
    input "E-mail"
    input "Senha" secure
    button "Entrar" -> go(Home)
}

screen Home {
    text "Você está logado!"
    button "Sair" -> go(Login)
}
```

## Arquitetura do compilador com ANTLR

O processamento de um arquivo `.photolab` segue o pipeline padrão de uma linguagem construída com ANTLR, adaptado ao escopo enxuto da linguagem.

A gramática (`PhotoLab.g4`) define, na parte de lexer, os tokens da linguagem — palavras-chave (`screen`, `template`, `state`, `button`, `input`, `text`, `image`, `list`, `row`, `column`, `grid`, `on`, `go`, `note`, `theme`, `project`, `import`), símbolos estruturais (chaves, parênteses, seta `->`) e literais (strings entre aspas, números, identificadores). Na parte de parser, define regras para cada elemento conceitual descrito acima: `screenDecl`, `componentDecl`, `layoutBlock`, `navigationRule`, `stateBlock`, `templateDecl`, `projectDecl`.

O ANTLR gera automaticamente o lexer, o parser e uma parse tree bruta, junto com uma interface de Visitor. A partir da parse tree, um Visitor próprio percorre os nós e constrói uma AST mais enxuta e específica do domínio — classes como `Screen`, `Component`, `NavigationEvent`, `Template`, `StateVariant` — que representam o protótipo de forma independente da sintaxe concreta.

Depois da construção da AST vem uma etapa de análise semântica que o ANTLR não faz sozinho: verificar se toda tela referenciada em `go(...)` existe de fato, se templates usados em `list ... using template X` estão declarados, e se não há telas duplicadas com o mesmo nome. Erros aqui devem ser reportados com a linha e coluna de origem, informação que a parse tree do ANTLR já carrega.

Por fim, a AST validada é entregue a um dos geradores de saída, que é onde a "compilação" realmente produz algo visível.

## Geração de saída

Dois geradores fazem sentido para a primeira versão da linguagem. O primeiro percorre a AST e produz um conjunto de páginas HTML com CSS mínimo, uma por tela, com os componentes renderizados como elementos visuais simples e os eventos de navegação virando links entre as páginas — o resultado é um protótipo clicável, abrível em qualquer navegador. O segundo percorre apenas as telas e as relações de navegação (ignorando componentes internos) e produz um diagrama de fluxo, por exemplo em formato Mermaid, mostrando o mapa de navegação do produto — útil para apresentar o fluxo geral para stakeholders sem entrar em detalhes visuais de cada tela.

Como os dois geradores partem da mesma AST, adicionar um terceiro formato de saída no futuro (exportar para Figma, gerar um PDF do fluxo, etc.) não exige tocar na gramática nem no parser.

## Extensibilidade futura

A gramática inicial cobre apenas telas estáticas, componentes básicos, layout e navegação simples. Incrementos planejados incluem: formulários com lógica condicional de pulo de pergunta, fluxos de diálogo para prototipagem de chatbot, dashboards com métricas e gráficos fictícios, templates de notificação (e-mail, push), variantes de localização/idioma no texto das telas, e regras simples de validação de fluxo (como um limite máximo de telas até um objetivo). Cada um desses pode ser adicionado como novas regras de parser sem alterar a estrutura já existente, desde que a gramática seja escrita de forma modular desde o início — outro motivo para manter cada conceito (tela, componente, navegação, estado) como uma regra de parser separada em vez de uma regra monolítica.

## Próximos passos sugeridos

O caminho natural a partir daqui é escrever a primeira versão do arquivo `.g4` cobrindo apenas telas e componentes estáticos (sem navegação, estados ou templates), gerar o parser, construir o Visitor que converte a parse tree numa AST mínima, e escrever o primeiro gerador de saída em HTML. Só depois de ver esse ciclo completo funcionando vale incrementar a gramática com navegação, dados fake e estados, um recurso por vez.
