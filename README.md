# AppRating

This repository is a Django application for app rating prediction.

## Important notes

- This project is not deployable on GitHub Pages because GitHub Pages only serves static sites.
- To run the app, use a Python-compatible host such as Render, Heroku, Railway, or PythonAnywhere.
- The root `index.html` is a placeholder so GitHub Pages will not show a 404.

## Fixes applied

- Added `.gitignore` rules to ignore generated model artifacts in `media/*.pkl` and `media/*.joblib`.
- Removed the tracked model artifact files from Git so they are no longer pushed as large binaries.

## Local setup

1. Create and activate a Python virtual environment.
2. Install requirements from `requirements.txt`.
3. Run `python manage.py migrate`.
4. Run `python manage.py runserver`.
