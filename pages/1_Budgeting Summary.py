import streamlit as st
import pandas as pd
from data.db import BudgetingDBSQLite

db = BudgetingDBSQLite()

st.title('💸 Budgeting Summary ')

st.header('Purchases')
purchases = db.get_purchases()
purchase_df = pd.DataFrame(purchases)
st.dataframe(purchase_df)
st.header('Purchase Items')
st.dataframe(db.get_purchase_items(purchases))
if not purchase_df.empty:
    st.metric('Total spent', f'{purchase_df['Total'].sum():.2f} €')