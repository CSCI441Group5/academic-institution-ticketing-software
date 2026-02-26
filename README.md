# Academic Institution Ticketing Software (2026S_CSCI441_VB Group 5)

## Project Overview

This project is a prototype for an automatic school ticket-based system
to allow for faculty/staff to submit support tickets and to allow for tech managers to manage and settle them.

The system is being developed via an agile-based design.

## Current Features

- User authentication via university login
- Submission spot for support tickets
- IT staff ticket list and status administration
- Email notification for confirmations

## Planned Features

- Ticket storage
- Automatic ticket routing
- Individualized dashboards
- Search feature for tickets

## Technology

- Frontend: Python/HTML & CSS
- Backend: Python/SQL
- Database: SQL

## How to run the project

### 1. Clone the repository

```
git clone https://github.com/CSCI441Group5/academic-institution-ticketing-software.git
cd academic-institution-ticketing-software
```

### 2. Run setup script

**macOS / Linux**

```
./setup.sh
```

**Windows (PowerShell)**

```
.\setup.ps1
```

This creates `.venv` (if missing) and installs dependencies.

### 3. Run the application

**macOS / Linux**

```
./run.sh
```

**Windows (PowerShell)**

```
.\run.ps1
```

**Manual run**

```
python run.py
```

If outside the virtual environment:

```
python3 run.py
```

### 4. Open in your browser

```
http://127.0.0.1:5000
```

## Manual setup (alternative)

### 1. Create and activate a virtual environment

**macOS / Linux**

```
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```
python -m venv .venv
.venv\Scripts\Activate
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run the application

```
python run.py
```

If outside the virtual environment:

```
python3 run.py
```

### 4. Open in your browser

```
http://127.0.0.1:5000
```

## Troubleshooting

**“command not found: python”**

```
python3 run.py
```

**Flask not found**

```
source .venv/bin/activate
```

## Quick Start

- First-time setup (or when dependencies change):
    - macOS / Linux: `./setup.sh`
    - Windows (PowerShell): `.\setup.ps1`

- Run the app:
    - macOS / Linux: `./run.sh`
    - Windows (PowerShell): `.\run.ps1`
