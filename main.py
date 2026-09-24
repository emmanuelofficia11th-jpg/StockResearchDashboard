import yfinance as yf
import numpy as np


# ============================================================
# STOCK RESEARCH & ANALYSIS ENGINE
# ============================================================


# ============================================================
# FORMATTING
# ============================================================

def format_large_number(number):
    """Convert large financial numbers into readable format."""

    if number is None:
        return "N/A"

    sign = "-" if number < 0 else ""
    number = abs(number)

    if number >= 1_000_000_000_000:
        return f"{sign}${number / 1_000_000_000_000:.2f}T"

    elif number >= 1_000_000_000:
        return f"{sign}${number / 1_000_000_000:.2f}B"

    elif number >= 1_000_000:
        return f"{sign}${number / 1_000_000:.2f}M"

    return f"{sign}${number:,.2f}"


def format_percentage(number):

    if number is None:
        return "N/A"

    return f"{number * 100:.2f}%"


def format_ratio(number):

    if number is None:
        return "N/A"

    return f"{number:.2f}"


def clamp_score(score):
    """Prevent scores going below 0 or above 10."""

    return max(0, min(10, score))


# ============================================================
# DATA
# ============================================================

def get_stock_data(ticker):

    stock = yf.Ticker(ticker)

    info = stock.info

    history = stock.history(period="1y")

    return stock, info, history


# ============================================================
# COMPANY PROFILE
# ============================================================

def display_company_profile(info, ticker):

    print("\n============================================================")
    print("COMPANY PROFILE")
    print("============================================================")

    print("Company:", info.get("longName", ticker))
    print("Ticker:", ticker)
    print("Sector:", info.get("sector", "N/A"))
    print("Industry:", info.get("industry", "N/A"))
    print("Country:", info.get("country", "N/A"))

    employees = info.get("fullTimeEmployees")

    if employees:
        print("Employees:", f"{employees:,}")

    print("\nABOUT")
    print("------------------------------------------------------------")

    description = info.get("longBusinessSummary")

    if description:
        print(description)
    else:
        print("Company description unavailable.")


# ============================================================
# MARKET DATA
# ============================================================

def display_market_data(info):

    print("\n============================================================")
    print("MARKET DATA")
    print("============================================================")

    price = info.get("currentPrice")
    high = info.get("fiftyTwoWeekHigh")
    low = info.get("fiftyTwoWeekLow")

    print(
        "Current Price:",
        f"${price:.2f}" if price is not None else "N/A"
    )

    print(
        "Market Cap:",
        format_large_number(info.get("marketCap"))
    )

    print(
        "52 Week High:",
        f"${high:.2f}" if high is not None else "N/A"
    )

    print(
        "52 Week Low:",
        f"${low:.2f}" if low is not None else "N/A"
    )


# ============================================================
# VALUATION
# ============================================================

def display_valuation(info):

    print("\n============================================================")
    print("VALUATION")
    print("============================================================")

    print(
        "P/E Ratio:",
        format_ratio(info.get("trailingPE"))
    )

    print(
        "Forward P/E:",
        format_ratio(info.get("forwardPE"))
    )

    print(
        "Price / Book:",
        format_ratio(info.get("priceToBook"))
    )

    print(
        "PEG Ratio:",
        format_ratio(info.get("trailingPegRatio"))
    )


# ============================================================
# GROWTH & PROFITABILITY
# ============================================================

def display_fundamentals(info):

    print("\n============================================================")
    print("GROWTH & PROFITABILITY")
    print("============================================================")

    print(
        "Revenue Growth:",
        format_percentage(info.get("revenueGrowth"))
    )

    print(
        "Earnings Growth:",
        format_percentage(info.get("earningsGrowth"))
    )

    print(
        "Profit Margin:",
        format_percentage(info.get("profitMargins"))
    )

    print(
        "Operating Margin:",
        format_percentage(info.get("operatingMargins"))
    )

    print(
        "Return on Equity:",
        format_percentage(info.get("returnOnEquity"))
    )

    print(
        "Return on Assets:",
        format_percentage(info.get("returnOnAssets"))
    )


# ============================================================
# FINANCIAL HEALTH
# ============================================================

def calculate_financial_health(info):

    cash = info.get("totalCash")
    debt = info.get("totalDebt")

    if cash is not None and debt is not None:
        net_debt = debt - cash
    else:
        net_debt = None

    return {
        "cash": cash,
        "debt": debt,
        "net_debt": net_debt,
        "current_ratio": info.get("currentRatio"),
        "debt_to_equity": info.get("debtToEquity"),
        "free_cash_flow": info.get("freeCashflow"),
        "operating_cash_flow": info.get("operatingCashflow")
    }


def display_financial_health(health):

    print("\n============================================================")
    print("FINANCIAL HEALTH")
    print("============================================================")

    print(
        "Cash:",
        format_large_number(health["cash"])
    )

    print(
        "Total Debt:",
        format_large_number(health["debt"])
    )

    print(
        "Net Debt:",
        format_large_number(health["net_debt"])
    )

    print(
        "Current Ratio:",
        format_ratio(health["current_ratio"])
    )

    print(
        "Debt / Equity:",
        format_ratio(health["debt_to_equity"])
    )

    print(
        "Free Cash Flow:",
        format_large_number(health["free_cash_flow"])
    )

    print(
        "Operating Cash Flow:",
        format_large_number(health["operating_cash_flow"])
    )


# ============================================================
# HISTORICAL PERFORMANCE
# ============================================================

def calculate_return(prices, trading_days):

    if len(prices) <= trading_days:
        return None

    old_price = prices.iloc[-trading_days - 1]
    current_price = prices.iloc[-1]

    return (current_price / old_price) - 1


def calculate_performance(history):

    prices = history["Close"]

    one_month = calculate_return(prices, 21)
    six_month = calculate_return(prices, 126)

    if len(prices) > 1:
        one_year = (prices.iloc[-1] / prices.iloc[0]) - 1
    else:
        one_year = None

    daily_returns = prices.pct_change().dropna()

    volatility = daily_returns.std() * np.sqrt(252)

    running_max = prices.cummax()

    drawdown = (prices / running_max) - 1

    max_drawdown = drawdown.min()

    return {
        "1_month": one_month,
        "6_month": six_month,
        "1_year": one_year,
        "volatility": volatility,
        "max_drawdown": max_drawdown
    }


def display_performance(performance):

    print("\n============================================================")
    print("PERFORMANCE & RISK")
    print("============================================================")

    print(
        "1 Month Return:",
        format_percentage(performance["1_month"])
    )

    print(
        "6 Month Return:",
        format_percentage(performance["6_month"])
    )

    print(
        "1 Year Return:",
        format_percentage(performance["1_year"])
    )

    print(
        "Annualised Volatility:",
        format_percentage(performance["volatility"])
    )

    print(
        "Maximum Drawdown:",
        format_percentage(performance["max_drawdown"])
    )


# ============================================================
# TECHNICAL ANALYSIS
# ============================================================

def calculate_technical_metrics(history):

    prices = history["Close"]

    current_price = prices.iloc[-1]

    sma_50 = prices.rolling(window=50).mean().iloc[-1]
    sma_200 = prices.rolling(window=200).mean().iloc[-1]

    distance_50 = (current_price / sma_50) - 1
    distance_200 = (current_price / sma_200) - 1

    # RSI
    changes = prices.diff()

    gains = changes.clip(lower=0)
    losses = -changes.clip(upper=0)

    average_gain = gains.rolling(window=14).mean()
    average_loss = losses.rolling(window=14).mean()

    rs = average_gain / average_loss

    rsi = 100 - (100 / (1 + rs))

    current_rsi = rsi.iloc[-1]

    high_52 = prices.max()

    distance_high = (current_price / high_52) - 1

    return {
        "sma_50": sma_50,
        "sma_200": sma_200,
        "distance_50": distance_50,
        "distance_200": distance_200,
        "rsi": current_rsi,
        "distance_high": distance_high
    }


def display_technicals(technical):

    print("\n============================================================")
    print("TECHNICAL & MOMENTUM ANALYSIS")
    print("============================================================")

    print(
        f"50-Day Moving Average: ${technical['sma_50']:.2f}"
    )

    print(
        f"200-Day Moving Average: ${technical['sma_200']:.2f}"
    )

    print(
        "Distance From 50-Day MA:",
        format_percentage(technical["distance_50"])
    )

    print(
        "Distance From 200-Day MA:",
        format_percentage(technical["distance_200"])
    )

    print(
        f"14-Day RSI: {technical['rsi']:.2f}"
    )

    print(
        "Distance From 52-Week High:",
        format_percentage(technical["distance_high"])
    )


# ============================================================
# SCORING — GROWTH
# ============================================================

def calculate_growth_score(info):

    values = [
        info.get("revenueGrowth"),
        info.get("earningsGrowth")
    ]

    scores = []

    for value in values:

        if value is None:
            continue

        if value >= 0.25:
            scores.append(10)

        elif value >= 0.15:
            scores.append(8)

        elif value >= 0.08:
            scores.append(6)

        elif value >= 0:
            scores.append(4)

        else:
            scores.append(1)

    return sum(scores) / len(scores) if scores else 5


# ============================================================
# SCORING — PROFITABILITY
# ============================================================

def calculate_profitability_score(info):

    profit_margin = info.get("profitMargins")
    roe = info.get("returnOnEquity")

    scores = []

    if profit_margin is not None:

        if profit_margin >= 0.25:
            scores.append(10)
        elif profit_margin >= 0.15:
            scores.append(8)
        elif profit_margin >= 0.08:
            scores.append(6)
        elif profit_margin > 0:
            scores.append(4)
        else:
            scores.append(1)

    if roe is not None:

        if roe >= 0.25:
            scores.append(10)
        elif roe >= 0.15:
            scores.append(8)
        elif roe >= 0.08:
            scores.append(6)
        elif roe > 0:
            scores.append(4)
        else:
            scores.append(1)

    return sum(scores) / len(scores) if scores else 5


# ============================================================
# SCORING — VALUATION
# ============================================================

def calculate_valuation_score(info):

    forward_pe = info.get("forwardPE")
    peg = info.get("trailingPegRatio")

    scores = []

    if forward_pe is not None and forward_pe > 0:

        if forward_pe <= 15:
            scores.append(10)
        elif forward_pe <= 20:
            scores.append(8)
        elif forward_pe <= 30:
            scores.append(6)
        elif forward_pe <= 40:
            scores.append(4)
        else:
            scores.append(2)

    if peg is not None and peg > 0:

        if peg <= 1:
            scores.append(10)
        elif peg <= 1.5:
            scores.append(8)
        elif peg <= 2:
            scores.append(6)
        elif peg <= 3:
            scores.append(4)
        else:
            scores.append(2)

    return sum(scores) / len(scores) if scores else 5


# ============================================================
# SCORING — FINANCIAL HEALTH
# ============================================================

def calculate_financial_health_score(health):

    score = 5

    cash = health["cash"]
    debt = health["debt"]
    current_ratio = health["current_ratio"]
    free_cash_flow = health["free_cash_flow"]
    operating_cash_flow = health["operating_cash_flow"]

    # Cash compared with debt
    if cash is not None and debt is not None:

        if cash > debt:
            score += 2

        elif debt > cash * 3:
            score -= 2

        elif debt > cash:
            score -= 1

    # Short-term liquidity
    if current_ratio is not None:

        if current_ratio >= 2:
            score += 1.5

        elif current_ratio >= 1:
            score += 0.5

        elif current_ratio < 1:
            score -= 1.5

    # Free cash flow
    if free_cash_flow is not None:

        if free_cash_flow > 0:
            score += 1

        else:
            score -= 1

    # Operating cash generation
    if operating_cash_flow is not None:

        if operating_cash_flow > 0:
            score += 0.5

        else:
            score -= 0.5

    return clamp_score(score)


# ============================================================
# SCORING — MOMENTUM
# ============================================================

def calculate_momentum_score(technical):

    score = 5

    if technical["distance_50"] > 0:
        score += 1
    else:
        score -= 1

    if technical["distance_200"] > 0:
        score += 2
    else:
        score -= 2

    rsi = technical["rsi"]

    if 50 <= rsi <= 70:
        score += 2

    elif 40 <= rsi < 50:
        score += 1

    elif rsi > 80:
        score -= 1

    elif rsi < 30:
        score -= 2

    return clamp_score(score)


# ============================================================
# SCORING — RISK
# ============================================================

def calculate_risk_score(performance):

    volatility = performance["volatility"]

    drawdown = abs(performance["max_drawdown"])

    scores = []

    if volatility < 0.20:
        scores.append(10)
    elif volatility < 0.30:
        scores.append(8)
    elif volatility < 0.40:
        scores.append(6)
    elif volatility < 0.50:
        scores.append(4)
    else:
        scores.append(2)

    if drawdown < 0.10:
        scores.append(10)
    elif drawdown < 0.20:
        scores.append(8)
    elif drawdown < 0.30:
        scores.append(6)
    elif drawdown < 0.40:
        scores.append(4)
    else:
        scores.append(2)

    return sum(scores) / len(scores)


# ============================================================
# OVERALL STOCK SCORE
# ============================================================

def calculate_stock_score(info, health, performance, technical):

    growth = calculate_growth_score(info)

    profitability = calculate_profitability_score(info)

    valuation = calculate_valuation_score(info)

    financial_health = calculate_financial_health_score(health)

    momentum = calculate_momentum_score(technical)

    risk = calculate_risk_score(performance)

    overall = (
        growth * 0.20
        + profitability * 0.20
        + valuation * 0.20
        + financial_health * 0.20
        + momentum * 0.10
        + risk * 0.10
    )

    return {
        "growth": growth,
        "profitability": profitability,
        "valuation": valuation,
        "financial_health": financial_health,
        "momentum": momentum,
        "risk": risk,
        "overall": overall
    }


def display_scores(scores):

    print("\n============================================================")
    print("STOCK SCORE")
    print("============================================================")

    print(
        f"Growth:             {scores['growth']:.1f} / 10"
    )

    print(
        f"Profitability:      {scores['profitability']:.1f} / 10"
    )

    print(
        f"Valuation:          {scores['valuation']:.1f} / 10"
    )

    print(
        f"Financial Health:   {scores['financial_health']:.1f} / 10"
    )

    print(
        f"Momentum:           {scores['momentum']:.1f} / 10"
    )

    print(
        f"Risk:               {scores['risk']:.1f} / 10"
    )

    print("------------------------------------------------------------")

    print(
        f"OVERALL SCORE:      {scores['overall']:.1f} / 10"
    )

    print("============================================================")

    print("\nModel weights:")

    print("Growth             20%")
    print("Profitability      20%")
    print("Valuation          20%")
    print("Financial Health   20%")
    print("Momentum           10%")
    print("Risk               10%")


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n============================================================")
    print("              STOCK RESEARCH DASHBOARD")
    print("============================================================")

    ticker = input(
        "\nEnter a stock ticker: "
    ).upper().strip()

    print(
        f"\nRetrieving and analysing {ticker}..."
    )

    try:

        stock, info, history = get_stock_data(ticker)

        if history.empty:
            print("\nNo historical price data found.")
            return

        health = calculate_financial_health(info)

        performance = calculate_performance(history)

        technical = calculate_technical_metrics(history)

        scores = calculate_stock_score(
            info,
            health,
            performance,
            technical
        )

        display_company_profile(info, ticker)

        display_market_data(info)

        display_valuation(info)

        display_fundamentals(info)

        display_financial_health(health)

        display_performance(performance)

        display_technicals(technical)

        display_scores(scores)

    except Exception as error:

        print("\nSomething went wrong.")

        print("Error:", error)


if __name__ == "__main__":
    main()
