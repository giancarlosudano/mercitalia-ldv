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
# mod_page_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(mod_page_style, unsafe_allow_html=True)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_BASE"), 
    api_key="", # ???
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

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient


endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

model_id = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL_ID")
formUrl = "YOUR_DOCUMENT"

st.write(endpoint)
st.write(key)
st.write(endpoint)


document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

# Make sure your document's type is included in the list of document types the custom model can analyze
#poller = document_analysis_client.begin_analyze_document_from_url(model_id, formUrl)

with open("C:/Users/gisudano/OneDrive - Microsoft/Desktop/Prototypes/ITF Mercitalia LDV/LDV samples/3 jpeg extraction/20231107 131436 OK/cim.jpg", "rb") as f:
    poller = document_analysis_client.begin_analyze_document(model_id, document=f)
result = poller.result()

for idx, document in enumerate(result.documents):
    print("--------Analyzing document #{}--------".format(idx + 1))
    print("Document has type {}".format(document.doc_type))
    print("Document has confidence {}".format(document.confidence))
    print("Document was analyzed by model with ID {}".format(result.model_id))
    for name, field in document.fields.items():
        field_value = field.value if field.value else field.content
        print("......found field of type '{}' with value '{}' and with confidence {}".format(field.value_type, field_value, field.confidence))

# iterate over tables, lines, and selection marks on each page
for page in result.pages:
    print("\nLines found on page {}".format(page.page_number))
    for line in page.lines:
        print("...Line '{}'".format(line.content.encode('utf-8')))
    for word in page.words:
        print(
            "...Word '{}' has a confidence of {}".format(
                word.content.encode('utf-8'), word.confidence
            )
        )
    for selection_mark in page.selection_marks:
        print(
            "...Selection mark is '{}' and has a confidence of {}".format(
                selection_mark.state, selection_mark.confidence
            )
        )

for i, table in enumerate(result.tables):
    print("\nTable {} can be found on page:".format(i + 1))
    for region in table.bounding_regions:
        print("...{}".format(i + 1, region.page_number))
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has content '{}'".format(
                cell.row_index, cell.column_index, cell.content.encode('utf-8')
            )
        )
print("-----------------------------------")

