#pacotes
library(RSelenium)
library(xlsx)

#ligando
setwd("~//Rproject//Passagens/")
checkForServer()
startServer()
mybrowser <- remoteDriver()
system("java -jar selenium-server-standalone-2.53.0.jar", wait = FALSE)
#se der erro, coloque o selenium-server-standalone-2.53.0 no wd e abra manualemnte clicando nele


#-------------------------------------------------------------------------------------------------------------------------
#deifnindo fun��es auxiliares


#fun��o que pega o c�gido fonte da p�gina, dados os daods da viagem
getPageGol <- function(origem,dataIda,destino,dataVolta) {
    #site
    gol <- "http://www.voegol.com.br/"
    #indo na gol
    mybrowser$navigate(gol)
    #lidando com pop-ups. Fazemos sempre duas tentativas para evitar erros por demora de carregamento
    try(popup <- mybrowser$findElement(using = 'css selector', ".encerrar" ), silent = T)
    try(popup <- mybrowser$findElement(using = 'css selector', ".encerrar" ), silent = T)
    try(popup$clickElement(), silent = T) #popup 1
    try(popup <- mybrowser$findElement(using = 'css selector', ".fsrDeclineButton" ), silent = T)
    try(popup <- mybrowser$findElement(using = 'css selector', ".fsrDeclineButton" ), silent = T)
    try(popup$clickElement(), silent = T) #popup 2
    OrigemG <- mybrowser$findElement(using = 'css selector', "#ctl00_PlaceHolderMain_origem" )
    DestinoG <- mybrowser$findElement(using = 'css selector', "#ctl00_PlaceHolderMain_para")
    dataSaidaG <- mybrowser$findElement(using = 'css selector', "#ida")
    dataVoltaG <- mybrowser$findElement(using = 'css selector', "#volta")
    adultosframe <- mybrowser$findElement(using = 'id', "adultos")
    #pesquisando viagem
    try(OrigemG$clearElement(), silent = T)#limpando elemento
    try(OrigemG$clearElement(), silent = T)#limpando elemento
    OrigemG$sendKeysToElement(list(origem)) #escolhendo origem
    autoCompOrigem <- mybrowser$findElement(using = 'css selector',"#autocomplete-de strong" )
    autoCompOrigem$clickElement()
    DestinoG$clearElement()#limpando elemento
    DestinoG$sendKeysToElement(list(destino)) #escolhendo destino
    autoCompDest <- mybrowser$findElement(using = 'css selector',"#autocomplete-para strong" )
    autoCompDest$clickElement()
    dataSaidaG$clearElement()#limpando elemento
    dataSaidaG$sendKeysToElement(list(dataIda)) #escolhendo data de sa�da
    dataVoltaG$clearElement()#limpando elemento
    dataVoltaG$sendKeysToElement(list(dataVolta)) #escolhendo data de volta
    adultosframe$clickElement()
    adultosframe$sendKeysToElement(list( key = "up_arrow" )) #limpando elemento
    adultosframe$sendKeysToElement(list( key = "up_arrow" )) #limpando elemento
    adultosframe$sendKeysToElement(list( key = "up_arrow" )) #limpando elemento
    adultosframe$sendKeysToElement(list( key = "down_arrow" )) #escolhendo 1 adulto

    
    botaoIrG <- mybrowser$findElement(using = 'css selector', "#bt-disparo")
    botaoIrG$clickElement()
    try(mybrowser$acceptAlert(), silent = T)
    #recolhendo c�digo fonte da p�gina
    page <- mybrowser$getPageSource(header = TRUE)
    page <- page[[1]]
    return(invisible(page))
  
}

#pega o pr�ximo Voo Direto no c�digo da p�gina
getNextVDs <- function(page) {
    #c�digo HTML que especifica o in�cio dos voos diretos
    id_VDStart <- '<span class="connectionScalesNumber"><strong style="display:none">0</strong><span><span class="plusBus">'
    #c�digo HTML que especifica o fim  dos voos diretos
    id_VDEnd <- '<div class="infoGrid bgGrid taxaInfo">'
    
    VDStart <- regexpr(id_VDStart, page)[[1]] #acha a posi��o inicial do primeiro voo direto na p�gina
    VDEnd <- regexpr(id_VDEnd, substr(page, VDStart, nchar(page)))[[1]]+VDStart #acha a posi��o final do primeiro voo direto na p�gina 
    VD <- substr(page, VDStart, VDEnd) #recorta o primeiro voo direto da p�gina
    if(VDStart == -1){
        return(list(-1, -1)) #caso n�o ache voos diretos
        } else {
            #caso ache um voo direto, retorna o c�digo fonte do voo direto e a posi��o final desse voo.
            #A posi��o final � importante para continuar a persquisa pegando os pr�ximos voos diretos,
            #lembrando que essa fun��o s� pega o pr�ximo voo direto na p�gina.
            return(list(VD, VDEnd)) 
        }
}

#pega todos os voos diretos do c�digo da p�gina
getAllVDs <- function(page){
    SEP <- "<AQUI_SE_SEPARA_UM_VOO_DIRETO>" #cirando separador
    AllVds <- c() #inicia vetor vazio de voos diretos
    
    #iterando pelo texto da p�gina
    while (TRUE) {
        VD <- getNextVDs(page)[[1]] #pega o pr�ximo voo direto na p�gina
        if(VD == -1){
            break() #sai do loop apenas quando n�o achar mais voos diretos na p�gina
            }
        AllVds <- paste(AllVds, VD, sep = SEP ) #adicioa no voo direto ao vetor de voos diretos
        page <- substr(page, getNextVDs(page)[[2]], nchar(page)) #atualiza a p�gina descartando o in�cio at� a posi��o final do voo direto 
        }
    return(AllVds) #retorna o c�digo fonte de todos os voos diretos
}


#pega o pr�ximo preco no c�digo
getNextPrice <- function(page){
    #Se a p�gina n�o for for um texto, retorna (-1,-1)
    #Essa fun��o trabalha com o texto dos voos diretos, que retorna (-1,-1) caso n�o encontra voos diretos.
    #Por isso, caso n�o haja voos diretos, getNextPrice ir� receber (-1.-1) e retornar� (-1,-1) tamb�m.
    if(is.character(page) == FALSE){
        return(list(-1, -1))
        } else {
            #O algor�tmo abaixo � an�logo ao usado para encontrar o pr�ximo voo direto (getNextVDs)
            priceCod <- regexpr('<span class="fareValue">', page)[[1]]
            if (priceCod == -1) {
                return(list(-1, -1))
                } else {
                    priceStart <- regexpr('    R', substr(page, priceCod, nchar(page)))[1]+priceCod+6
                    priceEnd <- regexpr('</span>', substr(page, priceStart, nchar(page)))[1]+priceStart-2
                    price <- substr(page, priceStart, priceEnd) #converter pre�o em num�rico
                    return( list(price, priceEnd) )
                }
        }
}

#pega a pr�xima taxa associada a cada pre�o
getNextTax <- function(page){
    if(is.character(page) == FALSE){
        return(list(-1, -1))
        } else {
            priceCod <- regexpr('<span class="fareValue">', page)[[1]]
            if (priceCod == -1) {
                return(list(-1, -1))
                } else {
                    taxStart <- regexpr('data-othertaxes=\"', substr(page, priceCod, nchar(page)))[1]+priceCod+nchar('data-othertaxes=\"')-1
                    taxEnd <- regexpr('\"', substr(page, taxStart, nchar(page)))[1]+taxStart-2
                    tax <- substr(page, taxStart, taxEnd)
                    return( list(tax, taxEnd) )
                }
        }
}

#pega todos os precos e taxas da p�gina retorna um vetor com todos os pre�os e taxas
getAllCosts <- function(page){
    VDs <- getAllVDs(page) # pega toddos os voos diretos no c�digo fonte da p�gina
    allCosts <- c() #inicia vetor vazio de todos os custos
    nomes <- c() #inicia vetor vazio de nomes
    
    #itera pelo c�digo fonte dos voos diretos
    while (TRUE) {
        p <- getNextPrice(VDs)[[1]] #pega o primeiro pre�o dos voos diretos
        if(p == -1){
            break() #Se n�o houver mair pre�os, sai do loop
            } 
        t <- getNextTax(VDs)[[1]] #pega a primeira taxa dos voos diretos
        cost <- c(p,t) #junta pre�o e taxa em um vetor de custos
        allCosts <- c(allCosts, cost) #adicona o vetor de custos ao vetor de todos os cursos
        nomes <- c(nomes, "preco", "taxa") #atualiza o vetor de nomes
        VDs <- substr(VDs, getNextPrice(VDs)[[2]], nchar(VDs)) #recorta os voos diretos excluindo o iterado nesse est�gio
        }
    names(allCosts) <- nomes #nomeia o vetor de todos os custos com o vetor de nomes
    return(allCosts)
}

#coletar
coletar <- function(cidade, ida, volta, n=80){
    tabela <- rep.int(c("Preco"), n) #inicia a tabela com um tamanho m
    cnames <- c("1") #vetor de nome das colunas.
    
    #iterando pelas origens das viagens para as cidades
    for(origem in cidade[[2]]){
        #pega a o c�digo fonte ta p�gina
        page <- getPageGol(origem = origem , destino = cidade[[1]]  , dataIda = ida, dataVolta = volta)
        custos <- getAllCosts(page) #pega os custos dos voos diretos da p�gina
        if(length(custos)>n){
            print("Tamanho dos custos maior que a tabela!!! Use uma tabela maior.")
            return() #se o vetor de cusotos for maior que a tabela, retorna um erro
        }
        
        #caso exista voos diretos
        if(!is.null(custos)){
            
            #pegando os precos no vetor de custos
            precos <- unname(custos[(names(custos) == "preco")]) #pga apenas os pre�os do vetos de custos
            length(precos) <- n #deixa o vetor de pre�os do mesmo tamanho que a tabela
            tabela <- cbind(tabela, precos) #adiciona o vetor de pre�os � tabela 
            cnames <- c(cnames, origem) #atualiza o vetor de nomes das colunas
            
            #pegando a m�dia das taxas
            taxas <- format(mean(as.numeric(gsub(",",".",custos[(names(custos) == "taxa")]))), decimal.mark = "," )
            length(taxas) <- n #deixa o vetor de taxas do mesmo tamanho que a tabela
            tabela <- cbind(tabela, taxas) #adiciona o vetor de taxa � tabela 
            cnames <- c(cnames, paste(origem, "Taxa", sep ="_" )) #
            
        }
        
        #caso n�o exita voos diretos
        if(is.null(custos)){
            custos <- "Sem VD" #avisa no vetor de custos que n�o h� voo direto
            length(custos) <- n #deixa o vetor de custos do tamanho ta dabela
            tabela <- cbind(tabela, custos) #adiciona o vetor de custos � tabela
            cnames <- c(cnames , origem) #atualiza o vetor de nomes das colunas
            } 
    }
    
    #terminada a itera��o
    colnames(tabela) <- cnames #nomeia as colunas da tebela
    return(tabela)
}

coletarTudo <- function(cidades,ida,volta,n){
    mybrowser$open() #abre o browser
    i <-  1
    wb <- createWorkbook() #cira um documento excel
    #Itera pelas cidades de cada pessoa enquanto
    while(i <= length(cidades)){
        tabela <- coletar(cidades[[i]],ida,volta,n) #cira uma tabela para a cidade
        sheet <- createSheet(wb, sheetName = cidades[[i]][[1]]) #cria um planilha excel com o nome da cidade
        addDataFrame(tabela, sheet, col.names = T, row.names = F) #adiciona � planlha ao documento excel
        i <- i+1 #atualiza o est�gio da itera��o
    }
    #retorna o documento excel
    return(wb)
}


#-------------------------------------------------------------------------------------------------------------------------
#fazendo a coleta


#Matheus
salvador <- list("SSA", c("GIG","CNF", "REC", "GRU", "BSB", "Fortaleza", "VIX"))
natal <- list("Natal", c("GIG", "GRU", "Fortaleza", "SSA"))
manaus <- list("MAO", c("GIG", "GRU", "BSB", "Belem"))
matheus <- list(salvador, natal, manaus)

#Luiz
curitiba <- list("CWB", c("GIG", "POA","GRU", "BSB"))
florianopolis <- list("FLN", c("GIG", "POA", "GRU", "BSB"))
fortaleza <- list("Fortaleza", c("GIG", "REC", "GRU", "BSB", "Belem", "SSA"))
luiz <- list(curitiba, florianopolis, fortaleza)

#Odete
rio <- list("GIG", c("POA", "BHZ", "REC","GRU", "BSB", "Belem", "Fortaleza","CWB", "SSA", "GYN", "VIX", "CGR"))
odete <- list(rio)


#luiz
saopaulo <- list("GRU", c("GIG", "POA", "CNF", "REC", "BSB", "Belem", "Fortaleza", "CWB", "SSA", "GYN", "VIX", "CGR"))
vicente <- list(saopaulo)

#datas
ida <- "27/08/2016"
volta <- "04/09/2016"


#salvando excel e testando o tempo do procedimento

start.time <- Sys.time()

wb1 <- coletarTudo(luiz, ida, volta, 60) #cria o documento excel da pesquisa
saveWorkbook(wb1, "coletaGOLLuiz.xlsx") #exporta o documento excel para fora do R, com o nome especificado e no wd

wb2 <- coletarTudo(matheus, ida, volta, 60) #cria o documento excel da pesquisa
saveWorkbook(wb2, "coletaGOLMatheus.xlsx") #exporta o documento excel para fora do R, com o nome especificado e no wd

wb3 <- coletarTudo(odete, ida, volta, 60) #cria o documento excel da pesquisa
saveWorkbook(wb3, "coletaGOLOdete.xlsx") #exporta o documento excel para fora do R, com o nome especificado e no wd

wb4 <- coletarTudo(vicente, ida, volta, 60) #cria o documento excel da pesquisa
saveWorkbook(wb4, "coletaGOLVicente.xlsx")

end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken #motra o tempo demorado
