"""
advanced_banking_dashboard.py
==============================
Advanced Banking Transaction Analysis Dashboard (single file).

Features:
  - Daily transaction trend
  - Transaction type pie chart
  - Branch-wise analysis
  - Transaction mode analysis
  - Failed transaction report
  - Customer search
  - Account summaries
  - Scatter plot
  - Histogram
  - Professional report section
  - Enhanced dashboard styling

Run with:
    pip install -r requirements.txt
    streamlit run advanced_banking_dashboard.py
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Advanced Banking Dashboard", layout="wide", page_icon="🏦")

np.random.seed(7)

# ---------------------------------------------------------------------------
# ENHANCED STYLING
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .main { background-color: #f5f7fa; }
    .stApp { font-family: 'Segoe UI', sans-serif; }

    .dashboard-header {
        background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
        padding: 28px 32px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }
    .dashboard-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 32px;
    }
    .dashboard-header p {
        color: #cfd8dc;
        margin: 4px 0 0 0;
        font-size: 15px;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e3e8ee;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] { color: #203a43; }

    .section-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #e3e8ee;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 18px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #203a43;
        margin-bottom: 4px;
    }
    .section-sub {
        font-size: 13px;
        color: #708090;
        margin-bottom: 14px;
    }
    .status-badge-success {
        background:#e6f7ee; color:#1c9d5c; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600;
    }
    .status-badge-failed {
        background:#fdeaea; color:#d64545; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        border: 1px solid #e3e8ee;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #203a43 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# REFERENCE DATA
# ---------------------------------------------------------------------------

BRANCHES = ["Chennai Main", "Mumbai Fort", "Delhi CP", "Bangalore MG Road",
            "Hyderabad Banjara", "Kolkata Park St", "Pune Camp", "Ahmedabad SG Highway"]

TXN_TYPES = ["Deposit", "Withdrawal", "Fund Transfer", "Bill Payment", "POS Purchase", "Loan EMI"]

TXN_MODES = ["UPI", "NEFT", "RTGS", "IMPS", "Debit Card", "Credit Card", "Cash", "Cheque", "Net Banking"]

FAILURE_REASONS = ["Insufficient Funds", "Network Timeout", "Invalid Account Details",
                    "Bank Server Down", "Card Declined", "Daily Limit Exceeded", "OTP Failure"]

FIRST_NAMES = ["Arjun", "Priya", "Rahul", "Ananya", "Vikram", "Sneha", "Karthik", "Divya",
               "Rohan", "Meera", "Aditya", "Kavya", "Suresh", "Pooja", "Manoj", "Neha",
               "James", "Mary", "John", "Patricia", "Michael", "Linda", "Robert", "Elizabeth"]
LAST_NAMES = ["Sharma", "Iyer", "Reddy", "Nair", "Gupta", "Patel", "Menon", "Rao",
              "Singh", "Kumar", "Verma", "Pillai", "Smith", "Johnson", "Williams", "Brown"]

NUM_CUSTOMERS = 70
NUM_ACCOUNTS = 90
DAYS_OF_HISTORY = 120


# ---------------------------------------------------------------------------
# SYNTHETIC DATA GENERATION
# ---------------------------------------------------------------------------

@st.cache_data
def generate_data():
    # Customers
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        customers.append({
            "customer_id": f"CUST{i:04d}",
            "customer_name": f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}",
            "home_branch": np.random.choice(BRANCHES),
        })
    customers_df = pd.DataFrame(customers)

    # Accounts
    accounts = []
    account_types = ["Savings", "Current", "Salary", "Credit Card"]
    for i in range(1, NUM_ACCOUNTS + 1):
        cust = customers_df.sample(1).iloc[0]
        accounts.append({
            "account_id": f"ACC{i:05d}",
            "customer_id": cust["customer_id"],
            "customer_name": cust["customer_name"],
            "account_type": np.random.choice(account_types, p=[0.45, 0.25, 0.2, 0.1]),
            "branch": cust["home_branch"],
            "opening_balance": round(np.random.uniform(1000, 50000), 2),
        })
    accounts_df = pd.DataFrame(accounts)

    # Transactions
    rows = []
    txn_no = 1
    start_date = datetime.now() - timedelta(days=DAYS_OF_HISTORY)

    for _, acc in accounts_df.iterrows():
        balance = acc["opening_balance"]
        avg_amt = np.random.uniform(200, 3000)
        daily_prob = np.random.uniform(0.25, 0.6)

        for d in range(DAYS_OF_HISTORY):
            day = start_date + timedelta(days=d)
            if np.random.rand() > daily_prob:
                continue
            n_today = np.random.choice([1, 1, 2, 3], p=[0.55, 0.25, 0.13, 0.07])
            for _ in range(n_today):
                txn_type = np.random.choice(TXN_TYPES)
                mode = np.random.choice(TXN_MODES)
                amount = max(round(np.random.gamma(2.2, avg_amt / 2), 2), 20)
                is_credit = txn_type == "Deposit" or (txn_type == "Fund Transfer" and np.random.rand() < 0.3)

                status = "Success" if np.random.rand() > 0.06 else "Failed"
                failure_reason = np.random.choice(FAILURE_REASONS) if status == "Failed" else ""

                if status == "Success":
                    balance += amount if is_credit else -amount

                rows.append({
                    "transaction_id": f"TXN{txn_no:07d}",
                    "date": day.replace(hour=int(np.clip(np.random.normal(13, 5), 0, 23)),
                                         minute=int(np.random.randint(0, 60))),
                    "account_id": acc["account_id"],
                    "customer_id": acc["customer_id"],
                    "customer_name": acc["customer_name"],
                    "branch": acc["branch"],
                    "account_type": acc["account_type"],
                    "amount": amount,
                    "direction": "Credit" if is_credit else "Debit",
                    "txn_type": txn_type,
                    "txn_mode": mode,
                    "status": status,
                    "failure_reason": failure_reason,
                    "balance_after": round(balance, 2),
                })
                txn_no += 1

    txns_df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return customers_df, accounts_df, txns_df


def money(x):
    return f"₹{x:,.2f}"


# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------

customers_df, accounts_df, txns_df = generate_data()

st.markdown("""
<div class="dashboard-header">
    <h1>🏦 Advanced Banking Transaction Dashboard</h1>
    <p>Real-time transaction monitoring, branch performance, and customer insights</p>
</div>
""", unsafe_allow_html=True)

# ---- Sidebar filters ----
st.sidebar.header("🔎 Filters")
min_date, max_date = txns_df["date"].min().date(), txns_df["date"].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date),
                                    min_value=min_date, max_value=max_date)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

branch_filter = st.sidebar.multiselect("Branch", options=sorted(txns_df["branch"].unique()),
                                        default=sorted(txns_df["branch"].unique()))
mode_filter = st.sidebar.multiselect("Transaction Mode", options=sorted(txns_df["txn_mode"].unique()),
                                      default=sorted(txns_df["txn_mode"].unique()))
status_filter = st.sidebar.multiselect("Status", options=sorted(txns_df["status"].unique()),
                                        default=sorted(txns_df["status"].unique()))

mask = (
    (txns_df["date"].dt.date >= start_date) & (txns_df["date"].dt.date <= end_date) &
    (txns_df["branch"].isin(branch_filter)) &
    (txns_df["txn_mode"].isin(mode_filter)) &
    (txns_df["status"].isin(status_filter))
)
df = txns_df[mask].copy()
st.sidebar.markdown("---")
st.sidebar.caption(f"{len(df):,} transactions match current filters")

# ---- Top KPI row ----
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Transactions", f"{len(df):,}")
k2.metric("Total Amount", money(df["amount"].sum()))
k3.metric("Success Rate", f"{100 * (df['status'] == 'Success').mean():.1f}%")
k4.metric("Failed Transactions", f"{(df['status'] == 'Failed').sum():,}")
k5.metric("Active Branches", f"{df['branch'].nunique()}")

tabs = st.tabs([
    "📈 Daily Trend", "🥧 Transaction Types", "🏢 Branch Analysis",
    "💳 Mode Analysis", "❌ Failed Transactions", "👤 Customer Search",
    "💰 Account Summaries", "📊 Scatter & Histogram", "📋 Report"
])

# ---------------------------------------------------------------------------
# TAB: Daily Transaction Trend
# ---------------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Daily Transaction Trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Transaction volume and amount trends over time</div>', unsafe_allow_html=True)

    daily = df.groupby(df["date"].dt.date).agg(
        transaction_count=("transaction_id", "count"),
        total_amount=("amount", "sum"),
        success_count=("status", lambda s: (s == "Success").sum()),
        failed_count=("status", lambda s: (s == "Failed").sum()),
    ).reset_index().rename(columns={"date": "day"})

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=daily["day"], y=daily["transaction_count"], name="Transaction Count",
                               mode="lines+markers", line=dict(color="#203a43", width=2)))
    fig1.update_layout(title="Daily Transaction Count", xaxis_title="Date", yaxis_title="Count",
                        height=380, plot_bgcolor="white")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.area(daily, x="day", y="total_amount", title="Daily Transaction Amount (₹)")
    fig2.update_traces(line_color="#2c5364", fillcolor="rgba(44,83,100,0.2)")
    fig2.update_layout(height=350, plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(daily, x="day", y=["success_count", "failed_count"], barmode="stack",
                   title="Daily Success vs. Failed Transactions",
                   color_discrete_map={"success_count": "#1c9d5c", "failed_count": "#d64545"})
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB: Transaction Type Pie Chart
# ---------------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🥧 Transaction Type Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Distribution of transactions by type</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        type_counts = df["txn_type"].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, hole=0.45,
                     title="By Transaction Count",
                     color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        type_amount = df.groupby("txn_type")["amount"].sum().sort_values(ascending=False)
        fig2 = px.pie(values=type_amount.values, names=type_amount.index, hole=0.45,
                      title="By Transaction Amount (₹)",
                      color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        df.groupby("txn_type").agg(
            count=("transaction_id", "count"), total_amount=("amount", "sum"),
            avg_amount=("amount", "mean")
        ).reset_index().style.format({"total_amount": "₹{:,.2f}", "avg_amount": "₹{:,.2f}"}),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB: Branch-wise Analysis
# ---------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏢 Branch-wise Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Performance and volume comparison across branches</div>', unsafe_allow_html=True)

    branch_summary = df.groupby("branch").agg(
        total_transactions=("transaction_id", "count"),
        total_amount=("amount", "sum"),
        avg_amount=("amount", "mean"),
        failed_count=("status", lambda s: (s == "Failed").sum()),
        unique_customers=("customer_id", "nunique"),
    ).reset_index()
    branch_summary["success_rate"] = round(
        100 * (branch_summary["total_transactions"] - branch_summary["failed_count"]) / branch_summary["total_transactions"], 1
    )
    branch_summary = branch_summary.sort_values("total_amount", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(branch_summary, x="branch", y="total_amount", title="Total Transaction Amount by Branch",
                     color="total_amount", color_continuous_scale="Teal")
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(branch_summary, x="branch", y="success_rate", title="Success Rate by Branch (%)",
                      color="success_rate", color_continuous_scale="RdYlGn")
        fig2.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        branch_summary.style.format({"total_amount": "₹{:,.2f}", "avg_amount": "₹{:,.2f}", "success_rate": "{:.1f}%"}),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB: Transaction Mode Analysis
# ---------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💳 Transaction Mode Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Usage and reliability across payment modes (UPI, NEFT, Card, etc.)</div>', unsafe_allow_html=True)

    mode_summary = df.groupby("txn_mode").agg(
        total_transactions=("transaction_id", "count"),
        total_amount=("amount", "sum"),
        failed_count=("status", lambda s: (s == "Failed").sum()),
    ).reset_index()
    mode_summary["success_rate"] = round(
        100 * (mode_summary["total_transactions"] - mode_summary["failed_count"]) / mode_summary["total_transactions"], 1
    )
    mode_summary = mode_summary.sort_values("total_transactions", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(mode_summary, x="txn_mode", y="total_transactions", title="Transactions by Mode",
                     color="txn_mode")
        fig.update_layout(showlegend=False, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(mode_summary, x="txn_mode", y="success_rate", title="Success Rate by Mode (%)",
                      color="success_rate", color_continuous_scale="RdYlGn")
        fig2.update_layout(xaxis_tickangle=-20)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        mode_summary.style.format({"total_amount": "₹{:,.2f}", "success_rate": "{:.1f}%"}),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB: Failed Transaction Report
# ---------------------------------------------------------------------------
with tabs[4]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">❌ Failed Transaction Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Details and root causes of failed transactions</div>', unsafe_allow_html=True)

    failed_df = df[df["status"] == "Failed"].sort_values("date", ascending=False)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Failed", f"{len(failed_df):,}")
    c2.metric("Failed Amount", money(failed_df["amount"].sum()))
    c3.metric("Failure Rate", f"{100 * len(failed_df) / max(len(df), 1):.2f}%")

    col1, col2 = st.columns(2)
    with col1:
        reason_counts = failed_df["failure_reason"].value_counts()
        fig = px.bar(reason_counts, orientation="h", title="Failure Reasons",
                     color_discrete_sequence=["#d64545"])
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fail_by_branch = failed_df.groupby("branch")["transaction_id"].count().sort_values(ascending=False)
        fig2 = px.bar(fail_by_branch, title="Failed Transactions by Branch",
                      color_discrete_sequence=["#d64545"])
        fig2.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        failed_df[["date", "transaction_id", "customer_name", "account_id", "branch",
                   "amount", "txn_type", "txn_mode", "failure_reason"]],
        use_container_width=True, height=380
    )
    csv = failed_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Failed Transactions (CSV)", csv, "failed_transactions.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB: Customer Search
# ---------------------------------------------------------------------------
with tabs[5]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Customer Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Look up a customer to see their profile and transaction history</div>', unsafe_allow_html=True)

    search_term = st.text_input("Search by customer name or ID", "")

    if search_term:
        matches = customers_df[
            customers_df["customer_name"].str.contains(search_term, case=False) |
            customers_df["customer_id"].str.contains(search_term, case=False)
        ]
    else:
        matches = customers_df

    if len(matches) == 0:
        st.warning("No matching customers found.")
    else:
        options = matches.apply(lambda r: f"{r.customer_name} ({r.customer_id})", axis=1).tolist()
        chosen = st.selectbox("Select customer", options)
        cust_id = chosen.split("(")[-1].strip(")")
        cust_row = customers_df[customers_df.customer_id == cust_id].iloc[0]
        cust_txns = df[df.customer_id == cust_id].sort_values("date", ascending=False)
        cust_accounts = accounts_df[accounts_df.customer_id == cust_id]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Customer", cust_row["customer_name"])
        c2.metric("Home Branch", cust_row["home_branch"])
        c3.metric("Accounts", f"{len(cust_accounts)}")
        c4.metric("Total Transactions", f"{len(cust_txns)}")

        col1, col2 = st.columns(2)
        with col1:
            spend = cust_txns[cust_txns.direction == "Debit"].groupby("txn_type")["amount"].sum()
            if not spend.empty:
                fig = px.pie(values=spend.values, names=spend.index, title="Spend by Transaction Type", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("**Accounts**")
            st.dataframe(cust_accounts[["account_id", "account_type", "branch", "opening_balance"]],
                        use_container_width=True)

        st.markdown("**Transaction History**")
        st.dataframe(
            cust_txns[["date", "account_id", "amount", "direction", "txn_type", "txn_mode", "status"]],
            use_container_width=True, height=320
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB: Account Summaries
# ---------------------------------------------------------------------------
with tabs[6]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💰 Account Summaries</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Balances, activity, and totals per account</div>', unsafe_allow_html=True)

    success_df = df[df.status == "Success"]
    latest_balance = success_df.sort_values("date").groupby("account_id")["balance_after"].last().rename("current_balance")

    acc_summary = success_df.groupby(["account_id", "customer_name", "account_type", "branch"]).agg(
        total_transactions=("transaction_id", "count"),
        total_debits=("amount", lambda s: s[success_df.loc[s.index, "direction"] == "Debit"].sum()),
        total_credits=("amount", lambda s: s[success_df.loc[s.index, "direction"] == "Credit"].sum()),
        last_activity=("date", "max"),
    ).reset_index().merge(latest_balance, on="account_id", how="left")
    acc_summary["net_flow"] = acc_summary["total_credits"] - acc_summary["total_debits"]
    acc_summary = acc_summary.sort_values("current_balance", ascending=False)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Accounts", f"{len(acc_summary):,}")
    c2.metric("Total Balance", money(acc_summary["current_balance"].sum()))
    c3.metric("Avg Balance", money(acc_summary["current_balance"].mean()))

    search_acc = st.text_input("Search by account ID or customer name", key="acc_search")
    view = acc_summary
    if search_acc:
        view = view[view["account_id"].str.contains(search_acc, case=False) |
                    view["customer_name"].str.contains(search_acc, case=False)]

    st.dataframe(
        view.style.format({"total_debits": "₹{:,.2f}", "total_credits": "₹{:,.2f}",
                            "current_balance": "₹{:,.2f}", "net_flow": "₹{:,.2f}"}),
        use_container_width=True, height=400
    )

    fig = px.histogram(acc_summary, x="current_balance", color="account_type", nbins=25,
                       title="Balance Distribution by Account Type")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB: Scatter Plot & Histogram
# ---------------------------------------------------------------------------
with tabs[7]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Scatter Plot Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Relationship between transaction amount and time of day</div>', unsafe_allow_html=True)

    plot_df = df.copy()
    plot_df["hour"] = plot_df["date"].dt.hour
    fig = px.scatter(plot_df, x="hour", y="amount", color="status",
                     size="amount", size_max=14, opacity=0.6,
                     color_discrete_map={"Success": "#1c9d5c", "Failed": "#d64545"},
                     title="Transaction Amount vs. Hour of Day",
                     labels={"hour": "Hour of Day", "amount": "Amount (₹)"})
    st.plotly_chart(fig, use_container_width=True)

    fig_scatter2 = px.scatter(plot_df.sample(min(2000, len(plot_df))), x="date", y="amount",
                              color="txn_type", title="Transaction Amount Over Time (by Type)",
                              labels={"date": "Date", "amount": "Amount (₹)"})
    st.plotly_chart(fig_scatter2, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:20px;">📉 Histogram</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Distribution of transaction amounts</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.histogram(df, x="amount", nbins=40, title="Transaction Amount Distribution",
                            color_discrete_sequence=["#203a43"])
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = px.histogram(df, x="amount", color="status", nbins=40, barmode="overlay",
                            title="Amount Distribution by Status",
                            color_discrete_map={"Success": "#1c9d5c", "Failed": "#d64545"})
        st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB: Professional Report Section
# ---------------------------------------------------------------------------
with tabs[8]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Professional Summary Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Executive summary for the selected date range and filters</div>', unsafe_allow_html=True)

    total_txns = len(df)
    total_amount = df["amount"].sum()
    success_rate = 100 * (df["status"] == "Success").mean() if total_txns else 0
    failed_amount = df.loc[df.status == "Failed", "amount"].sum()
    top_branch = df.groupby("branch")["amount"].sum().idxmax() if total_txns else "N/A"
    top_mode = df["txn_mode"].value_counts().idxmax() if total_txns else "N/A"
    top_type = df["txn_type"].value_counts().idxmax() if total_txns else "N/A"

    report_html = f"""
    <div style="font-family:'Segoe UI',sans-serif; line-height:1.7;">
    <h3 style="color:#203a43;">Transaction Summary — {start_date} to {end_date}</h3>
    <table style="width:100%; border-collapse:collapse;">
      <tr><td style="padding:8px 0; color:#708090;">Total Transactions</td><td style="text-align:right; font-weight:600;">{total_txns:,}</td></tr>
      <tr><td style="padding:8px 0; color:#708090;">Total Transaction Value</td><td style="text-align:right; font-weight:600;">{money(total_amount)}</td></tr>
      <tr><td style="padding:8px 0; color:#708090;">Overall Success Rate</td><td style="text-align:right; font-weight:600;">{success_rate:.2f}%</td></tr>
      <tr><td style="padding:8px 0; color:#708090;">Failed Transaction Value</td><td style="text-align:right; font-weight:600; color:#d64545;">{money(failed_amount)}</td></tr>
      <tr><td style="padding:8px 0; color:#708090;">Top Performing Branch</td><td style="text-align:right; font-weight:600;">{top_branch}</td></tr>
      <tr><td style="padding:8px 0; color:#708090;">Most Used Payment Mode</td><td style="text-align:right; font-weight:600;">{top_mode}</td></tr>
      <tr><td style="padding:8px 0; color:#708090;">Most Common Transaction Type</td><td style="text-align:right; font-weight:600;">{top_type}</td></tr>
      <tr><td style="padding:8px 0; color:#708090;">Unique Customers Active</td><td style="text-align:right; font-weight:600;">{df['customer_id'].nunique():,}</td></tr>
      <tr><td style="padding:8px 0; color:#708090;">Branches Covered</td><td style="text-align:right; font-weight:600;">{df['branch'].nunique()}</td></tr>
    </table>
    </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Branch Performance Ranking**")
    branch_rank = df.groupby("branch").agg(
        total_amount=("amount", "sum"), total_transactions=("transaction_id", "count")
    ).sort_values("total_amount", ascending=False).reset_index()
    branch_rank.index = branch_rank.index + 1
    st.dataframe(branch_rank.style.format({"total_amount": "₹{:,.2f}"}), use_container_width=True)

    st.markdown("**Download Full Report Data**")
    full_report_csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Complete Transaction Report (CSV)", full_report_csv,
                       "banking_transaction_report.csv", "text/csv")

    st.caption(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
              f"Data covers {start_date} to {end_date}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Advanced Banking Transaction Dashboard | Built with Streamlit & Plotly | Demo data is synthetic.")
