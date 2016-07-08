<h1 align="center"></h1>
<p align="center">
  Códigos de web scraping 
</p>
<br />

## Conteúdo

- [Coletando TAM](#coletando-tam)
  - Funções
  - Execução
  - Instruções de uso
- [Coletando GOL](#coletando-gol)
  - Funções
  - Execução
  - Instruções de uso

<br />
<br />
<br />

##Coletando TAM

O código usado para coletar automaticamente preços de passagens na TAM (LATAM) depende fortemente do pacote RSelenium para automatização do Browser. Para entender como funciona o RSelenium, sugere-se a leitura deste tutorial: [How to drive a Web browser with R (and RSelenium)][1]. Outra boa fonte para aprender a usar o RSelenium são as *vignettes* disponíveis no CRAN do pacote: [RSelenium][2]. As funções que o RSelenium desempenha no programa são: 1) pegar o texto bruto das tabelas de viagens na TAM e 2) pegar a taxa de embarque das viagens.  
  
Uma vez que tenhamos o texto bruto da tabela, o resto do programa trabalha para limpá-lo, extraindo apenas os preços dos voos diretos. Essa parte depende de manipulação de texto e da capacidade de identificar padrões no texto (como siglas aeroportuárias BSB, GRU, GIG). Para entender como isso é feito, é preciso ter uma noção básica nos metacaracteres do R. A 4º semana do MOOC em *Data Cleaning* da Johns Hopkins University, disponível no Coursera, fornece uma boa base em como lidar com textos no R. Em especial, recomenda-se as aulas [3][3] e [4][4] da semana.  
  
Por fim, caso você não tenha nenhum conhecimento em R, sugere-se ver os vídeos das duas primeiras semanas do curso [R-programming][5], da Johns Hopkins University, também disponível no Coursera.

  
<br />

###Funções:  
####1. `getDadosTAM(origem, dataIda, destino, dataVolta)`:  
A função coleta os dados em formato bruto no site da TAM e devolve uma lista com dois elementos.
O primeiro é o texto bruto da tabela das viagens. O segundo elemento é a taxa de embarque.  
OBS: Infelizmente, a função só funciona se o browser ficar aberto na tela.  
  
**Argumentos:**  
  * *origem*: a cidade de saída no site da TAM, dado pelo código do aeroporto (e.g BSB) ou pelo nome da cidade (e.g. Brasília).  
  * *dataIda*: a data de ida da viagem, no formato "dd/mm/aaaa".  
  * *destino*: a cidade de chegada no site da TAM, dado pelo código do aeroporto (e.g BSB) ou pelo nome da cidade (e.g. Brasília).  
  * *dataVolta*: a data de volta da viagem, no formato "dd/mm/aaaa".  
  
####2.`getTamDirectPrice(textobruto)`:  
A função pega o texto bruto da tabela de viagens, filtra apenas o voos diretos e limpa o texto para retornar apenas o valores dos preços.  
  
**Argumentos:**  
  * *textobruto*: O texto bruto das tabelas de viagens. É o primeiro elemento retornado por `getDadosTAM()`.  
  
####3.`coletar(cidade, ida, volta, n = 60)`:   
A função cria uma tabela de coleta de preços da cidade.  
  
**Argumentos:**  
  * *cidade*: a cidade deve ser uma lista, em que o primeiro elemento é a cidade destino e o segundo, um vetor com as cidades de origem.  
  * *ida*: a data de ida da viagem, no formato "dd/mm/aaaa".  
  * *volta*: a data de volta da viagem, no formato "dd/mm/aaaa".  
  * *n*: O número de linhas da tabela. Ele deve ser maior que o maior vetor de preços coletado, caso contrário, haverá um erro.   
  
####4.`coletarTudo(cidades, ida, volta, n = 60)`:   
A função cria um documento Excel em que cada aba é a coleta de preços de passagens de uma cidade, efetuada por `coletar()`.  
  
**Argumentos:**  
  * *cidades*: uma lista de cidades para realizar a coleta.  
  * *ida*: a data de ida da viagem, no formato "dd/mm/aaaa".  
  * *volta*: a data de volta da viagem, no formato "dd/mm/aaaa".  
  * *n*: O número de linhas da tabela. Ele deve ser maior que o maior vetor de preços coletado, caso contrário, haverá um erro.  
  
###Execução:   
Primeiramente, criamos as cidades cujos preços das viagens devem ser coletados.
Depois criamos as listas de cidade sob responsabilidade de cada pessoa. Em seguida, criamos as datas de ida e volta das viagens.
Por fim, realizamos as coletas e salvamos os documentos Excel criados no *working directory* (wd) do R.  
  
###Instruções de Uso:
Este tutorial pressupões que você tenha instalado no seu computador [(R)][7] (no mínimo versão 3.0.2), [RStudio][8], [Java][9] e [Firefox][11]. Além disso, pressupomos que você tenha o [Selenium Standalone Server][10] no seu *working directory*.

1. Abra o RStudio e crie um novo sript de R (Ctrl + Shift + N). Copie o código do arquivo Coletando_TAM.R no script recém criado.
2. Na linha 5, substitua o caminho pelo do seu *working directory*. Nas linhas 147 e i48, substitua as datas pelas datas de ida e volta pelas de seu interesse.
3. Rode o programa da linha 1 à linha 152. Para isso, selecione essas linhas com o mouse e aperte Ctrl + Enter.
4. As coletas de cada pessoa estão nas linhas 154 à 164. Recomenda-se fortemente rodar cada uma das coletas separadamente. Selecione as linhas da coleta e aperte Ctrl+Enter para rodar. Repita para as 4 coletas. Observação: é preciso que o computador fique aberto na página do Firefox em que a coleta esteja sendo feita, portanto o computador ficará indisponível enquanto a coleta estiver sendo feita. Caso a página seja minimizada ou fechada antes da coleta acabar, feche o RStudio e recomece do passo 1.
5. (Opcional) Caso deseja saber o tempo que demorou a coleta, seleciona as linhas 166 à 168 é aperte Ctrl+Enter.
6. Abra os documentos excel criados e converta os preços de texto para numérico. 

<br />
<br />
<br />

##Coletando GOL

O código usado para coletar automaticamente preços de passagens na GOL depende fortemente do pacote RSelenium para automatização do Browser. Para entender como funciona o RSelenium, sugere-se a leitura deste tutorial: [How to drive a Web browser with R (and RSelenium)][1]. Outra boa fonte para aprender a usar o RSelenium são as *vignettes* disponíveis no CRAN do pacote: [RSelenium][2].  Os papeis do Rselenium no código é realizar a pesquisa das viagens na GOL e coletar o código fonte da página em HTML.  
  
Uma vez que tenhamos o código fonte da página, o resto do programa trabalha para identificar o que no HTML são preços de voos diretos. É importante ressaltar que a coleta na GOL é feita com programação em uma linguagem de baixo nível, se comparada com a linguagem utilizada na coleta de preços na TAM. Por um lado, isso diminui a quantidade de abstração, tornando o código compreensível por qualquer um com nível básico em programação, por outro, torna o código mais extenso, com várias funções auxiliares e loops. Para entender melhor como funciona o programa, sugere-se a lição 1 do curso [CS101][6], da Udacity, na qual se ensina como achar links no código fonte de páginas (a lição é em Pyhton, mas pode ser facilmente traduzida para R).
  
Por fim, caso você não tenha nenhum conhecimento em R, sugere-se ver os vídeos das duas primeiras semanas do curso [R-programming][5], da Johns Hopkins University, também disponível no Coursera.  
  
OBS: Embora o código se fundamente na leitura de um texto em HTML, não é preciso ter conhecimento nessa linguagem para utilizá-lo ou entendê-lo



<br />

###Funções:  
####1. `getPageGol(origem, dataIda, destino, dataVolta)`:  
A função realiza a pesquisa da viagem e coleta o código fonte da página referente a essa viagem.  
  
**Argumentos:**  
  * *origem*: a cidade de saída no site da GOL, dado pelo código do aeroporto (e.g BSB) ou pelo nome da cidade (e.g. Brasília).  
  * *dataIda*: a data de ida da viagem, no formato "dd/mm/aaaa".  
  * *destino*: a cidade de chegada no site da GOL, dado pelo código do aeroporto (e.g BSB) ou pelo nome da cidade (e.g. Brasília).  
  * *dataVolta*: a data de volta da viagem, no formato "dd/mm/aaaa".  
  

####2.`getNextVDs`:  
Dado o código fonte da página, a função pega o próximo código que contenha o voo direto.  
  
**Argumentos:**  
  * *page*: o código fonte da página da viagem na GOL em formato texto HTML.  
  

####3.`getAllVDs`:  
A função é uma aplicação iterativa de `getNextVDs`, que vai escaneando a página em HTML e pegando todos os códigos que contenham voos diretos.  
  
**Argumentos:**  
  * *page*: o código fonte da página da viagem na GOL em formato texto HTML.  
  

####4.`getNextPrice`:  
Dado o código fonte da página, a função pega o próximo código que contenha um preço de passagem.  
  
**Argumentos:**  
  * *page*: o código fonte da página da viagem na GOL em formato texto HTML.  
  

####5.`getNextTax`:  
Dado o código fonte da página, a função pega o próximo código que contenha uma taxa de passagem.  
  
**Argumentos:**  
  * *page*: o código fonte da página da viagem na GOL em formato texto HTML.  
  

####6.`getAllCosts`:  
A função é uma aplicação iterativa de `getAllVDs`, `getNextPrice`, `getNextTax` que extrai do HTML da página apenas os voos diretos e em seguida, no código dos voos diretos, extrai os preços e as taxas das viagens.  
  
**Argumentos:**  
  * *page*: o código fonte da página da viagem na GOL em formato texto HTML.  
  

####7.`coletar`:  
A função é uma aplicação iterativa de `getAllCosts`. Para cada cidade origem de uma cidade destino passada, a função extrai os custos e a média das taxas de embarque e formata em uma tabela (**data frame**).  
  
**Argumentos:**  
  * *cidade*: a cidade deve ser uma lista, em que o primeiro elemento é a cidade destino e o segundo, um vetor com as cidades de origem.  
  * *ida*: a data de ida da viagem, no formato "dd/mm/aaaa".  
  * *volta*: a data de volta da viagem, no formato "dd/mm/aaaa".  
  * *n*: O número de linhas da tabela. Ele deve ser maior que o maior vetor de preços coletado, caso contrário, haverá um erro.  
  

####8.`coletarTudo(cidades, ida, volta, n = 60)`:   
A função é uma aplicação iterativa de `coletar`. Cria um documento Excel em que cada aba é a coleta de preços de passagens de uma cidade, efetuada por `coletar()`.  
  
**Argumentos:**  
  * *cidades*: uma lista de cidades para realizar a coleta.  
  * *ida*: a data de ida da viagem, no formato "dd/mm/aaaa".  
  * *volta*: a data de volta da viagem, no formato "dd/mm/aaaa".  
  * *n*: O número de linhas da tabela. Ele deve ser maior que o maior vetor de preços coletado, caso contrário, haverá um erro.  
  

###Execução:   
Primeiramente, criamos as cidades cujos preços das viagens devem ser coletados.
Depois criamos as listas de cidade sob responsabilidade de cada pessoa. Em seguida, criamos as datas de ida e volta das viagens.
Por fim, realizamos as coletas e salvamos os documentos Excel criados no *working directory* (wd) do R.  
  
  
###Instruções de Uso:
Este tutorial pressupões que você tenha instalado no seu computador [(R)][7] (no mínimo versão 3.0.2), [RStudio][8], [Java][9] e [Firefox][11]. Além disso, pressupomos que você tenha o [Selenium Standalone Server][10] no seu *working directory*.

1. Abra o RStudio e crie um novo sript de R (Ctrl + Shift + N). Copie o código do arquivo Coletando_GOL.R no script recém criado.
2. Na linha 6, substitua o caminho pelo do seu *working directory*. Nas linhas 169 e 260, substitua as datas pelas datas de ida e volta pelas de seu interesse.
3. Rode o programa da linha 1 à linha 265. Para isso, selecione essas linhas com o mouse e aperte Ctrl + Enter.
4. As coletas de cada pessoa estão nas linhas 267 à 277. Recomenda-se fortemente rodar cada uma das coletas separadamente. Selecione as linhas da coleta e aperte Ctrl+Enter para rodar. Repita para as 4 coletas.
5. (Opcional) Caso deseja saber o tempo que demorou a coleta, seleciona as linhas 279 à 281 é aperte Ctrl+Enter.
6. Abra os documentos Excel criados e converta os preços de texto para numérico.
7. (Eventual) Lidando com pop-ups. Muitos sites apresentam aleatoriamente avisos em pop-ups para seus usuários. Nos casos do site da GOL, já lidamos com esses pop-ups. Caso apareça um novo pop-up não previsto no programa isso irá impedi-lo de rodar normalmente e pode até resultar em um erro. Para lidar com o pop-up imprevisto, no Firefox, clique com o segundo botão do mouse no botão que fecha o pop-up e selecione "Inspecionar Elemento". O código fonte da página será mostrado, com uma linha destacada. Clique nessa linha com o segundo botão do mouse e selecione "Copiar Seletor Único". Na linha 26 do script do R, há uma parte que lida com pop-ups. Embaixo da linha 33, insira as seguintes 3 linhas com o seletor único recém copiado nos locais indicados (entre aspas).
    `try(popup <- mybrowser$findElement(using = 'css selector', "Aqui o seletor único copiado" ), silent = T)`  
    `try(popup <- mybrowser$findElement(using = 'css selector', "Aqui o seletor único copiado" ), silent = T)`
    `try(popup$clickElement(), silent = T)`  
  Repita os passos de 2 à 6.

<br />
<br />
<br />



  

[1]: http://www.computerworld.com/article/2971265/application-development/how-to-drive-a-web-browser-with-r-and-rselenium.html
[2]: https://cran.rstudio.com/web/packages/RSelenium/
[3]: https://d3c33hcgiwev3.cloudfront.net/_b3fbe6648dadbb7be034ad5fb60fe438_04_02_regularExpressions.pdf?Expires=1463788800&Signature=OfL0JyB~mg6lY~wujE3ZCVGHZ2ubjLPFs8-aSSCgOy9M8~6I9LRVhvd-wUibfCJvJY-b6dJDOa5lGtJLCqMY62Z43dffRDv1vwTk-Xwc6XBr29Kc~tEhVECz7kfJPj5AUX6ByOW~Tm2JpSsRj~io~ohfp80EYt7cJKAhzpGAIaE_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A
[4]: https://d3c33hcgiwev3.cloudfront.net/_e8959793d0eb07f2390ff487700daf5f_04_03_regularExpressionsII.pdf?Expires=1463788800&Signature=Cl-JQ3u-93Spipah1Spjvy1TuhXdw-OE9uTABIlYXOpJGsVNtlmK7RIae0xD2GpWTgrMB2qM64oHxfoDnTI0e73mKsyEeamd4yBxOH91~0445bZOqjhTNmrBiX~DmqQYyTMqJ0q1MNop0MjCrAz89M1jnMupHeX3JcWjcKL06x4_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A
[5]: https://www.coursera.org/learn/r-programming/home/welcome
[6]: https://classroom.udacity.com/courses/cs101
[7]: http://www.vps.fmvz.usp.br/CRAN/
[8]: https://www.rstudio.com/products/RStudio/#Desktop
[9]: https://www.java.com/pt_BR/download/
[10]: http://www.seleniumhq.org/download/
[11]: https://www.mozilla.org/pt-BR/firefox/new/
