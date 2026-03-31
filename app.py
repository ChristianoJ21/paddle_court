import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# ======================
# DATABASE CONNECTION
# ======================
def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="paddle_court_db"
        )
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# ======================
# UI CONFIG
# ======================
st.set_page_config(page_title="Paddle Court Rent", layout="wide", page_icon="🎾")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: white; }
    h1, h2, h3 { color: #38bdf8 !important; }
    
    /* GRID LAYOUT FOR CARDS (FILLS BOTTOM INSTEAD OF SCROLLING) */
    .card-grid { 
        display: flex; 
        flex-wrap: wrap; 
        gap: 20px; 
        padding: 10px; 
        justify-content: flex-start;
    }
    
    .card { 
        background: #1e293b; 
        padding: 20px; 
        border-radius: 15px; 
        width: 300px; /* Fixed width so they align in a grid */
        box-shadow: 0 4px 12px rgba(0,0,0,0.4); 
        color: white; 
        border: 1px solid #334155;
    }
    
    .price { color: #22c55e; font-size: 20px; font-weight: bold; }
    .tag { background: #334155; padding: 5px 10px; border-radius: 10px; font-size: 12px; display: inline-block; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🏓 Paddle Court Rental System")

menu = ["Users", "Courts Catalog", "Bookings", "Payments"]
choice = st.sidebar.selectbox("Menu", menu)

conn = get_connection()
if conn:
    cursor = conn.cursor(dictionary=True)

    # ======================
    # USERS
    # ======================
    if choice == "Users":
        st.header("👤 Manage Users")
        with st.form("add_user", clear_on_submit=True):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            if st.form_submit_button("Add User"):
                cursor.execute("INSERT INTO users (full_name, email, phone_number) VALUES (%s,%s,%s)", (name, email, phone))
                conn.commit()
                st.success(f"User {name} added!")
                st.rerun()

        df_users = pd.read_sql("SELECT * FROM users", conn)
        st.dataframe(df_users, use_container_width=True)

    # ======================
    # COURTS (CATALOG ONLY - NO WEB CRUD)
    # ======================
    elif choice == "Courts Catalog":
        st.header("🏟️ Court Catalog")
        st.info("💡 Note: Court management is handled via MySQL Terminal for security.")
        
        df_courts = pd.read_sql("SELECT * FROM courts", conn)
        if not df_courts.empty:
            # Using card-grid for wrapping layout
            cards_html = '<div class="card-grid">'
            for _, row in df_courts.iterrows():
                idr_price = int(row['hourly_rate'] * 15000)
                cards_html += f"""
                <div class="card">
                    <h3>{row['name']}</h3>
                    <div class="tag">ID: {row['court_id']}</div>
                    <p class="price">Rp {idr_price:,}/hour</p>
                </div>"""
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)
        else:
            st.info("Catalog is empty.")

    # ======================
    # BOOKINGS (WITH FCFS LOGIC)
    # ======================
    elif choice == "Bookings":
        st.header("📅 Manage Bookings")
        
        users_df = pd.read_sql("SELECT user_id, full_name FROM users", conn)
        courts_df = pd.read_sql("SELECT court_id, name FROM courts", conn)

        if users_df.empty or courts_df.empty:
            st.warning("Please add data in Users and MySQL Courts table first.")
        else:
            with st.form("add_booking"):
                u_choice = st.selectbox("Select Customer", users_df['full_name'])
                c_choice = st.selectbox("Select Court", courts_df['name'])
                
                u_id = users_df[users_df['full_name'] == u_choice]['user_id'].values[0]
                c_id = courts_df[courts_df['name'] == c_choice]['court_id'].values[0]
                
                start = st.datetime_input("Start Time", value=datetime.now())
                end = st.datetime_input("End Time", value=datetime.now())
                status = st.selectbox("Status", ["confirmed", "pending", "cancelled"])

                if st.form_submit_button("Confirm Booking"):
                    start_str = start.strftime('%Y-%m-%d %H:%M:%S')
                    end_str = end.strftime('%Y-%m-%d %H:%M:%S')

                    # --- FCFS CONFLICT CHECK ---
                    # Check if any "confirmed" booking overlaps with this time for the SAME court
                    check_query = """
                        SELECT * FROM bookings 
                        WHERE court_id = %s 
                        AND status = 'confirmed'
                        AND NOT (end_time <= %s OR start_time >= %s)
                    """
                    cursor.execute(check_query, (int(c_id), start_str, end_str))
                    conflict = cursor.fetchone()

                    if conflict:
                        st.error(f"❌ CONFLICT: Court '{c_choice}' is already booked during this time!")
                    elif start >= end:
                        st.error("❌ ERROR: End time must be after start time.")
                    else:
                        cursor.execute(
                            "INSERT INTO bookings (user_id, court_id, start_time, end_time, status) VALUES (%s,%s,%s,%s,%s)",
                            (int(u_id), int(c_id), start_str, end_str, status)
                        )
                        conn.commit()
                        st.success("✅ Booking successful (FCFS)!")
                        st.rerun()

        st.subheader("Booking History")
        query = """
            SELECT b.booking_id, u.full_name, c.name AS court_name, b.start_time, b.end_time, b.status 
            FROM bookings b 
            JOIN users u ON b.user_id = u.user_id 
            JOIN courts c ON b.court_id = c.court_id
            ORDER BY b.start_time DESC
        """
        df_b = pd.read_sql(query, conn)
        if not df_b.empty:
            cards_html = '<div class="card-grid">'
            for _, row in df_b.iterrows():
                color = {"confirmed": "#22c55e", "pending": "#facc15", "cancelled": "#ef4444"}.get(row["status"], "white")
                cards_html += f"""
                <div class="card">
                    <h3>{row['court_name']}</h3>
                    <div class="tag">{row['full_name']}</div>
                    <p style="font-size: 13px; margin: 10px 0;">{row['start_time'].strftime('%d %b, %H:%M')}</p>
                    <p style="color:{color}; font-weight:bold;">{row['status'].upper()}</p>
                </div>"""
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)

    # ======================
    # PAYMENTS
    # ======================
    elif choice == "Payments":
        st.header("💳 Manage Payments")

        bookings = pd.read_sql("SELECT * FROM bookings", conn)

        with st.form("add_payment"):
            booking_id = st.selectbox("Booking", bookings["booking_id"])
            amount = st.number_input("Amount")
            date = st.date_input("Payment Date")

            if st.form_submit_button("Add Payment"):
                cursor.execute(
                    "INSERT INTO payments (booking_id, amount, payment_date) VALUES (%s,%s,%s)",
                    (booking_id, amount, date)
                )
                conn.commit()
                st.success("Payment added!")

        st.subheader("All Payments")
        df = pd.read_sql("SELECT * FROM payments", conn)
        st.dataframe(df, use_container_width=True)
    conn.close()