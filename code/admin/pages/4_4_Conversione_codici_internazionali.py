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

try:
	st.set_page_config(page_title="Mercitalia - Automazione LDV / RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)
	st.title("Conversione di codici internazionali a codici Mercitalia")
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
		st.image(os.path.join('images','Slide5.JPG'), use_column_width=True)
		st.write("""
### Descrizione
In questa fase il sistema ha raccolto i dati di mittente e destinatario dalla CIM, eventualmente catturati da Orfeus, ma i codici sono di altri sistemi
per cui viene effettuata una ricerca "fuzzy" sulla ragione sociale nel database Mercitalia. Viene lasciata la possibilità di selezionare la corrispondenza più simile all'operatore.
### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa. La ricerca tra i file di Orfeus è effettuata mediante tradizionale ricerca XML di libreria
- **Azure Blob Storage**: Servizio di storage per file/blob ad alta scalabilità per la lettura dei file di Orfeus e dei file di codifica Clienti Mercitalia
""")

		import pandas as pd
		from fuzzywuzzy import process
		from dotenv import load_dotenv

		# Carica i dati da un file Excel
		excel_path = os.path.join('ldv', 'clienti.xlsx')
		st.write(excel_path)
		df = pd.read_excel(excel_path)

		# Trova la corrispondenza più simile nel DataFrame
		corrispondenze1 = process.extract(st.session_state['box-01'], df['ragione sociale'], limit=5)
		options1 = []

		# Stampa le corrispondenze trovate e i relativi codici
		for corrispondenza in corrispondenze1:
			match = corrispondenza[0]  # La ragione sociale corrispondente
			score = corrispondenza[1]  # Il punteggio di similarità

			# Trova l'indice (o gli indici) nel DataFrame dove c'è questa corrispondenza
			indici = df.index[df['ragione sociale'] == match].tolist()

			# Stampa i dettagli delle corrispondenze trovate

			for indice in indici:
				codice_corrispondente = df.loc[indice, 'codice']
				options1.append(f"{match} - Codice: {codice_corrispondente}, Similarità: {score}")

		st.write(f"Ricerca mittente: {st.session_state['box-01']}")
		st.selectbox("Mittente (Ragioni sociali simili)", options1, placeholder="Seleziona la corrispondenza più simile", key="mittente_scelto")
  
		# Trova la corrispondenza più simile nel DataFrame
		corrispondenze2 = process.extract(st.session_state['box-04'], df['ragione sociale'], limit=5)
		options2 = []
		# Stampa le corrispondenze trovate e i relativi codici
		for corrispondenza in corrispondenze2:
			match = corrispondenza[0]  # La ragione sociale corrispondente
			score = corrispondenza[1]  # Il punteggio di similarità

			# Trova l'indice (o gli indici) nel DataFrame dove c'è questa corrispondenza
			indici = df.index[df['ragione sociale'] == match].tolist()

			# Stampa i dettagli delle corrispondenze trovate
			

			for indice in indici:
				codice_corrispondente = df.loc[indice, 'codice']
				options2.append(f"{match} - Codice: {codice_corrispondente}, Similarità: {score}")
    
		st.write(f"Ricerca mittente: {st.session_state['box-04']}")
		st.selectbox("Destinatario (Ragioni sociali simili)", options2, placeholder="Seleziona la corrispondenza più simile", key="destinatario_scelto")

		if st.button("Conferma i valori"):
			st.toast("Valori confermati. E' possibile procedere con la fase successiva")

  
	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())

	