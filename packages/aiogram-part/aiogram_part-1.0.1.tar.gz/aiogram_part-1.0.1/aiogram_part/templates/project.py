class ProjectStructure:
    @staticmethod
    def get_full_structure(with_db: bool, db_type: str = "sqlite") -> dict:
        directories = [
            "core",
            "handlers/users/commands",
            "handlers/users/messages",
            "handlers/users/callbacks",
            "handlers/admins/commands",
            "handlers/errors",
            "middlewares/users",
            "middlewares/admins",
            "middlewares/common",
            "filters/users/common",
            "filters/users/callback",
            "filters/admins/common",
            "filters/admins/callback",
            "filters/common/common",
            "filters/common/callback",
            "states",
            "keyboards/users",
            "keyboards/admins",
            "keyboards/common",
            "services/users",
            "services/admins",
            "services/common",
            "utils/decorators",
            "utils/validators",
            "utils/formatters",
            "config",
            "tests/handlers",
            "tests/services",
        ]
        
        if with_db:
            directories.extend([
                "database/models",
                "database/crud",
                "database/enums",
                "database/migrations",
            ])
        
        files = {
            "bot.py": ProjectStructure._bot_py(with_db),
            ".env.example": ProjectStructure._env_example(db_type),
            ".gitignore": ProjectStructure._gitignore(),
            "requirements.txt": ProjectStructure._requirements(with_db, db_type),
            "requirements-dev.txt": ProjectStructure._requirements_dev(),
            "Dockerfile": ProjectStructure._dockerfile(),
            "docker-compose.yml": ProjectStructure._docker_compose(with_db, db_type),
            ".dockerignore": ProjectStructure._dockerignore(),
            "Makefile": ProjectStructure._makefile(),
            "pytest.ini": ProjectStructure._pytest_ini(),
            "README.md": ProjectStructure._readme(),
            "core/__init__.py": "",
            "core/configs.py": ProjectStructure._configs_py(),
            "core/bootstrap.py": ProjectStructure._bootstrap_py(with_db),
            "config/__init__.py": "",
            "config/settings.py": ProjectStructure._settings_py(),
            "handlers/__init__.py": ProjectStructure._handlers_init(),
            "handlers/users/__init__.py": ProjectStructure._users_init(),
            "handlers/users/commands/__init__.py": "",
            "handlers/users/messages/__init__.py": "",
            "handlers/users/callbacks/__init__.py": "",
            "handlers/admins/__init__.py": ProjectStructure._admins_init(),
            "handlers/admins/commands/__init__.py": "",
            "handlers/errors/__init__.py": "",
            "handlers/errors/error_handler.py": ProjectStructure._error_handler(),
            "middlewares/__init__.py": "",
            "middlewares/users/__init__.py": "",
            "middlewares/admins/__init__.py": "",
            "middlewares/common/__init__.py": "",
            "middlewares/common/throttling.py": ProjectStructure._throttling_middleware(),
            "filters/__init__.py": "",
            "filters/users/__init__.py": "",
            "filters/users/common/__init__.py": "",
            "filters/users/callback/__init__.py": "",
            "filters/admins/__init__.py": "",
            "filters/admins/common/__init__.py": "",
            "filters/admins/callback/__init__.py": "",
            "filters/common/__init__.py": "",
            "filters/common/common/__init__.py": "",
            "filters/common/callback/__init__.py": "",
            "states/__init__.py": "",
            "keyboards/__init__.py": "",
            "keyboards/users/__init__.py": "",
            "keyboards/admins/__init__.py": "",
            "keyboards/common/__init__.py": "",
            "services/__init__.py": "",
            "services/users/__init__.py": "",
            "services/admins/__init__.py": "",
            "services/common/__init__.py": "",
            "utils/__init__.py": "",
            "utils/decorators/__init__.py": "",
            "utils/decorators/rate_limit.py": ProjectStructure._rate_limit_decorator(),
            "utils/validators/__init__.py": "",
            "utils/formatters/__init__.py": "",
            "utils/logger.py": ProjectStructure._logger_py(),
            "tests/__init__.py": "",
            "tests/conftest.py": ProjectStructure._test_conftest(),
        }
        
        if with_db:
            files.update({
                "database/__init__.py": "",
                "database/connect.py": ProjectStructure._connect_py(),
                "database/models/__init__.py": "",
                "database/crud/__init__.py": "",
                "database/enums/__init__.py": "",
            })
        
        return {"directories": directories, "files": files}
    
    @staticmethod
    def _bot_py(with_db: bool) -> str:
        db_import = "\nfrom database.connect import init_db, close_db" if with_db else ""
        db_init = "\n    await init_db()" if with_db else ""
        db_close = "\n        await close_db()" if with_db else ""
        
        return f'''import asyncio
from core.bootstrap import dp, bot, on_startup{db_import}

async def main():{db_init}
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:{db_close}
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    @staticmethod
    def _env_example(db_type: str = "sqlite") -> str:
        db_urls = {
            "sqlite": "sqlite://db.sqlite3",
            "postgresql": "postgres://botuser:botpass@localhost/botdb",
            "mysql": "mysql://botuser:botpass@localhost/botdb"
        }
        db_url = db_urls.get(db_type, db_urls["sqlite"])
        
        return f'''# Bot Configuration
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321

# Database ({db_type.upper()})
DATABASE_URL={db_url}

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Environment
ENV=development
DEBUG=true

# Webhook (optional)
WEBHOOK_ENABLED=false
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=your_secret_here

# Rate Limiting
RATE_LIMIT=30
RATE_PERIOD=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Payment (optional)
PAYMENT_TOKEN=
'''
    
    @staticmethod
    def _gitignore() -> str:
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Environment variables
.env

# Database
*.sqlite3
*.db

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/

# Docker
.docker/
'''
    
    @staticmethod
    def _requirements(with_db: bool, db_type: str = "sqlite") -> str:
        base = '''aiogram==3.22.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
redis==5.0.1
aioredis==2.0.1
'''
        if with_db:
            base += '''tortoise-orm==0.20.0
aerich==0.7.2
'''
            # Add database-specific drivers
            if db_type == "sqlite":
                base += "aiosqlite==0.19.0\n"
            elif db_type == "postgresql":
                base += "asyncpg==0.29.0\n"
            elif db_type == "mysql":
                base += "aiomysql==0.2.0\n"
        return base
    
    @staticmethod
    def _requirements_dev() -> str:
        return '''pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
black==23.12.1
ruff==0.1.9
mypy==1.7.1
'''
    
    @staticmethod
    def _dockerfile() -> str:
        return '''FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
'''
    
    @staticmethod
    def _docker_compose(with_db: bool, db_type: str = "sqlite") -> str:
        base = '''version: '3.8'

services:
  bot:
    build: .
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
'''
        
        if with_db and db_type != "sqlite":
            base += '''    depends_on:
'''
            if db_type == "postgresql":
                base += '''      - postgres
      - redis
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-botuser}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-botpass}
      POSTGRES_DB: ${DB_NAME:-botdb}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
'''
            elif db_type == "mysql":
                base += '''      - mysql
      - redis
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD:-rootpass}
      MYSQL_DATABASE: ${DB_NAME:-botdb}
      MYSQL_USER: ${DB_USER:-botuser}
      MYSQL_PASSWORD: ${DB_PASSWORD:-botpass}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    command: --default-authentication-plugin=mysql_native_password
'''
            base += '''  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
'''
            if db_type == "postgresql":
                base += '''  postgres_data:
  redis_data:
'''
            elif db_type == "mysql":
                base += '''  mysql_data:
  redis_data:
'''
        else:
            # SQLite or no database
            if db_type == "sqlite":
                base += '''    volumes:
      - ./db.sqlite3:/app/db.sqlite3
'''
            base += '''    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
'''
        return base
    
    @staticmethod
    def _dockerignore() -> str:
        return '''__pycache__
*.py[cod]
*$py.class
.env
venv/
env/
*.sqlite3
*.db
.git
.gitignore
.DS_Store
.idea/
.vscode/
tests/
*.md
!README.md
logs/
'''
    
    @staticmethod
    def _makefile() -> str:
        return '''PYTHON = python3
PIP = pip3
PYTEST = pytest

.PHONY: help install dev test lint format clean docker run

help:
\t@echo "Available commands:"
\t@echo "  make install     Install dependencies"
\t@echo "  make dev         Install dev dependencies"
\t@echo "  make test        Run tests"
\t@echo "  make lint        Run linters"
\t@echo "  make format      Format code"
\t@echo "  make clean       Clean cache files"
\t@echo "  make docker      Build docker image"
\t@echo "  make run         Run bot"

install:
\t$(PIP) install -r requirements.txt

dev: install
\t$(PIP) install -r requirements-dev.txt

test:
\t$(PYTEST) tests/ -v --cov=. --cov-report=html

lint:
\truff check .
\tmypy .

format:
\tblack .
\truff check --fix .

clean:
\tfind . -type d -name "__pycache__" -exec rm -rf {} +
\tfind . -type f -name "*.py[co]" -delete
\tfind . -type d -name "*.egg-info" -exec rm -rf {} +
\tfind . -type d -name ".pytest_cache" -exec rm -rf {} +
\tfind . -type d -name ".mypy_cache" -exec rm -rf {} +
\trm -rf htmlcov/

docker:
\tdocker-compose build

run:
\t$(PYTHON) bot.py

.DEFAULT_GOAL := help
'''
    
    @staticmethod
    def _configs_py() -> str:
        return '''from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # Bot
    BOT_TOKEN: str
    ADMIN_IDS: list[int] = Field(default_factory=list)
    
    # Database
    DATABASE_URL: str = "sqlite://db.sqlite3"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # Webhook
    WEBHOOK_ENABLED: bool = False
    WEBHOOK_URL: str = ""
    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_SECRET: str = ""
    
    # Rate Limiting
    RATE_LIMIT: int = 30
    RATE_PERIOD: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/bot.log"
    
    # Payment
    PAYMENT_TOKEN: str = ""
    
    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.ADMIN_IDS, str):
            self.ADMIN_IDS = [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]

settings = Settings()
'''
    
    @staticmethod
    def _bootstrap_py(with_db: bool) -> str:
        db_import = "\nfrom database.connect import init_db" if with_db else ""
        db_call = "\n    await init_db()" if with_db else ""
        
        return f'''from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from core.configs import settings
from handlers import router
from handlers.errors.error_handler import router as error_router
from middlewares import setup_middlewares{db_import}

try:
    from redis.asyncio import Redis
    storage = RedisStorage(Redis.from_url(settings.redis_url))
except:
    storage = MemoryStorage()

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=storage)

async def on_startup():{db_call}
    setup_middlewares(dp)
    dp.include_router(error_router)
    dp.include_router(router)

async def on_shutdown():
    await bot.session.close()
'''
    
    @staticmethod
    def _handlers_init() -> str:
        return '''from aiogram import Router
from handlers.users import router as users_router
from handlers.admins import router as admins_router

router = Router()
router.include_router(users_router)
router.include_router(admins_router)
'''
    
    @staticmethod
    def _users_init() -> str:
        return '''from aiogram import Router

router = Router()
'''
    
    @staticmethod
    def _admins_init() -> str:
        return '''from aiogram import Router

router = Router()
'''
    
    @staticmethod
    def _middlewares_init() -> str:
        return '''from aiogram import Dispatcher
from middlewares.throttling import ThrottlingMiddleware

def setup_middlewares(dp: Dispatcher):
    dp.message.middleware(ThrottlingMiddleware())
'''
    
    @staticmethod
    def _logger_py() -> str:
        return '''import logging
import logging.config
from pathlib import Path
from config.settings import LOGGING

Path("logs").mkdir(exist_ok=True)

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
'''
    
    @staticmethod
    def _connect_py() -> str:
        return '''from tortoise import Tortoise
from core.configs import settings

TORTOISE_CONFIG = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

async def init_db():
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
'''
    @staticmethod
    def _settings_py() -> str:
        return '''from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": BASE_DIR / "logs" / "bot.log",
            "maxBytes": 10485760,
            "backupCount": 5,
        },
    },
    "loggers": {
        "aiogram": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}
'''
    
    @staticmethod
    def _error_handler() -> str:
        return '''from aiogram import Router
from aiogram.types import ErrorEvent
from utils.logger import logger

router = Router()

@router.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Update: {event.update} caused error: {event.exception}")
    pass
'''
    
    @staticmethod
    def _throttling_middleware() -> str:
        return '''from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from datetime import datetime, timedelta
from core.configs import settings

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.cache: Dict[int, datetime] = {}
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        now = datetime.now()
        
        if user_id in self.cache:
            last_time = self.cache[user_id]
            if now - last_time < timedelta(seconds=settings.RATE_PERIOD):
                return
        
        self.cache[user_id] = now
        result = await handler(event, data)
        return result
'''
    
    @staticmethod
    def _rate_limit_decorator() -> str:
        return '''from functools import wraps
from datetime import datetime, timedelta
from aiogram.types import Message

class RateLimiter:
    def __init__(self):
        self.cache: dict[int, datetime] = {}
    
    def __call__(self, limit: int = 1, period: int = 1):
        def decorator(func):
            @wraps(func)
            async def wrapper(message: Message, *args, **kwargs):
                user_id = message.from_user.id
                now = datetime.now()
                
                if user_id in self.cache:
                    last_time = self.cache[user_id]
                    if now - last_time < timedelta(seconds=period):
                        await message.answer("Too many requests. Please wait.")
                        return
                
                self.cache[user_id] = now
                return await func(message, *args, **kwargs)
            return wrapper
        return decorator

rate_limit = RateLimiter()
'''
    
    @staticmethod
    def _pytest_ini() -> str:
        return '''[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
asyncio_mode = auto
addopts = 
    -v
    --strict-markers
    --cov=.
    --cov-report=html
    --cov-report=term-missing
'''
    
    @staticmethod
    def _test_conftest() -> str:
        return '''import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

@pytest.fixture
async def bot():
    bot = Bot(token="TEST_TOKEN")
    yield bot
    await bot.session.close()

@pytest.fixture
def dp():
    return Dispatcher(storage=MemoryStorage())
'''
    
    @staticmethod
    def _readme() -> str:
        return '''# Telegram Bot

Professional Telegram bot built with aiogram 3.x

## Features

- ✅ Clean architecture
- ✅ Database integration (Tortoise ORM)
- ✅ Redis caching
- ✅ Rate limiting
- ✅ Error handling
- ✅ Logging
- ✅ Docker support
- ✅ Testing framework
- ✅ CI/CD ready

## Setup

### Local Development

1. Install dependencies:
```bash
make install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Run migrations (if using database):
```bash
aerich init -t database.connect.TORTOISE_CONFIG
aerich init-db
```

4. Run bot:
```bash
make run
```

### Docker

```bash
docker-compose up -d
```

## Development

### Install dev dependencies
```bash
make dev
```

### Run tests
```bash
make test
```

### Format code
```bash
make format
```

### Lint code
```bash
make lint
```

## Project Structure

```
bot/
├── core/           # Core functionality
├── handlers/       # Message handlers
├── middlewares/    # Middlewares
├── filters/        # Custom filters
├── keyboards/      # Keyboards
├── states/         # FSM states
├── services/       # Business logic
├── database/       # Database models
├── utils/          # Utilities
├── config/         # Configuration
└── tests/          # Tests
```

## License

MIT
'''
