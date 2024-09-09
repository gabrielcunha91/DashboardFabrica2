import streamlit as st
import pandas as pd
from babel.dates import format_date
from utils.queries import *
from utils.functions.cmv import *
from utils.functions.dados_gerais import *
from utils.components import *
from utils.user import logout

st.set_page_config(
  layout = 'wide',
  page_title = 'DRE',
  page_icon=':⚖',
  initial_sidebar_state="collapsed"
)  
pd.set_option('future.no_silent_downcasting', True)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')


