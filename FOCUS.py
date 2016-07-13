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

#Pega os valores dos IPs e dos cálculos especificados
def geralScrapeIPs(IPs, calculos, anos):
	
	#Seleções Padrão
	select('#indicador', 'Índices de preços')
	select('#periodicidade', 'Anual')
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

	#Prepara dicionários para armazenar valores
	inDic = {}
	for ip in IPs:
		inDic[ip] = {'Anos':anos}

	#scrape
	for ip in IPs:
		
		for calc in calculos:
			driver.find_element_by_css_selector(IPs[ip]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir

			time.sleep(0.5) #previne bugs por internet lenta
			source = driver.page_source
			
			inDic[ip][calc] = getValues(source) #atualiza dicionário

			driver.back()
			time.sleep(0.5)
			driver.find_element_by_css_selector(IPs[ip]).click() #limpa seleção
			time.sleep(0.5)
	return inDic

#Pega os valores dos indicadores TOP5 e dos calculos especificados
def TOP5ScrapeAnual(indicadores, calculos, anos):
	
	#Seleções Padrão
	select('#indicador', 'Indicadores do Top 5')
	select('#periodicidade', 'Anual')
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	

	ranking = ['Médio Prazo Mensal', 'Longo Prazo']
	
	for rk in ranking:
		select('#tipoRanking', rk)

		
		select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
			'tr > td:nth-child(2) > select', anos[0])
		select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
			'tr > td:nth-child(4) > select', anos[1])


		for ind in indicadores:
			driver.find_element_by_css_selector(indicadores[ind]).click()
			if(ind == "Câmbio"): #Se for a taxa de câmbio, seleciona fim de ano
				select('#tipoDeTaxa', 'Fim de ano')

			for calc in calculos:
				select('#calculo', calc)
				driver.find_element_by_css_selector('#btnConsultar8').click()
				time.sleep(0.5) #previne bugs por internet lenta
				source = driver.page_source

				print(getValues(source))

				driver.back()
				time.sleep(0.5)












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

dicionario = geralScrapeIPs(IPs, calculos, anos)
df = pd.DataFrame(dicionario)
print(df)
df.to_csv('teste.csv', sep=';')

#output para teste
#dicionarioteste = {'IPCA': {'Mediana': ['7,26', '5,40', '4,71', '4,50', '4,50'], 
#	'Anos': ['2016', '2017', '2018', '2019', '2020'],
#	'Média': ['7,27', '5,36', '4,85', '4,66', '4,60'],
#	'Desvio padrão': ['0,29', '0,47', '0,47', '0,39','0,42'],
#	'Mínimo': ['6,47', '4,50', '4,00', '3,80', '3,70'],
#	'Máximo': ['8,27', '7,48', '6,80', '6,00', '6,00']},
#	'IGP-DI': {'Mediana': ['9,20', '5,57', '5,05', '4,70', '4,55'],
#	'Anos': ['2016', '2017', '2018', '2019', '2020'],
#	'Média': ['9,08', '5,57', '5,21', '4,87', '4,79'],
#	'Desvio padrão': ['0,86', '0,57', '0,61', '0,49', '0,50'],
#	'Mínimo': ['6,10', '4,20', '4,00', '4,00', '4,00'],
#	'Máximo': ['0,73', '6,79', '6,80', '6,00', '6,00']}}


#TOP5

#cria dicinário de indicadores
#indicadores = {'IGP-DI':'#opcoesd_0', 'IPCA':'#opcoesd_2',
#	'Câmbio':'#opcoesd_3'}
#
#TOP5ScrapeAnual(indicadores, calculos, anos)