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

def read_field_from_cim():
	if 'box-01' not in st.session_state:
		from azure.core.credentials import AzureKeyCredential
		from azure.ai.formrecognizer import DocumentAnalysisClient
		endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
		key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
		model_id = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL_ID")
		model_id = "ldv06-neural"
		document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

		with open(os.path.join('ldv', "cim.jpg"),'rb') as f:
			poller = document_analysis_client.begin_analyze_document(model_id, document=f)
		result = poller.result()

		for idx, document in enumerate(result.documents):
			for name, field in document.fields.items():
				st.session_state[name] = field.value

		st.session_state["box-01-clean"] = prompt_for_box("1", "Estrai dal testo solo la ragione sociale del mittente della CIM", st.session_state["box-01"], llm)
		st.session_state["box-02-clean"] = prompt_for_box("2", "Estrai dal testo un codice numerico che rappresenta il codice mittente della CIM", st.session_state["box-02"], llm)
		st.session_state["box-03-clean"] = prompt_for_box("3", "Estrai dal testo un codice numerico che rappresenta il codice mittente della CIM", st.session_state["box-03"], llm)
		st.session_state["box-04-clean"] = prompt_for_box("4", "Estrai dal testo solo la ragione sociale del destinatario della CIM", st.session_state["box-04"], llm)
		st.session_state["box-05-clean"] = prompt_for_box("5", "Estrai dal testo un codice numerico che rappresenta il codice destinatario della CIM", st.session_state["box-05"], llm)
		st.session_state["box-06-clean"] = prompt_for_box("6", "Estrai dal testo un codice numerico che rappresenta il codice destinatario della CIM", st.session_state["box-06"], llm)
		st.session_state["box-10-clean"] = prompt_for_box("10", "Estrai solo le informazioni di un luogo di consegna della CIM", st.session_state["box-10"], llm)
		st.session_state["box-11-clean"] = prompt_for_box("11", "Estrai dal testo un codice alfanumerico che rappresenta il codice di una stazione di destinazione della CIM", st.session_state["box-11"], llm)
		st.session_state["box-12-clean"] = prompt_for_box("12", "Estrai dal testo un codice numerico che rappresenta il codice di una stazione di destinazione della CIM", st.session_state["box-12"], llm)
		st.session_state["box-13-clean"] = prompt_for_box("13", "Estrai dal testo le informazioni più importanti", st.session_state["box-13"], llm)
		st.session_state["box-14-clean"] = prompt_for_box("14", "Estrai dal testo un codice numerico che rappresenta un codice della CIM", st.session_state["box-14"], llm)
		st.session_state["box-16-clean"] = prompt_for_box("16", "Estrai le informazioni di un luogo di presa in carico della CIM", st.session_state["box-16"], llm)
		st.session_state["box-16-orario-clean"] = prompt_for_box("10", "Interpeta la stringa come una data di presa in carico della CIM, eventualmente anche data e orario", st.session_state["box-16-orario"], llm)
		st.session_state["box-18-clean"] = prompt_for_box("18", "Estrai le informazioni da testo", st.session_state["box-16"], llm)
		st.session_state["box-19-1-clean"] = prompt_for_box("19", "Estrai le informazioni dal testo", st.session_state["box-19-1-clean"], llm)
		st.session_state["box-19-2-clean"] = prompt_for_box("19", "Estrai le informazioni dal testo", st.session_state["box-19-1-clean"], llm)
		st.session_state["box-24-clean"] = prompt_for_box("24", "Estrai un codice numerico che rappresenta il codice NHM della CIM.", st.session_state["box-19-1-clean"], llm)
		st.session_state["box-25-clean"] = prompt_for_box("24", "Interpreta le informazioni dal testo, che sono dei pesi di vagoni. Estrai se lo trovi il totale della massa.", st.session_state["box-19-1-clean"], llm)
		st.session_state["box-29-clean"] = prompt_for_box("24", "Interpreta le informazioni di luogo e data della CIM", st.session_state["box-29-clean"], llm)
		st.session_state["box-49-clean"] = prompt_for_box("24", "Estrai dal testo un codice numerico composto eventualmente da più parti. ", st.session_state["box-49-clean"], llm)
		st.session_state["box-57-clean"] = prompt_for_box("57", "Nel testo ci sono informazioni di trasporti, con indirizzi e percorsi. Estrai tutte le informazioni che riesci a leggere in modo ordinato. ", st.session_state["box-49-clean"], llm)
		st.session_state["box-62-paese-clean"] = prompt_for_box("62", "Estrai dal testo un codice numerico che rappresenta un codice della etichetta della CIM. Se nel codice ci sono dei '-' non considerarli.", st.session_state["box-62-paese"], llm)
		st.session_state["box-62-stazione-clean"] = prompt_for_box("62", "Estrai dal testo un codice numerico che rappresenta un codice della etichetta della CIM. Se nel codice ci sono dei '-' non considerarli.", st.session_state["box-62-stazione"], llm)
		st.session_state["box-62-impresa-clean"] = prompt_for_box("62", "Estrai dal testo un codice numerico che rappresenta un codice della etichetta della CIM. Se nel codice ci sono dei '-' non considerarli.", st.session_state["box-62-impresa"], llm)
		st.session_state["box-62-spedizione-clean"] = prompt_for_box("62", "Estrai dal testo un codice numerico che rappresenta un codice della etichetta della CIM. Se nel codice ci sono dei '-' non considerarli.", st.session_state["box-62-spedizione"], llm)
		st.session_state["box-62-luogo-clean"] = prompt_for_box("29", "Estrai dal testo le sole informazioni del luogo.", st.session_state["box-29"], llm)
		st.session_state["box-62-data-clean"] = prompt_for_box("29", "Estrai dal testo le sole informazioni della data.", st.session_state["box-29"], llm)
		st.session_state["box-wagon-list-clean"] = ""
  
	return

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
	
	output_parser = StrOutputParser()
	system_message = "Sei un assistente virtuale che aiuta ad estrarre informazioni da una testo analizzato con OCR da documenti CIM utilizzati nel trasporto ferroviario internazionale di merci."
	prompt = ChatPromptTemplate.from_messages([("system", system_message),("user", "{input}")])
	chain = prompt | llm | output_parser
	response = chain.invoke({"input": prompt_base.format(numero_casella=numero_casella, descrizione_estrazione=descrizione_estrazione, box=box)})
	
	return response

try:
	st.set_page_config(page_title="Mercitalia - Automazione LDV / RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
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
		st.image(os.path.join('images','Slide2.JPG'), use_column_width=True)
		st.write("""
### Descrizione
In questa fase il sistema recupera dalla mail selezonata informazioni da:
- contenuto della mail
- allegati PDF o Excel convertiti in immagini

Successivamente viene utilizzato un modello di training AI trainato sui documenti CIM per estrarre le informazioni più importanti dalla lettera di vettura.
da una serie di mail i contenuti più importanti per procedere ad una selezione più stretta rispetto alle data.
Viene utilizzato anche GPT4-Vision assieme al servizio comlementare Azure AI Vision per estrarre informazioni dai documenti di dettaglio dei vagoni in quanto rappresentano tabelle "dense" con formati estremamente variabili.
Le estrazioni dai riquadr dell CIM viene passato al servizio GPT4 per una pulizia ulteriore del testo.
### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa
- **Azure Blob Storage**: Servizio di storage per file/blob ad alta scalabilità
- **Azure OpenAI**: Servizio di Large Language Model con modelli GPT4-Turbo e GPT-4-Vision
- **Azure Document Intelligence**: Servizio di AI per l'analisi di documenti, utilizzato un Custom Extraction Model per la CIM
""")


		read_field_from_cim()
  
		st.write(os.getenv("AZURE_OPENAI_BASE"))
		st.write(os.getenv("AZURE_OPENAI_KEY"))
  
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
  
		# Recupero Allegati e presentazione
		folder = os.path.join('ldv', st.session_state["ldv"])
		jpgs = []

		for file in os.listdir(folder):
			if file.endswith(".jpg"):
				file_completo = os.path.join(folder, file)
				jpgs.append(file_completo)

		expander_allegati = st.expander("Allegati", expanded=False)
		for jpg in jpgs:
			expander_allegati.image(jpg, width=500)
		# -------
  
		# Recupero Dati Email
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
		# -------
  
		# Recupero Dati CIM e popolamento sessione ocr-fields
		read_field_from_cim()
  
		fields = st.session_state['ocr-fields']
  
		st.info("Dati estratti dalla CIM")

		colbox1_1, colbox1_2 = st.columns([1,1])	
		with colbox1_1:
			st.text_area("(1) Mittente", value=st.session_state["box-01"], disabled=True, height=150, key="box1_1")
		with colbox1_2:
			st.text_area("(1) Mittente (Clean)", value=st.session_state["box_01_clean"], height=150, key="box1_2")
		st.divider()
		
		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(2) Mittente Codice 1", value=st.session_state["box-02"], disabled=True, height=100, key="box2_1")
		with colbox2_2:
			st.text_area("(2) Mittente Codice 1 (Clean)", value=st.session_state["box-02-clean"], height=100, key="box2_2")
		st.divider()

		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(3) Mittente Codice 2", value=st.session_state["box-03"], disabled=True, height=100, key="box3_1")
		with colbox2_2:
			st.text_area("(3) Mittente Codice 2 (Clean)", value=st.session_state["box-03-clean"], height=100, key="box3_2")
		st.divider()

		colbox1_1, colbox1_2 = st.columns([1,1])	
		with colbox1_1:
			st.text_area("(4) Destinatario", value=st.session_state["box-04"], disabled=True, height=150, key="box4_1")
		with colbox1_2:
			st.text_area("(4) Destinatario (Clean)", value=st.session_state["box_04_clean"], height=150, key="box4_2")
		st.divider()
		
		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(5) Destinatario Codice 1", value=st.session_state["box-05"], disabled=True, height=100, key="box5_1")
		with colbox2_2:
			st.text_area("(5) Destinatario Codice 1 (Clean)", value=st.session_state["box-05-clean"], height=100, key="box5_2")
		st.divider()

		colbox2_1, colbox2_2 = st.columns([1,1])
		with colbox2_1:
			st.text_area("(6) Destinatario Codice 2", value=st.session_state["box-06"], disabled=True, height=100, key="box6_1")
		with colbox2_2:
			st.text_area("(6) Destinatario Codice 2 (Clean)", value=st.session_state["box-06-clean"], height=100, key="box6_2")
		st.divider()

		colbox10_1, colbox10_2= st.columns([1,1])
		with colbox10_1:
			st.text_area("(10) Luogo di Consegna", value=st.session_state["box-10"], disabled=True, height=100, key="box10_1")
		with colbox10_2:
			st.text_area("(10) Luogo di Consegna (Clean)", value=st.session_state["box-10-clean"], height=100, key="box10_2")
		st.divider()

		colbox11_1, colbox11_2 = st.columns([1,1])
		with colbox11_1:
			st.text_area("(11) Codice Luogo Consegna 1", value=st.session_state["box-11"], disabled=True, height=100, key="box11_1")
		with colbox11_2:
			st.text_area("(11) Codice Luogo Consegna 1 (Clean)", st.session_state["box-11-clean"], height=100, key="box11_2")
		st.divider()
  
		colbox12_1, colbox12_2 = st.columns([1,1])
		with colbox11_1:
			st.text_area("(12) Codice Luogo Consegna 2", value=st.session_state["box-12"], disabled=True, height=100, key="box12_1")
		with colbox11_2:
			st.text_area("(12) Codice Luogo Consegna 2 (Clean)", st.session_state["box-12-clean"], height=100, key="box12_2")
		st.divider()

		colbox13_1, colbox13_2 = st.columns([1,1])
		with colbox13_1:
			st.text_area("(13) Condizioni commerciali", value=st.session_state["box-13"], disabled=True, height=100, key="box13_1")
		with colbox13_2:
			st.text_area("(13) Condizioni commerciali (Clean)", value=st.session_state["box-13-clean"], height=100, key="box13_2", )
		st.divider()

		colbox14_1, colbox14_2= st.columns([1,1])
		with colbox14_1:
			st.text_area("(14) Codice Contratto", value=st.session_state["box-14"], disabled=True, height=100, key="box14_1")
		with colbox14_2:
			st.text_area("(14) Codice Contratto (Clean)", value=st.session_state["box-14-clean"], height=100, key="box14_2")
		st.divider()

		colbox16_1, colbox16_2= st.columns([1,1])
		with colbox16_1:
			st.text_area("(16) Origine", value=st.session_state["box-16"], disabled=True, height=100, key="box16_1")
		with colbox16_2:
			st.text_area("(16) Origine (Clean)", value=st.session_state["box-16-clean"], height=100, key="box16_2")
		st.divider()
  
		colbox16_1_orario, colbox16_2_orario= st.columns([1,1])
		with colbox16_1_orario:
			st.text_area("(16) Origine Data", value=st.session_state["box-14"], disabled=True, height=100, key="box16_orario_1")
		with colbox16_2_orario:
			st.text_area("(16) Orogine Data (Clean)", value=st.session_state["box-14-clean"], height=100, key="box16_orario_2")
		st.divider()

		colbox17_1, colbox17_2= st.columns([1,1])
		with colbox17_1:
			st.text_area("(17) Origine Codice", value=st.session_state["box-17"], disabled=True, height=100, key="box17_1")
		with colbox17_2:
			st.text_area("(17) Origine Codice (Clean)", value=st.session_state["box-17-clean"], height=100, key="box17_2")
		st.divider()

		colbox18_1, colbox18_2 = st.columns([1,1])
		with colbox18_1:
			st.text_area("(18) Matricola carro distinta", value=st.session_state["box-18"], disabled=True, height=100, key="box18_1")
		with colbox18_2:
			st.text_area("(18) Matricola carro distinta (Clean)", value=["box-18-clean"], height=100, key="box18_2")
		st.divider()

		colbox19_1_1, colbox19_1_2 = st.columns([1,1])
		with colbox19_1_1:
			st.text_area("(19) Matricola carro percorso", value=st.session_state["box-19-1"], disabled=True, height=100, key="box19_1_1")
		with colbox19_1_2:
			st.text_area("(19) Matricola carro percorso (Clean)", value=["box-19-1-clean"], height=100, key="box19_1_2")
		st.divider()
  
		colbox19_2_1, colbox19_2_2 = st.columns([1,1])
		with colbox19_2_1:
			st.text_area("(19) Matricola carro da", value=st.session_state["box-19-2"], disabled=True, height=100, key="box19_2_1")
		with colbox19_2_2:
			st.text_area("(19) Matricola carro da (Clean)", value=["box-19-2-clean"], height=100, key="box19_2_2")
		st.divider()

		colbox49_1, colbox49_2 = st.columns([1,1])
		with colbox49_1:
			st.text_area("(49) Codice Affrancazione", value=st.session_state["box-49"], disabled=True, height=100, key="box49_1")
		with colbox49_2:
			st.text_area("(49) Codice Affrancazione (Clean)", value=st.session_state["box-49-clean"], height=100, key="box49_2")
		st.divider()

		colbox57_1, colbox57_2 = st.columns([1,1])
		with colbox57_1:
			st.text_area("(57) Altro trasporti", value=st.session_state["box-57"], disabled=True, height=100, key="box57_1")
		with colbox57_2:
			st.text_area("(57) Altro trasporti (Clean)", value=st.session_state["box-57-clean"], height=100, key="box57_2")
		st.divider()

		st.info("(62) Identificazione Spedizione")
  
		col_identificazione1, col_identificazione2 = st.columns([1,1])
		with col_identificazione1:
			st.text_input("Codice Paese", key="ident_paese_1", value=st.session_state["box-62-paese"], disabled=True)
			st.text_input("Codice Stazione", key="ident_stazione_1", value=st.session_state["box-62-stazione"], disabled=True)
			st.text_input("Codice Impresa", key="ident_impresa_1", value=st.session_state["box-62-impresa"], disabled=True)
			st.text_input("Codice Spedizione", key="ident_spedizione_1", value=st.session_state["box-62-spedizione"], disabled=True)
			st.text_input("Luogo", key="ident_luogo_1", value=st.session_state["box-62-luogo"], disabled=True)
			st.text_input("Data", key="ident_data_1", value=st.session_state["box-62-data"], disabled=True)
		
		with col_identificazione2:
			st.text_input("Codice Paese", key="ident_paese_2", value=st.session_state["box-62-paese-clean"], disabled=True)
			st.text_input("Codice Stazione", key="ident_stazione_2", value=st.session_state["box-62-stazione-clean"], disabled=True)
			st.text_input("Codice Impresa", key="ident_impresa_2", value=st.session_state["box-62-impresa-clean"], disabled=True)
			st.text_input("Codice Spedizione", key="ident_spedizione_2", value=st.session_state["box-62-spedizione-clean"], disabled=True)
			st.text_input("Luogo", key="ident_luogo_2", value=st.session_state["box-62-luogo-clean"], disabled=True)
			st.text_input("Data", key="ident_data_2", value=st.session_state["box-62-data-clean"], disabled=True)
		# -------
  
		# Recupero dati Wagon Lists
		st.info("Dettagli Vagoni")
		st.text_area("Dettaglio vagoni", height=500, value="", key="wagon_list")
		# -------

		if st.button("Conferma i valori"):
			# TODO completare i bo
			st.session_state["box-01-clean"] = st.session_state.box1_2
			st.session_state["box-02-clean"] = st.session_state.box2_2
			st.session_state["box-03-clean"] = st.session_state.box3_2
			st.session_state["box-04-clean"] = st.session_state.box4_2
			st.session_state["box-05-clean"] = st.session_state.box5_2
			st.session_state["box-06-clean"] = st.session_state.box6_2
			st.session_state["box-10-clean"] = st.session_state.box10_2
			st.session_state["box-12-clean"] = st.session_state.box12_2
			st.session_state["box-13-clean"] = st.session_state.box13_2
			st.session_state["box-14-clean"] = st.session_state.box14_2
			st.session_state["box-16-clean"] = st.session_state.box16_2
			st.session_state["box-18-clean"] = st.session_state.box18_2
			st.session_state["box-49-clean"] = st.session_state.box49_2
			st.session_state["box-57-clean"] = st.session_state.box57_2
			st.session_state["box-62-paese-clean"] = st.session_state.ident_paese_2
			st.session_state["box-62-stazione-clean"] = st.session_state.ident_stazione_2
			st.session_state["box-62-impresa-clean"] = st.session_state.ident_impresa_2
			st.session_state["box-62-spedizione-clean"] = st.session_state.ident_spedizione_2
			st.session_state["box-62-luogo-clean"] = st.session_state.ident_luogo_2
			st.session_state["box-62-data-clean"] = st.session_state.ident_data_2
			st.session_state["box-wagon-list"] = st.session_state.wagon_list
			st.toast("Valori confermati. E' possibile procedere con la fase successiva")
   
	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())