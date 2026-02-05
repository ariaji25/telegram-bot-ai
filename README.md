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
    - `/expense <amount> <category> <description>`: Logs an expense to the configured Google Sheet.
- **Dockerized:** Comes with a `Dockerfile` and `docker-compose.yml` for easy setup and deployment.

## Google Sheets Integration Setup

To enable expense logging to Google Sheets, you need to configure Google Cloud credentials and share your spreadsheet appropriately.

### 1. Google Cloud Platform (GCP) Setup for Service Account

1.  **Go to Google Cloud Console**: Navigate to [console.cloud.google.com](https://console.cloud.google.com/).
2.  **Create or Select a Project**: From the project dropdown at the top, select an existing project or create a new one.
3.  **Enable Google Drive API and Google Sheets API**: 
    *   In the console, go to "APIs & Services" > "Library".
    *   Search for "Google Drive API" and enable it.
    *   Search for "Google Sheets API" and enable it.
4.  **Create a Service Account**:
    *   Go to "APIs & Services" > "Credentials".
    *   Click on "+ Create Credentials" and select "Service account".
    *   Fill out the "Service account name" and "Service account ID" fields.
    *   Click "Create and continue". You can skip granting a role for now.
    *   Click "Done".
5.  **Generate and Download the JSON Key File**:
    *   On the "Credentials" page, find your newly created service account.
    *   Click on the email address of the service account.
    *   Go to the "Keys" tab.
    *   Click "Add Key" > "Create new key".
    *   Select "JSON" as the key type and click "Create".
    *   A JSON file containing your service account credentials will be downloaded. **Rename this file to `google_credentials.json` and place it in the root directory of this project.** **KEEP THIS FILE SECURE AND DO NOT COMMIT IT TO PUBLIC REPOSITORIES.**

### 2. Share Your Google Sheet with the Service Account

1.  **Create a Google Sheet**: Create a new Google Sheet where you want to store your expenses. Ensure the first row contains headers like `Timestamp`, `Amount`, `Category`, `Description`.
2.  **Share the Google Sheet**:
    *   Open your Google Sheet.
    *   Click the "Share" button.
    *   In the "Share with people and groups" dialog, paste the service account's email address (found in the `client_email` field within your `google_credentials.json` file).
    *   Grant it "Editor" permissions.
    *   Click "Share".

### 3. Configure `.env` for Google Sheets

Add the following variables to your `.env` file:

```
GOOGLE_SHEET_NAME=YourSpreadsheetName
GOOGLE_CREDENTIALS_FILE=google_credentials.json
```
- Replace `YourSpreadsheetName` with the exact name of your Google Sheet.
- `GOOGLE_CREDENTIALS_FILE` should point to the `google_credentials.json` file you placed in the project root.

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
    REDIS_USER=
    REDIS_PASSWORD=
    GOOGLE_SHEET_NAME=YourSpreadsheetName
    GOOGLE_CREDENTIALS_FILE=google_credentials.json
    ```
    -   `TELEGRAM_BOT_TOKEN`: Get this from BotFather on Telegram.
    -   `GROQ_API_KEY`: Get this from `https://console.groq.com/keys`.
    -   `GROQ_MODEL`: Recommended model (e.g., `gemma-7b-it`).
    -   `REDIS_HOST` should be set to `redis` to connect to the Redis container.
    -   `REDIS_USER` and `REDIS_PASSWORD` are optional, but if used, configure your Redis server accordingly.
    -   `GOOGLE_SHEET_NAME`: The exact name of your Google Sheet.
    -   `GOOGLE_CREDENTIALS_FILE`: The path to your service account JSON file.

4.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    This command will build the Docker image for the bot, pull the Redis image, and start both services.

5.  **Interact with your bot:**
    Open Telegram and find your bot. You can start interacting with it, including using the `/expense` command.

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
- [Google Sheets API](https://developers.google.com/sheets/api) (via `gspread`)
- [Docker](https://www.docker.com/)