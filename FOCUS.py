import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#Funções
def select(indicadorCSS, nome):
	indicador = driver.find_element_by_css_selector(indicadorCSS)
	for option in indicador.find_elements_by_tag_name('option'):
		if option.text == nome:
			option.click()
			break
	return

def getValues(page):
	startTable = page.find('var data1= [[')
	if startTable == -1:
		return None, 0
	endTable = page.find('ultima linha em branco', startTable)
	return re.findall('\d\,\d\d', page[startTable:endTable])


	   	
def MPAnual(anos):
	
	#cria vetor de cálculos
	calculos = ['Mínimo', 'Mediana', 'Máximo', 'Média', 'Desvio padrão']
	
	#seletor CSS dosindices [IPCA, IGP-DI, Câmbio]
	indicadores = ['#opcoesd_2', '#opcoesd_0', '#opcoesd_3'] 


	#Seleções Padrões
	#seleciona indicadores Top 5
	select('#indicador', 'Indicadores do Top 5')
	
	#seleciona ranking de médio prazo
	select('#tipoRanking', 'Médio Prazo Mensal')
	
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
		'tr > td:nth-child(4) > select', anos[1])


	#Seleções personalizadas
	for ind in indicadores:
		for calc in calculos:

			driver.find_element_by_css_selector(ind).click()
			select('#calculo', calc)
			if ind == '#opcoesd_3': #se o indicador for o câmbio
				select('#tipoDeTaxa', 'Fim de ano') #seleciona taxa fim de ano			
			driver.find_element_by_css_selector('#btnConsultar8').click()

			time.sleep(1)
			
			#Implementar funçao de extrair a série
			source = driver.page_source
			print(getValues(source))
			
			driver.back()
			time.sleep(1)

def LPAnual(anos):
	#cria vetor de cálculos
	calculos = ['Mínimo', 'Mediana', 'Máximo', 'Média', 'Desvio padrão']
	
	#seletor CSS dosindices [IPCA, IGP-DI, Câmbio]
	indicadores = ['#opcoesd_2', '#opcoesd_0', '#opcoesd_3'] 


	#Seleções Padrões
	#seleciona indicadores Top 5
	select('#indicador', 'Indicadores do Top 5')
	
	#seleciona ranking de médio prazo
	select('#tipoRanking', 'Longo Prazo')
	
	#sleciona periodicidade anual
	select('#periodicidade', 'Anual')
	
	#seleciona período que a projeção foi feita
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	#Seleciona começo e fim da série (ano atual e próximo)
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[2])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[4])


	#Seleções personalizadas
	for ind in indicadores:
		for calc in calculos:

			driver.find_element_by_css_selector(ind).click()
			select('#calculo', calc)
			if ind == '#opcoesd_3': #se o indicador for o câmbio
				select('#tipoDeTaxa', 'Fim de ano') #seleciona taxa fim de ano			
			driver.find_element_by_css_selector('#btnConsultar8').click()

			time.sleep(1)
			
			#Implementar funçao de extrair a série
			source = driver.page_source
			print(getValues(source))
			
			driver.back()
			time.sleep(1)



#Execução
site = "https://www3.bcb.gov.br/expectativas/publico/consulta/serieestatisticas"
driver = webdriver.Firefox()
driver.get(site)

#cria vetor de anos c/ ano atual e 4 anos à frente
anos = []
atual = datetime.datetime.strptime(time.strftime('%m/%d/%Y'), '%m/%d/%Y')
for ano in range(0,5):
	a = atual + datetime.timedelta(days = 366*ano)
	anos.append(a.strftime('%Y'))

print(anos)
LPAnual(anos)

