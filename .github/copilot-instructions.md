# Copilot Instructions for AI Agents

## Project Overview
This project is a Flask web application for managing students ("stagiaires"), promotions, filières, and absences. It uses MySQL as the database backend and SQLAlchemy as the ORM. The main application logic is in `venv/app.py`.

## Key Components
- **Models**: Defined in `venv/app.py` (`Filiere`, `Promotion`, `Stagiaire`, `Absence`).
- **Templates**: HTML files in `venv/templates/` (e.g., `home.html`, `addStagiaire.html`).
- **Static Assets**: CSS and images in `venv/static/`.
- **Database**: MySQL, configured via `SQLALCHEMY_DATABASE_URI` in `app.py`.
- **Requirements**: See `requirements.txt` for dependencies.

## Developer Workflows
- **Run the app locally**: `python venv/app.py` (ensure MySQL is running and accessible).
- **Database migrations**: Not automated; models are defined directly in code. Manual schema updates may be required.
- **Debug mode**: Enabled by default (`app.run(debug=True)`).
- **Testing**: No explicit test suite present.

## Project-Specific Patterns
- **Validation**: Input validation is performed in route handlers (e.g., CINE format, RIB uniqueness).
- **Templates**: Data is passed to templates using Flask's `render_template`.
- **API Endpoints**: JSON APIs for promotions and stagiaires (e.g., `/api/promotions/<id_filiere>`, `/api/stagiaires`).
- **Separation**: All logic (models, routes, validation) is in a single file (`app.py`).

## Integration Points
- **MySQL**: Credentials and DB name are hardcoded in `app.py`. Update as needed for deployment.
- **Flask-SQLAlchemy**: Used for ORM and DB session management.
- **Templates/Static**: Flask's default folder structure is used (`templates/`, `static/`).

## Conventions
- **Unique constraints**: Enforced in models for fields like `RIB`, `Telephone`, `Email`, and `Prenom`.
- **Error handling**: Returns error messages or re-renders forms with error context.
- **No blueprints**: All routes are defined directly on the main `app` object.

## Example: Adding a Stagiaire
- POST to `/addStagiaire` with required fields.
- Validates CINE, RIB, telephone, and email for uniqueness and format.
- On success, commits to DB and redirects to `/stagiaires`.

---

**For AI agents:**
- Keep all new models, routes, and templates consistent with the patterns in `app.py` and `venv/templates/`.
- Document any new developer workflows or conventions in this file.
- If adding tests, create a new `tests/` directory and document usage here.
