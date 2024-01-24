import streamlit as st
import os
import traceback
from datetime import datetime
import pandas as pd
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import xml.etree.ElementTree as ET


def plus_one():
    if st.session_state["slider"] < 10:
        st.session_state.slider += 1
    else:
        pass
    return


try:
	st.title("Lettere di Vettura")
	add_one = st.button("Add one to the slider", on_click=plus_one, key="add_one")
	slide_val = st.slider("Pick a number", 0, 10, key="slider")	

except Exception as e:
	st.error(traceback.format_exc())