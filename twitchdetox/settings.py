"""Change the bot's settings for connecting to chat."""
import json


def main():
    try:
        with open('settings.json') as settings_file:
            settings = json.load(settings_file)
    except FileNotFoundError:
        settings = {}

    set_setting(settings, 'username', 'Username: ')
    set_setting(settings, 'client_id', 'Client-ID: ')
    set_setting(settings, 'token', 'Token: ')
    set_setting(settings, 'channel', 'Channel: ')
    settings['keepalive'] = 300
    with open('settings.json', 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)


def set_setting(settings, setting, prompt):
    choice = input(prompt)
    if not choice:
        print("You have not entered a value. " +
              "If you want to leave this blank, " +
              "just hit enter again")
    if setting == "channel":
        choice = choice.lower()
    settings[setting] = choice
