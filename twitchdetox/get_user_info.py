"""Tool for getting the user-id of a user from their name."""
import requests


def get_uid(client_id, user):
    """Return a user's user-id"""
    headers = {"Client-ID": f"{client_id}",
               "Accept": "application/vnd.twitchtv.v5+json"}
    url = f"https://api.twitch.tv/kraken/users?login={user}"
    r = requests.get(url, headers=headers).json()
    return r['users'][0].get('_id')
