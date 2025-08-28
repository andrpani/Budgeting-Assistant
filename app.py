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
    st.header('Purchases')
    purchases = db.get_purchases()
    purchase_df = pd.DataFrame(purchases)
    st.dataframe(purchase_df)
    st.header('Purchase Items')
    st.dataframe(db.get_purchase_items(purchases))
    if not purchase_df.empty:
        st.metric('Total spent', f'{purchase_df['Total'].sum():.2f}')
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()
    uploaded_file = st.file_uploader(
        "Choose an image or document containing purchases",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        accept_multiple_files=False
    )
    if uploaded_file and uploaded_file.file_id not in st.session_state.processed_files:
        st.write('A file was uploaded')
        st.session_state.processed_files.add(uploaded_file.file_id)
        print(uploaded_file)
        print(type(uploaded_file))
        with st.spinner('Model is analyzing data...', show_time=True):
            data = llm_structured.invoke([MultimodalMessage(uploaded_file.name,
            uploaded_file, type='image', prompt='Describe the file')])
        st.write(data.purchases)
        db.insert_purchases(data.purchases)
        uploaded_file.close()
        st.rerun()
    


