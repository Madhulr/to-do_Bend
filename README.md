# Todo App Backend

This is the backend for the Todo application built with Django and Django REST Framework.

## Deployment to Render

### Prerequisites
1. A Render account
2. PostgreSQL database (can be created on Render)

### Steps to Deploy

1. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Select the backend directory as the root directory
   - Choose Python as the runtime

2. **Configure Environment Variables**
   Add the following environment variables in Render:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   DATABASE_NAME=your-database-name
   DATABASE_USER=your-database-user
   DATABASE_PASSWORD=your-database-password
   DATABASE_HOST=your-database-host
   DATABASE_PORT=5432
   ```

3. **Build Command**
   ```
   ./build.sh
   ```

4. **Start Command**
   ```
   gunicorn todo_project.wsgi:application
   ```

### Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- `GET /api/todos/` - List all todos
- `POST /api/todos/` - Create a new todo
- `GET /api/todos/{id}/` - Get a specific todo
- `PUT /api/todos/{id}/` - Update a todo
- `DELETE /api/todos/{id}/` - Delete a todo
- `GET /api/user-activities/` - Get user activities
- `GET /api/user-details/{username}/` - Get user details
- `POST /api/feedback/` - Submit feedback
- `GET /api/feedback/` - List all feedback 