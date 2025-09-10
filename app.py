import streamlit as st
from utils import assets
from utils import portfolio as pf
from utils import risk as rsk
import plotly.express as px

# Variables
all_tickers = assets.get_tickers()
tickers = ['AAPL','NVDA', 'MSFT', 'META', 'GOOGL']
period = "5y"
initial_capital = 10000
rf = 0.0431

asset_prices = assets.get_price_data(tickers, period)

asset_returns = assets.calc_returns(asset_prices)

equity_curve = assets.equity_curve(asset_returns, initial_capital)

drawdowns = assets.drawdowns(asset_returns)

st.title('Portfolio Risk & Optimization Engine')
tickers = st.multiselect("Select Tickers", all_tickers, default=tickers, max_selections=5)

tabs = st.tabs(["Asset Analysis", "Portfolio Optimization"])

st.sidebar.title("Controls")
rf = st.sidebar.slider("Risk-free Rate", min_value=0.00, max_value=5.00, step=0.01, format="%.2f", value=rf*100)/100

with tabs[0]:
    st.subheader("Growth of Hypothetical $10,000")

    ec_fig = px.line(equity_curve)
    ec_fig.update_layout(xaxis_title="Date", 
                    yaxis_title="Value of Investment (USD)")
    st.plotly_chart(ec_fig)

    st.subheader("Asset Drawdowns")
    dd_fig = px.area(drawdowns)
    dd_fig.update_traces(stackgroup = None, fill = 'tozeroy')
    dd_fig.update_layout(xaxis_title="Date", yaxis_title="Drawdowns (%)")
    st.plotly_chart(dd_fig)

    st.subheader("Distribution of Asset Returns")
    ticker = st.selectbox("Select Asset",tickers, index=0)
    confidence_level = st.select_slider("Select Confidence Level:", ["95%","98%","99%"],"98%").removesuffix('%')
    var, es = rsk.calc_var_es(asset_returns[ticker]*100,int(confidence_level))
    hist_fig = px.histogram(asset_returns[ticker]*100)
    hist_fig.update_layout(xaxis_title="Returns (%)", yaxis_title="Frequency")
    hist_fig.add_vline(
          x=var, line_width=3, line_color="red", annotation_text = f"VaR{confidence_level}: {(var).round(2)}%", 
          annotation_position="top right", annotation_font_size=14, annotation_font_color="red")
    hist_fig.add_vline(
          x=es, line_dash="dot", line_width=3, line_color="blue", annotation_text = f"Expected Shortfall: {(es).round(2)}%", 
          annotation_position="top left", annotation_font_size=14, annotation_font_color="blue")
    
    st.plotly_chart(hist_fig)

    st.subheader("Key Statistics")
    sum_stats = assets.summary_stats(asset_returns, rf)
    st.dataframe(sum_stats)

with tabs[1]:

    eqw = pf.gen_eq_weights(n = len(tickers))
    eqw_pf_returns = pf.calc_pf_returns(asset_returns, eqw)
    eqw_pf_returns.name = "Equal Weight Portfolio"
    #st.dataframe(eqw_pf_returns)
    equity_curve = assets.equity_curve(eqw_pf_returns, initial_capital)

    drawdowns = assets.drawdowns(eqw_pf_returns)

    ec_fig = px.line(equity_curve)
    ec_fig.update_layout(xaxis_title="Date", 
                    yaxis_title="Value of Investment (USD)")
    st.plotly_chart(ec_fig)

    st.subheader("Portfolio Drawdowns")
    dd_fig = px.area(drawdowns)
    dd_fig.update_traces(stackgroup = None, fill = 'tozeroy', line_color='red')
    dd_fig.update_layout(xaxis_title="Date", yaxis_title="Drawdowns (%)")
    st.plotly_chart(dd_fig)

    st.dataframe(pf.gen_random_pfs(1000,tickers))
    