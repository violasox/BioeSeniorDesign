from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load the environment variables with Twilio account info and phone numbers
load_dotenv()

# Your Account Sid and Auth Token from twilio.com/console
account_sid = os.environ['TWILIO_SID']
auth_token = os.environ['TWILIO_AUTH']
client = Client(account_sid, auth_token)

message = client.messages.create(
                     body="Alert: cannula out in room 5",
                     from_=os.environ['SEND_NUMBER'],
                     to=os.environ['RECV_NUMBER']
                 )

print(message.sid)
