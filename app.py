import base64
import streamlit as st
from data.db import BudgetingDBSQLite
from data.models import StructuredData, Purchase
from utils.config import load_settings
from utils.llm import MultimodalMessage
from langchain.chat_models import init_chat_model
from typing import List

@st.cache_resource
def initialize_app():
    pass

settings = load_settings('config.yaml')
llm = init_chat_model(settings.model.name, model_provider=settings.model.provider)
llm_structured = llm.with_structured_output(StructuredData)
# it can fail if the model name and provider is wrong? Try except?


if __name__ == '__main__':
    initialize_app()
    db = BudgetingDBSQLite()
    print(settings)
    uploaded_file = st.file_uploader(
        "Choose an image or document containing purchases",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        accept_multiple_files=False
    )
    st.header('Purchases')
    print(db.get_purchases())
    st.dataframe(db.get_purchases())
    if uploaded_file:
        st.write('A file was uploaded')
        print(uploaded_file)
        print(type(uploaded_file))
        #encoded_file = base64.b64encode(uploaded_file.read()).decode('utf-8')
        data = llm_structured.invoke([MultimodalMessage(uploaded_file.name,
          uploaded_file, type='image', prompt='Describe the file')])
        st.write(data.purchases)
        db.insert_purchases(data.purchases)

        # use the llm instance

