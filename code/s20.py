import requests

# Code A
requests.get('https://oim.108122.xyz/mass')

# Code B
requests.post('https://oim.108122.xyz/echo',
              json={'name': 'Alice'})

with open('data/s20.txt') as f:
    data = f.read()
    print(data)

with open('data/s20.txt', 'r') as f:
    for line in f:
        print(line.strip())
with open('data/s20.txt', 'w') as f:
    f.write('Hello, world!\n')
