import streamlit as st
from utils import assets
import plotly.express as px

# Variables
tickers = ['AAPL','NVDA', 'MSFT', 'META', 'GOOGL']
period = "5y"
initial_capital = 10000


asset_prices = assets.get_price_data(tickers, period)

asset_returns = assets.calc_returns(asset_prices)

equity_curve = assets.equity_curve(asset_returns, initial_capital)

drawdowns = assets.drawdowns(asset_returns)

st.subheader("Summary")

st.subheader("Growth of Hypothetical $10,000")

ec_fig = px.line(equity_curve)
ec_fig.update_layout(xaxis_title="Date", 
                  yaxis_title="Value of Investment (USD)")

st.plotly_chart(ec_fig)


st.subheader("Asset Drawdowns")
dd_fig = px.area(drawdowns)
dd_fig.update_traces(stackgroup=None, fill='tozeroy')
dd_fig.update_layout(xaxis_title="Date", 
                  yaxis_title="Drawdowns (%)")
st.plotly_chart(dd_fig)