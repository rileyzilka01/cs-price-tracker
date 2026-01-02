import requests

# response = requests.get("https://steamcommunity.com/market/pricehistory?appid=730&market_hash_name=AWP%20%7C%20Dragon%20Lore%20%28Factory%20New%29")
response = requests.get("https://steamcommunity.com/market/priceoverview/?currency=1&appid=730&market_hash_name=M249%20%7C%20System%20Lock%20%28Factory%20New%29")

j = response.json()

print(f"[STEAM] M249 | System Lock (FN): USD {j['lowest_price']}")