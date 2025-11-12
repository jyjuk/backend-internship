# Backend Internship

FastAPI backend application for internship project.

## Prerequisites

- Python 3.11+
- pip

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
│   │   └── routes/      # API routes
│   ├── core/            # Core functionality (config, etc.)
│   ├── schemas/         # Pydantic schemas
│   └── main.py          # Application entry point
├── tests/               # Test files
├── .env                 # Environment variables (not in git)
├── .env.sample          # Environment template
├── requirements.txt     # Python dependencies
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

## Authors

- [@jyjuk]

## Mentors

- FUZIR
- Ilia-puzdranovskuy
