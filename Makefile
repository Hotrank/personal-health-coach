.PHONY: lint-py format-py

lint-py:
	mypy .
	ruff check .

format-py:
	ruff format .