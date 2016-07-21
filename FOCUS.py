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

# seleciona a data em que as series foram criadas
def selectDataDeCriacao():

	# data em que as séries foram feitas
	dataFinal = driver.find_element_by_css_selector('#tfDataInicial1')
	dataFinal.send_keys(time.strftime("%d/%m/%Y"))
	dataInicial = driver.find_element_by_css_selector('#tfDataFinal2')
	dataInicial.send_keys(time.strftime("%d/%m/%Y"))

# seleciona a data de projeção
def selectData(anos, meses = None):
	# seleciona os anos
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(2) > select', anos[0])
	select('#form4 > div.centralizado > table > tbody:nth-child(8) >' \
		'tr > td:nth-child(4) > select', anos[-1])

# pega os valores na tabela da página do bcb
def getValues(page, tabs = 1):

	startTable = page.find('var data1= [[')
	if startTable == -1:
		return None, 0
	endTable = page.find('grid structure', startTable)

	dataDeCriacao = re.findall('\d\d\/\d\d\/\d\d\d\d', page)[1]

	# se só uma tab na página
	if(tabs == 1):
		valores = re.findall('-?\d?\d?\d?\d\,\d\d', page[startTable:endTable])
	
		return valores, dataDeCriacao

	# se mais de uma aba na página
	else:
		
		#prepara dicionário de abas
		tabDic = {}

		# acha todos os valores
		todos = re.findall('-?\d?\d?\d?\d\,\d\d', page[startTable:endTable])
		nPorAba = len(todos) / tabs
		
		for tab in range(1,tabs + 1):
			tabDic['Aba' + str(tab)] = todos[:int(nPorAba)]
			todos = todos[int(nPorAba):]
		
		return tabDic, dataDeCriacao

# pega os valores dos IPs dados os cálculos especificados (Anual)
def scrapeIPsAnual(IPs, calculos, anos):
	
	# seleções padrão
	select('#indicador', 'Índices de preços')
	select('#periodicidade', 'Anual')

	selectDataDeCriacao()
	selectData(anos)

	#  prepara dicironarios de data frames
	dfDic = {}
	
	# scrape
	for ip in IPs:
		
		# prepara data frame
		df = pd.DataFrame(index = anos + ['Feito em'], columns = calculos)
		df = df.fillna(0)
		
		for calc in calculos:
			driver.find_element_by_css_selector(IPs[ip]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir

			time.sleep(0.7) #previne bugs por internet lenta
			source = driver.page_source
			valueList, dataDeCriacao = getValues(source)
			valueList.append(dataDeCriacao)
			
			# se o tamanho do vetor de preço e da matriz divergir
			if(len(df[calc]) > len(valueList)):
				for n in range(0, len(df[calc]) - len(valueList)):
					valueList.append('')
			
			df[calc] = valueList

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
	
	selectDataDeCriacao()
	
	# prepara data frame
	IPsList = []
	for ip in IPs:
		IPsList.append(ip)

	df = pd.DataFrame(index = IPsList + ['Feito em'], columns = calculos)
	df = df.fillna(0)
	
	# scrape
	for calc in calculos:
		
		#inicia lista de cálculos
		valueList = []
		criadaEm = []

		for ip in IPsList:
	
			driver.find_element_by_css_selector(IPs[ip]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir
			time.sleep(0.7) #previne bugs por internet lenta
			
			# adiciona valor do IP à lista do cálculo
			value, criadaEm = getValues(driver.page_source)
			valueList = valueList + value

			driver.back()
			time.sleep(0.7)
			driver.find_element_by_css_selector(IPs[ip]).click() #limpa seleção
			time.sleep(0.7)

		df[calc] = valueList + [criadaEm]

	return df.T

# pega os valores dos IPs dados os cálculos especificados (Mensal)
def scrapeIPsMensal(IPs, calculos, meses, anos):
	
	#Seleções Padrão
	select('#indicador', 'Índices de preços')
	select('#periodicidade', 'Mensal')
	
	selectDataDeCriacao()
	
	# cria datas da coleta
	mesHj = datetime.datetime.now()
	str(mesHj)
	anoHj = int(str(mesHj)[0:4])
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
	shift = 0
	for mes in range(mesHj - 1, mesHj + 17):
		meses.append(meses[mes % 12] + " " + str(anoHj + shift))
		if(meses[mes % 12] == 'dezembro'): # se trocar o ano
			shift = shift + 1

	#scrape
	for ip in IPs:
				
		df = pd.DataFrame(index = meses[12:] + ['Criada em'],
			columns = calculos)
		df = df.fillna(0)

		for calc in calculos:
			driver.find_element_by_css_selector(IPs[ip]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir

			time.sleep(0.7) #previne bugs por internet lenta
			
			valueList, criadaEm = getValues(driver.page_source)
			valueList.append(criadaEm)

			# se o tamanho do vetor de preço e da matriz divergir
			if(len(df[calc]) > len(valueList)):
				for n in range(0, len(df[calc]) - len(valueList)):
					valueList.append('')
			
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

	selectDataDeCriacao()
	selectData(anos)

	# prepara dicironarios de data frames
	dfDic = {}

	# scrape
	for setor in setores:
		
		# prepara data frame
		df = pd.DataFrame(index = anos + ['Criada em'], columns = calculos)
		df = df.fillna(0)

		for calc in calculos:
			driver.find_element_by_css_selector(setores[setor]).click()
			select('#calculo', calc)
			driver.find_element_by_css_selector('#btnConsultar8').click() # ir

			time.sleep(0.7) #previne bugs por internet lenta

			valueList, criadaEm = getValues(driver.page_source)
			valueList.append(criadaEm)
			
			# se o tamanho do vetor de preço e da matriz divergir
			if(len(df[calc]) > len(valueList)):
				for n in range(0, len(df[calc]) - len(valueList)):
					valueList.append('')
			
			df[calc] = valueList

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

	selectDataDeCriacao()
	selectData(anos)

	# prepara data frame
	df = pd.DataFrame(index = anos + ['Criada em'], columns = calculos)
	df = df.fillna(0)
		
	for calc in calculos:
		time.sleep(0.7) #previne bugs por internet lenta
		select('#calculo', calc)
		driver.find_element_by_css_selector('#btnConsultar8').click() # ir
		time.sleep(0.7)
		
		valueList, criadaEm = getValues(driver.page_source)
		valueList.append(criadaEm)

		if len(valueList) < len(df[calc]):
			for n in range(0, len(df[calc]) - len(valueList)):
				valores.append('')

		df[calc] = valueList
		driver.back()
	
	return df.T

# pega os preços monitorados dados os cálculos e os anos
def scrapeMonitoradosAnual(calculos, anos):
	
	select('#indicador', 'Preços Administrados por Contrato e Monitorados')
	select('#periodicidade', 'Anual')

	selectDataDeCriacao()
	selectData(anos)

	# prepara data frame
	df = pd.DataFrame(index = anos + ['Criada em'], columns = calculos)
	df = df.fillna(0)
		
	for calc in calculos:
		time.sleep(0.7) #previne bugs por internet lenta
		select('#calculo', calc)
		driver.find_element_by_css_selector('#btnConsultar8').click() # ir
		time.sleep(0.7)
		
		valueList, criadaEm = getValues(driver.page_source)
		valueList.append(criadaEm)

		if len(valueList) < len(df[calc]):
			for n in range(0, len(df[calc]) - len(valueList)):
				valores.append('')

		df[calc] = valueList
		driver.back()
	
	return df.T

# pega os dados fiscais dados os cálculos e os anos
def scrapeFiscalAnual(calculos, anos):

	# seleções padrão
	select('#indicador', 'Fiscal')
	select('#periodicidade', 'Anual')

	selectDataDeCriacao()
	selectData(anos)
	
	#dicinário de tabs 
	tabs = {'Aba1':'Resultado Primário',
		'Aba2':'Resultado Nominal',
		'Aba3':'Dívida Líquida',}

	# prepara data frame
	df = pd.DataFrame(index = anos + ['Criada em'], columns = [])
	df = df.fillna(0)
	
	for calc in calculos:
		select('#calculo', calc)
		driver.find_element_by_css_selector('#btnConsultar8').click() # ir
		time.sleep(0.7) #previne bugs por internet lenta
		
		valoresDic, criadaEm = getValues(driver.page_source, 3)
		for tab in tabs:
			for aba in valoresDic:
				df[tabs[aba] + '-' + calc] = valoresDic[aba] + [criadaEm]
	
		driver.back()
		time.sleep(1)

	return df.T

# pega os dados da BP dados os cálculos e os anos
def scrapeBCAnual(calculos, anos):
	
	# seleções padrão
	select('#indicador', 'Balança Comercial')
	select('#periodicidade', 'Anual')

	selectDataDeCriacao()
	selectData(anos)

	#dicinário de tabs 
	tabs = {'Aba1':'Exportações', 'Aba2':'Importações', 'Aba3':'Saldo'}

	# prepara data frame
	df = pd.DataFrame(index = anos + ['Criada em'], columns = [])
	df = df.fillna(0)
	
	for calc in calculos:
		select('#calculo', calc)
		driver.find_element_by_css_selector('#btnConsultar8').click() # ir
		time.sleep(0.7) #previne bugs por internet lenta
		
		valoresDic, criadaEm = getValues(driver.page_source, 3)
		for tab in tabs:
			for aba in valoresDic:
				df[tabs[aba] + '-' + calc] = valoresDic[aba] + [criadaEm]

		driver.back()
		time.sleep(1)

	return df.T

# pega os dados da BP dados os cálculos e os anos
def scrapeBPAnual(calculos, anos):
	
	# seleções padrão
	select('#indicador', 'Balanço de Pagamentos')
	select('#periodicidade', 'Anual')

	selectDataDeCriacao()
	selectData(anos)

	#dicinário de tabs 
	tabs = {'Aba1':'Conta Corrente', 'Aba2':'IDP'}

	# prepara data frame
	df = pd.DataFrame(index = anos + ['Criada em'], columns = [])
	df = df.fillna(0)
	
	for calc in calculos:
		select('#calculo', calc)
		driver.find_element_by_css_selector('#btnConsultar8').click() # ir
		time.sleep(0.7) #previne bugs por internet lenta
		
		valoresDic, criadaEm = getValues(driver.page_source, 2)
		for tab in tabs:
			for aba in valoresDic:
				df[tabs[aba] + '-' + calc] = valoresDic[aba] + [criadaEm]

		driver.back()
		time.sleep(1)

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
	'Industrial':'#grupoPib\:opcoes_1',
	'Servico':'#grupoPib\:opcoes_2', 
	'Total':'#grupoPib\:opcoes_3'}

#Scrape 

ipsAnual = scrapeIPsAnual(IPs, calculos, anos)
for df in ipsAnual:
	df_ip = ipsAnual[df]
	arquivo = 'Focus (' + df + '-Anual)'
	df_ip.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

time.sleep(1)
ipsMensal = scrapeIPsMensal(IPs, calculos[0:3], meses, anos)
for df in ipsMensal:
	df_ip = ipsMensal[df]
	arquivo = 'Focus (' + df + '-Mensal)'
	df_ip.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

time.sleep(1)
PIBAnual = scrapePIBAnual(setores, calculos, anos)
for df in PIBAnual:
	df_pib = PIBAnual[df]
	arquivo = 'Focus (PIB-' + df + '-Anual)'
	df_pib.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

time.sleep(1)
ac12MesesSuav =  scrapeIPsAc12MesesSuav(IPs, calculos[0:3])
arquivo = 'Focus (Inflação Ac. 12 meses-Suavizada)'
ac12MesesSuav.to_csv(arquivo + ".csv", sep = ';', index = True) 

time.sleep(1)
monitorados = scrapeMonitoradosAnual(calculos, anos)
arquivo = 'Focus (Monitorados)'
monitorados.to_csv(arquivo + ".csv", sep = ';', index = True) 

time.sleep(1)
industria = scrapeIndustriaAnual(calculos[0:3], anos)
arquivo = 'Focus (Produção Industrial)'
industria.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

time.sleep(1)
fiscal = scrapeFiscalAnual(calculos[0:3], anos)
arquivo = 'Focus (Fiscal)'
fiscal.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

time.sleep(1)
BC = scrapeBCAnual(calculos[0:3], anos)
arquivo = 'Focus (Balança Comercial)'
BC.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

time.sleep(1)
BP = scrapeBPAnual(calculos[0:3], anos)
arquivo = 'Focus (Balança de Pagamentos)'
BP.to_csv(arquivo + ".csv", sep = ';', date_format = '%Y', index = True)

driver.close()