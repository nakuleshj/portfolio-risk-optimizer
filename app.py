import streamlit as st
from utils import assets
from utils import portfolio as pf
from utils import risk as rsk
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Variables
all_tickers = assets.get_tickers()
period = "5y"
initial_capital = 10000
rf = 0.0431

st.title("Portfolio Risk & Optimization Engine")
tickers = st.multiselect(
    "Portfolio Tickers",
    all_tickers,
    default=["AAPL", "XOM", "JPM", "GLD"],
    max_selections=5,
)


@st.cache_data(ttl=3600)
def get_asset_prices(tickers, period):
    return assets.get_price_data(tickers, period)


asset_prices = get_asset_prices(tickers, period)

asset_returns = assets.calc_returns(asset_prices)

equity_curve = assets.equity_curve(asset_returns, initial_capital)

drawdowns = assets.drawdowns(asset_returns)

tabs = st.tabs(["Asset Analysis", "Portfolio Optimization", "Risk Engine (VaR/ES)"])

st.sidebar.subheader("Portfolio Optimization Controls")
initial_capital = st.sidebar.number_input(
    "Initial Investment:", min_value=1000, max_value=100000, value=10000
)
rf = (
    st.sidebar.slider(
        "Risk-free Rate",
        min_value=0.00,
        max_value=5.00,
        step=0.01,
        format="%.2f",
        value=rf * 100,
    )
    / 100
)
n_rand_pf = st.sidebar.slider(
    "No. of Random Portfolios", min_value=500, max_value=10000, step=500, value=10000
)

with tabs[0]:
    st.subheader("Growth of Hypothetical $10,000")

    ec_fig = px.line(equity_curve)
    ec_fig.update_layout(xaxis_title="Date", yaxis_title="Value of Investment (USD)")
    st.plotly_chart(ec_fig)

    st.subheader("Asset Drawdowns")
    dd_fig = px.area(drawdowns)
    dd_fig.update_traces(stackgroup=None, fill="tozeroy")
    dd_fig.update_layout(xaxis_title="Date", yaxis_title="Drawdowns (%)")
    st.plotly_chart(dd_fig)

    st.subheader("Distribution of Asset Returns")
    ticker = st.selectbox("Select Asset", tickers, index=0)
    confidence_level = st.select_slider(
        "Select Confidence Level:", ["95%", "98%", "99%"], "98%"
    ).removesuffix("%")
    var, es = rsk.calc_var_es(asset_returns[ticker] * 100, int(confidence_level))
    hist_fig = px.histogram(asset_returns[ticker] * 100)
    hist_fig.update_layout(xaxis_title="Returns (%)", yaxis_title="Frequency")
    hist_fig.add_vline(
        x=var,
        line_width=3,
        line_color="red",
        annotation_text=f"VaR{confidence_level}: {(var).round(2)}%",
        annotation_position="top right",
        annotation_font_size=14,
        annotation_font_color="red",
    )
    hist_fig.add_vline(
        x=es,
        line_dash="dot",
        line_width=3,
        line_color="blue",
        annotation_text=f"Expected Shortfall: {(es).round(2)}%",
        annotation_position="top left",
        annotation_font_size=14,
        annotation_font_color="blue",
    )

    st.plotly_chart(hist_fig)

    st.subheader("Key Statistics")
    sum_stats = assets.summary_stats(asset_returns, rf)
    st.dataframe(sum_stats)

with tabs[1]:
    random_pfs_weights = pf.gen_random_pfs(n_rand_pf, tickers)
    random_pfs = pf.calc_pf_metrics(random_pfs_weights, asset_returns, rf)

    st.subheader("Efficient Frontier:")

    msr_pf = random_pfs.copy()
    msr_pf = msr_pf.sort_values(by="Sharpe", ascending=False).iloc[0]
    gmv_pf = random_pfs.copy()
    gmv_pf = gmv_pf.sort_values(by="Volatility").iloc[0]
    mpt_fig = px.scatter(
        random_pfs,
        x="Volatility",
        y="Return",
        color="Sharpe",
        color_continuous_scale="purples",
    )
    mpt_fig.add_trace(
        go.Scattergl(
            x=[msr_pf["Volatility"]],
            y=[msr_pf["Return"]],
            mode="markers",
            marker=dict(
                color="red",
                symbol="diamond",
                size=10,
                line=dict(width=2, color="black"),
            ),
            name="MSR Portfolio",
        )
    )
    mpt_fig.add_trace(
        go.Scattergl(
            x=[gmv_pf["Volatility"]],
            y=[gmv_pf["Return"]],
            mode="markers",
            marker=dict(
                color="green",
                symbol="square",
                size=10,
                line=dict(width=2, color="black"),
            ),
            name="GMV Portfolio",
        )
    )
    mpt_fig.update_layout(coloraxis_colorbar=dict(yanchor="top", y=0.8, x=1.02))
    st.plotly_chart(mpt_fig)

    st.subheader("Portfolio Analysis")
    eqw_pf = pf.gen_eq_weights(n=len(tickers))
    eqw_pf = pd.Series(eqw_pf, index=tickers)
    pf_map = {
        "Equally Weighted": eqw_pf,
        "Max Sharpe Ratio (MSR)": msr_pf,
        "Global Minimum Volatility (GMV)": gmv_pf,
    }

    cols_pie = st.columns(2)

    dds = {}
    ec = {}
    for i, k in enumerate(pf_map.keys()):
        selected_pf = pf_map.get(k)[tickers].sort_values()
        pf_returns = pf.calc_pf_returns(asset_returns, pf_map.get(k)[tickers])
        # pf_returns.name = k
        equity_curve_pf = assets.equity_curve(pf_returns, initial_capital)
        drawdowns_pf = assets.drawdowns(pf_returns)
        ec[k] = equity_curve_pf
        dds[k] = drawdowns_pf
        alloc_fig = px.pie(
            selected_pf, names=selected_pf.index, values=selected_pf.values, title=k
        )
        st.plotly_chart(alloc_fig)

    st.subheader(f"Growth of Hypothetical ${initial_capital:,}")

    ec_df = pd.DataFrame(ec)
    dds_df = pd.DataFrame(dds)

    ec_df.columns.name = "Portfolios:"
    ec_fig = px.line(ec_df)
    ec_fig.update_layout(
        xaxis_title="Date", yaxis_title="Value of Investment (USD)", showlegend=True
    )
    st.plotly_chart(ec_fig)

    st.subheader("Drawdowns")
    dds_df.columns.name = "Portfolios:"
    dd_fig = px.area(dds_df)
    dd_fig.update_traces(stackgroup=None, fill="tozeroy")
    dd_fig.update_layout(
        xaxis_title="Date", yaxis_title="Drawdowns (%)", showlegend=True
    )
    st.plotly_chart(dd_fig)

with tabs[2]:
    st.subheader("Portfolio PnL")
