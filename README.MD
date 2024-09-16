# Zid App Development

## Overview

This project is a Django-based application developed for OAuth 2.0 integration using Zid's authorization guide. The application is structured for easy management and testing.

![Description](https://i.ibb.co/ssVGGBN/Screenshot-from-2024-09-16-22-43-27.png)

## Project Structure

- `.gitignore`: Specifies which files to ignore in version control.
- `LICENSE`: License information for the project.
- `manage.py`: Entry point for Django project management commands.
- `requirements.txt`: Lists all the Python dependencies required for the project.
- `db.sqlite3`: SQLite database file containing the application's data.
- `app/`: Contains the Django app with models, views, and configurations.

## Requirements

- Python 3.x
- Django 3.x
- SQLite (or any other supported DBMS)
- Zid OAuth 2.0 credentials for integration

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd zid_app_development-main
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\\Scripts\\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Technical Documentation

### OAuth 2.0 Integration

This application implements Zid's OAuth 2.0 for user authentication. Follow Zid's [OAuth 2.0 guide](https://docs.zid.com/oauth2) to set up your client ID and secret, and update the configuration in the app's settings.

### Database

The default database is SQLite. To switch to PostgreSQL, update the `DATABASES` configuration in `settings.py` and install the required drivers.

### Testing

Unit tests are included in the `app/tests.py` file. To run the tests:

```bash
python manage.py test
```
