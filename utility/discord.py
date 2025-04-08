from .variables import *

@dataclass
class DiscordWebhookSettings:


def discord_send_webhook(url: str, content: str, username: str = None, ):
    """
    Sends a post request to the URL with the content.
    """

    # Just to handle using the library standalone
    import requests

    data = {
        'content': content,
        'allowed_mentions': {
            'parse': ['roles']
        },
        'flags': 1 << 2  # Suppress embeds
    }

    if username is not None:
        data['username'] = username

    requests.post(
        url=url,
        json=data
    )