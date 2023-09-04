import requests
from pprint import pprint


r = requests.get("https://9animetv.to/watch/one-piece-100?ep=2842")

pprint(r.text)
