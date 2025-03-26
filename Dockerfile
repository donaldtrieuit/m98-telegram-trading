FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update \
    && apt-get -y install vim libpq-dev gcc build-essential apt-utils nginx gettext \
    && pip install --upgrade pip \
    && pip install psycopg2
RUN pip install gunicorn

# Install dependencies:
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p /app/logs
RUN mv m98trading/settings/.env.example m98trading/settings/.env
RUN make collectstatic
RUN make make-compilemessages
RUN rm m98trading/settings/.env

RUN mkdir -p logs /var/www/html/static
RUN cp -ar staticfiles/* /var/www/html/static/