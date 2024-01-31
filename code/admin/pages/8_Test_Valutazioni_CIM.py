import streamlit as st
import os
import traceback
from datetime import datetime
import pandas as pd
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import base64
import datetime
import glob
import json
import openai
import os
import requests
import sys
import re
import lib.common as common

def read_field_from_cim(folder):
	from azure.core.credentials import AzureKeyCredential
	from azure.ai.formrecognizer import DocumentAnalysisClient
	endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
	key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
	model_id = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL_ID")
	model_id = "ldv6-neural"
	document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

	common.clean_session()

	with open(os.path.join('ldv', folder, "cim.jpg"),'rb') as f:
		poller = document_analysis_client.begin_analyze_document(model_id, document=f)
	result = poller.result()

	for idx, document in enumerate(result.documents):
		for name, field in document.fields.items():
			st.session_state[name] = field.value

	llm = AzureChatOpenAI(
		azure_endpoint=os.getenv("AZURE_OPENAI_BASE"), 
		api_key=os.getenv("AZURE_OPENAI_KEY"),
		api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
		max_tokens=1000, 
		temperature=0,
		deployment_name=os.getenv("AZURE_OPENAI_MODEL"),
		model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
		streaming=False
	)
	st.write("Estrazione mail: " + folder)
	my_bar = st.progress(0, text="Elaborazione dati con OCR e GPT")

	my_bar.progress(int((1) / 30 * 100), text="Elaborazione Mittente")
	st.session_state["box-01-clean"] = prompt_for_box("1", "Estrai dal testo solo la ragione sociale del mittente della CIM", st.session_state["box-01"], llm)

	my_bar.progress(int((2) / 30 * 100), text="Elaborazione Mittente Codice 1")
	st.session_state["box-02-clean"] = prompt_for_box("2", "Estrai dal testo un codice numerico che rappresenta il codice mittente della CIM", st.session_state["box-02"], llm)

	my_bar.progress(int((3) / 30 * 100), text="Elaborazione Mittente Codice 2")
	st.session_state["box-03-clean"] = prompt_for_box("3", "Estrai dal testo un codice numerico che rappresenta il codice mittente della CIM", st.session_state["box-03"], llm)

	my_bar.progress(int((4) / 30 * 100), text="Elaborazione Destinatario")
	st.session_state["box-04-clean"] = prompt_for_box("4", "Estrai dal testo solo la denominazione o ragione sociale", st.session_state["box-04"], llm)

	my_bar.progress(int((5) / 30 * 100), text="Elaborazione Destinatario Codice 1")
	st.session_state["box-05-clean"] = prompt_for_box("5", "Estrai dal testo un codice numerico che rappresenta il codice destinatario della CIM", st.session_state["box-05"], llm)

	my_bar.progress(int((6) / 30 * 100), text="Elaborazione Destinatario Codice 1")
	st.session_state["box-06-clean"] = prompt_for_box("6", "Estrai dal testo un codice numerico che rappresenta il codice destinatario della CIM", st.session_state["box-06"], llm)

	my_bar.progress(int((7) / 30 * 100), text="Elaborazione Luogo di consegna")
	st.session_state["box-10-clean"] = prompt_for_box("10", "Estrai solo le informazioni di un luogo di consegna della CIM", st.session_state["box-10"], llm)

	my_bar.progress(int((8) / 30 * 100), text="Elaborazione Luogo di consegna codice")
	st.session_state["box-11-clean"] = prompt_for_box("11", "Estrai dal testo un codice alfanumerico che rappresenta il codice di una stazione di destinazione della CIM", st.session_state["box-11"], llm)

	my_bar.progress(int((9) / 30 * 100), text="Elaborazione Destinazione")
	st.session_state["box-12-clean"] = prompt_for_box("12", "Estrai dal testo un codice numerico che rappresenta il codice di una stazione di destinazione della CIM", st.session_state["box-12"], llm)

	my_bar.progress(int((10) / 30 * 100), text="Elaborazione Destinazione Codice")
	st.session_state["box-13-clean"] = prompt_for_box("13", "Estrai dal testo le informazioni più importanti", st.session_state["box-13"], llm)

	my_bar.progress(int((11) / 30 * 100), text="Elaborazione box 14")
	st.session_state["box-14-clean"] = prompt_for_box("14", "Estrai dal testo un codice numerico che rappresenta un codice della CIM", st.session_state["box-14"], llm)

	my_bar.progress(int((12) / 30 * 100), text="Elaborazione box 16")
	st.session_state["box-16-clean"] = prompt_for_box("16", "Estrai le informazioni di un luogo di presa in carico della CIM", st.session_state["box-16"], llm)

	my_bar.progress(int((13) / 30 * 100), text="Elaborazione box 16 orario")
	st.session_state["box-16-orario-clean"] = prompt_for_box("16", "Interpreta la stringa come una data di presa in carico della CIM, eventualmente anche data e orario", st.session_state["box-16-orario"], llm)

	my_bar.progress(int((14) / 30 * 100), text="Elaborazione 17")
	st.session_state["box-17-clean"] = prompt_for_box("17", "Interpreta la stringa come una data di presa in carico della CIM, eventualmente anche data e orario", st.session_state["box-17"], llm)		

	my_bar.progress(int((15) / 30 * 100), text="Elaborazione 18")
	st.session_state["box-18-clean"] = prompt_for_box("18", "Estrai le informazioni dal testo", st.session_state["box-16"], llm)

	my_bar.progress(int((16) / 30 * 100), text="Elaborazione 19")
	st.session_state["box-19-1-clean"] = prompt_for_box("19", "Estrai le informazioni dal testo", st.session_state["box-19-1-clean"], llm)

	my_bar.progress(int((17) / 30 * 100), text="Elaborazione 19")
	st.session_state["box-19-2-clean"] = prompt_for_box("19", "Estrai le informazioni dal testo", st.session_state["box-19-1-clean"], llm)

	my_bar.progress(int((18) / 30 * 100), text="Elaborazione 24")
	st.session_state["box-24-clean"] = prompt_for_box("24", "Estrai un codice numerico che rappresenta il codice NHM della CIM.", st.session_state["box-24-clean"], llm)

	my_bar.progress(int((19) / 30 * 100), text="Elaborazione 25")
	st.session_state["box-25-clean"] = prompt_for_box("25", "Interpreta le informazioni dal testo, che sono dei pesi di vagoni. Estrai se lo trovi il totale della massa.", st.session_state["box-25-clean"], llm)

	my_bar.progress(int((21) / 30 * 100), text="Elaborazione 29")
	st.session_state["box-29-clean"] = prompt_for_box("29", "Interpreta le informazioni di luogo e data della CIM", st.session_state["box-29-clean"], llm)

	my_bar.progress(int((22) / 30 * 100), text="Elaborazione 49")
	st.session_state["box-49-clean"] = prompt_for_box("49", "Estrai dal testo un codice numerico composto eventualmente da più parti. ", st.session_state["box-49-clean"], llm)

	my_bar.progress(int((23) / 30 * 100), text="Elaborazione 57")
	st.session_state["box-57-clean"] = prompt_for_box("57", "Nel testo ci sono informazioni di trasporti, con indirizzi e percorsi. Estrai tutte le informazioni che riesci a leggere in modo ordinato. ", st.session_state["box-57-clean"], llm)

	my_bar.progress(int((24) / 30 * 100), text="Elaborazione 62 1")
	st.session_state["box-62-paese-clean"] = prompt_for_box("62", "Estrai dal testo un codice numerico di due cifre", st.session_state["box-62-paese"], llm)

	my_bar.progress(int((25) / 30 * 100), text="Elaborazione 62 2")
	st.session_state["box-62-stazione-clean"] = prompt_for_box("62", "Estrai dal testo un codice numerico che rappresenta un codice della etichetta della CIM. Se nel codice ci sono dei '-' non considerarli.", st.session_state["box-62-stazione"], llm)

	my_bar.progress(int((26) / 30 * 100), text="Elaborazione 62 3")
	st.session_state["box-62-impresa-clean"] = prompt_for_box("62", "Estrai dal testo un codice numerico che rappresenta un codice della etichetta della CIM. Se nel codice ci sono dei '-' non considerarli.", st.session_state["box-62-impresa"], llm)

	my_bar.progress(int((27) / 30 * 100), text="Elaborazione 63 4")
	st.session_state["box-62-spedizione-clean"] = prompt_for_box("62", "Estrai dal testo un codice numerico che rappresenta un codice della etichetta della CIM. Se nel codice ci sono dei '-' non considerarli.", st.session_state["box-62-spedizione"], llm)

	my_bar.progress(int((28) / 30 * 100), text="Elaborazione 62 luogo (da 29)")
	st.session_state["box-62-luogo-clean"] = prompt_for_box("29", "Estrai dal testo le sole informazioni del luogo.", st.session_state["box-29"], llm)

	my_bar.progress(int((29) / 30 * 100), text="Elaborazione 62 luogo (da 29)")
	st.session_state["box-62-data-clean"] = prompt_for_box("29", "Estrai dal testo le sole informazioni della data. Il risultato deve essere in questo formato: YYYYMMDD. Ignora eventualmente l'orario", st.session_state["box-29"], llm)

	
	import time
	folder_path = os.path.join('orpheus')
	file_list = os.listdir(folder_path)
	total_files = len(file_list)
	file_found = ""
 
	for index, file_name in enumerate(file_list):
		# Costruisci il percorso completo del file
		file_path = os.path.join(folder_path, file_name)
		# Verifica che sia un file e non una cartella
		if os.path.isfile(file_path):
			percent_complete = int((index + 1) / total_files * 100)
			my_bar.progress(percent_complete, text="Ricerca su file {}...".format(file_name))

			# Chiama la funzione per il file
			tree = ET.parse(file_path)
			root = tree.getroot()
			uic_country_codes = []
			station_codes = []
			carrier_codes = []
			consignment_numbers = []
			acceptance_dates = []
			
			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECN"):
				uic_country_code_node = ecn.find(".//AcceptancePoint/Point/Country/UICCountryCode")
				if uic_country_code_node is not None:
					uic_country_codes.append(uic_country_code_node.text)

			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECN"):
				station_code = ecn.find(".//AcceptancePoint/Station/Code")
				if station_code is not None:
					station_codes.append(station_code.text)

			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECNs"):
				carrier_code = ecn.find(".//ECNHeader/SendingCarrier")
				if carrier_codes is not None:
					carrier_codes.append(carrier_code.text)

			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECN"):
				consignment_number = ecn.find(".//AcceptancePoint/ConsignmentNumber")
				if consignment_numbers is not None:
					consignment_numbers.append(consignment_number.text)

			# Iterate through the ECN nodes
			for ecn in root.findall(".//ECN"):
				acceptance_date = ecn.find(".//AcceptancePoint/AcceptanceDate")
				if acceptance_date is not None:
					acceptance_dates.append(acceptance_date.text)
			
			data_ora_originale = acceptance_dates[0]
			# Analizzare la stringa nel formato originale
			# '%Y-%m-%dT%H:%M:%S%z' è il formato di analisi
			# '%Y' sta per anno, '%m' per mese, '%d' per giorno, '%H' per ore, '%M' per minuti, '%S' per secondi, '%z' per il fuso orario
			try:
				data_ora_obj = datetime.datetime.strptime(data_ora_originale, '%Y-%m-%dT%H:%M:%S%z')
				# Formattare l'oggetto datetime nel nuovo formato
				# '%Y%m%d-%H%M%S' è il formato di output
				data_ora_formattata = data_ora_obj.strftime('%Y%m%d')
			except ValueError as e:
				print(f"Errore nella conversione della data: {e} nel file {file_name}")

			if file_name == "ECTD.20231106_232258_875.xml":
				print("xml {0} e session {1} = {2}".format(uic_country_codes[0], st.session_state['box-62-paese-clean'], uic_country_codes[0] == st.session_state['box-62-paese-clean']))
				print("xml {0} e session {1} = {2}".format(station_codes[0], st.session_state['box-62-stazione-clean'], station_codes[0] == st.session_state['box-62-stazione-clean']))
				print("xml {0} e session {1} = {2}".format(carrier_codes[0], st.session_state['box-62-impresa-clean'], carrier_codes[0] == st.session_state['box-62-impresa-clean']))
				print("xml {0} e session {1} = {2}".format(consignment_numbers[0], st.session_state['box-62-spedizione-clean'], consignment_numbers[0].startswith(st.session_state['box-62-spedizione-clean'])))
				print("xml {0} e session {1} = {2}".format(data_ora_formattata, st.session_state['box-62-data-clean'], data_ora_formattata == st.session_state['box-62-data-clean']))

			# Confronto
			if st.session_state['box-62-paese-clean'] == uic_country_codes[0] \
				and st.session_state['box-62-stazione-clean'] == station_codes[0] \
				and st.session_state['box-62-impresa-clean'] == carrier_codes[0] \
			 	and consignment_numbers[0].startswith(st.session_state['box-62-spedizione-clean']) \
				and st.session_state['box-62-data-clean'] == data_ora_formattata:
				file_found = file_name

	if file_found:
	
		tree = ET.parse(file_path)
		root = tree.getroot()

		box_01_orfeus_values = []
		box_03_orfeus_values = []
		box_04_orfeus_values = []
		box_05_orfeus_values = []
		box_06_orfeus_values = []
		box_10_orfeus_values = []
		box_12_orfeus_values = []
		box_14_orfeus_values = []
		box_16_orfeus_values = []
	
		# Iterate through the ECN nodes
		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/Customers/Customer[@Type='CR']/Name")
			if node is not None:
				box_01_orfeus_values.append(node.text)
		st.session_state["box-01-orfeus"] = box_01_orfeus_values[0]

		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/Customers/Customer[@Type='CR']/CustomerCode")
			if node is not None:
				box_03_orfeus_values.append(node.text)
		st.session_state["box-03-orfeus"] = box_03_orfeus_values[0] 

		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/Customers/Customer[@Type='CE']/Name")
			if node is not None:
				box_04_orfeus_values.append(node.text)
		st.session_state["box-04-orfeus"] = box_04_orfeus_values[0]

		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/Customers/Customer[@Type='CE']/CustomerCode")
			if node is not None:
				box_05_orfeus_values.append(node.text)
		st.session_state["box-05-orfeus"] = box_05_orfeus_values[0]

		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/Customers/Customer[@Type='FPCE']/CustomerCode")
			if node is not None:
				box_06_orfeus_values.append(node.text)
		st.session_state["box-06-orfeus"] = box_06_orfeus_values[0] 

		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/DeliveryPoint/Point/Name")
			if node is not None:
				box_10_orfeus_values.append(node.text) 
		st.session_state["box-10-orfeus"] = box_10_orfeus_values[0]

		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/DeliveryPoint/Point/Code")
			if node is not None:
				box_12_orfeus_values.append(node.text)
		st.session_state["box-12-orfeus"] = box_12_orfeus_values[0]

		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/Tariff/ContractNumber")
			if node is not None:
				box_14_orfeus_values.append(node.text)
		st.session_state["box-14-orfeus"] = box_14_orfeus_values[0]

		for ecn in root.findall(".//ECNs"):
			node = ecn.find(".//ECN/AcceptancePoint/Point/Name")
			if node is not None:
				box_16_orfeus_values.append(node.text)
		st.session_state["box-16-orfeus"] = box_16_orfeus_values[0]

	# create a dataframe
	import pandas as pd

	# Example dataframes
	dati = [
		['Box 01', st.session_state['box-01'], st.session_state['box-01-clean'], st.session_state['box-01-orfeus']],
		['Box 02', st.session_state['box-02'], st.session_state['box-02-clean'], st.session_state['box-02-orfeus']],
		['Box 03', st.session_state['box-03'], st.session_state['box-03-clean'], st.session_state['box-03-orfeus']],
		['Box 04', st.session_state['box-04'], st.session_state['box-04-clean'], st.session_state['box-04-orfeus']],
		['Box 05', st.session_state['box-05'], st.session_state['box-05-clean'], st.session_state['box-05-orfeus']],
		['Box 06', st.session_state['box-06'], st.session_state['box-06-clean'], st.session_state['box-06-orfeus']],
		['Box 10', st.session_state['box-10'], st.session_state['box-10-clean'], st.session_state['box-10-orfeus']],
		['Box 11', st.session_state['box-11'], st.session_state['box-11-clean'], st.session_state['box-11-orfeus']],
		['Box 12', st.session_state['box-12'], st.session_state['box-12-clean'], st.session_state['box-12-orfeus']],
		['Box 13', st.session_state['box-13'], st.session_state['box-13-clean'], st.session_state['box-13-orfeus']],
		['Box 14', st.session_state['box-14'], st.session_state['box-14-clean'], st.session_state['box-14-orfeus']],
		['Box 16', st.session_state['box-16'], st.session_state['box-16-clean'], st.session_state['box-16-orfeus']],
		['Box 16-orario', st.session_state['box-16-orario'], st.session_state['box-16-orario-clean'], st.session_state['box-16-orario-orfeus']],
		['Box 17', st.session_state['box-17'], st.session_state['box-17-clean'], st.session_state['box-17-orfeus']],
		['Box 18', st.session_state['box-18'], st.session_state['box-18-clean'], st.session_state['box-17-orfeus']],
		['Box 19-1', st.session_state['box-19-1'], st.session_state['box-19-1-clean'], st.session_state['box-19-1-orfeus']],
		['Box 19-2', st.session_state['box-19-2'], st.session_state['box-19-1-clean'], st.session_state['box-19-1-orfeus']],
		['Box 25', st.session_state['box-25'], st.session_state['box-25-clean'], st.session_state['box-25-orfeus']],
		['Box 29', st.session_state['box-29'], st.session_state['box-29-clean'], st.session_state['box-29-orfeus']],
		['Box 49', st.session_state['box-49'], st.session_state['box-49-clean'], st.session_state['box-49-orfeus']],
		['Box 57', st.session_state['box-57'], st.session_state['box-57-clean'], st.session_state['box-57-orfeus']],
		['Box 62-paese', st.session_state['box-62-paese-clean'], st.session_state['box-01-clean'], ""],
		['Box 62-stazione', st.session_state['box-62-stazione-clean'], st.session_state['box-01-clean'], ""],
		['Box 62-impresa', st.session_state['box-62-impresa-clean'], st.session_state['box-01-clean'], ""],
		['Box 62-spedizione', st.session_state['box-62-spedizione-clean'], st.session_state['box-01-clean'], ""],
		['29 (luogo)', "", st.session_state['box-62-luogo-clean'], ""],
		['29 (data)', "", st.session_state['box-62-data-clean'], ""]
  	]
	
	# Crea il DataFrame
	df = pd.DataFrame(dati, columns=['Box', 'Estrazione OCR', 'Analisi GPT4', 'Orfeus se esistente'])
 
	return df

def prompt_for_box(numero_casella: str, descrizione_estrazione: str, box: str, llm: AzureChatOpenAI):
	prompt_base = """il testo delimitato da ### deriva da una scansione OCR di un modulo di trasporto ferroviario CIM internazionale. 
Il testo deriva da una casella che ha come numero iniziale {numero_casella} e che può contenere la descrizione della casella stessa.
###
{box}
###

{descrizione_estrazione}
- Non aggiungere altro alla risposta
- Se il testo inizia con il numero della casella non includerlo nella risposta
- Se non trovi nessun codice o nessuna informazione, scrivi "Non trovato"

Esempio 
- se la casella è la 29 e il testo è "29 800400500" la risposta sarà "80400500"
- se la casella è la 19 e il testo è "19 Ragione Sociale xxx yyy" la risposta sarà "Ragione Sociale xxx yyy"

Risposta:
"""
	response = ""
	output_parser = StrOutputParser()
	system_message = "Sei un assistente virtuale che aiuta ad estrarre informazioni da una testo analizzato con OCR da documenti CIM utilizzati nel trasporto ferroviario internazionale di merci."
	try:
		prompt = ChatPromptTemplate.from_messages([("system", system_message),("user", "{input}")])
		chain = prompt | llm | output_parser
		response = chain.invoke({"input": prompt_base.format(numero_casella=numero_casella, descrizione_estrazione=descrizione_estrazione, box=box)})
	except Exception as e:
		response = e
	return response

try:
	st.set_page_config(page_title="Mercitalia - Automazione LdV / RdS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Estrazione dati da email e allegati")
	st.sidebar.image(os.path.join('images','mercitalia.png'), use_column_width=True)
	load_dotenv()

	import streamlit_authenticator as stauth	
	import yaml
	from yaml.loader import SafeLoader

	with open('config.yaml') as file:
		config = yaml.load(file, Loader=SafeLoader)

	authenticator = stauth.Authenticate(
		config['credentials'],
		config['cookie']['name'],
		config['cookie']['key'],
		config['cookie']['expiry_days'],
		config['preauthorized']
	)

	if st.session_state["authentication_status"]:
		import pandas as pd
		import pandas as pd
		import streamlit as st
		from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
  
		ldv_folders = []
		dataframes = []
		for root, dirs, files in os.walk(os.path.join('ldv')):
			for name in dirs:
				df = read_field_from_cim(name)
				dataframes.append(df)
				st.dataframe(df)
		
		# Create a Pandas Excel writer using XlsxWriter as the engine
		with pd.ExcelWriter('ldv', 'output.xlsx', engine='xlsxwriter') as writer:
			i = 0
			for df in dataframes:
				df.to_excel(writer, sheet_name=ldv_folders[i])
			writer.save()

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())