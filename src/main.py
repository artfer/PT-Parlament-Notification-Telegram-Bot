import logging
from src.data.processor import Processor
from src.bot.client import send_telegram_message
from src.bot.messages import format_voting_session_message
from src.utils.date_tracker import get_last_processed_date, set_last_processed_date
from src.utils.helpers import setup_logging

def main():
    """
    Main function to be executed by the cron job.
    Fetches the last voting session, formats it, and sends it to Telegram.
    """
    setup_logging()
    
    logging.info("Starting the daily update process.")
    
    processor = Processor()
    
    # 1. Get the latest session info without processing yet
    latest_session_link, latest_date = processor.get_latest_session_info()
    if not latest_date:
        logging.info("No new session found. Exiting.")
        return

    # 2. Check if this date has already been processed
    last_processed_date = get_last_processed_date()
    if latest_date == last_processed_date:
        logging.info(f"Latest session date ({latest_date}) has already been processed. Skipping.")
        return
    
    # 3. If new, process the votes and send notifications
    votes_iterator = processor.get_latest_voting_data()
    votes_found = False
    if votes_iterator:
        for vote_details in votes_iterator:
            votes_found = True
            logging.info(f"Processing and sending notification for vote ID: {vote_details.get('id', 'N/A')}")
            message = format_voting_session_message(vote_details)
            send_telegram_message(message)

    # 4. If votes were found and sent, update the tracking file
    if votes_found:
        set_last_processed_date(latest_date)

if __name__ == "__main__":
    main()