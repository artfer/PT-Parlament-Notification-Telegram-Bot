import os
import logging

DATA_DIR = "/app/data"
FILE_PATH = os.path.join(DATA_DIR, "last_vote_day.txt")

def get_last_processed_date() -> str | None:
    """
    Reads the last processed date from the tracking file.

    Returns:
        The date string if the file exists in the persistent volume, otherwise None.
    """
    if not os.path.exists(FILE_PATH):
        logging.info(f"Tracking file '{FILE_PATH}' not found. Assuming first run.")
        return None
    try:
        with open(FILE_PATH, "r") as f:
            last_date = f.read().strip()
            logging.info(f"Read last processed date '{last_date}' from '{FILE_PATH}'.")
            return last_date
    except Exception as e:
        logging.error(f"Error reading from '{FILE_PATH}': {e}")
        return None

def set_last_processed_date(date: str):
    """Writes the given date to the tracking file."""
    # Ensure the data directory exists before writing
    os.makedirs(DATA_DIR, exist_ok=True)
    logging.info(f"Writing new date '{date}' to '{FILE_PATH}'.")
    with open(FILE_PATH, "w") as f:
        f.write(date)