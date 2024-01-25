
import pandas as pd
	from fuzzywuzzy import process
	from dotenv import load_dotenv

	# Carica i dati da un file Excel
	df = pd.read_excel(os.path.join('codici', "clienti.xslx"))

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

		st.selectbox("Ragioni sociali simili", options=[], placeholder="Seleziona la corrispondenza più simile", key="codice_destinatario_scelto")
