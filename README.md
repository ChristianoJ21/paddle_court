# paddle_court
# 🏓 Paddle Court Rental System

A web-based Paddle Court Rental System built using **Streamlit (Python)** and **MySQL**.
This application allows users to manage courts, bookings, users, and payments with a modern UI using horizontal card layouts.

---

## 🚀 Features

* 👤 User Management (Add & View)
* 🏟️ Court Management (Card UI Display)
* 📅 Booking System (Time-based scheduling)
* 💳 Payment Tracking
* 🎨 Modern Dark UI with horizontal cards
* 🔄 Full CRUD functionality

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python
* **Database**: MySQL
* **Libraries**:

  * pandas
  * mysql-connector-python

---

## 📦 Requirements

Make sure you have installed:

* Python (>= 3.9 recommended)
* MySQL Server
* Git

---

## ⚙️ Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/ChristianoJ21/paddle_court.git
cd paddle_court
```

---

### 2. Create Virtual Environment (Recommended)

#### On macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install streamlit mysql-connector-python pandas
```

---

### 4. Setup MySQL Database

Open MySQL and run:

```sql
CREATE DATABASE paddle_court_db;
USE paddle_court_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone_number VARCHAR(15)
);

CREATE TABLE courts (
    court_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hourly_rate DECIMAL(5,2) NOT NULL
);

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    court_id INT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status ENUM('pending','confirmed','cancelled') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (court_id) REFERENCES courts(court_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    amount DECIMAL(6,2) NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);
```

---

### 5. Configure Database Connection

Open `app.py` and update this section if needed:

```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="paddle_court_db"
    )
```

⚠️ Make sure:

* Database name = **paddle_court_db** (exact match)
* MySQL is running

---

### 6. Run the Application

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

## 🧪 Dummy Data (Optional)

You can insert sample data manually using SQL to test the system.

---

## 📸 Screenshots

(Add your app screenshots here for better presentation)

---

## ⚠️ Notes

* The system currently allows overlapping bookings
* Future improvement: add **booking validation system**

---

## 🚀 Future Improvements

* ✅ Prevent double booking
* 📊 Dashboard (analytics & revenue)
* 🔐 Authentication system (Admin/User roles)
* 🌐 Deployment (Streamlit Cloud)

---

## 👨‍💻 Author

Developed by **Christiano Jose Intoro**
Computer Science Student @ Universitas Gadjah Mada

---

## ⭐ Support

If you find this project useful, feel free to ⭐ the repository!
