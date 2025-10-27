# 💰 Smart Expense Tracker (Web + CLI)

The **Smart Expense Tracker** is a full-stack personal finance management app designed to help users easily track and analyze their daily expenses — from anywhere.  
It comes with a modern **Web Dashboard** for managing expenses visually and a powerful **Command-Line Interface (CLI)** for advanced and admin operations.

This project started as part of my journey in the IITM BS in Data Science and Applications program, where I wanted to build something practical that combines both **Software Engineering** and **Machine Learning** skills.

---

## 🚀 Project Overview

This app is a combination of:
- 🧾 **Web App** – for everyday users to log and visualize their expenses  
- ⚙️ **CLI Tool** – for admin tasks like data cleanup, backups, and generating reports  
- 🧠 **Smart Analytics** – for trend detection and auto-categorization using Machine Learning

Everything runs on a **common database**, so actions from the web or CLI stay in sync.

---

## 🧩 Features

### 👨‍💻 User-Facing Web Application
- Create an account, log in, and manage your expenses  
- Add, edit, or delete transactions with notes and categories  
- View spending summaries by category, month, and time range  
- Interactive visualizations (Chart.js) for better insights  
- Export data to CSV/Excel for offline analysis  

### 🧰 CLI Admin Tool
- Add or view expenses right from your terminal  
- Generate quick reports or statistics  
- Backup and clean database with one command  
- Train ML model for auto-tagging expenses (optional)  
- Perform admin operations securely  

### 🧠 Smart Insights 
- Expense categorization based on note text using NLP  
- Monthly trend prediction and spending alerts  

---

## 🧱 Tech Stack

| Layer | Technologies |
|--------|---------------|
| **Frontend** | Vue.js, HTML, CSS, JS, Chart.js |
| **Backend API** | Flask, REST API |
| **Database** | SQLite + SQLAlchemy ORM |
| **CLI** | Typer (Python) |
| **Data / ML** | Pandas, Scikit-learn |
| **Deployment** | Docker,  Railway |

---

## 🗂️ Project Structure

```
smart_expense_tracker/
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── expenses.py
│   │   └── reports.py
│   ├── database.py
│   ├── utils/
│   │   ├── analytics.py
│   │   ├── export.py
│   │   └── backup.py
│
├── frontend/
│   ├── static/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── add_expense.html
│   │   └── login.html
│
├── cli/
│   ├── cli.py
│
├── data/
│   ├── expenses.db
│   └── backups/
│
├── requirements.txt
├── config.py
├── README.md
└── Dockerfile
```

---

## 🧠 Learning Goals

This project helps me:
- Strengthen my **backend development** skills (Flask, REST APIs)
- Practice **database management** and ORM design  
- Build **clean CLI tools** for backend/admin workflows  
- Understand **data visualization** and interactive dashboards  
- Experiment with **basic ML features** like text classification  

---

## 🧩 Current Status
🔹 **Phase 1 (In Progress):** Database + CLI setup  
🔹 Phase 2: Flask API & routes  
🔹 Phase 3: Web Dashboard + Charts  
🔹 Phase 4: ML Insights + Deployment  

---

## 🧑‍💻 How to Run

```bash
# 1️⃣ Clone the repository
git clone https://github.com/23f2005532/Smart-Expense-Tracker-CLI-Dashboard-.git
cd Smart-Expense-Tracker-CLI-Dashboard-

# 2️⃣ Setup environment
python -m venv venv
venv\Scripts\activate 
pip install -r requirements.txt

# 3️⃣ Run the backend
cd backend
python app.py

# 4️⃣ Run the CLI
cd cli
python cli.py --help
```

---

## 📅 Development Timeline

| Phase | Goal | Status |
|-------|------|--------|
| Week 1 | CLI + Database setup | ⏳ In Progress |
| Week 2 | Flask backend routes | 🔜 Next |
| Week 3 | Web dashboard (frontend) | ⏳ Planned |
| Week 4 | ML analytics + Deployment | ⏳ Planned |

---

## 🧩 Future Enhancements
- Add JWT authentication and role-based access  
- Connect to PostgreSQL for production use  
- Add AI-based smart budgeting assistant  
- Mobile-friendly PWA dashboard  
- Cloud-hosted backups  

---

## 👨‍💻 Author
**Ehtesham Ansari**  
B.S. in Data Science and Applications, IIT Madras  
*Exploring Data Engineering, Automation, and MLOps*

If you like this project, feel free to ⭐ it or drop suggestions!

---

## 📜 License
This project is open-sourced under the **MIT License**.
