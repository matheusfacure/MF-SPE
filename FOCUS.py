import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np

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

#Pega os valores dos IPs e dos cálculos especificados (Anual)
def scrapeIPsAnual(IPs, calculos, anos):
	
	#Seleções Padrão
	select('#indicador', 'Índices de preços')
	select('#periodicidade', 'Anual')

	#Data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	

	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

	#Prepara dicironarios de data frames
	dfDic = {}

	#scrape
	for ip in IPs:
		
		#Prepara data frame
		df = pd.DataFrame(index = anos, columns = calculos)
		df = df.fillna(0)

		for calc in calculos:
			driver.find_element_by_css_selector(IPs[ip]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir

			time.sleep(0.5) #previne bugs por internet lenta
			source = driver.page_source
			
			df[calc] = getValues(source)

			driver.back()
			time.sleep(0.5)
			driver.find_element_by_css_selector(IPs[ip]).click() #limpa seleção
			time.sleep(0.5)

		dfDic[ip] = df.T

	
	return dfDic



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

calculos = ['Mínimo', 'Mediana', 'Máximo', 'Média', 'Desvio padrão']

#Geral

#IPs
IPs = {'IPCA':'#grupoIndicePreco\:opcoes_5',
	'IGP-DI':'#grupoIndicePreco\:opcoes_0'}

#ipsAnual = scrapeIPsAnual(IPs, calculos, anos)

#for df in ipsAnual:
#	df_ip = ipsAnual[df]
#	arquivo = 'Focus (' + df + ')'
#	df_ip.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

ipsMensal = scrapeIPsMensal(IPs, calculos, meses)


