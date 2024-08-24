# CREQUEST
Start project
```
cd app
pip install -r requirements.txt
python backend_pre_start.py
python initial_data.py
uvicorn main:app --reload
```
Create a Migration Script
```
alembic revision -m "create int table" --autogenerate
```
Run migrations
```
alembic upgrade head
```
Run pre-commit
```
pre-commit run --all-files
```
