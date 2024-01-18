import streamlit as st
import os
import traceback
import datetime
import pandas as pd

def get_field_from_cim():
	from azure.core.credentials import AzureKeyCredential
	from azure.ai.formrecognizer import DocumentAnalysisClient
	endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
	key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
	model_id = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL_ID")
	model_id = "ldv04"
	document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

	with open("C:/Users/gisudano/OneDrive - Microsoft/Desktop/Prototypes/ITF Mercitalia LDV/LDV samples/3 jpeg extraction/20231107 131436 OK/cim.jpg", "rb") as f:
		poller = document_analysis_client.begin_analyze_document(model_id, document=f)
	result = poller.result()

	fields = {}

	for idx, document in enumerate(result.documents):
		for name, field in document.fields.items():
			fields[name] = field.value

	st.write("Field trovati {}".format(len(fields)))
	return fields

try:
	
	st.title("Lettere di Vettura")
	
	date_begin = st.date_input("Data Inizio", datetime.date(2023, 10, 1))
	date_end = st.date_input("Data Fine", datetime.date(2023, 10, 30))
	
	if st.button("Elabora LdV..."):

		fields = get_field_from_cim()

		llm = AzureChatOpenAI(
			azure_endpoint=os.getenv("AZURE_OPENAI_BASE"), 
			api_key="",
			api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
			max_tokens=1000, 
			temperature=0,
			deployment_name=os.getenv("AZURE_OPENAI_MODEL"),
			model_name=os.getenv("AZURE_OPENAI_MODEL_NAME"),
			streaming=False
		)

		output_parser = StrOutputParser()
		system_message = "Sei un assistente virtuale che aiuta ad estrarre informazioni da testo analizzato con OCR da documenti di trasporto e lettere di vettura."
  		prompt = ChatPromptTemplate.from_messages([("system", system_message),("user", "{input}")])

		chain = prompt | llm | output_parser
		response = chain.invoke({"input": "Hello world..."}))
  
		st.write("Estrazione Dati da Email")
		st.text_input("From:", value=response)
		st.text_input("Oggetto Email:", value="")
		st.text_area("Corpo Email", height=100, value="")
		st.divider()
		st.write("Estrazione Dati da allegati Email")
		
		colbox1_1, colbox1_2, colbox1_3 = st.columns([1,1,1])
		with colbox1_1:
			st.text_area("(1) Mittente", value=fields["box-01"], height=100, key="box1_1")
		with colbox1_2:
			st.text_area("(1) Mittente (Clean)", value="", height=100, key="box1_2")
		with colbox1_3:
			st.text_area("(1) Mittente (Orpheus)", value="", height=100, key="box1_3")
		
		colbox2_1, colbox2_2, colbox2_3 = st.columns([1,1,1])
		with colbox2_1:
			st.text_area("(2) Mittente Codice", value="CZ27881369", height=100, key="box2_1")
		with colbox2_2:
			st.text_area("(2) Mittente Codice (Clean)", value="CZ27881369", height=100, key="box2_2")
		with colbox2_3:
			st.text_area("(2) Mittente Codice (Orpheus)", value="CZ27881369", height=100, key="box2_3")
			
		
		colbox4_1, colbox4_2, colbox4_3 = st.columns([1,1,1])
		with colbox4_1:
			st.text_area("(4) Destinatario", height=100, key="box4_1", value="4 Příjemce (jméno, adresa, země) Empfänger (Name, Anschrift, Land) SILOMAR S.p.A. ADAMANT BIONRG SRL snc Ponte Etiopia IT 16149 Genova Čis. DPH MWSt Nr. IT00246590103")
		with colbox4_2:
			st.text_area("(4) Destinatario (Clean)", height=100, key="box4_2", value="SILOMAR S.p.A. ADAMANT BIONRG SRL snc Ponte Etiopia IT 16149 Genova Čis. DPH MWSt Nr. IT00246590103")
		with colbox4_3:
			st.text_area("(4) Destinatario (Orpheus)", height=100, key="box4_3", value="MOREL DISTRIBUTION PROFILES BP 201 VAT:FR61421649575 Street:St Jean d'Ardières FR Zip 69822 BELLEVILLE CEDEX")
		
		
		colbox5_1, colbox5_2, colbox5_3 = st.columns([1,1,1])
		with colbox5_1:
			st.text_area("(5) Mittente Codice", height=100, key="box5_1", value="047565")
		with colbox5_2:
			st.text_area("(5) Mittente Codice (Clean)", height=100, key="box5_2", value="047565")
		with colbox5_3:
			st.text_area("(5) Mittente Codice (Orpheus)", height=100, key="box5_3", value="322644")
			
		
		colbox10_1, colbox10_2, colbox10_3 = st.columns([1,1,1])
		with colbox10_1:
			st.text_area("(10) Raccordo Consegna", height=100, key="box10_1", value="83046102")
		with colbox10_2:
			st.text_area("(10) Raccordo Consegna (Clean)", height=100, key="box10_2", value="83046102")
		with colbox10_3:
			st.text_area("(10) Raccordo Consegna (Orpheus)", height=100, key="box10_3", value="83046102")
			
		
		colbox12_1, colbox12_2, colbox12_3 = st.columns([1,1,1])
		with colbox12_1:
			st.text_area("(12) Codice Stazione Destinatario", height=100, key="box12_1", value="")
		with colbox12_2:
			st.text_area("(12) Codice Stazione Destinatario (Clean)", height=100, key="box12_2", value="")
		with colbox12_3:
			st.text_area("(12) Codice Stazione Destinatario (Orpheus)", height=100, key="box12_3", value="")
			
		
		colbox13_1, colbox13_2, colbox13_3 = st.columns([1,1,1])
		with colbox13_1:
			st.text_area("(13) Condizioni commerciali", height=100, key="box13_1", value="1 HORNÍ DVOŘIŠTĚ ST.HR ; TARVISIO BOSCOVERDE ; 3 CZ - 2154 ČDC ; AT - 2181 RCA ; IT - 2183 MIR ; 5 CDC:D334101 ; RCA 4159.01 Kdnr 8022774, MIR IN415901 unselected unselected")
		with colbox13_2:
			st.text_area("(13) Condizioni commerciali (Clean)", height=100, key="box13_2", value="1 HORNÍ DVOŘIŠTĚ ST.HR ; TARVISIO BOSCOVERDE ; 3 CZ - 2154 ČDC ; AT - 2181 RCA ; IT - 2183 MIR ; 5 CDC:D334101 ; RCA 4159.01 Kdnr 8022774, MIR IN415901 unselected unselected")
		with colbox13_3:
			st.text_area("(13) Condizioni commerciali (Orpheus)", height=100, key="box13_3", value="1 HORNÍ DVOŘIŠTĚ ST.HR ; TARVISIO BOSCOVERDE ; 3 CZ - 2154 ČDC ; AT - 2181 RCA ; IT - 2183 MIR ; 5 CDC:D334101 ; RCA 4159.01 Kdnr 8022774, MIR IN415901 unselected unselected")

		colbox14_1, colbox14_2, colbox14_3 = st.columns([1,1,1])
		with colbox14_1:
			st.text_area("(14) Codice Condizioni commerciali", height=100, key="box14_1", value="1 D334101")
		with colbox14_2:
			st.text_area("(14) Codice Condizioni commerciali (Clean)", height=100, key="box14_2", value="1 D334101")
		with colbox14_3:
			st.text_area("(14) Condizioni commerciali (Orpheus)", height=100, key="box14_3", value="1 D334101")
		
		colbox16_1, colbox16_2, colbox16_3 = st.columns([1,1,1])
		with colbox16_1:
			st.text_area("(16) Luogo consegna presa in carico", height=100, key="box16_1", value="524215")
		with colbox16_2:
			st.text_area("(16) Luogo consegna presa in carico (Clean)", height=100, key="box16_2", value="524215")
		with colbox16_3:
			st.text_area("(16) Luogo consegna presa in carico (Orpheus)", height=100, key="box16_3", value="524215")
			 
		colbox18_1, colbox18_2, colbox18_3 = st.columns([1,1,1])
		with colbox18_1:
			st.text_area("(18) Matricola carro distinta", height=100, key="box18_1", value="viz výkaz vozů siehe Wagenliste")
		with colbox18_2:
			st.text_area("(18) Matricola carro distinta (Clean)", height=100, key="box18_2", value="viz výkaz vozů siehe Wagenliste")
		with colbox18_3:
			st.text_area("(18) Matricola carro distinta (Orpheus)", height=100, key="box18_3", value="viz výkaz vozů siehe Wagenliste")
		
		colbox49_1, colbox49_2, colbox49_3 = st.columns([1,1,1])
		with colbox49_1:
			st.text_area("(49) Codice Affrancazione", height=100, key="box49_1", value="")
		with colbox49_2:
			st.text_area("(49) Codice Affrancazione (Clean)", height=100, key="box49_2", value="")
		with colbox49_3:
			st.text_area("(49) Codice Affrancazione (Orpheus)", height=100, key="box49_3", value="")
		
		colbox57_1, colbox57_2, colbox57_3 = st.columns([1,1,1])
		with colbox57_1:
			st.text_area("(57) Altro trasporti e ruolo", height=100, key="box57_1", value="")
		with colbox57_2:
			st.text_area("(57) Altro trasporti e ruolo (Clean)", height=100, key="box57_2", value="")
		with colbox57_3:
			st.text_area("(57) Altro trasporti e ruolo (Orpheus)", height=100, key="box57_3", value="")

		col_identificazione1, col_identificazione2, col_identificazione3 = st.columns([1,1,1])
		with col_identificazione1:
			st.write("(62) Identificazione Spedizione")
			st.text_input("Codice Paese", key="ident_paese_1", value="8.1")
			st.text_input("Codice Stazione", key="ident_stazione_1", value="0,3 1 6 6 -6")
			st.text_input("Codice Impresa", key="ident_impresa_1", value="2181")
			st.text_input("Codice Spedizione", key="ident_spedizione_1", value="6849 3-6")
			st.text_input("Luogo e Data", key="ident_luogo_data_1", value="Salzburg 06.10.2023")
		
		with col_identificazione2:
			st.write("(62) Identificazione Spedizione (clean)")
			st.text_input("Codice Paese", key="ident_paese_2", value="81")
			st.text_input("Codice Stazione", key="ident_stazione_2", value="03166-6")
			st.text_input("Codice Impresa", key="ident_impresa_2", value="2181")
			st.text_input("Codice Spedizione", key="ident_spedizione_2", value="68493-6")
			st.text_input("Luogo e Data", key="ident_luogo_data_2", value="Salzburg 06.10.2023")
		
		with col_identificazione3:
			st.write("(62) Identificazione Spedizione (Orpheus)")
			st.text_input("Codice Paese", key="ident_paese_3", value="81")
			st.text_input("Codice Stazione", key="ident_stazione_3", value="03166-6")
			st.text_input("Codice Impresa", key="ident_impresa_3", value="2181")
			st.text_input("Codice Spedizione", key="ident_spedizione_3", value="68493-6")
			st.text_input("Luogo e Data", key="ident_luogo_data_3", value="Salzburg 06.10.2023")

		st.write("Dettagli Vagoni")
		st.text_area("Informazioni di testata", height=200, value="")
		st.text_area("Dettaglio vagoni", height=500, value="")

		
except Exception as e:
	st.error(traceback.format_exc())