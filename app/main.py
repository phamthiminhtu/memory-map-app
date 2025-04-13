import streamlit as st
from components import render_header, render_sidebar

def main():
    st.set_page_config(
        page_title="Memory Map",
        page_icon="🗺️",
        layout="wide"
    )
    
    render_header()
    render_sidebar()
    
    st.title("Memory Map")
    st.write("Welcome to your personal memory mapping application!")

if __name__ == "__main__":
    main() 