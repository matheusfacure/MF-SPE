import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#Funções

#Seleciona o indicador (nome) de uma drop box indicada por seletor único CSS
def select(indicadorCSS, nome):
	indicador = driver.find_element_by_css_selector(indicadorCSS)
	for option in indicador.find_elements_by_tag_name('option'):
		if option.text == nome:
			option.click()
			break
	return

#pega os valores na tabela da página do bcb
def getValues(page):
	startTable = page.find('var data1= [[')
	if startTable == -1:
		return None, 0
	endTable = page.find('ultima linha em branco', startTable)
	return re.findall('\d\,\d\d', page[startTable:endTable])

#Seleciona na pagina de pequisa
def TOP5(ranking, periodicidade, anos):

	#seleciona indicadores Top 5
	select('#indicador', 'Indicadores do Top 5')
	
	#seleciona ranking de médio prazo
	select('#tipoRanking', ranking)
	
	#sleciona periodicidade anual
	select('#periodicidade', 'Anual')
	
	#seleciona período que a projeção foi feita
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	#Seleciona começo e fim da série (ano atual e próximo)
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

def TOPMPAnual(anos, ranking, indicadores, calculos):
	
	#Seleçiona primeiros dois anos e ranking Médio Prazo Mensal
	TOP5(ranking, 'Anual', anos)

	#Seleções personalizadas
	for ind in indicadores:
		for calc in calculos:

			driver.find_element_by_css_selector(ind).click()
			select('#calculo', calc)
			if ind == '#opcoesd_3': #se o indicador for o câmbio
				select('#tipoDeTaxa', 'Fim de ano') #seleciona taxa fim de ano
			driver.find_element_by_css_selector('#btnConsultar8').click()

			time.sleep(1) #previne bugs por internet lenta
			
			source = driver.page_source
			print(getValues(source))
			
			driver.back()
			time.sleep(1)


#Execução
site = "https://www3.bcb.gov.br/expectativas/publico/consulta/serieestatisticas"
driver = webdriver.Firefox()
driver.get(site)

#cria lista de anos c/ ano atual e 4 anos à frente
anos = []
atual = datetime.datetime.strptime(time.strftime('%m/%d/%Y'), '%m/%d/%Y')
for ano in range(0,5):
	a = atual + datetime.timedelta(days = 366*ano)
	anos.append(a.strftime('%Y'))

#cria lista de cálculos
calculos = ['Mínimo', 'Mediana', 'Máximo', 'Média', 'Desvio padrão']

#cria dicinário de indicadores
indicadores = ['#opcoesd_0','#opcoesd_2','#opcoesd_3']


print(anos)

TOPMPAnual(anos[0:2], 'Médio Prazo Mensal', indicadores, calculos)
TOPMPAnual(anos[2:], 'Longo Prazo', indicadores, calculos)


