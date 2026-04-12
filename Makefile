.PHONY: setup test clean lint format typecheck

setup:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy reviewer/

clean:
	rm -rf __pycache__
