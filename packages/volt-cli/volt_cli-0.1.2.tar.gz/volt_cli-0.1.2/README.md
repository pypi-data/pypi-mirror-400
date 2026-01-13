# ⚡ Volt

**Volt** is an extremely fast, modern template and stack manager for Python projects. Built for speed and simplicity, it automates the boilerplate so you can focus on building.

## 🚀 Features

- **Blazing Fast**: Powered by `uv` for instant dependency resolution and environment setup.
- **Modular Stacks**: Full support for **FastAPI** with production-grade defaults.
- **Interactive Scaffolding**: Generate CRUD, models, and schemas in seconds.
- **Docker Integration**: Automated `Dockerfile` and `docker-compose.yaml` generation.
- **Feature Adders**: Easily add Auth, Databases (PostgreSQL, MySQL, MongoDB), or Redis to existing projects.
- **Production Ready**: Structured, type-checked, and linted codebases out of the box.

## 📦 Installation

Volt requires Python 3.13+. We recommend installing it with `uv`:

```bash
# Install via uv (Recommended)
uv tool install volt-cli

# Or via pip
pip install volt-cli
```

## 🛠 Usage

### 1. Create a New Project
Generate a high-performance FastAPI application:
```bash
volt fastapi create my-app
```

### 2. Start Services
Volt manages your local development environment using Docker:
```bash
# Start DB, Redis, and App services
volt up

# Or in detached mode
volt up -d
```

### 3. Scaffold Resources
Generate full CRUD boilerplate (Model, Schema, Router, CRUD) for a resource:
```bash
volt generate crud User
```

### 4. Add Features
Enhance your project as it grows:
```bash
volt add db    # Add Database support (Postgres/MySQL/Mongo)
volt add auth  # Add JWT Authentication
```

### 5. Database Migrations
Volt wraps Alembic for seamless migration management:
```bash
volt db revision -m "add user table"
volt db upgrade head
```

### 6. Build for Production
Create container images for specific platforms:
```bash
volt build --platform linux/amd64
```

## 🏗 Supported Stacks

- **FastAPI**: 
  - **DB Controllers**: SQLAlchemy with async support.
  - **Validation**: Pydantic v2.
  - **Migrations**: Alembic.
  - **Containerization**: Optimized multi-stage Docker builds.

## 🤝 Contributing

1. Clone the repository.
2. Install dependencies: `uv sync`
3. Run tests: `pytest`

