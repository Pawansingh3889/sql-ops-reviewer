.PHONY: setup test clean

setup:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

clean:
	rm -rf __pycache__
