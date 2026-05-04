# ISE MAB Helpdesk Application

A simple and secure web tool that allows Help Desk technicians to add, remove, and view MAC addresses in Cisco ISE Endpoint Identity Groups without logging into the ISE GUI.

## Features
- View MAC addresses in any Endpoint Identity Group
- Add or update MAC addresses
- Remove MAC addresses from a group
- Protected Settings page (Admin only)
- Docker support

## Default Login Credentials

| Role     | Username   | Password    |
|----------|------------|-------------|
| Admin    | admin      | admin123    |
| User     | user       | user123     |

⚠️ Security Reminder: Please change the default passwords immediately after first login.

## Quick Start (Docker Recommended)

1. Download the project (Code → Download ZIP)
2. Extract the folder
3. Open PowerShell or Command Prompt inside the extracted folder and run:

   docker compose up --build -d

4. Open your browser and go to: http://localhost:8501
5. Login with one of the accounts above

## How to Configure (Admin Only)

1. Login as Admin
2. Click "1 Settings" in the left sidebar
3. Enter your ISE PAN URL, ERS Username, and Password
4. Click "Save ISE Settings"

## How to Change Login Accounts

1. Login as Admin
2. Go to Settings
3. Scroll to "Manage Login Accounts"
4. Update usernames/passwords
5. Click "Save Login Accounts"
6. Log out and log back in

## ISE Server Requirements

- Enable ERS API (Administration → System → Settings → API Settings)
- Create a dedicated user in the ERS Admin group

## Tech Stack
- Python 3.12
- Streamlit
- Cisco ISE ERS API
- Docker

## Support
Contact Will Turbeville for questions or enhancements.