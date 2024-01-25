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
	
	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())

	