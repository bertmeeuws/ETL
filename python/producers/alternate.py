import requests
from bs4 import BeautifulSoup


def scrape(gpuname):
    encodedName = gpuname.replace(" ","+")
    page = requests.request("GET", f"https://www.alternate.be/listing.xhtml?q={encodedName}&page=1")
    soup = BeautifulSoup(page.text, 'html.parser')
    products = []

    for i in soup.findAll("a",{"class":"card align-content-center productBox boxCounter text-font"}):
        name = i.find("div",{"class":"product-name font-weight-bold"}).text
        link = i.get("href")
        price = i.find("div",{"class":"col-auto order-2 pl-0"}).text
        inStock = i.find("div",{"class":"col-auto delivery-info text-right"}).text
        productNr = link.rsplit('/', 1)[-1]

        detail = requests.request("GET", link)
        soup = BeautifulSoup(detail.text, 'html.parser')

        table_element = soup.find("table")

        # Find the second <td> element within the <tr> (the one containing "4719072744526")
        type = table_element.select('td')[1].text
        ean = table_element.select('td')[3].text

        if type != "Grafische kaart":
            continue

        newProduct = AlternateProduct(name,price,link,inStock,productNr, ean)
        products.append(newProduct)

    return products
    
class AlternateProduct:
    def __init__(self, name, price, link, inStock, productNr, EAN):
        self.name = name
        self.price = price
        self.link = link
        self.inStock = inStock
        self.productNr = productNr
        self.EAN = EAN

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "link": self.link,
            "inStock": self.inStock,
            "productNr": self.productNr,
            "EAN": self.EAN
        }
        
    