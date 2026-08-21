# Payment Backend API

A Django REST Framework-based payment backend.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## API Endpoints

| Method | Endpoint              | Description          |
|--------|-----------------------|----------------------|
| GET    | `/api/`               | API root             |
| GET    | `/api/health/`        | Health check         |
| GET    | `/api/transactions/`  | List transactions    |
| POST   | `/api/transactions/`  | Create transaction   |
| GET    | `/api/transactions/`  | Retrieve transaction |
| PUT    | `/api/transactions/`  | Update transaction   |
| DELETE | `/api/transactions/`  | Delete transaction   |
| POST   | `/api/auth/token/`    | Obtain JWT token     |
| POST   | `/api/auth/token/refresh/` | Refresh JWT token |
