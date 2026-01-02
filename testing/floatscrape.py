# API KEY: JmiwpVPkhAEnKnafT8Kyd3vaui6YxjhT

import requests

response = requests.get(
	"https://csfloat.com/api/v1/listings?max_float=0.07&type=buy_now&limit=40&sort_by=lowest_price&paint_index=401",
	headers={"Authorization": "IN ENV FILE"}
)

j = response.json()

print(f"[FLOAT] M249 | System Lock (FN): USD ${j['data'][0]['price']/100}")