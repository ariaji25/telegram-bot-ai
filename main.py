import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import redis
import json
import gspread
from google.oauth2.service_account import Credentials

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logger.error("GROQ_API_KEY not found in environment variables.")
    exit(1)
groq_client = Groq(api_key=groq_api_key)

# Get Groq Model from environment variables
groq_model = os.getenv("GROQ_MODEL", "gemma-7b-it") # Default to gemma-7b-it if not set

# Initialize Redis client
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_db = int(os.getenv("REDIS_DB", 0))
redis_user = os.getenv("REDIS_USER")
redis_password = os.getenv("REDIS_PASSWORD")

redis_config = {
    'host': redis_host,
    'port': redis_port,
    'db': redis_db,
    'decode_responses': True
}

if redis_user:
    redis_config['username'] = redis_user
if redis_password:
    redis_config['password'] = redis_password

try:
    redis_client = redis.StrictRedis(**redis_config)
    redis_client.ping()
    logger.info("Connected to Redis successfully!")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Could not connect to Redis: {e}")
    redis_client = None

# Initialize Google Sheets client
google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
google_sheet_name = os.getenv("GOOGLE_SHEET_NAME")
gsheet_client = None

if google_credentials_file and google_sheet_name:
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_file(
            google_credentials_file, scopes=scopes
        )
        gsheet_client = gspread.authorize(credentials)
        logger.info("Connected to Google Sheets successfully!")
    except Exception as e:
        logger.error(f"Could not connect to Google Sheets: {e}")
        gsheet_client = None

def get_chat_history(chat_id: int) -> list:
    if redis_client:
        history = redis_client.get(f"chat_history:{chat_id}")
        return json.loads(history) if history else []
    return []

def add_to_chat_history(chat_id: int, role: str, content: str):
    if redis_client:
        history = get_chat_history(chat_id)
        history.append({"role": role, "content": content})
        # Keep history to a reasonable length, e.g., last 20 messages
        history = history[-20:]
        redis_client.set(f"chat_history:{chat_id}", json.dumps(history))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued and clear previous chat history."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Clear existing chat history for the user
    if redis_client:
        redis_client.delete(f"chat_history:{chat_id}")
        logger.info(f"Chat history for chat_id {chat_id} cleared by /start command.")

    await update.message.reply_html(
        f"Hi {user.mention_html()}! I'm a chatbot. I've cleared our previous conversation. How can I help you today?",
    )
    add_to_chat_history(chat_id, "system", "Chat started.")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the chat history for the user."""
    chat_id = update.effective_chat.id
    if redis_client:
        redis_client.delete(f"chat_history:{chat_id}")
        logger.info(f"Chat history for chat_id {chat_id} cleared by /clear command.")
        await update.message.reply_text("Your chat history has been cleared.")
    else:
        await update.message.reply_text("Redis is not connected, so chat history cannot be cleared.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Available commands:\n/start - Start a new conversation\n/clear - Clear chat history\n/help - Show this help message")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and respond using Groq API."""
    user_message = update.message.text
    chat_id = update.effective_chat.id
    logger.info(f"User ({chat_id}): {user_message}")

    add_to_chat_history(chat_id, "user", user_message)
    chat_history = get_chat_history(chat_id)

    # Convert chat history to Groq API message format
    groq_messages = []
    for msg in chat_history:
        groq_messages.append({"role": msg["role"], "content": msg["content"]})
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=groq_messages,
            model=groq_model, # Use the model from environment variable
        )
        ai_response = chat_completion.choices[0].message.content
        await update.message.reply_text(ai_response)
        add_to_chat_history(chat_id, "assistant", ai_response)
        logger.info(f"AI ({chat_id}): {ai_response}")
    except Exception as e:
        logger.error(f"Error communicating with Groq API or Redis: {e}")
        await update.message.reply_text("Sorry, I'm having trouble connecting to the AI or saving chat history. Please try again later.")

async def expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log an expense to Google Sheets."""
    if not gsheet_client:
        await update.message.reply_text(
            "Google Sheets integration is not configured. Please check the logs for details."
        )
        return

    try:
        # Example: /expense <amount> <category> <description>
        args = context.args
        if len(args) < 3:
            await update.message.reply_text(
                "Usage: /expense <amount> <category> <description>"
            )
            return

        amount = args[0]
        category = args[1]
        description = " ".join(args[2:])
        
        # Open the spreadsheet and select the first sheet
        sheet = gsheet_client.open(google_sheet_name).sheet1
        
        # Append the expense as a new row
        from datetime import datetime
        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), amount, category, description]
        sheet.append_row(row)
        
        await update.message.reply_text("Expense logged successfully!")

    except gspread.exceptions.SpreadsheetNotFound:
        await update.message.reply_text(
            f"Spreadsheet '{google_sheet_name}' not found. Please check the name and sharing settings."
        )
    except Exception as e:
        logger.error(f"Error logging expense: {e}")
        await update.message.reply_text(
            "Sorry, there was an error logging your expense."
        )


def main():
    """Start the bot."""
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_bot_token).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("expense", expense_command))

    # On non-command messages - handle with Groq API
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot started!")

if __name__ == "__main__":
    main()
