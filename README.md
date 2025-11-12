# 🗳️ PT Parliament Voting Notifier

This project is a Python-based bot that automatically scrapes the official Portuguese Parliament's website for daily voting sessions. It parses the results, formats them into a clear message, and sends a notification to a specified Telegram channel for each vote.

The entire application is containerized using Docker and scheduled to run once a day, ensuring you never miss an update.

## Features

- **Automated Scraping**: Fetches the latest voting session archive page.
- **PDF Parsing**: Downloads and parses the session's PDF file to extract details for each individual vote.
- **Detailed Notifications**: Scrapes the detail page for each vote to gather information like title, authors, and voting breakdown.
- **Telegram Integration**: Sends a formatted, easy-to-read message for each vote to a configured Telegram chat.
- **Stateful Operation**: Prevents duplicate notifications by saving the date of the last processed session in a persistent volume.
- **Containerized & Scheduled**: Uses Docker and cron to run automatically every day at 10 PM.
- **Chat ID Utility**: Includes a helper script to easily find a Telegram chat ID.

---

## How It Works

1.  The Docker container starts and initiates a cron job.
2.  Every day at 10:00 PM (22:00), the cron job executes the main script (`src/main.py`).
3.  The script checks the date of the latest voting session on the parliament website.
4.  It compares this date with the one stored in `last_vote_day.txt` (in the persistent `app_data` volume). If they match, the script exits to avoid sending duplicates.
5.  If the session is new, the script downloads and parses the session PDF to get links to all individual votes.
6.  It then iterates through each vote, scrapes its details, formats a message, and sends it to the configured Telegram chat.
7.  After successfully processing all votes for the new session, it updates `last_vote_day.txt` with the new date.

---

## Setup and Usage

Follow these steps to get the notifier up and running.

### Prerequisites

- Git
- Docker
- Docker Compose

### 1. Clone this Repository

### 2. Configure Environment Variables

The application's configuration is managed via environment variables set directly in the `docker-compose.yml` file.

Open the `docker-compose.yml` file and locate the `environment` section. You will need to replace the placeholder values.

```yaml
services:
  notifier:
    ...
    environment:
     - TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
     - TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID_HERE
     - ARCHIVE_URL=https://www.parlamento.pt/ActividadeParlamentar/Paginas/Votacoes.aspx
```

**How to get your credentials:**

-   **`TELEGRAM_BOT_TOKEN`**:
    1.  Talk to the BotFather on Telegram.
    2.  Create a new bot by sending `/newbot`.
    3.  BotFather will give you a unique token. Copy and paste it here.

-   **`TELEGRAM_CHAT_ID`**:
    1.  In your `.env` file, set a temporary value for `TELEGRAM_CHAT_ID` (e.g., `TELEGRAM_CHAT_ID=12345`).
    2.  Start the service for the first time: `docker compose up -d --build`.
    3.  Add your bot to the target Telegram group or channel and make it an administrator.
    4.  Execute the ID utility script inside the running container. This will start a temporary process to listen for your command.
        ```bash
        docker exec -it pt-parliament-notifier python -m src.utils.get_channel_id
        ```
    5.  In the Telegram group, type the command `/chatid`. The bot will reply with the correct chat ID (it's usually a negative number for groups).
    6.  Copy the correct ID and update the `TELEGRAM_CHAT_ID` value in your `.env` file.
    7.  Restart the service to apply the new environment variable:
        ```bash
        docker compose up -d --force-recreate
        ```

### 3. Build and Run the Container

With Docker and Docker Compose installed, run the following command from the project root:

```bash
# Build the image and start the service in detached mode
docker compose up -d --build
```

Your notifier is now running! It will automatically execute the script every night.