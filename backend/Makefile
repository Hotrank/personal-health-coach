.PHONY: lint format start-dev

lint:
	mypy .
	ruff check .

format:
	ruff format .

start-dev:
	uvicorn main:app --reload

test:
	PYTHONPATH=. pytest -s

# Alembic commands
# generate a new migration script with given message
alembic-generate:
	alembic revision --autogenerate -m "$(message)"

# apply migrations to the database
alembic-upgrade:
	alembic upgrade head

# psql
psql:
	psql -U devuser -d chatdb -h localhost
# example usage: make psql
# then \dt, \d table_name, etc. to inspect the database, \q to quit
