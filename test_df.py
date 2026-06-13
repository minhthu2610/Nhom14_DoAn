import streamlit as st
import pandas as pd

df = pd.DataFrame({"A": [1,2], "B": [3,4]})
st.dataframe(df.style.set_properties(**{
    'font-weight': 'bold',
    'color': 'var(--text-color)',
    'background-color': 'var(--background-color)',
    'border': '1px solid var(--text-color)'
}))
