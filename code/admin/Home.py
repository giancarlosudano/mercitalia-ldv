import sys
import streamlit as st
import os
import logging
from dotenv import load_dotenv
import streamlit_authenticator as stauth
import xml.etree.ElementTree as ET

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

st.set_page_config(page_title="Automazione Lettere di Vettura <=> RDS", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)

st.title("Automazione Processo Acquisizione Lettere di Vettura")
st.subheader("Trasporti internazionali in Import")
st.sidebar.image(os.path.join('images','mercitalia.png'), use_column_width=True)

file_name = "ECTD.20231106_232258_875.xml"
file_path = os.path.join('orpheus', file_name)
    
tree = ET.parse(file_path)
root = tree.getroot()

box_01_orfeus_values = []
box_10_orfeus_values = []

st.write("Analisi XML")
# Iterate through the ECN nodes
for ecn in root.findall(".//ECNs"):
    node = ecn.find(".//ECN/Customers/Customer[@Type='CR']/Name")
    if node is not None:
        st.write("trovato")
        box_01_orfeus_values.append(node.text)
        response = st.write(node.text)

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

name, authentication_status, username = authenticator.login(location='main')

if username == 'smith@mercitalia.com':
    st.session_state["authentication_status"] = True
    st.session_state["name"] = "John Smith"

if st.session_state["authentication_status"]:
    st.write(f'Welcome *{st.session_state["name"]}*, you are an **admin**.')
    
    # # Delete a single key-value pair
    # del st.session_state[key]

    # Delete all the items in Session state
    # for key in st.session_state.keys():
    #     del st.session_state[key]
    
    # Azzeramento delle variabili di sessione
    
    import lib.common as common
    common.clean_session()
    
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')