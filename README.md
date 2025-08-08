# FastAPI User & Role Testing Application

A FastAPI application for testing IGA (Identity Governance and Administration) connectors with user and role CRUD operations, HTMX-powered UI, and bearer token authentication.

## Features

- User management (CRUD operations) with status tracking (Active, Disabled, Terminated)
- Role management with user assignments
- Bearer token authentication for API
- HTMX-powered reactive UI with Alpine.js for interactivity
- API activity tracking per token
- SQLite database with SQLAlchemy ORM
- Password hashing with bcrypt
- Auto-generated passwords for new users
- OpenAPI documentation for easy integration

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Git (optional, for cloning)

### Option 1: Using the Start Script (Recommended)

**macOS/Linux:**
```bash
./start-app.sh
```

**Windows:**
```cmd
start-app.bat
```

**Cross-platform (Python):**
```bash
python start-app.py
```

The start script will:
- Create a virtual environment if needed
- Install dependencies automatically
- Start the application with auto-reload enabled

### Option 2: Manual Setup

1. Create virtual environment:
```bash
python -m venv .venv
```

2. Activate virtual environment:
```bash
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

### Access the Application

- **UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

The SQLite database (`app.db`) is automatically created on first run.

## API Endpoints

### Users
- `GET /api/v1/users` - List all users
- `POST /api/v1/users` - Create new user
- `GET /api/v1/users/{id}` - Get user details with role IDs
- `PATCH /api/v1/users/{id}` - Update user (including status)
- `DELETE /api/v1/users/{id}` - Delete user

### Roles
- `GET /api/v1/roles` - List all roles
- `GET /api/v1/roles/{id}` - Get role details with user IDs
- `GET /api/v1/roles/{id}/users` - Get full user objects assigned to a role

### Role Assignments
- `POST /api/v1/users/{user_id}/roles/{role_id}` - Assign role to user
- `DELETE /api/v1/users/{user_id}/roles/{role_id}` - Remove role from user

### Health Check
- `GET /health` - Application health check

## Authentication

All API calls require a bearer token in the Authorization header:
```
Authorization: Bearer <your-token-here>
```

Generate tokens through the UI's Token Management section.

## API Examples

### Create a User

```bash
# With auto-generated password
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com"
  }'

# With specific password (min 6 chars)
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "password": "mySecurePass123"
  }'
```

Response (with auto-generated password):
```json
{
  "id": "2J9mNpQ3r5s7tUvWxYz1234567890",
  "username": "jsmith",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "display_name": "Jane Smith",
  "status": "active",
  "generated_password": "Xy#9kL$mN2pQ"
}
```

**Note**: The `generated_password` field is only returned when a password is auto-generated.

### Update User Status

```bash
curl -X PATCH http://localhost:8000/api/v1/users/{id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "disabled"
  }'
```

### Assign Role to User

```bash
# Assign a role to a user
curl -X POST http://localhost:8000/api/v1/users/{user_id}/roles/{role_id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Remove a role from a user
curl -X DELETE http://localhost:8000/api/v1/users/{user_id}/roles/{role_id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get User with Roles

```bash
curl -X GET http://localhost:8000/api/v1/users/{id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
{
  "id": "abc123",
  "username": "jsmith",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "display_name": "Jane Smith",
  "status": "active",
  "role_ids": ["role123", "role456"]
}
```

### Get Users in a Role

```bash
curl -X GET http://localhost:8000/api/v1/roles/{role_id}/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Response:
```json
[
  {
    "id": "user123",
    "username": "jdoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "display_name": "John Doe",
    "status": "active"
  },
  {
    "id": "user456",
    "username": "jsmith",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "display_name": "Jane Smith",
    "status": "active"
  }
]
```

## Baton Connector Integration

This application is designed to work with [baton-http](https://github.com/ConductorOne/baton-http) connectors. The API returns resource IDs instead of full objects in relationship fields to facilitate efficient resource graph building.

Key integration points:
- `UserWithRoles` returns `role_ids` array
- `RoleWithUsers` returns `user_ids` array
- All IDs are stable SHA-1 hashes
- User status field supports: active, disabled, terminated

## Development

### Running Tests
```bash
python -m pytest
```

### Linting and Type Checking
```bash
python -m ruff check .
python -m mypy .
```

### Format Code
```bash
python -m ruff format .
```

### Generate OpenAPI Schema
```bash
.venv/bin/python generate_openapi.py
```

## Common Workflows

### Bulk User Import
```bash
TOKEN="YOUR_TOKEN_FROM_UI_HERE"

for user in "john:doe:john@example.com" "jane:smith:jane@example.com"; do
  IFS=':' read -r first last email <<< "$user"
  curl -X POST http://localhost:8000/api/v1/users \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"first_name\": \"$first\", \"last_name\": \"$last\", \"email\": \"$email\"}"
done
```

### Python Integration Example
```python
import requests

token = "YOUR_TOKEN_FROM_UI_HERE"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Create user
user_data = {
    "first_name": "Alice",
    "last_name": "Williams",
    "email": "alice@example.com"
}
response = requests.post(
    "http://localhost:8000/api/v1/users",
    headers=headers,
    json=user_data
)
user = response.json()

# Get existing role
response = requests.get(
    "http://localhost:8000/api/v1/roles",
    headers=headers
)
roles = response.json()
developer_role = next((r for r in roles if r["role_name"] == "Developer"), None)

if developer_role:
    # Assign role to user
    response = requests.post(
        f"http://localhost:8000/api/v1/users/{user['id']}/roles/{developer_role['id']}",
        headers=headers
    )
    print(f"Assigned {developer_role['role_name']} role to {user['display_name']}")
```

## Troubleshooting

### Port Already in Use
```bash
uvicorn app.main:app --reload --port 8001
```

### Database Reset
```bash
# Stop the server first (CTRL+C)
rm app.db
# Restart - creates fresh database
uvicorn app.main:app --reload
```

### Module Import Errors
Ensure virtual environment is activated:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### API Returns 401 Unauthorized
- Verify Authorization header is included
- Check token hasn't been deleted
- Generate new token if needed

## Security Notes

1. **Tokens**: Store API tokens securely. Anyone with a token can access the API.
2. **Passwords**: 
   - Auto-generated passwords are 12 characters with letters, numbers, and symbols
   - Passwords are hashed with bcrypt before storage
   - Generated passwords are only shown once at creation
3. **Local Testing**: This application is designed for local testing. Do not expose to the internet without proper security measures.
4. **No Token Expiration**: Tokens don't expire automatically. Delete them manually when no longer needed.
5. **API Activity**: All API calls are logged and viewable in the UI.

## License

This project is licensed under the MIT License.