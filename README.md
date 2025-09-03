command to remove __pychache__ :  `Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force`
command to save dir structure : `tree /F /A > directory_structure.txt`
run command from root dir to generate migrations: `poetry run alembic -c app/alembic.ini revision --autogenerate -m "create onboarding tables"`
run command from root dir to run migrations: `poetry run alembic -c app/alembic.ini upgrade head`
command to start fastapi server from root dir : `poetry run uvicorn app.main:app  --host 0.0.0.0 --port 8080`

```
Folder PATH listing
Volume serial number is CA69-10D6
C:.
|   .env
|   .gitignore
|   directory_structure.txt
|   oauth-public.key
|   poetry
|   poetry.lock
|   pyproject.toml
|   README.md
|   requirements.txt
|   secrets-to-remove.txt
|   
+---ai
|   |   __init__.py
|   |   
|   +---agents
|   |       resume_parser.py
|   |       __init__.py
|   |       
|   \---llms
|           config.py
|           
+---app
|   |   alembic.ini
|   |   all_files.txt
|   |   main.py
|   |   __init__.py
|   |   
|   +---alembic
|   |   |   env.py
|   |   |   script.py.mako
|   |   |   
|   |   \---versions
|   |           002_insert_onboarding_questions.py
|   |           003_insert_onboarding_questions.py
|   |           6258af572075_create_onboarding_tables.py
|   |           
|   +---api
|   |   |   api.py
|   |   |   __init__.py
|   |   |   
|   |   \---endpoints
|   |           auth.py
|   |           onboard_questions.py
|   |           resume.py
|   |           user_info.py
|   |           __init__.py
|   |           
|   +---core
|   |       config.py
|   |       errors.py
|   |       exception_handlers.py
|   |       redis.py
|   |       security.py
|   |       __init__.py
|   |       
|   +---crud
|   |       onboard_questions.py
|   |       resume.py
|   |       user_info.py
|   |       __init__.py
|   |       
|   +---db
|   |       base.py
|   |       session.py
|   |       __init__.py
|   |       
|   +---models
|   |       onboarding.py
|   |       __init__.py
|   |       
|   +---schemas
|   |       general_response.py
|   |       onboard_questions.py
|   |       user_info.py
|   |       __init__.py
|   |       
|   \---utils
|           api_utils.py
|           exceptions.py
|           redis_utils.py
|           s3_utils.py
|           
\---logs
        endpoints.log
        

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