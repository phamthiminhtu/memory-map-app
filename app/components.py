import streamlit as st

def render_header():
    st.markdown("""
        <style>
        .header {
            font-size: 24px;
            font-weight: bold;
            color: #1E88E5;
        }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.header("Navigation")
        st.button("Home")
        st.button("Add Memory")
        st.button("View Memories")
        st.button("Settings") 