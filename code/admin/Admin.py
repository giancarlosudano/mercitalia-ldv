import sys
import streamlit as st
import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

st.set_page_config(page_title="Admin", page_icon=os.path.join('images','favicon.ico'), layout="wide", menu_items=None)

mod_page_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(mod_page_style, unsafe_allow_html=True)

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
response = llm.invoke("Hello world...")

st.write(response.content)
