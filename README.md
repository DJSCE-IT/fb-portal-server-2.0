# Flask API Server

## Everything in this repo is for demo right now
## The development is going on and the Apis would be up and ready soon!

A modern Flask API server with authentication, user management, and proper project structure.

## Features

- User authentication with JWT
- User registration and login
- Profile management
- Protected routes
- SQLAlchemy ORM
- Database migrations
- CORS support
- Environment variables configuration

## Project Structure

```
api/
├── config/
│   └── config.py         # Configuration settings
├── models/
│   └── user.py          # Database models
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── users.py         # User management routes
│   └── main.py          # Main application routes
├── schemas/             # Data serialization schemas
├── services/           # Business logic
└── utils/              # Utility functions
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///app.db
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the server:
```bash
python -m api.main
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
  ```json
  {
    "username": "example",
    "email": "user@example.com",
    "password": "secure_password"
  }
  ```

- `POST /auth/login` - Login user
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password"
  }
  ```

### User Management

- `GET /users/profile` - Get user profile (requires authentication)
- `PUT /users/profile` - Update user profile (requires authentication)
- `DELETE /users/profile` - Delete user account (requires authentication)

### Main Routes

- `GET /` - Welcome message and API status
- `GET /protected` - Example protected route (requires authentication)

## Authentication

To access protected routes, include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Development

To run the server in development mode:
```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
export FLASK_APP=api.main
flask run
```

## Testing

Run tests using pytest:
```bash
pytest
```