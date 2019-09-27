import os
from flask import Flask, url_for, Response, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse, Dial

app = Flask(__name__)

_HOTLINE_NUMBERS = ['FILL ME IN e.g. +13129999999']
_HTTP_SCHEME = 'https'

class ConfigurationError(ValueError):
    pass

def get_hotline_numbers():
    global _HOTLINE_NUMBERS

    if _HOTLINE_NUMBERS is None:
        numbers_str = os.environ.get('COC_NUMBERS', None)

        if numbers_str is None:
            msg = 'Environment variable COC_NUMBERS must be present and must be a comma delimited' \
                  ' string of numbers with country codes'
            raise ConfigurationError(msg)

        _HOTLINE_NUMBERS = [num.strip() for num in numbers_str.split(',')]
    print(_HOTLINE_NUMBERS)
    return _HOTLINE_NUMBERS

@app.route('/end_call', methods=['GET', 'POST'])
def end_call():
    """Thank the person for contacting the team."""
    response = VoiceResponse()
    response.say("Thank you for using the PromptConf Code of Conduct Hotline", voice='alice')
    response.hangup()
    return Response(str(response), 200, mimetype="application/xml")

@app.route('/inbound', methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls with a connection message and forward"""
    # Start our TwiML response
    response = VoiceResponse()

    # Read a message aloud to the caller
    response.say(
        "Connecting you to the PromptConf Code of Conduct team",
        voice='alice'
    )

    for number in get_hotline_numbers():
        response.dial(
            number,
            caller_id='PromptConf Hotline',
            action=url_for('end_call')
        )

    return Response(str(response), 200, mimetype="application/xml")

@app.route('/sms', methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    response = MessagingResponse()

    # Add a message
    response.message(f'Thank you for contacting the PromptConf Code of Conduct. '
    + f'Please report your incident to our oncall team - Byron, Lorena, and Mica - either by calling this' +
    f'number or emailing coc@promptconf.com. Thank you.')

    return Response(str(response), 200, mimetype="application/xml")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    if port == 3000:
        app.debug = True
    app.run(host='0.0.0.0', port=port)
