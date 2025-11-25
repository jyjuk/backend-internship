# Backend Internship

FastAPI backend application for internship project.

## Prerequisites

- Python 3.11+
- pip
- Docker and Docker Compose

## Setup

1. Clone the repository:
```bash
git clone https://github.com/jyjuk/backend-internship.git
cd backend-internship
```

2. Create and activate virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.sample .env
```

Edit `.env` file with your configuration.

## Configuration

The application uses environment variables for configuration. Key settings include:

### Application Settings
- `APP_NAME`: Application name (default: BackendInternship)
- `DEBUG`: Debug mode (default: True)
- `ENVIRONMENT`: Environment type (default: development)

### Server Configuration
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### CORS Configuration
- `CORS_ORIGINS`: Allowed CORS origins (default: *)
  - Use `*` to allow all origins (development only)
  - Use comma-separated list for specific origins: `http://localhost:3000,https://example.com`
  - **Important**: In production, always specify exact origins instead of `*`

### Database Configuration
- `POSTGRES_USER`: PostgreSQL username (default: postgres)
- `POSTGRES_PASSWORD`: PostgreSQL password (default: postgres)
- `POSTGRES_HOST`: PostgreSQL host (default: postgres)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `POSTGRES_DB`: Database name (default: internship_db)
- `REDIS_HOST`: Redis host (default: redis)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_DB`: Redis database number (default: 0)

### JWT Configuration
- `JWT_SECRET_KEY`: Secret key for access tokens (use strong random key in production)
- `JWT_REFRESH_SECRET_KEY`: Secret key for refresh tokens (must be different from JWT_SECRET_KEY for enhanced security)
- `JWT_ALGORITHM`: JWT signing algorithm (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration time in minutes (default: 30)
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration time in days (default: 7)

### Auth0 Configuration (Optional)
- `AUTH0_DOMAIN`: Auth0 tenant domain
- `AUTH0_API_AUDIENCE`: Auth0 API identifier
- `AUTH0_ISSUER`: Auth0 token issuer URL
- `AUTH0_ALGORITHMS`: Auth0 token signing algorithm (default: RS256)

### Security
- `SECRET_KEY`: Secret key for security features (set in production)

Example `.env` file:
```env
APP_NAME=BackendInternship
DEBUG=True
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=internship_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=your-secret-key-here

# JWT Settings
JWT_SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-change-in-production-use-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Auth0 Settings (Optional)
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=https://your-api-audience
AUTH0_ISSUER=https://your-tenant.auth0.com/
AUTH0_ALGORITHMS=RS256
```

## Running the Application

### Using Docker Compose (Recommended):
```bash
# Start all services
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v
```

### Development mode (with auto-reload):
```bash
python app/main.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: http://localhost:8000

API documentation (Swagger UI): http://localhost:8000/docs

## Running with Docker

### Build Docker image:
```bash
docker build -t backend-internship .
```

### Run Docker container:
```bash
docker run -d -p 8000:8000 --name backend-app backend-internship
```

### Run with custom environment variables:
```bash
docker run -d -p 8000:8000 \
  -e CORS_ORIGINS="http://localhost:3000" \
  -e DEBUG=False \
  --name backend-app backend-internship
```

### Stop and remove container:
```bash
docker stop backend-app
docker rm backend-app
```

### View logs:
```bash
docker logs backend-app
```

### Access the application:
- API: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Development with Docker:
For development with auto-reload, mount your code as a volume:
```bash
docker run -d -p 8000:8000 -v $(pwd)/app:/app/app --name backend-app backend-internship
```

## Running Tests

Execute all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

Run specific test file:
```bash
pytest tests/test_health.py
```

Run tests with verbose output:
```bash
pytest -v
```

## API Endpoints

### Health Check

- **URL**: `/`
- **Method**: GET
- **Response**:
```json
{
  "status_code": 200,
  "detail": "ok",
  "result": "working"
}
```

## Project Structure
```
backend-internship/
├── app/
│   ├── api/
│   │   └── routes/                       # API routes
│   │       ├── health.py                 # Health check endpoint
│   │       ├── users.py                  # User CRUD endpoints
│   │       ├── auth.py                   # Authentication endpoints
│   │       ├── companies.py              # Company CRUD endpoints
│   │       ├── company_invitations.py    # Company invitation endpoints
│   │       ├── company_requests.py       # Company request endpoints
│   │       └── company_members.py        # Company member endpoints
│   ├── core/                             # Core functionality
│   │   ├── config.py                     # Configuration management
│   │   ├── database.py                   # PostgreSQL async connection
│   │   ├── redis.py                      # Redis async connection
│   │   ├── security.py                   # Password hashing and JWT utilities
│   │   ├── auth0.py                      # Auth0 token verification
│   │   ├── dependencies.py               # FastAPI dependencies (auth)
│   │   ├── middleware.py                 # Middleware setup (CORS, etc.)
│   │   └── logging_config.py             # Logging configuration
│   ├── models/                           # SQLAlchemy models
│   │   ├── base.py                       # Base mixins (UUID, Timestamp)
│   │   ├── user.py                       # User model
│   │   ├── company.py                    # Company model
│   │   ├── company_member.py             # Company membership model
│   │   ├── company_invitation.py         # Company invitation model
│   │   └── company_request.py            # Company request model
│   ├── repositories/                     # Data access layer
│   │   ├── base.py                       # Base repository with generic CRUD
│   │   ├── user.py                       # User repository
│   │   ├── company.py                    # Company repository
│   │   ├── company_member.py             # Company member repository
│   │   ├── company_invitation.py         # Company invitation repository
│   │   └── company_request.py            # Company request repository
│   ├── services/                         # Business logic layer
│   │   ├── user.py                       # User service
│   │   ├── auth.py                       # Authentication service
│   │   ├── company.py                    # Company service
│   │   ├── company_invitation_service.py # Company invitation service
│   │   ├── company_request_service.py    # Company request service
│   │   └── company_member_service.py     # Company member service
│   ├── schemas/                          # Pydantic schemas
│   │   ├── health.py                     # Health check schemas
│   │   ├── user.py                       # User schemas
│   │   ├── auth.py                       # Authentication schemas
│   │   ├── company.py                    # Company schemas
│   │   └── company_action.py             # Company action schemas
│   └── main.py                           # Application entry point
├── alembic/                              # Database migrations
│   ├── versions/                         # Migration files
│   └── env.py                            # Alembic configuration
├── tests/                                # Test files
├── logs/                                 # Application logs (excluded from git)
├── .env                                  # Environment variables (not in git)
├── .env.sample                           # Environment template
├── .dockerignore                         # Docker ignore rules
├── .gitignore                            # Git ignore rules
├── Dockerfile                            # Docker configuration
├── docker-compose.yml                    # Docker Compose configuration
├── alembic.ini                           # Alembic configuration
├── requirements.txt                      # Python dependencies
└── README.md
```

## Development Workflow

1. Ensure you're on `develop` branch: `git checkout develop`
2. Create new branch for each task: `git checkout -b BE-X-task-name`
3. Make changes and commit: `git add . && git commit -m "BE-X: Description"`
4. Push branch: `git push -u origin BE-X-task-name`
5. Create Pull Request to `develop` branch on GitHub
6. Request review from mentors
7. Wait for approval before merging

**Important**: Never merge to `main` branch during internship. All PRs go to `develop`.

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions and classes
- Keep functions small and focused

## Testing Guidelines

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Test both success and error cases

## Security Notes

- Never commit `.env` file to repository
- Always use strong `SECRET_KEY` in production
- Use different secret keys for access and refresh tokens
- Restrict `CORS_ORIGINS` to specific domains in production
- Keep dependencies updated

## Database Migrations

This project uses Alembic for database migrations.

### Creating a Migration

After making changes to models in `app/models/`, create a new migration:
```bash
# Inside Docker container
docker-compose exec app alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

Apply pending migrations to the database:
```bash
docker-compose exec app alembic upgrade head
```

### Rollback Migration

Rollback the last migration:
```bash
docker-compose exec app alembic downgrade -1
```

### View Migration History
```bash
docker-compose exec app alembic history
```

### Check Current Version
```bash
docker-compose exec app alembic current
```

## Models and Schemas

### Database Models

Models are defined in `app/models/` using SQLAlchemy ORM:
- `User` - User model with email, username, password, and timestamps

### Pydantic Schemas

Schemas for request/response validation in `app/schemas/user.py`:
- `SignUpRequest` - User registration
- `SignInRequest` - User login
- `UserUpdateRequest` - Update user information (admin)
- `UserSelfUpdateRequest` - Update own profile (username and password only)
- `User` - Simple user response
- `UserDetail` - Detailed user response with timestamps
- `UsersList` - List of users response

## Logging

The application uses Python's logging module configured in `app/core/logging_config.py`:
- Console output: INFO level
- File output: DEBUG level (`logs/app.log`)
- Separate loggers for uvicorn and SQLAlchemy

Logs are automatically created in the `logs/` directory (excluded from git).

## User CRUD Operations

### API Endpoints

The application provides RESTful API endpoints for user management:

#### Get All Users
```bash
GET /users/?skip=0&limit=100
Authorization: Bearer <your_token>
```
Returns paginated list of users.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100, max: 100)

#### Get User by ID
```bash
GET /users/{user_id}
Authorization: Bearer <your_token>
```
Returns detailed information about a specific user.

#### Create User
```bash
POST /users/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```
Creates a new user with hashed password.

#### Update User (Admin)
```bash
PUT /users/{user_id}
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "username": "newusername",
  "password": "newpassword",
  "is_active": true
}
```
Updates user information. All fields are optional. Requires authentication.

#### Delete User (Admin)
```bash
DELETE /users/{user_id}
Authorization: Bearer <your_token>
```
Deletes a user from the database. Requires authentication.

### Self-Management Endpoints

Users can manage their own profiles through dedicated `/users/me` endpoints:

#### Get Own Profile
```bash
GET /users/me
Authorization: Bearer <your_token>
```
Returns current user's profile information.

#### Update Own Profile
```bash
PUT /users/me
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "username": "newusername",
  "password": "newpassword123"
}
```
Updates current user's username and/or password. Both fields are optional.

**Restrictions:**
- Users can only update their own username and password
- Email and is_active fields cannot be modified via this endpoint
- Returns 403 Forbidden if attempting to modify another user's profile

#### Delete Own Profile
```bash
DELETE /users/me
Authorization: Bearer <your_token>
```
Deletes current user's account.

**Restrictions:**
- Users can only delete their own profile
- Returns 403 Forbidden if attempting to delete another user's profile

## Company CRUD Operations

### API Endpoints

The application provides CRUD operations for managing companies with owner-based permissions.

#### Create Company
```bash
POST /companies/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "My Company",
  "description": "Company description"
}
```
Creates a new company. Any authenticated user can create a company and automatically becomes the owner.

#### Get All Companies
```bash
GET /companies/?skip=0&limit=100
```
Returns paginated list of visible companies (no authentication required).

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100, max: 100)

#### Get Company by ID
```bash
GET /companies/{company_id}
```
Returns detailed information about a specific company.

#### Update Company
```bash
PUT /companies/{company_id}
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "Updated Company Name",
  "description": "Updated description",
  "is_visible": false
}
```
Updates company information. All fields are optional.

**Restrictions:**
- Only the company owner can update the company
- Returns 403 Forbidden if a non-owner attempts to update

#### Delete Company
```bash
DELETE /companies/{company_id}
Authorization: Bearer <your_token>
```
Deletes a company.

**Restrictions:**
- Only the company owner can delete the company
- Returns 403 Forbidden if a non-owner attempts to delete

### Company Visibility

Companies have a `is_visible` field that controls their visibility:
- `true` (default): Company appears in public listings
- `false`: Company is hidden from public listings

### Architecture

**Company Features:**
- Multiple companies per user (one-to-many relationship)
- Owner-based permissions (only owner can edit/delete)
- Visibility control (public or hidden)
- Automatic timestamps (created_at, updated_at)
- Cascade delete (when user is deleted, their companies are also deleted)

**Database Schema:**
- `id` (UUID, Primary Key)
- `name` (String, required, indexed)
- `description` (Text, optional)
- `is_visible` (Boolean, default: true)
- `owner_id` (UUID, Foreign Key to users)
- `created_at`, `updated_at` (Timestamps)

### Company Actions Models

**company_members** - User memberships in companies (many-to-many)
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to users)
- `company_id` (UUID, Foreign Key to companies)
- Unique constraint on (user_id, company_id)
- `created_at`, `updated_at` (Timestamps)

**company_invitations** - Owner invitations to users
- `id` (UUID, Primary Key)
- `company_id` (UUID, Foreign Key to companies)
- `invited_user_id` (UUID, Foreign Key to users)
- `invited_by_id` (UUID, Foreign Key to users)
- `status` (String: pending, accepted, declined, cancelled)
- `created_at`, `updated_at` (Timestamps)

**company_requests** - User requests to join companies
- `id` (UUID, Primary Key)
- `company_id` (UUID, Foreign Key to companies)
- `user_id` (UUID, Foreign Key to users)
- `status` (String: pending, accepted, declined, cancelled)
- `created_at`, `updated_at` (Timestamps)

### Company Actions

The application provides comprehensive invitation, request, and membership management for companies.

#### Invitations (Owner)

**Create Invitation**
```bash
POST /companies/{company_id}/invitations
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "invited_user_id": "uuid-of-user-to-invite"
}
```
Owner invites a user to join the company. Returns invitation details.

**Cancel Invitation**
```bash
DELETE /companies/{company_id}/invitations/{invitation_id}
Authorization: Bearer <your_token>
```
Owner cancels a pending invitation.

**List Company Invitations**
```bash
GET /companies/{company_id}/invitations?skip=0&limit=100
Authorization: Bearer <your_token>
```
Owner views all invitations sent for the company.

#### Invitations (User)

**Get My Invitations**
```bash
GET /companies/invitations/me?skip=0&limit=100
Authorization: Bearer <your_token>
```
User views invitations they have received.

**Accept Invitation**
```bash
POST /companies/invitations/{invitation_id}/accept
Authorization: Bearer <your_token>
```
User accepts an invitation and becomes a company member.

**Decline Invitation**
```bash
POST /companies/invitations/{invitation_id}/decline
Authorization: Bearer <your_token>
```
User declines an invitation.

#### Requests (User)

**Request to Join**
```bash
POST /companies/{company_id}/requests
Authorization: Bearer <your_token>
```
User requests to join a company. Returns request details.

**Cancel Request**
```bash
DELETE /companies/{company_id}/requests/{request_id}
Authorization: Bearer <your_token>
```
User cancels their pending request.

**Get My Requests**
```bash
GET /companies/requests/me?skip=0&limit=100
Authorization: Bearer <your_token>
```
User views their membership requests.

#### Requests (Owner)

**List Company Requests**
```bash
GET /companies/{company_id}/requests?skip=0&limit=100
Authorization: Bearer <your_token>
```
Owner views pending membership requests for the company.

**Accept Request**
```bash
POST /companies/{company_id}/requests/{request_id}/accept
Authorization: Bearer <your_token>
```
Owner accepts a request and the user becomes a company member.

**Decline Request**
```bash
POST /companies/{company_id}/requests/{request_id}/decline
Authorization: Bearer <your_token>
```
Owner declines a membership request.

#### Members

**List Company Members**
```bash
GET /companies/{company_id}/members?skip=0&limit=100
```
Public endpoint - anyone can view company members.

**Remove Member**
```bash
DELETE /companies/{company_id}/members/{user_id}
Authorization: Bearer <your_token>
```
Owner removes a member from the company.

**Leave Company**
```bash
DELETE /companies/{company_id}/members/me
Authorization: Bearer <your_token>
```
User leaves a company they are a member of.

#### Invitation & Request Statuses

Both invitations and requests have the following statuses:
- `pending` - Awaiting response
- `accepted` - Accepted (user becomes member)
- `declined` - Declined/Rejected
- `cancelled` - Cancelled by sender

#### Business Rules

- Users cannot be invited if already a member
- Users cannot request to join if already a member
- Only one pending invitation per user per company
- Only one pending request per user per company
- Only company owners can manage invitations and requests
- Accepting invitation/request automatically creates membership
- Members list is publicly visible


### Testing with Swagger UI

Access interactive API documentation at http://localhost:8000/docs to test all endpoints.

### Architecture

The application follows a layered architecture:

**Repository Layer** (`app/repositories/`):
- Handles database operations
- Provides data access abstraction
- `UserRepository`: CRUD operations for User model

**Service Layer** (`app/services/`):
- Contains business logic
- Handles validation and error handling
- Implements password hashing
- `UserService`: User management business logic with ownership validation

**API Layer** (`app/api/routes/`):
- Defines HTTP endpoints
- Request/response handling
- Dependency injection

### Security

- Passwords are hashed using bcrypt before storage
- Password validation (minimum 8 characters)
- Email and username uniqueness validation
- Users can only modify their own profiles through `/users/me` endpoints
- Comprehensive error handling and logging

## Authentication & Authorization

The application supports two authentication methods with JWT refresh tokens.

### 1. JWT Authentication (Login/Password)

Traditional authentication using email and password with JWT tokens (access + refresh).

#### Login Endpoint
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Types:**
- **Access Token**: Short-lived (30 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to get new access tokens

#### Refresh Access Token
```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "<your_refresh_token>"
}
```

**Response:**
```json
{
  "access_token": "<new_access_token>",
  "refresh_token": "<new_refresh_token>",
  "token_type": "bearer"
}
```

#### Get Current User (Unified Endpoint)
```bash
GET /auth/me
Authorization: Bearer <your_jwt_token_or_auth0_token>
```

**Response:** User details with email, username, timestamps

**Features:**
- Single endpoint supports both JWT and Auth0 tokens
- Tries Auth0 validation first, falls back to JWT
- Automatically creates user from Auth0 email if doesn't exist

### 2. Auth0 Integration

OAuth 2.0 authentication using Auth0 with automatic user provisioning.

#### Configuration

Set up Auth0 credentials in `.env`:
```env
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=https://your-api-audience
AUTH0_ISSUER=https://your-tenant.auth0.com/
AUTH0_ALGORITHMS=RS256
```

#### Get Token

1. Create Auth0 account at https://manage.auth0.com/dashboard
2. Create API with your audience identifier
3. Create Single Page Application
4. Configure Post-Login Action to add email claim to token
5. Get token from https://romanxeo.github.io/internship-token/ using:
   - Domain: your Auth0 domain
   - Client ID: from your SPA application
   - Audience: your API identifier

**Features:**
- Automatic user creation from Auth0 email
- Username extracted from email or Auth0 nickname
- Random secure password generated for Auth0 users
- Email claim added to access token via Auth0 Action

### Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: HS256 algorithm with configurable expiration
- **Refresh Tokens**: Long-lived tokens for obtaining new access tokens (7 days, configurable via `JWT_REFRESH_TOKEN_EXPIRE_DAYS`)
- **Separate Refresh Key**: Refresh tokens use different secret key (`JWT_REFRESH_SECRET_KEY`) for enhanced security
- **Auth0 Tokens**: RS256 algorithm with JWKS verification
- **Token Expiration**: Access tokens expire in 30 minutes (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Protected Endpoints**: Require valid Bearer token
- **User Validation**: Email and username uniqueness checks
- **Inactive User Check**: Prevents inactive users from accessing resources
- **Profile Ownership**: Users can only modify/delete their own profiles via `/users/me` endpoints

### Testing Authentication

Access Swagger UI at http://localhost:8000/docs:

1. **Test JWT Login:**
   - POST /auth/login with email/password
   - Copy **both** access_token and refresh_token
   - Click "Authorize" button
   - Paste access token
   - Try GET /auth/me

2. **Test Token Refresh:**
   - POST /auth/refresh with refresh_token
   - Receive new access and refresh tokens
   - Old tokens are still valid until expiration

3. **Test Auth0:**
   - Get Auth0 token from token generator
   - Click "Authorize" button  
   - Paste Auth0 token
   - Try GET /auth/me (same endpoint!)
   - User will be created automatically if doesn't exist
   - System automatically detects token type (Auth0 or JWT)

4. **Test Profile Self-Management:**
   - Login and get your access token
   - Click "Authorize" button
   - Try GET /users/me (view your profile)
   - Try PUT /users/me (update your username/password)
   - Try DELETE /users/me (delete your account)

## Authors

- [@jyjuk]

## Mentors

- tkach-v
- FUZIR
- Ilia-puzdranovskuy