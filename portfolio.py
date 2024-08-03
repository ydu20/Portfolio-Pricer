import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

SPOT_MIN = 0
SPOT_MAX = 100
SPOT_INIT = 50
VOL_MIN = 0
VOL_MAX = 100
VOL_INIT = 20
CASH_INIT = 1000000

# Session State abbriviation
state = st.session_state

# Define portfolio dataframe
if 'portfolio' not in state:
  state.portfolio = pd.DataFrame(columns = ['Position', 
      'Expiration', 'Quantity', "Avg. Entry", "Market Price", 'Cost', 'Market Value', 'P/L'])

# Define some state variables
if 'cost' not in state:
  state.cost = 50

if 'warning' not in state:
  state.warning = ''

if 'new_prod' not in state:
  state.new_prod = ''

if 'new_qty' not in state:
  state.new_qty = ''

if 'new_strike' not in state:
  state.new_strike = ''

# Helper functions
def add_position():
  # Temp
  state.new_prod = state.product
  state.new_qty = state.quantity
  if state.product == 'Option':
    state.new_strike = state.strike
  
  # Validate position
  if state.quantity == 0:
    state.warning = 'Quantity cannot be 0'
    return
  
  # Generate new position
  pos_name = ''
  pos_exp = "" if state.product == 'Stock' else state.expiration
  if state.product == 'Stock':
    pos_name = 'Stock'
  else:
    pos_name = f'{state.strike} {state.call_put} {state.expiration}D'

  found = False
  for index, row in state.portfolio.iterrows():
    if row['Position'] == pos_name:
      found = True
      qty = state.portfolio.at[index, 'Quantity']
      entry = state.portfolio.at[index, 'Avg. Entry']
      entry = round(((qty * entry) + state.cost) / (qty + state.quantity), 2)
      qty += state.quantity
      state.portfolio.at[index, 'Quantity'] = qty
      state.portfolio.at[index, 'Avg. Entry'] = entry
      state.portfolio.at[index, 'Cost'] = state.portfolio.at[index, 'Cost'] + state.cost
      state.portfolio.at[index, 'Market Value'] = state.portfolio.at[index, 'Market Value'] \
          + state.cost

      # TODO: If positions net out then remove position 


      break
  
  if not found:
    new_pos = {'Position': pos_name, 'Expiration': pos_exp, 'Quantity': state.quantity, 
        'Avg. Entry': state.spot, 'Market Price': state.spot, 'Cost': state.cost, 
        'Market Value': state.cost, 'P/L': 0}
    state.portfolio.loc[len(state.portfolio)] = new_pos

  # TODO: Cash management



def clear_warning():
  state.warning = ''

def update_portfolio():

  return


def update_cost():
  if state.product == 'Stock':
    state.cost = state.quantity * state.spot
  else:
    return 9999

def update_and_clear():
  update_cost()
  clear_warning()

def update_all():
  update_cost()
  update_portfolio()

# Main display
st.title('Options Portfolio Pricer')

st.slider('Spot', SPOT_MIN, SPOT_MAX, SPOT_INIT, key = 'spot', on_change = update_all)
st.slider('Implied Volatility', VOL_MIN, VOL_MAX, VOL_INIT, key = 'vol', on_change = update_all)

# Portfolio
st.subheader('Portfolio')

st.dataframe(state.portfolio, width = 1000, hide_index = True)



# Temp new entry
st.subheader('New Entry:')
if state.new_prod != '':
  st.markdown(f'Product: {state.new_prod}')
  st.markdown(f'Quantity: {state.new_qty}')
  if state.new_prod == 'Option':
    st.markdown(f'Strike: {state.new_strike}')

st.markdown(state.warning)


# Sidebar display
with st.sidebar:
  st.title('New Position')
  product = st.selectbox('Stock / Option', ['Stock', 'Option'], 
                            key = 'product')
  
  if (product == 'Option'):
    st.selectbox('Call/Put', ['Call', 'Put'], key='call_put', on_change = update_cost)
    st.number_input('Strike', min_value = SPOT_MIN, max_value = SPOT_MAX, 
                    value = state.spot, step = 1, key='strike', on_change = update_cost)
    st.number_input('Days to Expiration', min_value = 1, max_value = 500, 
                    value = 10, step = 1, key = 'expiration', on_change = update_cost)

  st.number_input('Quantity', min_value = -1000000, max_value = 1000000, 
                    value = 1, step = 1, key='quantity', on_change = update_and_clear)
  
  st.markdown(f'Cost: {state.cost}')

  st.button('Enter', on_click = add_position)

  st.markdown(f':red[{state.warning}]')

