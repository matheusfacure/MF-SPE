<h1 align="center">MF-SPE</h1>
<p align="center">
  Códigos em R usados pelos estagiários da Secretaria de Política Econômica do Ministério da Fazenda
</p>


## Conteúdo

- [Coletando TAM](#coletando-tam)
  - Funções
  - Execução

<br />
<br />
<br />

##Coletando TAM


O código usado para coletar automáticamente preços de passagens na TAM (LATAM) depende fortemente do pacote RSelenium para automatização do Browser. Para entender como funciona o RSelenium, sugere-se a leitura deste tutorial: [How to drive a Web browser with R (and RSelenium)][1]. Outra boa fonte para aprender a usar o RSelenium são as *vignettes* disponíveis no CRAN do pacote: [RSelenium][2]. As funções que o RSelenium desempenha no programa são: 1) pegar o texto bruto das tabelas de viagens na TAM e 2) pegar a taxa de embarque das viagens.  
  
Uma vez que tenhamos o texto bruto da tabela, o resto do programa trabalha para limpá-lo, extraindo apenas os preços dos vôos diretos. Essa parte dempende de manipulação de texto e da capacidade de identificar padrões no texto (como siglras aeroportuárias BSB, GRU, GIG). Para entender como isso é feito, é preciso ter uma noção básica nos metacaracteres do R. A 4º semana do MOOC em *Data Cleaning* da Johns Hopkins University, disponível no Coursera, fornece uma boa base em como lidar com textos no R. Em especial, recomenda-se as aulas [3][3] e [4][4] da semana.  
  
Por fim, caso você não tenha nenhum conhecimento em R, sugere-se ver os vídeos das duas primeiras semanas do curso [R-programming][5], da Johns Hopkins University, também disponível no Coursera.

[1]: http://www.computerworld.com/article/2971265/application-development/how-to-drive-a-web-browser-with-r-and-rselenium.html
[2]: https://cran.rstudio.com/web/packages/RSelenium/
[3]: https://d3c33hcgiwev3.cloudfront.net/_b3fbe6648dadbb7be034ad5fb60fe438_04_02_regularExpressions.pdf?Expires=1463788800&Signature=OfL0JyB~mg6lY~wujE3ZCVGHZ2ubjLPFs8-aSSCgOy9M8~6I9LRVhvd-wUibfCJvJY-b6dJDOa5lGtJLCqMY62Z43dffRDv1vwTk-Xwc6XBr29Kc~tEhVECz7kfJPj5AUX6ByOW~Tm2JpSsRj~io~ohfp80EYt7cJKAhzpGAIaE_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A
[4]: https://d3c33hcgiwev3.cloudfront.net/_e8959793d0eb07f2390ff487700daf5f_04_03_regularExpressionsII.pdf?Expires=1463788800&Signature=Cl-JQ3u-93Spipah1Spjvy1TuhXdw-OE9uTABIlYXOpJGsVNtlmK7RIae0xD2GpWTgrMB2qM64oHxfoDnTI0e73mKsyEeamd4yBxOH91~0445bZOqjhTNmrBiX~DmqQYyTMqJ0q1MNop0MjCrAz89M1jnMupHeX3JcWjcKL06x4_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A
[5]: https://www.coursera.org/learn/r-programming/home/welcome
  
<br />

###**Funções:**  
####1. `getDadosTAM(origem, dataIda, destino, dataVolta)`:  
A função coleta os dados em formato bruto no site da TAM e devolve uma lista com dois elementos.
O primeiro é o texto bruto da tabela das viágens. O segundo elemento é a taxa de embarque.  
OBS: Infelizmente, a função só funciona se o browser ficar aberto na tela.  
  
**Argumentos:**  
  * *origem*: a cidade de saída no site da TAM, dado pelo código do aeroporto (e.g BSB) ou pelo nome da cidade (e.g. Brasília).  
  * *dataIda*: a data de ida da viagem, no formato "dd/mm/aaaa".  
  * *destino*: a cidade de chegada no site da TAM, dado pelo códgio do aeroporto (e.g BSB) ou pelo nome da cidade (e.g. Brasília).  
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
  * *n*: O número de linas da tabela. Ele deve ser maior que o maior vetor de preços coletado, caso contrário, haverá um erro.   
  
####4.`coletarTudo(cidades, ida, volta, n = 60)`:   
A função cria um documento excel em que cada aba é a coleta de preços de passagens de uma cidade, efetuada por `coletar()`.  
  
**Argumentos:**  
  * *cidades*: uma lista de cidades para realizar a coleta.  
  * *ida*: a data de ida da viagem, no formato "dd/mm/aaaa".  
  * *volta*: a data de volta da viagem, no formato "dd/mm/aaaa".  
  * *n*: O número de linas da tabela. Ele deve ser maior que o maior vetor de preços coletado, caso contrário, haverá um erro.  
  
###**Execução:**   
Primeiramente, criamos as cidades cujos preços das viagens devem ser coletados.
Depois criamos as listas de cidade sob responsabilidade de cada pessoa. Em seguida, criamos as datas de ida e volta das viagens.
Por fim, realizamos as coletas e salvamos os documentos excel criados no working directory (wd) do R.

