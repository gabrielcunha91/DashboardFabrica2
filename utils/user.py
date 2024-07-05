import streamlit as st
import requests

def login(userName: str, password: str) -> bool:
  if (userName is None):
    return False

  login_data = {
    "username": userName,
    "password": password,
    "loginSource": 1,
  }

  login = requests.post('https://apps.blueprojects.com.br/fb/Security/Login',json=login_data).json()
    
  if "error" in login:
    return False

  else:
    if login['data']['success'] == True:
      return login
    else:
      return False

def logout():
  st.session_state['loggedIn'] = False
  st.switch_page('Login.py')


def handle_login(userName, password):
  #user data deve conter o usuario
  if user_data := login(userName, password):
    st.session_state['loggedIn'] = True
    st.session_state['userName'] = userName 
  else:
    st.session_state['loggedIn'] = False
    st.error("Email ou senha inválidos!!")