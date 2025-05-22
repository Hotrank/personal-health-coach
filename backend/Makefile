.PHONY: lint format start-dev

lint:
	mypy .
	ruff check .

format:
	ruff format .

start-dev:
	uvicorn main:app --reload
