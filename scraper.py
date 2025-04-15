import requests 
from bs4 import BeautifulSoup

url = "https://www.dr.dk/nyheder"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = soup.find_all("h2")

    print("News headlines: ")
    for i, h in enumerate(headlines[:10], start=1):
        print(f"{i}. {h.text.strip()}")
else:
    print(f"Error: {response.status_code}")

