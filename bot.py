import slack
import os
from flask import Flask, Request, Response
from slackeventsapi import SlackEventAdapter
import config

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(config.SIGNING_SECRET, '/slack/events',app)

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

@app.route('/login-decide', methods=['GET','POST'])
def message_count():
    client.chat_postMessage(channel="test", text="buenas tardes")

if __name__ == "__main__":
    app.run(debug=True)
