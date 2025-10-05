# Psychology Assessment Platform

A comprehensive psychological assessment and therapy support platform built with FastAPI, SQLAlchemy, and PostgreSQL. This platform provides various psychological tests, attendance tracking, and user management features.

## 🌟 Features

- **User Authentication**
  - JWT-based authentication
  - Role-based access control (User, Premium User, Admin)
  - Secure password hashing with bcrypt

- **Psychological Tests**
  - Multiple test types (RADS, DASS, MDQ)
  - Test result tracking
  - Question and answer management

- **Attendance System**
  - Daily check-ins with streak tracking
  - Reward system based on consecutive days
  - Weekly progress tracking

- **Situational Scenarios**
  - Interactive situational questions
  - Multiple difficulty levels
  - Progress tracking

- **User Management**
  - Profile management
  - Test history
  - Star-based reward system

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (or SQLite for development)
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd psychology
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Database configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/psychology
   
   # JWT Configuration
   SECRET_KEY=your-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   python -m app.scripts.import_datas
   ```

### Resetting the Database

To completely reset the database (WARNING: This will delete all data):

1. Drop and recreate the database:
   ```bash
   # For SQLite (default development)
   rm -f psychology.db
   
   # For PostgreSQL
   psql -U postgres -c "DROP DATABASE IF EXISTS psychology"
   psql -U postgres -c "CREATE DATABASE psychology"
   ```

2. Reinitialize the database:
   ```bash
   alembic upgrade head
   python -m app.scripts.import_datas
   ```

### Running the Application

1. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🛠️ API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `DELETE /api/v1/users/me` - Delete user account

### Attendance
- `GET /api/v1/attendance` - Mark daily attendance

### Tests
- `GET /api/v1/tests?type=RADS|DASS|MDQ` - Get test questions
- `POST /api/v1/tests` - Submit test answers

### Situational Scenarios
- `GET /api/v1/situational` - Get situational questions
- `POST /api/v1/situational` - Submit answers to situational questions

## 📊 Database Schema

The database includes the following main tables:
- `users` - User accounts and profiles
- `group` - Test categories
- `test` - Test questions
- `option` - Answer options for tests
- `situation_group` - Categories for situational questions
- `situational_question` - Situational questions
- `situational_answer` - Possible answers to situational questions

## 🧪 Testing

To run tests:
```bash
pytest
```

## 🐳 Docker Deployment

1. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

2. Initialize the database:
   ```bash
   docker-compose exec web alembic upgrade head
   docker-compose exec web python -m app.scripts.import_datas
   ```

### Resetting the Database in Docker

To completely reset the database in Docker (WARNING: This will delete all data):

1. Stop and remove containers and volumes:
   ```bash
   docker-compose down -v
   ```

2. Restart the services:
   ```bash
   docker-compose up -d
   ```

3. Reinitialize the database:
   ```bash
   docker-compose exec web alembic upgrade head
   docker-compose exec web python -m app.scripts.import_datas
   ```

The application will be available at http://localhost:8000

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For any questions or feedback, please contact the development team.
 psychology