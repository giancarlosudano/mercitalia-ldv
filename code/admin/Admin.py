import streamlit as st
import os
import logging
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

st.set_page_config(page_title="Admin", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)

# mod_page_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(mod_page_style, unsafe_allow_html=True)


from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = AzureChatOpenAI(
    azure_endpoint="https://mtcmilanoaiswe.openai.azure.com/", 
    api_key="c0761999a40748df99cd2f2959b52c2f", 
    api_version="2023-07-01-preview",
    max_tokens=1000, 
    temperature=0,
    deployment_name="gpt-4",
    model_name="gpt-4",
    streaming=False
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant."),
    ("user", "{input}")
])

output_parser = StrOutputParser()

chain = prompt | llm | output_parser
response = llm.invoke("Hello, how are you?")

st.write(response.content)

