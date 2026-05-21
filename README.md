# AppRating

This is a Django application. GitHub Pages cannot host Django apps because GitHub Pages only serves static HTML/CSS/JavaScript files.

## Important

- GitHub Pages is not a valid deployment target for this project.
- Use a Python-compatible host such as Render, Heroku, Railway, or PythonAnywhere.

## Deployment steps

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Collect static files:
   ```bash
   python manage.py collectstatic
   ```
4. Start the server locally:
   ```bash
   gunicorn AppRating.wsgi:application
   ```

## Notes

- `Procfile` is configured for production with Gunicorn.
- `whitenoise` is configured for static file serving in production.
- If you still want a live demo, deploy to a Django-capable service rather than GitHub Pages.
