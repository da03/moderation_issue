from openai import OpenAI
import time
import requests
client = OpenAI()
response = requests.get("https://raw.githubusercontent.com/da03/moderation_issue/main/example.txt")

flag_produce_error = True # when True, produces a 429/500 error; False, no error
flag_produce_error = False
if flag_produce_error: # raises a 429/500 error with 6,000 characters
    text = response.text[:6000]
else: # works fine with 5,999 characters
    text = response.text[:5999]

print (f'Number of characters: {len(text)}')
try:  
    response = client.moderations.create(input=text)
except Exception as e:
    print ('error', e)
