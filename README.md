# Telegram Groq AI Chatbot

This is a Telegram chatbot that integrates with the Groq AI API for generating responses. It uses Redis to store chat history, allowing for conversational context. The entire application is containerized using Docker and Docker Compose for easy setup and deployment.

## Features

- **Telegram Bot Integration:** A fully functional Telegram bot using the `python-telegram-bot` library.
- **Groq AI Integration:** Connects to the Groq AI API to provide intelligent, conversational responses.
- **Chat History:** Uses Redis to store a history of the conversation, allowing the AI to have context.
- **Commands:**
    - `/start`: Starts the conversation and clears any previous chat history.
    - `/clear`: Clears the current chat history.
    - `/help`: Displays help information.
- **Dockerized:** Comes with a `Dockerfile` and `docker-compose.yml` for easy setup and deployment.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation and Usage

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd telegram-bot
    ```

2.  **Create a `.env` file:**
    Copy the `.env.example` file to `.env`:
    ```bash
    cp .env.example .env
    ```

3.  **Configure your environment variables:**
    Open the `.env` file and fill in your API keys:
    ```
    TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    GROQ_API_KEY=YOUR_GROQ_API_KEY
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0
    ```
    -   `TELEGRAM_BOT_TOKEN`: Get this from BotFather on Telegram.
    -   `GROQ_API_KEY`: Get this from `https://console.groq.com/keys`.
    -   `REDIS_HOST` should be set to `redis` to connect to the Redis container.

4.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    This command will build the Docker image for the bot, pull the Redis image, and start both services.

5.  **Interact with your bot:**
    Open Telegram and find your bot. You can start interacting with it.

6.  **Stop the services:**
    To stop the bot and Redis container, run:
    ```bash
    docker-compose down
    ```

## Built With

- [Python](https://www.python.org/)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [Groq AI](https://groq.com/)
- [Redis](https://redis.io/)
- [Docker](https://www.docker.com/)