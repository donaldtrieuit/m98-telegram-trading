
# M98 Automation Trading

M98 Automation Trading is a tool designed to automate trading by reading signals from a Telegram channel or TradingView and placing market orders based on those signals. Built with Django and Django REST Framework, it leverages Celery for task automation, RabbitMQ as a message broker, and Redis for caching and task management.

## Table of Contents
- [Features](#features)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup Using Docker](#setup-using-docker) 
	  - [Initial Setup](#initial-setup)
  - [Usage](#usage)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- **Signal Detection**: Automatically reads trading signals from a specified Telegram channel or TradingView.
- **Order Execution**: Places buy/sell orders directly to the market based on the detected signals.
- **Customizable**: Easily configurable to adapt to different signal formats and trading platforms.
- **Scalable**: Uses Celery with RabbitMQ and Redis for efficient task processing.

## How It Works
1. The Django application monitors a Telegram channel or TradingView for trading signals.
2. When a signal is detected, Celery tasks process the data (e.g., buy/sell, price, etc.).
3. Orders are executed in the market automatically via integrated APIs.

## Getting Started
### Prerequisites
- Python 3.10
- Telegram API credentials (if using Telegram)
- TradingView integration (if applicable)
- Access to a trading platform API (e.g., M98 or your preferred broker)
- RabbitMQ installed and running
- Redis installed and running

### Setup using Docker  
This required you having [docker](https://docs.docker.com/get-docker/)  
  and [docker-compose](https://docs.docker.com/compose/install/) installed and running.  
  
#### Initial setup  
Make a copy of the `docker-compose.yml.sample` file. Optionally, make copies of the sample environment files if needed.  
  
```bash  
cp docker-compose.yml.sample docker-compose.yml
```  
  
The project used django-environ package for managing environment variables. You must also make a copy of the `.env_example` in the `m98trading/settings/` directory.   
After that, update the variables in `.env` file with your local environment.  
  
```bash  
cp m98trading/settings/.env_example m98trading/settings/.env
```  
  
Build docker containers  
```bash  
docker-compose build
```  
  
Now start the core backend service  
```bash  
docker-compose up -d
```  

### Usage  
Set up initial user  
```bash
python manage.py createsuperuser  
```  

Run test suite  
```bash  
make test  
```  
  
Check sorting on imports  
```bash  
make isort  
```  
  
Check code formating  
```bash  
make flake8  
```  
  
Autoformat code  
```bash  
make autopep8  
```  
  
Audit code  
```bash  
make flake8  
```  
  
Run checks  
```bash  
make checks  
```

## Technologies

-   **Django**: Web framework for the core application.
-   **Django REST Framework**: API development for signal integration and order management.
-   **Celery**: Asynchronous task queue for processing trading signals.
-   **RabbitMQ**: Message broker for Celery task distribution.
-   **Redis**: Caching and task result storage.

## Contributing

Feel free to fork this repository, submit issues, or create pull requests to improve the project!

## License

This project is licensed under the MIT License - see the file for details.

## Contact

- For questions or support, reach out via [GitHub Issues](https://github.com/donaldtrieuit/m98-telegram-trading/issues).
- Email: donaldtrieu@gmail.com