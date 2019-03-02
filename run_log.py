from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods =['POST'])
def sms():
    #number = request.form['From']
    #message_body = request.form['Body']

    resp = MessagingResponse()
    #response_message = 'Hello {}, You said:{}'.format(number, message_body)
    response_message = "Entering Idle Mode for 5 minutes"
    resp.message(response_message)

    return str(resp)

@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%m-%d %H:%M:%S]')
    logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response

@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%m-%d %H:%M]')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, tb)
    return e.status_code

if __name__ == "__main__":
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    logger = logging.getLogger('tdm')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    app.run(debug=False)
