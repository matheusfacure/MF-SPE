import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np

#Funções

# seleciona o indicador (nome) de uma drop box indicada por seletor único CSS
def select(indicadorCSS, nome):
	indicador = driver.find_element_by_css_selector(indicadorCSS)
	for option in indicador.find_elements_by_tag_name('option'):
		if option.text == nome:
			option.click()
			break
	return

# pega os valores na tabela da página do bcb
def getValues(page):
	startTable = page.find('var data1= [[')
	if startTable == -1:
		return None, 0
	endTable = page.find('ultima linha em branco', startTable)
	return re.findall('-?\d?\d?\d?\d\,\d\d', page[startTable:endTable])

# pega os valores dos IPs dados os cálculos especificados (Anual)
def scrapeIPsAnual(IPs, calculos, anos):
	
	# seleções padrão
	select('#indicador', 'Índices de preços')
	select('#periodicidade', 'Anual')

	# data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

	#  prepara dicironarios de data frames
	dfDic = {}

	# scrape
	for ip in IPs:
		
		# prepara data frame
		df = pd.DataFrame(index = anos, columns = calculos)
		df = df.fillna(0)

		for calc in calculos:
			driver.find_element_by_css_selector(IPs[ip]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir

			time.sleep(0.7) #previne bugs por internet lenta
			source = driver.page_source
			
			# se o tamanho do vetor de preço e da matriz divergir
			if(len(df[calc]) > len(anos)):
				diff = len(df[calc] - len(valueList))
				for n in range(0, diff):
					valueList.append(0)
			else:
				df[calc] = getValues(source)

			driver.back()
			time.sleep(0.7)
			driver.find_element_by_css_selector(IPs[ip]).click() #limpa seleção
			time.sleep(0.7)

		dfDic[ip] = df.T

	
	return dfDic

# pega o valor dos IPs acumulados 12 meses suavizado dados os cálculos
def scrapeIPsAc12MesesSuav(IPs, calculos):
	
	# seleções padrão
	indicador = 'Inflação acumulada para os próximos 12 meses - suavizada'
	select('#indicador', indicador)
	
	# data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	# prepara data frame
	IPsList = []
	for ip in IPs:
		IPsList.append(ip)

	df = pd.DataFrame(index = IPsList, columns = calculos)
	df = df.fillna(0)
	
	# scrape
	for calc in calculos:
		
		#inicia lista de cálculos
		valueList = []

		for ip in IPsList:
	
			driver.find_element_by_css_selector(IPs[ip]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir
			time.sleep(0.7) #previne bugs por internet lenta
			
			source = driver.page_source
			
			# adiciona valor do IP à lista do cálculo
			valueList.append(getValues(source)[0])

			driver.back()
			time.sleep(0.7)
			driver.find_element_by_css_selector(IPs[ip]).click() #limpa seleção
			time.sleep(0.7)

		df[calc] = valueList
	
	return df.T

# pega os valores dos IPs dados os cálculos especificados (Mensal)
def scrapeIPsMensal(IPs, calculos, meses, anos):
	
	#Seleções Padrão
	select('#indicador', 'Índices de preços')
	select('#periodicidade', 'Mensal')
	
	#Data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	# cria datas da coleta
	mesHj = datetime.datetime.now()
	str(mesHj)
	mesHj = int(mesHj.month)
	mesFinal = (mesHj + 18) % 13
	if(mesFinal < mesHj):
		anoFinal = 2
	else:
		anoFinal = 1

	# seleciona meses e anos
	select('#form4 > div.centralizado > table > tbody:nth-child(8) > tr >' \
		'td:nth-child(2) > select:nth-child(2)', anos[0])
	select('#mesReferenciaInicial', meses[mesHj - 1])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) > tr >' \
		'td:nth-child(4) > select:nth-child(2)', anos[anoFinal])
	select('#mesReferenciaFinal', meses[mesFinal - 1])


	#Prepara dicironarios de data frames
	dfDic = {}

	#prepara colunas das data frames
	for mes in range(mesHj - 1, mesHj + 17):
		meses.append(meses[mes % 12])

	#scrape
	for ip in IPs:
		
		
		df = pd.DataFrame(index = meses[12:], columns = calculos)
		df = df.fillna(0)

		for calc in calculos:
			driver.find_element_by_css_selector(IPs[ip]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir

			time.sleep(0.7) #previne bugs por internet lenta
			
			source = driver.page_source
			valueList = getValues(source) 
			
			# se o tamanho do vetor de preço e da matriz divergir
			if(len(df[calc]) > len(valueList)):
				diff = len(df[calc]) - len(valueList)
				for n in range(0, diff):
					valueList.append(0)
			else:
				df[calc] = valueList

			driver.back()
			time.sleep(0.7)
			driver.find_element_by_css_selector(IPs[ip]).click() #limpa seleção
			time.sleep(0.7)

		dfDic[ip] = df.T


	return(dfDic)

# pega os valores dos setores do PIB dados os cálculos especificados (Anual)
def scrapePIBAnual(setores, calculos, anos):
	
	# seleções padrão
	select('#indicador', 'PIB')
	select('#periodicidade', 'Anual')

	# data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

	# prepara dicironarios de data frames
	dfDic = {}

	# scrape
	for setor in setores:
		
		# prepara data frame
		df = pd.DataFrame(index = anos, columns = calculos)
		df = df.fillna(0)

		for calc in calculos:
			driver.find_element_by_css_selector(setores[setor]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir

			time.sleep(0.7) #previne bugs por internet lenta
			source = driver.page_source
			
			# se o tamanho do vetor de preço e da matriz divergir
			if(len(df[calc]) > len(anos)):
				diff = len(df[calc] - len(valueList))
				for n in range(0, diff):
					valueList.append(0)
			else:
				df[calc] = getValues(source)

			driver.back()
			time.sleep(0.7)
			driver.find_element_by_css_selector(setores[setor]).click()
			time.sleep(0.7)

		dfDic[setor] = df.T

	
	return dfDic

# pega os valores da produção industrial dados os cálculos e os anos
def scrapeIndustriaAnual(calculos, anos):

	# seleções padrão
	select('#indicador', 'Produção Industrial')
	select('#periodicidade', 'Anual')

	# data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

	# prepara data frame
	df = pd.DataFrame(index = anos, columns = calculos)
	df = df.fillna(0)
		
	for calc in calculos:
		select('#calculo', calc)
		driver.find_element_by_css_selector('#btnConsultar8').click() # ir
		time.sleep(0.7) #previne bugs por internet lenta
		
		valores = getValues(driver.page_source)
		
		if(len(valores) < len(anos)):
			diff = len(anos) - len(valores)
			for n in range(0,diff):
				valores.append(0)
		else:
			df[calc] = valores

		driver.back()
	
	return df.T

# pega os dados fiscais dados os cálculos e os anos
def scrapeFiscalAnual(calculos, anos):

	# seleções padrão
	select('#indicador', 'Fiscal')
	select('#periodicidade', 'Anual')

	# data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

	#dicinário de tabs 
	tabs = {'Resultado Primário':'#dijit_layout__TabButton_0',
		'Resultado Nominal':'#dijit_layout__TabButton_1',
		'Dívida Líquida':'#dijit_layout__TabButton_2'}

	# prepara data frame
	df = pd.DataFrame(index = anos, columns = [])
	df = df.fillna(0)
	
	for calc in calculos:
		select('#calculo', calc)
		driver.find_element_by_css_selector('#btnConsultar8').click() # ir
		time.sleep(0.7) #previne bugs por internet lenta
		
		for tab in tabs:
			driver.find_element_by_css_selector(tabs[tab]).click()

			valores = getValues(driver.page_source)
			
			if(len(valores) < len(anos)):
				diff = len(anos) - len(valores)
				for n in range(0,diff):
					valores.append(0)
			
			df[tab + '-' + calc] = valores
			
		driver.back()
	
	return df.T

# pega os dados da BP dados os cálculos e os anos
def scrapeBCAnual(calculos, anos):
	
	# seleções padrão
	select('#indicador', 'Balança Comercial')
	select('#periodicidade', 'Anual')

	# data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))
	
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

	#dicinário de tabs 
	tabs = {'Exportações':'#dijit_layout__TabButton_0',
		'Importações':'#dijit_layout__TabButton_1',
		'Saldo':'#dijit_layout__TabButton_2'}

	# prepara data frame
	df = pd.DataFrame(index = anos, columns = [])
	df = df.fillna(0)
	
	for calc in calculos:
		select('#calculo', calc)
		driver.find_element_by_css_selector('#btnConsultar8').click() # ir
		time.sleep(0.7) #previne bugs por internet lenta
		
		for tab in tabs:
			driver.find_element_by_css_selector(tabs[tab]).click()

			valores = getValues(driver.page_source)
			
			if(len(valores) < len(anos)):
				diff = len(anos) - len(valores)
				for n in range(0,diff):
					valores.append(0)
			
			df[tab + '-' + calc] = valores
			print(df.T)

		driver.back()
	
	return df.T


#Execução

site = "https://www3.bcb.gov.br/expectativas/publico/consulta/serieestatisticas"
driver = webdriver.Firefox() #Firefox() ou PhantomJS()
driver.get(site)

#cria lista de anos c/ ano atual e 4 anos à frente
anos = []
atual = datetime.datetime.strptime(time.strftime('%m/%d/%Y'), '%m/%d/%Y')
for ano in range(0,5):
	a = atual + datetime.timedelta(days = 366*ano)
	anos.append(a.strftime('%Y'))

# cria lista de meses
meses = ['janeiro', 'fevereiro', 'março','abril', 'maio', 'junho', 'julho',
	'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

# cria lista de cálculos
calculos = ['Mínimo', 'Mediana', 'Máximo', 'Média', 'Desvio padrão']

# cria dicionário de IPs
IPs = {'IGP-DI':'#grupoIndicePreco\:opcoes_0', 
	'IGP-M':'#grupoIndicePreco\:opcoes_1', 
	'INPC':'#grupoIndicePreco\:opcoes_2', 
	'IPA-DI':'#grupoIndicePreco\:opcoes_3',
	'IPA-M':'#grupoIndicePreco\:opcoes_4',  
	'IPCA':'#grupoIndicePreco\:opcoes_5', 
	'IPCA-15':'#grupoIndicePreco\:opcoes_6'}

# cria dicionário de setores do PIBs
setores = {'Agropecuaria':'#grupoPib\:opcoes_0',
	'Inducstrial':'#grupoPib\:opcoes_1',
	'Servico':'#grupoPib\:opcoes_2', 
	'Total':'#grupoPib\:opcoes_3'}

#Scrape 

#ipsAnual = scrapeIPsAnual(IPs, calculos, anos)
#for df in ipsAnual:
#	df_ip = ipsAnual[df]
#	arquivo = 'Focus (' + df + '-Anual)'
#	df_ip.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

#ipsMensal = scrapeIPsMensal(IPs, calculos[0:3], meses, anos)
#for df in ipsMensal:
#	df_ip = ipsMensal[df]
#	arquivo = 'Focus (' + df + '-Mensal)'
#	df_ip.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

#PIBAnual = scrapePIBAnual(setores, calculos, anos)
#for df in PIBAnual:
#	df_pib = PIBAnual[df]
#	arquivo = 'Focus (PIB-' + df + '-Anual)'
#	df_pib.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

#ac12MesesSuav =  scrapeIPsAc12MesesSuav(IPs, calculos[0:3])
#arquivo = 'Focus (Inflação Ac. 12 meses-Suavizada)'
#ac12MesesSuav.to_csv(arquivo + ".csv", sep = ';', index = True) 

#industria = scrapeIndustriaAnual(calculos[0:3], anos)
#arquivo = 'Focus (Produção Industrial)'
#industria.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

fiscal = scrapeFiscalAnual(calculos[0:3], anos)
arquivo = 'Focus (Fiscal)'
fiscal.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

BC = scrapeBCAnual(calculos[0:3], anos)
arquivo = 'Focus (Balança Comercial)'
BC.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

#driver.close()