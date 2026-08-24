# 🖥️ Sunucu & IT Envanteri Yönetim Sistemi (GIG Server Inventory)

Comprehensive, multi-lingual enterprise IT asset inventory management system built with Python Flask, MySQL, Chart.js, and Active Directory LDAP integration.

---

## 🌟 Key Features

- **IT Server Inventory (`/`)**: Manage servers with specs (CPU, RAM, Disk, IP, OS, Project), custom dynamic columns, filtering, and sorting.
- **Network Devices (`/networkdevices`)**: Asset management for Switches, Routers, Firewalls, Access Points, Modems, and custom device types.
- **Client Workstation Management (`/clients`)**: Track client PCs with live Active Directory (AD LDAP) synchronization.
- **Interactive Dashboard (`/dashboard`)**: Chart.js metrics for Server OS distribution, Network Devices, Client OS counts, Disk/RAM/CPU allocations, and top capacity machines.
- **Database Management & Backups (`/database`)**:
  - Native Python SQL export/import & database restoration.
  - Configurable automated database backup scheduler (Daily, Weekly, Monthly).
  - MySQL service status check and control.
  - Security configuration & database password modification.
- **Audit Logs (`/logs`)**: Comprehensive action history recording all user operations.
- **Role-Based Access Control (RBAC)**: Distinct permissions for Admin vs Visitor users.
- **Bilingual Interface**: Full Turkish (TR) and English (EN) language support.

---

## 📋 System Prerequisites

Before running the application on a new server or local machine, ensure the following are installed:

1. **Python**: Version `3.10` or higher.
2. **MySQL Server**: Version `8.0` or higher (running on local port `3306` or remote server).
3. **Active Directory Domain Controller** *(Optional)*: Required only if testing live Active Directory client synchronization.

---

## 🚀 Quick Setup & Installation Guide

### Step 1: Copy Environment Configuration File

Copy the template `.env.example` file to create your local `.env` configuration file:

```bash
cp .env.example .env
```

Open `.env` in a text editor and update the database and Active Directory credentials to match your environment:

```ini
SECRET_KEY=your_secure_random_key

# MySQL Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=sunucu_envanteri

# Active Directory Integration (Optional)
LDAP_SERVER=ldap://192.168.1.10:389
LDAP_DOMAIN=yourdomain.com
```

---

### Step 2: Import the Database Schema

Import the provided SQL dump file `serverinventorydeneme.sql` into your MySQL server:

**Using Command Line:**
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS sunucu_envanteri;"
mysql -u root -p sunucu_envanteri < serverinventorydeneme.sql
```

**Using MySQL Workbench / phpMyAdmin:**
1. Create a new database named `sunucu_envanteri`.
2. Import `serverinventorydeneme.sql` into the database.

---

### Step 3: Install Python Dependencies

Install all required Python packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### Step 4: Launch the Application

Run the Flask application:

```bash
python app.py
```

By default, the server will start at:
👉 **`http://localhost:5000`** (or `http://0.0.0.0:5000`)

---

## 🔑 Default Accounts & Access Control

- **Admin Account**: Has full read/write access to add, edit, delete servers, run AD sync, configure database backups, and view audit logs.
- **Visitor Account**: Read-only access to inventory, dashboard, and network devices.

---

## 🛠️ Configuration Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **MySQL Connection Failed** | Verify `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` in your `.env` file and ensure the MySQL service is running. |
| **AD Sync Failed** | Verify `LDAP_SERVER` and `LDAP_DOMAIN` in `.env`. Ensure your network has access to port `389` (or `636` for LDAPS). |
| **Permission Errors on Windows Service** | Run Python/Flask terminal as Administrator if using the Windows MySQL service start button. |

---

## 📁 Project Structure Overview

```text
SunucuEnvanter/
├── app.py                 # Core Flask backend routes & logic
├── scheduler.py           # Background database backup scheduler
├── requirements.txt       # Python package dependencies
├── .env.example           # Environment template file
├── serverinventorydeneme.sql # Initial database dump file
├── static/                # CSS styles, JS scripts, and translation JSONs
│   ├── css/style.css
│   └── js/translations/   # tr.json & en.json
└── templates/             # HTML templates (Jinja2)
```
