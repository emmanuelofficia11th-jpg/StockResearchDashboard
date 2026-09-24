import streamlit as st
import plotly.graph_objects as go

from main import (
    get_stock_data,
    calculate_financial_health,
    calculate_performance,
    calculate_technical_metrics,
    calculate_stock_score,
    format_large_number,
    format_percentage,
    format_ratio
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Stock Research Dashboard",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# CUSTOM FORMATTING
# ============================================================

def format_price(value):

    if value is None:
        return "N/A"

    return f"${value:,.2f}"


def score_label(score):

    if score >= 8:
        return "Strong"

    elif score >= 6:
        return "Good"

    elif score >= 4:
        return "Moderate"

    else:
        return "Weak"


# ============================================================
# PRICE CHART
# ============================================================

def create_price_chart(history, ticker):

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=history.index,
            y=history["Close"],
            mode="lines",
            name=ticker
        )
    )

    figure.update_layout(
        title=f"{ticker} — 1 Year Price History",
        xaxis_title="Date",
        yaxis_title="Price",
        height=500,
        hovermode="x unified"
    )

    return figure


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 Stock Research")

st.sidebar.write(
    "Search for a company using its stock ticker."
)

ticker = st.sidebar.text_input(
    "Stock ticker",
    value="NVDA",
    placeholder="e.g. AAPL"
).upper().strip()

analyse = st.sidebar.button(
    "Analyse Stock",
    type="primary",
    use_container_width=True
)

st.sidebar.divider()

st.sidebar.caption(
    "Research dashboard built using Python, "
    "Streamlit and financial market data."
)


# ============================================================
# MAIN HEADER
# ============================================================

st.title("📈 Stock Research Dashboard")

st.write(
    "Fundamental, valuation, financial health, "
    "risk and momentum analysis in one place."
)

st.divider()


# ============================================================
# INITIAL SCREEN
# ============================================================

if not analyse:

    st.info(
        "Enter a ticker in the sidebar and click **Analyse Stock**."
    )

    st.write("Try:")

    st.code("NVDA   AAPL   MSFT   GOOGL   AMZN")

    st.stop()


# ============================================================
# RETRIEVE DATA
# ============================================================

try:

    with st.spinner(
        f"Retrieving and analysing {ticker}..."
    ):

        stock, info, history = get_stock_data(ticker)

        if history.empty:
            st.error(
                "No historical data was found for this ticker."
            )
            st.stop()

        financial_health = calculate_financial_health(info)

        performance = calculate_performance(history)

        technical = calculate_technical_metrics(history)

        scores = calculate_stock_score(
            info,
            financial_health,
            performance,
            technical
        )


except Exception as error:

    st.error(
        "The stock could not be analysed. "
        "Check the ticker and try again."
    )

    with st.expander("Technical details"):
        st.write(error)

    st.stop()


# ============================================================
# COMPANY PROFILE
# ============================================================

company_name = info.get("longName", ticker)

sector = info.get("sector", "N/A")

industry = info.get("industry", "N/A")

country = info.get("country", "N/A")


st.header(company_name)

st.write(
    f"**{ticker}**  •  {sector}  •  {industry}  •  {country}"
)


# ============================================================
# COMPANY DESCRIPTION
# ============================================================

description = info.get("longBusinessSummary")

if description:

    st.subheader("About")

    st.write(description)


# ============================================================
# MARKET OVERVIEW
# ============================================================

st.subheader("Market Overview")

current_price = info.get("currentPrice")

market_cap = info.get("marketCap")

high_52 = info.get("fiftyTwoWeekHigh")

low_52 = info.get("fiftyTwoWeekLow")


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Current Price",
    format_price(current_price)
)


col2.metric(
    "Market Cap",
    format_large_number(market_cap)
)


col3.metric(
    "52 Week High",
    format_price(high_52)
)


col4.metric(
    "52 Week Low",
    format_price(low_52)
)


# ============================================================
# PRICE CHART
# ============================================================

st.subheader("Price Performance")

price_chart = create_price_chart(
    history,
    ticker
)

st.plotly_chart(
    price_chart,
    use_container_width=True
)


# ============================================================
# PERFORMANCE SUMMARY
# ============================================================

st.subheader("Historical Performance")

col1, col2, col3 = st.columns(3)


col1.metric(
    "1 Month",
    format_percentage(
        performance["1_month"]
    )
)


col2.metric(
    "6 Months",
    format_percentage(
        performance["6_month"]
    )
)


col3.metric(
    "1 Year",
    format_percentage(
        performance["1_year"]
    )
)


st.divider()


# ============================================================
# ANALYSIS TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Fundamentals",
        "Valuation",
        "Financial Health",
        "Risk",
        "Technical Analysis"
    ]
)


# ============================================================
# FUNDAMENTALS TAB
# ============================================================

with tab1:

    st.subheader("Growth")

    col1, col2 = st.columns(2)

    col1.metric(
        "Revenue Growth",
        format_percentage(
            info.get("revenueGrowth")
        )
    )

    col2.metric(
        "Earnings Growth",
        format_percentage(
            info.get("earningsGrowth")
        )
    )


    st.subheader("Profitability")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Profit Margin",
        format_percentage(
            info.get("profitMargins")
        )
    )

    col2.metric(
        "Operating Margin",
        format_percentage(
            info.get("operatingMargins")
        )
    )

    col3.metric(
        "Return on Equity",
        format_percentage(
            info.get("returnOnEquity")
        )
    )

    col4.metric(
        "Return on Assets",
        format_percentage(
            info.get("returnOnAssets")
        )
    )


# ============================================================
# VALUATION TAB
# ============================================================

with tab2:

    st.subheader("Valuation Multiples")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "P/E Ratio",
        format_ratio(
            info.get("trailingPE")
        )
    )

    col2.metric(
        "Forward P/E",
        format_ratio(
            info.get("forwardPE")
        )
    )

    col3.metric(
        "Price / Book",
        format_ratio(
            info.get("priceToBook")
        )
    )

    col4.metric(
        "PEG Ratio",
        format_ratio(
            info.get("trailingPegRatio")
        )
    )

    st.info(
        "Valuation ratios should be interpreted relative "
        "to the company's growth, industry and peers."
    )


# ============================================================
# FINANCIAL HEALTH TAB
# ============================================================

with tab3:

    st.subheader("Balance Sheet & Cash Flow")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Cash",
        format_large_number(
            financial_health["cash"]
        )
    )

    col2.metric(
        "Total Debt",
        format_large_number(
            financial_health["debt"]
        )
    )

    col3.metric(
        "Net Debt",
        format_large_number(
            financial_health["net_debt"]
        )
    )


    col1, col2 = st.columns(2)

    col1.metric(
        "Current Ratio",
        format_ratio(
            financial_health["current_ratio"]
        )
    )

    col2.metric(
        "Debt / Equity",
        format_ratio(
            financial_health["debt_to_equity"]
        )
    )


    col1, col2 = st.columns(2)

    col1.metric(
        "Free Cash Flow",
        format_large_number(
            financial_health["free_cash_flow"]
        )
    )

    col2.metric(
        "Operating Cash Flow",
        format_large_number(
            financial_health["operating_cash_flow"]
        )
    )


# ============================================================
# RISK TAB
# ============================================================

with tab4:

    st.subheader("Risk Analysis")

    col1, col2 = st.columns(2)

    col1.metric(
        "Annualised Volatility",
        format_percentage(
            performance["volatility"]
        )
    )

    col2.metric(
        "Maximum Drawdown",
        format_percentage(
            performance["max_drawdown"]
        )
    )

    st.caption(
        "Volatility is annualised from historical daily returns. "
        "Maximum drawdown measures the largest peak-to-trough "
        "decline during the analysed period."
    )


# ============================================================
# TECHNICAL TAB
# ============================================================

with tab5:

    st.subheader("Trend & Momentum")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "50-Day Moving Average",
        format_price(
            technical["sma_50"]
        )
    )

    col2.metric(
        "200-Day Moving Average",
        format_price(
            technical["sma_200"]
        )
    )

    col3.metric(
        "14-Day RSI",
        f"{technical['rsi']:.2f}"
    )


    col1, col2, col3 = st.columns(3)

    col1.metric(
        "vs 50-Day MA",
        format_percentage(
            technical["distance_50"]
        )
    )

    col2.metric(
        "vs 200-Day MA",
        format_percentage(
            technical["distance_200"]
        )
    )

    col3.metric(
        "From 52W High",
        format_percentage(
            technical["distance_high"]
        )
    )


# ============================================================
# STOCK SCORE
# ============================================================

st.divider()

st.header("Stock Score")

st.caption(
    "Multi-factor model combining business fundamentals, "
    "valuation, financial health, momentum and historical risk."
)


# Overall score

overall = scores["overall"]

col1, col2 = st.columns(
    [1, 2]
)


with col1:

    st.metric(
        "Overall Score",
        f"{overall:.1f} / 10"
    )

    st.write(
        f"**Rating: {score_label(overall)}**"
    )


with col2:

    st.progress(
        int(overall * 10)
    )


# ============================================================
# INDIVIDUAL SCORES
# ============================================================

st.subheader("Factor Scores")


col1, col2, col3 = st.columns(3)


col1.metric(
    "Growth",
    f"{scores['growth']:.1f} / 10"
)


col2.metric(
    "Profitability",
    f"{scores['profitability']:.1f} / 10"
)


col3.metric(
    "Valuation",
    f"{scores['valuation']:.1f} / 10"
)


col1, col2, col3 = st.columns(3)


col1.metric(
    "Financial Health",
    f"{scores['financial_health']:.1f} / 10"
)


col2.metric(
    "Momentum",
    f"{scores['momentum']:.1f} / 10"
)


col3.metric(
    "Risk",
    f"{scores['risk']:.1f} / 10"
)


# ============================================================
# MODEL WEIGHTS
# ============================================================

with st.expander(
    "How is the score calculated?"
):

    st.write(
        """
        The overall score is a weighted multi-factor model:

        - **Growth — 20%**
        - **Profitability — 20%**
        - **Valuation — 20%**
        - **Financial Health — 20%**
        - **Momentum — 10%**
        - **Risk — 10%**

        The score is intended as a research aid rather than
        an investment recommendation.

        Valuation and financial ratios can vary substantially
        between industries, so future versions of the model
        will incorporate sector-relative analysis.
        """
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.caption(
    "For educational and research purposes only. "
    "This dashboard does not constitute financial advice."
)
