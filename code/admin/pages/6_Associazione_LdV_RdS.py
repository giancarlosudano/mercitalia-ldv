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
	st.title("Associazione Ldv e RdS")
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
In questa fase il sistema ha raffinato al massimo i dati per una ricerca nel programma di trasporto della RDS ("richiesta di servizio") più appropriata.
A questo scopo **viene utilizzato GPT4 per sviluppare un algoritmo di ricerca**, che imposta le condizioni più adatte e stringenti, necessarie per la ricerca.
### Componenti utilizzati
- **Azure App Service**: Web Container che ospita una applicazione Python che organizza tutta la logica applicativa. La ricerca tra i file di Orfeus è effettuata mediante tradizionale ricerca XML di libreria
- **Azure OpenAI**: Servizio di LLM in modalità GPT4-Turbo per l'automazione del processo di "ragionamento" per la ricerca della RDS più appropriata
""")

		# st.write("### Dati Attuali recuperati")

		# st.write("Origine (codice): " + st.session_state["box-01-orfeus"])
		# st.write("Destinazione (codice) " + st.session_state["box-01-orfeus"])
		# st.write("Codice Contratto (codice): " + st.session_state["box-01-orfeus"])
		# st.write("Data Lettera di Vettura: " + st.session_state["box-01-orfeus"])
		# st.write("Punti frontiera: " + st.session_state["box-01-orfeus"])
		# st.write("Massa totale: " + st.session_state["box-01-orfeus"])
		# st.write("Lunghezza totale: " + st.session_state["box-01-orfeus"])
  
		import pandas as pd
		excel_path = os.path.join('ldv', 'rds-test.xlsx')
		df = pd.read_excel(excel_path)

		from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode		
		gb = GridOptionsBuilder.from_dataframe(df)
		gb.configure_side_bar()
		gridOptions = gb.build()

		data = AgGrid(df,
					gridOptions=gridOptions,
					enable_enterprise_modules=True,
					allow_unsafe_jscode=True,
					update_mode=GridUpdateMode.SELECTION_CHANGED,
					columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

# Origine colonne G H I
# Rete Mittente
# Stazione Mittente
# Des. Stazione Mittente
# Destinazione O P Q
# Rete Destinataria
# Stazione Destinataria
# Des. Stazione Destinataria
# Data RDS (C)
# Contratto (D)
# Mittente/Destinatario (TODO) (F)
# Sequenze PDF (punti di frontiera)
# Sequenza IF (Z)

		st.write("""Prompt GPT4-Turbo
data la lista di servizi ferroviari in tabella

scegli tutte le righe che rispettano questi requisiti:
- la colonna "Rete Mittente" deve essere uguale a **80**
- la colonna "Stazione Mittente" deve essere uguale a **637702**
- la colonna "Rete Destinataria" deve essere uguale a **83**
- la colonna "Stazione Mittente" deve essere uguale a **024323**
- il contratto deve essere uguale a **IN903417**
- la colonna "Data RDS" essere uguale a **07-11-2023** o successiva al massimo di 3 giorni, ignora l'orario

""")
		input = """data questa lista di servizi ferroviari

| ID RDS                          | ID RC       | DATA RDS            | CONTRATTO | Cliente Titolare | Descrizione Cliente Titolare                            | Rete Mittente | Stazione Mittente | Des. Stazione Mittente                                       | Rete Mitt. Effett. | Impianto Mitt. Effett. | Des.Impianto Mitt. Effett.                                   | Raccordo Mittente | Des. Raccordo Mittente                    | Rete Destinataria | Stazione Destinataria | Des. Stazione Destinataria                                   | Rete Dest. Effett. | Impianto Dest. Effett. | Des. Impianto Dest. Effett.                                  | Raccordo Destinatario | Des. Raccordo Destinatario               | IF /Stazione di contatto | Des. IF/Stazione di Contatto                                 | Sequenza ordinata PDF | Sequenza delle IF      | Peso MAX Ammesso | Lunghezza MAX Ammessa | RID SI/NO |
|---------------------------------|-------------|---------------------|-----------|------------------|---------------------------------------------------------|---------------|-------------------|--------------------------------------------------------------|--------------------|------------------------|--------------------------------------------------------------|-------------------|-------------------------------------------|-------------------|-----------------------|--------------------------------------------------------------|--------------------|------------------------|--------------------------------------------------------------|-----------------------|------------------------------------------|--------------------------|--------------------------------------------------------------|-----------------------|------------------------|------------------|-----------------------|-----------|
| 1-111565461_2023-11-07_09:30:00 | 1-111565461 | 07-11-2023 00:00:00 | IN064953  | 057422           | FRET SNCF                                               | 83            | 015222            | LECCO MAGGIANICO                                             | 83                 | 015222                 | LECCO MAGGIANICO                                             | 00BAT             | BATTAZZA SPA                              | 87                | 191015                | Ebange                                                       | 87                 | 191015                 | Ebange                                                       |                       |                                          | 3356                     | BLS Cargo AG                                                 | 259, 321              | 2183, 3356, 2187       | 600              | 400                   | NO        |
| 1-111652340_2023-11-07_16:30:00 | 1-111652340 | 07-11-2023 00:00:00 | IN283010  | 055845           | S.I.T.F.A. S.P.A.                                       | 83            | 002204            | TORINO ORBASSANO                                             | 83                 | 002204                 | TORINO ORBASSANO                                             | 00RF1             | FCA                                       | 51                | 622894                | TYCHY FIAT                                                   | 51                 | 622894                 | TYCHY FIAT                                                   |                       |                                          | 2181                     | RAIL CARGO AUSTRIA AG                                        | 826, 613, 330         | 2183, 2181, 2151       | 600              | 550                   | NO        |
| 1-112019179_2023-11-07_01:20:00 | 1-112019179 | 07-11-2023 00:00:00 | IN519010  | 030468           | GEBRUDER WEISS RAIL CARGO G.M.B.H.                      | 81            | 999901            | AUSTRIA                                                      | 81                 | 999901                 | AUSTRIA                                                      |                   |                                           | 83                | 046102                | GENOVA MARITTIMA                                             | 83                 | 046102                 | GENOVA MARITTIMA                                             | TEGET                 | GETOIL                                   | 2181                     | RAIL CARGO AUSTRIA AG                                        | 330                   | 2181, 2183             | 1600             | 0                     | SI        |
| 1-112210131_2023-11-07_12:30:00 | 1-112210131 | 07-11-2023 00:00:00 | IN903417  | 049832           | DB Cargo AG                                             | 80            | 637702            | Ludwigshafen (Rhein) BASF Ubf                                | 80                 | 637702                 | Ludwigshafen (Rhein) BASF Ubf                                |                   |                                           | 83                | 024323                | VERONA QUADRANTE EUROPA                                      | 83                 | 024323                 | VERONA QUADRANTE EUROPA                                      | 00TEI                 | RFI-TERMINALI ITALIA                     | 3157                     | LOKOMOTION GESELLSCHAFT FUER SCHIENENTRAKTION MBH            | 463, 332              | 2180, 3157, 2183       | 1600             | 540                   | SI        |
| 1-112210191_2023-11-07_03:39:00 | 1-112210191 | 07-11-2023 00:00:00 | IN903417  | 049832           | DB Cargo AG                                             | 83            | 024323            | VERONA QUADRANTE EUROPA                                      | 83                 | 024323                 | VERONA QUADRANTE EUROPA                                      | 00TEI             | RFI-TERMINALI ITALIA                      | 80                | 637702                | Ludwigshafen (Rhein) BASF Ubf                                | 80                 | 637702                 | Ludwigshafen (Rhein) BASF Ubf                                |                       |                                          | 3157                     |                                                              | 463, 332              | 2183, 3157, 2180       | 1300             | 540                   | SI        |
| 1-114533267_2023-11-07_14:17:00 | 1-114533267 | 07-11-2023 00:00:00 | 11661740  | 055845           | S.I.T.F.A. S.P.A.                                       | 83            | 117010            | S.FERDINANDO                                                 | 83                 | 117010                 | S.FERDINANDO                                                 | 00MC1             | TERMINAL MCT                              | 83                | 113001                | S.NICOLA DI MELFI                                            | 83                 | 113001                 | S.NICOLA DI MELFI                                            | 000RF                 | CONSORZIO A.S.I. - FIAT SATA SpA         |                          |                                                              |                       |                        | 800              | 530                   | NO        |
| 1-114853727_2023-11-07_12:13:00 | 1-114853727 | 07-11-2023 00:00:00 | IN902825  | 011827           | VIGLIENZONE ADRIATICA S.P.A.                            | 83            | 025312            | S.PIETRO IN GU'                                              | 83                 | 025312                 | S.PIETRO IN GU'                                              | AGTRA             | AGRICOLA ITALIANA ALIMENTARE S.P.A.       | 00                | 310                   | SEZANA                                                       | 00                 | 00                     | EUROPA                                                       |                       |                                          |                          |                                                              |                       | 2183                   | 750              | 420                   | NO        |
| 1-116193946_2023-11-07_20:15:00 | 1-116193946 | 07-11-2023 00:00:00 | 11662143  | 012885           | TRANSWAGGON  SPA                                        | 83            | 098210            | PONTECAGNANO                                                 | 83                 | 098210                 | PONTECAGNANO                                                 | 000RA             | AUTOMAR SPA                               | 83                | 070185                | FOSSACESIA-TORINO DI SANGRO                                  | 83                 | 070185                 | FOSSACESIA-TORINO DI SANGRO                                  | 00S01                 | SEVEL SPA                                |                          |                                                              |                       |                        | 500              | 530                   | NO        |

scegli le righe che rispettano questi requisiti in modo più preciso possibile:
- la colonna "Rete Mittente" deve essere uguale a 80
- la colonna "Stazione Mittente" deve essere uguale a 637702
- la colonna "Rete Destinataria" deve essere uguale a 83
- la colonna "Stazione Mittente" deve essere uguale a 024323
- il contratto deve essere uguale a IN903417
- la colonna "Data RDS" deve essere uguale a **07-11-2023**, ignora l'orario

Mostra il tuo ragionamento

Risposta:
"""

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

		prompt = ChatPromptTemplate.from_messages([
			("system", "You are an AI assistant."),
			("user", "{input}")
		])

		output_parser = StrOutputParser()
		chain = prompt | llm | output_parser
		response = chain.invoke({"input": input})

		st.write(response)

		if st.button("Conferma i valori"):
			st.toast("Valori confermati. E' possibile procedere con la fase successiva")

	elif st.session_state["authentication_status"] is False:
		st.error('Username/password is incorrect')
	elif st.session_state["authentication_status"] is None:
		st.warning('Please enter your username and password')

except Exception as e:
	st.error(traceback.format_exc())