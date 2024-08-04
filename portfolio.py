import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm

SPOT_MIN = 0
SPOT_MAX = 100
SPOT_INIT = 50
VOL_MIN = 0
VOL_MAX = 100
VOL_INIT = 20
CASH_INIT = 1000
EXPY_INIT = 20
RF_RATE = 0.04
DAY_COUNT = 252

# Session State abbriviation
state = st.session_state

# Define portfolio dataframe
if 'portfolio' not in state:
  state.portfolio = pd.DataFrame(columns = ['Position', 
      'Expiration', 'Quantity', "Avg. Entry", "Market Price", 'Cost', 'Market Value', 'P/L'])

# Define some state variables
if 'cost' not in state:
  state.cost = SPOT_INIT

if 'warning' not in state:
  state.warning = ''

if 'strike' not in state:
  state.strike = SPOT_INIT

if 'expiration' not in state:
  state.expiration = EXPY_INIT

if 'call_put' not in state:
  state.call_put = 'Call'

if 'portfolio_value' not in state:
  state.portfolio_value = CASH_INIT

if 'cash_value' not in state:
  state.cash_value = CASH_INIT


# Helper functions
def price_option(K, expiration, is_call):
  S = state.spot
  T = expiration / DAY_COUNT
  R = RF_RATE
  sigma = state.vol / 100

  d1 = (np.log(S / K) + (R + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
  d2 = d1 - sigma * np.sqrt(T)

  if is_call:
    return max(0.01, round(S * norm.cdf(d1) - K * np.exp(-R * T) * norm.cdf(d2), 2))
  else:
    return max(0.01, round(K * np.exp(-R * T) * norm.cdf(-d2) - S * norm.cdf(-d1), 2))


def add_position():
  # Validate position
  if state.quantity == 0:
    state.warning = 'Quantity cannot be 0'
    return
  
  # TODO: Check if has enough cash

  
  # Generate new position
  pos_name = ''
  pos_exp = "" if state.product == 'Stock' else state.expiration
  if state.product == 'Stock':
    pos_name = 'Stock'
  else:
    pos_name = f'{state.strike} {state.call_put} {state.expiration}D'

  found = False
  to_remove = -1
  for index, row in state.portfolio.iterrows():
    if row['Position'] == pos_name:
      found = True
      qty = state.portfolio.at[index, 'Quantity']
      # Remove if positions net out
      if qty + state.quantity == 0:
        to_remove = index
        break
      
      # Update position
      entry = state.portfolio.at[index, 'Avg. Entry']
      entry = round(((qty * entry) + state.cost) / (qty + state.quantity), 2)
      qty += state.quantity
      state.portfolio.at[index, 'Quantity'] = qty
      state.portfolio.at[index, 'Avg. Entry'] = entry
      state.portfolio.at[index, 'Cost'] = state.portfolio.at[index, 'Cost'] + state.cost
      state.portfolio.at[index, 'Market Value'] = state.portfolio.at[index, 'Market Value'] \
          + state.cost
      break
  
  if to_remove > -1:
    state.portfolio.drop([to_remove], inplace=True)

  if not found:
    new_pos = {'Position': pos_name, 'Expiration': pos_exp, 'Quantity': state.quantity, 
        'Avg. Entry': state.spot, 'Market Price': state.spot, 'Cost': state.cost, 
        'Market Value': state.cost, 'P/L': 0}
    state.portfolio.loc[len(state.portfolio)] = new_pos

  # Update cash position
  state.cash_value -= state.cost

def clear_warning():
  state.warning = ''

def update_portfolio():
  return

def update_cost():
  if state.product == 'Stock':
    state.cost = state.quantity * state.spot
  else:
    state.cost = state.quantity * price_option(state.strike, state.expiration, state.call_put == 'Call')

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

# Portfolio value
st.markdown(f'<div style="text-align: right;">Portfolio value: {"{:,}".format(state.portfolio_value)}</div>', 
            unsafe_allow_html=True)
st.markdown(f'<div style="text-align: right;">Cash value: {"{:,}".format(state.cash_value)}</div>', 
            unsafe_allow_html=True)



# Sidebar display
with st.sidebar:
  st.title('New Position')
  product = st.selectbox('Stock / Option', ['Stock', 'Option'], 
                            key = 'product', on_change = update_cost)
  
  if (product == 'Option'):
    st.selectbox('Call/Put', ['Call', 'Put'], key='call_put', on_change = update_cost)
    st.number_input('Strike', min_value = 1, max_value = SPOT_MAX, 
                    value = SPOT_INIT, step = 1, key='strike', on_change = update_cost)
    st.number_input('Days to Expiration', min_value = 1, max_value = 500, 
                    value = EXPY_INIT, step = 1, key = 'expiration', on_change = update_cost)

  st.number_input('Quantity', min_value = -1000000, max_value = 1000000, 
                    value = 1, step = 1, key='quantity', on_change = update_and_clear)
  
  st.markdown(f'Cost: {state.cost}')

  st.button('Enter', on_click = add_position)

  st.markdown(f':red[{state.warning}]')

