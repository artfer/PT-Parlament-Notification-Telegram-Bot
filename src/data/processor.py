import requests
from bs4 import BeautifulSoup
import logging
import pdfplumber
import io
from collections.abc import Generator

from src.config import settings
from src.utils.date_tracker import get_last_processed_date

class Processor:
    """
    Fetches and processes voting session data from the Portuguese Parliament's archive.
    """
    def __init__(self):
        self.archive_url = settings.ARCHIVE_URL

    def get_latest_session_info(self) -> tuple[str | None, str | None]:
        """
        Fetches the archive page and returns the link to the latest non-supplementary voting session.

        Returns:
            A string containing the URL of the last session,
            or None if no session is found or an error occurs.
        """
        logging.info(f"Fetching voting sessions from {self.archive_url}")
        try:
            response = requests.get(self.archive_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching the Archive URL: {e}")
            return None
        
        archive_html = BeautifulSoup(response.content, 'html.parser')
        calendar_components = archive_html.find_all(class_='home_calendar')

        for calendar_component in calendar_components:
            title = calendar_component.find(class_='title').text.strip()
            if 'suplementar' in title.lower():
                continue
            
            date = calendar_component.find(class_='date').text.strip()
            link = calendar_component.find('a')['href']
            logging.info(f"Found latest session: Date - {date}, Link - {link}")
            return link, date

        logging.warning("No valid voting session found on the page.")
        return None, None

    def get_voting_results_pdf(self, pdf_url: str) -> bytes | None:
        """
        Downloads the voting results PDF from the given URL.

        Args:
            pdf_url: The URL of the PDF file.

        Returns:
            The content of the PDF file as bytes, or None if an error occurs.
        """
        logging.info(f"Downloading PDF from {pdf_url}")
        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while downloading the PDF: {e}")
            return None

    def extract_vote_links(self, pdf_content: bytes) -> list[str]:
        """
        Extracts voting detail links from the PDF content.

        Args:
            pdf_content: The content of the PDF file as bytes.

        Returns:
            A list of unique URLs to the voting detail pages.
        """
        if not pdf_content:
            return []

        logging.info("Extracting links from PDF")
        file_links = []
        try:
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    if page.hyperlinks:
                        for link in page.hyperlinks:
                            if 'Detalhe' in link['uri']:
                                file_links.append(link['uri'])
        except Exception as e:
            logging.error(f"An error occurred while extracting links from PDF: {e}")
        
        unique_links = sorted(list(set(file_links)))
        logging.info(f"Found {len(unique_links)} unique vote links in PDF.")
        return unique_links

    def scrape_vote_details(self, project_url: str) -> dict | None:
        """
        Scrapes the details of a single vote from its detail page.

        Args:
            project_url: The URL of the vote detail page.

        Returns:
            A dictionary containing the scraped vote details, or None if an error occurs.
        """
        logging.info(f"Scraping vote details from {project_url}")
        try:
            r = requests.get(project_url)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching the URL: {e}")
            return None

        project_page = BeautifulSoup(r.content, 'html.parser')
        content = project_page.find(class_='ar-no-padding')
        if not content:
            logging.warning(f"Could not find content container for {project_url}")
            return None

        details = {'url': project_url}

        # Scrape ID, Title, Link, Authors, Result, and Votes
        try:
            details['id'] = content.select_one('[id*="Titulo"]').text.strip()
        except AttributeError:
            logging.warning(f"Could not find ID for {project_url}")

        try:
            title_element = content.select_one('[id*="Assunto"]') or content.select_one('[id*="DocumentoTitulo"]')
            details['title'] = title_element.text.strip()
        except AttributeError:
            logging.warning(f"Could not find Title for {project_url}")

        try:
            link_element = next((l for l in content.select('[id*="DocumentoPDF"]') if l.text == '[formato PDF]'), None)
            if link_element:
                details['link'] = link_element['href']
        except (AttributeError, StopIteration):
            logging.warning(f"Could not find PDF link for {project_url}")

        try:
            authors_element = content.select_one('[id*="Autores_GPs"]')
            if authors_element:
                authors = authors_element.text.strip().replace(',', '').split('\n')
                details['authors'] = [x.strip() for x in authors if x.strip() and '(' not in x.strip()]
            else:
                authors_element = content.select_one('[id*="AutoresD"]')
                if authors_element:
                    authors = authors_element.text.replace('\n', '').replace('\r', '').split(',')
                    authors = [x.strip() for x in authors if x.replace('\r', '').strip()]
                    authors = [x.split(' ')[-1].replace('(', '').replace(')', '') for x in authors]
                    details['authors'] = sorted(list(set(authors)))
                else:
                    authors_element = content.select('[id*="Autor"]')[-1]
                    details['authors'] = [authors_element.text.split(':')[-1].strip()]
        except (AttributeError, IndexError):
             logging.warning(f"Could not find Authors for {project_url}")

        try:
            result_element = content.select_one('[id*="Votacoes"][id*="Resultado"]')
            details['result'] = result_element.text.strip()
        except AttributeError:
            logging.warning(f"Could not find Result for {project_url}")

        try:
            if 'unanimidade' not in details.get('result', '').lower():
                votes_elements = content.select('[id*="Votacoes"][id*="Detalhes"]')
                if votes_elements:
                    votes_container = [x for x in votes_elements if x.contents][-1]
                    votes_text = ''.join([str(x) for x in votes_container.contents])
                else:
                    votes_container = content.select_one('[id*="Votacoes"]')
                    votes_text = str(votes_container.find_all('span')[-1])
                
                votes = votes_text.replace('<span>', '').replace('</span>', '').replace('<span/>', '')
                votes = votes.replace('<i>', '').replace('</i>', '').replace('<i/>', '')
                votes = votes.replace(': ', ':').replace(':', ': ')
                votes = votes.replace('  ', ' ')
                votes = votes.replace('<br/>', '<br>').replace('</br>', '<br>')
                details['votes'] = [x.strip() for x in votes.split('<br>') if x.strip()]
        except (AttributeError, IndexError):
            logging.warning(f"Could not parse votes for {project_url}")

        return details

    def get_latest_voting_data(self) -> Generator[dict, None, None] | None:
        """
        Orchestrates the fetching of voting data and yields each vote's details
        as a generator.

        Yields:
            A dictionary representing a single vote's details.
        
        Returns:
            A generator of vote details if there is a new session to process.
            None if the latest session has already been processed or if no
            session is found.
        """
        latest_session_link, session_date = self.get_latest_session_info()
        if not latest_session_link or not session_date:
            return

        pdf_content = self.get_voting_results_pdf(latest_session_link)
        if not pdf_content:
            return None

        vote_links = self.extract_vote_links(pdf_content)
        if not vote_links:
            return None

        # This is the generator expression that will be returned
        def vote_generator():
            logging.info(f"Processing {len(vote_links)} votes one by one...")
            for link in vote_links:
                details = self.scrape_vote_details(link)
                if details:
                    details['date'] = session_date
                    yield details
        
        return vote_generator()
