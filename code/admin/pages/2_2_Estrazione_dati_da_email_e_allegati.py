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

def get_field_from_cim():
	
	from azure.core.credentials import AzureKeyCredential
	from azure.ai.formrecognizer import DocumentAnalysisClient
	endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
	key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
	model_id = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL_ID")
	model_id = "ldv04"
	document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

	with open(os.path.join('ldv', "cim.jpg"),'rb') as f:
		poller = document_analysis_client.begin_analyze_document(model_id, document=f)
	result = poller.result()

	fields = {}

	for idx, document in enumerate(result.documents):
		for name, field in document.fields.items():
			fields[name] = field.value

	return fields

def prompt_for_box(numero_casella: str, descrizione_estrazione: str, box: str, llm: AzureChatOpenAI):
	return ""
	prompt_base = """il testo delimitato da ### deriva da una scansione OCR di un modulo di trasporto ferroviario. 
Il testo deriva da una casella che ha come numero iniziale {numero_casella} e che può contenere la descrizione della casella stessa.
###
{box}
###

{descrizione_estrazione}
Non aggiungere altro alla risposta

Risposta:
"""
	
	output_parser = StrOutputParser()
	system_message = "Sei un assistente virtuale che aiuta ad estrarre informazioni da testo analizzato con OCR da documenti di trasporto e lettere di vettura."
	prompt = ChatPromptTemplate.from_messages([("system", system_message),("user", "{input}")])
	chain = prompt | llm | output_parser
	response = chain.invoke({"input": prompt_base.format(numero_casella=numero_casella, descrizione_estrazione=descrizione_estrazione, box=box)})
	
	return response
	
	import pandas as pd
	from fuzzywuzzy import process
	from dotenv import load_dotenv

	# Carica i dati da un file Excel
	df = pd.read_excel(os.path.join('orpheus', "clienti.xslx"))

	# La ragione sociale che stai cercando
	ragione_sociale_da_cercare = st.session_state.box1_2

	# Trova la corrispondenza più simile nel DataFrame
	corrispondenze = process.extract(ragione_sociale_da_cercare, df['ragione sociale'], limit=5)

	# Stampa le corrispondenze trovate e i relativi codici
	for corrispondenza in corrispondenze:
		match = corrispondenza[0]  # La ragione sociale corrispondente
		score = corrispondenza[1]  # Il punteggio di similarità

		# Trova l'indice (o gli indici) nel DataFrame dove c'è questa corrispondenza
		indici = df.index[df['ragione sociale'] == match].tolist()

		# Stampa i dettagli delle corrispondenze trovate
		options = []

		for indice in indici:
			codice_corrispondente = df.loc[indice, 'codice']
			options.append(f"{match} - Codice: {codice_corrispondente}, Similarità: {score}")
	
	st.session_state["codice_mittente_scelto"] = options
	
	return

def elaborazione_ldv():
	
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

	fields = get_field_from_cim()
	return
 
	box_01_clean = "" if not fields["box-01"] else prompt_for_box("1", "Estrai solo le informazioni del mittente", fields["box-01"], llm)
	colbox1_1, colbox1_2, colbox1_3 = st.columns([1,1,1])
	st.session_state["session_box1_2"] = box_01_clean
 
	with colbox1_1:
		st.write(fields["box-01"])
	with colbox1_2:
		st.text_area("(1) Mittente (Clean)", value=st.session_state["session_box1_2"], height=150, key="box1_2")
	with colbox1_3:
		st.text_area("(1) Mittente (Orpheus)", value="", height=150, key="box1_3", disabled=True)

	st.divider()
	
	box_02_clean = "" if not fields["box-02"] else prompt_for_box("2", "Estrai solo le informazioni del codice mittente", fields["box-02"], llm)
	colbox2_1, colbox2_2, colbox2_3 = st.columns([1,1,1])
	with colbox2_1:
		st.write(fields["box-02"])
	with colbox2_2:
		st.text_area("(2) Mittente Codice (Clean)", value=box_02_clean, height=100, key="box2_2")
	with colbox2_3:
		st.text_area("(2) Mittente Codice (Orpheus)", value="", height=100, key="box2_3", disabled=True)
	st.selectbox("Ragioni sociali simili", options=[], placeholder="Seleziona la corrispondenza più simile", key="codice_mittente_scelto")

	st.divider()

	box_04_clean = "" if not fields["box-04"] else prompt_for_box("4", "Estrai solo le informazioni della ragione sociale del destinatario", fields["box-04"], llm)
	colbox4_1, colbox4_2, colbox4_3 = st.columns([1,1,1])
	with colbox4_1:
		st.write(fields["box-04"])
	with colbox4_2:
		st.text_area("(4) Destinatario (Clean)", height=150, key="box4_2", value=box_04_clean)
	with colbox4_3:
		st.text_area("(4) Destinatario (Orpheus)", height=150, key="box4_3", value="", disabled=True)
  
	st.divider()
 
	box_05_clean = "" if not fields["box-05"] else prompt_for_box("5", "Estrai solo le informazioni della codice mittente", fields["box-05"], llm)
	colbox5_1, colbox5_2, colbox5_3 = st.columns([1,1,1])
	with colbox5_1:
		st.write(fields["box-05"])
	with colbox5_2:
		st.text_area("(5) Destinatario Codice (Clean)", height=100, key="box5_2", value=box_05_clean)
	with colbox5_3:
		st.text_area("(5) Destinatario Codice (Orpheus)", height=100, key="box5_3", value="", disabled=True)
	st.selectbox("Ragioni sociali simili", options=[], placeholder="Seleziona la corrispondenza più simile", key="codice_destinatario_scelto")

	st.divider()

	box_10_clean = "" if not fields["box-10"] else prompt_for_box("10", "Estrai solo le informazioni del codice raccordo consegna", fields["box-10"], llm)
	colbox10_1, colbox10_2, colbox10_3 = st.columns([1,1,1])
	with colbox10_1:
		st.write(fields["box-10"])
	with colbox10_2:
		st.text_area("(10) Raccordo Consegna (Clean)", height=100, key="box10_2", value=box_10_clean)
	with colbox10_3:
		st.text_area("(10) Raccordo Consegna (Orpheus)", height=100, key="box10_3", value="", disabled=True)

	st.divider()

	box_12_clean = "" if not fields["box-12"] else prompt_for_box("12", "Estrai solo le informazioni del codice stazione destinatario. Il codice è solitamente un numero intero.", fields["box-12"], llm)
	colbox12_1, colbox12_2, colbox12_3 = st.columns([1,1,1])
	with colbox12_1:
		st.write(fields["box-12"])
	with colbox12_2:
		st.text_area("(12) Codice Stazione Destinatario (Clean)", height=100, key="box12_2", value=box_12_clean)
	with colbox12_3:
		st.text_area("(12) Codice Stazione Destinatario (Orpheus)", height=100, key="box12_3", value="", disabled=True)

	st.divider()

	box_13_clean = "" if not fields["box-13"] else prompt_for_box("13", "Estrai solo le informazioni delle condizioni commerciali.", fields["box-13"], llm)
	colbox13_1, colbox13_2, colbox13_3 = st.columns([1,1,1])
	with colbox13_1:
		st.write(fields["box-13"])
	with colbox13_2:
		st.text_area("(13) Condizioni commerciali (Clean)", height=100, key="box13_2", value=box_13_clean)
	with colbox13_3:
		st.text_area("(13) Condizioni commerciali (Orpheus)", height=100, key="box13_3", value="", disabled=True)
	st.divider()
	box_14_clean = "" if not fields["box-14"] else prompt_for_box("14", "Estrai il codice numerico che è solitamente n numero intero.", fields["box-14"], llm)
	colbox14_1, colbox14_2, colbox14_3 = st.columns([1,1,1])
	with colbox14_1:
		st.write(fields["box-14"])
	with colbox14_2:
		st.text_area("(14) Codice Condizioni commerciali (Clean)", height=100, key="box14_2", value=box_14_clean)
	with colbox14_3:
		st.text_area("(14) Condizioni commerciali (Orpheus)", height=100, key="box14_3", value="", disabled=True)
	st.divider()
	box_16_clean = "" if not fields["box-16"] else prompt_for_box("16", "Estrai le informazioni del luogo di consegna", fields["box-16"], llm)
	colbox16_1, colbox16_2, colbox16_3 = st.columns([1,1,1])
	with colbox16_1:
		st.write(fields["box-16"])
	with colbox16_2:
		st.text_area("(16) Luogo consegna presa in carico (Clean)", height=100, key="box16_2", value=box_16_clean)
	with colbox16_3:
		st.text_area("(16) Luogo consegna presa in carico (Orpheus)", height=100, key="box16_3", value="", disabled=True)
	st.divider()
	box_18_clean = "" if not fields["box-18"] else prompt_for_box("18", "Estrai le informazioni della matricola carro distinta", fields["box-18"], llm)
	colbox18_1, colbox18_2, colbox18_3 = st.columns([1,1,1])
	with colbox18_1:
		st.write(fields["box-18"])
	with colbox18_2:
		st.text_area("(18) Matricola carro distinta (Clean)", height=100, key="box18_2", value=box_18_clean)
	with colbox18_3:
		st.text_area("(18) Matricola carro distinta (Orpheus)", height=100, key="box18_3", value="", disabled=True)
	st.divider()
	box_49_clean = "" if not fields["box-49"] else prompt_for_box("49", "Estrai le informazioni del codice affrancazione che è solitamente un codice alfanumerico.", fields["box-49"], llm)
	colbox49_1, colbox49_2, colbox49_3 = st.columns([1,1,1])
	with colbox49_1:
		st.write(fields["box-49"])
	with colbox49_2:
		st.text_area("(49) Codice Affrancazione (Clean)", height=100, key="box49_2", value=box_49_clean)
	with colbox49_3:
		st.text_area("(49) Codice Affrancazione (Orpheus)", height=100, key="box49_3", value="", disabled=True)
	st.divider()
	box_57_clean = "" if not fields["box-57"] else prompt_for_box("57", "Estrai le sole informazioni di trasporto.", fields["box-57"], llm)
	colbox57_1, colbox57_2, colbox57_3 = st.columns([1,1,1])
	with colbox57_1:
		st.write(fields["box-57"])
	with colbox57_2:
		st.text_area("(57) Altro trasporti e ruolo (Clean)", height=100, key="box57_2", value=box_57_clean)
	with colbox57_3:
		st.text_area("(57) Altro trasporti e ruolo (Orpheus)", height=100, key="box57_3", value="", disabled=True)
	st.divider()
	box_62_paese_clean = "" if not fields["box-62-paese"] else prompt_for_box("62", "Estrai il codice del paese.", fields["box-62-paese"], llm)
	box_62_stazione_clean = "" if not fields["box-62-stazione"] else prompt_for_box("62", "Estrai il codice della stazione.", fields["box-62-stazione"], llm)
	box_62_impresa_clean = "" if not fields["box-62-impresa"] else prompt_for_box("62", "Estrai il codice dell'impresa.", fields["box-62-impresa"], llm)
	box_62_spedizione_clean = "" if not fields["box-62-spedizione"] else prompt_for_box("62", "Estrai il codice della spedizione.", fields["box-62-spedizione"], llm)
	box_29_luogo_clean = "" if not fields["box-29"] else prompt_for_box("29", "Estrai le sole informazioni del luogo.", fields["box-29"], llm)
	box_29_data_clean = "" if not fields["box-29"] else prompt_for_box("29", "Estrai le sola informazione della data e convertila nel formato YYYYMMDD.", fields["box-29"], llm)

	st.info("(62) Identificazione Spedizione")
 
	col_identificazione1, col_identificazione2, col_identificazione3 = st.columns([1,1,1])
	with col_identificazione1:
		st.text_input("Codice Paese", key="ident_paese_1", value=fields["box-62-paese"], disabled=True)
		st.text_input("Codice Stazione", key="ident_stazione_1", value=fields["box-62-stazione"], disabled=True)
		st.text_input("Codice Impresa", key="ident_impresa_1", value=fields["box-62-impresa"], disabled=True)
		st.text_input("Codice Spedizione", key="ident_spedizione_1", value=fields["box-62-spedizione"], disabled=True)
		st.text_input("Luogo", key="ident_luogo_1", value=fields["box-29"], disabled=True)
		st.text_input("Data", key="ident_data_1", value=fields["box-29"], disabled=True)
	
	with col_identificazione2:
		st.text_input("Codice Paese", key="ident_paese_2", value=box_62_paese_clean)
		st.text_input("Codice Stazione", key="ident_stazione_2", value=box_62_stazione_clean)
		st.text_input("Codice Impresa", key="ident_impresa_2", value=box_62_impresa_clean)
		st.text_input("Codice Spedizione", key="ident_spedizione_2", value=box_62_spedizione_clean)
		st.text_input("Luogo", key="ident_luogo_2", value=box_29_luogo_clean)
		st.text_input("Data", key="ident_data_2", value=box_29_data_clean)
	
	with col_identificazione3:
		st.text_input("Codice Paese", key="ident_paese_3", value="")
		st.text_input("Codice Stazione", key="ident_stazione_3", value="")
		st.text_input("Codice Impresa", key="ident_impresa_3", value="")
		st.text_input("Codice Spedizione", key="ident_spedizione_3", value="")
		st.text_input("Luogo", key="ident_luogo_3", value="")
		st.text_input("Data", key="ident_data_3", value="")

	st.info("Dettagli Vagoni")
	st.text_area("Informazioni di testata", height=200, value="")
	st.text_area("Dettaglio vagoni", height=500, value="")
	st.toast("Elaborazione effettuata per la lettera di vettura {}".format(st.session_state["ldv"]))
	return

try:
	st.set_page_config(page_title="Mercitalia - Automazione LDV / RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Estrazione dati da email e allegati")
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
		st.image(os.path.join('images','Slide2.JPG'), use_column_width=True)
		st.markdown('Descrizione della fase con eventuali note e inserimento di diagramma architetturale con tecnologie e stub AI utilizzati')

		fields = get_field_from_cim()

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
  
		folder = os.path.join('ldv', st.session_state["ldv"])
		jpgs = []

		for file in os.listdir(folder):
			if file.endswith(".jpg"):
				file_completo = os.path.join(folder, file)
				jpgs.append(file_completo)

		expander_allegati = st.expander("Allegati", expanded=False)
		for jpg in jpgs:
			expander_allegati.image(jpg, width=500)

		file_msg = os.path.join('ldv', st.session_state['ldv'], 'msg_data.txt')
		with open(file_msg, 'r') as file:
			content = file.read()
			from_pattern = r"from: (.+)"
			from_match = re.search(from_pattern, content)
			from_value = from_match.group(1) if from_match else None
			subject_pattern = r"subject: (.+)"
			subject_match = re.search(subject_pattern, content)
			subject_value = subject_match.group(1) if subject_match else None
			body_match = re.search(r'body:([\s\S]+)', content)
			body_value = body_match.group(1).strip()
   
		expander_email = st.expander("Email", expanded=True)
		expander_email.text_input("Da:", value=from_value, key="from_email")
		expander_email.text_input("Oggetto:", value=subject_value, key="email_subject")
		expander_email.text_area("Corpo", height=150, value=body_value, key="email_body")
		expander_email.info("Possibili estrazioni")
		expander_email.text_area("Estrazioni", height=100, value="", key="email_extraction")

		expander_cim = st.expander("CIM", expanded=True)
  
		expander_wagons = st.expander("Wagon List", expanded=True)
		
		# colbox1, colbox2, colbox3 = st.columns([1,1,1])
		
		# with colbox1:
		# 	st.text_area("(1) Mittente (OCR)", value="", height=150, key="box1_1")
		# with colbox2:
		# 	st.text_area("(1) Mittente (Clean)", value="", height=150, key="box1_2")
		# with colbox3:
		# 	st.text_area("(1) Mittente (Orpheus)", value="", height=150, key="box1_3", disabled=True)

		# with colbox1:
		# 	st.text_area("(2) Mittente Codice (OCR)", value="", height=150, key="box2_1")
		# with colbox2:
		# 	st.text_area("(2) Mittente Codice (Clean)", value="", height=150, key="box2_2")
		# with colbox3:
		# 	st.text_area("(2) Mittente Codice (Orpheus)", value="", height=150, key="box2_3", disabled=True)

		# st.selectbox("Ragioni sociali simili", options=[], placeholder="Seleziona la corrispondenza più simile", key="codice_mittente_scelto")

		# st.divider()

		# box_04_clean = "" if not fields["box-04"] else prompt_for_box("4", "Estrai solo le informazioni della ragione sociale del destinatario", fields["box-04"], llm)
		# colbox4_1, colbox4_2, colbox4_3 = st.columns([1,1,1])
		# with colbox4_1:
		# 	st.write(fields["box-04"])
		# with colbox4_2:
		# 	st.text_area("(4) Destinatario (Clean)", height=150, key="box4_2", value=box_04_clean)
		# with colbox4_3:
		# 	st.text_area("(4) Destinatario (Orpheus)", height=150, key="box4_3", value="", disabled=True)
	
		# st.divider()
	
		# box_05_clean = "" if not fields["box-05"] else prompt_for_box("5", "Estrai solo le informazioni della codice mittente", fields["box-05"], llm)
		# colbox5_1, colbox5_2, colbox5_3 = st.columns([1,1,1])
		# with colbox5_1:
		# 	st.write(fields["box-05"])
		# with colbox5_2:
		# 	st.text_area("(5) Destinatario Codice (Clean)", height=100, key="box5_2", value=box_05_clean)
		# with colbox5_3:
		# 	st.text_area("(5) Destinatario Codice (Orpheus)", height=100, key="box5_3", value="", disabled=True)
		# st.selectbox("Ragioni sociali simili", options=[], placeholder="Seleziona la corrispondenza più simile", key="codice_destinatario_scelto")

		# st.divider()

		# box_10_clean = "" if not fields["box-10"] else prompt_for_box("10", "Estrai solo le informazioni del codice raccordo consegna", fields["box-10"], llm)
		# colbox10_1, colbox10_2, colbox10_3 = st.columns([1,1,1])
		# with colbox10_1:
		# 	st.write(fields["box-10"])
		# with colbox10_2:
		# 	st.text_area("(10) Raccordo Consegna (Clean)", height=100, key="box10_2", value=box_10_clean)
		# with colbox10_3:
		# 	st.text_area("(10) Raccordo Consegna (Orpheus)", height=100, key="box10_3", value="", disabled=True)

		# st.divider()

		# box_12_clean = "" if not fields["box-12"] else prompt_for_box("12", "Estrai solo le informazioni del codice stazione destinatario. Il codice è solitamente un numero intero.", fields["box-12"], llm)
		# colbox12_1, colbox12_2, colbox12_3 = st.columns([1,1,1])
		# with colbox12_1:
		# 	st.write(fields["box-12"])
		# with colbox12_2:
		# 	st.text_area("(12) Codice Stazione Destinatario (Clean)", height=100, key="box12_2", value=box_12_clean)
		# with colbox12_3:
		# 	st.text_area("(12) Codice Stazione Destinatario (Orpheus)", height=100, key="box12_3", value="", disabled=True)

		# st.divider()

		# box_13_clean = "" if not fields["box-13"] else prompt_for_box("13", "Estrai solo le informazioni delle condizioni commerciali.", fields["box-13"], llm)
		# colbox13_1, colbox13_2, colbox13_3 = st.columns([1,1,1])
		# with colbox13_1:
		# 	st.write(fields["box-13"])
		# with colbox13_2:
		# 	st.text_area("(13) Condizioni commerciali (Clean)", height=100, key="box13_2", value=box_13_clean)
		# with colbox13_3:
		# 	st.text_area("(13) Condizioni commerciali (Orpheus)", height=100, key="box13_3", value="", disabled=True)
		# st.divider()
		# box_14_clean = "" if not fields["box-14"] else prompt_for_box("14", "Estrai il codice numerico che è solitamente n numero intero.", fields["box-14"], llm)
		# colbox14_1, colbox14_2, colbox14_3 = st.columns([1,1,1])
		# with colbox14_1:
		# 	st.write(fields["box-14"])
		# with colbox14_2:
		# 	st.text_area("(14) Codice Condizioni commerciali (Clean)", height=100, key="box14_2", value=box_14_clean)
		# with colbox14_3:
		# 	st.text_area("(14) Condizioni commerciali (Orpheus)", height=100, key="box14_3", value="", disabled=True)
		# st.divider()
		# box_16_clean = "" if not fields["box-16"] else prompt_for_box("16", "Estrai le informazioni del luogo di consegna", fields["box-16"], llm)
		# colbox16_1, colbox16_2, colbox16_3 = st.columns([1,1,1])
		# with colbox16_1:
		# 	st.write(fields["box-16"])
		# with colbox16_2:
		# 	st.text_area("(16) Luogo consegna presa in carico (Clean)", height=100, key="box16_2", value=box_16_clean)
		# with colbox16_3:
		# 	st.text_area("(16) Luogo consegna presa in carico (Orpheus)", height=100, key="box16_3", value="", disabled=True)
		# st.divider()
		# box_18_clean = "" if not fields["box-18"] else prompt_for_box("18", "Estrai le informazioni della matricola carro distinta", fields["box-18"], llm)
		# colbox18_1, colbox18_2, colbox18_3 = st.columns([1,1,1])
		# with colbox18_1:
		# 	st.write(fields["box-18"])
		# with colbox18_2:
		# 	st.text_area("(18) Matricola carro distinta (Clean)", height=100, key="box18_2", value=box_18_clean)
		# with colbox18_3:
		# 	st.text_area("(18) Matricola carro distinta (Orpheus)", height=100, key="box18_3", value="", disabled=True)
		# st.divider()
		# box_49_clean = "" if not fields["box-49"] else prompt_for_box("49", "Estrai le informazioni del codice affrancazione che è solitamente un codice alfanumerico.", fields["box-49"], llm)
		# colbox49_1, colbox49_2, colbox49_3 = st.columns([1,1,1])
		# with colbox49_1:
		# 	st.write(fields["box-49"])
		# with colbox49_2:
		# 	st.text_area("(49) Codice Affrancazione (Clean)", height=100, key="box49_2", value=box_49_clean)
		# with colbox49_3:
		# 	st.text_area("(49) Codice Affrancazione (Orpheus)", height=100, key="box49_3", value="", disabled=True)
		# st.divider()
		# box_57_clean = "" if not fields["box-57"] else prompt_for_box("57", "Estrai le sole informazioni di trasporto.", fields["box-57"], llm)
		# colbox57_1, colbox57_2, colbox57_3 = st.columns([1,1,1])
		# with colbox57_1:
		# 	st.write(fields["box-57"])
		# with colbox57_2:
		# 	st.text_area("(57) Altro trasporti e ruolo (Clean)", height=100, key="box57_2", value=box_57_clean)
		# with colbox57_3:
		# 	st.text_area("(57) Altro trasporti e ruolo (Orpheus)", height=100, key="box57_3", value="", disabled=True)
		# st.divider()
		# box_62_paese_clean = "" if not fields["box-62-paese"] else prompt_for_box("62", "Estrai il codice del paese.", fields["box-62-paese"], llm)
		# box_62_stazione_clean = "" if not fields["box-62-stazione"] else prompt_for_box("62", "Estrai il codice della stazione.", fields["box-62-stazione"], llm)
		# box_62_impresa_clean = "" if not fields["box-62-impresa"] else prompt_for_box("62", "Estrai il codice dell'impresa.", fields["box-62-impresa"], llm)
		# box_62_spedizione_clean = "" if not fields["box-62-spedizione"] else prompt_for_box("62", "Estrai il codice della spedizione.", fields["box-62-spedizione"], llm)
		# box_29_luogo_clean = "" if not fields["box-29"] else prompt_for_box("29", "Estrai le sole informazioni del luogo.", fields["box-29"], llm)
		# box_29_data_clean = "" if not fields["box-29"] else prompt_for_box("29", "Estrai le sola informazione della data e convertila nel formato YYYYMMDD.", fields["box-29"], llm)

		# st.info("(62) Identificazione Spedizione")
	
		# col_identificazione1, col_identificazione2, col_identificazione3 = st.columns([1,1,1])
		# with col_identificazione1:
		# 	st.text_input("Codice Paese", key="ident_paese_1", value=fields["box-62-paese"], disabled=True)
		# 	st.text_input("Codice Stazione", key="ident_stazione_1", value=fields["box-62-stazione"], disabled=True)
		# 	st.text_input("Codice Impresa", key="ident_impresa_1", value=fields["box-62-impresa"], disabled=True)
		# 	st.text_input("Codice Spedizione", key="ident_spedizione_1", value=fields["box-62-spedizione"], disabled=True)
		# 	st.text_input("Luogo", key="ident_luogo_1", value=fields["box-29"], disabled=True)
		# 	st.text_input("Data", key="ident_data_1", value=fields["box-29"], disabled=True)
		
		# with col_identificazione2:
		# 	st.text_input("Codice Paese", key="ident_paese_2", value=box_62_paese_clean)
		# 	st.text_input("Codice Stazione", key="ident_stazione_2", value=box_62_stazione_clean)
		# 	st.text_input("Codice Impresa", key="ident_impresa_2", value=box_62_impresa_clean)
		# 	st.text_input("Codice Spedizione", key="ident_spedizione_2", value=box_62_spedizione_clean)
		# 	st.text_input("Luogo", key="ident_luogo_2", value=box_29_luogo_clean)
		# 	st.text_input("Data", key="ident_data_2", value=box_29_data_clean)

		# with col_identificazione3:
		# 	st.text_input("Codice Paese", key="ident_paese_3", value="")
		# 	st.text_input("Codice Stazione", key="ident_stazione_3", value="")
		# 	st.text_input("Codice Impresa", key="ident_impresa_3", value="")
		# 	st.text_input("Codice Spedizione", key="ident_spedizione_3", value="")
		# 	st.text_input("Luogo", key="ident_luogo_3", value="")
		# 	st.text_input("Data", key="ident_data_3", value="")

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())