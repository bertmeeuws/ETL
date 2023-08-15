import requests
from bs4 import BeautifulSoup
import airflow

def scrape(gpuname):
    page = 1
    query = gpuname.replace(" ", "+")
    url = f"https://www.informatique.nl/zoeken/?q={query}&p={page}"
    print(url)
    response = requests.request("GET", url)

    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.text)
    pages = soup.find("ul", {"id": "pages"})

    print(pages)



