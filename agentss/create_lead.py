import pytz
from datetime import datetime
import requests
from dotenv import load_dotenv
from agents import function_tool
import streamlit as st
import os

load_dotenv()  



@function_tool
def create_lead(name: str, phone_number: str, concerns: str):
    '''This is responsible to book a call so a representative can reach out to a customer
    for more clarification and information.
    name - name of the user
    phone_number - phone number of the user
    concerns - concerns of the user
    '''

    air_api_key = st.secrets['AIRTABLE_API_KEY']
    # air_api_key = os.getenv('AIRTABLE_API_KEY')

    # Add to airtable 'booked calls'
    url = "https://api.airtable.com/v0/appeCc2gb9GAQHKhz/Booked%20Calls"
    headers = {
        "Authorization": air_api_key,  # NOTE: When adding your Airtable API key in secrets it must include "Bearer YOURKEY", keeping the Bearer and the space. If you don't add this then it won't work!
        "Content-Type": "application/json"
    }

    # platform = request.args.get('platform', 'Not Specified')

    # Define the timezone for the Philippines
    manila_tz = pytz.timezone('Asia/Manila')

    # Get current datetime in Manila timezone and format it
    current_datetime_manila = datetime.now(manila_tz).strftime(
        "%m/%d/%Y %I:%M %p").lower()

    data = {
        "records": [{
            "fields": {
                "Name": name,
                "Phone": phone_number,
                "Concerns": concerns,
                "Date": current_datetime_manila,
                "Platform": 'Website',
                "Status": "Todo"
            }
        }]
    }
    response_book_call = requests.post(url, headers=headers, json=data)
    if response_book_call.status_code == 200:
        return "Call successfully booked. Expect a representative to reach out"
    else:
        return {
        "error": 'There seems to be an error'
    }