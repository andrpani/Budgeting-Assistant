import streamlit as st
from data.db import db_init, get_purchases 

@st.cache_resource
def initialize_db():
    db_init('data/schema.sql')


if __name__ == '__main__':
    initialize_db()
    st.header('Purchases')
    st.dataframe(get_purchases())