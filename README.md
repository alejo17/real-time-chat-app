Django + Redis Real-time Chat

This project is a real-time chat application built with Django, Django Channels, WebSockets, and Redis.
Messages are stored in Redis, conversations and users in PostgreSQL.
It includes basic signup and login, throttling (rate limiting), and logging.


***Running with Docker***
    Prerequisites
    - Docker
    - Docker Compose

    Steps
    1. Build and start containers:
        docker-compose up --build
    2. Access the app at http://localhost:8000/signup

***Running Locally with Virtualenv***
    Prerequisites
    - Python 3
    - Redis installed and running locally
    - PostgreSQL installed and running locally

    Steps
    1. Create and activate a virtual environment:
        python -m venv venv
        source venv/bin/activate
    3. Install dependencies:
        pip install -r requirements.txt
    4. Configure your PostgreSQL database data(also POSTGRES_HOST for 'localhost')
        and Redis connection details(change 'redis' for '127.0.0.1') in settings.py file.
    5. Apply migrations:
        python manage.py migrate
    6. Run the development server:
        daphne realtimechat.asgi:application -p 8000
    7. Access the app at http://localhost:8000/signup

***Run tests***
    pytest -s