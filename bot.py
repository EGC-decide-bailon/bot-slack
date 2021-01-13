import slack
import os
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import config

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(config.SIGNING_SECRET, '/slack/events',app)

client = slack.WebClient(token=config.SLACK_TOKEN)
BOT_ID = client.api_call("auth.test")['user_id']


@app.route('/login-decide', methods=['POST'])
def message_count():
    data = request.form
    print(data)

if __name__ == "__main__":
    app.run(debug=True)
