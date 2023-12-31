import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, urls = []):
        self.visited_urls = []
        self.urls_to_visit = urls
        self.origin_url = urls

    # Function to fetch the content of a webpage
    def fetch_page_content(self,url):
      try:
         response = requests.get(url)
         response.raise_for_status()
         return response.text
      except requests.exceptions.RequestException as e:
         print(f"Error fetching the page: {e}")
         return None
    
      # Function to extract email addresses and mobile numbers from a given text
    def extract_emails_and_mobile_numbers(self,text):
      # Regular expressions to match email addresses and Indian mobile numbers
      email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
      mobile_pattern = r'\b[789]\d{9}\b'

      emails = re.findall(email_pattern, text)
      mobile_numbers = re.findall(mobile_pattern, text)

      return emails, mobile_numbers

   # Function to crawl a webpage and extract emails and mobile numbers
    def crawl_and_extract(self,url):
      page_content = self.fetch_page_content(url)
      
      if page_content:
         soup = BeautifulSoup(page_content, 'html.parser')
         text = soup.get_text()  # Extract all visible text from the page
         emails, mobile_numbers = self.extract_emails_and_mobile_numbers(text)

         return emails, mobile_numbers
      else:
         return [], []

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url = ''):
        if url.startswith('https://'):
            new_url = str(url)
        else:
         new_url = 'https://nitsri.ac.in/' + str(url)
        if new_url not in self.visited_urls and new_url not in self.urls_to_visit:
            self.urls_to_visit.append(new_url)

    def crawl(self, url):
        html = self.fetch_page_content(url)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(str(url))

    def run(self):
        
        i = 0 # iterator for one webpage link as Home of any site contains so much links and also link of links
        while self.urls_to_visit:
            if i == 1:
                break
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')
            print(1)
            try:
                self.crawl(url)
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)
            i += 1
        output_file = 'extracted_data2.txt'

      
        
        for url in self.urls_to_visit:
                  
                  emails, mobile_numbers = self.crawl_and_extract(url)

                  if len(emails) and len(mobile_numbers):
                    file = open(output_file,'a')
                    file.write(f"\nURL: {url}")
                    file.write(f"\nEmails: {', '.join(emails)}")
                    file.write(f"\nMobile Numbers: {', '.join(mobile_numbers)}\n")
                    file.close()

if __name__ == '__main__':
    Crawler(urls=['https://nitsri.ac.in/']).run()
    
