install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

lint:
	poetry run flake8 src

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) src.page_analyzer:app