# Backend Internship

FastAPI backend application for internship project.

## Prerequisites

- Python 3.11+
- pip
- Docker (optional, for containerized deployment)

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
SECRET_KEY=your-secret-key-here
```

## Running the Application

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
│   │   └── routes/       # API routes
│   ├── core/             # Core functionality (config, middleware, etc.)
│   │   ├── config.py     # Configuration management
│   │   └── middleware.py # Middleware setup (CORS, etc.)
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # Application entry point
├── tests/                # Test files
├── .env                  # Environment variables (not in git)
├── .env.sample           # Environment template
├── .dockerignore         # Docker ignore rules
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
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
- Restrict `CORS_ORIGINS` to specific domains in production
- Keep dependencies updated

## Authors

- [@jyjuk]

## Mentors

- tkach-v
- FUZIR
- Ilia-puzdranovskuy