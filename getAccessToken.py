import requests
import os
import dotenv


def get_lucid_access_token():
    token_url = 'https://api.lucid.co/oauth2/token'
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    # Prepare request parameters
    print("Getting refresh token")
    data = {
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ["CLIENT_SECRET"],
        'grant_type': "refresh_token",
        'refresh_token': os.environ['REFRESH_TOKEN']
    }

    try:
        # Make a POST request to obtain the access token
        response = requests.post(token_url, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse and return the access token from the response
        access_token = response.json().get('access_token')
        refresh_token = response.json().get('refresh_token')
        os.environ['REFRESH_TOKEN'] = refresh_token
        dotenv.set_key(dotenv_file, "REFRESH_TOKEN", os.environ["REFRESH_TOKEN"])
        print("Successfully retrieved access token and refresh token")
        return access_token

    except requests.exceptions.RequestException as e:
        print(e)
        return None
