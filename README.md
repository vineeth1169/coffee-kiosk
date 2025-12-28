# Coffee Shop Kiosk Application

[![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<repo>/actions)

> Replace `<owner>/<repo>` in the badge URL with your repository's owner and name so the badge shows build status.

This project is a simple coffee shop kiosk application that allows users to choose from a selection of coffee items, add them to a cart, and proceed to checkout. Users can cancel their actions at any time and clear their cart if needed.

## Project Structure

```
coffee-kiosk
├── src
│   ├── main.py
│   ├── kiosk.py
│   ├── menu.py
│   └── cart.py
├── tests
│   └── test_kiosk.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Instructions to Ensure Python is Installed and Run the Code

### Database setup (quick: SQLite)
By default the app now uses a local SQLite database for development, so you can run the server without installing or configuring MySQL.

1. (Optional) Copy `.env.example` to `.env` and set any overrides. If you do nothing, the app will use `sqlite:///dev.db` by default.

2. Initialize DB tables (quick):

```bash
python scripts/init_db.py
```

### Database setup (MySQL — optional)
If you prefer MySQL for production or testing, set the `MYSQL_*` variables in `.env` (or `SQLALCHEMY_DATABASE_URI`) and then run migrations:

```sql
CREATE DATABASE coffee_kiosk;
CREATE USER 'coffee_user'@'localhost' IDENTIFIED BY 'securepassword';
GRANT ALL PRIVILEGES ON coffee_kiosk.* TO 'coffee_user'@'localhost';
FLUSH PRIVILEGES;
```

Then update `.env` accordingly and run:

```bash
python scripts/init_db.py
# or use migrations
flask db init && flask db migrate && flask db upgrade
```

1. **Check if Python is Installed**:
   - Open a terminal or command prompt.
   - Type `python --version` or `python3 --version` and press Enter. If Python is installed, you will see the version number. If not, install Python from https://www.python.org/downloads/.

2. **(Recommended) Create & activate a virtual environment**:
   - PowerShell:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - Command Prompt (cmd.exe):
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Run the Flask + Socket.IO server (development)**:

- Copy `.env.example` to `.env` and fill in your MySQL credentials (or set env vars directly).
- Create the database in MySQL (example):
```sql
CREATE DATABASE coffee_kiosk;
```
- Run the app (uses eventlet for Socket.IO):
```bash
# from project root
python -m pip install -r requirements.txt
python -c "from src.app import create_app; from src.extensions import db; app=create_app();
with app.app_context(): db.create_all(); print('DB ready')"
socketio
# or run the server directly
python -m src.server
```

- Then open http://localhost:5000 to use the UI.

- The UI accepts either an item number or an item name (case-insensitive). For example, you can type `2` or `Latte` or `latte` to add a Latte. Typing `coffee` maps to `Espresso`.

5. **Run the tests**:

- Unit tests (pytest):
```bash
pip install -r requirements.txt
pytest -q
```

- End-to-end (E2E) UI tests with Playwright (recommended for UI flows):

  1. Install Playwright and browser binaries:
  ```bash
  pip install playwright pytest-playwright
  python -m playwright install --with-deps
  ```
  2. Run the E2E test(s):
  ```bash
  pytest tests/test_e2e_ui.py -q
  ```

The `scripts/setup_env.ps1` helper installs Playwright browsers automatically when run on Windows. In CI we also install browsers before running E2E tests.
6. **Notes**:
- The server will emit real-time events for `new_order`, `update_totals`, and `per_item_sales` which the UI subscribes to.
- For production, use proper MySQL credentials, secure SECRET_KEY, and consider running behind a WSGI server with eventlet or gevent.

## Features

- Choose from 7 different coffee items.
- Add items to the cart.
- Checkout and view total price.
- Cancel actions at any time.
- Clear the cart if needed.

Feel free to explore the code and modify it to suit your needs!