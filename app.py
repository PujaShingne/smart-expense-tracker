
import streamlit as st
import pandas as pd
import sqlite3

# Database Configuration
DB_NAME = "expenses.db"


# Create Database and Table

# Create Database and Table
def init_db():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)

    # Check whether date column already exists
    columns = [
        row[1] for row in conn.execute(
            "PRAGMA table_info(transactions)"
        ).fetchall()
    ]

    # Add date column if it is missing
    if "transaction_date" not in columns:
        conn.execute(
            "ALTER TABLE transactions ADD COLUMN transaction_date TEXT"
        )

    # Give older transactions today's date
    conn.execute("""
        UPDATE transactions
        SET transaction_date = date('now', 'localtime')
        WHERE transaction_date IS NULL
    """)

    conn.commit()
    conn.close()


# Initialize Database
init_db()

# Load Transactions from Database
def load_transactions():
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        """
        SELECT
            id AS ID,
            name AS Name,
            amount AS Amount,
            category AS Category,
            type AS Type,
            transaction_date AS Date
        FROM transactions
        """,
    conn
)

    conn.close()

    return df.to_dict("records")

# Page configuration
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# Professional Light Theme
st.markdown("""
<style>

/* Main application */
.stApp {
    background: #f3f6fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Headings */
h1, h2, h3 {
    color: #172554 !important;
    font-weight: 750 !important;
}

/* Text and labels */
p, label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    color: #263653 !important;
}

/* Input fields */
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #172554 !important;
    border: 1px solid #d5deed !important;
    border-radius: 9px !important;
}

/* Form cards */
[data-testid="stForm"] {
    background: #ffffff;
    padding: 24px;
    border: 1px solid #e1e8f2;
    border-radius: 14px;
}

/* Professional dashboard metric cards */
div[data-testid="stMetric"] {
    background: #ffffff;
    padding: 22px 20px;
    border-radius: 16px;
    border: 1px solid #e5eaf5;
    box-shadow: 0 4px 15px rgba(31, 55, 100, 0.06);
    transition: all 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 22px rgba(31, 55, 100, 0.12);
}

div[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #172554 !important;
    font-weight: 750;
}

/* Form buttons */
div[data-testid="stFormSubmitButton"] button {
    background-color: #3155d9 !important;
    color: #ffffff !important;
    border: 1px solid #3155d9 !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
}

div[data-testid="stFormSubmitButton"] button p,
div[data-testid="stFormSubmitButton"] button span {
    color: #ffffff !important;
}

div[data-testid="stFormSubmitButton"] button:hover {
    background-color: #2442b8 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #e9effb;
}

/* Download button */
div[data-testid="stDownloadButton"] button {
    background-color: #7c3aed !important;
    color: #ffffff !important;
    border: 1px solid #7c3aed !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
}

div[data-testid="stDownloadButton"] button p,
div[data-testid="stDownloadButton"] button span {
    color: #ffffff !important;
}

div[data-testid="stDownloadButton"] button:hover {
    background-color: #6d28d9 !important;
}

/* Dashboard chart corners */
div[data-testid="stArrowVegaLiteChart"],
div[data-testid="stVegaLiteChart"] {
    border-radius: 14px;
}

/* Dividers */
hr {
    border-color: #e2e8f0;
}

</style>
""", unsafe_allow_html=True)


# Initialize transaction storage
if "transactions" not in st.session_state:
    st.session_state.transactions = load_transactions()

# Migrate older transactions into SQLite
for transaction in st.session_state.transactions:
    if "ID" not in transaction:
        conn = sqlite3.connect(DB_NAME)

        cursor = conn.execute(
            """
            INSERT INTO transactions (name, amount, category, type)
            VALUES (?, ?, ?, ?)
            """,
            (
                transaction["Name"],
                transaction["Amount"],
                transaction["Category"],
                transaction["Type"]
            )
        )

        transaction["ID"] = cursor.lastrowid

        conn.commit()
        conn.close()
        
# Sidebar Navigation
st.sidebar.title("💰 Expense Tracker")
st.sidebar.write("Personal Finance Manager")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Transactions", "Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Manage your money smartly.")


# Main Header
st.title("💰 Smart Expense Tracker")
st.write("Welcome back! Here's your financial overview.")


# Prepare DataFrame
df = pd.DataFrame(
    st.session_state.transactions,
    columns=["Name", "Amount", "Category", "Type"]
)


# Calculate Financial Summary
income = df[df["Type"] == "Income"]["Amount"].sum()
expenses = df[df["Type"] == "Expense"]["Amount"].sum()
balance = income - expenses


# =====================================
# PAGE 1: DASHBOARD
# =====================================

if page == "Dashboard":

    st.header("📊 Financial Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Income", f"₹{income:.2f}")
    col2.metric("Total Expenses", f"₹{expenses:.2f}")
    col3.metric("Remaining Balance", f"₹{balance:.2f}")
    st.markdown("---")

    # Financial Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("💵 Income vs Expenses")

        comparison = pd.DataFrame(
            {"Amount": [income, expenses]},
            index=["Income", "Expenses"]
        )

        st.bar_chart(comparison)

    with chart_col2:
        st.subheader("🛍️ Spending by Category")

        expense_data = df[df["Type"] == "Expense"]

        if not expense_data.empty:
            category_total = expense_data.groupby(
                "Category"
            )["Amount"].sum()

            st.bar_chart(category_total)
        else:
            st.info("No expense data available yet.")
    st.markdown("---")

    st.subheader("📋 Recent Transactions")

    if not df.empty:
        st.dataframe(
            df.tail(5),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No transactions available yet. Add your first transaction!")


# =====================================
# PAGE 2: TRANSACTIONS
# =====================================

elif page == "Transactions":

    # Add Transaction
    st.header("➕ Add Transaction")

    with st.form("transaction_form"):

        name = st.text_input("Enter your name")

        amount = st.number_input(
            "Enter amount (₹)",
            min_value=0.0,
            step=10.0
        )

        category = st.selectbox(
            "Select category",
            ["Food", "Travel", "Shopping", "Education", "Other"]
        )

        transaction_type = st.selectbox(
            "Transaction type",
            ["Income", "Expense"]
        )
        transaction_date = st.date_input(
            "Select transaction date",
            value=pd.Timestamp.today().date()
        )  
        submitted = st.form_submit_button("Add Transaction")

        if submitted:

            if name.strip() == "":
                st.error("Please enter your name.")

            elif amount <= 0:
                st.error("Please enter a valid amount.")

            else:
                # Save transaction to SQLite Database
                conn = sqlite3.connect(DB_NAME)

                cursor = conn.execute(
                    """
                    INSERT INTO transactions
                    (name, amount, category, type, transaction_date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name.strip(),
                        amount,
                        category,
                        transaction_type,
                        transaction_date.isoformat()
                    )
                )
                transaction_id = cursor.lastrowid

                conn.commit()
                conn.close()

                # Update session state
                st.session_state.transactions.append({
                    "ID": transaction_id,
                    "Name": name.strip(),
                    "Amount": amount,
                    "Category": category,
                    "Type": transaction_type,
                    "Date": transaction_date.isoformat()
                })

                st.success("Transaction added successfully!")
                st.rerun()

    st.markdown("---")

    # Check whether transactions exist
    if st.session_state.transactions:

        df = pd.DataFrame(st.session_state.transactions)

        # Convert Date column into date format
        df["Date"] = pd.to_datetime(
            df["Date"], errors="coerce"
        ).dt.date


        # Date-wise filter
        st.subheader("📅 Filter by Date")

        min_date = df["Date"].min()
        max_date = df["Date"].max()

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )

        with col2:
            end_date = st.date_input(
                "End Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )


        # Transaction History
        st.header("📋 Transaction History")

        # Search by name
        search_name = st.text_input("🔍 Search by name")

        # Filter by category
        selected_category = st.selectbox(
            "Filter by category",
            ["All", "Food", "Travel", "Shopping", "Education", "Other"]
        )

        # Filter by type
        selected_type = st.selectbox(
            "Filter by type",
            ["All", "Income", "Expense"]
        )

        # Apply filters
        filtered_df = df.copy()
        if start_date and end_date:
            filtered_df = filtered_df[
                (filtered_df["Date"] >= start_date) &
                (filtered_df["Date"] <= end_date)
            ]

        if search_name:
            filtered_df = filtered_df[
                filtered_df["Name"].str.contains(
                    search_name,
                    case=False,
                    na=False
                )
            ]

        if selected_category != "All":
            filtered_df = filtered_df[
                filtered_df["Category"] == selected_category
            ]

        if selected_type != "All":
            filtered_df = filtered_df[
                filtered_df["Type"] == selected_type
            ]

        # Display transactions
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.write("Transactions found:", len(filtered_df))

        # CSV Download
        st.header("📥 Download Transactions")

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="my_transactions.csv",
            mime="text/csv"
        )

        st.markdown("---")

        # Edit Transaction
        st.header("✏️ Edit Transaction")

        selected_index = st.selectbox(
            "Select transaction to edit",
            range(len(st.session_state.transactions)),
            format_func=lambda i: (
                f"{i + 1}. "
                f"{st.session_state.transactions[i]['Name']} - "
                f"₹{st.session_state.transactions[i]['Amount']}"
            )
        )

        selected = st.session_state.transactions[selected_index]

        with st.form("edit_form"):

            edit_name = st.text_input(
                "Edit name",
                value=selected["Name"]
            )

            edit_amount = st.number_input(
                "Edit amount",
                min_value=0.01,
                value=float(selected["Amount"]),
                step=10.0
            )

            categories = [
                "Food", "Travel", "Shopping", "Education", "Other"
            ]

            edit_category = st.selectbox(
                "Edit category",
                categories,
                index=categories.index(selected["Category"])
            )

            types = ["Income", "Expense"]

            edit_type = st.selectbox(
                "Edit transaction type",
                types,
                index=types.index(selected["Type"])
            )
            edit_date = st.date_input(
                "Edit transaction date",
                value=pd.to_datetime(selected["Date"]).date()
            )

            update_button = st.form_submit_button("Update Transaction")

            if update_button:

                if edit_name.strip() == "":
                    st.error("Please enter a name.")

                else:
                    transaction_id = selected["ID"]

                    conn = sqlite3.connect(DB_NAME)

                    conn.execute(
                        """
                        UPDATE transactions
                        SET name = ?, amount = ?, category = ?, type = ?,
                            transaction_date = ?
                        WHERE id = ?
                        """,
                        (
                            (
                                edit_name.strip(),
                                edit_amount,
                                edit_category,
                                edit_type,
                                edit_date.isoformat(),
                                transaction_id
                            )
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.session_state.transactions[selected_index] = {
                        "ID": transaction_id,
                        "Name": edit_name.strip(),
                        "Amount": edit_amount,
                        "Category": edit_category,
                        "Type": edit_type,
                        "Date": edit_date.isoformat()
                    }

                    st.success("Transaction updated successfully!")
                    st.rerun()
        st.markdown("---")

        # Delete Transaction
        st.header("🗑️ Delete Transaction")

        with st.form("delete_form"):

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this transaction."
            )

            delete_button = st.form_submit_button("Delete Transaction")

            if delete_button:

                if confirm_delete:

                    transaction_id = selected["ID"]

                    conn = sqlite3.connect(DB_NAME)

                    conn.execute(
                        "DELETE FROM transactions WHERE id = ?",
                        (transaction_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.session_state.transactions.pop(selected_index)

                    st.success("Transaction deleted successfully!")
                    st.rerun()

                else:
                    st.warning("Please confirm before deleting.")

    else:
        st.info("No transactions available yet. Add your first transaction!")



# =====================================
# PAGE 3: ANALYTICS
# =====================================

elif page == "Analytics":

    st.header("📈 Financial Analytics")
    st.write("Track your monthly income, expenses and savings.")

    # Load transaction data
    analytics_df = pd.DataFrame(
        st.session_state.transactions
    )

    if not analytics_df.empty:

        # Convert Date into datetime format
        analytics_df["Date"] = pd.to_datetime(
            analytics_df["Date"],
            errors="coerce"
        )

        analytics_df = analytics_df.dropna(
            subset=["Date"]
        )

        # Create Month column
        analytics_df["Month"] = (
            analytics_df["Date"].dt.strftime("%B %Y")
        )

        # Calculate total income and expenses
        total_income = analytics_df[
            analytics_df["Type"] == "Income"
        ]["Amount"].sum()

        total_expenses = analytics_df[
            analytics_df["Type"] == "Expense"
        ]["Amount"].sum()

        balance = total_income - total_expenses

        # Financial Summary
        st.subheader("💰 Financial Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Income", f"₹{total_income:.2f}")
        col2.metric("Total Expenses", f"₹{total_expenses:.2f}")
        col3.metric("Remaining Balance", f"₹{balance:.2f}")

        st.markdown("---")

        # Monthly Financial Report
        st.subheader("📅 Monthly Financial Report")

        monthly_report = analytics_df.pivot_table(
            index="Month",
            columns="Type",
            values="Amount",
            aggfunc="sum",
            fill_value=0
        )

        # Add missing columns if necessary
        for column in ["Income", "Expense"]:
            if column not in monthly_report.columns:
                monthly_report[column] = 0

        monthly_report = monthly_report.rename(
            columns={"Expense": "Expenses"}
        )

        monthly_report["Balance"] = (
            monthly_report["Income"] -
            monthly_report["Expenses"]
        )

        monthly_report = monthly_report.reset_index()

        st.subheader("Monthly Report Table")

        # Format monthly report for display
        display_report = monthly_report.copy()

        for column in ["Income", "Expenses", "Balance"]:
            display_report[column] = display_report[column].apply(
                lambda x: f"₹{x:,.2f}"
            )

        st.table(display_report)

        st.markdown("---")

        # Monthly Income vs Expenses Chart
        st.subheader("📊 Monthly Income vs Expenses")

        chart_data = monthly_report.set_index("Month")[
            ["Income", "Expenses"]
        ]

        st.bar_chart(chart_data)

        st.markdown("---")

        # Category-wise Expense Analysis
        st.subheader("🛒 Category-wise Expenses")

        expense_data = analytics_df[
            analytics_df["Type"] == "Expense"
        ]

        if not expense_data.empty:

            category_total = expense_data.groupby(
                "Category"
            )["Amount"].sum()

            st.bar_chart(category_total)

        else:
            st.info("No expenses available for analysis.")

        st.markdown("---")

        # Transaction Statistics
        st.subheader("📊 Transaction Statistics")

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Transactions",
            len(analytics_df)
        )

        col2.metric(
            "Average Transaction",
            f"₹{analytics_df['Amount'].mean():.2f}"
        )

    else:
        st.info("No transactions available for analysis.")
