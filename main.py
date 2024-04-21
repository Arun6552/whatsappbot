from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from textwrap import shorten

app = Flask(__name__)

# Twilio credentials
account_sid = 'AC2c6304e64efd0d399b6f7af30a834fdd'
auth_token = '8683e838daf641c885e80323d0af6e37'

# Function to start conversation
def start_conversation():
    return "Hi Arun! How can I assist you today?"

# Function to provide help
def provide_help():
    return "Sure Arun, I'm here to help. What doubt do you have regarding your exam preparation? Please provide details, and I'll do my best to assist you."

# Function to provide information about you
def about_me():
    return "I am an AI chatbot programmed to assist you. Feel free to ask me anything!"

# Function to handle user messages when "Help Me" is clicked
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
def handle_message(user_msg):
    if user_msg.lower() == "start conversation":
        return start_conversation()
    elif user_msg.lower() == "help me":
        return provide_help()
    elif user_msg.lower() == "about me":
        return about_me()
    else:
        return handle_help_message(user_msg)

# Flask route to handle incoming messages from Twilio
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

if __name__ == "__main__":
    app.run(debug=True)
