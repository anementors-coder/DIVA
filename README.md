command to remove __pychache__ :  Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
command to save dir structure : tree /F /A > directory_structure.txt



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