# app/security.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Set

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# Попытаемся импортировать из .core.config, если этот файл там
# Иначе, если config.py на том же уровне, что и security.py
try:
    from core.config import settings # Если config.py в папке core/
except ImportError:
    from config import settings      # Если config.py на одном уровне с security.py

from schemas import TokenData  # Pydantic модель для данных в токене

# --- Настройки для JWT (остаются как были) ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли обычный пароль хешированному."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Возвращает хеш для пароля."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа.
    :param data: Данные для кодирования в токен (обычно {'sub': username, 'user_id': id}).
    :param expires_delta: Время жизни токена. Если None, используется значение по умолчанию.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Декодирует токен доступа.
    Возвращает данные пользователя (TokenData) или None, если токен невалиден.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")

        if username is None or user_id is None:
            return None

        return TokenData(username=username, user_id=user_id)
    except JWTError:
        return None

# --- Реализация API-ключа ---
API_KEY_NAME = "X-API-Key"  # Имя HTTP-заголовка для API-ключа
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Загружаем валидные API-ключи из переменной окружения
# VALID_ATM_API_KEYS должна быть задана в окружении (например, через docker-compose.yml из .env)
# Ключи могут быть перечислены через запятую
raw_keys_str = os.getenv("VALID_ATM_API_KEYS", "")
VALID_API_KEYS: Set[str] = set(key.strip() for key in raw_keys_str.split(',') if key.strip())

if not VALID_API_KEYS and os.getenv("DUMMY_API_KEY_FOR_DEV"): # Только для разработки, если основная переменная не задана
    print(f"WARNING: VALID_ATM_API_KEYS not set. Using DUMMY_API_KEY_FOR_DEV: {os.getenv('DUMMY_API_KEY_FOR_DEV')}")
    VALID_API_KEYS.add(os.getenv("DUMMY_API_KEY_FOR_DEV"))
elif not VALID_API_KEYS:
    print("CRITICAL WARNING: No VALID_ATM_API_KEYS configured. API key authentication will fail for ATM simulators.")


async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    """
    Зависимость для проверки API-ключа.
    Используется для авторизации запросов от ATM симуляторов.
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated or Missing API Key"
        )
    if api_key_header in VALID_API_KEYS:
        return api_key_header
    else:
        print(f"Failed API Key Auth: Received '{api_key_header}', Expected one of {VALID_API_KEYS}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )