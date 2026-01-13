POSTGRES_DOCKER = """
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
"""

MYSQL_DOCKER = """
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_DATABASE=app
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    healthcheck:
      test: ["CMD", "mysqladmin" ,"ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 5
"""

MONGODB_DOCKER = """
    image: mongo:latest
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 5s
      timeout: 5s
      retries: 5
"""

DOCKER_CONFIGS = {
    "PostgreSQL": POSTGRES_DOCKER,
    "MySQL": MYSQL_DOCKER,
    "MongoDB": MONGODB_DOCKER,
}
