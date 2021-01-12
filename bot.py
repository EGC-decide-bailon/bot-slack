import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter
import config


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

slack_event_adapter = SlackEventAdapter(config.SIGNING_SECRET, '/slack/events','https://egc-bailon-bot-slack.herokuapp.com/')

client = slack.WebClient(token=config.SLACK_TOKEN)
BOT_ID = client.api_call("auth.test")['user_id']

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text=text)


