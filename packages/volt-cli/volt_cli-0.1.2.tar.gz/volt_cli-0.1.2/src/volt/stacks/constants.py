DB_SQL_MODEL = ["SQLite", "PostgreSQL", "MySQL"]
DB_USER_DEFAULT = [DB_SQL_MODEL[1]]
DB_NOSQL_MODEL = {"MongoDB"}
DB_MONGO_MODEL = "MongoDB"
SQL_DEFAULT_DATABASE = {
    DB_SQL_MODEL[0]: "sqlite",
    DB_SQL_MODEL[1]: "postgres",
    DB_SQL_MODEL[2]: "mysql",
}


def get_db_path(db_choice: str) -> str:
    if db_choice in DB_SQL_MODEL:
        return "db_sqlmodel"
    elif db_choice == DB_MONGO_MODEL:
        return "db_mongo"
    else:
        raise ValueError(f"Invalid database choice: {db_choice}")
