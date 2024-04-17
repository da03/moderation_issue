# OpenAI Moderation API 429 or 500 Error Despite Not Reaching Usage Limit

When the input to the Moderation API is long, it raises a 429 rate limit error (or sometimes 500 error) even without actually reaching the rate limit. Note that this cannot be resolved by waiting and resending the same request, as the same error would be raised.

## Code to Reproduce the Error

Below is a minimum code snippet that can reproduce the error using a request of 6k Chinese characters. This example can also be found in a single file `test_moderation.py`:

```
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
```

In the above code, using 6000 characters will fail (by setting `flag_produce_error` to `True` in above code) with a 429 Rate limit error (or 500 server error), while using 5999 characters will succeed (by setting `flag_produce_error` to `False` in above code).


## Hypothesis: Encoding Issues

I suspect that these errors might be linked to encoding issues, particularly involving non-Latin characters. For example, if we use English characters in the above example (as opposed to Chinese characters in the original text), even scaling to millions of characters still works:

```
from openai import OpenAI
import time
import requests
client = OpenAI()
import string, random

text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=1000000))
print (f'Number of characters: {len(text)}')
try:
    response = client.moderations.create(input=text)
except Exception as e: 
    print ('error', e)
```


## Evidence supporting Hypotheis

I used the Moderation API to flag toxic data in the [WildChat dataset](https://huggingface.co/datasets/allenai/WildChat). During this process, I collected statistics on the languages of failing examples and observed that most errors involved inputs containing non-Latin characters, such as Korean and Chinese. Below are the detailed statistics showing the disproportionate occurrence of errors with these languages:

### Error Distribution by Language

- **Korean**: 66.44% of errors (0.51% of dataset)
- **Chinese**: 10.96% of errors (13.54% of dataset)
- **English**: 6.85% of errors (54.92% of dataset) (mostly containing special characters like ψ or •)
- **Russian**: 3.94% of errors (11.77% of dataset)
- **Japanese**: 2.40% of errors (0.53% of dataset)
- **Hindi**: 2.23% of errors (0.03% of dataset)

This suggests a possible correlation between non-Latin characters and the increased likelihood of receiving a 429 or 500 error from the Moderation API. To enable others to verify my results, I have included failing examples in [failing_examples](failing_examples).


## Workaround

While awaiting a more permanent fix or clarification from OpenAI, I've implemented a temporary workaround that involves breaking down large inputs into smaller segments, and then taking their maximum category scores as the result. In case others encounter the same issue, I have included my workaround in [workaround.py](workaround.py) as part of this repo.
