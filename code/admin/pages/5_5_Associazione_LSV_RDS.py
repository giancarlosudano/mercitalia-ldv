import streamlit as st
import os
import traceback
from datetime import datetime
import pandas as pd
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import StreamlitCallbackHandler
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
	st.title("Scelta della RDS con 'inferenza logica' di GPT4")
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
		st.image(os.path.join('images','Slide6.JPG'), use_column_width=True)
		st.write("""
### Descrizione
In questa fase il sistema ha raffinato al massimo i dati per una ricerca nel programma di trasporto della "RDS (richiesta di servizio)" più appropriata
Viene utilizzato GPT4 per sviluppare un algoritmo di ricerca che imposta le condizioni più adatte e stringenti per selezionare la RDS più appropriata
### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa. La ricerca tra i file di Orfeus è effettuata mediante tradizionale ricerca XML di libreria
- **Azure OpenAI**: Servizio di LLM in modalità GPT4-Turbo per l'automazione del processo di "ragionamento" per la ricerca della RDS più appropriata
""")

		st.write("### Dati Attuali recuperati")

		st.write("Origine: " + st.session_state["box-01-orfeus"])
		st.write("Destinazione: " + st.session_state["box-01-orfeus"])
		st.write("Codice Mittente: " + st.session_state["box-01-orfeus"])
		st.write("Codice Destinatario: " + st.session_state["box-01-orfeus"])
		st.write("Punti frontiera: " + st.session_state["box-01-orfeus"])
		st.write("Massa: " + st.session_state["box-01-orfeus"])
		st.write("Lunghezza: " + st.session_state["box-01-orfeus"])

		container_stream = st.container()

		llm = AzureChatOpenAI(
			azure_endpoint=os.getenv("AZURE_OPENAI_BASE"), 
			api_key=os.getenv("AZURE_OPENAI_KEY"),
			api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
			max_tokens=1000, 
			temperature=0,
			deployment_name=os.getenv("AZURE_OPENAI_MODEL"),
			model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
			streaming=True, callbacks=[StreamlitCallbackHandler(container_stream)]
		)

		prompt = ChatPromptTemplate.from_messages([
			("system", "You are an AI assistant."),
			("user", "{input}")
		])

		output_parser = StrOutputParser()

		input = """
		data questa lista di servizi ferroviari

		|ID|Origine|Destinazione|Contratto|Data|Cliente Mittente|Cliente Destinatario|Sequenza Punti Frontiera|Sequenza Imprese Ferroviarie|Peso|Lunghezza|
		|1|10400|15677|AA|22/11/2023|cliente 1|cliente dest 1|||1000|500|
		|2|10400|14566|AA|23/11/2023|cliente 2|cliente dest 2|||1000|500|
		|3|10400|15677|BB|24/11/2023|cliente 3|cliente dest 3|||1000|500|
		|4|10400|15677|CC|25/11/2023|cliente 4|cliente dest 4|||1000|500|
		|5|10400|15677|DD|26/11/2023|cliente 5|cliente dest 5|||1003|500|
		|6|10400|15677|AA|27/11/2023|cliente 6|cliente dest 6|||1000|500|
		|7|15067|15677|AA|28/11/2023|cliente 7|cliente dest 7|||1000|500|
		|8|45666|15677|AA|29/11/2023|cliente 8|cliente dest 8|||1000|500|
		|9|45667|15677|AA|30/11/2023|cliente 9|cliente dest 9|||1000|500|
		|10|45667|15677|AA|01/12/2023|cliente 10|cliente dest 10|||1500|500|
		|11|10400|15677|AA|02/12/2023|cliente 11|cliente dest 11|||1000|500|
		|12|34566|15677|AA|03/12/2023|cliente 12|cliente dest 12|||1000|500|
		|13|12333|15677|AA|04/12/2023|cliente 13|cliente dest 13|||1000|500|
		|14|45555|15677|AA|05/12/2023|cliente 14|cliente dest 14|||1000|500|
		|15|10400|15677|AA|06/12/2023|cliente 15|cliente dest 15|||1000|500|
		|16|10400|15677|AA|07/12/2023|cliente 16|cliente dest 16|||1000|500|

		scegli tutte le righe che rispettano questi requisiti:
		- la colonna origine deve essere uguale a 10400
		- la colonna destinazione deve essere uguale a 14566
		- il contratto deve essere uguale a AA
		- la data deve essere >= del 23-11-2023
		- il cliente deve essere uguale a "cliente 2"
		"""

		chain = prompt | llm | output_parser
		response = chain.invoke({"input": input})
		container_stream.empty()
	
	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())

	