from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import threading
import time
import requests
import random
from urllib.parse import quote_plus
from textwrap import shorten
from bs4 import BeautifulSoup


app = Flask(__name__)

# Twilio credentials
account_sid = 'AC2c6304e64efd0d399b6f7af30a834fdd'
auth_token = '8683e838daf641c885e80323d0af6e37'

# Dictionary to store user details
user_details = {}

# Function to start conversation
def start_conversation(user_phone):
    options = [
        "Want to have a normal conversation? Just say 'Hi', 'Hello', or 'Hey', or '1'. 🙋‍♂",
        "Need assistance with something? Just say 'Help me', or '2'. 🆘",
        "Want me to remind you of something? Just say 'Remind me', or '3'. ⏰",
        "Curious about me? Just say 'About me', or '4'. ℹ",
        "Want to end the conversation? Just say 'Stop', or '5'. 🛑"
    ]
    user_details[user_phone] = {'last_active': time.time()}
    return f"Sure there, here are some things you can do:\n" + "\n".join(options)

# Function to handle reminders
def handle_reminder(user_phone, user_msg):
    try:
        time_interval, time_unit = user_msg.split()
        time_interval = int(time_interval)
        if time_unit.lower() == "minute":
            delay_seconds = time_interval * 60
        elif time_unit.lower() == "hour":
            delay_seconds = time_interval * 3600
        elif time_unit.lower() == "day":
            delay_seconds = time_interval * 86400
        else:
            return "Please specify the time unit as 'minute', 'hour', or 'day'."
        
        threading.Thread(target=send_reminder, args=(user_phone, delay_seconds)).start()
        return f"Sure! You'll be reminded every {time_interval} {time_unit}(s)."
    except ValueError:
        return "Invalid time format. Please specify the time interval followed by the time unit (e.g., '1 minute')."

def send_reminder(user_phone, delay_seconds):
    while True:
        time.sleep(delay_seconds)
        try:
            response = requests.post(
                'https://api.twilio.com/2010-04-01/Accounts/AC2c6304e64efd0d399b6f7af30a834fdd/Messages.json',
                data={
                    'From': 'whatsapp:+14155238886',
                    'To': user_phone,
                    'Body': "⏰ Reminder: Don't forget to do your task!"
                },
                auth=('AC2c6304e64efd0d399b6f7af30a834fdd', '8683e838daf641c885e80323d0af6e37')
            )
            print("Reminder message sent successfully.")
        except Exception as e:
            print("An error occurred while sending the reminder message:", str(e))

# Function to stop conversation after 15 minutes of inactivity
def stop_conversation(user_phone):
    time.sleep(900)  # 15 minutes
    user_details.pop(user_phone, None)
    return "Thank you for using me! You can start a new conversation anytime by saying 'Hi'. 😊"

def handle_help_message(user_msg):
    # Perform a Google search for the user's query
    query = user_msg# Modify the query as needed
    encoded_query = quote_plus(query)
    google_search_url = f"https://www.google.com/search?q={encoded_query}"
    response = requests.get(google_search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')
    
    if search_results:
        extracted_text = search_results[0].get_text(separator='\n')
        if len(extracted_text.split()) <= 200:
            return extracted_text + f"\n\nFor more details, visit: {google_search_url}"
        else:
            shortened_text = shorten(extracted_text, width=200)
            return shortened_text + f"\n\nFor more details, visit: {google_search_url}"
    else:
        return f"Sorry, I couldn't find relevant information for your query: {user_msg}. You might want to try a different search query or consult other resources."


# Function to handle user messages
def handle_message(user_phone, user_msg):
    user_phone = user_phone.strip()
    user_msg = user_msg.strip()
    user_details[user_phone] = {'last_active': time.time()}
    
    if user_msg.lower() in ["hi", "hello", "hey","1"]:
        return start_conversation(user_phone)
    elif user_msg.lower() == "help me" or user_msg == "2":
        return "Please provide more details about your query."
    elif user_msg.lower() == "about me" or user_msg == "4":
        return "I am an AI chatbot programmed to assist you. You can ask me anything! 😊"
    elif user_msg.lower() == "stop" or user_msg == "5":
        user_details.pop(user_phone, None)
        return "Thank you for using me! You can start a new conversation anytime by saying 'Hi'. 😊"
    elif user_msg.lower().startswith("remind me"):
        return handle_reminder(user_phone, user_msg[9:])
    else:
        return handle_help_message(user_msg)

# Flask route to handle incoming messages from Twilio
@app.route("/", methods=['POST'])
def webhook():
    user_phone = request.values.get('From', '').strip()
    user_msg = request.values.get('Body', '').strip()

    response = MessagingResponse()

    if user_msg:
        reply_msg = handle_message(user_phone, user_msg)
        response.message(reply_msg)
    else:
        response.message("Sorry, I didn't understand that.")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
