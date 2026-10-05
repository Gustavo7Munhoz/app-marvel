import urllib.request
import json
import urllib.parse

def fetch_gem(name):
    query = urllib.parse.quote(f'name:{name}')
    url = f'https://comicvine.gamespot.com/api/objects?api_key=bbf8ecf304d2b89198f1e3ca3cd6a0433b6c74a3&format=json&filter={query}&field_list=id,name,deck&limit=1'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode('utf-8'))
        print(f"{name}: {data['results'][0]['id'] if data['results'] else 'NOT FOUND'}")
    except Exception as e:
        print(f"{name}: Error {e}")

gems = ['Soul Gem', 'Time Gem', 'Space Gem', 'Mind Gem', 'Reality Gem', 'Power Gem']
for g in gems:
    fetch_gem(g)
