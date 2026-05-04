# LibraTech Library Management System

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 8.0+ (or XAMPP/MariaDB)
- Git (optional)

### 1. Clone & Setup
```bash
git clone <repo>
cd lib_management_system
```

### 2. Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
- Start MySQL/XAMPP.
- Create database: `library_db`
- Update `.env` if not using defaults (root/no-password):
  ```
  DB_USER=root
  DB_PASSWORD=yourpassword
  DB_HOST=localhost
  DB_NAME=library_db
  DB_PORT=3306
  ```
- Run migrations: `python run_db_migration.py`

### 5. Run Server
```bash
# Method 1: Direct (recommended)
python app.py
```
OR
```bash
# Method 2: Flask CLI
flask run
```

**Server runs at: http://127.0.0.1:5000**

### 6. Default Login
- **Admin**: username `admin`, email `natividadkaeza05@gmail.com`, password `Admin12345`

## 🛠️ Features
- Student/Admin dashboards
- Book catalog, issue/return, reservations, fines
- QR/Barcode scanning
- Digital library (PDF reader)
- Analytics & reports
- Email notifications
- Automated fine calculation & scheduler

## Troubleshooting
- **Connection Refused**: Run `python app.py`, check terminal for DB errors.
- **DB Errors**: Verify MySQL running, credentials in `.env`.
- **Deps Missing**: `pip install -r requirements.txt`.
- Test DB: `python test_connection.py`

## Development
- Edit `.flaskenv` for env vars.
- `flask shell` for REPL (models pre-loaded).

Happy Libraring! 📚

