# GateLog - Apartment Guest Register

GateLog is a Flask web application for managing apartment guest entries with separate resident and security access.

## Project Folder

`/Users/geephylimon/Documents/New project/GateLog-Apartment-Guest-Register`

## Tech Stack

- Backend: Python Flask
- Frontend: HTML, CSS, minimal JavaScript
- Storage: In-memory list and dictionary data

## Features

- Resident login with flat number and password
- Security login with security name and password
- Residents can add, view, and delete guests
- Flat number is locked while adding a guest
- Past dates cannot be selected
- Inline validation for guest name, phone number, and date
- Security can view all guest records
- Security can filter by flat number and search records
- Security can mark entry and exit timestamps
- Logout flyout confirmation
- Mobile-friendly layout

## Demo Login Credentials

### Resident

- Flat Number: `A101`
- Password: `resident123`

### Security

- Security Name: `Security 1`
- Password: `gate123`

- Security Name: `Security 2`
- Password: `gate234`

- Security Name: `Security 3`
- Password: `gate345`

## Run Locally

Open Terminal and run:

```bash
cd "/Users/geephylimon/Documents/New project/GateLog-Apartment-Guest-Register"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open in browser:

`http://127.0.0.1:5001`

## Run on Replit

This project is already prepared for Replit with:

- `.replit`
- `replit.nix`
- Flask app reading `HOST` and `PORT` from environment variables

### Steps

1. Open [Replit](https://replit.com/).
2. Create a new Repl or choose `Import from GitHub`.
3. Upload this project folder or import the GitHub repository.
4. Replit will install dependencies from `requirements.txt`.
5. Click `Run`.
6. Replit will open the web preview automatically.

## Upload to GitHub Without Terminal

You can upload this project using GitHub Desktop.

### Steps in GitHub Desktop

1. Open `GitHub Desktop`.
2. Click `File > Add Local Repository`.
3. Select this folder:
   `/Users/geephylimon/Documents/New project/GateLog-Apartment-Guest-Register`
4. If it is not already a repository, click `Create a Repository`.
5. Use a repository name like:
   `GateLog-Apartment-Guest-Register`
6. Click `Create Repository`.
7. In the bottom-left commit box, enter:
   `Initial GateLog app`
8. Click `Commit to main`.
9. Click `Publish Repository`.
10. Choose public or private and finish publishing.

## Import GitHub Project into Replit

1. Open [Replit](https://replit.com/).
2. Choose `Import from GitHub`.
3. Select your GitHub repository.
4. Click `Import`.
5. Click `Run`.

## Project Structure

```text
GateLog-Apartment-Guest-Register/
├── .replit
├── replit.nix
├── app.py
├── requirements.txt
├── README.md
├── static/
│   └── style.css
├── templates/
│   ├── add_guest.html
│   ├── login.html
│   ├── resident.html
│   └── security.html
└── test_app.py
```

## Notes

- Data is stored in memory, so records reset when the app restarts.
- Entry and exit timestamps use Python `datetime`.
- Replit compatibility is already configured.
