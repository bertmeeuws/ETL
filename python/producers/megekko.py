def scrape(gpuname):
    import requests
    import json
    from bs4 import BeautifulSoup

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
            inStock = x["voorraad"] > 0 if True else False
            name = x["prodname"]
            price = x["price"]
            link = f"https://www.megekko.nl{x['link']}"

            detail = requests.request("GET", link)
            soup = BeautifulSoup(detail.text, 'html.parser')

            ean_label_div = soup.find('div', class_='t1', text='EAN')
            
            if ean_label_div == None:
                continue
            
            # Get the EAN code from the corresponding div with class "t2"
            ean_code_div = ean_label_div.find_next('div', class_='t2')
            ean_code = ean_code_div.text


            product = Product(name, price, "EUR", inStock, x["prodnum"], link, x["resultno"], ean_code)
            products.append(product)


    return products

def sendToKafka(**context):
    ti = context['ti']
    producer = ti.xcom_pull(task_ids='create_kafka_producer_task')
    products = ti.xcom_pull(task_ids='scrape_megekko_task')

    import json
    for el in products:
        byte_array = json.dumps(el.to_dict()).encode('utf-8')

    future = producer.send("megekko", byte_array)

    try:
        # Wait for the result and check if the message was sent successfully
        record_metadata = future.get(timeout=10)
        print(f"Message sent successfully to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
    except KafkaError as e:
        print(f"Failed to send message: {e}")

class Product:
    def __init__(self, name, price, currency, inStock, productNr, url, rank, EAN):
        self.name = name
        self.price = price
        self.currency = currency
        self.inStock = inStock
        self.productNr = productNr
        self.url = url
        self.rank = rank
        self.EAN = EAN


    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "inStock": self.inStock,
            "productNr": self.productNr,
            "url": self.url,
            "rank": self.rank,
            "EAN": self.EAN
        }
