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

def search_orfeus():
	import time
	folder_path = os.path.join('orpheus')
	file_list = os.listdir(folder_path)
	total_files = len(file_list)
	st.write("Numero di file da analizzare: {}".format(total_files))

	progress_text = "Ricerca su dati Orfeus xml in corso..."
	my_bar = st.progress(0, text=progress_text)
	for index, file_name in enumerate(file_list):
		# Costruisci il percorso completo del file
		file_path = os.path.join(folder_path, file_name)
		# Verifica che sia un file e non una cartella
		if os.path.isfile(file_path):
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
			for ecn in root.findall(".//ECN"):
				carrier_code = ecn.find(".//AcceptancePoint/CarrierCode")
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
				st.warning(f"Errore nella conversione della data: {e} nel file {file_name}")

			# Confronto
			if st.session_state['box-62-paese'] == uic_country_codes[0] \
				and st.session_state['box-62-stazione'] == station_codes[0] \
				and st.session.state['box-62-impresa'] == carrier_codes[0] \
			 	and st.session.state['box-62-spedizione'] == consignment_numbers[0] \
			    and st.session.state['box-62-luogo'] == data_ora_formattata:
				st.success("Trovato XML Orpheus: {}".format(file_name))

			# Confronto di test
			# if "80" == uic_country_codes[0] and "637702" == station_codes[0] and "3239" == carrier_codes[0] and "678649" == consignment_numbers[0] and "20231106" == data_ora_formattata:
			# 	st.success("Trovato XML Orpheus: {}".format(file_name))

		percent_complete = int((index + 1) / total_files * 100)
		my_bar.progress(percent_complete, text=progress_text)
  
		st.session_state['box-01-orfeus'] = "Orfeus XXX"
		st.session_state['box-02-orfeus'] = "Orfeus XXX"
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

		st.text_input("Codice Paese", key="ident_paese_1", value=st.session_state["box-62-paese"], disabled=True)
		st.text_input("Codice Stazione", key="ident_stazione_1", value=st.session_state["box-62-stazione"], disabled=True)
		st.text_input("Codice Impresa", key="ident_impresa_1", value=st.session_state["box-62-impresa"], disabled=True)
		st.text_input("Codice Spedizione", key="ident_spedizione_1", value=st.session_state["box-62-spedizione"], disabled=True)
		st.text_input("Luogo", key="ident_luogo_1", value=st.session_state["box-62-luogo"], disabled=True)
		st.text_input("Data", key="ident_data_1", value=st.session_state["box-62-data"], disabled=True)

		colbox1_1, colbox1_2 = st.columns([1,1])
		with colbox1_1:
			st.text_area("(1) Mittente", value=st.session_state['box-01'], disabled=True, height=150, key="box1_1")
		with colbox1_2:
			st.text_area("(1) Mittente (Orfeus)", value=st.session_state['box-01-orfeus'], height=150, key="box1_2")
		st.divider()
		
		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(2) Mittente Codice", value=st.session_state['box-02'] , disabled=True, height=100, key="box2_1")
		with colbox2_2:
			st.text_area("(2) Mittente Codice (Orfeus)", value=st.session_state['box-01-orfeus'], height=100, key="box2_2")
		st.divider()

		colbox4_1, colbox4_2 = st.columns([1,1])
		with colbox4_1:
			st.text_area("(4) Destinatario", value=st.session_state["box-04"], disabled=True, height=150, key="box4_1")
		with colbox4_2:
			st.text_area("(4) Destinatario (Orfeus)", height=150, value="", key="box4_2")
		st.divider()

		colbox5_1, colbox5_2 = st.columns([1,1])
		with colbox5_1:
			st.text_area("(5) Destinatario Codice", value=st.session_state["box-05"], disabled=True, height=100, key="box5_1")
		with colbox5_2:
			st.text_area("(5) Destinatario Codice (Orfeus)", height=100, key="box5_2", value="")
		st.divider()

		colbox10_1, colbox10_2= st.columns([1,1])
		with colbox10_1:
			st.text_area("(10) Raccordo Consegna", value=st.session_state["box-10"], disabled=True, height=100, key="box10_1")
		with colbox10_2:
			st.text_area("(10) Raccordo Consegna (Orfeus)", height=100, key="box10_2", value="")
		st.divider()

		colbox12_1, colbox12_2 = st.columns([1,1])
		with colbox12_1:
			st.text_area("(12) Codice Stazione Destinatario", value=st.session_state["box-12"], disabled=True, height=100, key="box12_1")
		with colbox12_2:
			st.text_area("(12) Codice Stazione Destinatario (Orfeus)", height=100, key="box12_2", value="")
		st.divider()

		colbox13_1, colbox13_2 = st.columns([1,1])
		with colbox13_1:
			st.text_area("(13) Condizioni commerciali", value=st.session_state["box-13"], disabled=True, height=100, key="box13_1")
		with colbox13_2:
			st.text_area("(13) Condizioni commerciali (Orfeus)", height=100, key="box13_2", value="")
		st.divider()

		colbox14_1, colbox14_2= st.columns([1,1])
		with colbox14_1:
			st.text_area("(14) Codice Condizioni commerciali", value=st.session_state["box-14"], disabled=True, height=100, key="box14_1")
		with colbox14_2:
			st.text_area("(14) Codice Condizioni commerciali (Orfeus)", height=100, key="box14_2", value="")
		st.divider()

		colbox16_1, colbox16_2 = st.columns([1,1])
		with colbox16_1:
			st.text_area("(16) Luogo consegna presa in carico", value=st.session_state["box-16"], disabled=True, height=100, key="box16_1")
		with colbox16_2:
			st.text_area("(16) Luogo consegna presa in carico (Orfeus)", height=100, key="box16_2", value="")
		st.divider()

		colbox18_1, colbox18_2 = st.columns([1,1])
		with colbox18_1:
			st.text_area("(18) Matricola carro distinta", value=st.session_state["box-18"], disabled=True, height=100, key="box18_1")
		with colbox18_2:
			st.text_area("(18) Matricola carro distinta (Orfeus)", height=100, key="box18_2", value="")
		st.divider()

		colbox49_1, colbox49_2 = st.columns([1,1])
		with colbox49_1:
			st.text_area("(49) Codice Affrancazione", value=st.session_state["box-49"], disabled=True, height=100, key="box49_1")
		with colbox49_2:
			st.text_area("(49) Codice Affrancazione (Orfeus)", height=100, key="box49_2", value="")
		st.divider()

		colbox57_1, colbox57_2 = st.columns([1,1])
		with colbox57_1:
			st.text_area("(57) Altro trasporti e ruolo", value=st.session_state["box-57"], disabled=True, height=100, key="box57_1")
		with colbox57_2:
			st.text_area("(57) Altro trasporti e ruolo (Orfeus)", height=100, key="box57_2", value="")
		st.divider()
		# -------

		# Recupero dati Wagon Lists
		st.info("Dettagli Vagoni")

		colbox_wagon_1, colbox_wagon_2 = st.columns([1,1])
		with colbox_wagon_1:
			st.text_area("Wagon List", value=st.session_state["box-wagon-list"], disabled=True, height=100, key="box_wagon_1")
		with colbox_wagon_2:
			st.text_area("Wagon List (Orfeus)", height=100, key="box_wagon_2", value="")
		st.divider()
		st.text_area("Dettaglio vagoni", height=500, value="")
		# -------

		st.button('Avvia ricerca su Orfeus', key="button_orfeus", on_click=search_orfeus)

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())