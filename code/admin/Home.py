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

# mod_page_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(mod_page_style, unsafe_allow_html=True)

st.title("Automazione Processo Acquisizione Lettere di Vettura")
st.subheader("Trasporti internazionali in Import")
# st.subheader("Utilizzo di generative AI per l'automazione del processo di assegnazione delle lettere di vettura alle RDS")
st.sidebar.image(os.path.join('images','mercitalia.png'), use_column_width=True)
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