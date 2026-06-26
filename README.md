# 🚑 XAMPP MariaDB System Database Repair

A small Windows Batch utility that automatically repairs a corrupted **MariaDB system database (`mysql`)** in XAMPP.

This tool was created after repeatedly encountering an issue where:

* Apache starts normally
* MySQL appears to start
* phpMyAdmin loads forever
* `mysql.exe` freezes
* PHP applications hang while connecting to MySQL
* Error log contains:

```
Fatal error:
Can't open and lock privilege tables:
Incorrect file format 'db'
```

Instead of manually replacing the system database every time, this script automates the repair process.

---

# Features

* Stops MariaDB safely
* Creates a backup of the existing `mysql` system database
* Restores a clean copy from the XAMPP backup folder
* Preserves all user databases
* Simple interactive interface
* Works with any XAMPP installation path

---

# What this repairs

Only the **system database**:

```
xampp/mysql/data/mysql
```

Your databases such as:

```
project_db
shop_db
portfolio_db
sps
deukhuri_shop
```

remain untouched.

---

# Requirements

* Windows
* XAMPP
* MariaDB
* Administrator privileges

---

# How to Use

## 1. Download

Clone the repository or download the ZIP.

---

## 2. Run

Right-click

```
repair-mysql.bat
```

Select

```
Run as Administrator
```

---

## 3. Enter your XAMPP path

Example

```
C:\xampp
```

The script automatically repairs the system database.

---

## 4. Start MySQL

Open

```
XAMPP Control Panel
```

Click

```
Start
```

---

# Folder Structure Expected

```
xampp
│
├── mysql
│   ├── backup
│   │    └── mysql
│   │
│   └── data
│        └── mysql
```

---

# Root Cause

This issue occurs when the MariaDB **system privilege tables become corrupted**.

Typical symptoms include:

* phpMyAdmin infinite loading
* MySQL client freezes
* PHP mysqli connection hangs
* Database applications never finish loading

The repair replaces only the corrupted system database using XAMPP's original backup.

---

# Safety

The script only replaces:

```
mysql/
```

It does **NOT** delete:

* Your databases
* Tables
* User project data

However, keeping regular backups is always recommended.

---

# Tested On

* Windows 11
* XAMPP 8.x
* MariaDB 10.4.x

---

# Author

**Promise**

BCA Student

Cybersecurity • Networking 

---

# License

MIT License
