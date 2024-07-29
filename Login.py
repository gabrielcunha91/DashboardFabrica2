import streamlit as st
from utils.user import *


st.set_page_config(
  initial_sidebar_state="collapsed",
  page_title="Login",
  page_icon="🔑",
  layout="centered",
)

def main():
  st.markdown("""
    <style>
      section[data-testid="stSidebar"][aria-expanded="true"]{
        display: none;
      }
    </style>
    """, unsafe_allow_html=True)
  if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False

  if not st.session_state['loggedIn']:
    st.title("Dashboard Fábrica de Bares")
    st.write("Insira seus dados de login:")
    userName = st.text_input(label=" ", value="", placeholder="Email")
    password = st.text_input(label=" ", value="", placeholder="Senha", type="password")
    st.button("Login", on_click=handle_login, args=(userName, password))
    st.stop()
  
  else:
    st.write("Você está logado!")
    st.markdown("Redirecionando para a página de Faturamento...")
    st.switch_page("pages/Faturamento_Zig.py")



if __name__ == "__main__":
  main()

