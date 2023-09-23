install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

lint:
	poetry run flake8 src

local:
	poetry run gunicorn -w 5 -b 0.0.0.0:8500 src.page_analyzer:app

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) src.page_analyzer:app