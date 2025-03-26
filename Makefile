CURRENT_DIRECTORY := $(shell pwd)
TESTSCOPE = apps
TESTFLAGS = --with-timer --timer-top-n 10 --keepdb


help:
	@echo "Docker Compose Help"
	@echo "-----------------------"
	@echo ""
	@echo "Run tests to ensure current state is good:"
	@echo "    make test"
	@echo ""
	@echo "If tests pass, add fixture data and start up the api:"
	@echo "    make begin"
	@echo ""
	@echo "Really, really start over:"
	@echo "    make clean"
	@echo ""
	@echo "See contents of Makefile for more targets."
.PHONY: help

install-dependencies:
	pip install -r requirements.txt
.PHONY: install-dependencies

test:
	pytest -n 8 --cov --cov-fail-under=65
.PHONY: test

checks:
	python manage.py check
.PHONY: checks

migrate:
	python manage.py migrate --no-input
.PHONY: migrate

make-migration:
	python manage.py makemigrations --merge --no-input
.PHONY: make-migration

make-compilemessages:
	python manage.py compilemessages --ignore venv
.PHONY: make-compilemessages

collectstatic:
	python manage.py collectstatic --no-input
.PHONY: collectstatic

server:
	python manage.py runserver 0.0.0.0:8000
.PHONY: server

isort:
	isort --atomic .
.PHONY: isort

apply-isort:
	isort .
.PHONY: apply-isort

autopep8:
	autopep8 -d .
.PHONY: autopep8

flake8:
	flake8 -v --count --show-source --statistics
.PHONY: flake8

celery:
	celery -A m98trading worker --pool=eventlet --concurrency=500 --loglevel=info --logfile=logs/celery.log
.PHONY: celery

celery_bot:
	celery -A m98trading worker --pool=eventlet --concurrency=500 --loglevel=info --statedb=/app/worker.state --logfile=logs/celery.log -Q bot_tasks
.PHONY: celery

celery_beat:
	celery -A m98trading beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler --logfile=logs/celery.log
.PHONY: celery_beat

flower:
	celery -A m98trading flower --purge_offline_workers=10
.PHONY: flower

dev-setup: \
	make-migration \
	migrate \
	collectstatic
.PHONY: dev-setup

local-ci: \
	checks \
	isort \
	flake8 \
	autopep8
.PHONY: local-ci

private-settings:
	echo 'SECRET_KEY="$(SECRET_KEY)"' > $$(pwd)/m98trading/settings/.env
	echo 'ALLOWED_HOSTS="$(ALLOWED_HOSTS)"' >> $$(pwd)/m98trading/settings/.env
	echo 'BASE_URL="$(BASE_URL)"' >> $$(pwd)/m98trading/settings/.env
	echo 'ENV_NAME="$(ENV_NAME)"' >> $$(pwd)/m98trading/settings/.env
.PHONY: private-settings