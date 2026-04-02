import requests
from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

#response = requests.get('https://oim.108122.xyz/mass', headers={"X-Token": "random"},)
#data=response.json()

response=requests.get('https://oim.108122.xyz/mass', headers={"X-Token": "zhizhi"},)

data=response.json()
print(len(data))
print(data.keys())
towns=data['data']
print(type(towns))

#pprint(towns)
print(len(towns))
requests.post('https://oim.108122.xyz/message',
              json={'message': 'Hello from Saad!'},
              headers={'X-Token': 'saadsaad'})

API_KEY = os.getenv('OPENWEATHER_API_KEY')
url = (f'https://api.openweathermap.org/data/2.5/weather'
       f'?q=Boston&appid={API_KEY}&units=imperial')
data = requests.get(url).json()
if 'main' in data:
    print(f"Boston: {data['main']['temp']}°F")
else:
    print(f"Error: {data.get('message', 'Unknown error')}")
