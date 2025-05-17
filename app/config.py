# app/core/config.py
import os

class Settings:
    PROJECT_NAME: str = "ATM Log Monitoring API"
    PROJECT_VERSION: str = "1.0.0"

    # Просто читаем ГОТОВУЮ строку DATABASE_URL из окружения
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Добавим проверку и дефолтное значение, если запускаем локально без Docker
    # и без установленной переменной DATABASE_URL (для удобства разработки вне Docker).
    # В Docker эта переменная ДОЛЖНА БЫТЬ установлена через docker-compose.yml.
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL environment variable not set. Using local fallback (this will fail in Docker if not set via compose).")
        # Замените на ваши реальные локальные креды для разработки БЕЗ Docker
        LOCAL_DEV_POSTGRES_USER = os.getenv("LOCAL_DEV_DB_USER", "postgres")
        LOCAL_DEV_POSTGRES_PASSWORD = os.getenv("LOCAL_DEV_DB_PASS", "password")
        LOCAL_DEV_POSTGRES_SERVER = os.getenv("LOCAL_DEV_DB_HOST", "localhost")
        LOCAL_DEV_POSTGRES_DB = os.getenv("LOCAL_DEV_DB_NAME", "atm_monitoring_db_local")
        DATABASE_URL = f"postgresql://{LOCAL_DEV_POSTGRES_USER}:{LOCAL_DEV_POSTGRES_PASSWORD}@{LOCAL_DEV_POSTGRES_SERVER}:5432/{LOCAL_DEV_POSTGRES_DB}"

    # Настройки для JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback_secret_key_if_not_set")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


settings = Settings()

# Отладочный вывод, чтобы убедиться, что значения корректны
print(f"DEBUG in config.py: DATABASE_URL = {settings.DATABASE_URL}")
print(f"DEBUG in config.py: SECRET_KEY = {settings.SECRET_KEY}")