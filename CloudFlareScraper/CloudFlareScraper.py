import httpx
import requests
from cloudscraper import create_scraper

class CloudFlareScraper:
    def __init__(self, url, **kwargs):
        self.url = url
        self.user_agent = kwargs.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        self.timeout = kwargs.get('timeout', 30)
        self.verify = kwargs.get('verify', True)
        self.proxies = kwargs.get('proxies', {})
        self.client = None
        self.scraper = None

    def __enter__(self):
        try:
            self.client = httpx.Client(timeout=self.timeout, verify=self.verify, proxies=self.proxies, headers={'User-Agent': self.user_agent})
        except Exception as e:
            self.client = None
        
        try:
            self.scraper = create_scraper()
        except Exception as e:
            self.scraper = None

        if self.client is None and self.scraper is None:
            raise ValueError("Neither HTTPX Client nor Cloudscraper is initialized.")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.client:
            self.client.close()

    def _send_request(self, method, data=None, **kwargs):
        headers = {'User-Agent': self.user_agent}
        headers.update(kwargs.get('headers', {}))
        
        try:
            if self.client:
                if method == 'GET':
                    response = self.client.get(self.url, headers=headers)
                elif method == 'POST':
                    headers['Content-Type'] = 'application/json'
                    response = self.client.post(self.url, headers=headers, data=data)
                else:
                    raise ValueError("Invalid HTTP method specified")
            elif self.scraper:
                if method == 'GET':
                    response = self.scraper.get(self.url, headers=headers, timeout=self.timeout, proxies=self.proxies)
                elif method == 'POST':
                    response = self.scraper.post(self.url, headers=headers, data=data, timeout=self.timeout, proxies=self.proxies)
                else:
                    raise ValueError("Invalid HTTP method specified")
            else:
                raise ValueError("Neither HTTPX Client nor Cloudscraper is initialized.")
            
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Request error occurred: {str(e)}")

    def get(self, **kwargs):
        return self._send_request('GET', **kwargs)

    def post(self, data, **kwargs):
        return self._send_request('POST', data, **kwargs)
