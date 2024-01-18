import getAccessToken
from ratelimiter import RateLimiter
import requests


# rate limits 60 per 5 seconds.
@RateLimiter(max_calls=60, period=5)
def get_document(document_id: str, access_token: str):
    base_url = "https://api.lucid.co/documents/"
    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
               'Authorization': 'Bearer ' + access_token,
               'Accept': 'image/jpeg', 'Lucid-Api-Version': '1'}
    # with a session, we get keep alive
    session = requests.session()
    full_url = base_url + document_id
    return session.get(full_url, headers=headers)
