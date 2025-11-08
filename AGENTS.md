# Repository Guidelines

## Project Structure & Module Organization
- `api/index.py` — Flask API that detects, extracts, inverts, and converts QR codes.
- `public/` — Static web UI served by Flask (`/`).
- `launcher.py` — Local entry point; starts Flask and opens the browser.
- `requirements.txt` — Runtime dependencies (OpenCV headless, pyzbar, Pillow, qrcode, Flask).
- `image/` — Sample assets for local testing.

## Build, Test, and Development Commands
- Setup (venv recommended):
  - `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
  - `pip install -r requirements.txt`
- Run locally: `python launcher.py` (serves at `http://127.0.0.1:53123`).
- Dev server (alternative): `FLASK_ENV=development flask --app api/index.py run --debug`.
- Quick API check:
  - `curl -X POST -F "files=@image/c7d18a0541d72fcc2c575634821dee1f_qr.png" -F "options={\"activeSteps\":[\"extract\",\"svg\"]}" http://127.0.0.1:5000/api/process`
- Docker (recommended for production):
  - Build: `docker build -t qr-processor .`
  - Run: `docker run -d -p 53123:53123 qr-processor`
  - Compose: `docker compose up -d` (serves at `http://<host>:53123`)

## Coding Style & Naming Conventions
- Python: PEP 8, 4‑space indent, `snake_case` for files/functions, `CapWords` for classes.
- Keep modules focused; avoid global state. Add docstrings and type hints where practical.
- Frontend: semantic HTML, utility CSS with `kebab-case` classes. Keep inline scripts minimal.
- If adding tooling, prefer `black` (format) and `ruff`/`flake8` (lint). Do not reformat unrelated files.

## Testing Guidelines
- No formal test suite yet. Use manual checks via the UI and the cURL example above.
- If adding tests, use `pytest`, place under `tests/`, and name files `test_*.py`. Aim for essential coverage of QR detection paths (normal, inverted, no‑QR).

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat`, `fix`, `refactor`, `docs`, `chore` (scopes welcome, e.g., `feat(qr处理): …`).
- PRs must include: clear description, linked issues, local run steps, and screenshots/GIFs for UI changes.
- Keep diffs focused; include before/after behavior and any config changes (env vars, ports).

## Security & Configuration Tips
- Upload limits: 50MB (`MAX_CONTENT_LENGTH`). Allowed types set in `api/index.py`.
- Common env vars: `FLASK_ENV`, `HOST`, `PORT`. Avoid committing secrets.
