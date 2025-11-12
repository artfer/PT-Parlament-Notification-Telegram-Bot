import os
from dotenv import load_dotenv

# Load environment variables from a .env file in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Telegram Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

# --- Data Fetcher Configuration ---
ARCHIVE_URL = 'https://www.parlamento.pt/ArquivoDocumentacao/Paginas/Arquivodevotacoes.aspx'