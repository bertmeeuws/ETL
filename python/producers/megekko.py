import requests
import json


def scrape(gpuname):
    url = "https://www.megekko.nl/pages/zoeken/v4/v4.php"

    encodedUri = gpuname.replace(" ", "+")

    payload = f"zoek={encodedUri}&cache=0&pageuri=%2Fhome%2F&filter=&pagemutate=force"

    headers = {
        "authority": "www.megekko.nl",
        "accept": "*/*",
        "accept-language": "en-GB,en;q=0.9,nl-BE;q=0.8,nl;q=0.7,en-US;q=0.6,fa;q=0.5,de;q=0.4,fr;q=0.3",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.megekko.nl",
        "pragma": "no-cache",
        "referer": "https://www.megekko.nl/home/",
        "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = {}

    f = open("megekko.json", "w")

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        data = json.loads(response.text)
    else:
        data = json.loads(response.text)
        f.write(json.dumps(data))

    list = data["zoek"]

    products = []

    for x in list:
        if x["prodname"].lower().find(gpuname.lower()) != -1:
            inStock = x["voorraad"] > 0 if True else False
            product = Product(x["prodname"], x["price"], "EUR", inStock)
            products.append(product)

    return products


class Product:
    def __init__(self, name, price, currency, inStock):
        self.name = name
        self.price = price
        self.currency = currency
        self.inStock = inStock

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "inStock": self.inStock,
        }
