import streamlit as st
import pandas as pd
import numpy as np

SPOT_MIN = 0
SPOT_MAX = 100
SPOT_INIT = 50

st.title('Options Portfolio Pricer')

spot = st.slider('Spot', SPOT_MIN, SPOT_MAX, SPOT_INIT)

if 'new_prod' not in st.session_state:
  st.session_state.new_prod = ''

if 'new_qty' not in st.session_state:
  st.session_state.new_qty = ''

if 'new_strike' not in st.session_state:
  st.session_state.new_strike = ''

def add_position():
  st.session_state.new_prod = st.session_state.product
  st.session_state.new_qty = st.session_state.quantity
  if st.session_state.product == 'Option':
    st.session_state.new_strike = st.session_state.strike


def calculate_cost():
  print("HEllo")

st.subheader('New Entry:')
if st.session_state.new_prod != '':
  st.markdown(f'Product: {st.session_state.new_prod}')
  st.markdown(f'Quantity: {st.session_state.new_qty}')
  if st.session_state.new_prod == 'Option':
    st.markdown(f'Strike: {st.session_state.new_strike}')


with st.sidebar:
  product = st.selectbox('Stock / Option', ['Stock', 'Option'], 
                         key = 'product')

  with st.form('new_position'):
    st.subheader(f'New {product} Position')
    # st.selectbox('Buy/Sell', ['Buy', 'Sell'], key='buy_sell')
    
    if (product == 'Option'):
      st.selectbox('Call/Put', ['Call', 'Put'], key='call_put')
      st.number_input('Strike', min_value = SPOT_MIN, max_value = SPOT_MAX, 
                      value = spot, step = 1, key='strike')

    st.number_input('Quantity', min_value = -1000000, max_value = 1000000, 
                    value = 1, step = 1, key='quantity')
    st.form_submit_button('Add', on_click = add_position)
