import sys
import streamlit as st
import os
import logging
from dotenv import load_dotenv
import streamlit_authenticator as stauth

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
st.set_page_config(page_title="Automazione Lettere di Vettura <=> RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)

st.title("Automazione Processo Acquisizione Lettere di Vettura")
st.subheader("Trasporti internazionali in Import")
st.sidebar.image(os.path.join('images','mercitalia.png'), use_column_width=True)

print('--------------------------------')
print(' NEW SESSION ')
print('--------------------------------')
print(os.getenv("AZURE_OPENAI_BASE")) 
print(os.getenv("AZURE_OPENAI_KEY"))

import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)
authenticator.logout(location='sidebar')

authenticator.login(location='main')

if st.session_state['authentication_status']:
    st.write(f'Welcome, you are logged in as {st.session_state["username"]}!')