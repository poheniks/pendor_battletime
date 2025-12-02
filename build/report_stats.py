import requests

url = 'https://script.google.com/macros/s/AKfycbzBizPcZSarUy1TYvCwcmonk32hWnJ_CcM7142eLCNl6qIy6OW_XR4flVoGM8OylahS5Q/exec'
options = {'key1' : 'value1'}
x = requests.post(url, json=options)
print(x.text)
