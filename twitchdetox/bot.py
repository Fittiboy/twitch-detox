"""Bot that monitors the chat and reads the messages. Stores a chat log."""
import irc.bot
import requests
import json
import time
from os.path import isfile


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel, keepalive=30):
        if not isfile('chat.log'):
            with open('chat.log', 'w') as chat_log_file:
                json.dump([], chat_log_file)

        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.headers = {'Client-ID': client_id,
                        'Accept': 'application/vnd.twitchtv.v5+json'}
        self.keepalive = keepalive
        self.temp_log = []
        self.lastlog = time.time()

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        r = requests.get(url, headers=self.headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(
                self, [(server, port, 'oauth:'+token)],
                username, username)

    def on_welcome(self, c, e):
        """Join a channel."""
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        c.set_keepalive(self.keepalive)
        print("Connected!")
        self.reconnect = 1

    def on_pubmsg(self, c, e):
        """Read incoming message and classify as toxic/non-toxic.

        Log incoming messages for manual labelling purposes.

        Additionally, turn the unnatural format of e.tags
        into a more workable dictionary, also containing a dictionary
        representation of the badges.
        """

        # e.tags comes as a list of dictionaries of the form
        # {'key': key, 'value': value}.  This line changes that
        # to a single dictionary of the more reasonable form {key: value}.
        e.tags = {dct['key']: dct['value'] for dct in e.tags}
        badges_tag = e.tags.get('badges')
        badges_list = []
        # The badges come as a string with the format
        # 'badge/version,badge/version,badge/version...'.
        #
        # This code converts the string into a more natural
        # dictionary of the form {badge: version, ...}.
        if badges_tag:
            badges_list = badges_tag.split(",")
        badges_list_collection = [badge.split("/") for badge
                                  in badges_list if badge]

        badges = {badge_list[0]: badge_list[1] for badge_list
                  in badges_list_collection}
        # Update the badges tag for later use in commands.py
        e.tags['badges'] = badges

        log_entry = {'args': e.arguments,
                     'tags': e.tags}
        self.temp_log.append(log_entry)

        if time.time() - self.lastlog > 30:
            with open('chat.log') as chat_log_file:
                chat_log = json.load(chat_log_file)

            chat_log += self.temp_log
            self.temp_log = []
            self.lastlog = time.time()

            with open('chat.log', 'w') as chat_log_file:
                json.dump(chat_log, chat_log_file)


def main():
    """Read the settings from settings.json and run the bot with these."""
    with open('settings.json') as settings_file:
        settings = json.load(settings_file)
    username = settings['username']
    client_id = settings['client_id']
    token = settings['token']
    channel = settings['channel']
    keepalive = settings['keepalive']

    bot = TwitchBot(username, client_id, token, channel, keepalive)
    bot.start()


if __name__ == "__main__":
    main()
