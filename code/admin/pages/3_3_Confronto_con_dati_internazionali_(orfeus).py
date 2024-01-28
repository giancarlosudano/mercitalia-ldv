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

def search_orfeus(my_bar):
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
	return file_found

def get_orfeus_data(file_name):
	file_path = os.path.join('orpheus', file_name)
    
	tree = ET.parse(file_path)
	root = tree.getroot()

	box_01_orfeus_values = []
	box_10_orfeus_values = []

	# Iterate through the ECN nodes
	for ecn in root.findall(".//ECNs"):
		node = ecn.find(".//ECN/Customers/Customer[@Type='CR']/Name")
		if node is not None:
			box_01_orfeus_values.append(node.text)
	st.session_state["box-01-orfeus"] = box_01_orfeus_values[0]
 
	# st.session_state["box-02-orfeus"] = "" # NA
 
	for ecn in root.findall(".//ECNs"):
		node = ecn.find(".//ECN/Customers/Customer[@Type='CR']/CustomerCode")
		if node is not None:
			box_01_orfeus_values.append(node.text)
	st.session_state["box-03-orfeus"] = "" # ECNs/ECN/Customers/Customer type "CR"/CustomerCode
 
	st.session_state["box-04-orfeus"] = "" # ECNs/ECN/Customers/Customer type "CE"/Name
	st.session_state["box-05-orfeus"] = "" # ECNs/ECN/Customers/Customer type "CE"/CustomerCode
	st.session_state["box-06-orfeus"] = "" # ECNs/ECN/Customers/Customer type "FPCE"/CustomerCode


	for ecn in root.findall(".//ECNs"):
		node = ecn.find(".//ECN/DeliveryPoint/Point/Name")
		if node is not None:
			box_10_orfeus_values.append(node.text) 
	st.session_state["box-10-orfeus"] = box_10_orfeus_values[0]
	# st.session_state["box-11-orfeus"] = "" #NA

	for ecn in root.findall(".//ECNs"):
		node = ecn.find(".//ECN/DeliveryPoint/Point/Name")
		if node is not None:
			box_10_orfeus_values.append(node.text)
	st.session_state["box-12-orfeus"] = "" # ENCs/ECN/DeliveryPoint/Point/Code
 
	# st.session_state["box-13-orfeus"] = "" #NA
	st.session_state["box-14-orfeus"] = "" # ECNs/ECN/Tariff/ContractNumber
	st.session_state["box-16-orfeus"] = "" # ENCs/ECN/AcceptancePoint/Point/Name
	# st.session_state["box-16-orario-orfeus"] = "" #NA
	# st.session_state["box-17-orfeus"] = "" 
	# st.session_state["box-18-orfeus"] = ""
	# st.session_state["box-19-1-orfeus"] = ""
	# st.session_state["box-19-2-orfeus"] = ""
	# st.session_state["box-24-orfeus"] = ""
	# st.session_state["box-25-orfeus"] = ""
	# st.session_state["box-49-orfeus"] = ""
	# st.session_state["box-57-orfeus"] = ""

	# Iterate through the ECN nodes
	# for ecn in root.findall(".//ECN"):
	# 	uic_country_code_node = ecn.find(".//AcceptancePoint/Point/Country/UICCountryCode")
	# 	if uic_country_code_node is not None:
	# 		uic_country_codes.append(uic_country_code_node.text)

	# # Iterate through the ECN nodes
	# for ecn in root.findall(".//ECN"):
	# 	station_code = ecn.find(".//AcceptancePoint/Station/Code")
	# 	if station_code is not None:
	# 		station_codes.append(station_code.text)

	# # Iterate through the ECN nodes
	# for ecn in root.findall(".//ECNs"):
	# 	carrier_code = ecn.find(".//ECNHeader/SendingCarrier")
	# 	if carrier_codes is not None:
	# 		carrier_codes.append(carrier_code.text)

	# # Iterate through the ECN nodes
	# for ecn in root.findall(".//ECN"):
	# 	consignment_number = ecn.find(".//AcceptancePoint/ConsignmentNumber")
	# 	if consignment_numbers is not None:
	# 		consignment_numbers.append(consignment_number.text)

	# # Iterate through the ECN nodes
	# for ecn in root.findall(".//ECN"):
	# 	acceptance_date = ecn.find(".//AcceptancePoint/AcceptanceDate")
	# 	if acceptance_date is not None:
	# 		acceptance_dates.append(acceptance_date.text)
   
	return

try:
	st.set_page_config(page_title="Mercitalia - Automazione LDV / RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Confronto con dati internazionali (Orfeus)")
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
		st.image(os.path.join('images','Slide4.JPG'), use_column_width=True)
		st.write("""
### Descrizione
In questa fase il sistema a partire dai dati di etichetta della CIM cerca tra i dati del sistema Orfeus (di cui è stato fornito una esportazione su range temporale)
Se il file Orfeus XML corrispondente alle informazioni di etichetta esiste allora vengono catturati tutti i dati necessari dal file per sostituire eventuali campi mancanti o di scansione non perfetta.
Viene data priorità ai dati di Orfeus rispetto a quelli di CIM.
### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa. La ricerca tra i file di Orfeus è effettuata mediante tradizionale ricerca XML di libreria
- **Azure Blob Storage**: Servizio di storage per file/blob ad alta scalabilità per la lettura dei file di Orfeus
""")	
		# Recupero Dati CIM

		st.info("Dati estratti dalla CIM")

		st.text_input("Codice Paese", key="ident_paese_1", value=st.session_state["box-62-paese-clean"], disabled=True)
		st.text_input("Codice Stazione", key="ident_stazione_1", value=st.session_state["box-62-stazione-clean"], disabled=True)
		st.text_input("Codice Impresa", key="ident_impresa_1", value=st.session_state["box-62-impresa-clean"], disabled=True)
		st.text_input("Codice Spedizione", key="ident_spedizione_1", value=st.session_state["box-62-spedizione-clean"], disabled=True)
		st.text_input("Luogo", key="ident_luogo_1", value=st.session_state["box-62-luogo-clean"], disabled=True)
		st.text_input("Data", key="ident_data_1", value=st.session_state["box-62-data-clean"], disabled=True)
  
		my_bar = st.progress(0, text="Ricerca su dati Orfeus...")
		file_found = search_orfeus(my_bar)
		st.toast("File trovato: {}".format(file_found))

		get_orfeus_data(file_found)
  
		colbox1_1, colbox1_2 = st.columns([1,1])	
		with colbox1_1:
			st.text_area("(1) Mittente (clean)", value=st.session_state["box-01-clean"], disabled=True, height=150, key="box1_1")
		with colbox1_2:
			st.text_area("(1) Mittente (Orfeus)", value=st.session_state["box-01-orfeus"], height=150, key="box1_2")

		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(2) Mittente Codice 1 (clean)", value=st.session_state["box-02-clean"], disabled=True, height=100, key="box2_1")
		with colbox2_2:
			st.text_area("(2) Mittente Codice 1 (Orfeus)", value=st.session_state["box-02-orfeus"], height=100, key="box2_2")

		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(3) Mittente Codice 2 (clean)", value=st.session_state["box-03-clean"], disabled=True, height=100, key="box3_1")
		with colbox2_2:
			st.text_area("(3) Mittente Codice 2 (Orfeus)", value=st.session_state["box-03-orfeus"], height=100, key="box3_2")

		colbox1_1, colbox1_2 = st.columns([1,1])	
		with colbox1_1:
			st.text_area("(4) Destinatario (clean)", value=st.session_state["box-04-clean"], disabled=True, height=150, key="box4_1")
		with colbox1_2:
			st.text_area("(4) Destinatario (Orfeus)", value=st.session_state["box-04-orfeus"], height=150, key="box4_2")
		
		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(5) Destinatario Codice 1 (clean)", value=st.session_state["box-05-clean"], disabled=True, height=100, key="box5_1")
		with colbox2_2:
			st.text_area("(5) Destinatario Codice 1 (Orfeus)", value=st.session_state["box-05-orfeus"], height=100, key="box5_2")

		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(6) Destinatario Codice 2 (clean)", value=st.session_state["box-06-clean"], disabled=True, height=100, key="box6_1")
		with colbox2_2:
			st.text_area("(6) Destinatario Codice 2 (Orfeus)", value=st.session_state["box-06-orfeus"], height=100, key="box6_2")

		colbox10_1, colbox10_2= st.columns([1,1])
		with colbox10_1:
			st.text_area("(10) Luogo di Consegna (clean)", value=st.session_state["box-10-clean"], disabled=True, height=100, key="box10_1")
		with colbox10_2:
			st.text_area("(10) Luogo di Consegna (Orfeus)", value=st.session_state["box-10-orfeus"], height=100, key="box10_2")

		colbox11_1, colbox11_2 = st.columns([1,1])
		with colbox11_1:
			st.text_area("(11) Codice Luogo Consegna 1 (clean)", value=st.session_state["box-11-clean"], disabled=True, height=100, key="box11_1")
		with colbox11_2:
			st.text_area("(11) Codice Luogo Consegna 1 (Orfeus)", value=st.session_state["box-11-orfeus"], height=100, key="box11_2")
  
		colbox12_1, colbox12_2 = st.columns([1,1])
		with colbox11_1:
			st.text_area("(12) Codice Luogo Consegna 2 (clean)", value=st.session_state["box-12-clean"], disabled=True, height=100, key="box12_1")
		with colbox11_2:
			st.text_area("(12) Codice Luogo Consegna 2 (Orfeus)", value=st.session_state["box-12-orfeus"], height=100, key="box12_2")

		colbox13_1, colbox13_2 = st.columns([1,1])
		with colbox13_1:
			st.text_area("(13) Condizioni commerciali (clean)", value=st.session_state["box-13-clean"], disabled=True, height=100, key="box13_1")
		with colbox13_2:
			st.text_area("(13) Condizioni commerciali (Orfeus)", value=st.session_state["box-13-orfeus"], height=100, key="box13_2", )

		colbox14_1, colbox14_2= st.columns([1,1])
		with colbox14_1:
			st.text_area("(14) Codice Contratto (clean)", value=st.session_state["box-14-clean"], disabled=True, height=100, key="box14_1")
		with colbox14_2:
			st.text_area("(14) Codice Contratto (Orfeus)", value=st.session_state["box-14-orfeus"], height=100, key="box14_2")

		colbox16_1, colbox16_2= st.columns([1,1])
		with colbox16_1:
			st.text_area("(16) Origine (clean)", value=st.session_state["box-16-clean"], disabled=True, height=100, key="box16_1")
		with colbox16_2:
			st.text_area("(16) Origine (Orfeus)", value=st.session_state["box-16-orfeus"], height=100, key="box16_2")
  
		colbox16_1_orario, colbox16_2_orario= st.columns([1,1])
		with colbox16_1_orario:
			st.text_area("(16) Origine Data (clean)", value=st.session_state["box-14-clean"], disabled=True, height=100, key="box16_orario_1")
		with colbox16_2_orario:
			st.text_area("(16) Orogine Data (Orfeus)", value=st.session_state["box-14-orfeus"], height=100, key="box16_orario_2")

		colbox17_1, colbox17_2= st.columns([1,1])
		with colbox17_1:
			st.text_area("(17) Origine Codice (clean)", value=st.session_state["box-17-clean"], disabled=True, height=100, key="box17_1")
		with colbox17_2:
			st.text_area("(17) Origine Codice (Orfeus)", value=st.session_state["box-17-orfeus"], height=100, key="box17_2")

		colbox18_1, colbox18_2 = st.columns([1,1])
		with colbox18_1:
			st.text_area("(18) Matricola carro distinta (clean)", value=st.session_state["box-18-clean"], disabled=True, height=100, key="box18_1")
		with colbox18_2:
			st.text_area("(18) Matricola carro distinta (Orfeus)", value=st.session_state["box-18-orfeus"], height=100, key="box18_2")

		colbox19_1_1, colbox19_1_2 = st.columns([1,1])
		with colbox19_1_1:
			st.text_area("(19) Matricola carro percorso (clean)", value=st.session_state["box-19-1-clean"], disabled=True, height=100, key="box19_1_1")
		with colbox19_1_2:
			st.text_area("(19) Matricola carro percorso (Orfeus)", value=st.session_state["box-19-1-orfeus"], height=100, key="box19_1_2")
  
		colbox19_2_1, colbox19_2_2 = st.columns([1,1])
		with colbox19_2_1:
			st.text_area("(19) Matricola carro da (clean)", value=st.session_state["box-19-2-clean"], disabled=True, height=100, key="box19_2_1")
		with colbox19_2_2:
			st.text_area("(19) Matricola carro da (Orfeus)", value=st.session_state["box-19-2-orfeus"], height=100, key="box19_2_2")
  
		colbox24_1, colbox24_2 = st.columns([1,1])
		with colbox24_1:
			st.text_area("(24) Codice NHM (clean)", value=st.session_state["box-24-clean"], disabled=True, height=100, key="box24_1")
		with colbox24_2:
			st.text_area("(24) Codice NHM (Orfeus)", value=st.session_state["box-24-orfeus"], height=100, key="box24_2")

		colbox25_1, colbox25_2 = st.columns([1,1])
		with colbox25_1:
			st.text_area("(25) Massa (clean)", value=st.session_state["box-25-clean"], disabled=True, height=100, key="box25_1")
		with colbox25_2:
			st.text_area("(25) Massa (Orfeus)", value=st.session_state["box-25-orfeus"], height=100, key="box25_2")

		colbox49_1, colbox49_2 = st.columns([1,1])
		with colbox49_1:
			st.text_area("(49) Codice Affrancazione (clean)", value=st.session_state["box-49-clean"], disabled=True, height=100, key="box49_1")
		with colbox49_2:
			st.text_area("(49) Codice Affrancazione (Orfeus)", value=st.session_state["box-49-orfeus"], height=100, key="box49_2")

		colbox57_1, colbox57_2 = st.columns([1,1])
		with colbox57_1:
			st.text_area("(57) Altro trasporti (clean)", value=st.session_state["box-57-clean"], disabled=True, height=100, key="box57_1")
		with colbox57_2:
			st.text_area("(57) Altro trasporti (Orfeus)", value=st.session_state["box-57-orfeus"], height=100, key="box57_2")
  	  
		#TODO: visualizzare il delta tra le due colonne
		#TODO: modificare le session orfeus con i dati dell'xml
  
		if st.button("Conferma i valori"):
			#TODO: Salvare i valori
			st.toast("Valori confermati. E' possibile procedere con la fase successiva")


	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())