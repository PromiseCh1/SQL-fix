# Promise's XAMPP SQL Repair Utility

A professional Windows desktop application to diagnose and safely repair broken XAMPP MariaDB installations.  
Created by Promise.

## Features

- Auto-detect XAMPP installations on all drives.
- Manual folder selection.
- Comprehensive diagnostics (system, error logs, file tree, processes, network).
- Smart Repair – replaces only the system database (`mysql`) from the backup, preserving all user databases.
- Full backup before any repair.
- One‑click restore from previous backups.
- Generate detailed logs and diagnostics as a zip file.
- Clean, dark‑theme GUI built with PySide6.
- No emojis, production‑grade code.

## Requirements

- Windows 7/10/11
- Python 3.12+ (or use the compiled .exe)
- PySide6 and psutil (see `requirements.txt`)

## Installation

1. Clone this repository.
2. Install dependencies: