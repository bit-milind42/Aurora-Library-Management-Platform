<div align="center">

# Aurora Library Management Platform

</div>


Aurora is a compact, modern Library Management Platform focusing on the core circulation lifecycle (request → issue → return), automated fine handling, and a clean developer-friendly REST API. It combines a dark, minimal UI with practical backend workflows suitable for academic or small institutional libraries.

## Problem We Solve
Small libraries often rely on spreadsheets or ad‑hoc tools to track books, due dates, and fines—leading to inconsistency, data loss, and poor visibility. Aurora centralizes:
- Unified tracking of book availability & active issues
- Enforced one-active-issue-per-user-per-book rule
- Automatic overdue fine estimation
- Simple payment integration hook (Razorpay)
- Dual auth (web session + API tokens) for hybrid web + external client use

## Key Features 
- Custom user + student profile layer
- Catalog: books, authors, categories, cover images
- Issue workflow (request / active / return)
- Overdue fines + payment initiation
- JWT + session authentication
- REST API (DRF ViewSets, pagination)
- Dark responsive UI + dashboard + messages

## Tech Stack
Core: Django 4.x, Django REST Framework, SimpleJWT
DB: SQLite (dev) / easily switchable to Postgres
Payments: Razorpay (optional keys)
Auth: Session + JWT pair/refresh
UI: Custom dark theme (glass style)

## How To Run
```bash
python -m venv .venv
.venv\\Scripts\\Activate.ps1   # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
copy library\.env.example library\.env   # adjust secrets
cd library
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Visit: http://127.0.0.1:8000/

Optional Razorpay setup:
Add to `library/.env`:
```
RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
```

## License
MIT License – see `LICENSE`.

## Open for Contribution
Contributions welcome! Ways to help:
1. Open an issue (bug / enhancement)
2. Fork & create a feature branch
3. Keep PRs focused & include brief description

Suggested areas: OpenAPI docs, email notifications, React/Next frontend, reporting dashboard.

---
Aurora Library – Fast, Focused, Modern.
