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
# FORMATTING
# ============================================================

def format_price(value):
    if value is None:
        return "N/A"

    return f"${value:,.2f}"


def score_label(score):
    if score >= 8:
        return "High Model Score"
    elif score >= 6:
        return "Above-Average Model Score"
    elif score >= 4:
        return "Moderate Model Score"
    else:
        return "Low Model Score"


# ============================================================
# DATA ANALYSIS
# ============================================================

def analyse_stock(ticker):
    stock, info, history = get_stock_data(ticker)

    if history.empty:
        raise ValueError(
            f"No historical data was found for {ticker}."
        )

    financial_health = calculate_financial_health(info)
    performance = calculate_performance(history)
    technical = calculate_technical_metrics(history)

    scores = calculate_stock_score(
        info,
        financial_health,
        performance,
        technical
    )

    return {
        "stock": stock,
        "info": info,
        "history": history,
        "financial_health": financial_health,
        "performance": performance,
        "technical": technical,
        "scores": scores
    }


# ============================================================
# CHARTS
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


def create_comparison_chart(
    history_a,
    history_b,
    ticker_a,
    ticker_b
):
    prices_a = history_a["Close"].dropna()
    prices_b = history_b["Close"].dropna()

    common_dates = prices_a.index.intersection(
        prices_b.index
    )

    prices_a = prices_a.loc[common_dates]
    prices_b = prices_b.loc[common_dates]

    if prices_a.empty or prices_b.empty:
        return None

    # Both stocks begin at 100.
    # This lets us compare percentage performance rather
    # than comparing their different share prices.
    normalised_a = (prices_a / prices_a.iloc[0]) * 100
    normalised_b = (prices_b / prices_b.iloc[0]) * 100

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=common_dates,
            y=normalised_a,
            mode="lines",
            name=ticker_a
        )
    )

    figure.add_trace(
        go.Scatter(
            x=common_dates,
            y=normalised_b,
            mode="lines",
            name=ticker_b
        )
    )

    figure.update_layout(
        title="Relative 1-Year Performance",
        xaxis_title="Date",
        yaxis_title="Growth of 100",
        height=520,
        hovermode="x unified",
        legend_title="Stock"
    )

    return figure


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 Stock Research")

mode = st.sidebar.radio(
    "Choose research mode",
    [
        "🔎 Analyse Stock",
        "⚖️ Compare Stocks"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Research dashboard built using Python, "
    "Streamlit and financial market data."
)


# ============================================================
# HEADER
# ============================================================

st.title("📈 Stock Research Dashboard")

st.write(
    "Fundamental, valuation, financial health, "
    "risk and momentum analysis in one place."
)

st.divider()


# ============================================================
# SINGLE STOCK MODE
# ============================================================

if mode == "🔎 Analyse Stock":

    st.sidebar.subheader("Stock Analysis")

    ticker = st.sidebar.text_input(
        "Stock ticker",
        value="NVDA",
        placeholder="e.g. AAPL"
    ).upper().strip()

    analyse = st.sidebar.button(
        "Analyse Stock",
        type="primary",
        width="stretch"
    )

    if not analyse:
        st.info(
            "Enter a ticker in the sidebar and "
            "click **Analyse Stock**."
        )

        st.write("Try:")
        st.code("NVDA   AAPL   MSFT   GOOGL   AMZN")
        st.stop()

    try:
        with st.spinner(
            f"Retrieving and analysing {ticker}..."
        ):
            data = analyse_stock(ticker)

    except Exception as error:
        st.error(
            "The stock could not be analysed. "
            "Check the ticker and try again."
        )

        with st.expander("Technical details"):
            st.write(error)

        st.stop()

    info = data["info"]
    history = data["history"]
    financial_health = data["financial_health"]
    performance = data["performance"]
    technical = data["technical"]
    scores = data["scores"]

    company_name = info.get("longName", ticker)
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    country = info.get("country", "N/A")

    st.header(company_name)

    st.write(
        f"**{ticker}**  •  {sector}  •  "
        f"{industry}  •  {country}"
    )

    description = info.get("longBusinessSummary")

    if description:
        st.subheader("About")
        st.write(description)

    # --------------------------------------------------------
    # MARKET OVERVIEW
    # --------------------------------------------------------

    st.subheader("Market Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Price",
        format_price(info.get("currentPrice"))
    )

    col2.metric(
        "Market Cap",
        format_large_number(
            info.get("marketCap")
        )
    )

    col3.metric(
        "52 Week High",
        format_price(
            info.get("fiftyTwoWeekHigh")
        )
    )

    col4.metric(
        "52 Week Low",
        format_price(
            info.get("fiftyTwoWeekLow")
        )
    )

    # --------------------------------------------------------
    # PRICE CHART
    # --------------------------------------------------------

    st.subheader("Price Performance")

    st.plotly_chart(
        create_price_chart(
            history,
            ticker
        ),
        width="stretch"
    )

    # --------------------------------------------------------
    # HISTORICAL PERFORMANCE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ANALYSIS TABS
    # --------------------------------------------------------

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Fundamentals",
            "Valuation",
            "Financial Health",
            "Risk",
            "Technical Analysis"
        ]
    )

    # FUNDAMENTALS

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

    # VALUATION

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
            "Valuation ratios should be interpreted "
            "relative to the company's growth, "
            "industry and peers."
        )

    # FINANCIAL HEALTH

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
                financial_health[
                    "operating_cash_flow"
                ]
            )
        )

    # RISK

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
            "Volatility is annualised from historical "
            "daily returns. Maximum drawdown measures "
            "the largest peak-to-trough decline during "
            "the analysed period."
        )

    # TECHNICAL

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

    # --------------------------------------------------------
    # STOCK SCORE
    # --------------------------------------------------------

    st.divider()

    st.header("Stock Score")

    st.caption(
        "Multi-factor model combining business "
        "fundamentals, valuation, financial health, "
        "momentum and historical risk."
    )

    overall = scores["overall"]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(
            "Overall Score",
            f"{overall:.1f} / 10"
        )

        st.write(
            f"**{score_label(overall)}**"
        )

    with col2:
        st.progress(
            int(overall * 10)
        )

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

    with st.expander(
        "How is the score calculated?"
    ):

        st.write(
            """
            The overall score is a weighted
            multi-factor model:

            - **Growth — 20%**
            - **Profitability — 20%**
            - **Valuation — 20%**
            - **Financial Health — 20%**
            - **Momentum — 10%**
            - **Risk — 10%**

            The score is intended as a research aid
            rather than an investment recommendation.

            Valuation and financial ratios can vary
            substantially between industries, so
            future versions of the model will
            incorporate sector-relative analysis.
            """
        )


# ============================================================
# STOCK COMPARISON MODE
# ============================================================

else:

    st.sidebar.subheader("Stock Comparison")

    ticker_a = st.sidebar.text_input(
        "Stock A",
        value="NVDA",
        key="ticker_a"
    ).upper().strip()

    ticker_b = st.sidebar.text_input(
        "Stock B",
        value="AMD",
        key="ticker_b"
    ).upper().strip()

    compare = st.sidebar.button(
        "Compare Stocks",
        type="primary",
        width="stretch"
    )

    st.header("⚖️ Compare Stocks")

    st.write(
        "Compare two companies across fundamentals, "
        "valuation, financial health, market "
        "performance and risk."
    )

    if not compare:
        st.info(
            "Choose two stock tickers in the sidebar "
            "and click **Compare Stocks**."
        )

        st.code("Examples: NVDA vs AMD   |   AAPL vs MSFT")

        st.stop()

    if ticker_a == ticker_b:
        st.warning(
            "Choose two different stocks to compare."
        )
        st.stop()

    try:

        with st.spinner(
            f"Comparing {ticker_a} and {ticker_b}..."
        ):

            data_a = analyse_stock(ticker_a)
            data_b = analyse_stock(ticker_b)

    except Exception as error:

        st.error(
            "One or both stocks could not be analysed. "
            "Check the tickers and try again."
        )

        with st.expander("Technical details"):
            st.write(error)

        st.stop()

    info_a = data_a["info"]
    info_b = data_b["info"]

    health_a = data_a["financial_health"]
    health_b = data_b["financial_health"]

    performance_a = data_a["performance"]
    performance_b = data_b["performance"]

    technical_a = data_a["technical"]
    technical_b = data_b["technical"]

    scores_a = data_a["scores"]
    scores_b = data_b["scores"]

    name_a = info_a.get(
        "longName",
        ticker_a
    )

    name_b = info_b.get(
        "longName",
        ticker_b
    )

    # --------------------------------------------------------
    # COMPANY HEADERS
    # --------------------------------------------------------

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(name_a)

        st.write(
            f"**{ticker_a}** • "
            f"{info_a.get('sector', 'N/A')}"
        )

        st.metric(
            "Current Price",
            format_price(
                info_a.get("currentPrice")
            )
        )

        st.metric(
            "Market Cap",
            format_large_number(
                info_a.get("marketCap")
            )
        )

    with col2:

        st.subheader(name_b)

        st.write(
            f"**{ticker_b}** • "
            f"{info_b.get('sector', 'N/A')}"
        )

        st.metric(
            "Current Price",
            format_price(
                info_b.get("currentPrice")
            )
        )

        st.metric(
            "Market Cap",
            format_large_number(
                info_b.get("marketCap")
            )
        )

    # --------------------------------------------------------
    # MODEL SCORES
    # --------------------------------------------------------

    st.divider()

    st.subheader("Model Scores")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            ticker_a,
            f"{scores_a['overall']:.1f} / 10"
        )

        st.caption(
            score_label(
                scores_a["overall"]
            )
        )

    with col2:

        st.metric(
            ticker_b,
            f"{scores_b['overall']:.1f} / 10"
        )

        st.caption(
            score_label(
                scores_b["overall"]
            )
        )

    st.write("#### Factor Breakdown")

    score_names = [
        ("Growth", "growth"),
        ("Profitability", "profitability"),
        ("Valuation", "valuation"),
        ("Financial Health", "financial_health"),
        ("Momentum", "momentum"),
        ("Risk", "risk")
    ]

    for label, key in score_names:

        col1, col2, col3 = st.columns(
            [2, 1, 1]
        )

        col1.write(f"**{label}**")

        col2.write(
            f"{ticker_a}: "
            f"**{scores_a[key]:.1f}/10**"
        )

        col3.write(
            f"{ticker_b}: "
            f"**{scores_b[key]:.1f}/10**"
        )

    # --------------------------------------------------------
    # RELATIVE PERFORMANCE
    # --------------------------------------------------------

    st.divider()

    st.subheader("Relative Performance")

    st.caption(
        "Both stocks start at 100 so their percentage "
        "performance can be compared directly."
    )

    comparison_chart = create_comparison_chart(
        data_a["history"],
        data_b["history"],
        ticker_a,
        ticker_b
    )

    if comparison_chart is not None:

        st.plotly_chart(
            comparison_chart,
            width="stretch"
        )

    else:

        st.warning(
            "There was not enough overlapping price "
            "history to create the comparison chart."
        )

    # --------------------------------------------------------
    # HISTORICAL RETURNS
    # --------------------------------------------------------

    st.subheader("Historical Returns")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("**1 Month**")

        st.write(
            f"{ticker_a}: "
            f"{format_percentage(performance_a['1_month'])}"
        )

        st.write(
            f"{ticker_b}: "
            f"{format_percentage(performance_b['1_month'])}"
        )

    with col2:

        st.write("**6 Months**")

        st.write(
            f"{ticker_a}: "
            f"{format_percentage(performance_a['6_month'])}"
        )

        st.write(
            f"{ticker_b}: "
            f"{format_percentage(performance_b['6_month'])}"
        )

    with col3:

        st.write("**1 Year**")

        st.write(
            f"{ticker_a}: "
            f"{format_percentage(performance_a['1_year'])}"
        )

        st.write(
            f"{ticker_b}: "
            f"{format_percentage(performance_b['1_year'])}"
        )

    # --------------------------------------------------------
    # COMPARISON TABS
    # --------------------------------------------------------

    st.divider()

    compare_tab1, compare_tab2, compare_tab3, \
        compare_tab4, compare_tab5 = st.tabs(
            [
                "Fundamentals",
                "Valuation",
                "Financial Health",
                "Risk",
                "Technical"
            ]
        )

    # FUNDAMENTALS

    with compare_tab1:

        st.subheader("Growth & Profitability")

        metrics = [
            (
                "Revenue Growth",
                format_percentage(
                    info_a.get("revenueGrowth")
                ),
                format_percentage(
                    info_b.get("revenueGrowth")
                )
            ),
            (
                "Earnings Growth",
                format_percentage(
                    info_a.get("earningsGrowth")
                ),
                format_percentage(
                    info_b.get("earningsGrowth")
                )
            ),
            (
                "Profit Margin",
                format_percentage(
                    info_a.get("profitMargins")
                ),
                format_percentage(
                    info_b.get("profitMargins")
                )
            ),
            (
                "Operating Margin",
                format_percentage(
                    info_a.get("operatingMargins")
                ),
                format_percentage(
                    info_b.get("operatingMargins")
                )
            ),
            (
                "Return on Equity",
                format_percentage(
                    info_a.get("returnOnEquity")
                ),
                format_percentage(
                    info_b.get("returnOnEquity")
                )
            ),
            (
                "Return on Assets",
                format_percentage(
                    info_a.get("returnOnAssets")
                ),
                format_percentage(
                    info_b.get("returnOnAssets")
                )
            )
        ]

        for label, value_a, value_b in metrics:

            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )

            col1.write(f"**{label}**")
            col2.write(f"{ticker_a}: {value_a}")
            col3.write(f"{ticker_b}: {value_b}")

    # VALUATION

    with compare_tab2:

        st.subheader("Valuation Multiples")

        metrics = [
            (
                "P/E Ratio",
                format_ratio(
                    info_a.get("trailingPE")
                ),
                format_ratio(
                    info_b.get("trailingPE")
                )
            ),
            (
                "Forward P/E",
                format_ratio(
                    info_a.get("forwardPE")
                ),
                format_ratio(
                    info_b.get("forwardPE")
                )
            ),
            (
                "Price / Book",
                format_ratio(
                    info_a.get("priceToBook")
                ),
                format_ratio(
                    info_b.get("priceToBook")
                )
            ),
            (
                "PEG Ratio",
                format_ratio(
                    info_a.get("trailingPegRatio")
                ),
                format_ratio(
                    info_b.get("trailingPegRatio")
                )
            )
        ]

        for label, value_a, value_b in metrics:

            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )

            col1.write(f"**{label}**")
            col2.write(f"{ticker_a}: {value_a}")
            col3.write(f"{ticker_b}: {value_b}")

        st.info(
            "Direct valuation comparisons are most "
            "useful when companies have similar "
            "business models, growth profiles and sectors."
        )

    # FINANCIAL HEALTH

    with compare_tab3:

        st.subheader("Balance Sheet & Cash Flow")

        metrics = [
            (
                "Cash",
                format_large_number(
                    health_a["cash"]
                ),
                format_large_number(
                    health_b["cash"]
                )
            ),
            (
                "Total Debt",
                format_large_number(
                    health_a["debt"]
                ),
                format_large_number(
                    health_b["debt"]
                )
            ),
            (
                "Net Debt",
                format_large_number(
                    health_a["net_debt"]
                ),
                format_large_number(
                    health_b["net_debt"]
                )
            ),
            (
                "Current Ratio",
                format_ratio(
                    health_a["current_ratio"]
                ),
                format_ratio(
                    health_b["current_ratio"]
                )
            ),
            (
                "Debt / Equity",
                format_ratio(
                    health_a["debt_to_equity"]
                ),
                format_ratio(
                    health_b["debt_to_equity"]
                )
            ),
            (
                "Free Cash Flow",
                format_large_number(
                    health_a["free_cash_flow"]
                ),
                format_large_number(
                    health_b["free_cash_flow"]
                )
            ),
            (
                "Operating Cash Flow",
                format_large_number(
                    health_a[
                        "operating_cash_flow"
                    ]
                ),
                format_large_number(
                    health_b[
                        "operating_cash_flow"
                    ]
                )
            )
        ]

        for label, value_a, value_b in metrics:

            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )

            col1.write(f"**{label}**")
            col2.write(f"{ticker_a}: {value_a}")
            col3.write(f"{ticker_b}: {value_b}")

    # RISK

    with compare_tab4:

        st.subheader("Historical Risk")

        metrics = [
            (
                "Annualised Volatility",
                format_percentage(
                    performance_a["volatility"]
                ),
                format_percentage(
                    performance_b["volatility"]
                )
            ),
            (
                "Maximum Drawdown",
                format_percentage(
                    performance_a["max_drawdown"]
                ),
                format_percentage(
                    performance_b["max_drawdown"]
                )
            )
        ]

        for label, value_a, value_b in metrics:

            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )

            col1.write(f"**{label}**")
            col2.write(f"{ticker_a}: {value_a}")
            col3.write(f"{ticker_b}: {value_b}")

    # TECHNICAL

    with compare_tab5:

        st.subheader("Trend & Momentum")

        metrics = [
            (
                "50-Day Moving Average",
                format_price(
                    technical_a["sma_50"]
                ),
                format_price(
                    technical_b["sma_50"]
                )
            ),
            (
                "200-Day Moving Average",
                format_price(
                    technical_a["sma_200"]
                ),
                format_price(
                    technical_b["sma_200"]
                )
            ),
            (
                "14-Day RSI",
                f"{technical_a['rsi']:.2f}",
                f"{technical_b['rsi']:.2f}"
            ),
            (
                "vs 50-Day MA",
                format_percentage(
                    technical_a["distance_50"]
                ),
                format_percentage(
                    technical_b["distance_50"]
                )
            ),
            (
                "vs 200-Day MA",
                format_percentage(
                    technical_a["distance_200"]
                ),
                format_percentage(
                    technical_b["distance_200"]
                )
            ),
            (
                "From 52W High",
                format_percentage(
                    technical_a["distance_high"]
                ),
                format_percentage(
                    technical_b["distance_high"]
                )
            )
        ]

        for label, value_a, value_b in metrics:

            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )

            col1.write(f"**{label}**")
            col2.write(f"{ticker_a}: {value_a}")
            col3.write(f"{ticker_b}: {value_b}")


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.caption(
    "For educational and research purposes only. "
    "This dashboard does not constitute financial advice."
)
