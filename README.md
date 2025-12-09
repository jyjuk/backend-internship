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
│   │       ├── company_members.py        # Company member endpoints
│   │       ├── quizzes.py                # Quiz and quiz attempt endpoints
│   │       ├── exports.py                # Data export endpoints
│   │       ├── analytics.py              # Analytics endpoints
│   │       ├── notifications.py          # Notification endpoints
│   │       └── ws.py                     # WebSocket endpoints  
│   ├── core/                             # Core functionality
│   │   ├── config.py                     # Configuration management
│   │   ├── database.py                   # PostgreSQL async connection
│   │   ├── redis.py                      # Redis async connection
│   │   ├── security.py                   # Password hashing and JWT utilities
│   │   ├── auth0.py                      # Auth0 token verification
│   │   ├── dependencies.py               # FastAPI dependencies (auth)
│   │   ├── middleware.py                 # Middleware setup (CORS, etc.)
│   │   ├── logging_config.py             # Logging configuration
│   │   └── websocket.py                  # WebSocket connection manager
│   ├── models/                           # SQLAlchemy models
│   │   ├── base.py                       # Base mixins (UUID, Timestamp)
│   │   ├── user.py                       # User model
│   │   ├── company.py                    # Company model
│   │   ├── company_member.py             # Company membership model
│   │   ├── company_invitation.py         # Company invitation model
│   │   ├── company_request.py            # Company request model
│   │   ├── quiz.py                       # Quiz model
│   │   ├── question.py                   # Question model
│   │   ├── answer.py                     # Answer model
│   │   ├── quiz_attempt.py               # Quiz attempt model
│   │   └── notification.py               # Notification model
│   ├── repositories/                     # Data access layer
│   │   ├── base.py                       # Base repository with generic CRUD
│   │   ├── user.py                       # User repository
│   │   ├── company.py                    # Company repository
│   │   ├── company_member.py             # Company member repository
│   │   ├── company_invitation.py         # Company invitation repository
│   │   ├── company_request.py            # Company request repository
│   │   ├── quiz.py                       # Quiz repository
│   │   ├── question.py                   # Question repository
│   │   ├── answer.py                     # Answer repository
│   │   ├── quiz_attempt.py               # Quiz attempt repository
│   │   └── notification.py               # Notification repository
│   ├── services/                         # Business logic layer
│   │   ├── user.py                       # User service
│   │   ├── auth.py                       # Authentication service
│   │   ├── company.py                    # Company service
│   │   ├── company_invitation_service.py # Company invitation service
│   │   ├── company_request_service.py    # Company request service
│   │   ├── company_member_service.py     # Company member service
│   │   ├── quiz_service.py               # Quiz service
│   │   ├── quiz_attempt_service.py       # Quiz attempt service
│   │   ├── redis_service.py              # Redis service for temporary storage
│   │   ├── export_service.py             # Export service for JSON/CSV formats
│   │   ├── analytics_service.py          # Analytics service for statistics
│   │   └── notification_service.py       # Notification service
│   ├── schemas/                          # Pydantic schemas
│   │   ├── health.py                     # Health check schemas
│   │   ├── user.py                       # User schemas
│   │   ├── auth.py                       # Authentication schemas
│   │   ├── company.py                    # Company schemas
│   │   ├── company_action.py             # Company action schemas
│   │   ├── quiz.py                       # Quiz schemas
│   │   ├── analytics.py                  # Analytics schemas
│   │   └── notification.py               # Notification schemas
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
- `is_admin` (Boolean, default: false)
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

#### Admin Management

**Get Company Admins**

```bash
GET /companies/{company_id}/admins?skip=0&limit=100
```

Public endpoint - anyone can view company admins.

**Promote Member to Admin**

```bash
POST /companies/{company_id}/members/{user_id}/promote
Authorization: Bearer <your_token>
```

Owner promotes a member to admin role.

**Demote Admin to Member**

```bash
POST /companies/{company_id}/members/{user_id}/demote
Authorization: Bearer <your_token>
```

Owner demotes an admin back to regular member.

**Business Rules:**

- Only company owner can promote/demote admins
- Cannot promote user who is already an admin
- Cannot demote user who is not an admin
- Admin status is stored in `company_members` table with `is_admin` boolean field

### Quiz System

The application provides a comprehensive quiz system for companies where owners and admins can create, manage quizzes
with questions and answers.

#### Quiz Models

**quizzes** - Company quizzes

- `id` (UUID, Primary Key)
- `company_id` (UUID, Foreign Key to companies)
- `title` (String, max 255, required)
- `description` (Text, optional)
- `frequency` (Integer, default: 0) - Total participation count
- `created_at`, `updated_at` (Timestamps)

**questions** - Quiz questions

- `id` (UUID, Primary Key)
- `quiz_id` (UUID, Foreign Key to quizzes, cascade delete)
- `title` (Text, required)
- `order` (Integer, required) - Question order in quiz
- `created_at`, `updated_at` (Timestamps)

**answers** - Question answer options

- `id` (UUID, Primary Key)
- `question_id` (UUID, Foreign Key to questions, cascade delete)
- `text` (Text, required)
- `is_correct` (Boolean, required) - Multiple answers can be correct
- `order` (Integer, required) - Answer order in question
- `created_at`, `updated_at` (Timestamps)

#### Quiz Endpoints

**Create Quiz**

```bash
POST /companies/{company_id}/quizzes
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "title": "Python Quiz",
  "description": "Test your Python knowledge",
  "questions": [
    {
      "title": "What is Python?",
      "order": 0,
      "answers": [
        {"text": "A programming language", "is_correct": true, "order": 0},
        {"text": "A snake", "is_correct": false, "order": 1}
      ]
    },
    {
      "title": "Is Python dynamically typed?",
      "order": 1,
      "answers": [
        {"text": "Yes", "is_correct": true, "order": 0},
        {"text": "No", "is_correct": false, "order": 1}
      ]
    }
  ]
}
```

Owner or admin creates a quiz with nested questions and answers.

**Get All Quizzes**

```bash
GET /companies/{company_id}/quizzes?skip=0&limit=100
```

Public endpoint - anyone can view company quizzes with all questions and answers.

**Get Quiz Details**

```bash
GET /companies/{company_id}/quizzes/{quiz_id}
```

Public endpoint - get specific quiz with all questions and answers.

**Update Quiz**

```bash
PUT /companies/{company_id}/quizzes/{quiz_id}
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "title": "Updated Python Quiz",
  "questions": [...]
}
```

Owner or admin updates quiz. All fields optional. Questions update replaces all existing questions.

**Delete Quiz**

```bash
DELETE /companies/{company_id}/quizzes/{quiz_id}
Authorization: Bearer <your_token>
```

Owner or admin deletes quiz (cascade deletes questions and answers).

#### Quiz Business Rules

- Only company owner or admin can create/update/delete quizzes
- Each quiz must have minimum 2 questions
- Each question must have 2-4 answer options
- At least one answer per question must be correct
- Multiple correct answers are supported
- Questions and answers have `order` field for consistent display
- Quiz listing and details are publicly accessible
- Frequency tracks total participation (future feature)

### Quiz Workflow

Users can take quizzes, submit answers, and view their performance statistics.

#### Quiz Attempt Endpoints

**Submit Quiz**

```bash
POST /companies/{company_id}/quizzes/{quiz_id}/attempts
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "answers": [
    {
      "question_id": "uuid-of-question-1",
      "answer_ids": ["uuid-of-answer-1"]
    },
    {
      "question_id": "uuid-of-question-2",
      "answer_ids": ["uuid-of-answer-2", "uuid-of-answer-3"]
    }
  ]
}
```

Submit quiz answers and get immediate results with score and percentage.

**Response:**

```json
{
  "id": "attempt-uuid",
  "user_id": "user-uuid",
  "quiz_id": "quiz-uuid",
  "company_id": "company-uuid",
  "score": 8,
  "total_questions": 10,
  "correct_answers": 8,
  "percentage": 80.0,
  "completed_at": "2024-01-15T10:30:00Z"
}
```

**Get My Company Stats**

```bash
GET /companies/{company_id}/my-stats
Authorization: Bearer <your_token>
```

Get your quiz statistics within a specific company.

**Response:**

```json
{
  "company_id": "company-uuid",
  "company_name": "Tech Company",
  "stats": {
    "total_attempts": 15,
    "total_questions_answered": 150,
    "total_correct_answers": 120,
    "average_score": 80.0,
    "last_attempt_at": "2024-01-15T10:30:00Z"
  }
}
```

**Get My System Stats**

```bash
GET /users/me/quiz-stats
Authorization: Bearer <your_token>
```

Get your quiz statistics across all companies.

**Response:**

```json
{
  "stats": {
    "total_attempts": 45,
    "total_questions_answered": 450,
    "total_correct_answers": 360,
    "average_score": 80.0,
    "last_attempt_at": "2024-01-15T10:30:00Z"
  },
  "companies_participated": 3
}
```

#### Quiz Workflow Business Rules

- Users must answer ALL questions to submit quiz
- Multiple answer selection is supported (for questions with multiple correct answers)
- Answer correctness requires EXACT match of all correct answer IDs
- Score calculation: correct_answers / total_questions
- Average score: total_correct_answers / total_questions_answered (across all attempts)
- Quiz frequency counter increments on each submission
- Last attempt time tracked per user
- Statistics calculated separately for company and system-wide

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

### Redis Workflow

Quiz responses are temporarily stored in Redis for 48 hours, providing quick access to recent answer history.

#### Redis Storage Details

**Key Structure:**

```
quiz_response:{user_id}:{quiz_id}:{question_id}
```

**Stored Data:**

```json
{
  "user_id": "uuid",
  "company_id": "uuid",
  "quiz_id": "uuid",
  "question_id": "uuid",
  "answer_ids": [
    "uuid1",
    "uuid2"
  ],
  "is_correct": true,
  "answered_at": "2024-01-15T10:30:00Z"
}
```

**TTL (Time To Live):** 48 hours (172,800 seconds) - automatically deleted after expiration

#### Redis Endpoints

**Get My Quiz Responses**

```bash
GET /companies/{company_id}/quizzes/{quiz_id}/my-responses
Authorization: Bearer <your_token>
```

Retrieve your stored responses for a specific quiz from Redis (available for 48 hours).

**Response:**

```json
{
  "responses": [
    {
      "user_id": "user-uuid",
      "company_id": "company-uuid",
      "quiz_id": "quiz-uuid",
      "question_id": "question-uuid",
      "answer_ids": [
        "answer-uuid-1",
        "answer-uuid-2"
      ],
      "is_correct": true,
      "answered_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 10
}
```

#### Redis Workflow Business Rules

- Responses stored automatically when quiz is submitted
- Each question response stored separately with unique key
- TTL of 48 hours enforced at storage time
- Automatic expiration - no manual cleanup needed
- Multiple correct answers supported in answer_ids array
- Responses sorted by answered_at timestamp
- Only user's own responses accessible
- Returns empty array if no responses found or expired

### Data Export

Export quiz response data from Redis in JSON or CSV formats with role-based access control.

#### Export Permissions

**Users:**

- Can export their own quiz responses

**Owners/Admins:**

- Can export specific user's responses in their company
- Can export all responses for a specific quiz
- Can export all company responses (when quiz_id provided)

#### Export Endpoints

**Export My Responses**

```bash
GET /export/my-responses?format=json&quiz_id={quiz_id}
Authorization: Bearer <your_token>
```

Export your own quiz responses in JSON or CSV format.

**Query Parameters:**

- `format` - json or csv (default: json)
- `quiz_id` - UUID (required for now)

**Export Specific User's Responses (Owner/Admin)**

```bash
GET /export/companies/{company_id}/users/{user_id}/responses?format=csv&quiz_id={quiz_id}
Authorization: Bearer <your_token>
```

Export a specific user's responses within your company.

**Export Quiz Responses (Owner/Admin)**

```bash
GET /export/companies/{company_id}/quizzes/{quiz_id}/responses?format=json
Authorization: Bearer <your_token>
```

Export all user responses for a specific quiz in your company.

**Export Company Responses (Owner/Admin)**

```bash
GET /export/companies/{company_id}/responses?format=csv&quiz_id={quiz_id}
Authorization: Bearer <your_token>
```

Export company quiz responses (requires quiz_id).

#### Export Formats

**JSON Format:**

```json
[
  {
    "user_id": "uuid",
    "company_id": "uuid",
    "quiz_id": "uuid",
    "question_id": "uuid",
    "answer_ids": [
      "uuid1",
      "uuid2"
    ],
    "is_correct": true,
    "answered_at": "2024-01-15T10:30:00Z"
  }
]
```

**CSV Format:**

```csv
user_id,company_id,quiz_id,question_id,answer_ids,is_correct,answered_at
uuid1,uuid2,uuid3,uuid4,"[""uuid5"",""uuid6""]",true,2024-01-15T10:30:00Z
```

#### Export Business Rules

- Data exported from Redis (48-hour TTL applies)
- CSV answer_ids formatted as JSON array string
- Filenames auto-generated based on export type
- Content-Disposition header sets download filename
- Owner/Admin permissions verified before export
- User must be company member for user-specific exports
- Empty results return empty array (JSON) or empty string (CSV)
- Only responses stored in Redis are exported (within 48h)

### Analytics

Comprehensive analytics system for quiz performance tracking with weekly trends, providing insights for users and
company administrators.

#### Analytics Permissions

**Users:**

- Can view their own overall statistics across all companies
- Can view detailed analytics for each quiz they've taken
- Can view their recent quiz attempts

**Owners/Admins:**

- Can view company overview analytics with trends
- Can view all company members' statistics
- Can view all company quizzes' performance
- Can view detailed analytics for specific users in their company

#### User Analytics Endpoints

**Get My Overall Analytics**

```bash
GET /analytics/users/me/overall
Authorization: Bearer <your_token>
```

View overall rating - average score across all quizzes from all companies.

**Response:**

```json
{
  "average_score": 75.5,
  "total_attempts": 45,
  "total_companies": 3,
  "total_quizzes_taken": 15
}
```

---

**Get My Quiz Analytics**

```bash
GET /analytics/users/me/quizzes
Authorization: Bearer <your_token>
```

View average scores for each quiz with weekly trends.

**Response:**

```json
{
  "quizzes": [
    {
      "quiz_id": "uuid",
      "quiz_title": "Python Basics",
      "company_id": "uuid",
      "company_name": "Tech Corp",
      "average_score": 80.0,
      "attempts_count": 5,
      "last_attempt_at": "2024-12-02T10:30:00Z",
      "weekly_trend": [
        {
          "week": "2024-W48",
          "avg_score": 75.0,
          "attempts": 2
        },
        {
          "week": "2024-W49",
          "avg_score": 85.0,
          "attempts": 3
        }
      ]
    }
  ]
}
```

---

**Get My Recent Attempts**

```bash
GET /analytics/users/me/recent-attempts?limit=10
Authorization: Bearer <your_token>
```

View list of recent quiz attempts with timestamps.

**Query Parameters:**

- `limit` - Number of attempts (1-50, default: 10)

**Response:**

```json
{
  "attempts": [
    {
      "quiz_id": "uuid",
      "quiz_title": "Python Basics",
      "company_name": "Tech Corp",
      "score": 8,
      "total_questions": 10,
      "percentage": 80.0,
      "completed_at": "2024-12-02T10:30:00Z"
    }
  ]
}
```

#### Company Analytics Endpoints (Owner/Admin)

**Get Company Overview**

```bash
GET /analytics/companies/{company_id}/overview
Authorization: Bearer <your_token>
```

View company overview with weekly trends (owner/admin only).

**Response:**

```json
{
  "company_id": "uuid",
  "company_name": "Tech Corp",
  "total_members": 25,
  "total_quizzes": 10,
  "total_attempts": 250,
  "average_company_score": 75.5,
  "weekly_trend": [
    {
      "week": "2024-W48",
      "avg_score": 73.0,
      "attempts": 50
    },
    {
      "week": "2024-W49",
      "avg_score": 78.0,
      "attempts": 60
    }
  ]
}
```

---

**Get Company Members Analytics**

```bash
GET /analytics/companies/{company_id}/members
Authorization: Bearer <your_token>
```

View statistics for all company members with last attempt times (owner/admin only).

**Response:**

```json
{
  "members": [
    {
      "user_id": "uuid",
      "username": "john_doe",
      "email": "john@example.com",
      "total_attempts": 15,
      "average_score": 82.5,
      "last_attempt_at": "2024-12-02T10:30:00Z"
    }
  ]
}
```

---

**Get Company Quizzes Analytics**

```bash
GET /analytics/companies/{company_id}/quizzes
Authorization: Bearer <your_token>
```

View performance analytics for all company quizzes with completion rates (owner/admin only).

**Response:**

```json
{
  "quizzes": [
    {
      "quiz_id": "uuid",
      "quiz_title": "Python Basics",
      "total_attempts": 25,
      "average_score": 75.5,
      "completion_rate": 80.0,
      "weekly_trend": [
        {
          "week": "2024-W48",
          "avg_score": 73.0,
          "attempts": 10
        },
        {
          "week": "2024-W49",
          "avg_score": 78.0,
          "attempts": 15
        }
      ]
    }
  ]
}
```

---

**Get User Analytics in Company**

```bash
GET /analytics/companies/{company_id}/users/{user_id}
Authorization: Bearer <your_token>
```

View detailed analytics for specific user in company with quiz-by-quiz breakdown (owner/admin only).

**Response:**

```json
{
  "user_id": "uuid",
  "username": "john_doe",
  "company_id": "uuid",
  "company_name": "Tech Corp",
  "total_attempts": 15,
  "average_score": 82.5,
  "quizzes": [
    {
      "quiz_id": "uuid",
      "quiz_title": "Python Basics",
      "company_id": "uuid",
      "company_name": "Tech Corp",
      "average_score": 85.0,
      "attempts_count": 5,
      "last_attempt_at": "2024-12-02T10:30:00Z",
      "weekly_trend": [
        {
          "week": "2024-W48",
          "avg_score": 80.0,
          "attempts": 2
        },
        {
          "week": "2024-W49",
          "avg_score": 90.0,
          "attempts": 3
        }
      ]
    }
  ]
}
```

#### Analytics Features

**Weekly Trends:**

- ISO week format: `2024-W48`
- Groups attempts by calendar week
- Calculates average score per week
- Tracks number of attempts per week
- Sorted chronologically

**Metrics Calculated:**

- **Average Score**: (total_correct / total_questions) × 100
- **Completion Rate**: (unique_users_attempted / total_members) × 100
- **Overall Rating**: Average across all quizzes and companies
- **Attempts Count**: Total number of quiz submissions

**Data Sources:**

- PostgreSQL `quiz_attempts` table (permanent storage)
- Real-time calculations via SQL aggregations
- No caching - always fresh data

#### Analytics Business Rules

- User analytics available to all authenticated users (own data only)
- Company analytics require owner or admin role
- Weekly trends calculated from all historical attempts
- Zero values returned when no data available (not errors)
- Completion rate based on unique users (one user = one completion)
- Last attempt timestamp from most recent submission
- Average scores rounded to 2 decimal places
- Trends sorted chronologically (oldest to newest)
- Member verification required for user-specific company analytics

## Notifications System

### Overview

Notification system that automatically notifies users about important events in the application.

### Features

- **Auto-notifications**: Automatically send notifications when a new quiz is created in a company
- **User notifications**: View all notifications for the current user
- **Unread count**: Get count of unread notifications
- **Mark as read**: Mark individual or all notifications as read
- **Notification types**: Support for different notification types (quiz_created, etc.)

### Notification Model

```python
class Notification:
    id: UUID
    user_id: UUID  # FK -> users.id
    message: str  # max 500 chars
    notification_type: str  # max 50 chars
    is_read: bool  # default: False
    related_entity_id: UUID  # nullable, references quiz/company/etc
    read_at: datetime  # nullable
    created_at: datetime
    updated_at: datetime
```

### Notification Types

- `quiz_created` - New quiz created in company (auto-sent to all company members except creator)

### API Endpoints

#### Get User Notifications

```bash
GET /notifications?skip=0&limit=50&unread_only=false
Authorization: Bearer <your_token>
```

**Query Parameters:**

- `skip` (int, default: 0) - Number of notifications to skip
- `limit` (int, default: 50, max: 100) - Number of notifications to return
- `unread_only` (bool, default: false) - Return only unread notifications

**Response:**

```json
{
  "notifications": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "message": "New quiz 'Python Basics' has been created in TechCorp. Take it now!",
      "notification_type": "quiz_created",
      "is_read": false,
      "read_at": null,
      "created_at": "2024-12-05T10:30:00Z",
      "updated_at": "2024-12-05T10:30:00Z"
    }
  ],
  "total": 25,
  "total_count": 5
}
```

---

#### Get Unread Count

```bash
GET /notifications/unread-count
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "unread_count": 5
}
```

---

#### Mark Notification as Read

```bash
PUT /notifications/{notification_id}/read
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "message": "New quiz created",
  "notification_type": "quiz_created",
  "is_read": true,
  "read_at": "2024-12-05T10:35:00Z",
  "created_at": "2024-12-05T10:30:00Z",
  "updated_at": "2024-12-05T10:35:00Z"
}
```

---

#### Mark All Notifications as Read

```bash
PUT /notifications/mark-all-read
Authorization: Bearer <your_token>
```

**Response:**

```json
{
  "message": "All notifications marked as read",
  "updated_count": 5
}
```

### WebSocket Real-Time Notifications

#### WebSocket Connection

Connect to receive real-time notifications:

```bash
ws://localhost:8000/ws/notifications?token=<your_jwt_access_token>
```

**Connection Example (JavaScript):**

```javascript
const token = "your_jwt_access_token";
const ws = new WebSocket(`ws://localhost:8000/ws/notifications?token=${token}`);

ws.onopen = () => {
    console.log("Connected to notifications");
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Notification received:", data);

    if (data.type === "new_notification") {
        // Handle new notification
        console.log("New notification:", data.notification);
    }
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
};

ws.onclose = () => {
    console.log("Disconnected from notifications");
};

// Send ping to keep connection alive
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
    }
}, 30000); // Every 30 seconds
```

#### WebSocket Message Types

**Connection Established:**

```json
{
  "type": "connection_established",
  "message": "Connected to notifications for user john_doe"
}
```

**New Notification (Real-time):**

```json
{
  "type": "new_notification",
  "notification": {
    "id": "uuid",
    "message": "New quiz 'Python Basics' has been created in TechCorp. Take it now!",
    "notification_type": "quiz_created",
    "is_read": false,
    "created_at": "2024-12-05T10:30:00.000Z",
    "related_entity_id": "quiz-uuid"
  }
}
```

**Pong (Keep-Alive Response):**

```json
{
  "type": "pong"
}
```

#### WebSocket Features

- **Real-time delivery**: Notifications sent instantly when created
- **Authentication**: JWT token required via query parameter
- **Multiple connections**: User can have multiple active WebSocket connections
- **Auto-reconnect**: Client should implement reconnection logic
- **Keep-alive**: Send "ping" messages every 30 seconds to keep connection active
- **Graceful disconnect**: Proper cleanup on connection close
- **Connection manager**: Manages all active user connections centrally

#### WebSocket Error Codes

- `1008` - Policy Violation
    - Invalid token
    - User not found
    - Inactive user
    - Authentication failed

#### WebSocket Architecture

```
Quiz Created by Owner/Admin
    ↓
NotificationService.notify_quiz_created()
    ↓
Create notifications in PostgreSQL
    ↓
Send real-time via WebSocket (ConnectionManager)
    ↓
Broadcast to all user's active connections
    ↓
Frontend receives instant notification
```

#### WebSocket vs REST

| Feature | WebSocket | REST API |
|---------|-----------|----------|
| Delivery | Real-time (instant) | Polling required |
| Connection | Persistent | Request/Response |
| Overhead | Low (after initial connection) | High (each request) |
| Use Case | Live notifications | Fetch historical |

---

### Automatic Notifications

#### Quiz Created Trigger

When a company owner or admin creates a new quiz, all company members (except the creator) automatically receive a
notification.

**Trigger:** `POST /companies/{company_id}/quizzes`  
**Recipients:** All company members except quiz creator  
**Message Format:** `"New quiz '{quiz_title}' has been created in {company_name}. Take it now!"`  
**Notification Type:** `quiz_created`  
**Related Entity:** `quiz_id`

### Notification Workflow

```
User creates quiz via QuizService.create_quiz()
    ↓
Quiz successfully created in database
    ↓
NotificationService.notify_quiz_created() triggered
    ↓
Fetch all company members from database
    ↓
Filter out quiz creator from recipients
    ↓
Create bulk notifications for all members
    ↓
Notifications stored in database
    ↓
Members can view via GET /notifications
```

### Database Schema

```sql
CREATE TABLE notifications
(
    id                UUID PRIMARY KEY,
    user_id           UUID                     NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    message           VARCHAR(500)             NOT NULL,
    notification_type VARCHAR(50)              NOT NULL,
    is_read           BOOLEAN                  NOT NULL DEFAULT FALSE,
    related_entity_id UUID,
    read_at           TIMESTAMP WITH TIME ZONE,
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);
CREATE INDEX ix_notifications_is_read ON notifications (is_read);
CREATE INDEX ix_notifications_created_at ON notifications (created_at);
```

### Tests

**Location:** `tests/test_notification.py`

**Test Coverage:**

- `test_notification_service_has_required_methods` - Verify NotificationService has all required methods
- `test_notification_schemas` - Verify notification schemas have required fields
- `test_notification_create_schema` - Test NotificationCreate schema instantiation
- `test_unread_count_response_schema` - Test UnreadCountResponse schema

**Run tests:**

```bash
pytest tests/test_notification.py -v
```

### Business Rules

- Only company members (excluding creator) receive quiz creation notifications
- Notifications stored permanently in PostgreSQL (no TTL)
- Each notification tracks read status and read timestamp
- Bulk notification creation for performance
- Users can only view their own notifications
- Marking as read is idempotent (safe to call multiple times)
- Notification failure doesn't break quiz creation (logged as error)

### Future Enhancements

- Company invitation notifications
- Quiz completion/result notifications
- Reminder notifications for pending quizzes
- Email notifications integration
- Push notifications (mobile/web)
- User notification preferences/settings
- Notification categories and filtering
- Batch operations (delete, archive)

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
- **Refresh Tokens**: Long-lived tokens for obtaining new access tokens (7 days, configurable
  via `JWT_REFRESH_TOKEN_EXPIRE_DAYS`)
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
