import base64
import streamlit as st
import pandas as pd
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
    st.title('Welcome to the Budgeting Assistant App! 👋🏻')
    st.header('File analyzer')
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()
    uploaded_file = st.file_uploader(
        "Choose an image or document containing purchases",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        accept_multiple_files=False
    )
    if uploaded_file:
        #st.write('A file was uploaded')
        st.image(uploaded_file.getvalue())
        #if uploaded_file.file_id not in st.session_state.processed_files:
        st.session_state.processed_files.add(uploaded_file.file_id)
        print(uploaded_file)
        print(type(uploaded_file))
        with st.spinner('Model is analyzing data...', show_time=True):
            data = llm_structured.invoke([MultimodalMessage(uploaded_file.name,
            uploaded_file, type='image', prompt='Describe the file')])
        st.write(data.purchases)
        hint = st.text_input("Give an hint to the model")
        left, right = st.columns(2)
        if left.button('Confirm', width='stretch', icon='🆗'):
            left.markdown('confirmed')
            #st.rerun()
            #db.insert_purchases(data.purchases)
        if right.button('Try again', width='stretch', icon='🔄'):
            right.write(f'Model will retry with: {hint}')
            #uploaded_file.close()
            
    


