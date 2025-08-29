command to remove __pychache__ :  `Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force`
command to save dir structure : `tree /F /A > directory_structure.txt`
run command from root dir to generate migrations: `poetry run alembic -c app/alembic.ini upgrade head`
run command from root dir to run migrations: `poetry run alembic -c app/alembic.ini upgrade head`
command to start fastapi server from root dir : `poetry run uvicorn app.main:app`

```
code.ayesha
├─ .env
├─ backend
│  ├─ app
│  │  ├─ alembic
│  │  │  ├─ env.py
│  │  │  ├─ script.py.mako
│  │  │  └─ versions
│  │  ├─ alembic.ini
│  │  ├─ app
│  │  │  ├─ api
│  │  │  │  ├─ deps.py
│  │  │  │  ├─ v1
│  │  │  │  │  ├─ api.py
│  │  │  │  │  ├─ endpoints
│  │  │  │  │  │  └─ __init__.py
│  │  │  │  │  └─ __init__.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ core
│  │  │  │  ├─ config.py
│  │  │  │  ├─ security.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ crud
│  │  │  │  ├─ base_crud.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ db
│  │  │  │  ├─ base.py
│  │  │  │  ├─ base_class.py
│  │  │  │  ├─ init_db.py
│  │  │  │  ├─ session.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ deps
│  │  │  ├─ initial_data.py
│  │  │  ├─ main.py
│  │  │  ├─ models
│  │  │  │  ├─ onboarding.py
│  │  │  │  ├─ user.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ schemas
│  │  │  │  └─ __init__.py
│  │  │  ├─ utils
│  │  │  │  ├─ exceptions
│  │  │  │  │  └─ __init__.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ __init__.py
│  │  │  └─ __pycache__
│  │  │     ├─ main.cpython-313.pyc
│  │  │     └─ __init__.cpython-313.pyc
│  │  ├─ poetry.lock
│  │  ├─ pyproject.toml
│  │  ├─ README.md
│  │  └─ test
│  │     ├─ api
│  │     │  └─ __init__.py
│  │     ├─ test_main.py
│  │     └─ __init__.py
│  └─ Dockerfile
├─ docker-compose.yml
└─ README.md

```

Redis Storage Strategy:

🔑 Key Structure:
├── jwt:{jti} → Full JWT payload (expires with token)
├── user:{user_id}:data → Essential user data (30 days)
├── user:{user_id}:latest_jti → Latest JTI mapping (30 days)
└── user:{user_id}:session → Session data (7 days)


Available Redis Operations:

from app.utils.redis_utils import redis_user_manager

# Store/retrieve JWT by JTI (short-term)
redis_user_manager.store_jwt_payload(jti, payload, ttl)
redis_user_manager.get_jwt_payload(jti)

# Store/retrieve user data (long-term)
redis_user_manager.store_user_data(user_id, payload)
redis_user_manager.get_user_data(user_id)

# Session management
redis_user_manager.store_session_data(user_id, data)
redis_user_manager.get_session_data(user_id)

# Utility functions
redis_user_manager.get_user_latest_jti(user_id)
redis_user_manager.is_user_data_valid(user_id)
redis_user_manager.delete_user_data(user_id)


API Endpoints :

- GET /api/v1/auth/redis/{jti} - Get JWT by JTI
- GET /api/v1/auth/user/{user_id}/data - Get user data (works after JWT expires!)
- GET /api/v1/auth/user/{user_id}/latest-jti - Get latest JTI for user
- GET /api/v1/signup/questions - Get all onboarding questions
- GET /api/v1/signup/questions/{id} - Get specific question
- POST /api/v1/signup/user-info - Create user info (requires JWT)
- GET /api/v1/signup/user-info - Get user info (requires JWT)
- PUT /api/v1/signup/user-info - Update user info (requires JWT)
- DELETE /api/v1/signup/user-info - Delete user info (requires JWT)

The user ID is automatically extracted from the JWT token, so users can only access their own data.