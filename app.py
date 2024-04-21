from flask import Flask, request
from twilio.rest import Client
import schedule
import requests
from twilio.twiml.messaging_response import MessagingResponse
import time
import requests
from urllib.parse import quote_plus
import random
from urllib.parse import quote_plus
from textwrap import shorten
from bs4 import BeautifulSoup

app = Flask(__name__)

# Twilio credentials
account_sid = 'AC2c6304e64efd0d399b6f7af30a834fdd'
auth_token = '8683e838daf641c885e80323d0af6e37'
whatsapp_client = Client(account_sid, auth_token)

# Sample contact list (replace with your actual contact list)
contacts = ['whatsapp:+919078029962']
# Function to send "Drink water" message to each contact
def send_water_reminder():
    try:
        for contact in contacts:
            message = whatsapp_client.messages.create(
                body="Hey Neeru !! Please Drink water and Take care of your health.❤️ \n Remainder from your lovely AI Chatbot by Arun",
                from_='whatsapp:+14155238886',  # Twilio sandbox number
                to=contact
            )
            print(f"Water reminder sent to {contact}.")
            print("Message delivered:", message.sid)  # Log message delivery status
    except Exception as e:
        print("An error occurred:", str(e))


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

# Function to start conversation
def start_conversation(user_phone):
    options = [
        "Want to have a normal conversation? Just say 'Hi', 'Hello', or 'Hey', or '1'. 🙋‍♂",
        "Need assistance with something? Just say 'Help me', or '2'. 🆘",
        "Want me to remind you of something? Just say 'Remind me', or '3'. ⏰",
        "Curious about me? Just say 'About me', or '4'. ℹ",
        "Want to end the conversation? Just say 'Stop', or '5'. 🛑"
    ]
    return f"Sure there, here are some things you can do:\n" + "\n".join(options)


# Function to handle user messages
def handle_message(user_msg):
    user_msg = user_msg.strip()
    if user_msg.lower() in ["hi", "hello", "hey","1"]:
        return start_conversation(user_msg)
    elif user_msg.lower() == "help me" or user_msg == "2":
        return "Please provide more details about your query."
    elif user_msg.lower() == "about me" or user_msg == "4":
        return "I am an AI chatbot programmed to assist you. You can ask me anything! 😊"
    elif user_msg.lower() == "stop" or user_msg == "5":
        return "Thank you for using me! You can start a new conversation anytime by saying 'Hi'. 😊"
    else:
        return handle_help_message(user_msg)


@app.route("/", methods=['POST'])
def webhook():
    user_msg = request.values.get('Body', '').strip()

    response = MessagingResponse()

    if user_msg:
        reply_msg = handle_message(user_msg)
        response.message(reply_msg)
    else:
        response.message("Sorry, I didn't understand that.")

    return str(response)


# Schedule to send "Drink water" message every minute
schedule.every(1).minutes.do(send_water_reminder)



if __name__ == "__main__":
    # Start the Flask server
    app.run(host="127.0.0.1", port=5000,debug=True)

    # Start the scheduler
    while True:
        try:
            # Run pending scheduled tasks
            schedule.run_pending()
            # Sleep for 1 second to avoid excessive CPU usage
            time.sleep(1)
        except KeyboardInterrupt:
            # Stop the scheduler loop when interrupted
            break