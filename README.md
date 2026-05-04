# ISE MAB Helpdesk Application

A simple and secure web tool that allows Help Desk technicians to add, remove, and view MAC addresses in Cisco ISE Endpoint Identity Groups without logging into the ISE GUI.

## Features
- View MAC addresses in any Endpoint Identity Group
- Add or update MAC addresses
- Remove MAC addresses from a group
- Dedicated Settings page for configuration
- Docker support

## Quick Start (Docker Recommended)

1. Download the project (Code → Download ZIP)
2. Extract the folder
3. Open PowerShell or Command Prompt inside the extracted folder and run:

   docker compose up --build -d

4. Open your browser and go to: http://localhost:8501

## How to Configure ISE Connection

1. In the left sidebar, click "1 Settings"
2. Enter your ISE PAN URL, ERS Username, and Password
3. Choose Authentication Type (Basic Auth for now)
4. Click "Save Settings"
5. Return to the main page using the sidebar

The app will automatically create/update the .env file with your settings.

## Configuration Example

ISE_URL=https://ise.yourcompany.com
ERS_USER=ers_helpdesk
ERS_PASS=YourSecurePassword

Security Note: Never commit your real .env file to GitHub.

## ISE Server Requirements

- ERS must be enabled (Administration → System → Settings → API Settings → Enable ERS Read/Write)
- Use a dedicated account assigned to the ERS Admin group

## Tech Stack
- Python 3.12
- Streamlit
- Cisco ISE ERS API
- Docker

## Support
For questions or feature requests, contact Will Turbeville.